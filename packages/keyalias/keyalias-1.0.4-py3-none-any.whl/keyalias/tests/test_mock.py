import unittest
from typing import *

from keyalias.core import classdecorator, getdecorator, getproperty


class TestDecorators(unittest.TestCase):

    def setUp(self: Self) -> None:
        # Create a mock class to test the decorators
        class MockClass(dict):
            pass

        self.MockClass = MockClass

    def test_getproperty(self: Self) -> None:
        "Test the functionality of getproperty function."
        prop_key = "test_key"
        mock_instance = self.MockClass()
        mock_instance[prop_key] = "test_value"

        # Create a property for 'test_key'
        test_property = getproperty(prop_key)

        # Bind the property manually to the instance
        type(mock_instance).test_key = test_property

        # Test getter
        self.assertEqual(mock_instance.test_key, "test_value")

        # Test setter
        mock_instance.test_key = "new_value"
        self.assertEqual(mock_instance["test_key"], "new_value")

        # Test deleter
        del mock_instance.test_key
        self.assertNotIn(prop_key, mock_instance)

    def test_classdecorator_with_single_alias(self: Self) -> None:
        "Test classdecorator with a single alias."
        mock_instance = self.MockClass()

        # Apply the classdecorator with a single alias
        class MyClass(self.MockClass):
            pass

        MyClass = classdecorator(MyClass, alias1="key1")

        instance = MyClass()
        instance["key1"] = "value1"

        # Test that alias1 points to key1
        self.assertEqual(instance.alias1, "value1")

        instance.alias1 = "new_value"
        self.assertEqual(instance["key1"], "new_value")

    def test_classdecorator_with_multiple_aliases(self: Self) -> None:
        "Test classdecorator with multiple aliases."
        mock_instance = self.MockClass()

        # Apply the classdecorator with multiple aliases
        class MyClass(self.MockClass):
            pass

        MyClass = classdecorator(MyClass, alias1="key1", alias2="key2")

        instance = MyClass()
        instance["key1"] = "value1"
        instance["key2"] = "value2"

        # Test alias1 and alias2
        self.assertEqual(instance.alias1, "value1")
        self.assertEqual(instance.alias2, "value2")

        # Test updating values
        instance.alias1 = "new_value1"
        instance.alias2 = "new_value2"
        self.assertEqual(instance["key1"], "new_value1")
        self.assertEqual(instance["key2"], "new_value2")

    def test_getdecorator(self: Self) -> None:
        "Test getdecorator function which is a partial of classdecorator."

        @getdecorator(alias1="key1")
        class MyClass(self.MockClass):
            pass

        instance = MyClass()
        instance["key1"] = "value1"

        # Test that alias1 points to key1
        self.assertEqual(instance.alias1, "value1")

        # Test setting through alias
        instance.alias1 = "new_value"
        self.assertEqual(instance["key1"], "new_value")

    def test_getdecorator(self: Self) -> None:
        @getdecorator(alias1="key1")
        class MyClass(self.MockClass):
            pass

        instance = MyClass()
        instance["key1"] = "value1"

        # Test that alias1 points to key1
        self.assertEqual(instance.alias1, "value1")

        # Test setting through alias
        instance.alias1 = "new_value"
        self.assertEqual(instance["key1"], "new_value")

    def test_invalid_property_access(self: Self) -> None:
        "Test handling of invalid property access through a missing key."
        prop_key = "missing_key"
        mock_instance = self.MockClass()

        # Create a property for 'missing_key'
        test_property = getproperty(prop_key)

        # Bind the property manually to the instance
        type(mock_instance).missing_key = test_property

        # Test getter should raise KeyError since key is missing
        with self.assertRaises(KeyError):
            _ = mock_instance.missing_key

        # Test setting the value
        mock_instance.missing_key = "new_value"
        self.assertEqual(mock_instance[prop_key], "new_value")

        # Test deleting the value
        del mock_instance.missing_key
        self.assertNotIn(prop_key, mock_instance)

    def test_decorator_preserves_class_attributes(self: Self) -> None:
        "Test that classdecorator does not remove original class attributes."

        class MyClass:
            original_attr = "original"

        # Apply the decorator
        class MyDecoratedClass(MyClass):
            pass

        MyDecoratedClass = classdecorator(MyDecoratedClass, alias1="key1")

        instance = MyDecoratedClass()
        self.assertEqual(instance.original_attr, "original")

    def test_partial_application_of_getdecorator(self: Self) -> None:
        "Test that functools.partial works correctly with getdecorator."
        partial_decorator = getdecorator(alias1="key1")

        @partial_decorator
        class MyClass(self.MockClass):
            pass

        instance = MyClass()
        instance["key1"] = "value1"
        self.assertEqual(instance.alias1, "value1")

    def test_setter_raises_error(self: Self) -> None:
        "Test that setting a property with an invalid type raises appropriate errors."
        mock_instance = self.MockClass()

        class MyClass(self.MockClass):
            pass

        MyClass = classdecorator(MyClass, alias1="key1")

        instance = MyClass()

        with self.assertRaises(KeyError):
            del instance.alias1

    def test_classdecorator_with_no_aliases(self: Self) -> None:
        "Test classdecorator with no alias provided."

        class MyClass(self.MockClass):
            pass

        MyClass = classdecorator(MyClass)

        instance = MyClass()
        instance["key1"] = "value1"

        # No alias was set, so accessing via alias1 should raise AttributeError
        with self.assertRaises(AttributeError):
            _ = instance.alias1


if __name__ == "__main__":
    unittest.main()
