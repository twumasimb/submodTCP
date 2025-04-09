import re
import sys
import os
import json
from datetime import datetime
from prioritization.utils import evaluate_fault_detection_efficiency

def parse_test_output(output_text):
    """Parse the output from pytest runs and extract test results."""
    # Regular expression to find test names and their results
    test_pattern = r"tests/test_calculator\.py::TestCalculator::(\w+)\[v1\] (PASSED|FAILED)"
    matches = re.findall(test_pattern, output_text)
    
    results = []
    for test_name, status in matches:
        results.append({
            'test_name': test_name,
            'status': status
        })
    
    return results

def create_summary_file(results, output_file, apfd=None):
    """Create a markdown summary file with the test results."""
    with open(output_file, 'w') as f:
        f.write("# Test Execution Summary\n\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Statistics
        passed = sum(1 for r in results if r['status'] == 'PASSED')
        failed = sum(1 for r in results if r['status'] == 'FAILED')
        total = len(results)
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        f.write(f"## Summary Statistics\n")
        f.write(f"- Total Tests: {total}\n")
        f.write(f"- Passed: {passed} ({pass_rate:.1f}%)\n")
        f.write(f"- Failed: {failed} ({100-pass_rate:.1f}%)\n")
        if apfd is not None:
            f.write(f"- APFD Score: {apfd:.4f}\n")
        f.write("\n")
        
        # Table of results
        f.write("## Test Results in Execution Order\n\n")
        f.write("| # | Test Name | Status |\n")
        f.write("|---|----------|--------|\n")
        
        for i, result in enumerate(results, 1):
            status_emoji = "✅" if result['status'] == 'PASSED' else "❌"
            f.write(f"| {i} | {result['test_name']} | {status_emoji} {result['status']} |\n")

def main():
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "test_output.txt"
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "test_summary.md"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        print("Capture test output to a file first using:")
        print("./run_prioritized_tests.sh > test_output.txt")
        return
    
    # Read the test output
    with open(input_file, 'r') as f:
        output_text = f.read()
    
    # Parse the output
    results = parse_test_output(output_text)

    # Calculate APFD if available
    apfd = None
    if os.path.exists("prioritized_tests.json"):
        with open("prioritized_tests.json", "r") as f:
            prioritized_tests = json.load(f)
        efficiency_metrics = evaluate_fault_detection_efficiency(prioritized_tests)
        apfd = efficiency_metrics.get('apfd', None)

    # Create the summary file
    create_summary_file(results, output_file, apfd)
    print(f"Test summary created: {output_file}")

if __name__ == "__main__":
    main()