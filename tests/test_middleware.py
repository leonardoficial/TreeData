
import unittest

from unittest.mock import MagicMock, patch

from treedata.controller.Middleware import Middleware


class CustomTestResult(unittest.TextTestResult):

    def addSuccess(self, test):
        super().addSuccess(test)
        print(f" ✅ . {test._testMethodName}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f" ❌ . {test._testMethodName}")

    def addError(self, test, err):
        super().addError(test, err)
        print(f" ERROR . {test._testMethodName}")


class CustomTestRunner(unittest.TextTestRunner):
    resultclass = CustomTestResult


class TestMiddlewareInitialization(unittest.TestCase):
    """Test cases for Middleware class initialization."""


    def test_initializes_empty_settings_when_none_is_passed(self):
        """Test that settings is set to an empty dictionary when None is passed."""

        middleware = Middleware(settings=None)
        
        self.assertEqual(middleware.settings, {})


    def test_raises_type_error_when_settings_is_not_a_dictionary(self):
        """Test that a TypeError is raised when settings is not a dictionary."""

        with self.assertRaises(TypeError):

            Middleware(settings="not a dict")


    def test_initializes_with_valid_settings(self):
        """Test that settings is set correctly when a valid dictionary is passed."""

        valid_settings = {"key": "value"}

        middleware = Middleware(settings=valid_settings)
        
        self.assertEqual(middleware.settings, valid_settings)


    def test_initializes_with_existing_path(self):
        """Test that the middleware path exists."""

        middleware = Middleware()

        self.assertTrue(middleware.path.exists())




if __name__ == '__main__':

    print("")

    unittest.main(testRunner=CustomTestRunner(), verbosity=2)