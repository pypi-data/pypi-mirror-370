from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from typing import Any, override, Self, Type

class SubAddrId(ManagedObj, Serializable):
  """
  Represents a sub-address ID.

  >>> from blsct import SubAddrId
  >>> x = SubAddrId(123, 456)
  >>> x
  SubAddrId(7b00000000000000c801000000000000)
  >>> ser = x.serialize()
  >>> deser = SubAddrId.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(
    self,
    account: int,
    address: int
  ):
    """Generate a sub-address ID from an account and an address"""
    obj = blsct.gen_sub_addr_id(account, address);
    super().__init__(obj)

  @override
  def value(self) -> Any:
    return blsct.cast_to_sub_addr_id(self.obj)

  @classmethod
  @override
  def default_obj(cls: Type[Self]) -> Self:
    raise NotImplementedError(f"Cannot create a SubAddrId without required parameters.")

  def serialize(self) -> str:
    """Serialize the SubAddrId to a hexadecimal string"""
    return blsct.serialize_sub_addr_id(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the SubAddrId from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_sub_addr_id(hex);
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize SubAddrId. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 

