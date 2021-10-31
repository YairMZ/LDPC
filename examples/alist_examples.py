from utils import AList


# generate an AList object from a file
alist = AList.from_file("../code_specs/Mackay_96.3.963.alist")
# convert the object to a standard numpy array
arr = alist.to_array()
# create an instance from an array
foo = AList.from_array(arr)
# save AList to file
foo.to_file("../tests/test_data/test.alist")
# express the matrix as a CodeStructure object
structure = foo.code_params()
# convert AList to a scipy sparse array
sp = foo.to_sparse()
# or convert a sparse matrix to an AList
bar = AList.from_sparse(sp)
