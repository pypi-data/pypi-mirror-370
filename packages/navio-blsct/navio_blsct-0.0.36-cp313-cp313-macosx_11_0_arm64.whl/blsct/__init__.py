import typing

if not typing.TYPE_CHECKING:
  try:
    import blsct.blsct as x
    if not getattr(x, "_initialized", False):
      x.init()
      x._initialized = True
      del x

  except ImportError:
    pass

from .address import Address
from .address_encoding import AddressEncoding
from .amount_recovery_req import AmountRecoveryReq
from .amount_recovery_res import AmountRecoveryRes
from .ctx import CTx
from .ctx_id import CTxId
from .ctx_in import CTxIn
from .ctx_out import CTxOut
from .ctx_out_blsct_data import CTxOutBlsctData
from .hash_id import HashId
from .keys.child_key import ChildKey
from .keys.child_key_desc.blinding_key import BlindingKey
from .keys.child_key_desc.token_key import TokenKey
from .keys.child_key_desc.tx_key_desc.spending_key import SpendingKey
from .keys.child_key_desc.tx_key import TxKey
from .keys.child_key_desc.tx_key_desc.view_key import ViewKey
from .keys.double_public_key import DoublePublicKey
from .keys.priv_spending_key import PrivSpendingKey
from .keys.public_key import PublicKey
from .out_point import OutPoint
from .point import Point
from .range_proof import RangeProof
from .scalar import Scalar
from .script import Script
from .signature import Signature
from .sub_addr import SubAddr
from .sub_addr_id import SubAddrId
from .token_id import TokenId
from .tx_in import TxIn
from .tx_out import TxOut
from .view_tag import ViewTag

# inject the swig module constants, functions and etc into the current namespace 
import blsct.blsct as blsct_swig

for name in dir(blsct_swig):
  if not name.startswith("_") and name not in globals():
    globals()[name] = getattr(blsct_swig, name)

