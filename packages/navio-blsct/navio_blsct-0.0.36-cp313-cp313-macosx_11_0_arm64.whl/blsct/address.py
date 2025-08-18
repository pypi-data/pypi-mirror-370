from . import blsct
from .address_encoding import AddressEncoding
from .keys.double_public_key import DoublePublicKey

class Address():
  """
  Encode and decode address strings from DoublePublicKey objects.

  This class provides static methods to convert between DoublePublicKey objects and their string representations using a specified encoding.

  >>> from blsct import DoublePublicKey, Address, AddressEncoding
  >>> dpk = DoublePublicKey()
  >>> addr = Address.encode(dpk, AddressEncoding.Bech32M)
  >>> addr
  'nv15glx4094hlz7ltmjqp5cqa...'  # doctest: +SKIP
  >>> dec_dpk = Address.decode(addr)
  >>> dpk.serialize() == dec_dpk.serialize()
  True
   """
  @staticmethod
  def encode(dpk: DoublePublicKey, encoding: AddressEncoding):
    """Encode a DoublePublicKey to an address string using the specified encoding""" 

    blsct_encoding = None
    if encoding == AddressEncoding.Bech32:
      blsct_encoding = blsct.Bech32
    else: # encoding == AddressEncoding.Bech32M:
      blsct_encoding = blsct.Bech32M

    dpk = blsct.cast_to_dpk(dpk.obj)
    rv = blsct.encode_address(dpk, blsct_encoding)
    rv_result = int(rv.result)

    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to encode address. Error code = {rv_result}")

    enc_addr = blsct.as_string(rv.value)
    blsct.free_obj(rv)
    return enc_addr

  @staticmethod
  def decode(addr: str):
    """Decode an address string to a DoublePublicKey"""

    rv = blsct.decode_address(addr)
    rv_result = int(rv.result)

    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to decode address. Error code = {rv_result}")

    # move rv.value (blsct_dpk) to DoublePublicKey
    dpk = DoublePublicKey.from_obj(rv.value)
    blsct.free_obj(rv)

    return dpk

