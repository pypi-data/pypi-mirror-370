from . import blsct
from .keys.child_key_desc.tx_key_desc.spending_key import SpendingKey
from .managed_obj import ManagedObj
from .out_point import OutPoint
from .serializable import Serializable
from .keys.child_key_desc.tx_key_desc.spending_key import SpendingKey
from .token_id import TokenId
from typing import Any, override, Self

class TxIn(ManagedObj, Serializable):
  """
  Represents a transaction input used to construct CTxIn in a confidential transaction.

  >>> from blsct import OutPoint, SpendingKey, TokenId, CTxId, TxIn, CTX_ID_SIZE
  >>> import secrets
  >>> amount = 123
  >>> gamma = 100
  >>> spending_key = SpendingKey()
  >>> token_id = TokenId()
  >>> ctx_id = CTxId.deserialize(secrets.token_hex(CTX_ID_SIZE))
  >>> out_point = OutPoint(ctx_id, 0)
  >>> tx_in = TxIn(amount, gamma, spending_key, token_id, out_point)
  >>> tx_in.get_amount()
  123
  >>> tx_in.get_gamma()
  100
  >>> tx_in.get_spending_key()
  SpendingKey(36bcc5eac63182e19...) # doctest: +SKIP
  >>> tx_in.get_token_id()
  TokenId(000000000000000000000...) # doctest: +SKIP
  >>> tx_in.get_out_point()
  OutPoint(31f41784d028c886a886...) # doctest: +SKIP
  >>> tx_in.get_staked_commitment()
  False
  >>> tx_in.get_rbf()
  False
  >>> ser = tx_in.serialize()
  >>> deser = TxIn.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(
    self,
    amount: int,
    gamma: int,
    spending_key: SpendingKey,
    token_id: TokenId,
    out_point: OutPoint,
    staked_commitment: bool = False,
    rbf: bool = False,
  ):
    rv = blsct.build_tx_in(
      amount,
      gamma,
      spending_key.value(),
      token_id.value(),
      out_point.value(),
      staked_commitment,
      rbf
    )
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to build TxIn. Error code = {rv_result}")

    obj = rv.value
    obj_size = rv.value_size
    blsct.free_obj(rv)

    super().__init__(obj)
    self.obj_size = obj_size

  def get_amount(self) -> int:
    """Get the amount of the transaction input."""
    return blsct.get_tx_in_amount(self.value())

  def get_gamma(self) -> int:
    """Get the gamma value of the transaction input."""
    return blsct.get_tx_in_gamma(self.value())

  def get_spending_key(self) -> SpendingKey:
    """Get the spending key of the transaction input."""
    obj = blsct.get_tx_in_spending_key(self.value())
    return SpendingKey.from_obj(obj)

  def get_token_id(self) -> TokenId:
    """Get the token ID of the transaction input."""
    obj = blsct.get_tx_in_token_id(self.value())
    return TokenId.from_obj(obj)

  def get_out_point(self) -> OutPoint:
    """Get the out point of the transaction input."""
    obj = blsct.get_tx_in_out_point(self.value())
    return OutPoint.from_obj(obj)

  def get_staked_commitment(self) -> bool:
    """Get the staked commitment flag of the transaction input."""
    return blsct.get_tx_in_staked_commitment(self.value())

  def get_rbf(self) -> bool:
    """Get the replace-by-fee flag of the transaction input."""
    return blsct.get_tx_in_rbf(self.value())

  @override
  def value(self) -> Any:
    return blsct.cast_to_tx_in(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create a TxIn without required parameters.")

  def serialize(self) -> str:
    """Serialize the TxIn to a hexadecimal string"""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, self.obj_size)

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the TxIn from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    obj = blsct.hex_to_malloced_buf(hex)
    return cls.from_obj_with_size(obj, obj_size)

