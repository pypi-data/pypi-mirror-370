from ....scalar import Scalar
from typing import Any

class ViewKey(Scalar):
  """
  Represents a view key. A view key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import ViewKey
  >>> ViewKey()
  ViewKey(36827248acf0d00c8eaf139bfb86a92e7915fd40281e3a1f4e82c554b9ea5edb) # doctest: +SKIP
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

