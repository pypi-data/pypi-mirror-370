import unittest

from frozendict import frozendict

from argshold.core import ArgumentHolder, FrozenArgumentHolder


class TestArgumentHolder(unittest.TestCase):
    def setUp(self):
        self.args = [1, 2, 3]
        self.kwargs = {"a": 10, "b": 20}
        self.holder = ArgumentHolder(*self.args, **self.kwargs)

    def test_initialization(self):
        self.assertEqual(self.holder.args, self.args)
        self.assertEqual(self.holder.kwargs, self.kwargs)

    def test_set_args(self):
        new_args = [4, 5, 6]
        self.holder.args = new_args
        self.assertEqual(self.holder.args, new_args)

    def test_set_kwargs(self):
        new_kwargs = {"x": 30, "y": 40}
        self.holder.kwargs = new_kwargs
        self.assertEqual(self.holder.kwargs, new_kwargs)

    def test_delete_args(self):
        del self.holder.args
        self.assertEqual(self.holder.args, [])

    def test_delete_kwargs(self):
        del self.holder.kwargs
        self.assertEqual(self.holder.kwargs, {})

    def test_copy(self):
        copy_holder = self.holder.copy()
        self.assertIsInstance(copy_holder, ArgumentHolder)
        self.assertEqual(copy_holder.args, self.args)
        self.assertEqual(copy_holder.kwargs, self.kwargs)

    def test_len(self):
        self.assertEqual(len(self.holder), len(self.args) + len(self.kwargs))


class TestFrozenArgumentHolder(unittest.TestCase):
    def setUp(self):
        self.args = (1, 2, 3)
        self.kwargs = frozendict({"a": 10, "b": 20})
        self.holder = FrozenArgumentHolder(*self.args, **self.kwargs)

    def test_initialization(self):
        self.assertEqual(self.holder.args, self.args)
        self.assertEqual(self.holder.kwargs, self.kwargs)

    def test_immutable_args(self):
        with self.assertRaises(AttributeError):
            self.holder.args = [4, 5, 6]

    def test_immutable_kwargs(self):
        with self.assertRaises(AttributeError):
            self.holder.kwargs = {"x": 30, "y": 40}

    def test_hash(self):
        self.assertEqual(hash(self.holder), hash((self.args, self.kwargs)))

    def test_copy(self):
        copy_holder = self.holder.copy()
        self.assertIsInstance(copy_holder, FrozenArgumentHolder)
        self.assertEqual(copy_holder.args, self.args)
        self.assertEqual(copy_holder.kwargs, self.kwargs)

    def test_len(self):
        self.assertEqual(len(self.holder), len(self.args) + len(self.kwargs))


if __name__ == "__main__":
    unittest.main()
