import unittest

from solution import average


class AverageTests(unittest.TestCase):
    def test_average_of_positive_numbers(self):
        self.assertEqual(average([2, 4, 6]), 4)

    def test_average_of_negative_numbers(self):
        self.assertEqual(average([-4, -2]), -3)

    def test_empty_list_returns_zero(self):
        self.assertEqual(average([]), 0)


if __name__ == "__main__":
    unittest.main()