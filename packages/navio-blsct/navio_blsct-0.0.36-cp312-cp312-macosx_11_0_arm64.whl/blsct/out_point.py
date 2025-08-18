from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from .ctx_id import CTxId
from typing import Any, override, Self

class OutPoint(ManagedObj, Serializable):
  """
  Represents an outpoint of a confidential transaction. Also known as `COutPoint` on the C++ side.

  >>> from blsct import OutPoint, CTxId, CTX_ID_SIZE
  >>> import secrets
  >>> ctx_id = CTxId.deserialize(secrets.token_hex(CTX_ID_SIZE))
  >>> out_index = 0
  >>> out_point = OutPoint(ctx_id, out_index)
  >>> out_point
  OutPoint(ae8f9ba6eaef62fbd4b0215cda24e231...) # doctest: +SKIP
  >>> ser = out_point.serialize()
  >>> ser == OutPoint.deserialize(ser).serialize()
  True
  """
  def __init__(self, ctx_id: CTxId, out_index: int):
    rv = blsct.gen_out_point(ctx_id.serialize(), out_index)
    obj = rv.value
    blsct.free_obj(rv)
    super().__init__(obj)

  def serialize(self) -> str:
    """Serialize the OutPoint to a hexadecimal string"""
    return blsct.serialize_out_point(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the OutPoint from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_out_point(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize OutPoint. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 

  @override
  def value(self) -> Any:
    return blsct.cast_to_out_point(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create an OutPoint without required parameters.")

