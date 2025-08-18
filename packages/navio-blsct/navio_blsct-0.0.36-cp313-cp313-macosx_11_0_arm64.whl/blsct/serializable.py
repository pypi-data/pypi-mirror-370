from .clonable import Clonable
from typing import Protocol, runtime_checkable, Self, Type

@runtime_checkable
class Serializable(Clonable, Protocol):
  def serialize(self) -> str: ...

  @classmethod
  def deserialize(cls: Type[Self], hex: str) -> Self: ...

  def clone(self) -> Self:
    ser = self.serialize()
    return self.__class__.deserialize(ser)

