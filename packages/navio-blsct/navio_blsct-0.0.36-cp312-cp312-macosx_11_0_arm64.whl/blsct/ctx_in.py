from . import blsct
from .managed_obj import ManagedObj
from .script import Script
from .ctx_id import CTxId
from .serializable import Serializable
from typing import Any, override, Self, Type

class CTxIn(ManagedObj, Serializable):
  """
  Represents a transaction input in a constructed confidential transaction. Also known as `CTxIn` on the C++ side.

  For code examples, see the `ctx.py` class documentation.
  """

  def __init__(self, obj: Any = None):
    super().__init__(obj)

  def get_prev_out_hash(self) -> CTxId:
    """Get the transaction ID of the previous output being spent."""
    obj = blsct.get_ctx_in_prev_out_hash(self.value())
    return CTxId.from_obj(obj)

  def get_prev_out_n(self) -> int:
    """Get the output index of the previous output being spent."""
    return blsct.get_ctx_in_prev_out_n(self.value())

  def get_script_sig(self) -> Script:
    """Get the scriptSig used to unlock the previous output."""
    obj = blsct.get_ctx_in_script_sig(self.value())
    return Script.from_obj(obj)

  def get_sequence(self) -> int:
    """Get the sequence field of the transaction input."""
    return blsct.get_ctx_in_sequence(self.value())

  def get_script_witness(self) -> Script:
    """Get the scriptWitness for the transaction input."""
    obj = blsct.get_ctx_in_script_witness(self.value())
    return Script.from_obj(obj)

  @override
  def value(self) -> Any:
    return blsct.cast_to_ctx_in(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("CTxIn should not be directly instantiated.")

  @override
  def serialize(self) -> str:
    """Serialize the CTxIn object to a hexadecimal string."""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, self.obj_size)

  @classmethod
  @override
  def deserialize(
    cls: Type[Self],
    hex: str,
  ) -> Self:
    """Create a CTxIn from a hexadecimal string."""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    obj = blsct.hex_to_malloced_buf(hex)
    return cls.from_obj_with_size(obj, obj_size)

