from bitstring import Bits
from encoder import WiFiSpecCode, EncoderWiFi

# create information bearing bits
bits = Bits(bytes=bytes(list(range(41))))[:648//2]
# create encoder
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
# encode bits
encoded = enc.encode(bits)

