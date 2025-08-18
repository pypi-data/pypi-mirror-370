from typing import Protocol, runtime_checkable

@runtime_checkable
class PrettyPrintable(Protocol):
  def pretty_print(self) -> str: ...

