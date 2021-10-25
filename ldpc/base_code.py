"""Base class for LDPC codes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeStructure:
    num_vnodes: int  # number of variable nodes (information bits) per frame
    num_cnodes: int  # number of check nodes (parity bits) per frame
    max_vnode_deg: int
    max_cnode_deg: int
    vnode_deg_list: list[int]
    cnode_deg_list: list[int]
    vnode_adjacency: dict[int, set[int]]  # lists each vnode (key) neighbors (set of cnodes indices)
    cnode_adjacency: dict[int, set[int]]  # lists each cnode (key) neighbors (set of vnodes indices)
