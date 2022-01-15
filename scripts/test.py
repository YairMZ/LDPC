from ldpc.utils import QCFile
from ldpc.decoder import bsc_llr
from bitstring import Bits
from ldpc.decoder.fast_decoder import LogSpaDecoder
import numpy as np


h = QCFile.from_file("../ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
p = 0.05
dec = LogSpaDecoder(bsc_llr(p),h,10)
encoded_ref = Bits(auto=np.genfromtxt('../tests/test_data/ieee_802_11/encoded_N648_R12.csv', delimiter=',', dtype=np.int_))[:648]
res = dec.decode(encoded_ref)

