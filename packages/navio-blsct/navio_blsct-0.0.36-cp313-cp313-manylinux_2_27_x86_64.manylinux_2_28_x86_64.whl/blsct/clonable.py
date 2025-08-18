from typing import Protocol, runtime_checkable, Self

@runtime_checkable
class Clonable(Protocol):
  def clone(self) -> Self: ...

