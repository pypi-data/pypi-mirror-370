from ...scalar import Scalar
from typing import Any

class TokenKey(Scalar):
  """
  Represents a token key. A token key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import TokenKey
  >>> TokenKey()
  TokenKey(444fcf29a7063c776439edd39cbd23dff6e5b1470423ffb3cc478084792aa555)  # doctest: +SKIP
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)
 

