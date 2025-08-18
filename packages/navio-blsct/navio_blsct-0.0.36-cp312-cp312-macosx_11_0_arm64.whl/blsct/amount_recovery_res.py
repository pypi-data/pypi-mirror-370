from . import blsct
from .serializable import Serializable
from typing import override, Self
import pickle

class AmountRecoveryRes(Serializable):
  """
  The result of recovering a single amount from a non-aggregated range proof.

  Refer to :class:`RangeProof` for a usage example.
  """
  def __init__(
    self,
    is_succ: bool,
    amount: int,
    message: str,
  ):
    self.is_succ = is_succ
    self.amount = amount
    self.message = message
  
  def __str__(self):
    is_succ = self.is_succ
    amount = self.amount
    message = self.message
    return f"AmtRecoveryRes({is_succ=}, {amount=}, {message=})"

  def serialize(self) -> str:
    """Serialize the AmountRecoveryRes to a hexadecimal string"""
    pickled_bytes = pickle.dumps({
        "is_succ": self.is_succ,
        "amount": self.amount,
        "message": self.message,
    })
    return pickled_bytes.hex()

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the AmountRecoveryRes from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_dict = pickle.loads(bytes.fromhex(hex))
    return cls(
        is_succ=obj_dict["is_succ"],
        amount=obj_dict["amount"],
        message=obj_dict["message"],
    )

