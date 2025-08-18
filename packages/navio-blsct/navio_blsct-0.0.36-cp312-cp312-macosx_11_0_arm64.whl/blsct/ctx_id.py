from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from typing import Any, override, Type, Self

class CTxId(ManagedObj, Serializable):
  """
  Represents the transaction ID of a CMutableTransaction

  >>> from blsct import CTxId, CTX_ID_SIZE
  >>> import secrets
  >>> hex = secrets.token_hex(CTX_ID_SIZE)
  >>> ctx_id = CTxId.deserialize(hex)
  >>> ctx_id.serialize()
  'ec7b726c443d3ebb7fb8704fe039a6df993a8a4552ab88c3463627ccd947f334'
  >>> ctx_id.serialize() == hex
  True
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  @override
  def serialize(self) -> str:
    """Serialize the CTxId object to a hexadecimal string."""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, blsct.CTX_ID_SIZE)

  @classmethod
  @override
  def deserialize(
    cls: Type[Self],
    hex: str,
  ) -> Self:
    """Create a TxId from a hexadecimal string."""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    if len(hex) != blsct.CTX_ID_SIZE * 2:
      raise ValueError(f"Invalid TxId hex length. Expected {blsct.CTX_ID_SIZE * 2}, but got {len(hex)}.")
    obj = blsct.hex_to_malloced_buf(hex) 
    return cls(obj)

  @override
  def value(self):
    return blsct.cast_to_uint8_t_ptr(self.obj)

  @classmethod
  @override
  def default_obj(cls: Type[Self]) -> Any:
    raise NotImplementedError("Cannot create a CTxId without required parameters.")

