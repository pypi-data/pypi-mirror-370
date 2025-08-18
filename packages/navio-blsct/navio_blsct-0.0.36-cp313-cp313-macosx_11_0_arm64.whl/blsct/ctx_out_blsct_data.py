from . import blsct
from .keys.child_key_desc.tx_key_desc.spending_key import SpendingKey
from .keys.child_key_desc.blinding_key import BlindingKey
from .managed_obj import ManagedObj
from .point import Point
from .range_proof import RangeProof
from typing import Any, override

class CTxOutBlsctData(ManagedObj):
  """
  Represents a blsct-related data in transaction output in a constructed confidential transaction.
  Also known as `CTxOutBlsctData` on the C++ side. This class provides access to the `CTxOutBlsctData` object, but does not own neither the `CTxOut` nor `CTxOutBlsctData` object.

  For code examples, see the `ctx.py` class documentation.
  """
  def __init__(self, ctxout_obj: Any = None):
    super().__init__(ctxout_obj)
    self._borrowed = True

  def get_spending_key(self) -> SpendingKey:
    """Get the spending key of the transaction output."""
    obj = blsct.get_ctx_out_spending_key(self.value())
    return SpendingKey.from_obj(obj)

  def get_ephemeral_key(self) -> Point:
    """Get the ephemeral key of the transaction output."""
    obj = blsct.get_ctx_out_ephemeral_key(self.value())
    return Point.from_obj(obj)

  def get_blinding_key(self) -> BlindingKey:
    """Get the blinding key of the transaction output."""
    obj = blsct.get_ctx_out_blinding_key(self.value())
    return BlindingKey.from_obj(obj)

  def get_range_proof(self) -> RangeProof:
    """Get the range proof of the transaction output."""
    if hasattr(self, "rp_cache") and self.rp_cache is not None:
      return self.rp_cache
    rv = blsct.get_ctx_out_range_proof(self.value())
    inst = RangeProof.from_obj_with_size(rv.value, rv.value_size)
    blsct.free_obj(rv)
    self.rp_cache = inst
    return inst

  def get_view_tag(self) -> int:
    """Get the view tag of the transaction output."""
    return blsct.get_ctx_out_view_tag(self.value())

  @override
  def value(self) -> Any:
    return blsct.cast_to_ctx_out(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("CTxOutBlsctData should not be directly instantiated.")


