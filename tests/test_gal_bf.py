import numpy as np
import pytest
from ldpc.utils import IncorrectLength, QCFile
from ldpc.decoder import GalBfDecoder, InfoBitsNotSpecified
import numpy.typing as npt


class TestGalBfDecoder:
    def test_incorrect_length(self) -> None:
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = GalBfDecoder(h=h, max_iter=20, info_idx=np.array([True] * 324 + [False] * 324))
        bits: npt.NDArray[np.int_] = np.array([1, 1, 0], dtype=np.int_)
        with pytest.raises(IncorrectLength):
            decoder.decode(bits)  # type: ignore

    def test_decoder(self) -> None:
        info_bits = np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore
        encoded_ref = np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore

        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = GalBfDecoder(h=h, max_iter=2000, info_idx=np.array([True] * 324 + [False] * 324))
        decoded = np.zeros_like(encoded_ref)
        decoded_info = np.zeros_like(info_bits)
        rng = np.random.default_rng()
        no_errors = 1
        for frame_idx in range(len(encoded_ref) // decoder.n):
            corrupted = encoded_ref[frame_idx * decoder.n: (frame_idx + 1) * decoder.n].copy()
            error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
            corrupted[error_idx] = 1 - corrupted[error_idx]

            decoder_output = decoder.decode(corrupted)
            decoded[frame_idx * decoder.n: (frame_idx + 1) * decoder.n] = decoder_output[0]
            decoded_info[frame_idx * decoder.k: (frame_idx + 1) * decoder.k] = decoder.info_bits(decoder_output[0])
            assert decoder_output[1] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0
