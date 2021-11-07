import numpy as np
from bitstring import Bits
from encoder import WiFiSpecCode, EncoderWiFi
from utils import QCFile


# create information bearing bits
bits = Bits(bytes=bytes(list(range(41))))[:648//2]
# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
# encode bits
encoded = enc.encode(bits)

# verify validity of codeword
h = QCFile.from_file("../code_specs/ieee802.11/N648_R12.qc").to_array()
np.dot(h, np.array(encoded)) % 2  # creates an all zero vector as required.
