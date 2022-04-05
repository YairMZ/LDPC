from ldpc.decoder.log_spa_decoder import LogSpaDecoder
import numpy as np
from ldpc.decoder.channel_models import ChannelModel
from ldpc.wifi_spec_codes import WiFiSpecCode
import os
from ldpc.utils.qc_format import QCFile
from typing import Optional


class DecoderWiFi(LogSpaDecoder):
    """Decode messages according to the codes in the IEEE802.11n standard using Log SPA decoder"""
    _spec_base_path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'code_specs', 'ieee802.11')

    def __init__(self, spec: WiFiSpecCode, max_iter: int, channel_model: Optional[ChannelModel] = None,
                 decoder_type: Optional[str] = "BP"):
        """

        :param channel_model: a callable which receives a channel input, and returns the channel llr
        :param spec: specify which code from the spec we use
        :param max_iter: The maximal number of iterations for belief propagation algorithm
        :param decoder_type: must be either "BP" or "MS" for min-sum decoder
        """
        self.spec = spec
        qc_file = QCFile.from_file(os.path.join(self._spec_base_path, spec.name + ".qc"))
        h = qc_file.to_array()
        m, n = h.shape
        k = n - m
        super().__init__(h, max_iter, info_idx=np.array([True] * k + [False] * m), channel_model=channel_model,
                         decoder_type=decoder_type)
