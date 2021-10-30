[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status - GitHub](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/YairMZ/LDPC/branch/main/graph/badge.svg?token=2RR3afDfeD)](https://codecov.io/gh/YairMZ/LDPC)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
# LDPC
My implementation of LDPC codes

To run tests simply clone, cd into the cloned repo, and run:
```shell
python -m pytest
```
or
```shell
python -m pytest --cov-report=html
```
to run also coverage tests.

## Included modules:
 - Utilities:
   - AList - The module is allows reading and writing "alist" files. "alist" files format which were invented by David 
MacKay, allow storing sparse matrices efficiently in files. The format is documented
[here](http://www.inference.org.uk/mackay/codes/alist.html).
   - Frame - Each bit sequence is allocated a frame with a unique id for bookkeeping during simulation.
 - Encoder:
   - Generator based encoder (via matrix multiplication). 

## Examples:
### AList

```python
from utils import AList

# generate an AList object from a file
alist = AList.from_file("code_specs/Mackay_96.3.963.alist")
# convert the object to a standard numpy array
arr = alist.to_array()
# create an instance from an array
foo = AList.from_array(arr)
# save AList to file
foo.to_file("../tests/test_data/test.alist")
# express the matrix as a CodeStructure object
structure = foo.code_params()
# convert AList to a scipy.sparse array
sp = foo.to_sparse()
# or convert a sparse matrix to an AList
bar = AList.from_sparse(sp)
```

### Frames
```python
from utils import Frame, FramesManager
from bitstring import Bits

# Frames shouldn't be instantiated on their own, but instead using the manager
fm = FramesManager()
# using the manager to crete a frame
bits = Bits(bytes=b"\x01\x02")
tx_frame = fm.create_frame(bits)
# create a copy of the tx_frame to simulate rx
rx_frame = fm.copy_frame(tx_frame)
# Note that copying copies only bits, ids are still unique
print(rx_frame.uid != tx_frame.uid)
# two frames can be registered as a tx, rx pair:
fm.register_pair(tx_frame, rx_frame)
```
