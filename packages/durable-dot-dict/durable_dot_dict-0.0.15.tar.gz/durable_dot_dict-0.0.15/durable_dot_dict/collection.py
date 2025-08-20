from typing import Any, Callable, List, Iterable, Type, Optional, Union
from typing import Generator, Iterator, TypeVar
from durable_dot_dict.dotdict import DotDict

T = TypeVar("T", bound=DotDict)


def first(*args: Callable[[], Any]) -> Any:
    for func in args:
        try:
            return func()
        except Exception:
            continue
    raise ValueError("All provided callables failed.")


def first_not_none(*args: Callable[[], Any]) -> Any:
    for func in args:
        try:
            result = func()
            if result is None:
                continue
            return result
        except Exception:
            continue
    raise ValueError("All provided callables failed.")


class DotDictStream:
    def __init__(self, collection: Iterable[T]):
        self.collection = collection

    def __iter__(self):
        yield from self.collection

    def __rshift__(self, other) -> 'DotDictStream':
        return DotDictStream(item >> other for item in self.collection)

    def __lshift__(self, other) -> 'DotDictStream':
        return DotDictStream(item << other for item in self.collection)

    def list(self, cast_to: Optional[Type[T]] = None) -> List[T]:
        if cast_to is None:
            return list(self.collection)
        return [item.cast_to(cast_to) for item in self.collection]

    def first(self, cast_to: Optional[Type[T]] = None) -> Optional[Union[T, DotDict]]:
        try:
            item = next(self.collection)

            if cast_to is None:
                return item
            return item.cast_to(cast_to)
        except StopIteration:
            return None

    def remap(self, mapping) -> Generator[DotDict, None, None]:
        for item in self.collection:
            yield item >> mapping
