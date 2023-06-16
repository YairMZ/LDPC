# Decoder Module
The module implements decoders for LDPC codes. Currently implemented:
   - Log-SPA - The [LogSpaDecoder](log_spa_decoder.py) class allows decoding frames via using the 
[Log-SPA algorithm](https://yairmz.github.io/LDPC/ldpc_overview/log_spa.html).
   - MS - Initializing the [LogSpaDecoder](log_spa_decoder.py) decoder using `MS` as the `decoder_type` argument will result in an MS decoder
   - Bit Flipping  - Gallager bit flipping algorithm. See [GalBfDecoder](gal_bf.py)
   - Weighted Bit Flipping - Three Weighted bit flipping algorithms. See [WbfDecoder](wbf.py)

------
## Examples:

### Log-SPA

```python
import numpy as np
from bitstring import Bits, BitArray
from ldpc.utils import QCFile
from ldpc.decoder import LogSpaDecoder, bsc_llr

info_bits = Bits(auto=np.genfromtxt(
    'tests/test_data/ieee_802_11/info_bits_N648_R12.csv', delimiter=',', dtype=np.int_))
encoded_ref = Bits(auto=np.genfromtxt(
    'tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_))

# corrupt bits by flipping with probability p.
p = 0.01
corrupted = BitArray(encoded_ref)
no_errors = int(len(corrupted) * p)
rng = np.random.default_rng()
error_idx = rng.choice(len(corrupted), size=no_errors, replace=False)
for idx in error_idx:
    corrupted[idx] = not corrupted[idx]

# create a decoder which assumes a probability of p=0.01 for bit flips by a BSC channel.
# allow up to 20 iterations for the bp decoder.
h = QCFile.from_file("code_specs/ieee802.11/N648_R12.qc").to_array()
decoder = LogSpaDecoder(bsc_llr(p=p), h=h, max_iter=20, info_idx=np.array([True] * 324 + [False] * 324))
decoded = Bits()
decoded_info = Bits()
for frame_idx in range(len(corrupted) // decoder.n):
    # The decode method returns a tuple (estimated_bits, llr, decode_success, no_iterations) where:
    #   - estimated_bits is a 1-d np array of hard bit estimates
    #   - llr is a 1-d np array of soft bit estimates   
    #   - decode_success is a boolean flag stating of the estimated_bits form a valid  code word
    #   - no_iterations is the number of iterations of belief propagation before exiting the loop
    decoder_output = decoder.decode(corrupted[frame_idx * decoder.n: (frame_idx + 1) * decoder.n])
    decoded += decoder_output[0]
    decoded_info += decoder.info_bits(decoder_output[0])
assert sum(encoded_ref ^ decoded) == 0
assert sum(info_bits ^ decoded_info) == 0
```