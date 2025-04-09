# tests/test_v0.py
import pytest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from v0.calculator import Calculator

@pytest.fixture
def calculator():
    return Calculator()

# Import all the tests
from test_calculator import TestCalculator