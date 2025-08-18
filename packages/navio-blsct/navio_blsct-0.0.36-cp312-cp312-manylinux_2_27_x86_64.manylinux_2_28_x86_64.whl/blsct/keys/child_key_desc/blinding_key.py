from ...scalar import Scalar
from typing import Any

class BlindingKey(Scalar):
  """
  Represents a blinding key. A blinding key is a Scalar and introduces no new functionality; it serves purely as a semantic alias.

  >>> from blsct import BlindingKey
  >>> BlindingKey()
  BlindingKey(2b55c4ecbf4abdc2f6c9a4890b2b91f650d10fd73a146157e016cb8314edad75)  # doctest: +SKIP
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

 
