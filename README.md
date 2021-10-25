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
 - AList - The module is allows reading and writing "alist" files. "alist" files format which were invented by David 
MacKay, allow storing sparse matrices efficiently in files. The format is documented
[here](http://www.inference.org.uk/mackay/codes/alist.html).

## Examples:
### AList
```python
from utils import AList
# generate an AList object from a file
alist = AList.from_file("tests/test_data/Mackay_96.3.963.alist")
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