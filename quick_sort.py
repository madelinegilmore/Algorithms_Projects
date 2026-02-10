import copy
import random


def identify_quicksort_pivots(sorters, test_indices=[3, 5, 10], num_trials=10):
    """
    Identifies QuickSort pivot strategies among the specified sorters.
    """
    def calculate_variance(values):
        if not values or len(values) <= 1:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)

    def run_test(array, idx, name):
        try:
            test_array = copy.deepcopy(array)
            result = sorters[idx].sort(test_array)
            time_taken, _ = result
            return time_taken
        except RecursionError:
            return float('inf')

    characteristics = {}
    sorted_array = list(range(500))
    reverse_sorted = list(range(500, 0, -1))
    killer_array = list(range(1, 500)) + [0]
    median3_killer = [499] + list(range(498)) + [498]
    median3_trap = sorted_array.copy()
    median3_trap[0], median3_trap[len(median3_trap) // 2] = median3_trap[len(median3_trap) // 2], median3_trap[0]

    for idx in test_indices:
        sorted_time = run_test(sorted_array, idx, 'Sorted')
        reverse_time = run_test(reverse_sorted, idx, 'Reverse')
        killer_time = run_test(killer_array, idx, 'Killer')
        median3_killer_time = run_test(median3_killer, idx, 'Median3 Killer')
        median3_trap_time = run_test(median3_trap, idx, 'Median3 Trap')

        random_times = [run_test(random.sample(range(1000), 500), idx, f'Random {i}') for i in range(num_trials)]
        avg_random_time = sum(random_times) / len(random_times)
        random_variance = calculate_variance(random_times)

        characteristics[idx] = {
            'sorted_time': sorted_time,
            'reverse_time': reverse_time,
            'killer_time': killer_time,
            'median3_killer_time': median3_killer_time,
            'median3_trap_time': median3_trap_time,
            'avg_random_time': avg_random_time,
            'random_variance': random_variance
        }

    results = {}
    strategies = []
    for idx in test_indices:
        c = characteristics[idx]
        sorted_ratio = c['sorted_time'] / c['avg_random_time']
        reverse_ratio = c['reverse_time'] / c['avg_random_time']
        killer_ratio = c['killer_time'] / c['avg_random_time']
        median3_killer_ratio = c['median3_killer_time'] / c['avg_random_time']
        median3_trap_ratio = c['median3_trap_time'] / c['avg_random_time']

        if c['sorted_time'] == float('inf') or c['reverse_time'] == float('inf'):
            strategy = 'Last element pivot'
        elif median3_killer_ratio > 1.5 and median3_trap_ratio > 1.5:
            strategy = 'Median-of-3 pivot'
        elif c['random_variance'] > 0.002:
            strategy = 'Random pivot'
        elif max(sorted_ratio, reverse_ratio, killer_ratio) < 1.2:
            strategy = 'Random pivot (low variance)'
        else:
            strategy = 'Inconclusive'

        results[idx] = strategy
        strategies.append(strategy)

    unique_strategies = len(set(strategies))
    if unique_strategies < len(test_indices):
        print("Duplicate pivot strategies detected. Trying again...")
        return identify_quicksort_pivots(sorters, random.sample(range(len(sorters)), len(test_indices)), num_trials)

    return results


from mystery import Mystery
mystery = Mystery("madeline.gilmore@techexchange.in")
sorters = mystery.get_sorters()

pivot_strategies = identify_quicksort_pivots(sorters, [3, 5, 10])
print("\nQuickSort Pivot Strategies:")
for idx, strategy in pivot_strategies.items():
    sorter_name = sorters[idx]._Sorter__sorter_instance.__class__.__name__
    print(f"Sorter {idx} ({sorter_name}): {strategy}")
