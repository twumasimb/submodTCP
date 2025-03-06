# experiment_runner.py

import inspect
from typing import List, Dict
import matplotlib.pyplot as plt
from test_prioritization import (
    TestCase, TestPrioritization,
    CoverageBasedFunction, DiversityBasedFunction, CombinedFunction,
    extract_coverage, evaluate_prioritization
)
from test_library import TestLibrarySystem
import pickle

class ExperimentRunner:
    def __init__(self):
        # Extract test cases from TestLibrarySystem
        self.test_cases = self._extract_test_cases()
        # Simulate some faults that certain tests can detect
        self.faults = self._create_fault_matrix()
        
    def _extract_test_cases(self) -> List[TestCase]:
        """Extract test cases from TestLibrarySystem class."""
        test_cases = []
        
        for name, method in inspect.getmembers(TestLibrarySystem, predicate=inspect.isfunction):
            if name.startswith('test_'):
                code = inspect.getsource(method)
                test_case = TestCase(name, code)
                extract_coverage(test_case)
                test_cases.append(test_case)
        
        return test_cases
    
    def _create_fault_matrix(self) -> Dict[str, set[str]]:
        """Create a simulated fault matrix for evaluation."""
        # In practice, this would come from real fault data
        # Here we simulate some faults that certain tests can detect
        return {
            'fault1': {'test_add_book_duplicate', 'test_add_book_success'},
            'fault2': {'test_borrow_book_already_borrowed', 'test_return_book_success'},
            'fault3': {'test_get_overdue_books'},
            'fault4': {'test_search_books_no_results', 'test_search_books_by_title'},
            'fault5': {'test_remove_book_nonexistent', 'test_remove_book_success'}
        }
    
    def run_experiments(self):
        """Run experiments with different prioritization approaches."""
        # Get all unique elements for coverage calculation
        all_elements = set().union(*(test.coverage for test in self.test_cases))
        
        # Create objective functions
        coverage_fn = CoverageBasedFunction(all_elements)
        diversity_fn = DiversityBasedFunction()
        combined_fn = CombinedFunction(coverage_fn, diversity_fn, alpha=0.5)
        
        # Dictionary to store results
        results = {}
        
        # Run each prioritization strategy
        for name, objective_fn in [
            ('Coverage', coverage_fn),
            ('Diversity', diversity_fn),
            ('Combined', combined_fn)
        ]:
            prioritization = TestPrioritization(self.test_cases, objective_fn)
            prioritized_order = prioritization.prioritize(len(self.test_cases))
            
            # Evaluate the prioritization
            metrics = evaluate_prioritization(
                self.test_cases,
                prioritized_order,
                self.faults
            )
            
            results[name] = {
                'order': prioritized_order,
                'metrics': metrics
            }
        
        return results
    
    def save_results(self, results, filename='results.pkl'):
        """Save the results to a pickle file."""
        with open(filename, 'wb') as f:
            pickle.dump(results, f)
    
    def plot_results(self, results):
        """Plot FDR curves for different approaches."""
        plt.figure(figsize=(10, 6))
        
        for name, result in results.items():
            fdr_curve = result['metrics']['FDR_curve']
            plt.plot(range(1, len(fdr_curve) + 1), fdr_curve, label=name, marker='o')
        
        plt.xlabel('Number of Tests Executed')
        plt.ylabel('Fault Detection Rate')
        plt.title('Fault Detection Rate vs Tests Executed')
        plt.legend()
        plt.grid(True)
        plt.show()
        
        # Print APFD scores
        print("\nAPFD Scores:")
        for name, result in results.items():
            print(f"{name}: {result['metrics']['APFD']:.3f}")

def main():
    # Run experiments
    runner = ExperimentRunner()
    results = runner.run_experiments()
    
    # Plot and display results
    runner.plot_results(results)

    runner.save_results(results=results)

if __name__ == "__main__":
    main()