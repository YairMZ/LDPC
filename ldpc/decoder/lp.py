from numpy.typing import NDArray
import numpy as np
from typing import Optional, Union
from ldpc.utils import IncorrectLength
from ldpc.decoder.common import InfoBitsNotSpecified
from enum import Enum, auto
from scipy.sparse import csr_matrix


class admm_decoder:
    """LP based decoder for LDPC codes.
    Uses the ADMM algorithm to solve the LP problem.
    Based on the paper "Reduced-Complexity Linear Programming Decoding Based on ADMM for LDPC Codes" by
    Haoyuan Wei, Xiaopeng Jiao, and Jianjun Mu
    """
    def __init__(self, h: NDArray, mu:float):
        self.h: NDArray[np.int_] = h
        self.m, self.n = h.shape
        self.projection_matrices: list[csr_matrix] = self._generate_projection_matrices()
        self.mu = mu
        self.variable_degree = np.sum(self.h, axis=0)

    def decode(self, channel_llr: NDArray[np.float_], prior_reliability: Optional[NDArray[np.float_]] = None) \
            -> tuple[NDArray[np.int_], bool, int, NDArray[np.int_], NDArray[np.int_]]:
        """
        decode a sequence received from the channel

        :param channel_llr: a sequence of channel LLR values
        :param prior_reliability: an array of prior reliabilities for each bit, 0 is no prior reliability, positive means more
        reliable, negative means less reliable
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
            - syndrome
            - a measure of validity of each vnode, lower is better
        """
        lambda_ = np.zeros(self.m)
        z = np.ones(self.m) * 0.5
        w_old = np.ones(self.m) * 0.5

        for i in range(self.n):
            t = np.sum(z-lambda_/self.mu) - channel_llr[i]/self.mu
            if t >= self.variable_degree[i]:
                v = 



    def _generate_projection_matrices(self) -> list[csr_matrix]:
        """generate projection matrices for the LP problem"""
        check_degree = np.sum(self.h, axis=1)
        projections = [None]*self.m
        for idx in range(self.m):
            projections[idx] = np.zeros((check_degree[idx], self.n))
            col_idx = 0
            for col in range(self.n):
                if self.h[idx, col] == 1:
                    projections[idx][col_idx, col] = 1
                    col_idx += 1
            projections[idx] = csr_matrix(projections[idx])
        return projections