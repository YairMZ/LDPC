import numpy as np
import pytest
from ldpc.utils import IncorrectLength, QCFile
from ldpc.decoder import PbfDecoder, PbfVariant
import numpy.typing as npt


class TestPbfDecoder:
    def test_incorrect_length(self) -> None:
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = PbfDecoder(h=h, max_iter=20, decoder_variant=PbfVariant.PPBF)
        bits: npt.NDArray[np.int_] = np.array([1, 1, -1], dtype=np.int_)
        with pytest.raises(IncorrectLength):
            decoder.decode(bits,1)  # type: ignore

    def test_missing_p_vec(self) -> None:
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = PbfDecoder(h=h, max_iter=20, decoder_variant=PbfVariant.PPBF)
        bits = np.ones(648, dtype=np.int_)
        with pytest.raises(ValueError):
            decoder.decode(bits,1)

    def test_invalid_p_vec(self) -> None:
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = PbfDecoder(h=h, max_iter=20, decoder_variant=PbfVariant.PPBF)
        bits = np.ones(648, dtype=np.int_)
        with pytest.raises(ValueError):  # p_vec too short
            p_vec = np.ones(10, dtype=np.int_)
            decoder.decode(bits, 1,p_vector=p_vec)
        with pytest.raises(ValueError):  # p_vec too long
            p_vec = np.ones(20, dtype=np.int_)
            decoder.decode(bits, 1,p_vector=p_vec)
        with pytest.raises(ValueError):  # p_vec contains negative values
            p_vec = -np.ones(14)
            decoder.decode(bits, 1,p_vector=p_vec)
        with pytest.raises(ValueError):  # p_vec contains values > 1
            p_vec = np.ones(14) * 2
            decoder.decode(bits, 1,p_vector=p_vec)


    def test_pbf(self) -> None:
        info_bits = np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore
        encoded_ref = np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore

        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()

        p_vector = np.zeros(14)
        for i in range(2, 13):
            p_vector[i] = p_vector[i - 1] + 1 / 12
        p_vector[1] = p_vector[2] / 2
        p_vector[-1] = 1

        decoder = PbfDecoder(h=h, max_iter=300, decoder_variant=PbfVariant.PPBF, info_idx=np.array(
            [True] * 324 + [False] * 324), p_vector=p_vector)
        decoded = np.zeros_like(encoded_ref)
        decoded_info = np.zeros_like(info_bits)
        rng = np.random.default_rng()
        no_errors = 1
        fer = 0
        for frame_idx in range(len(encoded_ref) // decoder.n):
            corrupted = encoded_ref[frame_idx * decoder.n: (frame_idx + 1) * decoder.n].copy()
            error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
            corrupted[error_idx] = 1 - corrupted[error_idx]
            decoder_output = decoder.decode(corrupted,1)
            decoded[frame_idx * decoder.n: (frame_idx + 1) * decoder.n] = decoder_output[0]
            decoded_info[frame_idx * decoder.k: (frame_idx + 1) * decoder.k] = decoder.info_bits(decoder_output[0])
            fer += decoder_output[2] is False
            # assert decoder_output[2] is True
        print(f"frame errors: {fer}")
        fer /= frame_idx + 1
        print(f"FER: {fer}")
        assert fer < 0.4
