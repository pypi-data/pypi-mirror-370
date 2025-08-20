import datetime
from typing import Any, Callable, Generator, Iterable, TypeVar

T = TypeVar("T")


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def distinct(
    iterable: Iterable[T],
    key: Callable[[T], Any] = (lambda i: i),
) -> Generator[T, None, None]:
    seen: set = set()
    for item in iterable:
        if key(item) in seen:
            continue
        seen.add(key(item))
        yield item
