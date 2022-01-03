import numpy as np
from bitstring import BitArray, Bits
from ldpc.decoder import DecoderWiFi, bsc_llr
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils import QCFile

# create information bearing bits
rng = np.random.default_rng()
info_bits = Bits(bytes=rng.bytes(41))[:648//2]
# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
# encode bits
encoded = enc.encode(info_bits)

# verify validity of codeword
h = QCFile.from_file("../ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
np.dot(h, np.array(encoded)) % 2  # creates an all zero vector as required.

# create a decoder which assumes a probability of p=0.05 for bit flips by the channel
# allow up to 20 iterations for the bp decoder.
p = 0.05
decoder = DecoderWiFi(bsc_llr(p=p), spec=WiFiSpecCode.N648_R12, max_iter=20, info_idx=np.array([True]*324 + [False]*324))

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
