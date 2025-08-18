from . import blsct
from .managed_obj import ManagedObj
from .serializable import Serializable
from .scalar import Scalar
from .pretty_printable import PrettyPrintable
from typing import Any, override, Self, Type

class Point(ManagedObj, Serializable, PrettyPrintable):
  """
  Represents an element in the BLS12-381 G1 curve group.
  A wrapper of MclG1Point_ in navio-core.

  .. _MclG1Point: https://github.com/nav-io/navio-core/blob/master/src/blsct/arith/mcl/mcl_g1point.h

  Instantiating a Point object without a parameter returns the base point of the BLS12-381 G1 curve.

  >>> from blsct import Point, Scalar
  >>> Point()
  Point(a4eb0bfafd459d032737596...) # doctest: +SKIP
  >>> Point.random()
  Point(b45f2b49f894ec369133766...) # doctest: +SKIP
  >>> Point.base()
  Point(97f1d3a73197d7942695638...) # doctest: +SKIP
  >>> s = Scalar()
  >>> Point.from_scalar(s)
  Point(b83378b6c0b2cb416dc7391...) # doctest: +SKIP
  >>> p = Point()
  >>> p.is_valid()
  True
  >>> q = Point()
  >>> p == p
  True
  >>> p == q
  False
  >>> ser = p.serialize()
  >>> deser = Point.deserialize(ser)
  >>> ser == deser.serialize()
  True
  """
  def __init__(self, obj: Any = None):
    super().__init__(obj)

  @classmethod
  def random(cls: Type[Self]) -> Self:
    """Generate a random point"""
    rv = blsct.gen_random_point()
    point = cls.from_obj(rv.value)
    blsct.free_obj(rv)
    return point

  @classmethod
  def base(cls: Type[Self]) -> Self:
    """Get the base point of the BLS12-381 G1 curve"""
    rv = blsct.gen_base_point()
    point = cls.from_obj(rv.value)
    blsct.free_obj(rv)
    return point

  @classmethod
  def from_scalar(cls: Type[Self], scalar: Scalar) -> Self:
    obj = blsct.point_from_scalar(scalar.value())
    return cls.from_obj(obj)

  def is_valid(self) -> bool:
    """Check if the point is valid"""
    return blsct.is_valid_point(self.value())

  @override
  def serialize(self) -> str:
    """Serialize the point to a hexadecimal string"""
    return blsct.serialize_point(self.value())

  @classmethod
  @override
  def deserialize(cls, hex: str) -> Self:
    """Deserialize the point from a hexadecimal string"""
    if len(hex) % 2 != 0:
      hex = f"0{hex}"
    rv = blsct.deserialize_point(hex)
    rv_result = int(rv.result)
    if rv_result != 0:
      blsct.free_obj(rv)
      raise RuntimeError(f"Deserializaiton failed. Error code = {rv_result}")  # pragma: no co

    obj = rv.value
    blsct.free_obj(rv)
    return cls.from_obj(obj)

  @override
  def value(self) -> Any:
    return blsct.cast_to_point(self.obj)

  @classmethod
  def default_obj(cls) -> Any:
    rv = blsct.gen_random_point()
    obj = rv.value
    blsct.free_obj(rv)
    return obj 
 
  def pretty_print(self) -> str:
    """Convert the point to a string representation"""
    return blsct.point_to_str(self.value())

  @override
  def __eq__(self, other: object) -> bool:
    if isinstance(other, Point):
      return bool(blsct.is_point_equal(self.value(), other.value()))
    else:
      return False

