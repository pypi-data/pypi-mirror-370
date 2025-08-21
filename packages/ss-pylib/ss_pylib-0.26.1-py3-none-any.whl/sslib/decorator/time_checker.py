import time
from typing import Callable
from datetime import timedelta


def time_checker(title: str, notifier: Callable[[str], bool | None] | None = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if notifier is None:
                print(f'{title} 시작')
            else:
                notifier(f'{title} 시작')
            start = time.time()
            result = func(*args, **kwargs)
            delta_seconds = time.time() - start
            end = timedelta(seconds=delta_seconds)
            if notifier is None:
                print(f'{title} 종료({end})')
            else:
                notifier(f'{title} 종료({end})')
            return result

        return wrapper

    return decorator


def async_time_checker(title: str, notifier: Callable[[str], bool | None] | None = None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if notifier is None:
                print(f'{title} 시작')
            else:
                notifier(f'{title} 시작')
            start = time.time()
            result = await func(*args, **kwargs)
            delta_seconds = time.time() - start
            end = timedelta(seconds=delta_seconds)
            if notifier is None:
                print(f'{title} 종료({end})')
            else:
                notifier(f'{title} 종료({end})')
            return result

        return wrapper

    return decorator
