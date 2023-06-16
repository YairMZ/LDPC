import numpy as np
from typing import Callable

__all__ = ["ChannelModel", "bsc_llr", "InfoBitsNotSpecified", "awgn_llr"]

ChannelModel = Callable[[np.float_], np.float_]


class InfoBitsNotSpecified(Exception):
    """Raised when a non-binary matrix is used while a binary one expected"""
    pass


def bsc_llr(p: float) -> ChannelModel:
    """
    bsc llr is defined as:
        L(c_i) = log(Pr(c_i=0| y_i) / Pr(c_i=1| y_i)) = (-1)^y log((1-p)/p)
    :param float p: the llr is parameterized by the bit flip probability of the channel p.
    :returns: return a callable which accepts a single argument - y_i (a bit from the channel), and returns its llr
    """
    return lambda y: np.power(-1, y) * np.log((1-p)/p)  # type: ignore

def awgn_llr(sigma: float):
    """
    awgn llr is defined as:
        x_i = 1 - 2 * c_i
        y_i = x_i + n_i
        L(y_i) = log(Pr(c_i=0| y_i) / Pr(c_i=1| y_i)) = 2 * y_i / sigma^2
    :param float sigma: the llr is parameterized by the standard deviation of the noise sigma.
    :returns: return a callable which accepts a single argument - y_i noisy channel symbol, and returns its llr
    """
    return lambda y: 2 * y / np.power(sigma, 2)  # type: ignore

# Simply add more channel models by writing a function which receives a channel symbol as input and returns an LLR as
# output
