from __future__ import annotations
import numpy as np
import itertools
from typing import Any, Optional, Tuple
from functools import total_ordering
from abc import ABC, abstractmethod
import numpy.typing as npt
from ldpc.decoder.channel_models import ChannelModel
from numba import jit


__all__ = ["Node", "CNode", "VNode"]


@jit(nopython=True, cache=True)  # type: ignore
def c_message(requester_uid: int, senders: Tuple[int], received_messages: Tuple[float]) -> np.float_:
    q: npt.NDArray[np.float_] = np.array([msg for uid, msg in zip(senders, received_messages) if uid != requester_uid])
    return -np.prod(np.sign(q)) * np.log(  # type: ignore
        np.maximum(np.tanh(
            sum(
                -np.log(np.maximum(np.tanh(np.absolute(q) / 2), 1e3 * np.finfo(np.float_).eps))
            ) / 2), 1e3 * np.finfo(np.float_).eps))


@total_ordering  # type: ignore
class Node(ABC):
    """Base class VNodes anc CNodes.
    Derived classes are expected to implement an "initialize" and  method a "message" which should return the message to
    be passed on the graph.
    Nodes are ordered and deemed equal according to their ordering_key.
    """
    _uid_generator = itertools.count()

    def __init__(self, name: str = "", ordering_key: Optional[int] = None) -> None:
        """
        :param name: name of node
        """
        self.uid = next(Node._uid_generator)
        self.name = name or str(self.uid)
        self.ordering_key = ordering_key if ordering_key is not None else self.uid
        self.neighbors: dict[int, Node] = {}  # keys as senders uid
        self.received_messages: dict[int, np.float_] = {}  # keys as senders uid, values as messages

    def register_neighbor(self, neighbor: Node) -> None:
        self.neighbors[neighbor.uid] = neighbor

    def __str__(self) -> str:
        return self.name or str(self.uid)

    def get_neighbors(self) -> list[int]:
        """
        :return: The method returns a list of uid of neighbors
        """
        return list(self.neighbors.keys())

    def receive_messages(self) -> None:
        """When called, the node will request messages from all of it neighbors"""
        for node_id, node in self.neighbors.items():
            self.received_messages[node_id] = node.message(self.uid)

    @abstractmethod
    def message(self, requester_uid: int) -> np.float_:
        """Used to return a message to the requesting node"""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Used for initializing nodes to process new channel symbols"""
        pass

    def __hash__(self) -> int:
        return self.uid

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.ordering_key == other.ordering_key

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.ordering_key < other.ordering_key


class CNode(Node):
    """Check nodes in Tanner graph"""

    def __init__(self, name: str = "", ordering_key: Optional[int] = None,  decoder: Optional[str] = "BP") -> None:
        """
        :param ordering_key: used to order nodes per their order in the parity check matrix
        :param name: optional name of node
        :param decoder: must be either "BP" or "MS" for min-sum decoder
        """
        self.decoder_type = decoder
        super().__init__(name, ordering_key)

    def initialize(self) -> None:
        """
        clear received messages
        """
        self.received_messages = {node_uid: 0 for node_uid in self.neighbors}  # type: ignore

    def message(self, requester_uid: int) -> np.float_:
        """
        pass messages from c-nodes to v-nodes
        :param requester_uid: uid of requesting v-node
        """
        if self.decoder_type == "MS":
            q: npt.NDArray[np.float_] = np.array([msg for uid, msg in self.received_messages.items() if uid != requester_uid])
            return np.prod(np.sign(q)) * np.absolute(q).min()   # type: ignore

        # full BP
        return c_message(requester_uid, tuple(self.received_messages.keys()), tuple(self.received_messages.values()))  # type: ignore

        # def phi(x: npt.NDArray[np.float_]) -> npt.NDArray[np.float_]:
        #     """see sources for definition and reasons for use of this function"""
        #     return -np.log(np.maximum(np.tanh(x / 2), 1e3 * np.finfo(np.float_).eps))
        # return np.prod(np.sign(q))*phi(sum(phi(np.absolute(q))))  # type: ignore

        # return -np.prod(np.sign(q)) * np.log(
        #     np.maximum(np.tanh(
        #         sum(
        #             -np.log(np.maximum(np.tanh(np.absolute(q) / 2), 1e3 * np.finfo(np.float_).eps))
        #         ) / 2), 1e3 * np.finfo(np.float_).eps))


class VNode(Node):
    """Variable nodes in Tanner graph"""
    def __init__(self, ordering_key: int, name: str = "", channel_model: Optional[ChannelModel] = None):
        """
        :param channel_model: a function which receives channel outputs anr returns relevant message
        :param ordering_key: used to order nodes per their order in the parity check matrix
        :param name: optional name of node
        """
        self.channel_model: Optional[ChannelModel] = channel_model
        self.channel_symbol: np.float_ = None  # type: ignore
        self.channel_llr: np.float_ = None  # type: ignore
        super().__init__(name, ordering_key)

    def initialize(self, channel_symbol: np.float_) -> None:  # type: ignore
        """
        clear received messages and initialize channel llr with channel bit
        :param channel_symbol: bit received from channel, currently assumes hard inputs.
        """
        self.channel_symbol = channel_symbol
        if self.channel_model is not None:
            self.channel_llr = self.channel_model(channel_symbol)
        else:
            self.channel_llr = channel_symbol
        self.received_messages = {node_uid: 0 for node_uid in self.neighbors}  # type: ignore

    def message(self, requester_uid: int) -> np.float_:
        """
        pass messages from v-nodes to c-nodes
        :param requester_uid: uid of requesting c-node
        """
        return self.channel_llr + sum(msg for uid, msg in self.received_messages.items() if uid != requester_uid)

    def estimate(self) -> np.float_:
        """provide a soft bit estimate"""
        return self.channel_llr + sum(self.received_messages.values())
