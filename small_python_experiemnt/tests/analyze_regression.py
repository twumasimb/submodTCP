# tests/analyze_regression.py

import subprocess
import json

def run_test(test_name):
    """Run a specific test and return whether it passed or failed"""
    cmd = f"pytest tests/test_v1.py::TestCalculator::{test_name} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0  # True if passed, False if failed

# List of all test methods
tests = [
    "test_add",
    "test_subtract",
    "test_divide",
    "test_multiply",
    "test_power",
    "test_square_root"
]

# Run tests and record which ones fail
results = {}
for test in tests:
    passed = run_test(test)
    results[test] = "PASS" if passed else "FAIL"

# Print results in order of failure (failed tests first)
print("Test Prioritization Results:")
print("-" * 40)
for test, result in sorted(results.items(), key=lambda x: 0 if x[1] == "FAIL" else 1):
    print(f"{test:20} {result}")

# Save results to a file
with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)