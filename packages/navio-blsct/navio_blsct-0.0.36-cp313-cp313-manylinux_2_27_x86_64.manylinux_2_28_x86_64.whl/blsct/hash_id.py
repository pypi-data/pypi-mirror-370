from . import blsct
from .serializable import Serializable
from .keys.public_key import PublicKey
from .keys.child_key_desc.tx_key_desc.view_key import ViewKey
from .managed_obj import ManagedObj
from typing import Any, override, Self

class HashId(ManagedObj, Serializable):
  """
  Represents a hash ID consisting of a blinding public key, a spending public key, and a view key. Also known as `CKeyId` which is an alias for `uint160` on the C++ side.

  >>> from blsct import ChildKey, HashId, PublicKey, ViewKey, Scalar
  >>> blinding_pub_key = PublicKey()
  >>> spending_pub_key = PublicKey()
  >>> seed = Scalar()
  >>> view_key = ChildKey(seed).to_tx_key().to_view_key()
  >>> hash_id = HashId(blinding_pub_key, spending_pub_key, view_key)
  >>> ser = hash_id.serialize()
  >>> deser = HashId.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(
    self,
    blinding_pub_key: PublicKey,
    spending_pub_key: PublicKey,
    view_key: ViewKey
  ):
    obj = blsct.calc_key_id(
      blinding_pub_key.value(),
      spending_pub_key.value(),
      view_key.value()
    )
    super().__init__(obj)

  def serialize(self) -> str:
    """Serialize the HashId to a hexadecimal string"""
    return blsct.serialize_key_id(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the HashId from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_key_id(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize HashId. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 

  @override
  def value(self) -> Any:
    return blsct.cast_to_key_id(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    blinding_pub_key = PublicKey()
    spending_pub_key = PublicKey()
    view_key = ViewKey()

    return blsct.calc_key_id(
      blinding_pub_key.value(),
      spending_pub_key.value(),
      view_key.value()
    )

