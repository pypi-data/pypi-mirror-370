from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from .pretty_printable import PrettyPrintable
from typing import Any, override, Self 

class Scalar(ManagedObj, Serializable, PrettyPrintable):
  """
  Represents an element of the finite field :math:`\\mathbb{F}_r`, where :math:`r` is the order of the generator point of the BLS12-381 G1 group.

  A wrapper of MclScalar_ in navio-core.

  .. _MclScalar: https://github.com/nav-io/navio-core/blob/master/src/blsct/arith/mcl/mcl_scalar.h

  Instantiating a Scalar without a parameter is equivalent to calling Scalar.random().

  >>> from blsct import Scalar
  >>> Scalar()
  Scalar(5131bedc360ef599553bc6f020c251183ae8504b7b4fe0991e1e5864cc4e422) # doctest: +SKIP
  >>> Scalar(123)
  Scalar(7b)
  >>> Scalar.zero()
  Scalar(0)
  >>> Scalar.random()
  Scalar(693a3c156e22d2305c30e4297e3f974201a081e0910f7303ebc5f36f00161c43) # doctest: +SKIP
  >>> a = Scalar()
  >>> b = Scalar()
  >>> a == a
  True
  >>> a == b
  False
  >>> a.to_int()
  5339113002865401837 # doctest: +SKIP
  >>> ser = a.serialize()
  >>> deser = Scalar.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(self, value: Any = None):
    if isinstance(value, int):
      rv = blsct.gen_scalar(value)
      super().__init__(rv.value)
    elif value is None:
      super().__init__()
    elif isinstance(value, object):
      super().__init__(value)
    else:
      raise ValueError(f"Scalar can only be instantiated with int, but got '{type(value).__name__}'")

  @classmethod
  def random(cls) -> Self:
    """Generate a random scalar"""
    rv = blsct.gen_random_scalar()
    scalar = cls(rv.value)
    blsct.free_obj(rv)
    return scalar

  def to_int(self) -> int:
    """Convert the scalar to an integer"""
    return  blsct.scalar_to_uint64(self.value())

  def pretty_print(self) -> str:
    """Convert the scalar to a string representation"""
    return blsct.scalar_to_str(self.value())

  @override
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Scalar):
      return bool(blsct.is_scalar_equal(self.value(), other.value()))
    else:
      return False

  @classmethod
  def zero(cls) -> Self:
    """Return a zero scalar"""
    return cls(0)

  @override
  def value(self) -> Any:
    return blsct.cast_to_scalar(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_random_scalar()
    obj = rv.value
    blsct.free_obj(rv)
    return obj

  def serialize(self) -> str:
    """Serialize the scalar to a hexadecimal string"""
    return blsct.serialize_scalar(self.value())
    
  @classmethod
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the scalar from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_scalar(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise RuntimeError(f"Deserializaiton failed. Error code = {rv_result}")  # pragma: no co
    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj)

