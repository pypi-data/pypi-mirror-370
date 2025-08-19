import functools
from abc import ABC, abstractmethod
from collections import abc
from typing import *

from datarepr import datarepr
from scaevola import Scaevola
from unhash import unhash

from datahold import _utils

__all__ = [
    "HoldABC",
    "HoldDict",
    "HoldList",
    "HoldSet",
    "OkayABC",
    "OkayDict",
    "OkayList",
    "OkaySet",
]


class HoldABC(ABC):

    __slots__ = ("_data",)

    __hash__ = unhash

    @abstractmethod
    def __init__(self: Self, *args: Any, **kwargs: Any) -> None: ...

    @classmethod
    def __subclasshook__(cls: type, other: type, /) -> bool:
        "This magic classmethod can be overwritten for a custom subclass check."
        return NotImplemented

    @property
    @abstractmethod
    def data(self): ...


@_utils.holdDecorator(
    "__contains__",
    "__delitem__",
    "__eq__",
    "__format__",
    "__ge__",
    "__getitem__",
    "__gt__",
    "__ior__",
    "__iter__",
    "__le__",
    "__len__",
    "__lt__",
    "__or__",
    "__repr__",
    "__reversed__",
    "__ror__",
    "__setitem__",
    "__str__",
    "clear",
    "copy",
    "get",
    "items",
    "keys",
    "pop",
    "popitem",
    "setdefault",
    "update",
    "values",
)
class HoldDict(HoldABC, abc.MutableMapping):
    data: dict


@_utils.holdDecorator(
    "__add__",
    "__contains__",
    "__delitem__",
    "__eq__",
    "__format__",
    "__ge__",
    "__getitem__",
    "__gt__",
    "__iadd__",
    "__imul__",
    "__iter__",
    "__le__",
    "__len__",
    "__lt__",
    "__mul__",
    "__repr__",
    "__reversed__",
    "__rmul__",
    "__setitem__",
    "__str__",
    "append",
    "clear",
    "copy",
    "count",
    "extend",
    "index",
    "insert",
    "pop",
    "remove",
    "reverse",
    "sort",
)
class HoldList(HoldABC, abc.MutableSequence):
    data: list


@_utils.holdDecorator(
    "__and__",
    "__contains__",
    "__eq__",
    "__format__",
    "__ge__",
    "__gt__",
    "__iand__",
    "__ior__",
    "__isub__",
    "__iter__",
    "__ixor__",
    "__le__",
    "__len__",
    "__lt__",
    "__or__",
    "__rand__",
    "__repr__",
    "__ror__",
    "__rsub__",
    "__rxor__",
    "__str__",
    "__sub__",
    "__xor__",
    "add",
    "clear",
    "copy",
    "difference",
    "difference_update",
    "discard",
    "intersection",
    "intersection_update",
    "isdisjoint",
    "issubset",
    "issuperset",
    "pop",
    "remove",
    "symmetric_difference",
    "symmetric_difference_update",
    "union",
    "update",
)
class HoldSet(HoldABC, abc.MutableSet):
    data: set


class OkayABC(Scaevola, HoldABC):

    def __bool__(self: Self, /) -> bool:
        "This magic method implements bool(self)."
        return bool(self._data)

    def __contains__(self: Self, value: Any, /) -> bool:
        "This magic method implements value in self."
        return value in self._data

    def __eq__(self: Self, other: Any, /) -> bool:
        "This magic method implements self==other."
        if type(self) is type(other):
            return self._data == other._data
        try:
            other = type(self)(other)
        except:
            return False
        return self._data == other._data

    def __format__(self: Self, format_spec: Any = "", /) -> str:
        "This magic method implements format(self, format_spec)."
        return format(str(self), str(format_spec))

    def __getitem__(self: Self, key: Any, /) -> Any:
        "This magic method implements self[key]."
        return self._data[key]

    def __gt__(self: Self, other: Any, /) -> bool:
        "This magic method implements self>=other."
        return not (self == other) and (self >= other)

    def __iter__(self: Self, /) -> Iterator:
        "This magic method implements iter(self)."
        return iter(self._data)

    def __le__(self: Self, other: Any, /) -> bool:
        "This magic method implements self<=other."
        return self._data <= type(self._data)(other)

    def __len__(self: Self, /) -> int:
        "This magic method implements len(self)."
        return len(self._data)

    def __lt__(self: Self, other: Any, /) -> bool:
        "This magic method implements self<other."
        return not (self == other) and (self <= other)

    def __ne__(self: Self, other: Any, /) -> bool:
        "This magic method implements self!=other."
        return not (self == other)

    def __repr__(self: Self, /) -> str:
        "This magic method implements repr(self)."
        return datarepr(type(self).__name__, self._data)

    def __reversed__(self: Self, /) -> Self:
        "This magic method implements reversed(self)."
        return type(self)(reversed(self.data))

    def __sorted__(self: Self, /, **kwargs: Any) -> Self:
        "This magic method implements sorted(self, **kwargs)."
        ans = type(self)(self.data)
        ans.sort(**kwargs)
        return ans

    def __str__(self: Self, /) -> str:
        "This magic method implements str(self)."
        return repr(self)

    def copy(self: Self, /) -> Self:
        "This method creates a new holder with equivalent data."
        return type(self)(self.data)


class OkayDict(OkayABC, HoldDict):

    def __init__(self: Self, data: Any = (), /, **kwargs) -> None:
        "This magic method initializes self."
        self.data = dict(data, **kwargs)

    def __or__(self: Self, other: Any, /) -> Self:
        "This magic method implements self|other."
        return type(self)(self._data | dict(other))

    @property
    def data(self: Self, /) -> dict:
        "This property represents the data."
        return dict(self._data)

    @data.setter
    def data(self: Self, values: Any, /) -> None:
        self._data = dict(values)

    @data.deleter
    def data(self: Self, /) -> None:
        self._data = dict()

    @classmethod
    def fromkeys(cls: type, iterable: Iterable, value: Any = None, /) -> Self:
        "This classmethod creates a new instance with keys from iterable and values set to value."
        return cls(dict.fromkeys(iterable, value))

    def get(self: Self, /, *args: Any) -> Any:
        "This method returns self[key] if key is in the dictionary, and default otherwise."
        return self._data.get(*args)

    def items(self: Self, /) -> abc.ItemsView:
        "This method returns a view of the items of the current instance."
        return self._data.items()

    def keys(self: Self, /) -> abc.KeysView:
        "This method returns a view of the keys of the current instance."
        return self._data.keys()

    def values(self: Self, /) -> abc.ValuesView:
        "This method returns a view of the values of the current instance."
        return self._data.values()


class OkayList(OkayABC, HoldList):

    def __add__(self: Self, other: Any, /) -> Self:
        "This magic method implements self+other."
        return type(self)(self._data + list(other))

    def __init__(self: Self, data: Iterable = ()) -> None:
        "This magic method initializes self."
        self.data = data

    def __mul__(self: Self, value: SupportsIndex, /) -> Self:
        "This magic method implements self*other."
        return type(self)(self.data * value)

    def __rmul__(self: Self, value: SupportsIndex, /) -> Self:
        "This magic method implements other*self."
        return self * value

    def count(self: Self, value: Any, /) -> int:
        "This method returns the number of occurences of value."
        return self._data.count(value)

    @property
    def data(self: Self, /) -> list:
        "This property represents the data."
        return list(self._data)

    @data.setter
    def data(self: Self, values: Iterable, /) -> None:
        self._data = list(values)

    @data.deleter
    def data(self: Self, /) -> None:
        self._data = list()

    def index(self: Self, /, *args: Any) -> int:
        "This method returns the index of the first occurence of value, or raises a ValueError if value is not present."
        return self._data.index(*args)


class OkaySet(OkayABC, HoldSet):

    def __and__(self: Self, other: Any, /) -> Self:
        "This magic method implements self&other."
        return type(self)(self._data & set(other))

    def __init__(self: Self, data: Iterable = ()) -> None:
        "This magic method initializes self."
        self.data = data

    def __or__(self: Self, other: Any, /) -> Self:
        "This magic method implements self|other."
        return type(self)(self._data | set(other))

    def __sub__(self: Self, other: Any, /) -> Self:
        "This magic method implements self-other."
        return type(self)(self._data - set(other))

    def __xor__(self: Self, other: Any, /) -> Self:
        "This magic method implements self^other."
        return type(self)(self._data ^ set(other))

    @property
    def data(self: Self, /) -> set:
        "This property represents the data."
        return set(self._data)

    @data.setter
    def data(self: Self, values: Iterable) -> None:
        self._data = set(values)

    @data.deleter
    def data(self: Self, /) -> None:
        self._data = set()

    def difference(self: Self, /, *others: Any) -> Self:
        "This method returns a copy of self without the items also found in any of the others."
        return type(self)(self._data.difference(*others))

    def intersection(self: Self, /, *others: Any) -> set:
        "This method returns a copy of self without the items not found in all of the others."
        return type(self)(self._data.intersection(*others))

    def isdisjoint(self: Self, other: Any, /) -> bool:
        "This method determines if self and other have no intersection."
        return self._data.isdisjoint(other)

    def issubset(self: Self, other: Any, /) -> bool:
        "This method determines if self is a subset of other."
        return self._data.issubset(other)

    def issuperset(self: Self, other: Any, /) -> bool:
        "This method determines if self is a superset of other."
        return self._data.issuperset(other)

    def symmetric_difference(self: Self, other: Any, /) -> Self:
        "This method returns the symmetric difference between self and other."
        return type(self)(self._data.symmetric_difference(other))

    def union(self: Self, /, *others: Any) -> Self:
        "This method returns a copy of self with all the items in the others added."
        return type(self)(self._data.union(*others))
