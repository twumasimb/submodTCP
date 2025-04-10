#!/usr/bin/env python
"""
Script to run and compare different test prioritization methods.

This script:
1. Runs each prioritization method
2. Executes tests in the prioritized order
3. Calculates APFD metrics for each method
4. Generates comparison reports and visualizations

Usage:
    python -m prioritization.compare_methods [--methods METHOD1,METHOD2,...] [--output DIR] [--no-execute]
"""

import os
import sys
import time
import argparse
import subprocess
import tempfile
from typing import List, Dict, Any

from prioritization.order import prioritize_tests
from prioritization.apfd_calculator import APFDCalculator
from prioritization.logging_utils import setup_logger

def run_tests_in_order(tests: List[Dict[str, Any]], output_file: str) -> None:
    """
    Run tests in the specified order and save the output to a file.
    
    Args:
        tests: List of test dictionaries in prioritized order
        output_file: File to save the test output to
    """
    with open(output_file, 'w') as f:
        for test in tests:
            test_name = test['full_name']
            command = f"pytest tests/test_v1.py::{test_name} -v"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            # Write the output to the file
            f.write(result.stdout)
            if result.stderr:
                f.write(result.stderr)
            
            # Ensure output is flushed in case of interruption
            f.flush()

def compare_methods(methods: List[str], output_dir: str, execute_tests: bool) -> None:
    """
    Compare different test prioritization methods.
    
    Args:
        methods: List of method names to compare
        output_dir: Directory to save the results to
        execute_tests: Whether to execute tests or use existing output files
    """
    logger = setup_logger("compare_methods")
    logger.info(f"Comparing methods: {', '.join(methods)}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Dictionary to store metrics for each method
    method_metrics = {}
    
    for method in methods:
        logger.info(f"Processing method: {method}")
        method_output_dir = os.path.join(output_dir, method)
        os.makedirs(method_output_dir, exist_ok=True)
        
        # Get prioritized tests
        tests = prioritize_tests(method=method, logger=logger)
        
        # Execute tests if requested
        if execute_tests:
            output_file = os.path.join(method_output_dir, f"{method}_test_output.txt")
            logger.info(f"Running tests in prioritized order, saving output to {output_file}")
            run_tests_in_order(tests, output_file)
        else:
            # Use existing output file
            output_file = os.path.join(method_output_dir, f"{method}_test_output.txt")
            if not os.path.exists(output_file):
                logger.warning(f"Output file {output_file} does not exist, skipping {method}")
                continue
                
        # Calculate APFD metrics
        calculator = APFDCalculator(logger)
        metrics = calculator.process_test_output_file(output_file)
        
        # Save summary report
        summary_file = os.path.join(method_output_dir, f"{method}_apfd_summary.md")
        calculator.generate_summary_report(metrics, method, summary_file)
        
        # Generate plot
        plot_file = os.path.join(method_output_dir, f"{method}_apfd_plot.png")
        calculator.plot_fault_detection(metrics, method, plot_file, display=False)
        
        # Store metrics for comparison
        method_metrics[method] = metrics
        
        logger.info(f"APFD for {method}: {metrics['apfd']:.4f}")
        
    # Compare methods
    if len(method_metrics) > 1:
        logger.info("Comparing methods...")
        
        # Generate comparison plot
        calculator = APFDCalculator(logger)
        comparison_plot = os.path.join(output_dir, "method_comparison.png")
        calculator.compare_methods(method_metrics, comparison_plot, display=False)
        
        # Generate comparison report
        comparison_file = os.path.join(output_dir, "method_comparison.md")
        with open(comparison_file, 'w') as f:
            f.write("# Test Prioritization Method Comparison\n\n")
            f.write("## APFD Scores\n\n")
            f.write("| Method | APFD | Total Faults | Avg. Detection Position |\n")
            f.write("|--------|------|--------------|-------------------------|\n")
            
            # Sort methods by APFD score
            sorted_methods = sorted(method_metrics.items(), key=lambda x: x[1]['apfd'], reverse=True)
            
            for method, metrics in sorted_methods:
                f.write(f"| {method} | {metrics['apfd']:.4f} | {metrics['total_faults']} | {metrics['avg_position']:.2f} |\n")
            
            f.write("\n## Fault Detection Analysis\n\n")
            f.write("| Fault | Best Method | Position | Worst Method | Position |\n")
            f.write("|-------|-------------|----------|--------------|----------|\n")
            
            # Analyze which method found each fault earliest
            all_faults = set()
            for metrics in method_metrics.values():
                all_faults.update(metrics['detected_faults'])
                
            for fault in all_faults:
                positions = {}
                for method, metrics in method_metrics.items():
                    pos = metrics['fault_detection_positions'].get(fault, float('inf'))
                    positions[method] = pos
                
                # Find best and worst methods
                best_method = min(positions.items(), key=lambda x: x[1])
                worst_method = max(positions.items(), key=lambda x: x[1])
                
                # Format infinity for readability
                worst_pos = worst_method[1] if worst_method[1] != float('inf') else "Not Found"
                
                f.write(f"| {fault} | {best_method[0]} | {best_method[1]} | {worst_method[0]} | {worst_pos} |\n")
                
        logger.info(f"Method comparison saved to {comparison_file}")
        logger.info(f"Method comparison plot saved to {comparison_plot}")

def main():
    parser = argparse.ArgumentParser(description="Compare test prioritization methods")
    parser.add_argument("--methods", default="random,semantic,submod", 
                        help="Comma-separated list of methods to compare")
    parser.add_argument("--output", default="comparison_results",
                        help="Directory to save the results to")
    parser.add_argument("--no-execute", action="store_true",
                        help="Don't execute tests, use existing output files")
    
    args = parser.parse_args()
    
    methods = args.methods.split(',')
    compare_methods(methods, args.output, not args.no_execute)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())