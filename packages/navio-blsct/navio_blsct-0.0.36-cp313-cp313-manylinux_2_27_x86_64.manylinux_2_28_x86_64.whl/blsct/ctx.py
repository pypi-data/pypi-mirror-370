from . import blsct
from .ctx_in import CTxIn
from .ctx_out import CTxOut
from .managed_obj import ManagedObj
from .serializable import Serializable
from .ctx_id import CTxId
from .tx_in import TxIn
from .tx_out import TxOut
from typing import Any, override, Self, Type

# stores serialized tx represented as uint8_t*
class CTx(ManagedObj, Serializable):
  """
  Represents a confidential transaction. Also known as `CMutableTransaction` on the C++ side.

  >>> from blsct import ChildKey, DoublePublicKey, OutPoint, PublicKey, SpendingKey, SubAddr, SubAddrId, TokenId, CTX_ID_SIZE, CTx, CTxId, TxIn, TxOut
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
  >>> for ctx_in in ctx.get_ctx_ins(): 
  ...   print(f"prev_out_hash: {ctx_in.get_prev_out_hash()}")
  ...   print(f"prev_out_n: {ctx_in.get_prev_out_n()}")
  ...   print(f"script_sig: {ctx_in.get_script_sig()}")
  ...   print(f"sequence: {ctx_in.get_sequence()}")
  ...   print(f"script_witness: {ctx_in.get_script_witness()}")
  ...
  prev_out_hash: CTxId(9194a7eaafe70c6f623eef4740c934f569b8a7f0a246ce4377c34a5bb9a6f126)
  prev_out_n: 0
  script_sig: Script(0000000000008f676000000000006b67400000000000726720000000)
  sequence: 4294967295
  script_witness: Script(0000000000008f676000000000006b67400000000000726720000000)
  >>> for ctx_out in ctx.get_ctx_outs():
  ...   print(f"value: {ctx_out.get_value()}")
  ...   print(f"script_pub_key: {ctx_out.get_script_pub_key()}")
  ...   print(f"blsct_data.spending_key: {ctx_out.blsct_data().get_spending_key()}")
  ...   print(f"blsct_data.ephemeral_key: {ctx_out.blsct_data().get_ephemeral_key()}")
  ...   print(f"blsct_data.blinding_key: {ctx_out.blsct_data().get_blinding_key()}")
  ...   print(f"blsct_data.view_tag: {ctx_out.blsct_data().get_view_tag()}")
  ...   rp = ctx_out.blsct_data().get_range_proof()
  ...   print(f"blsct_data.range_proof.A: {rp.get_A()}")
  ...   print(f"blsct_data.range_proof.A_wip: {rp.get_A_wip()}")
  ...   print(f"blsct_data.range_proof.B: {rp.get_B()}")
  ...   print(f"blsct_data.range_Proof.r_prime: {rp.get_r_prime()}")
  ...   print(f"blsct_data.range_proof.s_prime: {rp.get_s_prime()}")
  ...   print(f"blsct_data.range_proof.delta_prime: {rp.get_delta_prime()}")
  ...   print(f"blsct_data.range_proof.alpha_hat: {rp.get_alpha_hat()}")
  ...   print(f"blsct_data.range_proof.tau_x: {rp.get_tau_x()}")
  ...   print(f"token_id: token={ctx_out.get_token_id().token()}, subid={tx_out.get_token_id().subid()}")
  ...   print(f"vector_predicate: {ctx_out.get_vector_predicate()}")
  ...
  value: 0
  script_pub_key: Script(51000000000000000000000000000000000000000000000000000000) # doctest: +SKIP
  blsct_data.spending_key: SpendingKey(2db08363ad3374035953866a054d5501da26aefbe55b4566d5e28a8bd1c3c051) # doctest: +SKIP
  blsct_data.ephemeral_key: Point(b56c69fa701103d7228d365f4405ac81ca91dc7c4fe439e700289da87ca60d370680f1e03e64109bbce546028be38515) # doctest: +SKIP
  blsct_data.blinding_key: BlindingKey(1f8947367d5a91d84b6e743072e55424b57b66e9030d84bc4d2c1f0f69633f29) # doctest: +SKIP
  blsct_data.view_tag: 31130 # doctest: +SKIP
  blsct_data.range_proof.A: Point(a70ec0dfc74dc592c94e6a142824520af6aa42501cbd3700abc7fb8ef05b1b9da808a0f4eabf8a8a59eed227276a9339) # doctest: +SKIP
  blsct_data.range_proof.A_wip: Point(afe823eeca1b6c81f781e96f016d9d3679b7808f7f6940a012a28c49e5e3230b8ab64ffaa5ca50d7577d193fd3b7fa47) # doctest: +SKIP
  blsct_data.range_proof.B: Point(a93f76c421f03eef9744d232cc2d0c818830b7962db32350b23695107840f83ff2a976a4dd71abbb97fbb0d220d23921) # doctest: +SKIP
  blsct_data.range_Proof.r_prime: Scalar(28383d7f0279a9d57da02f9cd763c2fd2ac3af13267c36da251ce4b1aeebaec7) # doctest: +SKIP
  blsct_data.range_proof.s_prime: Scalar(164ba1cf029e24b9e8ef462ad741371f89e71ca7db5226f1bf331e18c55ac06b) # doctest: +SKIP
  blsct_data.range_proof.delta_prime: Scalar(452a82bdb8e035d53e6e45b92bdd3d49fb68045f15f0b3dbd97df60ae3a84c1e) # doctest: +SKIP
  blsct_data.range_proof.alpha_hat: Scalar(385ebad68297e142a0aa2e83897799df7a08adf0e8e23046884eb3ad041ea7bd) # doctest: +SKIP
  blsct_data.range_proof.tau_x: Scalar(6b537c1670116d3a7518b45b1b9ba5608ed1b597ea40f018390e19e0cb0b0507) # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615 # doctest: +SKIP
  vector_predicate: # doctest: +SKIPu
  value: 0 # doctest: +SKIP
  script_pub_key: Script(51000000f5000000c000000020000000a00000040000800080000004) # doctest: +SKIP
  blsct_data.spending_key: SpendingKey(24848b6f0958cf217783f48f260366e0e0c2ccda954a0188e83381c61bf33902) # doctest: +SKIP
  blsct_data.ephemeral_key: Point(800bfdedb0bee4dcf6f56309a8c6c566a57c12f77f0f2320243c672c7529451598b327f0fe58df8bbd655014620fcd8a) # doctest: +SKIP
  blsct_data.blinding_key: BlindingKey(4c1258acd66282b7ccc627f7f65e27faac425bfd0001a40100000000ffffffff) # doctest: +SKIP
  blsct_data.view_tag: 21881 # doctest: +SKIP
  blsct_data.range_proof.A: Point(8731fba528d2461adc510c2cea6538cb4c31869448ee04f83665aa24a83c6a79aff088893d908ad7df4236e8c10a7ed1) # doctest: +SKIP
  blsct_data.range_proof.A_wip: Point(b739df1c0a90ec625e155b2a371eaf20c87b0e9e1f354d233793553a61b472b804d1504640db589aec88faba42842798) # doctest: +SKIP
  blsct_data.range_proof.B: Point(8c1598246f94d52ce83b441eeaff84850f962a21ad2613740ccf21d1b032465070381ad8481bc245f25c2a61a535e5fc) # doctest: +SKIP
  blsct_data.range_Proof.r_prime: Scalar(1de1c43d513ce5096bbdda19ca6ac1543cdad4bfb7bef9fcfdefa75ea9a48a88) # doctest: +SKIP
  blsct_data.range_proof.s_prime: Scalar(71f2f4ef98c06db856707d00063ae8ec4056e65c752dff7a43202e02879eda82) # doctest: +SKIP
  blsct_data.range_proof.delta_prime: Scalar(5a8ce55526ff2b178b85d113086fa666311002368e34cd4fa577018436049d88) # doctest: +SKIP
  blsct_data.range_proof.alpha_hat: Scalar(6c99352423c2ff98671fdc97fefc00dc427022c88bab93acf1a5ed2d28311d26) # doctest: +SKIP
  blsct_data.range_proof.tau_x: Scalar(4193251795eaf35243e68c9fef5dd7cafd3c34bcc0422c5c5b8f825c56767546) # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615 # doctest: +SKIP
  vector_predicate: # doctest: +SKIP
  value: 292125 # doctest: +SKIP
  script_pub_key: Script(6a00000000000000ac00000000007400000000000000000001000000) # doctest: +SKIP
  blsct_data.spending_key: SpendingKey(4c1258acd66282b7ccc627f7f65e27faac425bfd0001a40100000000ffffffff) # doctest: +SKIP
  blsct_data.ephemeral_key: Point(c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000) # doctest: +SKIP
  blsct_data.blinding_key: BlindingKey(4c1258acd66282b7ccc627f7f65e27faac425bfd0001a40100000000ffffffff) # doctest: +SKIP
  blsct_data.view_tag: 0 # doctest: +SKIP
  blsct_data.range_proof.A: Point(c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000) # doctest: +SKIP
  blsct_data.range_proof.A_wip: Point(c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000) # doctest: +SKIP
  blsct_data.range_proof.B: Point(c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000) # doctest: +SKIP
  blsct_data.range_Proof.r_prime: Scalar(0) # doctest: +SKIP
  blsct_data.range_proof.s_prime: Scalar(0) # doctest: +SKIP
  blsct_data.range_proof.delta_prime: Scalar(0) # doctest: +SKIP
  blsct_data.range_proof.alpha_hat: Scalar(0) # doctest: +SKIP
  blsct_data.range_proof.tau_x: Scalar(0) # doctest: +SKIP
  token_id: token=0, subid=18446744073709551615 # doctest: +SKIP
  vector_predicate: 03b8d499d518e3b451b71cfab4d84bf885f46252aed7dc6d9dddc743cd3c996b5f0518596d5292a02980426512f7a31555 # doctest: +SKIP
  >>> ser = ctx.serialize()
  >>> deser = CTx.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(self, tx_ins: list[TxIn], tx_outs: list[TxOut]):
    self.tx_ins = []
    for tx_in in tx_ins:
      self.tx_ins.append(tx_in.clone())

    self.tx_outs = []
    for tx_out in tx_outs:
      self.tx_outs.append(tx_out.clone())

    def free_tx_ins_outs():
      for tx_in in self.tx_ins:
        blsct.free_obj(tx_in.value())

      for tx_out in self.tx_outs:
        blsct.free_obj(tx_out.value())

    # create vector object and add tx_ins to it
    tx_in_vec = blsct.create_tx_in_vec()
    for tx_in in self.tx_ins:
      blsct.add_tx_in_to_vec(tx_in_vec, tx_in.value())

    # create vector object and add tx_outs to it
    tx_out_vec = blsct.create_tx_out_vec()
    for tx_out in self.tx_outs:
      blsct.add_tx_out_to_vec(tx_out_vec, tx_out.value())

    rv = blsct.build_ctx(tx_in_vec, tx_out_vec)
    rv_result = int(rv.result)

    # free the temporary vector objects
    blsct.free_obj(tx_in_vec)
    blsct.free_obj(tx_out_vec)

    if rv_result == blsct.BLSCT_IN_AMOUNT_ERROR:
      blsct.free_obj(rv)
      free_tx_ins_outs()
      raise ValueError(f"Failed to build transaction. tx_ins[{rv.in_amount_err_index}] has an invalid amount")

    if rv_result == blsct.BLSCT_OUT_AMOUNT_ERROR:
      blsct.free_obj(rv)
      free_tx_ins_outs()
      raise ValueError(f"Failed to build transaciton. tx_outs[{rv.out_amount_err_index}] has an invalid amount")

    if rv_result != 0:
      free_tx_ins_outs()
      blsct.free_obj(rv)
      raise ValueError(f"building tx failed. Error code = {rv_result}")

    obj = rv.ser_ctx # rv.ser_ctx is a byte array*
    obj_size = rv.ser_ctx_size # rv.ser_ctx_size is the byte array size
    blsct.free_obj(rv)

    super().__init__(obj)
    self.obj_size = obj_size

  def get_ctx_id(self) -> CTxId:
    """Get the transaction ID."""
    tx_id_hex = blsct.get_ctx_id(self.value(), self.obj_size)

    return CTxId.deserialize(tx_id_hex)

  def get_ctx_ins(self) -> list[CTxIn]:
    """Get the list of CTxIns generated from TxIns."""
    ctx_ins = blsct.get_ctx_ins(self.value(), self.obj_size)
    num_ctx_ins = blsct.get_ctx_in_count(ctx_ins)

    xs = []
    for i in range(num_ctx_ins):
      rv = blsct.get_ctx_in(ctx_ins, i)
      x = CTxIn.from_obj(rv.value)
      xs.append(x)

    blsct.free_obj(ctx_ins)
    return xs

  def get_ctx_outs(self) -> list[CTxOut]:
    """Get the list of CTxOuts generated from TxOuts."""
    ctx_outs = blsct.get_ctx_outs(self.value(), self.obj_size)
    num_ctx_outs = blsct.get_ctx_out_count(ctx_outs)

    xs = []
    for i in range(num_ctx_outs):
      rv = blsct.get_ctx_out(ctx_outs, i)
      x = CTxOut.from_obj(rv.value)
      xs.append(x)

    blsct.free_obj(ctx_outs)
    return xs

  @override
  def serialize(self) -> str:
    """Serialize the transaction to a hexadecimal string."""
    buf = blsct.cast_to_uint8_t_ptr(self.value())
    return blsct.to_hex(buf, self.obj_size)

  @classmethod
  @override
  def deserialize(cls: Type[Self], hex: str) -> Self:
    """Deserialize a transaction from a hexadecimal string."""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    obj_size = len(hex) // 2
    obj = blsct.hex_to_malloced_buf(hex)
    return cls.from_obj_with_size(obj, obj_size)

  @override
  def value(self) -> Any:
    # self.obj is uint8_t*
    return blsct.cast_to_uint8_t_ptr(self.obj)

  @classmethod
  @override
  def default_obj(cls) -> Any:
    raise NotImplementedError("Cannot create a Tx without required parameters.")

