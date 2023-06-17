from numpy.typing import ArrayLike, NDArray
import numpy as np
from typing import Optional, Union
from ldpc.utils import IncorrectLength
from ldpc.decoder.common import InfoBitsNotSpecified
from enum import Enum, auto


__all__ = ["WbfDecoder", "WbfVariant"]


class WbfVariant(Enum):
    """Enumerate variants of the weighted bit flipping algorithm"""
    WBF = auto()  # based on Ryan's book, chapter 10.8
    MWBF = auto()  # based on Ryan's book, chapter 10.9
    MWBF_NO_LOOPS = auto()  # based on Ryan's book, chapter 10.9, but without loops


class WbfDecoder:
    """Weighted bit flipping algorithm for LDPC decoding codes
    Several variants are implemented, see the paper for details.
    Variant is chosen by the decoder_variant parameter in the constructor.
    See WbfVariant enum for available variants.
        - WBF - Implementation based on Ryan's book, chapter 10.8. Originally proposed by Kou, Fossorier and Lin in
        "Low-Density Parity-Check Codes Based on Finite Geometries: A Rediscovery and New Results"
        -MWBF - Implementation based on Ryan's book, chapter 10.9. Originally proposed by Zhang, and Fossorier in
        "A modified weighted bit-flipping decoding of low-density parity-check codes"
        -MWBF_NO_LOOPS - Implementation based on Ryan's book, chapter 10.9. Originally proposed by Liu and Pados in
        “A decoding algorithm for finite-geometry LDPC codes”
    """
    def __init__(self, h: ArrayLike, max_iter: int, decoder_variant: WbfVariant, info_idx: Optional[NDArray[np.bool_]] = None,
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

        if self.decoder_variant in {WbfVariant.WBF, WbfVariant.MWBF, WbfVariant.MWBF_NO_LOOPS}:
            # for each check node i, which vnodes j are connected to it, referred to as the "N_i" set in by Ryan
            self.check2vnode = {i: [j for j in range(self.n) if self.h[i,j] == 1] for i in range(self.m)}
            # for each vnode j, which cnodes i are connected to it, referred to as the "M_j" set in by Ryan
            self.vnode2check = {j: [i for i in range(self.m) if self.h[i,j] == 1] for j in range(self.n)}
        if self.decoder_variant in {WbfVariant.MWBF, WbfVariant.MWBF_NO_LOOPS}:
            mean_mj_size = np.array([len(self.vnode2check[j]) for j in range(self.n)]).mean()
            self.confidence_coefficient: float = kwargs.get("confidence_coefficient",1/mean_mj_size)

    def decode(self, channel_llr: NDArray[np.float_], prior_reliability: Optional[NDArray[np.float_]]= None) \
            -> tuple[NDArray[np.int_], bool, int, NDArray[np.int_], NDArray[np.int_]]:
        """
        decode a sequence received from the channel

        :param channel_llr: a sequence of channel LLR values
        :param prior_reliability: an array of prior reliabilities for each bit, 0 is no prior reliability, positive means more reliable, negative means less reliable
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
            - syndrome
            - a measure of validity of each vnode, lower is better
        """
        if len(channel_llr) != self.n:
            raise IncorrectLength("incorrect block size")
        if prior_reliability is None:
            prior_reliability = np.zeros(self.n, dtype=np.float_)
        if self.decoder_variant in {WbfVariant.WBF, WbfVariant.MWBF, WbfVariant.MWBF_NO_LOOPS}:
            return self._decode_wbf_and_mwbf(channel_llr, prior_reliability)
        else:
            raise NotImplementedError("decoder variant not implemented")

    def info_bits(self, estimate: NDArray[np.int_]) -> NDArray[np.int_]:
        """extract information bearing bits from decoded estimate, assuming info bits indices were specified"""
        if self.info_idx is not None:
            return estimate[self.info_idx]
        else:
            raise InfoBitsNotSpecified("decoder cannot tell info bits")

    def _decode_wbf_and_mwbf(self, channel_llr: NDArray[np.float_], prior_reliability: NDArray[np.float_])-> tuple[
        NDArray[np.int_], bool, int, NDArray[np.int_], NDArray[np.int_]]:
        """
        decode a sequence received from the channel using the WBF or MWBF algorithm
        :param channel_llr: received LLR values
        :param prior_reliability: prior reliability of each bit
        :return:
        """
        channel_word = np.array(channel_llr < 0, dtype=np.int_)
        abs_llr = np.abs(channel_llr)
        cnode_validity = self.syndrome_reliability(abs_llr)
        reliability_profile = np.zeros(self.n, dtype=np.float_)  # bit is more reliable as reliability_profile is lower
        # (more negative), and less reliable as it is higher (more positive)
        if self.decoder_variant == WbfVariant.MWBF_NO_LOOPS:
            loop_exclusion_list: list[set[int,],] = []
            last_flip_sequence: set[int,] = set()

        for iteration in range(self.max_iter):
            syndrome = self.h @ channel_word % 2
            if not syndrome.any():  # no errors detected, exit
                break
            if self.decoder_variant == WbfVariant.WBF:
                reliability_profile = np.array([sum((2 * syndrome[i] - 1) * cnode_validity[i] for i in self.vnode2check[j])
                                                for j in range(self.n)], dtype=np.float_)
            elif self.decoder_variant in {WbfVariant.MWBF, WbfVariant.MWBF_NO_LOOPS}:
                reliability_profile = np.array([sum((2*syndrome[i] -1)*cnode_validity[i][j] for i in self.vnode2check[j])
                                                for j in range(self.n)], dtype=np.float_)
                reliability_profile -= self.confidence_coefficient * abs_llr
            reliability_profile -= prior_reliability
            if self.decoder_variant == WbfVariant.MWBF_NO_LOOPS:
                flip_bit, chosen_flip_sequence = self._choose_next_flip(last_flip_sequence, loop_exclusion_list,
                                                                        reliability_profile)
                last_flip_sequence = chosen_flip_sequence
                loop_exclusion_list.append(chosen_flip_sequence)
            else: # WBF and MWBF
                flip_bit = np.argwhere(reliability_profile == np.amax(reliability_profile)).flatten()
                if len(flip_bit) > 1: # if there are several bits with the same reliability, choose one at random
                    flip_bit = np.random.choice(flip_bit)
            channel_word[flip_bit] = 1-channel_word[flip_bit]
        return channel_word, not syndrome.any(), iteration, syndrome, reliability_profile

    def syndrome_reliability(self, abs_llr: NDArray[np.float_]) -> Union[NDArray[np.float_], list[dict[int, float]]]:
        """
        return the reliability of each bit in the syndrome. The higher the value, the more reliable the bit is.
        """
        if self.decoder_variant == WbfVariant.WBF:
            return np.array([min(abs_llr[self.check2vnode[i]]) for i in range(self.m)], dtype=np.float_)
        elif self.decoder_variant in {WbfVariant.MWBF, WbfVariant.MWBF_NO_LOOPS}:
            cnode_validity = [None]*self.m
            for i in range(self.m):
                mask = np.ones(len(self.check2vnode[i]), dtype=np.bool_)
                for idx,j in enumerate(self.check2vnode[i]):
                    if cnode_validity[i] is None:
                        cnode_validity[i] = {}
                    mask[idx] = False
                    cnode_validity[i][j] = min(abs_llr[self.check2vnode[i]][mask])
                    mask[idx] = True
            return cnode_validity
        else:
            raise ValueError("unknown decoder variant")

    def _choose_next_flip(self, last_flip_sequence, loop_exclusion_list, reliability_profile) -> tuple[int, set[int,]]:
        """
        verify that there are no loops in the sequence of attempts to flip bits in MWBF_NO_LOOPS decoder
        """
        i = 0
        allowed_flip_bits = [True]*self.n
        while i < self.n:
            candidate_sequence = last_flip_sequence.copy()
            flip_bit = np.argwhere((reliability_profile == np.amax(reliability_profile[allowed_flip_bits])) & allowed_flip_bits
                                   ).flatten()
            flip_bit = np.random.choice(flip_bit) if len(flip_bit) > 1 else flip_bit[0]
            if flip_bit in last_flip_sequence:
                candidate_sequence.remove(flip_bit)
            else:
                candidate_sequence.add(flip_bit)
            if candidate_sequence not in loop_exclusion_list:
                break
            i += 1
            allowed_flip_bits[flip_bit] = False
        if i == self.n:
            raise RuntimeError("loop in the sequence of attempts to flip bits")
        return flip_bit, candidate_sequence
