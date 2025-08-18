from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from typing import Any, override, Self, Type

class TokenId(ManagedObj, Serializable):
  """
  Represents a token ID. A token ID consists of two parameters: token and subid, both of which are optional. When omitted, default values are used instead of random values.

  >>> from blsct import TokenId
  >>> TokenId()
  TokenId(000000000000000...0000000ffffffffffffffff) # doctest: +SKIP
  >>> TokenId.from_token(123)
  TokenId(7b0000000000000...0000000ffffffffffffffff) # doctest: +SKIP
  >>> token_id = TokenId.from_token_and_subid(123, 456)
  >>> token_id.token()
  123
  >>> token_id.subid()
  456
  >>> ser = token_id.serialize()
  >>> deser = TokenId.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  @classmethod
  def from_token(cls: Type[Self], token: int) -> Self:
    """Generate a token ID from a given token."""
    rv = blsct.gen_token_id(token);
    token_id = cls(rv.value)
    blsct.free_obj(rv)
    return token_id
 
  @classmethod
  def from_token_and_subid(
    cls: Type[Self],
    token: int,
    subid: int,
  ) -> Self:
    """Generate a token ID from a given token and subid."""
    rv = blsct.gen_token_id_with_subid(token, subid) 
    token_id = cls(rv.value)
    blsct.free_obj(rv)
    return token_id

  def token(self) -> int:
    """Get the token from the token ID."""
    return blsct.get_token_id_token(self.value())

  def subid(self) -> int:
    """Get the subid from the token ID."""
    return blsct.get_token_id_subid(self.value())

  @override
  def value(self):
    return blsct.cast_to_token_id(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_default_token_id()
    obj = rv.value
    blsct.free_obj(rv)
    return obj

  def serialize(self) -> str:
    """Serialize the TokenId to a hexadecimal string"""
    return blsct.serialize_token_id(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the TokenId from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_token_id(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize TokenId. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 

