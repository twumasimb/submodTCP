#!/usr/bin/env python
"""
Command-line script for calculating APFD metrics from test output files.

Usage:
    python -m prioritization.calculate_apfd <test_output_file> [--method <method_name>] [--output <output_dir>] [--plot]

Arguments:
    test_output_file         Path to the test output file to analyze
    --method                 Name of the prioritization method used
    --output                 Directory to save the results to
    --plot                   Generate and save detection curve plots
"""

import os
import sys
import argparse
from prioritization.apfd_calculator import APFDCalculator
from prioritization.logging_utils import setup_logger

def main():
    parser = argparse.ArgumentParser(description="Calculate APFD metrics from test output files")
    parser.add_argument("test_output_file", help="Path to the test output file to analyze")
    parser.add_argument("--method", default="unknown", help="Name of the prioritization method used")
    parser.add_argument("--output", default=".", help="Directory to save the results to")
    parser.add_argument("--plot", action="store_true", help="Generate and save detection curve plots")
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(f"apfd_{args.method}")
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Process the test output file
    calculator = APFDCalculator(logger)
    metrics = calculator.process_test_output_file(args.test_output_file)
    
    # Generate summary report
    summary_file = os.path.join(args.output, f"{os.path.basename(args.test_output_file).split('.')[0]}_apfd_summary.md")
    calculator.generate_summary_report(metrics, args.method, summary_file)
    
    # Generate fault detection plot if requested
    if args.plot:
        plot_file = os.path.join(args.output, f"{os.path.basename(args.test_output_file).split('.')[0]}_apfd_plot.png")
        calculator.plot_fault_detection(metrics, args.method, plot_file, display=False)
    
    # Print summary to console
    print(f"\nAPFD Metrics for {args.method}:")
    print(f"  APFD Score: {metrics['apfd']:.4f}")
    print(f"  Total Tests: {metrics['total_tests']}")
    print(f"  Total Faults: {metrics['total_faults']}")
    print(f"  Average Fault Detection Position: {metrics['avg_position']:.2f}")
    print(f"  Percentage of Tests Needed to Find All Faults: {metrics['tests_needed_percentage']:.2f}%")
    print(f"\nDetailed results saved to {summary_file}")
    
    if args.plot:
        print(f"Fault detection plot saved to {plot_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())