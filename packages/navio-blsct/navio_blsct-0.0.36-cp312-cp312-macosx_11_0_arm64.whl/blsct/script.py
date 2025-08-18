from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from typing import Any, Self, override

class Script(ManagedObj, Serializable):
  """
  Represents a script, which may be a scriptPubKey, scriptSig, or scriptWitness. Also known as `CScript` on the C++ side.


  A :class:`Script` appears as an attribute of :class:`CTxOut` (scriptPubKey) or :class:`CTxIn` (scriptSig and scriptWitness), and is not meant to be instantiated directly.

  >>> from blsct import ChildKey, DoublePublicKey, OutPoint, PublicKey, SpendingKey, SubAddr, SubAddrId, TokenId, CTX_ID_SIZE, CTx, CTxId, TxIn, TxOut, Script
  >>> import secrets
  >>> num_tx_in = 1
  >>> num_tx_out = 1
  >>> default_fee = 200000
  >>> fee = (num_tx_in + num_tx_out) * default_fee
  >>> out_amount = 10000
  >>> in_amount = fee + out_amount
  >>> ctx_id = CTxId.deserialize(secrets.token_hex(32))
  >>> out_index = 0
  >>> out_point = OutPoint(ctx_id, out_index)
  >>> gamma = 100
  >>> spending_key = SpendingKey()
  >>> token_id = TokenId()
  >>> tx_in = TxIn(in_amount, gamma, spending_key, token_id, out_point)
  >>> sub_addr = SubAddr.from_double_public_key(DoublePublicKey())
  >>> tx_out = TxOut(sub_addr, out_amount, 'navio')
  >>> ctx = CTx([tx_in], [tx_out])
  >>> ctx_outs = ctx.get_ctx_outs()
  >>> script_pub_key = ctx_outs[0].get_script_pub_key()
  >>> ser = script_pub_key.serialize()
  >>> deser = Script.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  @override
  def value(self):
    return blsct.cast_to_script(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot directly instantiate create a Script without required parameters.")

  def serialize(self) -> str:
    """Serialize the Script to a hexadecimal string"""
    return blsct.serialize_script(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the Script from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_script(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise ValueError(f"Failed to deserialize OutPoint. Error code = {rv_result}")

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj) 
