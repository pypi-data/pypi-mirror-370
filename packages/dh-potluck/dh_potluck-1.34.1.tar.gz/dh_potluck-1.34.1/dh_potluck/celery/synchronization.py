from contextlib import contextmanager, nullcontext, suppress
from functools import partial, wraps
from typing import Callable, Optional, TypeVar


class SemaphoreLocked(Exception):
    pass


try:
    from redis import Redis

    @contextmanager
    def Semaphore(redis_client: Redis, key_name: str, ttl: int, capacity: int = 1):
        """
        Context manager allowing using Redis backend for task synchronization

        Synopsis:

        redis = Redis(host=..., port=..., db=...)

        # mutual exclusivity (mutex) to perform operation on a foo resource
        @celery.task
        def a_task(foo, bar):
            with Semaphore(redis, 'mutex'+foo, 60):
                # now I have exclusive access to for 60 seconds to 'foo' resource
                do_the_job()
            except MutexTaken:
                # some other task is already using the resource so I skip
                pass

        # optionally restrict to only N concurrent operations on a specific task, regardless of the
        # task capacity (warning, will be blocking tasks waiting on execution)

        def optional_limited_capacity():
            if not Config.MAX_CONCURRENT_RUNNING_TASKS:
                # always allowing entering the resource
                return Semaphore.dummy()
            return Semaphore(redis, 'throttled_resource', 3600, Config.MAX_CONCURRENT_RUNNING_TASKS)

        @celery.task
        def throttled_task(foo, bar):
            while True:
                with optional_limited_capacity():
                    # now I am one of N to do the work
                    do_the_job();
                    break;
                except MutexTaken:
                    time.sleep(1) # not to hog server CPU

        """
        current_value = int(redis_client.get(key_name) or 0)
        if current_value >= capacity:
            raise SemaphoreLocked()
        current_value += 1
        redis_client.set(key_name, value=current_value, ex=ttl)

        try:
            yield

        finally:
            current_value = int(redis_client.get(key_name) or 0)
            current_value -= 1
            if current_value <= 0:
                redis_client.delete(key_name)
            else:
                redis_client.set(key_name, value=current_value, ex=ttl)

    setattr(Semaphore, 'dummy', lambda: nullcontext())

except ModuleNotFoundError:
    pass


T = TypeVar('T')


def ignore_semaphore_locked(
    func: Optional[Callable[..., T]] = None, *, return_value: Optional[T] = None
):
    if not callable(func):
        return partial(ignore_semaphore_locked, return_value=return_value)

    @wraps(func)
    def wrapper(*args, **kwargs):
        with suppress(SemaphoreLocked):
            return func(*args, **kwargs)
        return return_value

    return wrapper
