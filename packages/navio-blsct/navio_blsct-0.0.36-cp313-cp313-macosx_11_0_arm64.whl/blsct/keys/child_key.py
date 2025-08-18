from .. import blsct
from ..scalar import Scalar
from .child_key_desc.blinding_key import BlindingKey
from .child_key_desc.token_key import TokenKey
from .child_key_desc.tx_key import TxKey

class ChildKey(Scalar):
  """
  Represents a child key. A child key is a Scalar and introduces no new functionality; it serves purely as a semantic alias. BlindingKey, TokenKey and TxKey are exclusively derived from a ChildKey.

  >>> from blsct import ChildKey, Scalar
  >>> s = Scalar()
  >>> k = ChildKey(s)
  >>> k.to_blinding_key()
  BlindingKey(610a6f73231d115a54aee8b43c6d6fc5349aa4c45dc9987aad3f7a98fc6249d8) # doctest: +SKIP
  >>> k.to_token_key()
  TokenKey(58fd2bdf696268ecfbed529b4968dbfa0e324e5cbe00b18a6398c7feaa9627a4) # doctest: +SKIP
  >>> k.to_tx_key()
  TxKey(2fc0697ce315e42491d60e278ac729802be887e912f536f67a8eea9dc4b2900c) # doctest: +SKIP
  >>> 
  """
  def __init__(
    self,
    seed: Scalar,
  ):
    """create a child key from a scalar"""
    obj = blsct.from_seed_to_child_key(seed.value())
    super().__init__(obj)

  def to_blinding_key(self) -> BlindingKey:
    """derive a blinding key from the child key"""
    obj = blsct.from_child_key_to_blinding_key(self.value())
    return BlindingKey(obj)

  def to_token_key(self) -> TokenKey:
    """derive a token key from the child key"""
    obj = blsct.from_child_key_to_token_key(self.value())
    return TokenKey(obj)

  def to_tx_key(self) -> TxKey:
    """derive a tx key from the child key"""
    obj = blsct.from_child_key_to_tx_key(self.value())
    return TxKey(obj)

