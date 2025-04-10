# tests/test_calculator.py

import os
import sys
import math
import pytest

# We'll use a fixture to switch between v0 and v1 calculator
@pytest.fixture(params=["v0", "v1"])
def calculator(request):
    # Add the parent directory to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    if request.param == "v0":
        from v0.calculator import Calculator
    else:  # v1
        from v1.calculator import Calculator
    
    return Calculator()

class TestCalculator:
    
    def test_add(self, calculator):
        assert calculator.add(1, 2) == 3
        assert calculator.add(-1, 1) == 0
        assert calculator.add(-1, -1) == -2
        assert calculator.add(0, 0) == 0
        assert calculator.add(1.5, 2.5) == 4.0
        
    def test_subtract(self, calculator):
        assert calculator.subtract(3, 2) == 1
        assert calculator.subtract(1, 1) == 0
        assert calculator.subtract(-1, -1) == 0
        assert calculator.subtract(0, 5) == -5
        assert calculator.subtract(5.5, 2.5) == 3.0
        
    def test_multiply(self, calculator):
        assert calculator.multiply(2, 3) == 6
        assert calculator.multiply(-2, 3) == -6
        assert calculator.multiply(-2, -3) == 6
        assert calculator.multiply(0, 5) == 0
        assert calculator.multiply(2.5, 2) == 5.0
        
    def test_divide(self, calculator):
        assert calculator.divide(6, 3) == 2
        assert calculator.divide(5, 2) == 2.5
        assert calculator.divide(-6, 3) == -2
        assert calculator.divide(-6, -3) == 2
        assert calculator.divide(0, 5) == 0
        
        # Test division by zero exception
        with pytest.raises(ValueError):
            calculator.divide(5, 0)
            
    def test_power(self, calculator):
        assert calculator.power(2, 3) == 8
        assert calculator.power(2, 0) == 1
        assert calculator.power(0, 5) == 0
        assert calculator.power(5, 1) == 5
        assert calculator.power(2, -1) == 0.5
        
    def test_square_root(self, calculator):
        assert calculator.square_root(4) == 2
        assert calculator.square_root(9) == 3
        assert calculator.square_root(0) == 0
        assert pytest.approx(calculator.square_root(2), 0.0001) == 1.4142135623730951
        
        # Test negative number exception
        with pytest.raises(ValueError):
            calculator.square_root(-1)
    
    def test_factorial(self, calculator):
        assert calculator.factorial(0) == 1
        assert calculator.factorial(1) == 1
        assert calculator.factorial(5) == 120
        assert calculator.factorial(10) == 3628800
        
        # Test non-integer and negative input exceptions
        with pytest.raises(ValueError):
            calculator.factorial(-1)
        with pytest.raises(ValueError):
            calculator.factorial(1.5)
    
    def test_absolute(self, calculator):
        assert calculator.absolute(0) == 0
        assert calculator.absolute(5) == 5
        assert calculator.absolute(-5) == 5
        assert calculator.absolute(-3.14) == 3.14
    
    def test_modulus(self, calculator):
        assert calculator.modulus(10, 3) == 1
        assert calculator.modulus(10, 2) == 0
        assert calculator.modulus(-10, 3) == 2
        assert calculator.modulus(5.5, 2) == 1.5
        
        # Test modulus by zero exception
        with pytest.raises(ValueError):
            calculator.modulus(5, 0)
    
    def test_gcd(self, calculator):
        assert calculator.gcd(48, 18) == 6
        assert calculator.gcd(0, 5) == 5
        assert calculator.gcd(5, 0) == 5
        assert calculator.gcd(-48, 18) == 6
        assert calculator.gcd(48, -18) == 6
        
        # Test non-integer input exception
        with pytest.raises(ValueError):
            calculator.gcd(5.5, 2)
    
    def test_average(self, calculator):
        assert calculator.average([1, 2, 3, 4, 5]) == 3
        assert calculator.average([0]) == 0
        assert calculator.average([-5, 5]) == 0
        assert calculator.average([1.5, 2.5, 3.5]) == 2.5
        
        # Test empty list exception
        with pytest.raises(ValueError):
            calculator.average([])
    
    # Combined operation tests
    def test_combined_operations(self, calculator):
        # Test combining add, multiply, and divide
        result = calculator.divide(calculator.multiply(calculator.add(3, 4), 2), 4)
        assert result == 3.5
        
        # Test combining subtract, power and absolute
        result = calculator.absolute(calculator.power(calculator.subtract(3, 5), 2))
        assert result == 4
        
        # Test combining factorial and square_root
        result = calculator.square_root(calculator.factorial(4))
        assert pytest.approx(result, 0.0001) == 4.898979485566356
        
        # Test combining average and modulus
        result = calculator.modulus(calculator.average([10, 20, 30]), 7)
        assert result == 6
    
    # # Tests for V1-only features
    # def test_v1_features(self, calculator):
    #     # Skip these tests for v0 calculator
    #     if not hasattr(calculator, "log"):
    #         pytest.skip("Advanced features not available in this calculator version")
            
    #     # Test logarithm
    #     assert pytest.approx(calculator.log(100), 0.0001) == 2.0
    #     assert pytest.approx(calculator.log(8, 2), 0.0001) == 3.0
        
    #     # Test logarithm with invalid input
    #     with pytest.raises(ValueError):
    #         calculator.log(0)
    #     with pytest.raises(ValueError):
    #         calculator.log(-5)
            
    #     # Test trigonometric functions
    #     assert pytest.approx(calculator.sin(math.pi/2), 0.0001) == 1.0
    #     assert pytest.approx(calculator.cos(0), 0.0001) == 1.0
    #     assert pytest.approx(calculator.tan(math.pi/4), 0.0001) == 1.0
        
    #     # Test memory functions
    #     calculator.memory_store(5)
    #     assert calculator.memory_recall() == 5
        
    #     calculator.memory_add(3)
    #     assert calculator.memory_recall() == 8
        
    #     calculator.memory_clear()
    #     assert calculator.memory_recall() == 0