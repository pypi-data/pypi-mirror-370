import unittest

from dummyfunction.core import dummyfunction


class TestDummyFunction(unittest.TestCase):
    def test_dummyfunction_no_args(self):
        """Test dummyfunction with no arguments."""
        try:
            dummyfunction()
        except Exception as e:
            self.fail(f"dummyfunction() raised an exception: {e}")

    def test_dummyfunction_with_args(self):
        """Test dummyfunction with positional arguments."""
        try:
            dummyfunction(1, 2, 3, "test")
        except Exception as e:
            self.fail(f"dummyfunction(1, 2, 3, 'test') raised an exception: {e}")

    def test_dummyfunction_with_kwargs(self):
        """Test dummyfunction with keyword arguments."""
        try:
            dummyfunction(a=1, b=2, c="test")
        except Exception as e:
            self.fail(f"dummyfunction(a=1, b=2, c='test') raised an exception: {e}")

    def test_dummyfunction_with_args_and_kwargs(self):
        """Test dummyfunction with both positional and keyword arguments."""
        try:
            dummyfunction(1, "string", key1=True, key2=None)
        except Exception as e:
            self.fail(
                f"dummyfunction(1, 'string', key1=True, key2=None) raised an exception: {e}"
            )


if __name__ == "__main__":
    unittest.main()
