import numpy as np
import pytest
from ldpc.utils import IncorrectLength, QCFile
from ldpc.decoder import WbfDecoder, WbfVariant, awgn_llr, bsc_llr
import numpy.typing as npt


class TestWbfDecoder:
    def test_incorrect_length(self) -> None:
        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = WbfDecoder(h=h, max_iter=20, decoder_variant=WbfVariant.WBF)
        bits: npt.NDArray[np.int_] = np.array([1, 1, -1], dtype=np.int_)
        with pytest.raises(IncorrectLength):
            decoder.decode(bits)  # type: ignore

    def test_wbf(self) -> None:
        info_bits = np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore
        encoded_ref = np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore

        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = WbfDecoder(h=h, max_iter=2000, decoder_variant=WbfVariant.WBF, info_idx=np.array([True] * 324 + [False] * 324))
        decoded = np.zeros_like(encoded_ref)
        decoded_info = np.zeros_like(info_bits)
        rng = np.random.default_rng()
        no_errors = 3
        f = no_errors/decoder.n
        channel = bsc_llr(f)

        for frame_idx in range(len(encoded_ref) // decoder.n):
            corrupted = encoded_ref[frame_idx * decoder.n: (frame_idx + 1) * decoder.n].copy()
            error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
            corrupted[error_idx] = 1 - corrupted[error_idx]
            corrupted = channel(corrupted)
            decoder_output = decoder.decode(corrupted)
            decoded[frame_idx * decoder.n: (frame_idx + 1) * decoder.n] = decoder_output[0]
            decoded_info[frame_idx * decoder.k: (frame_idx + 1) * decoder.k] = decoder.info_bits(decoder_output[0])
            assert decoder_output[1] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0

    def test_mwbf(self) -> None:
        info_bits = np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore
        encoded_ref = np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore

        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = WbfDecoder(h=h, max_iter=2000, decoder_variant=WbfVariant.MWBF, info_idx=np.array([True] * 324 + [False] * 324))
        decoded = np.zeros_like(encoded_ref)
        decoded_info = np.zeros_like(info_bits)
        rng = np.random.default_rng()
        snr = 5.5
        snr_linear = 10 ** (snr / 10)
        noise_power = 1 / snr_linear
        sigma = np.sqrt(noise_power / 2)
        channel = awgn_llr(sigma=sigma)
        baseband = 1 - 2 * encoded_ref
        noise = sigma * rng.normal(size=len(baseband))
        # channel: y_i = x_i + n_i, i.e. add noise
        noisy = baseband + noise
        channel_llr = channel(noisy)
        for frame_idx in range(len(encoded_ref) // decoder.n):
            decoder_output = decoder.decode(channel_llr[frame_idx * decoder.n: (frame_idx + 1) * decoder.n])
            decoded[frame_idx * decoder.n: (frame_idx + 1) * decoder.n] = decoder_output[0]
            decoded_info[frame_idx * decoder.k: (frame_idx + 1) * decoder.k] = decoder.info_bits(decoder_output[0])
            assert decoder_output[1] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0

    def test_mwbf_no_loop(self) -> None:
        info_bits = np.genfromtxt(
            'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore
        encoded_ref = np.genfromtxt(
            'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_)  # type: ignore

        h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
        decoder = WbfDecoder(h=h, max_iter=200, decoder_variant=WbfVariant.MWBF_NO_LOOPS, info_idx=np.array([True] * 324 + [False] * 324))
        decoded = np.zeros_like(encoded_ref)
        decoded_info = np.zeros_like(info_bits)
        rng = np.random.default_rng()
        snr = 5
        snr_linear = 10 ** (snr / 10)
        noise_power = 1 / snr_linear
        sigma = np.sqrt(noise_power / 2)
        channel = awgn_llr(sigma=sigma)
        baseband = 1 - 2 * encoded_ref
        noise = sigma * rng.normal(size=len(baseband))
        # channel: y_i = x_i + n_i, i.e. add noise
        noisy = baseband + noise
        channel_llr = channel(noisy)
        for frame_idx in range(len(encoded_ref) // decoder.n):
            decoder_output = decoder.decode(channel_llr[frame_idx * decoder.n: (frame_idx + 1) * decoder.n])
            decoded[frame_idx * decoder.n: (frame_idx + 1) * decoder.n] = decoder_output[0]
            decoded_info[frame_idx * decoder.k: (frame_idx + 1) * decoder.k] = decoder.info_bits(decoder_output[0])
            assert decoder_output[1] is True
        assert sum(encoded_ref ^ decoded) == 0
        assert sum(info_bits ^ decoded_info) == 0
