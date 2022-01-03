import bitstring

from ldpc.encoder.base_encoder import Encoder
import numpy as np
import numpy.typing as npt
from bitstring import Bits
from ldpc.utils.custom_exceptions import NonBinaryMatrix, IncorrectLength


class EncoderG(Encoder):
    """Encoder which is based on multiplying the generator matrix by message bits"""
    def __init__(self, generator: npt.NDArray[np.int_]) -> None:
        """
        :param generator: generator matrix, should be a binary matrix
        :raises: NonBinaryMatrix if matrix elements are non-binary
        """
        self.generator = generator
        if generator.max(initial=0) > 1 or generator.min(initial=1) < 0:
            raise NonBinaryMatrix
        k, n = generator.shape
        super().__init__(k, n)

    def encode(self, information_bits: Bits) -> Bits:
        if len(information_bits) != self.k:
            raise IncorrectLength
        return bitstring.Bits(np.matmul(np.array(information_bits, dtype=np.int_), self.generator))
