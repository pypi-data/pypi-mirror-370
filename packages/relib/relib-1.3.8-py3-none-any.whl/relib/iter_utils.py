from __future__ import annotations
from contextlib import contextmanager
from itertools import chain, islice
from typing import Any, Generic, Iterable, Literal, Sequence, overload
from .dict_utils import dict_firsts
from .types import T1, T2, T3, T4, T5, T, U

__all__ = [
  "as_list", "at",
  "chunked",
  "distinct_by", "distinct", "drop_none",
  "first", "flatten",
  "interleave", "intersect",
  "list_split",
  "move_value",
  "partition",
  "range_of", "reversed_enumerate",
  "seekable", "sort_by",
  "transpose",
]

def as_list(iterable: Iterable[T]) -> list[T]:
  return iterable if isinstance(iterable, list) else list(iterable)

def at(values: Sequence[T], index: int, default: U = None) -> T | U:
  try:
    return values[index]
  except IndexError:
    return default

def first(iterable: Iterable[T]) -> T | None:
  return next(iter(iterable), None)

def drop_none(iterable: Iterable[T | None]) -> list[T]:
  return [x for x in iterable if x is not None]

def distinct(iterable: Iterable[T]) -> list[T]:
  return list(dict.fromkeys(iterable))

def distinct_by(pairs: Iterable[tuple[object, T]]) -> list[T]:
  return list(dict_firsts(pairs).values())

def sort_by(pairs: Iterable[tuple[Any, T]], reverse=False) -> list[T]:
  pairs = sorted(pairs, key=lambda p: p[0], reverse=reverse)
  return [v for _, v in pairs]

def move_value(iterable: Iterable[T], from_i: int, to_i: int) -> list[T]:
  values = list(iterable)
  values.insert(to_i, values.pop(from_i))
  return values

def reversed_enumerate(values: Sequence[T] | tuple[T, ...]) -> Iterable[tuple[int, T]]:
  return zip(range(len(values))[::-1], reversed(values))

def intersect(*iterables: Iterable[T]) -> list[T]:
  return list(set.intersection(*map(set, iterables)))

def interleave(*iterables: Iterable[T]) -> list[T]:
  return flatten(zip(*iterables))

def list_split(iterable: Iterable[T], sep: T) -> list[list[T]]:
  values = [sep, *iterable, sep]
  split_at = [i for i, x in enumerate(values) if x is sep]
  ranges = list(zip(split_at[0:-1], split_at[1:]))
  return [values[start + 1:end] for start, end in ranges]

def partition(iterable: Iterable[tuple[bool, T]]) -> tuple[list[T], list[T]]:
  true_values, false_values = [], []
  for predicate, value in iterable:
    if predicate:
      true_values.append(value)
    else:
      false_values.append(value)
  return true_values, false_values

def range_of(values: Sequence) -> range:
  return range(len(values))

class seekable(Generic[T]):
  def __init__(self, iterable: Iterable[T]):
    self.index = 0
    self.source = iter(iterable)
    self.sink: list[T] = []

  def __iter__(self):
    return self

  def __next__(self) -> T:
    if len(self.sink) > self.index:
      item = self.sink[self.index]
    else:
      item = next(self.source)
      self.sink.append(item)
    self.index += 1
    return item

  def __bool__(self):
    return bool(self.lookahead(1))

  def clear(self):
    self.sink[:self.index] = []
    self.index = 0

  def seek(self, index: int) -> seekable[T]:
    remainder = index - len(self.sink)
    if remainder > 0:
      next(islice(self, remainder, remainder), None)
    self.index = max(0, min(index, len(self.sink)))
    return self

  def step(self, count: int) -> seekable[T]:
    return self.seek(self.index + count)

  @contextmanager
  def freeze(self):
    def commit(offset: int = 0):
      nonlocal initial_index
      initial_index = self.index + offset
    initial_index = self.index
    try:
      yield commit
    finally:
      self.seek(initial_index)

  def lookahead(self, count: int) -> list[T]:
    with self.freeze():
      return list(islice(self, count))

  def forgetful(self) -> Iterable[T]:
    for value in self:
      self.clear()
      yield value

@overload
def chunked(values: Iterable[T], *, num_chunks: int, chunk_size=None) -> list[list[T]]: ...
@overload
def chunked(values: Iterable[T], *, num_chunks=None, chunk_size: int) -> list[list[T]]: ...
def chunked(values, *, num_chunks=None, chunk_size=None):
  values = as_list(values)
  if isinstance(num_chunks, int):
    chunk_size = (len(values) / num_chunks).__ceil__()
  elif isinstance(chunk_size, int):
    num_chunks = (len(values) / chunk_size).__ceil__()
  assert isinstance(num_chunks, int) and isinstance(chunk_size, int)
  return [values[i * chunk_size:(i + 1) * chunk_size] for i in range(num_chunks)]

@overload
def flatten(iterable: Iterable[T], depth: Literal[0]) -> list[T]: ...
@overload
def flatten(iterable: Iterable[Iterable[T]], depth: Literal[1] = 1) -> list[T]: ...
@overload
def flatten(iterable: Iterable[Iterable[Iterable[T]]], depth: Literal[2]) -> list[T]: ...
@overload
def flatten(iterable: Iterable[Iterable[Iterable[Iterable[T]]]], depth: Literal[3]) -> list[T]: ...
@overload
def flatten(iterable: Iterable[Iterable[Iterable[Iterable[Iterable[T]]]]], depth: Literal[4]) -> list[T]: ...
@overload
def flatten(iterable: Iterable, depth: int) -> list: ...
def flatten(iterable: Iterable, depth: int = 1) -> list:
  for _ in range(depth):
    iterable = chain.from_iterable(iterable)
  return list(iterable)

@overload
def transpose(tuples: Iterable[tuple[T1, T2]], default_num_returns=0) -> tuple[list[T1], list[T2]]: ...
@overload
def transpose(tuples: Iterable[tuple[T1, T2, T3]], default_num_returns=0) -> tuple[list[T1], list[T2], list[T3]]: ...
@overload
def transpose(tuples: Iterable[tuple[T1, T2, T3, T4]], default_num_returns=0) -> tuple[list[T1], list[T2], list[T3], list[T4]]: ...
@overload
def transpose(tuples: Iterable[tuple[T1, T2, T3, T4, T5]], default_num_returns=0) -> tuple[list[T1], list[T2], list[T3], list[T4], list[T5]]: ...
@overload
def transpose(tuples: Iterable[tuple[T, ...]], default_num_returns=0) -> tuple[list[T], ...]: ...
def transpose(tuples: Iterable[tuple], default_num_returns=0) -> tuple[list, ...]:
  output = tuple(zip(*tuples))
  if not output:
    return ([],) * default_num_returns
  return tuple(map(list, output))
