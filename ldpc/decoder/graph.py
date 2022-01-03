from __future__ import annotations
import networkx as nx
from ldpc.decoder.node import VNode, CNode
import numpy as np
import numpy.typing as npt
from typing import Optional, Union
from ldpc.decoder.channel_models import ChannelModel


__all__ = ["TannerGraph"]

Edge = tuple[int, int]
EdgesSet = set[tuple[int, int]]


class TannerGraph:
    """A Tanner graph used to describe an LDPC code. Allows building from a biadjacency matrix."""
    def __init__(self) -> None:
        self.v_nodes: dict[int, VNode] = {}
        self.c_nodes: dict[int, CNode] = {}
        self.edges: EdgesSet = set()

    def add_v_node(self, channel_model: ChannelModel, ordering_key: int, name: str = "") -> VNode:
        """
        :param ordering_key: should reflect order according to parity check matrix, channel symbols in order
        :param name: name of node.
        :param channel_model: add an exiting node to graph. If not used a new node is created.
        """
        node = VNode(channel_model, ordering_key, name)
        self.v_nodes[node.uid] = node
        return node

    def add_c_node(self, name: str = "", ordering_key: Optional[int] = None) -> CNode:
        """
        :param ordering_key: use only for debug purposes
        :param name: name of node
        """
        node = CNode(name, ordering_key)
        self.c_nodes[node.uid] = node
        return node

    def add_edge(self, vnode_uid: int, cnode_uid: int) -> None:
        vnode = self.v_nodes.get(vnode_uid)
        cnode = self.c_nodes.get(cnode_uid)
        if vnode is None or cnode is None:
            raise ValueError()
        cnode.register_neighbor(vnode)
        vnode.register_neighbor(cnode)
        self.edges.update({(vnode_uid, cnode_uid)})

    def add_edges_by_uid(self, edges_set: EdgesSet) -> None:
        """
        :param edges_set: each element in the set is a tuple. In the tuple first element is a v-node uid and second is
        c-node uid
        """
        for v_uid, c_uid in edges_set:
            if v_uid not in self.v_nodes:
                raise ValueError("No v-node with uid " + str(v_uid) + " in graph")
            if c_uid not in self.c_nodes:
                raise ValueError("No c-node with uid " + str(c_uid) + " in graph")
            self.add_edge(v_uid, c_uid)

    def add_edges_by_name(self, edges_set: set[tuple[str, str]]) -> None:
        """
        :param edges_set: each element in the set is a tuple. In the tuple first element is a v-node name and second is
        c-node name
        """
        for v_name, c_name in edges_set:
            v_uid = [node.uid for node in self.v_nodes.values() if node.name == v_name]
            if not v_uid:
                raise ValueError("No v-node with name " + v_name + " in graph")
            c_uid = [node.uid for node in self.c_nodes.values() if node.name == c_name]
            if not c_uid:
                raise ValueError("No c-node with name " + c_name + " in graph")
            self.add_edge(v_uid[0], c_uid[0])

    def get_edges(self, by_name: bool = False) -> Union[set[tuple[str, str]], EdgesSet]:
        """
        :param by_name: if true nodes are referred to by name, otherwise by uid. Default to false
        :return: returns a set of edges. if by_name each element is a tuple of node names, else it is a tuple of uid.
        """
        if not by_name:
            return self.edges
        return {(self.v_nodes.get(vn).name, self.c_nodes.get(cn).name) for vn, cn in self.edges}  # type: ignore

    def to_nx(self) -> nx.Graph:
        """Transform a TannerGraph object into an networkx.Graph object"""
        g = nx.Graph()
        for uid, cnode in self.c_nodes.items():
            g.add_node(uid, label=cnode.name, bipartite=0, color="blue")
        for uid, vnode in self.v_nodes.items():
            g.add_node(uid, label=vnode.name, bipartite=1, color="red")
        g.add_edges_from(self.edges)
        return g

    @classmethod
    def from_biadjacency_matrix(cls, h: npt.ArrayLike, channel_model: ChannelModel) -> TannerGraph:
        """
        :param channel_model: channel model to compute channel symbols llr within v nodes
        :param h: parity check matrix, shape MXN with M check nodes and N variable nodes. assumed binary matrix.
        """
        g = TannerGraph()
        h = np.array(h)
        m, n = h.shape
        for i in range(n):
            g.add_v_node(name="v" + str(i), channel_model=channel_model, ordering_key=i)
        for j in range(m):
            g.add_c_node(name="c" + str(j), ordering_key=j)
            for i in range(n):
                if h[j, i] == 1:
                    g.add_edges_by_name({("v" + str(i), "c" + str(j))})
        return g

    def __str__(self) -> str:
        return "Graph with " + str(len(self.c_nodes) + len(self.v_nodes)) + " nodes and " + str(len(self.edges)) + \
               " edges"

    def ordered_v_nodes(self) -> list[VNode]:
        """return vnodes of graph as a list of nodes ordered by the ordering key defined for the nodes"""
        return sorted(self.v_nodes.values())
