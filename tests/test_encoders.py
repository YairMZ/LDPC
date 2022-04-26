from ldpc.encoder import EncoderG, EncoderTriangularH
import pytest
from ldpc.utils import NonBinaryMatrix, AList, IncorrectLength
import numpy as np
from bitstring import Bits
import numpy.typing as npt


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
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0, 1])
        encoded = np.matmul(bits, g)
        res = enc.encode(Bits(bits))
        assert res == Bits(encoded)

    def test_incorrect_length(self) -> None:
        g = AList.from_file("tests/test_data/Hamming_7_4_g.alist").to_array()
        enc = EncoderG(g)
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0])
        with pytest.raises(IncorrectLength):
            enc.encode(Bits(bits))


class TestEncoderTriangularH:
    def test_non_binary_matrix(self) -> None:
        mat = np.arange(1, 5).reshape((2, 2))
        with pytest.raises(NonBinaryMatrix):
            EncoderTriangularH(mat)

    def test_params(self) -> None:
        h = AList.from_file("tests/test_data/systematic_4098_3095.alist").to_array()
        enc = EncoderTriangularH(h)
        assert enc.n == 4098
        assert enc.m == 3095
        assert enc.k == 4098-3095
        np.testing.assert_array_equal(h, enc.h)  # type: ignore

    def test_encoding(self) -> None:
        h = AList.from_file("tests/test_data/systematic_4098_3095.alist").to_array()
        enc = EncoderTriangularH(h)
        bits: npt.NDArray[np.int_] = np.random.randint(2, size=enc.k)
        encoded = enc.encode(Bits(bits))
        s = np.mod(np.matmul(h, encoded), 2)
        assert s.max() == 0
        assert s.min() == 0

    def test_incorrect_length(self) -> None:
        h = AList.from_file("tests/test_data/systematic_4098_3095.alist").to_array()
        enc = EncoderTriangularH(h)
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0])
        with pytest.raises(IncorrectLength):
            enc.encode(Bits(bits))
