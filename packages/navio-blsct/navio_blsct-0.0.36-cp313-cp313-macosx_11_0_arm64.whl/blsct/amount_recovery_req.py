from __future__ import annotations
from . import blsct
from .point import Point
from .range_proof import RangeProof
from .serializable import Serializable
from typing import override, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from .range_proof import RangeProof

class AmountRecoveryReq(Serializable):
  """
  A request for recovering a single amount from a non-aggregated range proof.

  Refer to :class:`RangeProof` for a usage example.
  """
  def __init__(
    self,
    range_proof: "RangeProof",
    nonce: Point,
  ):
    self.range_proof = range_proof
    self.nonce = nonce

  def serialize(self) -> str:
    """Serialize the AmountRecoveryReq to a hexadecimal string"""
    range_proof_hex = self.range_proof.serialize()
    nonce_hex = self.nonce.serialize()
    return range_proof_hex + nonce_hex

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the AmountRecoveryReq from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    hex_len = len(hex)
    nonce_hex_len = blsct.POINT_SIZE * 2
    
    range_proof_hex_len = hex_len - nonce_hex_len
    range_proof_hex = hex[:range_proof_hex_len]
    nonce_hex = hex[range_proof_hex_len:]

    nonce = Point.deserialize(nonce_hex)
    range_proof = RangeProof.deserialize(range_proof_hex)

    return cls(range_proof, nonce)

