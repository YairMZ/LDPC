# Encoder Module
The module implements encoders for LDPC codes. Currently implemented:
   - generator based - The [EncoderG](generator_based_encoder.py) class allows encoding frames via multiplication with a
specified generator matrix.
   - IEEE802.11 - The [EncoderWiFi](ieee802_11_encoder.py) class allows encoding frames using the IEEE802.11 spec codes.
Encoding is done via back substitution.
   - Parity check based - [EncoderTriangularH](h_based_encoder.py) class allows encoding frames via back substitution. It requires a lower triangular parity check matrix.

------
## Examples:
### Generator Based 

Add example

### IEEE802.11 (WiFi)

```python
import numpy as np
from bitstring import Bits
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils import QCFile

# create information bearing bits
bits = np.array(Bits(bytes=bytes(list(range(41))))[:648 // 2], dtype=np.int_)
# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
# encode bits
encoded = enc.encode(bits)

# verify validity of codeword
h = QCFile.from_file("../code_specs/ieee802.11/N648_R12.qc").to_array()
np.dot(h, np.array(encoded)) % 2  # creates an all zero vector as required.
```