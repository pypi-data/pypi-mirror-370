from typing import Any
from .types import T

__all__ = [
  "as_any",
  "ensure_tuple",
  "non_none",
]

def as_any(obj: Any) -> Any:
  return obj

def non_none(obj: T | None) -> T:
  assert obj is not None
  return obj

def ensure_tuple(value: T | tuple[T, ...]) -> tuple[T, ...]:
  return value if isinstance(value, tuple) else (value,)
