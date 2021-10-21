# documentation on the format appear in:
# http://www.inference.org.uk/mackay/codes/alist.html
# https://aff3ct.readthedocs.io/en/latest/user/simulation/parameters/codec/ldpc/decoder.html#dec-ldpc-dec-h-path
from __future__ import annotations
from typing import Callable
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass


class InconsistentAList(Exception):
    pass


# noinspection SpellCheckingInspection
@dataclass(frozen=True)
class AList:
    n: int  # number of columns
    m: int  # number of rows
    largest_column_weight: int
    # largest column weight (amount of non-zeros along a column). Referred to as biggest_num_n in Mackay's reference
    largest_row_weight: int
    # largest row weight (amount of non-zeros along a row). Referred to as biggest_num_m in Mackay's reference
    column_weights: list[int]  # Referred to as num_nlist in Mackay's reference
    row_weights: list[int]  # Referred to as num_mlist in Mackay's reference

    # indices start from 1 and not from 0 (in compliance with Mackay's reference).
    non_zero_elements_in_column: list[list[int]]  # each sub-list is a of indices of non-zero elements in column.
    # For parity check matrices, each sub-list indicates check-nodes connected to a certain variable node.
    non_zero_elements_in_row: list[list[int]]  # each sub-list is a of indices of non-zero elements in column.
    # For parity check matrices, each sub-list indicates check-nodes connected to a certain variable node.

    @classmethod
    def from_file(cls, path: str) -> AList:
        with open(path, "r") as file:
            row_read: Callable[[], list[int]] = lambda: list(map(int, file.readline().split()))
            ln = row_read()
            n, m = ln[0], ln[1]
            ln = row_read()
            largest_column_weight, largest_row_weight = ln[0], ln[1]
            column_weights = row_read()
            row_weights = row_read()

            non_zero_elements_in_column: list[list[int]] = [None] * n  # type: ignore
            non_zero_elements_in_row: list[list[int]] = [None] * m  # type: ignore
            for i in range(n):
                non_zero_elements_in_column[i] = row_read()
            for i in range(m):
                non_zero_elements_in_row[i] = row_read()

            return cls(n, m, largest_column_weight, largest_row_weight, column_weights, row_weights,
                       non_zero_elements_in_column, non_zero_elements_in_row)

    def to_file(self, path: str) -> None:
        with open(path, "w") as file:
            file.write("{} {}\n".format(self.n, self.m))
            file.write("{} {}\n".format(self.largest_column_weight, self.largest_row_weight))
            file.write(str(self.column_weights).replace(",", "")[1:-1] + " \n")
            file.write(str(self.row_weights).replace(",", "")[1:-1] + " \n")
            for col in self.non_zero_elements_in_column:
                file.write(str(col).replace(", ", "\t")[1:-1] + "\n")
            for row in self.non_zero_elements_in_row:
                file.write(str(row).replace(", ", "\t")[1:-1] + "\n")

    @classmethod
    def from_array(cls, arr: npt.NDArray[np.int_]) -> AList:
        m, n = arr.shape
        column_weights: list[int] = [None] * n  # type: ignore
        row_weights: list[int] = [None] * m  # type: ignore
        non_zero_elements_in_column: list[list[int]] = [None] * n  # type: ignore
        non_zero_elements_in_row: list[list[int]] = [None] * m  # type: ignore

        for idx, col in enumerate(arr.T):
            # noinspection Mypy
            non_zero_elements_in_column[idx] = (np.flatnonzero(col) + 1).tolist()  # type: ignore
            column_weights[idx] = len(non_zero_elements_in_column[idx])

        for idx, row in enumerate(arr):
            # noinspection Mypy
            non_zero_elements_in_row[idx] = (np.flatnonzero(row) + 1).tolist()  # type: ignore
            row_weights[idx] = len(non_zero_elements_in_row[idx])

        largest_column_weight = max(column_weights)
        largest_row_weight = max(row_weights)

        return cls(n, m, largest_column_weight, largest_row_weight, column_weights, row_weights,
                   non_zero_elements_in_column, non_zero_elements_in_row)

    def to_array(self) -> npt.NDArray[np.int_]:
        arr = np.zeros((self.m, self.n))
        if not self.verify_elements():
            raise InconsistentAList("inconsistent A list")
        for idx, row in enumerate(self.non_zero_elements_in_row):
            for element in row:
                arr[idx, element-1] = 1
        return arr

    def verify_elements(self) -> bool:
        non_zero_elements = [0] * self.m * self.n
        cp = non_zero_elements.copy()
        for idx, row in enumerate(self.non_zero_elements_in_row):
            for element in row:
                non_zero_elements[idx*self.n + element-1] = 1

        for idx, col in enumerate(self.non_zero_elements_in_column):
            for element in col:
                cp[idx + self.n*(element-1)] = 1

        return cp == non_zero_elements
