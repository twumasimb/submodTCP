#!/bin/bash

# This script was auto-generated to run tests in prioritized order

pytest tests/test_calculator.py::TestCalculator::test_divide -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_square_root -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_combined_operations -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_average -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_gcd -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_factorial -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_subtract -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_add -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_absolute -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_modulus -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_multiply -v -k "v1"
pytest tests/test_calculator.py::TestCalculator::test_power -v -k "v1"
