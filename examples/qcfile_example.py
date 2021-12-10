from ldpc.utils import QCFile


# generate an object from a file
qc = QCFile.from_file("../ldpc/code_specs/ieee802.11/N648_R12.qc")
# convert the object to a standard numpy array
arr = qc.to_array()
# create an instance from an existing array
foo = QCFile.from_array(arr, qc.z)
# save object to file
foo.to_file("../tests/test_data/test.qc")
# convert object to a scipy sparse array
sp = foo.to_sparse()
# trying to build an object from an incompatible matrix will raise a value error
arr[1, 2] = 1  # Now the array isn't a column permutation of an identity
QCFile.from_array(arr, qc.z)  # this raises an error
