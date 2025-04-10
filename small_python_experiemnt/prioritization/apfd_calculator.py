"""
APFD (Average Percentage of Fault Detection) Calculator Module

This module provides comprehensive functionality for calculating the APFD metric
for test case prioritization, as well as related metrics and visualizations.

The APFD metric measures how quickly faults are detected by a test suite execution
order, with values ranging from 0 to 1 (higher is better).

Formula: APFD = 1 - (TF₁ + TF₂ + ... + TFₘ) / (n × m) + 1/(2n)

Where:
- TFᵢ = position of the first test that reveals fault i
- m = number of faults
- n = number of test cases
"""

import re
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set

class APFDCalculator:
    """
    A class for calculating APFD and related metrics from test execution results.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the APFD calculator.
        
        Args:
            logger: Optional logger for tracking execution
        """
        self.logger = logger
        self.fault_mapping = {
            "negative_gcd": ["test_gcd"],
            "negative_exponent": ["test_power"],
            "sqrt_approximation": ["test_square_root"],
            "missing_modulus_zero_check": ["test_modulus"],
            "factorial_zero_case": ["test_factorial"],
            "missing_division_zero_check": ["test_divide"],
            "combined_operations": ["test_combined_operations"],
            "subtraction_negative": ["test_subtract"]
        }
    
    def parse_test_output(self, output_text: str) -> List[Dict[str, Any]]:
        """
        Parse pytest output text and extract test results in execution order.
        
        Args:
            output_text: Raw text output from pytest
            
        Returns:
            List of test result dictionaries with test name, status, and fault info
        """
        if self.logger:
            self.logger.info("Parsing test output...")
            
        test_pattern = r"tests/test_calculator\.py::TestCalculator::(\w+)\[v1\] (PASSED|FAILED)"
        
        test_matches = re.finditer(test_pattern, output_text)
        test_results = []
        
        for match in test_matches:
            test_name = match.group(1)
            status = match.group(2)
            
            # Find the test section in the output
            test_section_match = re.search(
                rf"{re.escape(match.group(0))}.*?(===+|$)", 
                output_text[match.start():], 
                re.DOTALL
            )
            
            test_output = ""
            if test_section_match:
                test_output = test_section_match.group(0)
            
            result = {
                "test_name": test_name,
                "status": status,
                "output": test_output,
                "detected_fault": None
            }
            
            # If test failed, determine which fault it detected
            if status == "FAILED":
                result["detected_fault"] = self._identify_fault(test_name, test_output)
                
            test_results.append(result)
            
        if self.logger:
            self.logger.info(f"Parsed {len(test_results)} test results")
            
        return test_results
    
    def _identify_fault(self, test_name: str, test_output: str) -> str:
        """
        Identify the specific fault detected by a failed test.
        
        Args:
            test_name: Name of the test that failed
            test_output: Output of the failed test
            
        Returns:
            String identifying the fault detected
        """
        fault_type = "unknown_fault"
        
        # Map test names to specific faults
        if "test_gcd" in test_name and "assert -6 == 6" in test_output:
            fault_type = "negative_gcd"
        elif "test_power" in test_name and "assert 0 == 0.5" in test_output:
            fault_type = "negative_exponent"
        elif "test_square_root" in test_name and "assert 1.99" in test_output:
            fault_type = "sqrt_approximation"
        elif "test_modulus" in test_name and "ZeroDivisionError" in test_output:
            fault_type = "missing_modulus_zero_check"
        elif "test_factorial" in test_name and "assert 0 == 1" in test_output:
            fault_type = "factorial_zero_case"
        elif "test_divide" in test_name and "ZeroDivisionError" in test_output:
            fault_type = "missing_division_zero_check"
        elif "test_combined_operations" in test_name:
            fault_type = "combined_operations"
        elif "test_subtract" in test_name and "subtract" in test_output:
            fault_type = "subtraction_negative"
            
        return fault_type
    
    def calculate_apfd(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate APFD and related metrics from test results.
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            Dictionary with APFD and related metrics
        """
        if self.logger:
            self.logger.info("Calculating APFD metrics...")
            
        total_tests = len(test_results)
        detected_faults: Set[str] = set()
        fault_detection_positions: Dict[str, int] = {}
        
        # Track fault detection positions
        for i, test in enumerate(test_results, 1):
            if test["status"] == "FAILED" and test["detected_fault"]:
                fault = test["detected_fault"]
                if fault not in detected_faults:
                    detected_faults.add(fault)
                    fault_detection_positions[fault] = i
        
        # Calculate APFD and related metrics
        total_faults = len(detected_faults)
        
        if total_faults == 0 or total_tests == 0:
            if self.logger:
                self.logger.warning("No faults detected or no tests run.")
            return {
                "apfd": 0,
                "total_tests": total_tests,
                "total_faults": 0,
                "fault_detection_positions": {},
                "detected_faults": [],
                "avg_position": 0,
                "tests_needed_percentage": 0,
                "error_detection": []
            }
        
        # Calculate APFD using the formula
        sum_positions = sum(fault_detection_positions.values())
        apfd = 1 - (sum_positions / (total_tests * total_faults)) + (1 / (2 * total_tests))
        
        # Average position where faults were detected
        avg_position = sum_positions / total_faults
        
        # Percentage of tests needed to find all faults
        max_position = max(fault_detection_positions.values())
        tests_needed_percentage = (max_position / total_tests) * 100
        
        # Create error detection curve data points
        error_detection = []
        found_so_far = 0
        
        # Sort the fault detection positions by test position
        sorted_positions = sorted(fault_detection_positions.items(), key=lambda x: x[1])
        position_index = 0
        
        for i in range(1, total_tests + 1):
            # Check if we found a new fault at this position
            if position_index < len(sorted_positions) and sorted_positions[position_index][1] == i:
                found_so_far += 1
                position_index += 1
                
            error_detection.append((i, found_so_far))
        
        metrics = {
            "apfd": apfd,
            "total_tests": total_tests,
            "total_faults": total_faults,
            "fault_detection_positions": fault_detection_positions,
            "detected_faults": list(detected_faults),
            "avg_position": avg_position,
            "tests_needed_percentage": tests_needed_percentage,
            "error_detection": error_detection
        }
        
        if self.logger:
            self.logger.info(f"APFD score: {apfd:.4f}")
            self.logger.info(f"Average fault detection position: {avg_position:.2f}")
            self.logger.info(f"Percentage of tests needed to find all faults: {tests_needed_percentage:.2f}%")
            
        return metrics
    
    def process_test_output_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a test output file to calculate APFD metrics.
        
        Args:
            file_path: Path to test output file
            
        Returns:
            Dictionary with APFD metrics
        """
        if self.logger:
            self.logger.info(f"Processing test output file: {file_path}")
            
        try:
            with open(file_path, 'r') as f:
                output_text = f.read()
                
            test_results = self.parse_test_output(output_text)
            metrics = self.calculate_apfd(test_results)
            
            # Add test execution order and results to the metrics
            metrics["test_execution"] = [
                {"position": i, "test_name": test["test_name"], "status": test["status"]}
                for i, test in enumerate(test_results, 1)
            ]
            
            return metrics
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error processing test output file: {str(e)}")
            raise
    
    def plot_fault_detection(self, metrics: Dict[str, Any], method_name: str = "", 
                           output_path: Optional[str] = None, display: bool = True) -> None:
        """
        Plot the fault detection curve.
        
        Args:
            metrics: Dictionary with APFD metrics
            method_name: Name of the prioritization method
            output_path: Path to save the plot (optional)
            display: Whether to display the plot
        """
        if self.logger:
            self.logger.info(f"Creating fault detection plot for method: {method_name}")
            
        plt.figure(figsize=(12, 7))
        
        # Extract data points
        error_detection = metrics["error_detection"]
        tests_run = [point[0] for point in error_detection]
        errors_found = [point[1] for point in error_detection]
        
        # Plot the error detection curve
        plt.plot(tests_run, errors_found, marker='o', linestyle='-', linewidth=2, markersize=8)
        
        # Mark where each specific fault was detected
        fault_positions = metrics["fault_detection_positions"]
        fault_markers = sorted([(pos, fault) for fault, pos in fault_positions.items()])
        
        for pos, fault in fault_markers:
            plt.annotate(
                fault, 
                xy=(pos, errors_found[pos-1]),
                xytext=(pos, errors_found[pos-1] + 0.2),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                fontsize=9,
                ha='center'
            )
        
        # Add a perfect detection line for reference
        if metrics["total_faults"] > 0:
            optimal_x = list(range(1, metrics["total_faults"] + 1))
            optimal_y = list(range(1, metrics["total_faults"] + 1))
            optimal_x.append(metrics["total_tests"])
            optimal_y.append(metrics["total_faults"])
            
            plt.plot(optimal_x, optimal_y, 'r--', alpha=0.5, label="Optimal Detection")
        
        # Add APFD value to the plot
        plt.text(
            0.02, 0.95, 
            f"APFD: {metrics['apfd']:.4f}\nTotal Faults: {metrics['total_faults']}", 
            transform=plt.gca().transAxes,
            fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white", alpha=0.8)
        )
        
        # Configure the plot
        plt.xlabel('Number of Tests Run', fontsize=12)
        plt.ylabel('Number of Faults Detected', fontsize=12)
        plt.title(f'Fault Detection Rate - {method_name}', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # Set appropriate y-axis limits
        max_faults = max(errors_found) if errors_found else 0
        plt.ylim(0, max_faults + 1)
        
        # Set x-axis ticks at every test position
        plt.xticks(range(1, metrics["total_tests"] + 1))
        
        # Improve appearance
        plt.tight_layout()
        
        # Save or display the plot
        if output_path:
            plt.savefig(output_path, dpi=300)
            if self.logger:
                self.logger.info(f"Fault detection plot saved to {output_path}")
                
        if display:
            plt.show()
            
    def generate_summary_report(self, metrics: Dict[str, Any], method_name: str = "",
                              output_path: Optional[str] = None) -> str:
        """
        Generate a detailed summary report of APFD metrics.
        
        Args:
            metrics: Dictionary with APFD metrics
            method_name: Name of the prioritization method
            output_path: Path to save the report (optional)
            
        Returns:
            Summary report as a string
        """
        if self.logger:
            self.logger.info(f"Generating summary report for method: {method_name}")
            
        report = [
            f"# APFD Summary Report - {method_name}",
            "",
            f"## Effectiveness Metrics",
            "",
            f"- **APFD Score**: {metrics['apfd']:.4f}",
            f"- **Total Tests**: {metrics['total_tests']}",
            f"- **Total Faults**: {metrics['total_faults']}",
            f"- **Average Position of Fault Detection**: {metrics['avg_position']:.2f}",
            f"- **Percentage of Tests Needed to Find All Faults**: {metrics['tests_needed_percentage']:.2f}%",
            "",
            f"## Fault Detection Positions",
            ""
        ]
        
        # Add table of fault detection positions
        report.append("| Fault | Detected at Position | Detected by Test |")
        report.append("|------|---------------------|------------------|")
        
        fault_positions = metrics["fault_detection_positions"]
        sorted_faults = sorted(fault_positions.items(), key=lambda x: x[1])
        
        for fault, position in sorted_faults:
            test_name = ""
            for test in metrics["test_execution"]:
                if test["position"] == position:
                    test_name = test["test_name"]
                    break
                    
            report.append(f"| {fault} | {position} | {test_name} |")
        
        report.append("")
        report.append("## Test Execution Order")
        report.append("")
        report.append("| # | Test Name | Status |")
        report.append("|---|-----------|--------|")
        
        for test in metrics["test_execution"]:
            status_emoji = "✅" if test["status"] == "PASSED" else "❌"
            report.append(f"| {test['position']} | {test['test_name']} | {status_emoji} {test['status']} |")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
                
            if self.logger:
                self.logger.info(f"Summary report saved to {output_path}")
                
        return report_text
    
    def compare_methods(self, method_metrics: Dict[str, Dict[str, Any]], 
                       output_path: Optional[str] = None, display: bool = True) -> None:
        """
        Compare different prioritization methods based on their APFD scores.
        
        Args:
            method_metrics: Dictionary mapping method names to their metrics
            output_path: Path to save the comparison plot (optional)
            display: Whether to display the plot
        """
        if self.logger:
            self.logger.info(f"Comparing {len(method_metrics)} prioritization methods")
            
        plt.figure(figsize=(12, 8))
        
        # Bar chart for APFD scores
        methods = list(method_metrics.keys())
        apfd_scores = [metrics['apfd'] for metrics in method_metrics.values()]
        
        plt.subplot(2, 1, 1)
        bars = plt.bar(methods, apfd_scores, color='skyblue')
        
        # Add APFD values on top of bars
        for bar, score in zip(bars, apfd_scores):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{score:.4f}",
                ha='center', 
                fontsize=10
            )
            
        plt.ylabel('APFD Score', fontsize=12)
        plt.title('APFD Scores by Prioritization Method', fontsize=14)
        plt.ylim(0, 1.1)  # APFD is between 0 and 1
        plt.grid(axis='y', alpha=0.3)
        
        # Line chart for fault detection
        plt.subplot(2, 1, 2)
        
        for method, metrics in method_metrics.items():
            error_detection = metrics["error_detection"]
            tests_run = [point[0] for point in error_detection]
            errors_found = [point[1] for point in error_detection]
            
            # Normalize by percentage of tests run
            tests_pct = [x / metrics["total_tests"] * 100 for x in tests_run]
            
            plt.plot(tests_pct, errors_found, marker='o', linestyle='-', label=method)
        
        plt.xlabel('Percentage of Test Suite Run (%)', fontsize=12)
        plt.ylabel('Faults Detected', fontsize=12)
        plt.title('Fault Detection Rate Comparison', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300)
            if self.logger:
                self.logger.info(f"Method comparison plot saved to {output_path}")
                
        if display:
            plt.show()
            
        # Calculate and report which method detected faults earliest
        if self.logger:
            total_methods = len(method_metrics)
            if total_methods > 1:
                self.logger.info("\nMethod comparison summary:")
                
                for fault in set().union(*[m['detected_faults'] for m in method_metrics.values()]):
                    positions = []
                    for method, metrics in method_metrics.items():
                        pos = metrics['fault_detection_positions'].get(fault, float('inf'))
                        positions.append((method, pos))
                    
                    positions.sort(key=lambda x: x[1])
                    best_method, best_pos = positions[0]
                    
                    if best_pos < float('inf'):
                        self.logger.info(f"Fault '{fault}' detected earliest by {best_method} at position {best_pos}")