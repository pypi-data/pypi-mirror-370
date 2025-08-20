import asyncio
import contextvars
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from time import time
from typing import Callable, Coroutine, Iterable, ParamSpec, TypeVar
from .iter_utils import as_list
from .processing_utils import noop
from .types import T

__all__ = [
  "as_async", "async_limit",
  "clear_console", "console_link",
  "default_executor", "default_workers",
  "raise_if_interrupt", "roll_tasks",
  "measure_duration",
]

P = ParamSpec("P")
R = TypeVar("R")
Coro = Coroutine[object, object, R]

default_workers = min(32, (os.cpu_count() or 1) + 4)
default_executor = ThreadPoolExecutor(max_workers=default_workers)

def raise_if_interrupt():
  if sys.exc_info()[0] in (KeyboardInterrupt, SystemExit):
    raise

def clear_console() -> None:
  os.system("cls" if os.name == "nt" else "clear")

def console_link(text: str, url: str) -> str:
  return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"

async def worker(task: Coro[T], semaphore: asyncio.Semaphore, update=noop) -> T:
  async with semaphore:
    result = await task
    update()
    return result

async def roll_tasks(tasks: Iterable[Coro[T]], workers=default_workers, progress=False) -> list[T]:
  semaphore = asyncio.Semaphore(workers)
  if not progress:
    return await asyncio.gather(*[worker(task, semaphore) for task in tasks])

  from tqdm import tqdm
  tasks = as_list(tasks)
  with tqdm(total=len(tasks)) as pbar:
    update = partial(pbar.update, 1)
    return await asyncio.gather(*[worker(task, semaphore, update) for task in tasks])

def as_async(workers: int | ThreadPoolExecutor = default_executor) -> Callable[[Callable[P, R]], Callable[P, Coro[R]]]:
  executor = ThreadPoolExecutor(max_workers=workers) if isinstance(workers, int) else workers

  def on_fn(func: Callable[P, R]) -> Callable[P, Coro[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
      loop = asyncio.get_running_loop()
      ctx = contextvars.copy_context()
      fn_call = partial(ctx.run, func, *args, **kwargs)
      return await loop.run_in_executor(executor, fn_call)
    return wrapper
  return on_fn

def async_limit(workers=default_workers) -> Callable[[Callable[P, Coro[R]]], Callable[P, Coro[R]]]:
  semaphore = asyncio.Semaphore(workers)

  def on_fn(func: Callable[P, Coro[R]]) -> Callable[P, Coro[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
      async with semaphore:
        return await func(*args, **kwargs)
    return wrapper
  return on_fn

active_mds = []

class measure_duration:
  def __init__(self, name):
    self.name = name
    active_mds.append(self)

  def __enter__(self):
    self.start = time()

  def __exit__(self, *_):
    duration = round(time() - self.start, 4)
    depth = len(active_mds) - 1
    indent = "──" * depth + " " * (depth > 0)
    text = f"{self.name}: {duration} seconds"
    print(indent + text)
    active_mds.remove(self)
