import unittest
from datetime import date, datetime, time, timedelta

from inheritance_dict import InheritanceDict


class A(str):
    pass


class TypeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Prepare shared InheritanceDict fixtures for the test class.

        Creates two class-level InheritanceDict instances:
        - inheritance_dict: mapping object->1, int->2, str->3, "a"->4
        - inheritance_dict2: mapping int->2, str->3, "a"->4

        These fixtures are used by the tests to verify exact-type lookups and MRO-based resolution.
        """
        super().setUpClass()
        cls.inheritance_dict = InheritanceDict({object: 1, int: 2, str: 3, "a": 4})
        cls.inheritance_dict2 = InheritanceDict({int: 2, str: 3, "a": 4})

    def test_exact_type(self):
        """
        Verify that InheritanceDict returns values for exact key types (and string keys) via both item access and .get().

        Asserts that:
        - For `self.inheritance_dict`, exact-type lookups yield 1 for `object`, 2 for `int`, 3 for `str`, and 4 for `"a"`, using both indexing and `get()`.
        - For `self.inheritance_dict2` (which lacks an `object` mapping), exact-type lookups yield 2 for `int`, 3 for `str`, and 4 for `"a"`, using both indexing and `get()`.
        """
        self.assertEqual(1, self.inheritance_dict[object])
        self.assertEqual(2, self.inheritance_dict[int])
        self.assertEqual(3, self.inheritance_dict[str])
        self.assertEqual(4, self.inheritance_dict["a"])
        self.assertEqual(1, self.inheritance_dict.get(object))
        self.assertEqual(2, self.inheritance_dict.get(int))
        self.assertEqual(3, self.inheritance_dict.get(str))
        self.assertEqual(4, self.inheritance_dict.get("a"))
        self.assertEqual(2, self.inheritance_dict2[int])
        self.assertEqual(3, self.inheritance_dict2[str])
        self.assertEqual(4, self.inheritance_dict2["a"])
        self.assertEqual(2, self.inheritance_dict2.get(int))
        self.assertEqual(3, self.inheritance_dict2.get(str))
        self.assertEqual(4, self.inheritance_dict2.get("a"))

    def test_mro_walk(self):
        self.assertEqual(1, self.inheritance_dict[complex])
        self.assertEqual(2, self.inheritance_dict[bool])
        self.assertEqual(3, self.inheritance_dict[A])
        self.assertEqual(1, self.inheritance_dict.get(complex))
        self.assertEqual(2, self.inheritance_dict.get(bool))
        self.assertEqual(3, self.inheritance_dict.get(A))
        self.assertEqual(2, self.inheritance_dict2[bool])
        self.assertEqual(3, self.inheritance_dict2[A])
        self.assertEqual(2, self.inheritance_dict2.get(bool))
        self.assertEqual(3, self.inheritance_dict2.get(A))

    def test_missing_key(self):
        with self.assertRaises(KeyError):
            self.inheritance_dict2[object]
        with self.assertRaises(KeyError):
            self.inheritance_dict2[complex]
        with self.assertRaises(KeyError):
            self.inheritance_dict["B"]
        self.assertEqual(None, self.inheritance_dict2.get(object))
        self.assertEqual(None, self.inheritance_dict2.get(complex))
        self.assertEqual(None, self.inheritance_dict.get("B"))
        self.assertEqual(10, self.inheritance_dict2.get(object, 10))
        self.assertEqual(10, self.inheritance_dict2.get(complex, 10))
        self.assertEqual(10, self.inheritance_dict.get("B", 10))


if __name__ == "__main__":
    unittest.main()
