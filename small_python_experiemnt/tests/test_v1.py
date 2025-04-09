# tests/test_v1.py
import os
import sys
import pytest

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from v1.calculator import Calculator

@pytest.fixture
def calculator():
    return Calculator()

# Import all the tests
from test_calculator import TestCalculator