import unittest
from typing import Callable

from argshold.core import ArgumentHolder, FrozenArgumentHolder


class TestMatMulOperations(unittest.TestCase):

    def test_matmul_argument_holder(self):
        # Define a simple transformation function to test with matmul
        def multiply_by_two(x):
            return x * 2

        # Create an ArgumentHolder instance with some arguments
        arg_holder = ArgumentHolder(1, 2, 3, a=4, b=5)

        # Perform @matmul operation with the function `multiply_by_two`
        result = arg_holder @ multiply_by_two

        # Check if the positional arguments are transformed correctly
        self.assertEqual(result.args, [2, 4, 6])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(result.kwargs, {"a": 8, "b": 10})

    def test_matmul_frozen_argument_holder(self):
        # Define a simple transformation function to test with matmul
        def square(x):
            return x * x

        # Create a FrozenArgumentHolder instance with some arguments
        frozen_arg_holder = FrozenArgumentHolder(2, 3, 4, x=5, y=6)

        # Perform @matmul operation with the function `square`
        result = frozen_arg_holder @ square

        # Check if the positional arguments are transformed correctly
        self.assertEqual(list(result.args), [4, 9, 16])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(dict(result.kwargs), {"x": 25, "y": 36})

    def test_rmatmul_argument_holder(self):
        # Define a simple transformation function to test with rmatmul
        def add_five(x):
            return x + 5

        # Create an ArgumentHolder instance with some arguments
        arg_holder = ArgumentHolder(1, 2, 3, a=4, b=5)

        # Perform @matmul operation with the function `add_five`
        result = add_five @ arg_holder

        # Check if the positional arguments are transformed correctly
        self.assertEqual(result.args, [6, 7, 8])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(result.kwargs, {"a": 9, "b": 10})

    def test_rmatmul_frozen_argument_holder(self):
        # Define a simple transformation function to test with rmatmul
        def subtract_three(x):
            return x - 3

        # Create a FrozenArgumentHolder instance with some arguments
        frozen_arg_holder = FrozenArgumentHolder(10, 20, 30, x=40, y=50)

        # Perform @matmul operation with the function `subtract_three`
        result = subtract_three @ frozen_arg_holder

        # Check if the positional arguments are transformed correctly
        self.assertEqual(list(result.args), [7, 17, 27])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(dict(result.kwargs), {"x": 37, "y": 47})

    def test_imatmul_argument_holder(self):
        # Define a simple transformation function to test with imatmul
        def multiply_by_three(x):
            return x * 3

        # Create an ArgumentHolder instance with some arguments
        arg_holder = ArgumentHolder(1, 2, 3, a=4, b=5)

        # Perform @= operation with the function `multiply_by_three`
        arg_holder @= multiply_by_three

        # Check if the positional arguments are transformed correctly
        self.assertEqual(arg_holder.args, [3, 6, 9])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(arg_holder.kwargs, {"a": 12, "b": 15})

    def test_imatmul_frozen_argument_holder(self):
        # Define a simple transformation function to test with imatmul
        def add_ten(x):
            return x + 10

        # Create a FrozenArgumentHolder instance with some arguments
        frozen_arg_holder = FrozenArgumentHolder(1, 2, 3, x=4, y=5)

        # Perform @= operation with the function `add_ten`
        frozen_arg_holder @= add_ten

        # Check if the positional arguments are transformed correctly
        self.assertEqual(list(frozen_arg_holder.args), [11, 12, 13])

        # Check if the keyword arguments are transformed correctly
        self.assertEqual(dict(frozen_arg_holder.kwargs), {"x": 14, "y": 15})


if __name__ == "__main__":
    unittest.main()
