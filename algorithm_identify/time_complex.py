import time
import tracemalloc
import random
import pandas as pd
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
from collections import defaultdict
import math

'''
This is an updated version of sort_tests.py after submitting the wrong version :/
'''

def create_test_suite():
    """Create a test suite with varied input sizes and patterns."""
    test_cases = {
        # Standard cases
        "Sorted Small": list(range(100)),
        "Reverse Small": list(range(100, 0, -1)),
        "Random Small": random.sample(range(100), 100),
        
        # Scaling tests
        "Random Tiny": random.sample(range(100), 10),
        "Random Small": random.sample(range(1000), 100),
        "Random Medium": random.sample(range(10000), 1000),
        "Random Large": random.sample(range(20000), 5000),  # Added larger test for better O(n log n) detection
        
        # Special cases for inefficient algorithms
        "Micro Array": random.sample(range(10), 5),  # Only 5 elements
        "Mini Array": random.sample(range(20), 8),   # Only 8 elements
        
        # Algorithm-specific test cases
        "Nearly Sorted": sorted(random.sample(range(1000), 990)) + random.sample(range(1000), 10),
        "Few Unique": [random.randint(0, 10) for _ in range(1000)],  # Good test for counting sort
        "Many Duplicates": [random.randint(0, 100) for _ in range(1000)],  # Good for bucket-based sorts
        
        # Special case for O(n+k) algorithms
        "Small Range": [random.randint(0, 20) for _ in range(1000)],  # Small k value for counting sort
        "Large Range": [random.randint(0, 5000) for _ in range(1000)],  # Large k value for counting sort
    }
    return test_cases

def is_sorted(arr):
    """Verify if an array is correctly sorted."""
    return all(arr[i] <= arr[i+1] for i in range(len(arr)-1))

def run_with_timeout(sorter, data, sorter_name, case, timeout=10):
    """Run sorting with timeout to prevent infinite loops."""
    original_data = data.copy()
    
    def target(return_dict):
        start_time = time.time()  # Still track external time for timeout handling
        print(f"🔵 Sorting: {sorter_name} on {case}")
        try:
            result = sorter.sort(data)
            end_time = time.time()
            
            # Check if result is a tuple containing (sorted_array, time, memory)
            if isinstance(result, tuple) and len(result) >= 3:
                sorted_array = result[0]
                sort_time = result[1]  # Use time reported by sorter
                sort_memory = result[2]  # Use memory reported by sorter
            else:
                # Fall back to external measurement if tuple not returned
                sorted_array = result if result is not None else data
                sort_time = end_time - start_time
                sort_memory = tracemalloc.get_traced_memory()[1]
            
            # Verify the result is sorted correctly
            sorting_correct = is_sorted(sorted_array)
            
            return_dict["time"] = sort_time
            return_dict["memory"] = sort_memory
            return_dict["success"] = sorting_correct
            
            if sorting_correct:
                print(f"✅ Sorted: {sorter_name} on {case} in {return_dict['time']:.4f} sec")
            else:
                print(f"❌ Incorrect: {sorter_name} on {case}")
                return_dict["time"] = float('inf')
        except Exception as e:
            return_dict["time"] = float('inf')
            return_dict["memory"] = float('inf')
            return_dict["success"] = False
            print(f"❌ Error in {sorter_name} on {case}: {str(e)}")
        finally:
            if tracemalloc.is_tracing():
                tracemalloc.stop()

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=target, args=(return_dict,))
    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        print(f"⏳ Timeout: {sorter_name} on {case}")
        return float('inf'), float('inf'), False

    return return_dict.get("time", float('inf')), return_dict.get("memory", float('inf')), return_dict.get("success", False)


def analyze_complexity(data_points):
    """Analyze the algorithmic complexity based on data points with improved n log n detection."""
    if len(data_points) < 3:
        return "Inconclusive (insufficient data)"
    
    # Sort by input size
    data_points.sort()
    
    sizes = np.array([p[0] for p in data_points])
    values = np.array([p[1] for p in data_points])
    
    # Handle negative, zero, or very small values
    for i, val in enumerate(values):
        if val <= 0:
            values[i] = 1e-10  # Small positive value
    
    try:
        # Create model functions for fitting
        def constant_model(x, a):
            return a * np.ones_like(x)
            
        def log_model(x, a):
            return a * np.log(x)
            
        def linear_model(x, a):
            return a * x
            
        def linearithmic_model(x, a):
            return a * x * np.log(x)
            
        def quadratic_model(x, a):
            return a * x**2
                  
        # Calculate normalized mean squared error for each model
        from scipy.optimize import curve_fit
        import warnings
        
        # Suppress curve_fit warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            
            # Dictionary to store model results
            models = {}
            
            # Fit each model and calculate error
            for name, model_func in [
                ("constant", constant_model),
                ("logarithmic", log_model),
                ("linear", linear_model),
                ("linearithmic", linearithmic_model),
                ("quadratic", quadratic_model),
            ]:
                try:
                    # Fit the model
                    popt, _ = curve_fit(model_func, sizes, values)
                    
                    # Calculate predictions
                    predictions = model_func(sizes, *popt)
                    
                    # Calculate normalized mean squared error
                    mse = np.mean((values - predictions)**2)
                    nmse = mse / np.mean(values**2)  # Normalize by mean of squared values
                    
                    # Store results
                    models[name] = {
                        "params": popt,
                        "nmse": nmse
                    }
                except:
                    # If fitting fails, assign a high error
                    models[name] = {
                        "params": None,
                        "nmse": float('inf')
                    }
        
        # Add more weight to linearithmic detection (compensate for similarity to linear)
        if "linearithmic" in models and "linear" in models:
            # If linearithmic and linear are close in error, prefer linearithmic for certain ratios
            linearithmic_error = models["linearithmic"]["nmse"]
            linear_error = models["linear"]["nmse"]
            
            # Adjust linearithmic error - needs fine tuning based on typical data patterns
            if linearithmic_error < linear_error * 1.2:
                # If they're close, check rate of growth
                if len(sizes) >= 3:
                    # Calculate growth rates between points
                    growth_ratios = []
                    for i in range(1, len(values)):
                        # Calculate ratio of value increases vs size increases
                        value_ratio = values[i] / values[i-1]
                        size_ratio = sizes[i] / sizes[i-1]
                        growth_ratio = value_ratio / size_ratio
                        growth_ratios.append(growth_ratio)
                    
                    # If growth is increasing (n log n behavior), prefer linearithmic
                    if all(r >= 1.0 for r in growth_ratios):
                        models["linearithmic"]["nmse"] *= 0.8  # Boost linearithmic
        
        # Find the best model (lowest error)
        best_model = min(models.items(), key=lambda x: x[1]["nmse"])
        model_name = best_model[0]
        
        # Additional validation for merge sort detection
        # Check if linear and linearithmic are both low error and close to each other
        if model_name == "linear" and "linearithmic" in models:
            linear_error = models["linear"]["nmse"]
            linearithmic_error = models["linearithmic"]["nmse"]
            
            # If they're very close, do a specific test for merge sort patterns
            if linearithmic_error < linear_error * 1.5:
                # For larger datasets, merge sort's n log n behavior becomes more apparent
                larger_sizes = sizes[sizes >= 100]
                larger_values = values[sizes >= 100]
                
                if len(larger_sizes) >= 2:
                    # Check if the growth rate is increasing (signature of n log n)
                    ratios = np.diff(larger_values) / np.diff(larger_sizes)
                    if len(ratios) >= 2 and ratios[-1] > ratios[0]:
                        model_name = "linearithmic"  # Override to linearithmic
        
        # Interpret the best model
        complexity_map = {
            "constant": "O(1) - Constant",
            "logarithmic": "O(log n) - Logarithmic",
            "linear": "O(n) - Linear",
            "linearithmic": "O(n log n) - Linearithmic",
            "quadratic": "O(n²) - Quadratic",
        }
        
        return complexity_map.get(model_name, "Inconclusive")
        
    except Exception as e:
        return f"Analysis failed: {str(e)}"

def analyze_time_complexity(time_results):
    """Analyze the algorithmic time complexity with improved n log n detection."""
    data_points = []
    
    # Use more data points for better curve fitting
    for size_category in ["Tiny", "XSmall", "Small", "Medium", "Large"]:
        key = f"Random {size_category}"
        if key in time_results and time_results[key] != float('inf'):
            size_map = {
                "Tiny": 10, 
                "XSmall": 50,
                "Small": 100, 
                "Medium": 1000, 
                "Large": 5000
            }
            data_points.append((size_map[size_category], time_results[key]))
    
    return analyze_complexity(data_points)

def analyze_space_complexity(memory_results):
    """Analyze the algorithmic space complexity."""
    data_points = []
    
    for size_category in ["Tiny", "Small", "Medium"]:
        key = f"Random {size_category}"
        if key in memory_results and memory_results[key] != float('inf'):
            size_map = {"Tiny": 10, "Small": 100, "Medium": 1000}
            data_points.append((size_map[size_category], memory_results[key]))
    
    return analyze_complexity(data_points)

def run_tests(sorters):
    """Run enhanced performance tests for all sorting algorithms."""
    test_cases = create_test_suite()
    time_results = defaultdict(dict)
    memory_results = defaultdict(dict)
    
    # Debug - print all sorters
    print("\n🔍 List of all sorters available:")
    for idx, sorter in enumerate(sorters, 1):
        sorter_name = sorter._Sorter__sorter_instance.__class__.__name__
        print(f"{idx}. {sorter_name}")
    print(f"Total sorters: {len(sorters)}\n")
    
    # Run tests with all sorters
    for idx, sorter in enumerate(sorters):
        base_sorter_name = sorter._Sorter__sorter_instance.__class__.__name__
        # Count how many times this name has appeared so far
        same_name_count = sum(1 for s in sorters[:idx] 
                             if s._Sorter__sorter_instance.__class__.__name__ == base_sorter_name)
        # Add a suffix if it's a duplicate
        sorter_name = base_sorter_name if same_name_count == 0 else f"{base_sorter_name}_{same_name_count+1}"
        print(f"\n🔍 Testing sorter: {sorter_name}")
        
        # Initialize results dictionary even if all tests fail
        time_results[sorter_name] = {}
        memory_results[sorter_name] = {}
        
        # Run each test case
        for case_name, data in test_cases.items():
            test_data = data.copy()
            time_taken, memory_used, success = run_with_timeout(sorter, test_data, sorter_name, case_name)
            
            # Store results
            time_results[sorter_name][case_name] = time_taken
            memory_results[sorter_name][case_name] = memory_used
        
        # Analyze complexity
        time_complexity = analyze_time_complexity(time_results[sorter_name])
        space_complexity = analyze_space_complexity(memory_results[sorter_name])
    
    # Create summary DataFrame
    summary_data = []
    for sorter_name in time_results.keys():
        time_complexity = analyze_time_complexity(time_results[sorter_name])
        space_complexity = analyze_space_complexity(memory_results[sorter_name])
        
        summary_data.append({
            'Sorter': sorter_name,
            'Time Complexity': time_complexity,
            'Space Complexity': space_complexity
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Create detailed DataFrames
    time_df = pd.DataFrame({sorter_name: pd.Series(test_results) 
                           for sorter_name, test_results in time_results.items()})
    
    memory_df = pd.DataFrame({sorter_name: pd.Series(test_results) 
                             for sorter_name, test_results in memory_results.items()})
    
    # Print and save results
    print("\n📊 Algorithm Analysis Results:\n")
    print(summary_df)
    
    return summary_df, time_df, memory_df



if __name__ == "__main__":
    from mystery import Mystery
    
    # Initialize Mystery class with your email
    mystery = Mystery("madeline.gilmore@techexchange.in")
    sorters = mystery.get_sorters()  # Get personalized sorting algorithms
    
    # Run enhanced tests
    summary_df, time_df, memory_df = run_tests(sorters)
    
    # Find suspected merge sort algorithms - THIS LOOP SHOULD BE HERE
    for idx, sorter in enumerate(sorters):
        sorter_name = sorter._Sorter__sorter_instance.__class__.__name__
        