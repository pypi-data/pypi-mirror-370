import unittest
from types import FunctionType
from typing import *

from datahold import core
from datahold.core import *


class TestOkayDict(unittest.TestCase):

    def setUp(self: Self) -> None:
        self.okay_dict = OkayDict({"a": 1, "b": 2})

    def test_contains(self: Self) -> None:
        self.assertIn("a", self.okay_dict)
        self.assertNotIn("c", self.okay_dict)

    def test_getitem(self: Self) -> None:
        self.assertEqual(self.okay_dict["a"], 1)
        with self.assertRaises(KeyError):
            self.okay_dict["c"]

    def test_setitem(self: Self) -> None:
        self.okay_dict["c"] = 3
        self.assertEqual(self.okay_dict["c"], 3)

    def test_delitem(self: Self) -> None:
        del self.okay_dict["a"]
        self.assertNotIn("a", self.okay_dict)

    def test_len(self: Self) -> None:
        self.assertEqual(len(self.okay_dict), 2)

    def test_or(self: Self) -> None:
        merged = self.okay_dict | {"c": 3}
        self.assertEqual(merged, OkayDict({"a": 1, "b": 2, "c": 3}))


class TestOkayList(unittest.TestCase):

    def setUp(self: Self) -> None:
        self.okay_list = OkayList([1, 2, 3])

    def test_contains(self: Self) -> None:
        self.assertIn(2, self.okay_list)
        self.assertNotIn(5, self.okay_list)

    def test_getitem(self: Self) -> None:
        self.assertEqual(self.okay_list[0], 1)

    def test_setitem(self: Self) -> None:
        self.okay_list[0] = 5
        self.assertEqual(self.okay_list[0], 5)

    def test_append(self: Self) -> None:
        self.okay_list.append(4)
        self.assertEqual(self.okay_list[-1], 4)

    def test_len(self: Self) -> None:
        self.assertEqual(len(self.okay_list), 3)


class TestOkaySet(unittest.TestCase):

    def setUp(self: Self) -> None:
        self.okay_set = OkaySet({1, 2, 3})

    def test_contains(self: Self) -> None:
        self.assertIn(1, self.okay_set)
        self.assertNotIn(4, self.okay_set)

    def test_add(self: Self) -> None:
        self.okay_set.add(4)
        self.assertIn(4, self.okay_set)

    def test_remove(self: Self) -> None:
        self.okay_set.remove(2)
        self.assertNotIn(2, self.okay_set)

    def test_len(self: Self) -> None:
        self.assertEqual(len(self.okay_set), 3)

    def test_union(self: Self) -> None:
        result = self.okay_set | {4, 5}
        self.assertEqual(result, OkaySet({1, 2, 3, 4, 5}))


class TestDoc(unittest.TestCase):
    def test_doc(self: Self) -> None:
        for x in core.__all__:
            y = getattr(core, x)
            for a in dir(y):
                b = getattr(y, a)
                if not callable(b) and not isinstance(b, property):
                    continue
                if getattr(b, "__isabstractmethod__", False):
                    continue
                doc = getattr(b, "__doc__", None)
                error = "%r inside %r has no docstring" % (a, x)
                self.assertNotEqual(doc, None, error)


if __name__ == "__main__":
    unittest.main()
