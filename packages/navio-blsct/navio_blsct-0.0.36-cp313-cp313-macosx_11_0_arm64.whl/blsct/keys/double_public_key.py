from .. import blsct
from ..managed_obj import ManagedObj
from .public_key import PublicKey
from ..scalar import Scalar
from ..serializable import Serializable
from typing import Any, override, Self, Type

class DoublePublicKey(ManagedObj, Serializable):
  """
  The unique source from which an address is derived.

  Instantiating a DoublePublicKey object without a parameter returns a DoublePublicKey consisting of two randomly generated PublicKeys.

  >>> from blsct import DoublePublicKey, PublicKey, ViewKey
  >>> DoublePublicKey()
  DoublePublicKey(889636dce7b7706ad4...) # doctest: +SKIP
  >>> pk1 = PublicKey()
  >>> pk2 = PublicKey()
  >>> DoublePublicKey.from_public_keys(pk1, pk2)
  DoublePublicKey(8284d61a300241dcbe...) # doctest: +SKIP
  >>> vk = ViewKey()
  >>> spending_pk = PublicKey()
  >>> DoublePublicKey.from_keys_and_acct_addr(vk, spending_pk, 1, 2)
  DoublePublicKey(8eb6d5f160935d06a1a...) # doctest: +SKIP
  >>> dpk = DoublePublicKey()
  >>> ser = dpk.serialize()
  >>> deser = DoublePublicKey.deserialize(ser)
  >>> deser.serialize() == ser
  True
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  @classmethod
  def from_public_keys(
    cls: Type[Self],
    pk1: PublicKey,
    pk2: PublicKey,
  ) -> Self:
    """Create a DoublePublicKey from two PublicKeys."""
    rv = blsct.gen_double_pub_key(pk1.value(), pk2.value())
    dpk = cls(rv.value)
    blsct.free_obj(rv)
    return dpk

  @classmethod
  def from_keys_and_acct_addr(
    cls: Type[Self],
    view_key: Scalar,
    spending_pub_key: PublicKey,
    account: int,
    address: int
  ) -> Self:
    """Create a DoublePublicKey from a view key, spending public key, account, and address."""
    obj = blsct.gen_dpk_with_keys_and_sub_addr_id(
      view_key.value(),
      spending_pub_key.value(),
      account,
      address
    )
    return cls(obj) 

  @override
  def serialize(self) -> str:
    """Serialize the DoublePublicKey to a hexadecimal string"""
    return blsct.serialize_dpk(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the DoublePublicKey from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_dpk(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize DoublePublicKey. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 

  @override
  def value(self):
    return blsct.cast_to_dpk(self.obj)

  @override
  @classmethod
  def default_obj(cls: Type[Self]) -> Self:
    pk1 = PublicKey()
    pk2 = PublicKey()
    tmp = DoublePublicKey.from_public_keys(pk1, pk2)
    obj = tmp.move()
    return obj

