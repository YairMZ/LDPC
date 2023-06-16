from numpy.typing import ArrayLike, NDArray
import numpy as np
from typing import Optional
from ldpc.utils import IncorrectLength
from ldpc.decoder.common import InfoBitsNotSpecified

__all__ = ["GalBfDecoder"]


class GalBfDecoder:
    """Decode codewords according to Gallager bit-flipping algorithm"""
    def __init__(self, h: ArrayLike, max_iter: int, info_idx: Optional[NDArray[np.bool_]] = None,
                 percent_flipped: int = 10):
        """

        :param h:the parity check code matrix of the code
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param info_idx: a boolean array representing the indices of information bits in the code
        :param percent_flipped: the percentage of bits which ave unsatisfied equations to flip in each iteration
        """
        self.info_idx = info_idx
        self.h: NDArray[np.int_] = h
        self.m, self.n = h.shape
        self.k = self.n - self.m if info_idx is None else np.sum(info_idx)
        self.max_iter = max_iter
        self.percent_flipped = percent_flipped

    def decode(self, channel_word: NDArray[np.float_]) \
            -> tuple[NDArray[np.int_], bool, int, NDArray[np.int_], NDArray[np.int_]]:
        """
        decode a sequence received from the channel

        :param channel_word: a sequence of n bit samples from the channel, or LLR values
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
            - syndrome
            - a measure of validity of each vnode, lower is better
        """
        if len(channel_word) != self.n:
            raise IncorrectLength("incorrect block size")
        if min(channel_word) < 0:  # LLR values were given
            channel_word = np.array(channel_word < 0, dtype=np.int_)
        else:
            channel_word = channel_word.astype(np.int_)
        vnode_validity = np.zeros(self.n, dtype=np.int_)
        for iteration in range(self.max_iter):
            syndrome = self.h @ channel_word % 2
            if not syndrome.any():  # no errors detected, exit
                break
            # for each vnode how many equations are failed
            vnode_validity: NDArray[np.int_] = syndrome @ self.h
            num_suspected_vnodes = sum(vnode_validity > 0)
            num_flip_bits = 1#max(1, num_suspected_vnodes//self.percent_flipped)  # flip 10% of the suspected bits
            flip_bits = np.argpartition(vnode_validity,-num_flip_bits)[-num_flip_bits:]
            channel_word[flip_bits] = 1 - channel_word[flip_bits]

        return channel_word, not syndrome.any(), iteration+1, syndrome, vnode_validity

    def info_bits(self, estimate: NDArray[np.int_]) -> NDArray[np.int_]:
        """extract information bearing bits from decoded estimate, assuming info bits indices were specified"""
        if self.info_idx is not None:
            return estimate[self.info_idx]
        else:
            raise InfoBitsNotSpecified("decoder cannot tell info bits")
