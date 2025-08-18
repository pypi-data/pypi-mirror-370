from . import blsct
from .ctx_out_blsct_data import CTxOutBlsctData
from .managed_obj import ManagedObj
from .script import Script
from .serializable import Serializable
from .token_id import TokenId
from typing import Any, override, Self, Type

class CTxOut(ManagedObj, Serializable):
  """
  Represents a transaction output in a constructed confidential transaction. Also known as `CTxOut` on the C++ side.

  For code examples, see the `ctx.py` class documentation.
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  def get_value(self) -> int:
    """Get the value of the transaction output."""
    return blsct.get_ctx_out_value(self.value())

  def get_script_pub_key(self) -> Script:
    """Get the scriptPubKey of the transaction output."""
    obj = blsct.get_ctx_out_script_pubkey(self.value())
    return Script.from_obj(obj)

  def blsct_data(self) -> CTxOutBlsctData:
    """Get the blsct-related data of the transaction output."""
    if hasattr(self, "blsct_data_cache") and self.blsct_data_cache is not None:
      return self.blsct_data_cache
    inst = CTxOutBlsctData.from_obj(self.value())
    inst._borrowed = True
    self.blsct_data_cache = inst
    return inst

  def get_token_id(self) -> 'TokenId':
    """Get the token ID of the transaction output."""
    obj = blsct.get_ctx_out_token_id(self.value())
    return TokenId.from_obj(obj)

  def get_vector_predicate(self) -> str:
    """Get the vector predicate of the transaction output in hex."""
    rv = blsct.get_ctx_out_vector_predicate(self.value())
    if rv.result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to get vector predicate. Error code = {rv.result}")
    if rv.value_size != 0:
      blsct.free_obj(rv)
      return ""
    buf = blsct.cast_to_uint8_t_ptr(rv.value)
    hex = blsct.to_hex(buf, rv.value_size)
    blsct.free_obj(rv)
    return hex 

  @override
  def value(self) -> Any:
    return blsct.cast_to_ctx_out(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("CTxOut should not be directly instantiated.")

  @override
  def serialize(self) -> str:
    """Serialize the CTxOut object to a hexadecimal string."""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, self.obj_size)

  @classmethod
  @override
  def deserialize(
    cls: Type[Self],
    hex: str,
  ) -> Self:
    """Create a CTxOut from a hexadecimal string."""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    obj = blsct.hex_to_malloced_buf(hex)
    return cls.from_obj_with_size(obj, obj_size)

