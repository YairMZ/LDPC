from __future__ import annotations
import itertools
import bitstring


class Frame:
    """Frame objects holds binary frames for simulation"""
    uid_generator = itertools.count()

    def __init__(self, bits: bitstring.Bits) -> None:
        """
        :param bits: frame bits
        """
        self.bits = bits
        self.uid = next(Frame.uid_generator)

    def __str__(self) -> str:
        return "id: " + str(self.uid)


class FramesManager:
    """The class holds all frames in a dictionary with uid as key.
    It also holds a list of tuples, where each tuple contains a TX frame and a corresponding RX frame."""
    def __init__(self) -> None:
        self.frames_dict: dict[int, Frame] = {}
        self.frame_pairs: list[tuple[int, int]] = []

    def register_frame(self, frame: Frame) -> None:
        self.frames_dict[frame.uid] = frame

    def register_pair(self, tx_frame_id: int, rx_frame_id: int) -> None:
        self.frame_pairs.append((tx_frame_id, rx_frame_id))

    def create_frame(self, bits: bitstring.Bits) -> Frame:
        frame = Frame(bits)
        self.register_frame(frame)
        return frame

    def copy_frame(self, frame: Frame) -> Frame:
        return self.create_frame(frame.bits)
