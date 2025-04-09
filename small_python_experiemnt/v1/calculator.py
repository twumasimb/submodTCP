# v1/calculator.py - Modified calculator with intentional errors

import math

class Calculator:
    def __init__(self):
        self.result = 0
        self.memory = 0  # Memory storage for advanced operations
        
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        # ERROR 1: Incorrect subtraction logic
        # This incorrectly adds instead of subtracts when b is negative
        if b < 0:
            return a + abs(b)  # ERROR: Should be a - b
        return a - b
        
    def multiply(self, a, b):
        return a * b
        
    def divide(self, a, b):
        # ERROR 2: Missing zero division check
        # Division by zero check has been removed causing potential crash
        return a / b  # ERROR: Missing zero division check
        
    def power(self, a, b):
        # ERROR 3: Incorrect power calculation for negative exponents
        # This returns 0 for any negative exponent, which is incorrect
        if b < 0:
            return 0  # ERROR: Should be a ** b
        return a ** b
        
    def square_root(self, a):
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        # ERROR 4: Approximation error in square root calculation
        # This uses an approximation that is slightly inaccurate
        return a ** 0.499  # ERROR: Incorrect exponent, should be 0.5

    def factorial(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial is only defined for non-negative integers")
        # ERROR: Incorrect factorial calculation for n=0
        if n == 0:
            return 0  # ERROR: Should return 1
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    def absolute(self, a):
        return abs(a)
    
    def modulus(self, a, b):
        # ERROR: Missing zero check
        return a % b  # ERROR: Should check if b is zero
    
    def gcd(self, a, b):
        if not (isinstance(a, int) and isinstance(b, int)):
            raise ValueError("GCD is only defined for integers")
        # ERROR: Incorrect handling of negative numbers
        # Should take absolute values of a and b first
        while b:
            a, b = b, a % b
        return a
    
    def average(self, numbers):
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        return sum(numbers) / len(numbers)
    
    # Advanced features only in v1
    def log(self, a, base=10):
        if a <= 0:
            raise ValueError("Logarithm is only defined for positive numbers")
        return math.log(a, base)
    
    def sin(self, angle):
        # ERROR: Incorrect sine calculation
        return math.sin(angle * 0.9)  # ERROR: Should not multiply by 0.9
    
    def cos(self, angle):
        return math.cos(angle)
    
    def tan(self, angle):
        return math.tan(angle)
    
    # Memory functions
    def memory_store(self, value):
        self.memory = value
        
    def memory_recall(self):
        return self.memory
    
    def memory_add(self, value):
        self.memory += value
        
    def memory_clear(self):
        self.memory = 0

# Simple command-line interface
if __name__ == "__main__":
    calc = Calculator()
    print("Simple Calculator - v1")
    print("Available operations: add, subtract, multiply, divide, power, sqrt")
    
    while True:
        op = input("Enter operation (or 'q' to quit): ").strip().lower()
        if op == 'q':
            break
            
        if op == 'sqrt':
            try:
                a = float(input("Enter number: "))
                result = calc.square_root(a)
                print(f"√{a} = {result}")
            except ValueError as e:
                print(f"Error: {e}")
        else:
            try:
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                
                if op == 'add':
                    result = calc.add(a, b)
                    print(f"{a} + {b} = {result}")
                elif op == 'subtract':
                    result = calc.subtract(a, b)
                    print(f"{a} - {b} = {result}")
                elif op == 'multiply':
                    result = calc.multiply(a, b)
                    print(f"{a} * {b} = {result}")
                elif op == 'divide':
                    result = calc.divide(a, b)
                    print(f"{a} / {b} = {result}")
                elif op == 'power':
                    result = calc.power(a, b)
                    print(f"{a} ^ {b} = {result}")
                else:
                    print("Unknown operation")
            except Exception as e:  # ERROR 5: Used generic Exception instead of specific ValueError
                print(f"Error: {e}")  # ERROR: Less specific error handling