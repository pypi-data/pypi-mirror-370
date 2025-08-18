from . import blsct
from .keys.child_key_desc.tx_key_desc.view_key import ViewKey
from .keys.public_key import PublicKey
from .scalar import Scalar
from typing import Any, Self, Type

class ViewTag:
  """
  Represents a view tag derived from a blinding public key and a view key. The view tag is a 64-bit unsigned integer.

  >>> from blsct import ChildKey, PublicKey, Scalar, TxKey, ViewTag
  >>> blinding_pub_key = PublicKey()
  >>> seed = Scalar()
  >>> view_key = ChildKey(seed).to_tx_key().to_view_key()
  >>> ViewTag(blinding_pub_key, view_key)
  ViewTag(61568) # doctest: +SKIP
  """
  def __init__(
    self,
    blinding_pub_key: PublicKey,
    view_key: ViewKey
  ):
    value = blsct.calc_view_tag(
      blinding_pub_key.value(),
      view_key.value()
    )
    self.value = value

  def __str__(self):
    name = self.__class__.__name__
    return f"{name}({self.value})"

  def __repr__(self):
    return self.__str__()

  @classmethod
  def default_obj(cls: Type[Self]) -> Any:
    blinding_pub_key = PublicKey()
    view_key = ViewKey()
    return cls(blinding_pub_key, view_key)

