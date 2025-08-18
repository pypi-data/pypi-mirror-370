from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from .sub_addr import SubAddr
from .token_id import TokenId
from typing import Any, Optional, Literal, override, Self 

TxOutputType = Literal["Normal", "StakedCommitment"]

class TxOut(ManagedObj, Serializable):
  """
  Represents a transaction output used to construct a CTxOut in a confidential transaction.

  >>> from blsct import ChildKey, DoublePublicKey, PublicKey, SubAddr, SubAddrId, TxOut
  >>> sub_addr = SubAddr.from_double_public_key(DoublePublicKey())
  >>> amount = 789
  >>> memo = "apple"
  >>> tx_out = TxOut(sub_addr, amount, memo)
  >>> tx_out.get_destination()
  SubAddr(827cc8283b488e5...) # doctest: +SKIP
  >>> tx_out.get_amount()
  789
  >>> tx_out.get_memo()
  'apple'
  >>> tx_out.get_token_id()
  TokenId(0000000000000000000000000000000000000000000000000000000000000000ffffffffffffffff)
  >>> tx_out.get_min_stake()
  0
  >>> ser = tx_out.serialize()
  >>> deser = TxOut.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(
    self,
    sub_addr: SubAddr,
    amount: int,
    memo: str,
    token_id: Optional[TokenId] = None,
    output_type: TxOutputType = 'Normal',
    min_stake: int = 0,
  ):
    token_id = TokenId() if token_id is None else token_id

    rv = blsct.build_tx_out(
      sub_addr.value(),
      amount,
      memo,
      token_id.value(),
      blsct.Normal if output_type == "Normal" else blsct.StakedCommitment,
      min_stake
    )
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to build TxOut. Error code = {rv_result}")

    obj = rv.value
    obj_size = rv.value_size
    blsct.free_obj(rv)

    super().__init__(obj)
    self.obj_size = obj_size

  def get_destination(self) -> SubAddr:
    """Get the destination of the transaction output."""
    obj = blsct.get_tx_out_destination(self.value())
    return SubAddr.from_obj(obj)

  def get_amount(self) -> int:
    """Get the amount of the transaction output."""
    return blsct.get_tx_out_amount(self.value())

  def get_memo(self) -> str:
    """Get the memo of the transaction output."""
    return blsct.get_tx_out_memo(self.value())

  def get_token_id(self) -> TokenId:
    """Get the token ID of the transaction output."""
    obj = blsct.get_tx_out_token_id(self.value())
    return TokenId.from_obj(obj)

  def get_output_type(self) -> TxOutputType:
    """Get the output type of the transaction output."""
    return blsct.get_tx_out_output_type(self.value())

  def get_min_stake(self) -> int:
    """Get the min stake of the transaction output."""
    return blsct.get_tx_out_min_stake(self.value())

  @override
  def value(self) -> Any:
    return blsct.cast_to_tx_out(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create a TxOut without required parameters.")

  def serialize(self) -> str:
    """Serialize the TxOut to a hexadecimal string"""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, self.obj_size)

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the TxOut from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    obj = blsct.hex_to_malloced_buf(hex)
    return cls.from_obj_with_size(obj, obj_size)
