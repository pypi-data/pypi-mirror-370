import re
from typing import Any, Callable, Iterable, overload
from .types import T

__all__ = [
  "clamp",
  "df_from_array",
  "for_each",
  "noop",
  "str_filterer", "StrFilter",
]

def noop() -> None:
  pass

def for_each(func: Callable[[T], Any], iterable: Iterable[T]) -> None:
  for item in iterable:
    func(item)

@overload
def clamp(value: int, low: int, high: int) -> int: ...
@overload
def clamp(value: float, low: float, high: float) -> float: ...
def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))

def _cat_tile(cats, n_tile):
  import numpy as np
  return cats[np.tile(np.arange(len(cats)), n_tile)]

def df_from_array(
  value_cols: dict[str, Any],
  dim_labels: list[tuple[str, list[str | int | float]]],
  indexed=False,
):
  import numpy as np
  import pandas as pd
  dim_sizes = np.array([len(labels) for _, labels in dim_labels])
  assert all(array.shape == tuple(dim_sizes) for array in value_cols.values())
  array_offsets = [
    (dim_sizes[i + 1:].prod(), dim_sizes[:i].prod())
    for i in range(len(dim_sizes))
  ]
  category_cols = {
    dim: _cat_tile(pd.Categorical(labels).repeat(repeats), tiles)
    for (dim, labels), (repeats, tiles) in zip(dim_labels, array_offsets)
  }
  value_cols = {name: array.reshape(-1) for name, array in value_cols.items()}
  df = pd.DataFrame({**category_cols, **value_cols}, copy=False)
  if indexed:
    df = df.set_index([name for name, _ in dim_labels])
  return df

StrFilter = Callable[[str], bool]

def str_filterer(
  include_patterns: list[re.Pattern[str]] = [],
  exclude_patterns: list[re.Pattern[str]] = [],
) -> StrFilter:
  def str_filter(string: str) -> bool:
    if any(pattern.search(string) for pattern in exclude_patterns):
      return False
    if not include_patterns:
      return True
    return any(pattern.search(string) for pattern in include_patterns)

  return str_filter
