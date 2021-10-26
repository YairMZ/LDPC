import bitstring

from encoder import Encoder
import numpy as np
import numpy.typing as npt
from bitstring import Bits
from utils import NonBinaryMatrix, IncorrectLength


class EncoderG(Encoder):
    def __init__(self, generator: npt.NDArray[np.int_]) -> None:
        """
        :param generator: generator matrix, should be a binary matrix
        :raises: NonBinaryMatrix if matrix elements are non-binary
        """
        self.generator = generator
        if generator.max() > 1 or generator.min() < 0:
            raise NonBinaryMatrix
        k, n = generator.shape
        super().__init__(k, n)

    def encode(self, information_bits: Bits) -> Bits:
        if len(information_bits) != self.k:
            raise IncorrectLength
        return bitstring.Bits(np.matmul(np.array(information_bits, dtype=np.int_), self.generator))
