from ....scalar import Scalar
from typing import Any

class SpendingKey(Scalar):
  """
  Represents a spending key. A spending key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import SpendingKey
  >>> SpendingKey()
  SpendingKey(b62a0f6b61bdb1780312a2e659c978b9400b8fca429d807d449edd94ebd6a30)  # doctest: +SKIP
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)
 
