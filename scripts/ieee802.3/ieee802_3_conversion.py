import numpy as np
from ldpc.utils import AList

# generator
with open("g.txt") as f:
    lines = f.readlines()
    lines = [[int(idx) for idx in line.split()] for line in lines]


arr = np.zeros((1732, 2048), dtype=np.int_)
for idx, line in enumerate(lines):
    for column in line:
        arr[idx, column] = 1

alist = AList.from_array(arr)
alist.to_file("../../code_specs/ieee802.3_G.alist")

# parity check
# problematic matrix in file.
