from __future__ import annotations
from . import blsct
from .amount_recovery_res import AmountRecoveryRes
from .managed_obj import ManagedObj
from .point import Point
from .scalar import Scalar
from .serializable import Serializable
from .token_id import TokenId
from typing import Any, Optional, override, Self, TYPE_CHECKING

if TYPE_CHECKING:
  from .range_proof import RangeProof
  from .amount_recovery_req import AmountRecoveryReq

class RangeProof(ManagedObj, Serializable):
  """
  Represents a (possibly aggregated) range proof for one or more confidential transaction amounts.

>>> from blsct import AmountRecoveryReq, AmountRecoveryRes, Point, RangeProof, TokenId
>>> nonce = Point()
>>> token_id = TokenId()
>>> rp = RangeProof([456], nonce, 'navio', token_id)
>>> RangeProof.verify_proofs([rp])
True
>>> req = AmountRecoveryReq(rp, nonce)
>>> res = RangeProof.recover_amounts([req])
0: AmtRecoveryRes(is_succ=True, amount=456, message='navio')
>>> rp.get_A()
Point(a2fb420771db27ad...) # doctest: +SKIP
>>> rp.get_A_wip()
Point(a110e82e7ce9db7b...) # doctest: +SKIP
>>> rp.get_B()
Point(b20c77bdcf884cc9...) # doctest: +SKIP
>>> rp.get_r_prime()
Scalar(2edf3c0ca70d395fda7c809776a3328824a5fc29bd6261afd7e03e9ab952a31b) # doctest: +SKIP
>>> rp.get_s_prime()
Scalar(17fe26b25aeb9e2a24dcb257d308f27e57ab4fe6b852bead0259b8e0e4b9abe7) # doctest: +SKIP
>>> rp.get_delta_prime()
Scalar(1bc93e6b42fb582f51ba0cd51d64ca2b85cebd15cb8a5c84a1df16f0c6b13cea) # doctest: +SKIP
>>> rp.get_alpha_hat()
Scalar(1c1eaca43fbaf1ec5f1304ec56d0e29e639a5189a61a7bd752e1d449702c463b) # doctest: +SKIP
>>> rp.get_tau_x()
Scalar(5e07a8b9254fab11399f42d5695c9bfe3d00bc6478c5a480442cfac6567ef2ee) # doctest: +SKIP
>>> ser = rp.serialize()
>>> deser = RangeProof.deserialize(ser)
>>> ser == deser.serialize()
True
  """
  def __init__(
    self,
    amounts: list[int],
    nonce: Point,
    message: str,
    token_id: Optional[TokenId] = None,
  ):
    vec = blsct.create_uint64_vec()
    for amount in amounts:
      blsct.add_to_uint64_vec(vec, amount)

    if token_id is None:
      token_id = TokenId()
    
    rv = blsct.build_range_proof(
      vec,
      nonce.value(),
      message,
      token_id.value(),
    )
    blsct.free_uint64_vec(vec)

    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise RuntimeError(f"Building range proof failed. Error code = {rv_result}")

    super().__init__(rv.value)
    self.obj_size = rv.value_size
    blsct.free_obj(rv)

  @staticmethod
  def verify_proofs(proofs: list["RangeProof"]) -> bool:
    """Verify a list of range proofs."""
    vec = blsct.create_range_proof_vec()
    for proof in proofs:
      blsct.add_range_proof_to_vec(vec, proof.obj_size, proof.value())
    
    rv = blsct.verify_range_proofs(vec)
    rv_result = int(rv.result)

    if rv_result != 0:
      blsct.free_obj(rv)
      raise RuntimeError(f"Verifying range proofs failed. Error code = {rv_result}")

    blsct.free_range_proof_vec(vec)

    return rv.value != 0

  @staticmethod
  def recover_amounts(reqs: list[AmountRecoveryReq]) -> list[AmountRecoveryRes]:
    """
    Recover the amount from each given single-amount range proof. The results may include failures.
    """
    req_vec = blsct.create_amount_recovery_req_vec()

    for req in reqs:
      blsct_req = blsct.gen_amount_recovery_req(
        req.range_proof.value(),
        req.range_proof.obj_size,
        req.nonce.value(),
      )
      blsct.add_to_amount_recovery_req_vec(req_vec, blsct_req)

    rv = blsct.recover_amount(req_vec)
    blsct.free_amount_recovery_req_vec(req_vec)

    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_amounts_ret_val(rv)
      raise RuntimeError(f"Recovering amount failed. Error code = {rv_result}")
 
    res = []
    size = blsct.get_amount_recovery_result_size(rv.value)

    for i in range(size):
      is_succ = blsct.get_amount_recovery_result_is_succ(rv.value, i)
      amount = blsct.get_amount_recovery_result_amount(rv.value, i)
      message = blsct.get_amount_recovery_result_msg(rv.value, i)
      x = AmountRecoveryRes(
        is_succ, 
        amount,
        message,
      )
      res.append(x)
    
    blsct.free_amounts_ret_val(rv)
    return res

  def get_A(self) -> Point:
    """Get the range proof element A."""
    obj = blsct.get_range_proof_A(self.value(), self.obj_size)
    return Point.from_obj(obj)

  def get_A_wip(self) -> Point:
    """Get the range proof element A_wip."""
    obj = blsct.get_range_proof_A_wip(self.value(), self.obj_size)
    return Point.from_obj(obj)

  def get_B(self) -> Point:
    """Get the range proof element B."""
    obj = blsct.get_range_proof_B(self.value(), self.obj_size)
    return Point(obj)

  def get_r_prime(self) -> Scalar:
    """Get the range proof element r_prime."""
    obj = blsct.get_range_proof_r_prime(self.value(), self.obj_size)
    return Scalar(obj)

  def get_s_prime(self) -> Scalar:
    """Get the range proof element s_prime."""
    obj = blsct.get_range_proof_s_prime(self.value(), self.obj_size)
    return Scalar(obj)

  def get_delta_prime(self) -> Scalar:
    """Get the range proof element delta_prime."""
    obj = blsct.get_range_proof_delta_prime(self.value(), self.obj_size)
    return Scalar(obj)

  def get_alpha_hat(self) -> Scalar:
    """Get the range proof element alpha hat."""
    obj = blsct.get_range_proof_alpha_hat(self.value(), self.obj_size)
    return Scalar(obj)

  def get_tau_x(self) -> Scalar:
    """Get the range proof element tau_x."""
    obj = blsct.get_range_proof_tau_x(self.value(), self.obj_size)
    return Scalar(obj)

  @override
  def value(self) -> Any:
    return blsct.cast_to_range_proof(self.obj)

  def serialize(self) -> str:
    """Serialize the RangeProof to a hexadecimal string"""
    return blsct.serialize_range_proof(self.value(), self.obj_size)

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the RangeProof from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    rv =  blsct.deserialize_range_proof(hex, obj_size);
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize RangeProof. Error code = {rv_result}")

    obj = rv.value
    obj_size = rv.value_size
    blsct.free_obj(rv)
    return cls.from_obj_with_size(obj, obj_size)

