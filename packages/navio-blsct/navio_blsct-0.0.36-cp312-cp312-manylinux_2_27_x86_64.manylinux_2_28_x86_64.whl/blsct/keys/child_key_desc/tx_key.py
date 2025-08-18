from ... import blsct
from ...scalar import Scalar
from .tx_key_desc.spending_key import SpendingKey
from .tx_key_desc.view_key import ViewKey
from typing import Any

class TxKey(Scalar):
  """
  Represents a tx key. A tx key is a Scalar and introduces no new functionality; it serves purely as a semantic alias. Both SpendingKey and ViewKey are exclusively derived from a TxKey.

  >>> from blsct import TxKey
  >>> k = TxKey()
  >>> k.to_spending_key()
  SpendingKey(63c64ea2d7cb5765fae960e1e1b985709e9d46e8c848086e35e53bfb75038421) # doctest: +SKIP
  >>> k.to_view_key()
  ViewKey(3f8b181966e7ffddc9312f6a57884f367989d7a24c96e9daca651c6b224fde9d) # doctest: +SKIP
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  def to_spending_key(self) -> SpendingKey:
    """derive a spending key from the tx key"""
    obj = blsct.from_tx_key_to_spending_key(self.value())
    return SpendingKey(obj)

  def to_view_key(self) -> ViewKey:
    """derive a view key from the tx key"""
    obj = blsct.from_tx_key_to_view_key(self.value())
    return ViewKey(obj)

