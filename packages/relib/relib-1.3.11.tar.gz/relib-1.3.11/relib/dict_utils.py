from typing import Any, Callable, Iterable, overload
from .type_utils import as_any
from .types import K1, K2, K3, K4, K5, K6, T1, T2, K, T, U

sentinel = object()

__all__ = [
  "deep_dict_pairs", "deepen_dict", "dict_by", "dict_firsts",
  "flatten_dict",
  "get_at", "group",
  "key_of",
  "map_dict", "merge_dicts",
  "omit",
  "pick",
  "remap",
  "tuple_by",
]

def merge_dicts(*dicts: dict[K, T]) -> dict[K, T]:
  if len(dicts) == 1:
    return dicts[0]
  result = {}
  for d in dicts:
    result |= d
  return result

def omit(d: dict[K, T], keys: Iterable[K], optional=False) -> dict[K, T]:
  if keys:
    d = dict(d)
    for key in keys:
      try:
        del d[key]
      except KeyError if optional else ():
        pass
  return d

def pick(d: dict[K, T], keys: Iterable[K]) -> dict[K, T]:
  return {key: d[key] for key in keys}

def dict_by(keys: Iterable[K], values: Iterable[T]) -> dict[K, T]:
  return dict(zip(keys, values))

def tuple_by(d: dict[K, T], keys: Iterable[K]) -> tuple[T, ...]:
  return tuple(d[key] for key in keys)

def map_dict(fn: Callable[[T], T], d: dict[K, T]) -> dict[K, T]:
  return {key: fn(value) for key, value in d.items()}

@overload
def remap(d: dict[K1, T1]) -> dict[K1, T1]: ...
@overload
def remap(d: dict[K1, T1], *, keys: dict[K1, K2] = {}) -> dict[K2, T1]: ...
@overload
def remap(d: dict[K1, T1], *, values: dict[T1, T2] = {}) -> dict[K1, T2]: ...
@overload
def remap(d: dict[K1, T1], *, keys: dict[K1, K2], values: dict[T1, T2]) -> dict[K2, T2]: ...
def remap(d: dict, *, keys=sentinel, values=sentinel) -> dict:
  match (keys, values):
    case (dict(), dict()):
      return {keys[key]: values[value] for key, value in d.items()}
    case (dict(), _):
      return {keys[key]: value for key, value in d.items()}
    case (_, dict()):
      return {key: values[value] for key, value in d.items()}
  return d

def key_of(dicts: Iterable[dict[T, U]], key: T) -> list[U]:
  return [d[key] for d in dicts]

def get_at(d: dict, keys: Iterable[Any], default: T) -> T:
  try:
    for key in keys:
      d = d[key]
  except KeyError:
    return default
  return as_any(d)

def dict_firsts(pairs: Iterable[tuple[K, T]]) -> dict[K, T]:
  result: dict[K, T] = {}
  for key, value in pairs:
    result.setdefault(key, value)
  return result

def group(pairs: Iterable[tuple[K, T]]) -> dict[K, list[T]]:
  values_by_key = {}
  for key, value in pairs:
    values_by_key.setdefault(key, []).append(value)
  return values_by_key

def deep_dict_pairs(d, prefix=()):
  for key, value in d.items():
    if not isinstance(value, dict) or value == {}:
      yield prefix + (key,), value
    else:
      yield from deep_dict_pairs(value, prefix + (key,))

def flatten_dict(deep_dict: dict, prefix=()) -> dict:
  return dict(deep_dict_pairs(deep_dict, prefix))

@overload
def deepen_dict(d: dict[tuple[K1], U]) -> dict[K1, U]: ...
@overload
def deepen_dict(d: dict[tuple[K1, K2], U]) -> dict[K1, dict[K2, U]]: ...
@overload
def deepen_dict(d: dict[tuple[K1, K2, K3], U]) -> dict[K1, dict[K2, dict[K3, U]]]: ...
@overload
def deepen_dict(d: dict[tuple[K1, K2, K3, K4], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, U]]]]: ...
@overload
def deepen_dict(d: dict[tuple[K1, K2, K3, K4, K5], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, dict[K5, U]]]]]: ...
@overload
def deepen_dict(d: dict[tuple[K1, K2, K3, K4, K5, K6], U]) -> dict[K1, dict[K2, dict[K3, dict[K4, dict[K5, dict[K6, U]]]]]]: ...
def deepen_dict(d: dict[tuple[Any, ...], Any]) -> dict:
  output = {}
  if () in d:
    return d[()]
  for (*tail, head), value in d.items():
    curr = output
    for key in tail:
      curr = curr.setdefault(key, {})
    curr[head] = value
  return output
