import functools
from itertools import zip_longest
import multiprocessing
import concurrent.futures


def maybe_multiprocessing(func, args, num_processes, use_tqdm=True, tqdm_desc=""):
    from tqdm import tqdm

    maybe_tqdm = functools.partial(tqdm, total=len(args), desc=tqdm_desc) if use_tqdm else lambda x: x
    if num_processes <= 0:
        res = [func(d) for d in maybe_tqdm(args)]
    else:
        with multiprocessing.Pool(processes=num_processes) as pool:
            res = list(maybe_tqdm(pool.imap_unordered(func, args)))
    return res


def maybe_multithreading(
    func, args_list, kwargs_list=(), num_threads=10, use_tqdm=False, tqdm_desc=""
):
    from tqdm import tqdm

    maybe_tqdm = functools.partial(tqdm, desc=tqdm_desc) if use_tqdm else lambda x: x
    d = {}
    if num_threads > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(func, *args, **kwargs)
                for args, kwargs in zip_longest(args_list, kwargs_list, fillvalue=d)
            ]
            res = [
                future.result() for future in maybe_tqdm(concurrent.futures.as_completed(futures))
            ]
    else:
        res = [
            func(*args, **kwargs)
            for args, kwargs in maybe_tqdm(zip_longest(args_list, kwargs_list, fillvalue=d))
        ]
    return res


__all__ = ["maybe_multiprocessing", "maybe_multithreading"]