from enum import Enum, auto

class AddressEncoding(Enum):
  """
  Address encoding types used when converting DoublePublicKey objects to and from strings.
  """

  Bech32 = auto()
  """Traditional Bech32 encoding"""

  Bech32M = auto()
  """Modified version of Bech32 encoding"""
 
