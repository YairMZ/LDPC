from utils import AList


# generate an AList object from a file
alist = AList.from_file("../tests/test_data/Mackay_96.3.963.alist")
# convert the object to a standard numpy array
arr = alist.to_array()
arr
# create an instance from an array
foo = AList.from_array(arr)
# save AList to file
foo.to_file("../tests/test_data/test.alist")
