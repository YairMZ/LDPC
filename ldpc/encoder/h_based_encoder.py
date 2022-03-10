from ldpc.encoder.base_encoder import Encoder
import numpy.typing as npt
import numpy as np
from bitstring import Bits
from ldpc.utils.custom_exceptions import IncorrectLength, NonBinaryMatrix


class EncoderTriangularH(Encoder):
    """Encoder which encodes using back-substitution, given a parity check matrix in lower triangular form
    based on: "Efficient Encoding of Low-Density Parity-Check Codes"
    """
    def __init__(self, h: npt.NDArray[np.int_]) -> None:
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
        super().__init__(k, n)

    def encode(self, information_bits: Bits) -> Bits:
        if len(information_bits) != self.k:
            raise IncorrectLength
        info: npt.NDArray[np.int_] = np.array(information_bits, dtype=np.int_)
        encoded: npt.NDArray[np.int_] = np.zeros(self.n, dtype=np.int_)
        encoded[:self.k] = info
        p: npt.NDArray[np.int_] = np.mod(np.matmul(self.h[:, :self.k], info), 2)
        for l in range(self.m):
            for j in range(l):
                p[l] = (p[l] + self.h[l, j + self.k] * p[j]) % 2
        encoded[self.k:] = p
        return Bits(encoded)
