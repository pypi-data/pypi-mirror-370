from typing import Callable, Generator, Iterable, TypeVar, cast


_T = TypeVar("_T")


def filter_not_none(iterable: Iterable[_T | None]) -> Iterable[_T]:
    return cast(Iterable[_T], filter(lambda item: item is not None, iterable))


def split_before(iterable: Iterable[_T], pred: Callable[[list[_T]], bool]) -> "Generator[list[_T]]":
    """
    Yields lists of items from `iterable`, where each list ends just before an
    item that would cause `pred` on the list to return `True`.

    >>> list(split_before([9, 4, 1, 2, 4, 5, 4, 6, 7, 7], lambda l: sum(l) > 10))
    [[9], [4, 1, 2], [4, 5], [4, 6], [7], [7]]
    """
    sub = []

    for item in iterable:
        if not sub or not pred(sub + [item]):
            sub.append(item)
        else:
            yield sub
            sub = [item]

    if sub:
        yield sub


def split_by(iterable: Iterable[_T], pred: Callable[[_T], bool]) -> "Generator[tuple[_T | None, list[_T]]]":
    header: _T | None = None
    subrows: list[_T] = []

    for item in iterable:
        if pred(item):
            if header or subrows:
                yield header, subrows
            header = item
            subrows = []
        else:
            subrows.append(item)

    if header or subrows:
        yield header, subrows
