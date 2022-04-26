import numpy as np
from bitstring import Bits, BitArray
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
import pytest
from ldpc.utils import IncorrectLength, QCFile
from ldpc.decoder import LogSpaDecoder, bsc_llr, InfoBitsNotSpecified, DecoderWiFi
import numpy.typing as npt


class TestEncoder802_11:
    def test_incorrect_length(self) -> None:
        enc = EncoderWiFi(WiFiSpecCode.N648_R12)
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0])
        with pytest.raises(IncorrectLength):
            enc.encode(Bits(bits))

    def test_encoding_648_r12(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_))  # type: ignore
        enc = EncoderWiFi(WiFiSpecCode.N648_R12)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_648_r56(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R56.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R56.csv', delimiter=',', dtype=np.int_))  # type: ignore
        enc = EncoderWiFi(WiFiSpecCode.N648_R56)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_1296_r23(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N1296_R23.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N1296_R23.csv', delimiter=',', dtype=np.int_))  # type: ignore
        enc = EncoderWiFi(WiFiSpecCode.N1296_R23)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference

    def test_encoding_1944_r34(self) -> None:
        # comparing encodings with reference implementation by: https://github.com/tavildar/LDPC
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N1944_R34.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N1944_R34.csv', delimiter=',', dtype=np.int_))  # type: ignore
        enc = EncoderWiFi(WiFiSpecCode.N1944_R34)

        encoded = Bits()
        for frame_idx in range(len(info_bits)//enc.k):
            encoded += enc.encode(info_bits[frame_idx*enc.k: (frame_idx+1)*enc.k])
        assert sum(encoded_ref ^ encoded) == 0  # assert Hamming distance of my implementation with reference


class TestDecoder802_11:
    def test_incorrect_length(self) -> None:
        p = 0.1
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = LogSpaDecoder(h=h, max_iter=20, channel_model=bsc_llr(p=p))
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0], dtype=np.int_)
        with pytest.raises(IncorrectLength):
            decoder.decode(bits)  # type: ignore

    def test_decoder_648_r12(self) -> None:
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_))  # type: ignore
        p = 0.01

        corrupted = BitArray(encoded_ref)
        no_errors = int(len(corrupted) * p)
        rng = np.random.default_rng()
        error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
        for idx in error_idx:
            corrupted[idx] = not corrupted[idx]

        decoder = DecoderWiFi(spec=WiFiSpecCode.N648_R12, max_iter=20, channel_model=bsc_llr(p=p))
        decoded = Bits()
        decoded_info = Bits()
        for frame_idx in range(len(corrupted) // decoder.n):
            decoder_output = decoder.decode(corrupted[frame_idx * decoder.n: (frame_idx + 1) * decoder.n])
            decoded += decoder_output[0]
            decoded_info += decoder.info_bits(decoder_output[0])
            assert decoder_output[2] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0

    def test_ms_decoder_1296_r23(self) -> None:
        info_bits = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N1296_R23.csv', delimiter=',', dtype=np.int_))  # type: ignore
        encoded_ref = Bits(auto=np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N1296_R23.csv', delimiter=',', dtype=np.int_))  # type: ignore
        p = 0.01

        corrupted = BitArray(encoded_ref)
        no_errors = int(len(corrupted) * p)
        rng = np.random.default_rng()
        error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
        for idx in error_idx:
            corrupted[idx] = not corrupted[idx]

        decoder = DecoderWiFi(spec=WiFiSpecCode.N1296_R23, max_iter=20, channel_model=bsc_llr(p=p),decoder_type="MS")
        decoded = Bits()
        decoded_info = Bits()
        for frame_idx in range(len(corrupted) // decoder.n):
            decoder_output = decoder.decode(corrupted[frame_idx * decoder.n: (frame_idx + 1) * decoder.n])
            decoded += decoder_output[0]
            decoded_info += decoder.info_bits(decoder_output[0])
            assert decoder_output[2] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0

    def test_decoder_no_info(self) -> None:
        p = 0.1
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = LogSpaDecoder(h=h, max_iter=20, channel_model=bsc_llr(p=p))
        estimate: npt.NDArray[np.int_] = np.array(Bits(bytes=bytes(list(range(81)))), np.int_)
        with pytest.raises(InfoBitsNotSpecified):
            decoder.info_bits(estimate)
