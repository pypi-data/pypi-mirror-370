from .. import blsct
from ..scalar import Scalar
from .child_key_desc.tx_key_desc.view_key import ViewKey
from .child_key_desc.tx_key_desc.spending_key import SpendingKey
from .public_key import PublicKey

class PrivSpendingKey(Scalar):
  """
  Represents a private spending key. A private spending key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import PrivSpendingKey, PublicKey, ViewKey, SpendingKey
  >>> pk = PublicKey()
  >>> vk = ViewKey()
  >>> sk = SpendingKey()
  >>> PrivSpendingKey(pk, vk, sk, 1, 2)
  PrivSpendingKey(1a38fdaf2544f9ecb9ad4370f0d5bf310cf9f9722842b5a6cccb30714651ab9a) # doctest: +SKIP
  """
  def __init__(
    self,
    blinding_pub_key: PublicKey,
    view_key: ViewKey,
    spending_key: SpendingKey,
    account: int,
    address: int
  ):
    blsct_psk = blsct.calc_priv_spending_key(
      blinding_pub_key.value(),
      view_key.value(),
      spending_key.value(),
      account,
      address
    )
    super().__init__(blsct_psk)

