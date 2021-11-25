from .graph import TannerGraph
from numpy.typing import ArrayLike, NDArray
import numpy as np
from collections.abc import Sequence
from .channel_models import ChannelModel

__all__ = ["LogSpaDecoder"]


class LogSpaDecoder:
    """Decode codewords according to Log-SPA version of the belief propagation algorithm"""
    def __init__(self, channel_model: ChannelModel, h: ArrayLike, max_iter: int):
        self.h = np.array(h)
        self.graph = TannerGraph.from_biadjacency_matrix(h=self.h, channel_model=channel_model)
        self.n = len(self.graph.v_nodes)
        self.max_iter = max_iter

    def decode(self, channel_word: Sequence[int]) -> tuple[NDArray[np.int_], NDArray[np.float_], bool]:
        """
        decode a sequence received from the channel

        :param channel_word: a sequence of n bit samples from the channel
        :return: return a tuple (estimated_bits, llr, decode_success)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success isa boolean flag stating of the estimated_bits form a valid  code word
        """
        if len(channel_word) != self.n:
            raise ValueError("incorrect block size")

        # initial step
        for idx, vnode in enumerate(self.graph.ordered_v_nodes()):
            vnode.initialize(channel_word[idx])
        for cnode in self.graph.c_nodes.values():  # send initial channel based messages to check nodes
            cnode.receive_messages()

        for _ in range(self.max_iter):
            # Check to Variable Node Step(horizontal step):
            for vnode in self.graph.v_nodes.values():
                vnode.receive_messages()
            # Variable to Check Node Step(vertical step)
            for cnode in self.graph.c_nodes.values():
                cnode.receive_messages()

            # Check stop condition
            llr = np.array([node.estimate() for node in self.graph.ordered_v_nodes()])
            estimate = np.array([1 if node_llr < 0 else 0 for node_llr in llr], dtype=np.int_)
            syndrome = self.h.dot(estimate) % 2
            if not syndrome.any():
                break

        return estimate, llr, not syndrome.any()
