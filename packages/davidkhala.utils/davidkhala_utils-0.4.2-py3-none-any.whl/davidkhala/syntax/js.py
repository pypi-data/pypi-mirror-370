from functools import reduce
from typing import Callable, TypeVar, Generic

ValueType = TypeVar('ValueType')


class Array(list, Generic[ValueType]):
    def map(self, func: Callable):
        return Array(map(func, self))

    def reduce(self, func: Callable, initial=None):
        if initial is None:
            return reduce(func, self)
        return reduce(func, self, initial)

    def filter(self, func: Callable):
        return Array(filter(func, self))

    def forEach(self, func: Callable[[ValueType, int, "Array"], None]):
        for index, value in enumerate(self):
            func(value, index, self)

    def minus(self, array):
        return [x for x in self if x not in array]
