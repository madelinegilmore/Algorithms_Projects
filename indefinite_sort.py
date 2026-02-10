from mystery import Mystery
import time

mystery = Mystery("madeline.gilmore@techexchange.in")
sorters = mystery.get_sorters()

test_indices = [4, 8, 11] #stooge, slow, python, indices (no conclusion after time_complex analysis) >> took out bogo because it kept crashing the program

best_case = list(range(100))
worst_case = list(range(100, 0, -1))
almost_sorted = [1, 2, 3, 4, 5, 7, 6]

def identify_special_sorts(sorters, indices):
    """Identifies sorts whos time complexities were not clear: Stooge, Slow, Python's sort, and Bogo."""

    times = {}
    for idx in indices:
        print(f"Starting tests for index: {idx}") # print statments for debugging
        times[idx] = {}
        print(f"Running best case for index: {idx}")
        times[idx]['best'] = sorters[idx].sort(best_case.copy())[0]
        print(f"Running worst case for index: {idx}")
        times[idx]['worst'] = sorters[idx].sort(worst_case.copy())[0]
        print(f"Running almost sorted case for index: {idx}")
        times[idx]['almost'] = sorters[idx].sort(almost_sorted.copy())[0]
        print(f"Finished tests for index: {idx}")

    # Python sort is the fastest on all cases
    print("Identifying Python Sort...")
    python_index = min(indices, key=lambda idx: times[idx]['almost'])
    print(f"Python Sort identified at index: {python_index}")

    # slow is generally slower than stooge
    remaining = [idx for idx in indices if idx != python_index]
    print(f"Remaining indices: {remaining}")

    if len(remaining) == 2:
    # Check that Stooge is slower than Slow by comparing their worst-case times > slow sort has a worse worst case than stooge
    stooge_index, slow_index = sorted(remaining, key=lambda idx: times[idx]['worst'], reverse=True)
    elif len(remaining) == 1:
        stooge_index = remaining[0]

    bogo_index = 9 # Bogo is at index 9, by default since it had to be taken out of tests due to long run time

    print(f"Stooge Sort identified at index: {stooge_index}")
    print(f"Slow Sort identified at index: {slow_index}")
    print(f"Bogo Sort identified at index: {bogo_index}")

    return sorters[bogo_index], stooge_sort, slow_sort, sorters[python_index], bogo_index, stooge_index, slow_index, python_index

bogo_sort, stooge_sort, slow_sort, python_sort, bogo_idx, stooge_idx, slow_idx, python_idx = identify_special_sorts(sorters, test_indices)

print(f"Bogo Sort: {bogo_idx}")
print(f"Stooge Sort: {stooge_idx}")
print(f"Slow Sort: {slow_idx}")
print(f"Python Sort: {python_idx}")