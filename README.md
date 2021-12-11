[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status - GitHub](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/YairMZ/LDPC/branch/main/graph/badge.svg?token=2RR3afDfeD)](https://codecov.io/gh/YairMZ/LDPC)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
# LDPC
My implementation of LDPC codes.
My notes regarding theory and implementation appears on GitHub Pages: https://yairmz.github.io/LDPC/  
To install:
```shell
pip install sim-ldpc
```
To run tests simply clone, cd into the cloned repo, and run:
```shell
python -m pytest
```
or
```shell
python -m pytest --cov-report=html
```
to run also coverage tests, or
```shell
python -m pytest  -n auto --cov-report=html
```
to run tests in parallel (with number of CPU's dictated by machine) to speed up tests.

-----
## Included modules
 - [Utilities](ldpc/utils/README.md): implementing various utility operations to assist with encoding, decoding and 
simulations.
 - [Encoder](ldpc/encoder/README.md): implementing a generator based encoder, and encoders for IEEE802.11 (WiFi) LDPC codes.
 - [Decoder](ldpc/decoder/README.md): implementing a Log-SPA based BP decoder.

-----

## Basic Example
```python
import numpy as np
from bitstring import BitArray, Bits
from ldpc.decoder import LogSpaDecoder, bsc_llr
from ldpc.encoder import EncoderWiFi, WiFiSpecCode
from ldpc.utils import QCFile

# create information bearing bits
rng = np.random.default_rng()
info_bits = Bits(bytes=rng.bytes(41))[:648//2]
# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
# encode bits
encoded = enc.encode(info_bits)

# verify validity of codeword
h = QCFile.from_file("ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
np.dot(h, np.array(encoded)) % 2  # creates an all zero vector as required.

# create a decoder which assumes a probability of p=0.05 for bit flips by the channel
# allow up to 20 iterations for the bp decoder.
p = 0.05
decoder = LogSpaDecoder(bsc_llr(p=p), h=h, max_iter=20, info_idx=np.array([True]*324 + [False]*324))

# create a corrupted version of encoded codeword with error rate p
corrupted = BitArray(encoded)
no_errors = int(len(corrupted)*p)
error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
for idx in error_idx:
    corrupted[idx] = not corrupted[idx]
decoded, llr, decode_success, num_of_iterations = decoder.decode(corrupted)
# Verify correct decoding
print(Bits(decoded) == encoded)  # true
info = decoder.info_bits(decoded)

```
__________
## Sources
 - Cai Z., Hao J., Tan P.H., Sun S., Chin P.S., Efficient encoding of IEEE 802.11n LDPC codes. Electronics Letters 25, 
1471--1472 (2006).
 - IEEE802.11 encoder tested against the implementation in https://github.com/tavildar/LDPC
 - [Channel codes : classical and modern](https://www.cambridge.org/il/academic/subjects/engineering/communications-and-signal-processing/channel-codes-classical-and-modern)
by William E. Ryan, 2009.
  


