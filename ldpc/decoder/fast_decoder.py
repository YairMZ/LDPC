from numpy.typing import ArrayLike, NDArray
import numpy as np
from collections.abc import Sequence
from ldpc.decoder.channel_models import ChannelModel
from typing import Optional
from bitstring import Bits
from ldpc.utils import IncorrectLength
import numpy.typing as npt

__all__ = ["LogSpaDecoder", "InfoBitsNotSpecified"]


class InfoBitsNotSpecified(Exception):
    """Raised when a non-binary matrix is used while a binary one expected"""
    pass


class LogSpaDecoder:
    """Decode codewords according to Log-SPA version of the belief propagation algorithm"""
    def __init__(self, channel_model: ChannelModel, h: ArrayLike, max_iter: int,
                 info_idx: Optional[NDArray[np.bool_]] = None):
        """

        :param channel_model: a callable which receives a channel input, and returns the channel llr
        :param h:the parity check code matrix of the code
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param info_idx: a boolean array representing the indices of information bits in the code
        """
        self.info_idx = info_idx
        self.h: npt.NDArray[np.int_] = np.array(h, dtype=np.int_)
        self.m, self.n = self.h.shape
        self.k = self.n - self.m
        self.column_weights = np.sum(self.h, 0, dtype=np.int_)
        self.row_weights = np.sum(self.h, 1, dtype=np.int_)
        self.max_col_weight: int = max(self.column_weights)
        self.max_row_weight: int = max(self.row_weights)
        self.col_mat: npt.NDArray[np.int_] = np.zeros((self.n, self.max_col_weight), dtype=np.int_)
        self.row_mat: npt.NDArray[np.int_] = np.zeros((self.m, self.max_row_weight), dtype=np.int_)
        for i_row in range(self.m):
            index = 0
            for i_col in range(self.n):
                if self.h[i_row, i_col] == 1:
                    self.row_mat[i_row, index] = i_col
                    index += 1
        for i_col in range(self.n):
            index = 0
            for i_row in range(self.m):
                if self.h[i_row, i_col] == 1:
                    self.col_mat[i_col, index] = i_row
                    index += 1

        # self.v_neighbors = {i: np.argwhere(self.h[:, i] == 1).flatten() for i in range(self.n)}
        # self.c_neighbors = {i: np.argwhere(self.h[i, :] == 1).flatten() for i in range(self.m)}
        self.channel_model = channel_model
        self.max_iter = max_iter

    def decode(self, channel_word: Sequence[int], max_iter: Optional[int] = None, min_sum: Optional[bool] = False) \
            -> tuple[NDArray[np.int_], NDArray[np.float_], bool, int]:
        """
        decode a sequence received from the channel

        :param channel_word: a sequence of n bit samples from the channel
        :param max_iter: maximal iterations of decoder. If None, self.max_iter is used as default.
        :param min_sum: optional, if true uses a min_sum decoder, else full Log SPA
        :return: return a tuple (estimated_bits, llr, decode_success, no_iterations)
        where:
            - estimated_bits is a 1-d np array of hard bit estimates
            - llr is a 1-d np array of soft bit estimates
            - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
            - no_iterations is the number of iterations of belief propagation before exiting the loop
        """
        if len(channel_word) != self.n:
            raise IncorrectLength("incorrect block size")
        if max_iter is None:
            max_iter = self.max_iter

        r: npt.NDArray[np.float_] = np.zeros(self.h.shape, dtype=np.float_)  # the messages r_ij.
        # r[i,j] is the message from cnode i to vnode j.
        last_r: npt.NDArray[np.float_] = np.zeros(self.h.shape, dtype=np.float_)
        channel_llr: npt.NDArray[np.float_] = self.channel_model(channel_word)
        llr: npt.NDArray[np.float_] = np.array(channel_llr)
        error_vec = np.zeros(max_iter)
        q: npt.NDArray[np.float_] = np.multiply(llr, self.h)  # the messages q_ij.
        # q[i,j] is the message from vnode j to cnode i.

        for iteration in range(max_iter):
            # alpha = np.sign(q)
            # beta = np.abs(q)

            # update r
            for p_chk_idx in range(self.m):
                for neighbor_idx in range(self.row_weights[p_chk_idx]):
                    v_node_neighbor = self.row_mat[p_chk_idx, neighbor_idx]
                    if min_sum:
                        pr = np.inf
                    else:
                        pr = 1
                        phi = 0

                    # mask = np.zeros(self.max_row_weight, dtype=bool)
                    for vnode_neighbor_idx in range(self.row_weights[p_chk_idx]):
                        if neighbor_idx == vnode_neighbor_idx:
                            continue
                        # mask[:self.row_weights[p_chk_idx]] = True
                        # mask[vnode_neighbor_idx] = False
                        # other_vnode_neighbors = self.row_mat[p_chk_idx, mask]
                        if min_sum:
                            pr = np.sign(pr) * np.sign(q[p_chk_idx, self.row_mat[p_chk_idx, vnode_neighbor_idx]]) * min(
                                abs(q[p_chk_idx, self.row_mat[p_chk_idx, vnode_neighbor_idx]]), abs(pr))
                        else:
                            pr *= np.sign(q[p_chk_idx, self.row_mat[p_chk_idx, vnode_neighbor_idx]])
                            phi += -np.log(np.tanh(np.abs(q[p_chk_idx, self.row_mat[p_chk_idx, vnode_neighbor_idx]])/2))

                    if min_sum:
                        r[p_chk_idx, v_node_neighbor] = pr
                    else:
                        r[p_chk_idx, v_node_neighbor] = pr*(-np.log(np.tanh(phi/2)))

            # update llr
            llr = channel_llr + np.sum(r, axis=0)
            # update q
            q = np.multiply(llr - r, self.h)

        # # channel llr
        # channel_llr: npt.NDArray[np.float_] = self.channel_model(channel_word)
        # # r = np.zeros(self.h.shape, dtype=np.float_)
        # q = self.h * channel_llr
        # r: npt.NDArray[np.float_] = np.zeros(self.h.shape, dtype=np.float_)
        # llr: npt.NDArray[np.float_] = np.zeros(self.n, dtype=np.float_)
        #
        # for iteration in range(max_iter):
        #     for j in range(self.m):
        #         for i in self.c_neighbors[j]:
        #             r[j, i] = np.prod(np.sign(q[j, self.c_neighbors[j][self.c_neighbors[j] != i]])) * (
        #                 -np.log(np.tanh(
        #                     np.sum(
        #                             -np.log(np.tanh(
        #                                 np.abs(q[j, self.c_neighbors[j][self.c_neighbors[j] != i]]) / 2
        #                             ))
        #                     ) / 2
        #                 ))
        #             )
        #
        #     for i in range(self.n):
        #         llr[i] = channel_llr[i] + np.sum(r[self.v_neighbors[i], i])
        #         for j in self.v_neighbors[i]:
        #             q[j, i] = llr[i] - r[j, i]

            # Check stop condition
            estimate: npt.NDArray[np.int_] = np.array(llr < 0, dtype=np.int_)
            syndrome = self.h.dot(estimate) % 2
            if not syndrome.any():
                break

        return estimate, llr, not syndrome.any(), iteration

    # def info_bits(self, estimate: NDArray[np.int_]) -> Bits:
    #     """extract information bearing bits from decoded estimate, assuming info bits indices were specified"""
    #     if self.info_idx is not None:
    #         return Bits(auto=estimate[self.info_idx])
    #     else:
    #         raise InfoBitsNotSpecified("decoder cannot tell info bits")
    #
    # def ordered_vnodes(self) -> list[VNode]:
    #     """getter for ordered graph v-nodes"""
    #     return self.graph.ordered_v_nodes()
    #
    # def update_channel_model(self, channel_models: dict[int, ChannelModel]) -> None:
    #     """
    #     rectify channel model for specific vnodes
    #
    #     :param channel_models: a dictionary with keys as node uid, and value as a new channel model
    #     """
    #     for uid, model in channel_models.items():
    #         node = self.graph.v_nodes.get(uid)
    #         if isinstance(node, VNode):
    #             node.channel_model = model
