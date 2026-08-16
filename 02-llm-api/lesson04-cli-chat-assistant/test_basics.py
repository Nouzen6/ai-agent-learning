import unittest


def add(a, b):
    return a + b


class TestAdd(unittest.TestCase):
    def test_add_two_numbers(self):
        actual = add(2, 3)
        expected = 5

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()