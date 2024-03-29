from ldpc.encoder.base_encoder import Encoder
from numpy.typing import NDArray
import numpy as np
from ldpc.utils.custom_exceptions import IncorrectLength, NonBinaryMatrix


class EncoderTriangularH(Encoder):
    """Encoder which encodes using back-substitution, given a parity check matrix in lower triangular form
    based on: "Efficient Encoding of Low-Density Parity-Check Codes"
    """
    def __init__(self, h: NDArray[np.int_]) -> None:
        """
        :param h: parity check matrix, should be a lower triangular binary matrix
        :raises: NonBinaryMatrix if matrix elements are non-binary
        """
        self.h = h
        if h.max(initial=0) > 1 or h.min(initial=1) < 0:
            raise NonBinaryMatrix
        m, n = h.shape
        k = n - m
        self.m = m
        # check if parity part is identity
        self.identity_p = np.array_equal(h[:, k:], np.identity(m))

        super().__init__(k, n)

    def encode(self, information_bits: NDArray[np.int_]) -> NDArray[np.int_]:
        if len(information_bits) != self.k:
            raise IncorrectLength
        encoded: NDArray[np.int_] = np.zeros(self.n, dtype=np.int_)
        encoded[:self.k] = information_bits
        p: NDArray[np.int_] = np.mod(np.matmul(self.h[:, :self.k], information_bits), 2)
        if not self.identity_p:
            for l in range(1, self.m):
                p[l] += np.mod(np.dot(self.h[l, self.k:self.k+l], p[:l]), 2)
        encoded[self.k:] = p
        return encoded
