from . import blsct
from abc import ABC, abstractmethod
from typing import Any, Type, Self
from .serializable import Serializable

class ManagedObj(ABC):
  def add_default_attrs(self):
    self.obj_size: int | None = None
    self._managed: bool = False
    self._borrowed: bool = False

  def __init__(self, obj=None):
    self.obj = self.default_obj() if obj is None else obj
    self.add_default_attrs()

  @abstractmethod
  def value(self):
    pass

  @classmethod
  def default_obj(cls: Type[Self]) -> Self:
    name = cls.__name__
    raise NotImplementedError(f"{name}.default_obj()")

  def move(self) -> Any:
    if self.obj is None:
      raise ValueError("Object is None")
    obj = self.obj
    self.obj = None
    return obj

  def __del__(self):
    if self.obj is not None and self._borrowed is False:
      blsct.free_obj(self.obj)

  def __enter__(self):
    self._managed = True
    return self

  def __exit__(self, *_):
    if self.obj is not None and self._managed is True and self._borrowed is False:
      blsct.free_obj(self.obj)
      self.obj = None
    return False

  def __str__(self):
    name = self.__class__.__name__
    if isinstance(self, Serializable):
      return f"{name}({self.serialize()})"
    else:
      return f"{name}({self.obj})"

  def __repr__(self):
    return self.__str__()

  @classmethod
  def from_obj(cls, obj):
    inst = cls.__new__(cls)
    inst.obj = obj
    inst.add_default_attrs()
    return inst

  @classmethod
  def from_obj_with_size(cls, obj, obj_size: int):
    inst = cls.from_obj(obj)
    inst.obj_size = obj_size
    return inst
