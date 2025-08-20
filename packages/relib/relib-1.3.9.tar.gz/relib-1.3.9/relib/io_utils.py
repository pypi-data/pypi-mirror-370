import json
from pathlib import Path
from typing import Any, Iterable

__all__ = [
  "clear_directory",
  "empty_dirs",
  "read_json",
  "write_json",
]

default_sentinel = object()

def read_json(path: Path, default=default_sentinel) -> Any:
  if default is not default_sentinel and not path.exists():
    return default
  with path.open("r") as f:
    return json.load(f)

def write_json(path: Path, obj: object, indent: None | int = None) -> None:
  with path.open("w") as f:
    separators = (",", ":") if indent is None else None
    return json.dump(obj, f, indent=indent, separators=separators)

def empty_dirs(path: Path) -> Iterable[Path]:
  nonempty_count = 0
  for child in path.iterdir():
    nonempty_count += 1
    if child.is_dir():
      for grand_child in empty_dirs(child):
        yield grand_child
        nonempty_count -= child == grand_child
  if nonempty_count == 0:
    yield path

def clear_directory(path: Path):
  if path.is_dir():
    for file in path.glob("**/.DS_Store"):
      file.unlink()
    for directory in empty_dirs(path):
      directory.rmdir()
