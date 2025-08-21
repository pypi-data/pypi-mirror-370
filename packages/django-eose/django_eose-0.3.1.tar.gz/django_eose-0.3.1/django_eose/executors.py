from concurrent.futures import ThreadPoolExecutor
from multiprocessing import get_context
from typing import Iterable, Callable, Generator, Any
import sys

def run_sync(
        iterable: Iterable,
        func: Callable,
        **_
    ) -> Generator[int, Any, None]:
    """
    Basic Python iteration over the iterable that executes the function one at a time.
    """
    for item in iterable:
        yield func(item)

def run_threads(
        iterable: Iterable,
        func: Callable,
        chunksize: int,
        max_workers: int | None = None
    ) -> Generator[int, Any, None]:
    """
    Divide the task between threads based on the number of workers.
    """
    def chunk_generator(iterable, chunksize):
        """
        Iterate over the iterable and return it divided into chunks based on the chunksize.
        """
        chunk: set = set()
        for item in iterable:
            chunk.add(item)
            if len(chunk) == chunksize:
                yield chunk
                chunk = set()
        if chunk:
            yield chunk

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        for chunk in chunk_generator(iterable, chunksize):
            for result in ex.map(func, chunk):
                yield result

def run_processes(
        iterable: Iterable,
        func: Callable,
        chunksize: int,
        max_workers: int | None = None
    ) -> Generator[int, Any, None]:
    """
    Divide the task between processes based on the number of workers. It's faster for CPU-bound tasks.
    """
    if sys.platform.startswith("linux"):
        # Use "fork" for better performance on Linux
        start_method = "fork"
    else:
        # Use "spawn" for Windows compatibility
        start_method = "spawn"

    ctx = get_context(start_method)
    with ctx.Pool(processes=max_workers) as pool:
        for result in pool.imap_unordered(func, iterable, chunksize=chunksize):
            yield result

def get_executor(mode: str) -> Callable[[str], Generator[int, Any, None]]:
    match mode:
        case "processes":
            return run_processes
        case "threads":
            return run_threads
        case "sync":
            return run_sync
        case _:
            raise ValueError(f"Invalid executor: {mode}")
