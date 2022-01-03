from ldpc.encoder.base_encoder import Encoder
import numpy as np
from bitstring import Bits
from ldpc.utils.custom_exceptions import IncorrectLength
from ldpc.utils.qc_format import QCFile
import os
from numpy.typing import NDArray
from ldpc.wifi_spec_codes import WiFiSpecCode


class EncoderWiFi(Encoder):
    """Encode messages according to the codes in the IEEE802.11n standard"""
    _spec_base_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'code_specs', 'ieee802.11')

    def __init__(self, spec: WiFiSpecCode) -> None:
        """
        :param spec: specify which code from the spec we use
        """
        self.spec = spec
        qc_file = QCFile.from_file(os.path.join(self._spec_base_path, spec.name + ".qc"))
        self.h = qc_file.to_array()
        self.m, n = self.h.shape
        k = n - self.m
        self.z = qc_file.z
        self.block_structure = qc_file.block_structure
        super().__init__(k, n)

    def encode(self, information_bits: Bits) -> Bits:
        """Based on: Efficient encoding of IEEE 802.11n LDPC codes,
        https://www.researchgate.net/publication/3389450_Efficient_encoding_of_IEEE_80211n_LDPC_codes
        """
        if len(information_bits) != self.k:
            raise IncorrectLength

        shifted_messages = self._shifted_messages(information_bits)
        parities = np.zeros((self.m//self.z, self.z), dtype=np.int_)
        # special parts see article
        parities[0, :] = np.sum(shifted_messages, axis=0) % 2  # find first batch of z parity bits
        parities[1, :] = (shifted_messages[0, :] + np.roll(parities[0, :], -1)) % 2  # find second set of z parity bits
        parities[-1, :] = (shifted_messages[-1, :] + np.roll(parities[0, :], -1)) % 2  # find last set of z parity bits
        for idx in range(1, (self.m//self.z)-2):  # -1 needed to avoid exceeding memory limits due to idx+1 below.
            # -2 needed as bottom row is a special case.
            if self.block_structure[idx][self.k // self.z] >= 0:
                # special treatment of x-th row, see article
                parities[idx+1, :] = (parities[idx, :] + shifted_messages[idx, :] + parities[0, :]) % 2
            else:
                parities[idx+1, :] = (parities[idx, :] + shifted_messages[idx, :]) % 2

        return information_bits + Bits(np.ravel(parities))

    def _shifted_messages(self, information_bits: Bits) -> NDArray[np.int_]:
        # break message bits into groups (rows) of Z bits. Each row is a subset of z bits, overall k message bits
        bit_blocks = np.array(information_bits, dtype=np.int_).reshape((self.k // self.z, self.z))

        # find shifted messages (termed lambda_i in article)
        shifted_messages = np.zeros((self.m // self.z, self.z),
                                    dtype=np.int_)  # each row is a sum of circular shifts of
        # message bits (some lambda_i in article). One row per block of h.
        for i in range(self.m // self.z):
            for j in range(self.k // self.z):
                if self.block_structure[i][j] >= 0:  # zero blocks don't contribute to parity bits
                    # multiply by translation reduces to shift.
                    vec = np.roll(bit_blocks[j, :], -self.block_structure[i][j])
                    shifted_messages[i, :] = np.logical_xor(shifted_messages[i, :], vec)  # xor as sum mod 2
        return shifted_messages
