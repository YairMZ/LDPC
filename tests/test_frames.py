from ldpc.utils import FramesManager
from bitstring import Bits


class TestFrames:
    def test_frame_equality(self) -> None:
        fm = FramesManager()
        bits = Bits(bytes=b"\x01\x02")
        tx_frame = fm.create_frame(bits)
        rx_frame = fm.copy_frame(tx_frame)
        assert tx_frame == rx_frame

    def test_frames_registration(self) -> None:
        fm = FramesManager()
        bits = Bits(bytes=b"\x01\x02")
        tx_frame = fm.create_frame(bits)
        assert tx_frame.uid in fm.frames_dict and fm.frames_dict.get(tx_frame.uid) is tx_frame

    def test_pairs_registration(self) -> None:
        fm = FramesManager()
        bits = Bits(bytes=b"\x01\x02")
        tx_frame = fm.create_frame(bits)
        rx_frame = fm.copy_frame(tx_frame)
        fm.register_pair(tx_frame, rx_frame)
        assert (tx_frame.uid, rx_frame.uid) in fm.frame_pairs
