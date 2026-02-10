from mystery import Mystery

mystery = Mystery("madeline.gilmore@techexchange.in")
sorters = mystery.get_sorters()

best_case = list(range(1000))
worst_case = list(range(1000, 0, -1))
almost_sorted = [1, 2, 3, 4, 5, 7, 6]

def identify_sorts(sorters):
    """Identifies Bubble, Insertion, and Selection Sort among sorters[0], sorters[1], and sorters[6]."""
    
    # 1. Get characteristics for each sorter
    test_indices = [0, 1, 6] # indices with O(n^2) time
    characteristics = {}
    
    for idx in test_indices:
        best_time, best_space = sorters[idx].sort(best_case.copy())
        worst_time, worst_space = sorters[idx].sort(worst_case.copy())
        almost_time, almost_space = sorters[idx].sort(almost_sorted.copy())
        
        # Store all characteristics
        characteristics[idx] = {
            'best_time': best_time,
            'worst_time': worst_time,
            'time_ratio': worst_time / best_time if best_time > 0 else float('inf'),
            'almost_time': almost_time,
        }
    
    # 2. Selection Sort typically has the most consistent performance regardless of input
    # Find the one with the ratio closest to 1.0.
    selection_index = min(test_indices, key=lambda idx: abs(characteristics[idx]['time_ratio'] - 1.0))
    
    # 3. Insertion sort performs much better on almost sorted arrays
    remaining = [i for i in test_indices if i != selection_index] # takes selection_index out of equation
    insertion_index = min(remaining, key=lambda idx: characteristics[idx]['almost_time']) #picks the minimun time on almost_time
    
    # 4. The remaining one is bubble sort
    bubble_index = [i for i in test_indices if i != selection_index and i != insertion_index][0]
    
    return sorters[selection_index], sorters[bubble_index], sorters[insertion_index], selection_index, bubble_index, insertion_index

# Identify the sorts and their indices
selection_sort, bubble_sort, insertion_sort, sel_idx, bub_idx, ins_idx = identify_sorts(sorters)

# Print results using the indices we got from our function
print(f"Selection Sort: {sel_idx}")
print(f"Bubble Sort: {bub_idx}")
print(f"Insertion Sort: {ins_idx}")
