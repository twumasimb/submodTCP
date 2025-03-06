# test_prioritization.py

from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple
import inspect
import numpy as np
from itertools import combinations

class TestCase:
    def __init__(self, name: str, code: str):
        self.name = name
        self.code = code
        self.coverage: Set[str] = set()  # Set of covered elements
        
    def __str__(self) -> str:
        return f"TestCase({self.name})"

class SubmodularFunction(ABC):
    @abstractmethod
    def evaluate(self, selected: List[TestCase], candidate: TestCase) -> float:
        """Evaluate the marginal gain of adding candidate to selected."""
        pass

class CoverageBasedFunction(SubmodularFunction):
    def __init__(self, all_elements: Set[str]):
        self.all_elements = all_elements
    
    def evaluate(self, selected: List[TestCase], candidate: TestCase) -> float:
        """Evaluate based on new elements covered."""
        current_coverage = set().union(*(test.coverage for test in selected))
        new_coverage = candidate.coverage - current_coverage
        return len(new_coverage)

class DiversityBasedFunction(SubmodularFunction):
    def evaluate(self, selected: List[TestCase], candidate: TestCase) -> float:
        """Evaluate based on how different the candidate is from selected tests."""
        if not selected:
            return 1.0
        
        # Calculate average Jaccard distance to selected tests
        distances = []
        for test in selected:
            intersection = len(candidate.coverage & test.coverage)
            union = len(candidate.coverage | test.coverage)
            jaccard = 1 - (intersection / union if union > 0 else 0)
            distances.append(jaccard)
        
        return np.mean(distances)

class CombinedFunction(SubmodularFunction):
    def __init__(self, coverage_fn: CoverageBasedFunction, 
                 diversity_fn: DiversityBasedFunction,
                 alpha: float = 0.5):
        self.coverage_fn = coverage_fn
        self.diversity_fn = diversity_fn
        self.alpha = alpha
    
    def evaluate(self, selected: List[TestCase], candidate: TestCase) -> float:
        """Combine coverage and diversity objectives."""
        coverage_score = self.coverage_fn.evaluate(selected, candidate)
        diversity_score = self.diversity_fn.evaluate(selected, candidate)
        return self.alpha * coverage_score + (1 - self.alpha) * diversity_score

class TestPrioritization:
    def __init__(self, test_cases: List[TestCase], objective_fn: SubmodularFunction):
        self.test_cases = test_cases
        self.objective_fn = objective_fn
    
    def prioritize(self, k: int) -> List[TestCase]:
        """Greedy algorithm for submodular maximization."""
        selected = []
        remaining = self.test_cases.copy()
        
        for _ in range(min(k, len(self.test_cases))):
            best_gain = float('-inf')
            best_test = None
            
            for test in remaining:
                gain = self.objective_fn.evaluate(selected, test)
                if gain > best_gain:
                    best_gain = gain
                    best_test = test
            
            if best_test:
                selected.append(best_test)
                remaining.remove(best_test)
        
        return selected

def extract_coverage(test_case: TestCase) -> None:
    """Extract coverage information from test case code."""
    # This is a simplified version - in practice, you'd use code coverage tools
    # Here we just extract function calls and variable names as coverage elements
    import ast
    from textwrap import dedent
    
    class CoverageVisitor(ast.NodeVisitor):
        def __init__(self):
            self.covered = set()
        
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.covered.add(node.func.id)
            self.generic_visit(node)
        
        def visit_Name(self, node):
            self.covered.add(node.id)
            self.generic_visit(node)
    
    # Remove indentation before parsing
    code = dedent(test_case.code)
    tree = ast.parse(code)
    visitor = CoverageVisitor()
    visitor.visit(tree)
    test_case.coverage = visitor.covered

def evaluate_prioritization(original_order: List[TestCase], 
                          prioritized_order: List[TestCase],
                          faults: Dict[str, Set[str]]) -> Dict[str, float]:
    """
    Evaluate the prioritization using APFD and other metrics.
    
    Args:
        original_order: Original test case order
        prioritized_order: Prioritized test case order
        faults: Dictionary mapping fault IDs to sets of test cases that detect them
    
    Returns:
        Dictionary of evaluation metrics
    """
    n = len(prioritized_order)
    m = len(faults)
    if n == 0 or m == 0:
        return {"APFD": 0.0, "FDR": 0.0}
    
    # Calculate APFD (Average Percentage of Faults Detected)
    tf = 0  # Sum of first positions where each fault is detected
    for fault_id, detecting_tests in faults.items():
        for i, test in enumerate(prioritized_order, 1):
            if test.name in detecting_tests:
                tf += i
                break
    
    apfd = 1 - (tf / (n * m)) + (1 / (2 * n))
    
    # Calculate FDR (Fault Detection Rate)
    detected_faults = set()
    fdr_values = []
    
    for i, test in enumerate(prioritized_order, 1):
        for fault_id, detecting_tests in faults.items():
            if test.name in detecting_tests:
                detected_faults.add(fault_id)
        fdr_values.append(len(detected_faults) / m)
    
    return {
        "APFD": apfd,
        "FDR": fdr_values[-1],
        "FDR_curve": fdr_values
    }