from __future__ import annotations
import numpy as np
import itertools
from typing import Any, Optional
from functools import total_ordering
from abc import ABC, abstractmethod
import numpy.typing as npt
from ldpc.decoder.channel_models import ChannelModel


__all__ = ["Node", "CNode", "VNode"]


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
        self.name = name if name else str(self.uid)
        self.ordering_key = ordering_key if ordering_key is not None else self.uid
        self.neighbors: dict[int, Node] = {}  # keys as senders uid
        self.received_messages: dict[int, Any] = {}  # keys as senders uid, values as messages

    def register_neighbor(self, neighbor: Node) -> None:
        self.neighbors[neighbor.uid] = neighbor

    def __str__(self) -> str:
        if self.name:
            return self.name
        else:
            return str(self.uid)

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
    def message(self, requester_uid: int) -> Any:
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
    def initialize(self) -> None:
        """
        clear received messages
        """
        self.received_messages = {node_uid: 0 for node_uid in self.neighbors}

    def message(self, requester_uid: int) -> np.float_:
        """
        pass messages from c-nodes to v-nodes
        :param requester_uid: uid of requesting v-node
        """
        def phi(x: npt.NDArray[np.float_]) -> Any:
            """see sources for definition and reasons fr use of this function"""
            return -np.log(np.tanh(x/2))
        q = np.array([msg for uid, msg in self.received_messages.items() if uid != requester_uid])
        return np.prod(np.sign(q))*phi(np.sum(phi(np.absolute(q))))  # type: ignore


class VNode(Node):
    """Variable nodes in Tanner graph"""
    def __init__(self, channel_model: ChannelModel, ordering_key: int, name: str = ""):
        """
        :param channel_model: a function which receives channel outputs anr returns relevant message
        :param ordering_key: used to order nodes per their order in the parity check matrix
        :param name: optional name of node
        """
        self.channel_model: ChannelModel = channel_model
        self.channel_symbol: int = None  # type: ignore # currently assuming hard channel symbols
        self.channel_llr: np.float_ = None  # type: ignore
        super().__init__(name, ordering_key)

    def initialize(self, channel_symbol: int) -> None:  # type: ignore
        """
        clear received messages and initialize channel llr with channel bit
        :param channel_symbol: bit received from channel. currently assumes hard inputs.
        """
        self.channel_symbol = channel_symbol
        self.channel_llr = self.channel_model(channel_symbol)
        self.received_messages = {node_uid: 0 for node_uid in self.neighbors}

    def message(self, requester_uid: int) -> np.float_:
        """
        pass messages from v-nodes to c-nodes
        :param requester_uid: uid of requesting c-node
        """
        return self.channel_llr + np.sum(  # type: ignore
            [msg for uid, msg in self.received_messages.items() if uid != requester_uid]
        )

    def estimate(self) -> np.float_:
        """provide a soft bit estimate"""
        return self.channel_llr + np.sum(list(self.received_messages.values()))  # type: ignore
