from . import blsct
from .managed_obj import ManagedObj
from .keys.public_key import PublicKey
from .scalar import Scalar
from .serializable import Serializable
from typing import Any, override, Self, Type

class Signature(ManagedObj, Serializable):
  """
  Represents the signature of a transaction.

  >>> from blsct import PublicKey, Scalar, Signature
  >>> sk = Scalar()
  >>> pk = PublicKey.from_scalar(sk)
  >>> sig = Signature(sk, 'navio')
  >>> sig.verify('navio', pk)
  >>> ser = sig.serialize()
  >>> deser = Signature.deserialize(ser)
  >>> ser == deser.serialize()
  >>> True
  """
  def __init__(self, priv_key: Scalar, msg: str):
    obj = blsct.sign_message(priv_key.value(), msg)
    super().__init__(obj)

  def verify(self, msg: str, pub_key: PublicKey) -> bool:
    """Verify a signature using the public key corresponding to the private key that signed the transaction."""
    return blsct.verify_msg_sig(pub_key.value(), msg, self.value())

  @override
  def value(self) -> Any:
    return blsct.cast_to_signature(self.obj)

  @classmethod
  @override
  def default_obj(cls: Type[Self]) -> Self:
    raise NotImplementedError(f"Cannot create a Signature without required parameters.")

  def serialize(self) -> str:
    """Serialize the Signature to a hexadecimal string"""
    return blsct.serialize_signature(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the Signature from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_signature(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize Signature. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 
