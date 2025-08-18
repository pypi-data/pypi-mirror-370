import math
import sys
import unittest
from unittest.mock import patch

from click.testing import CliRunner

# Import the script's components
from expit.core import function, main


class TestFunction(unittest.TestCase):
    def test_function_regular_values(self):
        # Test regular values of x
        self.assertAlmostEqual(function(0), 0.5)
        self.assertAlmostEqual(function(1), 1 / (1 + math.exp(-1)), places=5)
        self.assertAlmostEqual(function(-1), 1 / (1 + math.exp(1)), places=5)

    def test_function_large_positive(self):
        # Test large positive values of x (result should approach 1)
        self.assertAlmostEqual(function(100), 1.0, places=5)
        self.assertAlmostEqual(function(1000), 1.0, places=5)

    def test_function_large_negative(self):
        # Test large negative values of x (result should approach 0)
        self.assertAlmostEqual(function(-100), 0.0, places=5)
        self.assertAlmostEqual(function(-1000), 0.0, places=5)

    def test_function_overflow(self):
        # Test overflow values to ensure they are handled without errors
        self.assertAlmostEqual(function(sys.float_info.max), 1.0, places=5)
        self.assertAlmostEqual(function(-sys.float_info.max), 0.0, places=5)

    def test_function_infinity(self):
        # Test positive and negative infinity inputs
        self.assertEqual(function(float("inf")), 1.0)
        self.assertEqual(function(float("-inf")), 0.0)

    def test_function_nan(self):
        # Test NaN input; behavior may vary, but we can ensure it doesn't throw an error
        result = function(float("nan"))
        self.assertTrue(
            math.isnan(result) or result in [0.0, 1.0]
        )  # Depending on interpretation, could be NaN, 0, or 1


class TestMainCommand(unittest.TestCase):
    def setUp(self):
        # Set up CliRunner for Click command-line testing
        self.runner = CliRunner()

    def test_main_help_option(self):
        # Test help option (-h, --help) to ensure it displays usage information
        result = self.runner.invoke(main, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage", result.output)
        self.assertIn("applies the expit function to x", result.output)

        result = self.runner.invoke(main, ["-h"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Usage", result.output)
        self.assertIn("applies the expit function to x", result.output)

    def test_main_version_option(self):
        # Test version option (-V, --version) to check version output
        result = self.runner.invoke(main, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.output.lower())

        result = self.runner.invoke(main, ["-V"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.output.lower())

    def test_main_valid_input(self):
        # Test main function with a valid float input, checking output
        result = self.runner.invoke(main, ["1"])
        expected_output = f"{function(1)}\n"
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)

        result = self.runner.invoke(main, ["--", "-1"])
        expected_output = f"{function(-1)}\n"
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)

    def test_main_edge_case(self):
        # Test main function with extreme float inputs
        result = self.runner.invoke(main, [str(sys.float_info.max)])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{function(sys.float_info.max)}\n")

        result = self.runner.invoke(main, ["--", str(-sys.float_info.max)])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{function(-sys.float_info.max)}\n")

    def test_main_invalid_input(self):
        # Test main function with invalid input, expecting an error
        result = self.runner.invoke(main, ["abc"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Invalid value for 'X'", result.output)


if __name__ == "__main__":
    unittest.main()
