from __future__ import annotations
import itertools
import bitstring
from typing import Union


class Frame:
    """Frame objects holds binary frames for simulation. Shouldn't be instantiated on is own, use hte manager."""
    uid_generator = itertools.count()

    def __init__(self, bits: bitstring.Bits) -> None:
        """
        :param bits: frame bits
        """
        self.bits = bits
        self.uid = next(Frame.uid_generator)

    def __str__(self) -> str:
        return "id: " + str(self.uid)

    def __eq__(self, other: object) -> bool:
        """Only bits are compared not uid"""
        if not isinstance(other, Frame):
            raise NotImplementedError
        return self.bits == other.bits  # type: ignore


class FramesManager:
    """The class holds all frames in a dictionary with uid as key.
    It also holds a list of tuples, where each tuple contains a TX frame and a corresponding RX frame."""
    def __init__(self) -> None:
        self.frames_dict: dict[int, Frame] = {}
        self.frame_pairs: set[tuple[int, int]] = set()

    def register_frame(self, frame: Frame) -> None:
        """register frame to have a dict of all frames"""
        self.frames_dict[frame.uid] = frame

    def register_pair(self, tx_frame: Union[int, Frame], rx_frame: Union[int, Frame]) -> None:
        """register pair as a tx, rx pair
        :param tx_frame: frame object or frame uid
        :param rx_frame: frame object or frame uid
        """
        tx_frame_id: int = tx_frame.uid if isinstance(tx_frame, Frame) else tx_frame
        rx_frame_id: int = rx_frame.uid if isinstance(rx_frame, Frame) else rx_frame
        self.frame_pairs.add((tx_frame_id, rx_frame_id))

    def create_frame(self, bits: bitstring.Bits) -> Frame:
        frame = Frame(bits)
        self.register_frame(frame)
        return frame

    def copy_frame(self, frame: Frame) -> Frame:
        """Note the uid isn't copied"""
        return self.create_frame(frame.bits)
