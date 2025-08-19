import unittest

from argshold.core import ArgumentHolder, FrozenArgumentHolder


class TestArgumentHolder(unittest.TestCase):
    def test_initialization(self):
        args = (1, 2, 3)
        kwargs = {"a": 10, "b": 20}
        holder = ArgumentHolder(*args, **kwargs)

        self.assertEqual(holder.args, list(args))
        self.assertEqual(holder.kwargs, kwargs)

    def test_equality(self):
        holder1 = ArgumentHolder(1, 2, a=3, b=4)
        holder2 = ArgumentHolder(1, 2, a=3, b=4)
        holder3 = ArgumentHolder(1, 2, a=3)

        self.assertEqual(holder1, holder2)
        self.assertNotEqual(holder1, holder3)

    def test_argument_modification(self):
        holder = ArgumentHolder(1, 2, 3, a=10, b=20)

        holder.args = [4, 5, 6]
        holder.kwargs = {"x": 30, "y": 40}

        self.assertEqual(holder.args, [4, 5, 6])
        self.assertEqual(holder.kwargs, {"x": 30, "y": 40})

    def test_len(self):
        holder = ArgumentHolder(1, 2, 3, a=10, b=20)
        self.assertEqual(len(holder), 5)

    def test_call(self):
        holder = ArgumentHolder(1, 2, a=3, b=4)
        result = holder.call(lambda x, y, a, b: x + y + a + b)
        self.assertEqual(result, 10)

    def test_copy(self):
        holder = ArgumentHolder(1, 2, a=3, b=4)
        copied_holder = holder.copy()

        self.assertEqual(copied_holder.args, holder.args)
        self.assertEqual(copied_holder.kwargs, holder.kwargs)
        self.assertIsNot(copied_holder, holder)

    def test_conversion(self):
        holder = ArgumentHolder(1, 2, a=3, b=4)
        frozen_holder = holder.toFrozenArgumentHolder()

        self.assertIsInstance(frozen_holder, FrozenArgumentHolder)
        self.assertEqual(frozen_holder.args, tuple(holder.args))
        self.assertEqual(frozen_holder.kwargs, holder.kwargs)


class TestFrozenArgumentHolder(unittest.TestCase):
    def test_initialization(self):
        args = (1, 2, 3)
        kwargs = {"a": 10, "b": 20}
        holder = FrozenArgumentHolder(*args, **kwargs)

        self.assertEqual(holder.args, args)
        self.assertEqual(holder.kwargs, kwargs)

    def test_equality(self):
        holder1 = FrozenArgumentHolder(1, 2, a=3, b=4)
        holder2 = FrozenArgumentHolder(1, 2, a=3, b=4)
        holder3 = FrozenArgumentHolder(1, 2, a=3)

        self.assertEqual(holder1, holder2)
        self.assertNotEqual(holder1, holder3)

    def test_len(self):
        holder = FrozenArgumentHolder(1, 2, 3, a=10, b=20)
        self.assertEqual(len(holder), 5)

    def test_call(self):
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        result = holder.call(lambda x, y, a, b: x + y + a + b)
        self.assertEqual(result, 10)

    def test_hash(self):
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        hash_value = hash(holder)

        self.assertIsInstance(hash_value, int)

    def test_conversion(self):
        holder = FrozenArgumentHolder(1, 2, a=3, b=4)
        normal_holder = holder.toArgumentHolder()

        self.assertIsInstance(normal_holder, ArgumentHolder)
        self.assertEqual(normal_holder.args, list(holder.args))
        self.assertEqual(normal_holder.kwargs, dict(holder.kwargs))


if __name__ == "__main__":
    unittest.main()
