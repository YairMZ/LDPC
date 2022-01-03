from ldpc.decoder.log_spa_decoder import *
from numpy.typing import NDArray
import numpy as np
from ldpc.decoder.channel_models import ChannelModel
from typing import Optional
from ldpc.wifi_spec_codes import WiFiSpecCode
import os
from ldpc.utils.qc_format import QCFile


class DecoderWiFi(LogSpaDecoder):
    """Decode messages according to the codes in the IEEE802.11n standard using Log SPA decoder"""
    _spec_base_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'code_specs', 'ieee802.11')

    def __init__(self, channel_model: ChannelModel, spec: WiFiSpecCode, max_iter: int,
                 info_idx: Optional[NDArray[np.bool_]] = None):
        """

        :param channel_model: a callable which receives a channel input, and returns the channel llr
        :param spec: specify which code from the spec we use
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param info_idx: a boolean array representing the indices of information bits in the code
        """
        self.spec = spec
        qc_file = QCFile.from_file(os.path.join(self._spec_base_path, spec.name + ".qc"))
        h = qc_file.to_array()
        super().__init__(channel_model, h, max_iter, info_idx)
