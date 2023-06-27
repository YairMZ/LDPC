from numpy.typing import ArrayLike, NDArray
import numpy as np
from typing import Optional, Union
from ldpc.utils import IncorrectLength
from ldpc.decoder.common import InfoBitsNotSpecified, bsc_llr
from enum import Enum, auto


__all__ = ["PbfDecoder", "PbfVariant"]


class PbfVariant(Enum):
    """Enumerate variants of the probabilistic bit flipping algorithm"""
    PPBF = auto()  # based on an article by K. Le et al. named "A Probabilistic Parallel Bit-Flipping Decoder for Low-Density Parity-Check Codes"


class PbfDecoder:
    """Probabilistic bit flipping algorithm for LDPC decoding codes
    The PBF algorithm is a probabilistic bit flipping algorithm for LDPC codes.
    Variant is chosen by the decoder_variant parameter in the constructor.
    See PbfVariant enum for available variants.
        - PPBF - Implementation based on an article by K. Le et al. "A Probabilistic Parallel Bit-Flipping Decoder for
        Low-Density Parity-Check Codes"

    """
    def __init__(self, h: ArrayLike, max_iter: int, decoder_variant: PbfVariant, info_idx: Optional[NDArray[np.bool_]] = None,
                 **kwargs) -> None:
        """

        :param h:the parity check code matrix of the code
        :param decoder_variant: the variant of the decoder to use
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param info_idx: a boolean array representing the indices of information bits in the code
        """
        self.info_idx = info_idx
        self.h: NDArray[np.int_] = h
        self.m, self.n = h.shape
        self.k = self.n - self.m if info_idx is None else np.sum(info_idx)
        self.max_iter = max_iter
        self.decoder_variant = decoder_variant

        self.use_priors = kwargs.get("use_priors", 0)

        if self.decoder_variant in {PbfVariant.PPBF}:
            # for each check node i, which vnodes j are connected to it, referred to as the "N_i" set in by Ryan
            self.check2vnode = {i: [j for j in range(self.n) if self.h[i, j] == 1] for i in range(self.m)}
            # for each vnode j, which cnodes i are connected to it, referred to as the "M_j" set in by Ryan
            self.vnode2check = {j: [i for i in range(self.m) if self.h[i, j] == 1] for j in range(self.n)}
            self.vnode_degree = np.sum(h,axis=0)
            self.cnode_degree = np.sum(h,axis=1)
            # if probabilities vector was supplied use it, otherwise None
            self.p_vector: NDArray[np.float_] = kwargs.get("p_vector", None)
            if self.p_vector is not None:
                self._verify_p_vector(self.p_vector)


    def decode(self, channel_word: NDArray[np.int_], prior: Optional[NDArray[np.int_]] = None,
               p_vector: Optional[NDArray[np.float_]] = None) \
            -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int, NDArray[np.int_], NDArray[np.int_]]:
        """
        decode a sequence received from the channel

        :param p_vector: a vector of probabilities for flipping a bit, per energy level. If None, use the default
        :param channel_word: a sequence of channel hard values
        :param prior: an array of hard priors. -1 for no prior, 0 for 0 prior, 1 for 1 prior
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
            - syndrome
            - a measure of validity of each vnode, lower is better
        """
        if len(channel_word) != self.n:
            raise IncorrectLength("incorrect block size")
        if prior is None or self.use_priors == 0:
            prior = -1*np.ones(self.n, dtype=np.int_)
        elif len(prior) != self.n:
            raise IncorrectLength("incorrect prior size")
        if p_vector is None:
            if self.p_vector is None:
                raise ValueError("p_vector must be supplied")
            else:
                p_vector = self.p_vector
        else:
            self._verify_p_vector(p_vector)
        # initialize the vnodes to the channel word
        vnode_values = channel_word.copy()
        for iteration in range(self.max_iter):
            syndrome = self.h @ vnode_values % 2
            if not syndrome.any():  # no errors detected, exit
                break
            # for each vnode how many equations are failed
            vnode_reliability = np.array((syndrome @ self.h)*max(self.vnode_degree) / self.vnode_degree).astype(np.int_)
            flipped_vnodes = vnode_values ^ channel_word
            prior_mask = np.array(prior != -1, dtype=np.int_)
            prior_reliability = np.bitwise_xor(prior, vnode_values) * prior_mask
            # for each vnode, the energy is the sum equations it failed to satisfy (vnode_reliability) plus 1 if it was flipped
            # w.r.t the channel word (flipped_vnodes) plus 1 if it was flipped w.r.t the prior (prior_reliability)
            energy = flipped_vnodes + vnode_reliability + prior_reliability
            # The energy dictates the probability of flipping the current value  in the next iteration. The probability is
            # calculated by the p_vector, which is a vector of probabilities for flipping a bit, per energy level

            # Draw a random bit according ta bernoulli distribution with the calculated probability per vnode energy.
            # If the drawn bit is 1, flip the current value of the vnode
            bit_flip_p = np.array([p_vector[energy[i]] for i in range(self.n)])
            flipped = np.random.binomial(1, bit_flip_p)
            vnode_values = np.bitwise_xor(vnode_values, flipped)

        # we output also soft information (LLR) for each bit which can be used for Turbo decoding
        # the LLR is calculated as the log of the ratio of probabilities of the bit being 1 or 0
        # Since hte absolute value of the LLR indicates the confidence in the bit value, we use p_vector[energy] of each vnode
        # as a crossover probability of a hypothetical BSC channel with the same LLR
        channels = [bsc_llr(p) for p in p_vector]
        llr = np.array([channels[energy[i]](vnode_values[i]) for i in range(self.n)])
        return vnode_values, llr, not syndrome.any(), iteration, syndrome, energy

    def info_bits(self, estimate: NDArray[np.int_]) -> NDArray[np.int_]:
        """extract information bearing bits from decoded estimate, assuming info bits indices were specified"""
        if self.info_idx is not None:
            return estimate[self.info_idx]
        else:
            raise InfoBitsNotSpecified("decoder cannot tell info bits")

    def _verify_p_vector(self, p_vector: NDArray[np.float_]) -> None:
        """
        verify that the p_vector is valid
        :param p_vector: p_vector to verify
        :return: None
        """
        if len(p_vector) != max(self.vnode_degree) + 2 + self.use_priors:
            raise IncorrectLength(f"incorrect length of p_vector, must be of length "
                                  f"{max(self.vnode_degree) + 2 + self.use_priors}")
        if np.any(p_vector < 0) or np.any(p_vector > 1):
            raise ValueError("p_vector must be between 0 and 1")
