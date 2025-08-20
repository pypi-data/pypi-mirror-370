import time


def retry(*, max_retry=0, seconds_to_wait=10, raise_exception=Exception, catch_exceptions=(Exception,)):
    def wrapper(func):
        def do_retry(*args, **kwargs):
            for i in range(max_retry + 1):  # the meaning of 1 is we should try at least once.
                if i > 0:
                    time.sleep(seconds_to_wait)
                try:
                    return func(*args, **kwargs)
                except catch_exceptions as e:
                    print(f"{catch_exceptions} raised. #tried: {i + 1}. err_msg: {e}")
            raise raise_exception("Exceeds max number of retry.")
        return do_retry
    return wrapper

__all__ = ["retry"]