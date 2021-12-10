from abc import ABC, abstractmethod
from bitstring import Bits


class Encoder(ABC):
    """Base class for encoders"""
    def __init__(self, k: int, n: int) -> None:
        """
        :param k: number of information bits per frame.
        :param n: number of bits per frame.
        """
        self.k = k
        self.n = n

    @abstractmethod
    def encode(self, information_bits: Bits) -> Bits:
        """
        This method is used to encode information bits
        :param information_bits:
        :return:
        :raises: The method should raise IncorrectLength exception if len(information_bits) != self.k
        """
