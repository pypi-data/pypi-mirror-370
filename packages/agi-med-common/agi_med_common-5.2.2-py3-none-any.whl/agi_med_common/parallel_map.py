from typing import Any, TypeVar
from collections.abc import Callable
from collections.abc import Iterable
import concurrent.futures
from tqdm import tqdm


X = TypeVar("X")


def parallel_map(
    func: Callable[..., X],
    items: Iterable[Any],
    process: bool = False,
    multiple_args: bool = False,
    kwargs_args: bool = False,
    max_workers: int = 2,
    show_tqdm: bool = False,
    desc: str = "",
) -> list[X]:
    pool = (
        concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
        if process
        else concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    )
    with pool as executor:
        futures = []
        for item in items:
            if kwargs_args:
                future = executor.submit(func, **item)
            elif multiple_args:
                future = executor.submit(func, *item)
            else:
                future = executor.submit(func, item)
            futures.append(future)
        results: list[X] = [future.result() for future in tqdm(futures, disable=(not show_tqdm), desc=desc)]
    return results
