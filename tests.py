import unittest
import unittest.mock
import zadanie_4 as zad4
import random


class TestSortingAlgorithms(unittest.TestCase):
    def generate_list_of_random_numbers(range_start=1, range_end=200, list_size=100):
        return random.sample(range(range_start, range_end), list_size)

    generated_nums = generate_list_of_random_numbers()

    def test_quick_sort_last(self):
        test_list = self.generated_nums
        expected = test_list.copy()
        expected.sort()
        result = zad4.Algorithms.quick_sort(test_list.copy(), zad4.PivotsTypes.last_element)
        self.assertEqual(expected, result)

    def test_quick_sort_median(self):
        test_list = self.generated_nums
        expected = test_list.copy()
        expected.sort()
        result = zad4.Algorithms.quick_sort(test_list.copy(), zad4.PivotsTypes.median_of_three)
        self.assertEqual(expected, result)

    def test_quick_sort_random(self):
        test_list = self.generated_nums
        expected = test_list.copy()
        expected.sort()
        result = zad4.Algorithms.quick_sort(test_list.copy(), zad4.PivotsTypes.random_element)
        self.assertEqual(expected, result)

if __name__ == '__main__':
    unittest.main()
