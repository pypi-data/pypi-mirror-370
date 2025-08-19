import unittest
from typing import *

from argshold.core import ArgumentHolder, FrozenArgumentHolder


class TestArgumentHolder(unittest.TestCase):

    def test_initialization(self: Self) -> None:
        holder = ArgumentHolder(1, 2, a=3, b=4)
        self.assertEqual(holder.args, [1, 2])
        self.assertEqual(holder.kwargs, {"a": 3, "b": 4})

    def test_set_args_and_kwargs(self: Self) -> None:
        holder = ArgumentHolder()
        holder.args = [10, 20]
        holder.kwargs = {"x": 30, "y": 40}
        self.assertEqual(holder.args, [10, 20])
        self.assertEqual(holder.kwargs, {"x": 30, "y": 40})

    def test_equality(self: Self) -> None:
        holder1 = ArgumentHolder(1, 2, a=3, b=4)
        holder2 = ArgumentHolder(1, 2, a=3, b=4)
        holder3 = ArgumentHolder(1, 2, a=5)
        self.assertEqual(holder1, holder2)
        self.assertNotEqual(holder1, holder3)

    def test_len(self: Self) -> None:
        holder = ArgumentHolder(1, 2, a=3, b=4)
        self.assertEqual(len(holder), 4)

    def test_call(self: Self) -> None:
        holder = ArgumentHolder(1, 2, a=3, b=4)

        def sample_function(*args: Any, **kwargs: Any) -> Any:
            return args, kwargs

        result = holder.call(sample_function)
        self.assertEqual(result, ((1, 2), {"a": 3, "b": 4}))

    def test_copy(self: Self) -> None:
        holder = ArgumentHolder(1, 2, a=3, b=4)
        copied = holder.copy()
        self.assertEqual(holder, copied)
        self.assertIsNot(holder, copied)


class TestFrozenArgumentHolder(unittest.TestCase):

    def test_initialization(self: Self) -> None:
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        self.assertEqual(holder.args, (1, 2))
        self.assertEqual(holder.kwargs, {"a": 3, "b": 4})

    def test_equality(self: Self) -> None:
        holder1 = FrozenArgumentHolder(1, 2, a=3, b=4)
        holder2 = FrozenArgumentHolder(1, 2, a=3, b=4)
        holder3 = FrozenArgumentHolder(1, 2, a=5)
        self.assertEqual(holder1, holder2)
        self.assertNotEqual(holder1, holder3)

    def test_len(self: Self) -> None:
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        self.assertEqual(len(holder), 4)

    def test_hash(self: Self) -> None:
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        self.assertIsInstance(hash(holder), int)

    def test_call(self: Self) -> None:
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)

        def sample_function(*args, **kwargs):
            return args, kwargs

        result = holder.call(sample_function)
        self.assertEqual(result, ((1, 2), {"a": 3, "b": 4}))

    def test_frozen_behavior(self: Self) -> None:
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        with self.assertRaises(AttributeError):
            holder.args = [10, 20]
        with self.assertRaises(AttributeError):
            holder.kwargs = {"x": 30, "y": 40}


if __name__ == "__main__":
    unittest.main()
