# Test Case Prioritization (TCP) Tool

A Python-based tool for prioritizing test cases using various techniques including semantic analysis and submodular optimization.

## Overview

This tool provides several methods to prioritize test case execution order to detect bugs faster:

1. **Random Prioritization**: Simple shuffling of test cases
2. **Semantic Prioritization**: Orders tests based on test complexity and function risk
3. **Previous Failure Prioritization**: Prioritizes tests that failed in the past
4. **Submodular Optimization**: Uses code embeddings and submodular functions to find an optimal test order

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/submodTCP.git
   cd submodTCP/small_python_experiemnt
   ```

2. Install dependencies:
   ```bash
   pip install pytest
   pip install transformers torch  # For submodular prioritization
   pip install tqdm numpy
   pip install coverage  # For coverage-based analysis
   ```

## Usage

Basic usage:
```bash
python -m prioritization.order --method [random|semantic|failure|submod] --evaluate
```

Options:
- `--method`: Prioritization method (random, semantic, failure, or submod)
- `--evaluate`: Analyze how quickly the method finds all bugs
- `--test-dir`: Directory containing test files (default: ../tests)
- `--output`: Save prioritized order to a file
- `--source-dir`: Directory containing source code (for submod method)
- `--seed`: Random seed for reproducibility
- `--failure-history`: JSON file with test failure history

### Running the code

1. **Random prioritization:**
   ```bash
   python -m prioritization.order --method random
   ```

2. **Semantic prioritization with evaluation:**
   ```bash
   python -m prioritization.order --method semantic --evaluate
   ```

3. **Using previous failure history:**
   ```bash
   python -m prioritization.order --method failure --failure-history test_results.json
   ```

4. **Submodular optimization:**
   ```bash
   python -m prioritization.order --method submod --source-dir v1
   ```

5. **Save prioritized order to a file:**
   ```bash
   python -m prioritization.order --method semantic --output prioritized_tests.json
   ```

6. **Run with a specific random seed for reproducibility:**
   ```bash
   python -m prioritization.order --method random --seed 42
   ```

7. **Run on a specific test directory:**
   ```bash
   python -m prioritization.order --method semantic --test-dir ./mytests
   ```

### Running the test cases

To run the entire test suite:
```
pytest tests/test_v1.py
```

To run a specific test:
```
pytest tests/test_v1.py::TestCalculator::test_divide
```

## Prioritization Methods

### Random Prioritization
Randomly shuffles test cases. Useful as a baseline for comparison with more sophisticated methods.

```
python -m prioritization.order --method random --seed 42
```

### Semantic Prioritization
Analyzes the content of test cases and prioritizes them based on:
- Tests with exception handling
- Tests with more assertions
- Tests for more complex functions (e.g., division, square root)
- Tests with wider function coverage

```
python -m prioritization.order --method semantic
```

### Previous Failure Prioritization
Prioritizes test cases that failed in previous runs, based on a failure history file.

```
python -m prioritization.order --method failure --failure-history test_results.json
```

### Submodular Optimization Prioritization
Uses code embeddings from UnixCoder to measure similarity between tests and functions, then applies a submodular optimization to select tests that maximize information gain.

```
python -m prioritization.order --method submod --source-dir v1
```

## Evaluation

The tool can evaluate how quickly each prioritization method finds all bugs:

```
python -m prioritization.order --method semantic --evaluate
```

This produces metrics including:
- APFD (Average Percentage of Fault Detection)
- Average position where bugs were found
- Percentage of tests needed to find all bugs
- Position where each specific bug was found

## Project Structure

```
small_python_experiemnt/
├── prioritization/          # Test prioritization package
│   ├── __init__.py
│   ├── order.py             # Implementation of prioritization algorithms
│   └── utils.py             # Helper functions for analysis
├── tests/                   # Test files
│   ├── test_calculator.py   # Main test cases
│   ├── test_v0.py           # Version-specific imports
│   └── test_v1.py           # Version-specific imports
├── v0/                      # Original correct implementation
│   └── calculator.py
└── v1/                      # Implementation with bugs
    └── calculator.py
```

## How It Works

### Submodular Optimization Process

1. **Code Embedding**: The tool uses UnixCoder to embed both source code functions and test cases into vector representations
2. **Similarity Calculation**: Computes similarities between test cases and functions
3. **Greedy Selection**: Selects test cases iteratively based on marginal gain
4. **Information Maximization**: Prioritizes tests that provide the most new information

### Fault Detection Evaluation

The evaluation process:
1. Runs tests in the prioritized order
2. Records when each fault is first detected
3. Calculates APFD and other metrics
4. Generates a report showing how quickly bugs were found

## Example Output

```
Prioritized Test Order:
------------------------------------------------------------
1. TestCalculator::test_divide
2. TestCalculator::test_power
3. TestCalculator::test_square_root
4. TestCalculator::test_subtract
5. TestCalculator::test_multiply
6. TestCalculator::test_add
------------------------------------------------------------

Fault Detection Results for Semantic Prioritization:
------------------------------------------------------------
Total tests: 6
Total faults: 3
APFD score: 0.8333
Average fault detection position: 2.00
Percentage of tests needed to find all faults: 50.00%

Faults found at positions:
  division_by_zero: Test #1
  negative_exponent: Test #2
  incorrect_sqrt: Test #3
------------------------------------------------------------
```

## Calculator Features and Functions

The calculator implementation includes the following functionality:

### Basic Operations (Available in v0 and v1)
- **add(a, b)**: Addition of two numbers
- **subtract(a, b)**: Subtraction of two numbers 
- **multiply(a, b)**: Multiplication of two numbers 
- **divide(a, b)**: Division of two numbers
- **power(a, b)**: Raises 'a' to the power 'b'
- **square_root(a)**: Calculates the square root of 'a'
- **factorial(n)**: Calculates n! (n factorial)
- **absolute(a)**: Returns the absolute value of 'a'
- **modulus(a, b)**: Returns the remainder of a ÷ b
- **gcd(a, b)**: Returns the greatest common divisor of a and b
- **average(numbers)**: Calculates the average of a list of numbers

### Advanced Operations (Only in v1)
- **log(a, base=10)**: Logarithm with configurable base
- **sin(angle)**: Sine of an angle
- **cos(angle)**: Cosine of an angle
- **tan(angle)**: Tangent of an angle
- **memory_store(value)**: Stores a value in memory
- **memory_recall()**: Returns the value stored in memory
- **memory_add(value)**: Adds a value to memory
- **memory_clear()**: Resets memory to 0

## Seeded Faults in v1 Calculator

The v1 implementation contains intentional errors (seeded faults) for testing purposes:

| Function | Fault Description |
|----------|------------------|
| subtract | Incorrectly adds instead of subtracts when `b` is negative |
| divide | Missing zero division check, could cause runtime error |
| power | Returns 0 for any negative exponent, should use correct power formula |
| square_root | Uses incorrect exponent (0.499 instead of 0.5) causing approximation errors |
| factorial | Incorrectly returns 0 for factorial of 0 (should be 1) |
| modulus | Missing zero division check |
| gcd | Incorrect handling of negative numbers (doesn't apply absolute value) |
| sin | Incorrectly multiplies angle by 0.9 causing incorrect results |

## Testing Approach

The test suite covers all calculator functions with a variety of test cases:

1. **Individual Function Tests**: Each calculator function has its own test function with multiple assertions
2. **Edge Cases**: Tests cover edge cases like division by zero, negative inputs, etc.
3. **Combined Operations**: Some tests combine multiple calculator functions to test integration
4. **Conditional Tests**: Advanced features are only tested when available (v1 only)

The test fixture design allows tests to run against both v0 and v1 implementations, which helps:
- Verify that correct implementations pass all tests (v0)
- Detect seeded faults in the buggy implementation (v1)
- Ensure consistent behavior across calculator versions

## Improvements

This expanded implementation demonstrates:

1. **Feature Evolution**: Shows how software evolves with new features (v0 to v1)
2. **Bug Introduction**: Illustrates how new bugs can be introduced during development
3. **Test Coverage**: Provides comprehensive test coverage for all functions
4. **Test Prioritization**: Offers a realistic scenario for testing TCP techniques

Running the test prioritization tool on this expanded calculator will show which test ordering strategies most efficiently detect the various seeded faults.




---
#### Commands to use in the rearranged test case
```bash
pytest tests/test_calculator.py::TestCalculator::{test_method_name} -v -k "v0"
```


```bash
./run_prioritized_tests.sh > test_output.txt
```


```bash
python test_summary.py test_output.txt test_summary.md
```