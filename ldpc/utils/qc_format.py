# documentation on the format appears in:
# https://aff3ct.readthedocs.io/en/latest/user/simulation/parameters/codec/ldpc/decoder.html#dec-ldpc-dec-h-path
from __future__ import annotations
from typing import Callable
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
import scipy.sparse as sp


class InconsistentQCFile(Exception):
    pass


@dataclass(frozen=True)
class QCFile:
    c: int  # number of columns
    r: int  # number of rows
    z: int  # size identity / zero blocks

    block_structure: list[list[int]]  # each sub-list is a list of integers. Each integer describes a block a either

    # being an all zero matrix (value of -1), an identity matrix (value of zero), or a right shifted identity matrix
    # (positive value smaller than z).

    @classmethod
    def from_file(cls, path: str) -> QCFile:
        with open(path, "r") as file:
            row_read: Callable[[], list[int]] = lambda: list(map(int, file.readline().split()))
            ln = row_read()
            c, r, z = ln[0], ln[1], ln[2]
            structure: list[list[int]] = [row_read() for _ in range(r)]

        return cls(c, r, z, structure)

    def to_file(self, path: str) -> None:
        with open(path, "w") as file:
            file.write("{}\t{}\t{}\n".format(self.c, self.r, self.z))
            for row in self.block_structure:
                file.write(str(row).replace(", ", "\t")[1:-1] + "\n")

    def to_array(self) -> npt.NDArray[np.int_]:
        return np.array(self.to_sparse().toarray())

    def verify_elements(self) -> bool:
        for row in self.block_structure:
            for col in row:
                if col >= self.z:
                    return False
        return True

    def to_sparse(self) -> sp.lil_matrix:
        if not self.verify_elements():
            raise InconsistentQCFile("inconsistent QC format")
        z = self.z
        blocks: list[sp.spmatrix] = [None] * (z + 1)
        blocks[0] = sp.identity(z, dtype=np.int_, format='dia')
        shifted = sp.dia_matrix((np.ones((2, z)), np.array([1, -(z - 1)])), shape=(z, z), dtype=np.int_).tocsr()
        for shift in range(1, z):
            blocks[shift] = shifted ** shift
        blocks[-1] = sp.lil_matrix((z, z))  # all zeros block
        return sp.bmat(
            [[blocks[col] for col in row] for row in self.block_structure],
            format='lil',
            dtype=np.int_
        )

    @classmethod
    def from_array(cls, arr: npt.NDArray[np.int_], z: int) -> QCFile:
        m, n = arr.shape
        if not float(m / z).is_integer() or not float(n / z).is_integer():
            raise ValueError("inconsistent z value")
        r, c = int(m / z), int(n / z)
        blocks: list[npt.NDArray[np.int_]] = [sp.identity(z, dtype=np.int_, format='dia').toarray()]
        shifted = sp.dia_matrix((np.ones((2, z)), np.array([1, -(z - 1)])), shape=(z, z), dtype=np.int_).tocsr()
        for shift in range(1, z):
            blocks.append((shifted ** shift).toarray())
        blocks.append(np.zeros((z, z), dtype=np.int_))  # all zeros block
        structure: list[list[int]] = [[z + 1] * c for _ in range(r)]
        for row in range(r):
            for col in range(c):
                sub_array = arr[row * z:(row + 1) * z, col * z:(col + 1) * z]
                for block_idx, block in enumerate(blocks):
                    if np.array_equal(sub_array, block):
                        structure[row][col] = -1 if block_idx == z else block_idx
                        break
        for row in range(r):
            for col in range(c):
                if structure[row][col] >= z:
                    raise ValueError("incompatible array")
        return cls(c, r, z, structure)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QCFile):
            return False
        return self.z == other.z and self.block_structure == other.block_structure and self.r == other.r and \
            self.c == other.c
