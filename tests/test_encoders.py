from encoder import EncoderG
import numpy as np
import pytest
from utils import NonBinaryMatrix, AList, IncorrectLength
import numpy as np
from bitstring import Bits


class TestEncoderG:
    def test_non_binary_matrix(self) -> None:
        mat = np.arange(1, 5).reshape((2, 2))
        with pytest.raises(NonBinaryMatrix):
            EncoderG(mat)

    def test_params(self) -> None:
        g = AList.from_file("tests/test_data/Hamming_7_4_g.alist").to_array()
        enc = EncoderG(g)
        assert enc.n == 7
        assert enc.k == 4
        np.testing.assert_array_equal(g, enc.generator)  # type: ignore

    def test_encoding(self) -> None:
        g = AList.from_file("tests/test_data/Hamming_7_4_g.alist").to_array()
        enc = EncoderG(g)
        bits = np.array([1, 1, 0, 1])
        encoded = np.matmul(bits, g)
        res = enc.encode(Bits(bits))
        assert res == Bits(encoded)

    def test_incorrect_length(self) -> None:
        g = AList.from_file("tests/test_data/Hamming_7_4_g.alist").to_array()
        enc = EncoderG(g)
        bits = np.array([1, 1, 0])
        with pytest.raises(IncorrectLength):
            enc.encode(Bits(bits))
