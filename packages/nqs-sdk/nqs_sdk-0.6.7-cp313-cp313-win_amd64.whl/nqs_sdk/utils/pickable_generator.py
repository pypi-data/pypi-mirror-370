from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterator, Tuple, TypeVar


T = TypeVar("T")


class PickableGenerator(ABC, Iterator, Generic[T]):
    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        pass

    @abstractmethod
    def __next__(self) -> T:
        pass


class NoneGenerator(PickableGenerator):
    def __init__(self) -> None:
        pass

    def __iter__(self) -> Iterator[None]:
        return self

    def __next__(self) -> None:
        return None


class StatefulGenerator(PickableGenerator[T]):
    def __init__(self, state: Any, update: Callable[[Any], Tuple[Any, T]]) -> None:
        self._state = state
        self._update = update
        self._running = True

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        # once stopped StatefulGenerator manages next calls to raise StopIterator by itself
        if self._running:
            try:
                # _update can raise StopIteration if necessary
                self._state, current = self._update(self._state)
                return current
            except StopIteration:
                self._running = False
                raise
        else:
            raise StopIteration
