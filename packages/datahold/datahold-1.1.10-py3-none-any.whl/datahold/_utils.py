import functools
from types import FunctionType
from typing import *

__all__ = [
    "holdDecorator",
]


class holdDecorator:
    _funcnames: tuple[str]

    def __call__(self: Self, cls: type) -> type:
        datacls: type = cls.__annotations__["data"]
        name: str
        new: FunctionType
        old: FunctionType
        for name in self._funcnames:
            old = getattr(datacls, name)
            new = self.getHoldFunc(old)
            new.__doc__ = old.__doc__
            new.__module__ = cls.__module__
            new.__name__ = name
            new.__qualname__ = cls.__qualname__ + "." + name
            setattr(cls, name, new)
        return cls

    def __init__(self: Self, *funcnames: str) -> None:
        self._funcnames = funcnames

    @classmethod
    def getHoldFunc(cls: type, old: FunctionType) -> Any:
        @functools.wraps(old)
        def new(self: Self, *args: Any, **kwargs: Any) -> Any:
            data: Any = self.data
            ans: Any = old(data, *args, **kwargs)
            self.data = data
            return ans

        return new
