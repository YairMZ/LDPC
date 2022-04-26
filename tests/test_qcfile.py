import numpy as np
from ldpc.utils import QCFile, InconsistentQCFile
import scipy.sparse as sp
import pytest
import numpy.typing as npt
from typing import Any


class TestQCFile:
    def test_files_io(self) -> None:
        # Uses ieee802.11 file
        original_file = "ldpc/code_specs/ieee802.11/N648_R12.qc"
        a = QCFile.from_file(original_file)
        assert a.z == 27
        assert a.r == 12
        assert a.c == 24

        test_file = "tests/test_data/test.qc"
        a.to_file(test_file)
        with open(original_file, "r") as o_file:
            with open(test_file, "r") as n_file:
                assert o_file.read() == n_file.read()

    def test_array_io(self) -> None:
        """matrix: [[P0, P1],[P2, 0]]
        z=10
        """
        z = 10
        arr: npt.NDArray[np.int_] = np.block([[np.eye(z), np.eye(z, k=1) + np.eye(z, k=-z+1)],
                                              [np.eye(z, k=2) + np.eye(z, k=-z+2), np.zeros((z, z))]])
        a = QCFile.from_array(arr, z)
        assert arr.shape == (a.z*a.r, a.z*a.c)
        assert a.block_structure == [[0, 1], [2, -1]]
        b = a.to_array()
        np.testing.assert_array_equal(arr, b)  # type: ignore

    def test_bad_array(self) -> None:
        z = 10
        arr: npt.NDArray[np.int_] = np.block([[np.eye(z), np.eye(z, k=1) + np.eye(z, k=-z + 1)],
                                              [np.eye(z, k=2) + np.eye(z, k=-z + 2), np.zeros((z, z))]])
        a = arr[:, :-1]
        with pytest.raises(ValueError):
            QCFile.from_array(a, z)
        a = arr[:-1, :]
        with pytest.raises(ValueError):
            QCFile.from_array(a, z)
        arr[-1, -1] = 1
        with pytest.raises(ValueError):
            QCFile.from_array(arr, z)

    def test_verify_elements(self) -> None:
        original_file = "ldpc/code_specs/ieee802.11/N648_R12.qc"
        a = QCFile.from_file(original_file)
        assert a.verify_elements() is True
        a.block_structure[0][0] = a.z
        assert a.verify_elements() is False

    def test_sparse_arrays(self) -> None:
        """matrix: [[P0, P1],[P2, 0]]
        z=10
        """
        z = 10
        arr: Any = np.block([[np.eye(z), np.eye(z, k=1) + np.eye(z, k=-z+1)],
                             [np.eye(z, k=2) + np.eye(z, k=-z+2), np.zeros((z, z))]])
        a = QCFile.from_array(arr, z)
        arr = sp.lil_matrix(arr)
        b = a.to_sparse()
        assert sp.spmatrix.sum(arr != b) == 0
        a.block_structure[0][0] = a.z
        with pytest.raises(InconsistentQCFile):
            a.to_sparse()
