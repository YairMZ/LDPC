[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status - GitHub](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)](https://github.com/YairMZ/LDPC/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/YairMZ/LDPC/branch/main/graph/badge.svg?token=2RR3afDfeD)](https://codecov.io/gh/YairMZ/LDPC)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)
# LDPC
My implementation of LDPC codes.
My notes regarding theory and implementation appears on GitHub Pages: https://yairmz.github.io/LDPC/  

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
 - [Utilities](utils/README.md): implementing various utility operations to assist with encoding, decoding and 
simulations.
 - [Encoder](encoder/README.md): implementing a generator based encoder, and encoders for IEEE802.11 (WiFi) LDPC codes.
 - [Decoder](decoder/README.md): implementing a Log-SPA based BP decoder.

__________
## Sources
 - Cai Z., Hao J., Tan P.H., Sun S., Chin P.S., Efficient encoding of IEEE 802.11n LDPC codes. Electronics Letters 25, 
1471--1472 (2006).
 - IEEE802.11 encoder tested against the implementation in https://github.com/tavildar/LDPC
 - [Channel codes : classical and modern](https://www.cambridge.org/il/academic/subjects/engineering/communications-and-signal-processing/channel-codes-classical-and-modern)
by William E. Ryan, 2009.
  


