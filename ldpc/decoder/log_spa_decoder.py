from ldpc.decoder.graph import TannerGraph
from numpy.typing import ArrayLike, NDArray
import numpy as np
from collections.abc import Sequence
from ldpc.decoder.channel_models import ChannelModel
from typing import Optional
from bitstring import Bits
from ldpc.utils import IncorrectLength
from ldpc.decoder.node import VNode
import numpy.typing as npt

__all__ = ["LogSpaDecoder", "InfoBitsNotSpecified"]


class InfoBitsNotSpecified(Exception):
    """Raised when a non-binary matrix is used while a binary one expected"""
    pass


class LogSpaDecoder:
    """Decode codewords according to Log-SPA version of the belief propagation algorithm"""
    def __init__(self, h: ArrayLike, max_iter: int, info_idx: Optional[NDArray[np.bool_]] = None,
                 channel_model: Optional[ChannelModel] = None):
        """

        :param h:the parity check code matrix of the code
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param info_idx: a boolean array representing the indices of information bits in the code
        :param channel_model: optional, a callable which receives a channel input, and returns the channel llr. If not
        specified, llr is expected to be fed into the decoder.
        """
        self.info_idx = info_idx
        self.h: npt.NDArray[np.int_] = np.array(h)
        self.graph = TannerGraph.from_biadjacency_matrix(h=self.h, channel_model=channel_model)
        self.n = len(self.graph.v_nodes)
        self.max_iter = max_iter

    def decode(self, channel_word: Sequence[np.float_], max_iter: Optional[int] = None) \
            -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int]:
        """
        decode a sequence received from the channel

        :param channel_word: a sequence of n bit samples from the channel
        :param max_iter: maximal iterations of decoder. If None, self.max_iter is used as default.
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
        """
        if len(channel_word) != self.n:
            raise IncorrectLength("incorrect block size")

        # initial step
        for idx, vnode in enumerate(self.graph.ordered_v_nodes()):
            vnode.initialize(channel_word[idx])
        for cnode in self.graph.c_nodes.values():  # send initial channel based messages to check nodes
            cnode.receive_messages()

        if max_iter is None:
            max_iter = self.max_iter
        for iteration in range(max_iter):
            # Check to Variable Node Step(horizontal step):
            for vnode in self.graph.v_nodes.values():
                vnode.receive_messages()
            # Variable to Check Node Step(vertical step)
            for cnode in self.graph.c_nodes.values():
                cnode.receive_messages()

            # Check stop condition
            llr: npt.NDArray[np.float_] = np.array([node.estimate() for node in self.graph.ordered_v_nodes()])
            estimate: npt.NDArray[np.int_] = np.array(llr < 0, dtype=np.int_)
            # np.array([1 if node_llr < 0 else 0 for node_llr in llr], dtype=np.int_)
            syndrome = self.h.dot(estimate) % 2
            if not syndrome.any():
                break

        return estimate, llr, not syndrome.any(), iteration

    def info_bits(self, estimate: NDArray[np.int_]) -> Bits:
        """extract information bearing bits from decoded estimate, assuming info bits indices were specified"""
        if self.info_idx is not None:
            return Bits(auto=estimate[self.info_idx])
        else:
            raise InfoBitsNotSpecified("decoder cannot tell info bits")

    def ordered_vnodes(self) -> list[VNode]:
        """getter for ordered graph v-nodes"""
        return self.graph.ordered_v_nodes()

    def update_channel_model(self, channel_models: dict[int, ChannelModel]) -> None:
        """
        rectify channel model for specific vnodes

        :param channel_models: a dictionary with keys as node uid, and value as a new channel model
        """
        for uid, model in channel_models.items():
            node = self.graph.v_nodes.get(uid)
            if isinstance(node, VNode):
                node.channel_model = model
