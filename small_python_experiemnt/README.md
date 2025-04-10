# Test Case Prioritization (TCP) Tool

A Python-based tool for prioritizing test cases to detect faults earlier using various strategies including semantic analysis and submodular optimization.

## Overview

This tool aims to find the most efficient order to run test cases, maximizing the early detection of faults. It implements several prioritization techniques and evaluates their effectiveness using the Average Percentage of Fault Detection (APFD) metric.

The project includes:

1. A calculator implementation (v0) with correct implementations of mathematical functions
2. A deliberately buggy version (v1) with seeded faults for testing
3. A test suite covering basic and advanced calculator functions
4. Multiple test prioritization strategies
5. Evaluation tools for comparing prioritization effectiveness

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/twumasimb/submodTCP.git
   cd submodTCP/small_python_experiemnt
   ```

2. Install dependencies:
   ```bash
   pip install pytest pytest-html
   pip install transformers torch tqdm numpy
   pip install matplotlib
   ```

## Prioritization Methods

The tool implements four main prioritization strategies:

### 1. Random Prioritization

Randomly shuffles test cases to establish a baseline for comparison.

```bash
python -m prioritization.order --method random --seed 42
```

### 2. Semantic Prioritization

Analyzes the content of test cases and prioritizes based on:
- Tests with exception handling
- Tests with more assertions
- Tests targeting complex functions (division, square root, etc.)
- Tests with wider function coverage

```bash
python -m prioritization.order --method semantic
```

### 3. Previous Failure Prioritization

Prioritizes test cases that failed in previous test runs.

```bash
python -m prioritization.order --method failure --failure-history test_results.json
```

### 4. Submodular Optimization

Uses code embeddings from the UnixCoder model to measure similarity between tests and functions, then applies submodular optimization to select tests that maximize information gain.

```bash
python -m prioritization.order --method submod --source-dir v1
```

## Understanding APFD

The Average Percentage of Fault Detection (APFD) is a metric that quantifies how quickly faults are detected in a prioritized test suite. APFD values range from 0 to 1, with higher values indicating better prioritization.

### APFD Formula

```
APFD = 1 - (TF₁ + TF₂ + ... + TFₘ) / (n × m) + 1/(2n)
```

Where:
- TFᵢ = position of the first test case that reveals fault i
- m = number of faults
- n = number of test cases

### Example Calculation

If you have 12 tests and 7 faults detected at positions 2, 4, 5, 6, 7, 9, and 10:

```
APFD = 1 - (2 + 4 + 5 + 6 + 7 + 9 + 10) / (12 × 7) + 1/(2 × 12)
     = 1 - 43/84 + 1/24
     ≈ 0.51
```

## Using the APFD Calculator

### Calculate APFD for a Single Test Output

To calculate APFD for a test output file:

```bash
python -m prioritization.calculate_apfd test_random_output.txt --method random --plot
```

This will:
1. Parse the test output file
2. Determine which faults were detected and at what positions
3. Calculate the APFD score and related metrics
4. Generate a summary report and fault detection plot

### Compare Multiple Prioritization Methods

To compare the effectiveness of different prioritization methods:

```bash
python -m prioritization.compare_methods --methods random,semantic,submod --output comparison_results
```

This will:
1. Run each prioritization method
2. Execute tests in the prioritized order
3. Calculate APFD scores for each method
4. Generate comparison reports and visualizations

## Seeded Faults in the v1 Calculator

The v1 implementation contains intentional errors for testing TCP techniques:

| Function | Fault Description |
|----------|------------------|
| subtract | Incorrectly adds instead of subtracts when `b` is negative |
| divide | Missing zero division check |
| power | Returns 0 for negative exponents instead of calculating correctly |
| square_root | Uses incorrect exponent (0.499 instead of 0.5) causing approximation errors |
| factorial | Incorrectly returns 0 for factorial of 0 (should be 1) |
| modulus | Missing zero division check |
| gcd | Incorrect handling of negative numbers |
| sin | Incorrectly multiplies angle by 0.9 causing wrong results |

## Calculator Functions

### Basic Operations (v0 and v1)
- **add(a, b)**: Addition
- **subtract(a, b)**: Subtraction 
- **multiply(a, b)**: Multiplication
- **divide(a, b)**: Division
- **power(a, b)**: Exponentiation
- **square_root(a)**: Square root
- **factorial(n)**: Factorial
- **absolute(a)**: Absolute value
- **modulus(a, b)**: Modulo operation
- **gcd(a, b)**: Greatest common divisor
- **average(numbers)**: Arithmetic mean

### Advanced Operations (v1 only)
- **log(a, base=10)**: Logarithm with configurable base
- **sin(angle)**, **cos(angle)**, **tan(angle)**: Trigonometric functions
- **memory_store(value)**, **memory_recall()**, etc.: Memory operations

## Project Structure

```
small_python_experiemnt/
├── prioritization/            # Test prioritization package
│   ├── apfd_calculator.py     # APFD calculation utilities
│   ├── calculate_apfd.py      # APFD calculation CLI
│   ├── compare_methods.py     # Method comparison utilities
│   ├── evaluation_utils.py    # Evaluation helper functions
│   ├── order.py               # Main prioritization module
│   ├── prioritization_methods.py # Implementation of prioritization algorithms
│   └── utils.py               # General utility functions
├── tests/                     # Test files
│   ├── test_calculator.py     # Main test cases
│   ├── test_v0.py             # Tests for v0 implementation
│   └── test_v1.py             # Tests for v1 implementation
├── v0/                        # Original correct implementation
│   └── calculator.py
├── v1/                        # Implementation with seeded bugs
│   └── calculator.py
├── run_prioritized_tests.sh   # Script to run tests in prioritized order
└── test_summary.py            # Test summary generation
```

## Understanding APFD Calculation in the Tool

The APFD calculation in this tool involves:

1. **Test Execution Tracking**: Running tests in the prioritized order and recording pass/fail status.

2. **Fault Identification**: Mapping each failing test to the specific fault it detected in the v1 implementation.

3. **Detection Position Recording**: Recording the first test position where each fault was detected.

4. **APFD Calculation**: Applying the APFD formula to the detection positions.

5. **Visualization**: Generating plots and reports to understand fault detection effectiveness.

### Understanding Fault Detection

The tool identifies seven specific faults in the v1 implementation:

1. **negative_gcd**: GCD calculation fails with negative numbers
2. **negative_exponent**: Power function fails with negative exponents
3. **sqrt_approximation**: Square root function returns slightly incorrect values
4. **missing_modulus_zero_check**: Modulus operation fails to check for zero divisors
5. **factorial_zero_case**: Factorial incorrectly handles n=0
6. **missing_division_zero_check**: Division fails to check for zero divisors
7. **combined_operations**: Bugs manifest in combined operations

## Example Output

```
Prioritized Test Order:
-----------------------------------------------------------
1. TestCalculator::test_divide
2. TestCalculator::test_power
3. TestCalculator::test_square_root
4. TestCalculator::test_factorial
5. TestCalculator::test_modulus
6. TestCalculator::test_gcd
-----------------------------------------------------------

APFD Metrics for semantic:
  APFD Score: 0.8333
  Total Tests: 12
  Total Faults: 7
  Average Fault Detection Position: 3.71
  Percentage of Tests Needed to Find All Faults: 50.00%

Detailed results saved to results/semantic_apfd_summary.md
Fault detection plot saved to results/semantic_apfd_plot.png
```

## Testing Approach

The test suite covers all calculator functions with various test cases:

1. **Individual Function Tests**: Each calculator function has its own test function
2. **Edge Cases**: Tests for division by zero, negative inputs, etc.
3. **Combined Operations**: Tests combining multiple calculator functions
4. **Parameterized Tests**: Same tests run against both v0 and v1 implementations

The test fixture design allows you to:
- Verify correct implementations pass all tests (v0)
- Detect seeded faults in the buggy implementation (v1)
- Compare prioritization effectiveness across different methods

## Contributing

Contributions are welcome! Here are some ways to improve the project:

1. Add new prioritization methods
2. Enhance APFD visualization
3. Support additional test frameworks
4. Implement CI/CD integration
5. Create more complex test cases and fault scenarios

## License

[MIT License](LICENSE)