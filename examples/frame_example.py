from utils import FramesManager
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
