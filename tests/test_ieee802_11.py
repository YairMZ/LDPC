import numpy as np
from bitstring import Bits
from encoder import WiFiSpecCode, EncoderWiFi
from utils import QCFile
import pytest
from utils import IncorrectLength


class TestEncoder802_11:
    def test_incorrect_length(self) -> None:
        enc = EncoderWiFi(WiFiSpecCode.N648_R12)
        bits = np.array([1, 1, 0])
        with pytest.raises(IncorrectLength):
            enc.encode(Bits(bits))

    def test_encoding_648_r12(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',',
                                            dtype=np.int_))
        encoded_ref = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',',
                                              dtype=np.int_))
        enc = EncoderWiFi(WiFiSpecCode.N648_R12)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_648_r56(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/info_bits_N648_R56.csv', delimiter=',',
                                            dtype=np.int_))
        encoded_ref = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/encoded_N648_R56.csv', delimiter=',',
                                              dtype=np.int_))
        enc = EncoderWiFi(WiFiSpecCode.N648_R56)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_1296_r23(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/info_bits_N1296_R23.csv', delimiter=',',
                                            dtype=np.int_))
        encoded_ref = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/encoded_N1296_R23.csv', delimiter=',',
                                              dtype=np.int_))
        enc = EncoderWiFi(WiFiSpecCode.N1296_R23)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_1944_r34(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/info_bits_N1944_R34.csv', delimiter=',',
                                            dtype=np.int_))
        encoded_ref = Bits(auto=np.genfromtxt('tests/test_data/ieee_802_11/encoded_N1944_R34.csv', delimiter=',',
                                              dtype=np.int_))
        enc = EncoderWiFi(WiFiSpecCode.N1944_R34)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference
