import time
import os
import datetime
import random
import pandas
from functools import wraps
from collections import namedtuple

Row = namedtuple('DataRow', ['label', 'last_element', 'random_element', 'median_of_three'])


class DataRow:
    rows = []
    label = None
    last_element = None
    random_element = None
    median_of_three = None
    last_element_average = None
    random_element_average = None
    median_of_three_average = None
    last_element_std = None
    random_element_std = None
    median_of_three_std = None
    result = None


class DataGenerator:
    @staticmethod
    def random(count):
        return DataGenerator.generate_list_of_random_numbers(count)

    @staticmethod
    def sorted(count):
        temp_list = DataGenerator.generate_list_of_random_numbers(count)
        return sorted(temp_list)

    @staticmethod
    def reverse_sorted(count):
        temp_list = DataGenerator.generate_list_of_random_numbers(count)
        return sorted(temp_list, reverse=True)

    @staticmethod
    def generate_list_of_random_numbers(count):
        range_start = 1
        range_end = count * 2
        list_size = count
        return random.sample(range(range_start, range_end), list_size)


class PivotsTypes:
    @staticmethod
    def last_element(**kwargs):
        high_index = kwargs['high_index']
        return high_index

    @staticmethod
    def random_element(**kwargs):
        return random.randint(kwargs['low_index'], kwargs['high_index'])

    @staticmethod
    def median_of_three(**kwargs):
        array, low_index, high_index = kwargs['array'], kwargs['low_index'], kwargs['high_index']
        medium_index = (low_index + high_index) // 2
        sorted_values = sorted([array[low_index], array[medium_index], array[high_index]])
        median_value = sorted_values[1]
        median_value_index = array.index(median_value)
        return median_value_index


class Algorithms:
    def algorithm_timer(func):
        @wraps(func)
        def timer(*args, **kwargs):
            time_start = time.perf_counter()
            algorithm = func(*args, **kwargs)
            time_elapsed = time.perf_counter() - time_start
            kwargs['measurements'].append(time_elapsed)
            return algorithm
        return timer

    @algorithm_timer
    def quick_sort(test_data, pivot_type, measurements=[]):

        def quick_sorting(array, low_index, high_index, p_type):
            if low_index < high_index:
                pivot = p_type(array=array, low_index=low_index, high_index=(high_index-1))
                array[pivot], array[low_index] = array[low_index], array[pivot]
                pivot_index = partition(array, low_index, high_index)
                quick_sorting(array, low_index, pivot_index, p_type)
                quick_sorting(array, pivot_index + 1, high_index, p_type)

        def partition(array, low_index, high_index):
            pivot = array[low_index]
            left_wall = low_index
            for index in range(low_index, high_index):
                if array[index] < pivot:
                    left_wall += 1
                    array[index], array[left_wall] = array[left_wall], array[index]
            array[low_index], array[left_wall] = array[left_wall], array[low_index]
            return left_wall

        numbers = test_data.copy()
        quick_sorting(numbers, 0, len(numbers), pivot_type)


class Tester:
    def __init__(self):
        self.last_element_results = []
        self.random_element_results = []
        self.median_of_three_results = []
        self.results = []

    def run_full_tests(self, data_generator, number_of_tests=5, number_of_subtests=10,
                           data_count=300, count_increment=150):
        self.check_recursion_error_possibility(data_count, count_increment, number_of_tests)
        current_test = 1
        count = data_count
        while current_test <= number_of_tests:
            current_subtest = 1
            while current_subtest <= number_of_subtests:
                test_data = data_generator(count)
                self.single_subtest(test_data)
                current_subtest += 1
            self.results.append(self.build_result(current_test, number_of_subtests, count))
            self.clear_partial_results()
            current_test += 1
            count += count_increment

    @staticmethod
    def check_recursion_error_possibility(data_count, count_increment, number_of_tests):
        if data_count + count_increment * (number_of_tests - 1) < 1000:
            return True
        else:
            raise RecursionError("Size of input data can't be larger than 1000 due to recursion limit!")

    def single_subtest(self, test_data):
        Algorithms.quick_sort(test_data, PivotsTypes.last_element, measurements=self.last_element_results)
        Algorithms.quick_sort(test_data, PivotsTypes.random_element, measurements=self.random_element_results)
        Algorithms.quick_sort(test_data, PivotsTypes.median_of_three, measurements=self.median_of_three_results)

    def build_result(self, current_test, number_of_subtests, count):
        result = DataRow()
        result.rows = []
        result.count = count
        for current_subtest in range(number_of_subtests):
            label = f'{str(current_test)}-{str(current_subtest + 1)}'
            result.rows.append(Row(label,
                                   self.last_element_results[current_subtest],
                                   self.random_element_results[current_subtest],
                                   self.median_of_three_results[current_subtest])
                               )
        from statistics import mean
        result.last_element_average = mean(self.last_element_results)
        result.random_element_average = mean(self.random_element_results)
        result.median_of_three_average = mean(self.median_of_three_results)
        from statistics import pstdev
        result.last_element_std = pstdev(self.last_element_results)
        result.random_element_std = pstdev(self.random_element_results)
        result.median_of_three_std = pstdev(self.median_of_three_results)
        return result
        
    def clear_partial_results(self):
        self.last_element_results.clear()
        self.random_element_results.clear()
        self.median_of_three_results.clear()

    def clear_all_results(self):
        self.last_element_results.clear()
        self.random_element_results.clear()
        self.median_of_three_results.clear()
        self.results.clear()
        

class ExcelExporter:
    DataSheet = namedtuple('DataSheet', ['sheet_name', 'data_frame'])

    def __init__(self):
        self.filename = ExcelExporter.generate_filename()
        self.data_sheets = []

    @staticmethod
    def generate_filename():
        formatted_current_datetime = datetime.datetime.now().strftime("%y-%m-%d_%H_%M")
        return f"Sorting Algorithms Measurements_{formatted_current_datetime}"

    def export_file(self):
        with pandas.ExcelWriter(f"{self.filename}.xlsx") as file:
            for sheet_name, data_frame in self.data_sheets:
                data_frame.to_excel(file, sheet_name=f'{sheet_name}')

    def launch_file(self):
        os.system(f"start EXCEL.EXE \"{self.filename}.xlsx\"")

    def generate_sheet(self, data, sheet_name):
        data_frame = ExcelExporter.create_data_frame(data)
        self.data_sheets.append(self.DataSheet(sheet_name, data_frame))

    @staticmethod
    def create_data_frame(data):
        def pad_with_none(arr, target_length):
            return arr + [None] * (target_length - len(arr))

        test_numbers = []
        numbers_count = []
        last_element_results = []
        last_element_averages = []
        last_element_deviations = []
        random_element_results = []
        random_element_averages = []
        random_element_deviations = []
        median_of_three_results = []
        median_of_three_averages = []
        median_of_three_deviations = []
        for item in data:
            rows = len(item.rows)
            test_numbers.extend([row.label for row in item.rows])
            numbers_count.extend(pad_with_none([item.count], rows))
            last_element_results.extend([row.last_element for row in item.rows])
            last_element_averages.extend(pad_with_none([item.last_element_average], rows))
            last_element_deviations.extend(pad_with_none([item.last_element_std], rows))
            random_element_results.extend([row.random_element for row in item.rows])
            random_element_averages.extend(pad_with_none([item.random_element_average], rows))
            random_element_deviations.extend(pad_with_none([item.random_element_std], rows))
            median_of_three_results.extend([row.median_of_three for row in item.rows])
            median_of_three_averages.extend(pad_with_none([item.median_of_three_average], rows))
            median_of_three_deviations.extend(pad_with_none([item.median_of_three_std], rows))
            
        measurements_data = {
            'Test number': test_numbers,
            'Numbers count': numbers_count,
            'Last Element Results': last_element_results,
            'Last Element Avg': last_element_averages,
            'Last Element STD': last_element_deviations,
            'Random Element Results': random_element_results,
            'Random Element Avg': random_element_averages,
            'Random Element STD': random_element_deviations,
            'Median Of Three Results': median_of_three_results,
            'Median Of Three Avg': median_of_three_averages,
            'Median Of Three STD': median_of_three_deviations,
        }
        measurements_data_frame = pandas.DataFrame(measurements_data, dtype=float)
        measurements_data_frame = measurements_data_frame.set_index('Test number')
        return measurements_data_frame


RunConfig = namedtuple('RunConfig', ['sheet_name', 'generator'])


def main():
    run_configs = (
        RunConfig("Random order", DataGenerator.random),
        RunConfig("Sorted", DataGenerator.sorted),
        RunConfig("Reverse-sorted", DataGenerator.reverse_sorted),
    )

    exporter = ExcelExporter()
    for config in run_configs:
        tester = Tester()
        tester.run_full_tests(config.generator)
        exporter.generate_sheet(tester.results, config.sheet_name)
        tester.clear_all_results()
    exporter.export_file()
    exporter.launch_file()


if __name__ == '__main__':
    main()
    