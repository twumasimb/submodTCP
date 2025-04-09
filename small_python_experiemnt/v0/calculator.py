# v0/calculator.py - Original calculator implementation

class Calculator:
    def __init__(self):
        self.result = 0
        
    def add(self, a, b):
        return a + b
        
    def subtract(self, a, b):
        return a - b
        
    def multiply(self, a, b):
        return a * b
        
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
        
    def power(self, a, b):
        return a ** b
        
    def square_root(self, a):
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return a ** 0.5

    def factorial(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError("Factorial is only defined for non-negative integers")
        if n == 0:
            return 1
        result = 1
        for i in range(1, n + 1):
            result *= i
        return result
    
    def absolute(self, a):
        return abs(a)
    
    def modulus(self, a, b):
        if b == 0:
            raise ValueError("Cannot calculate modulus with divisor zero")
        return a % b
    
    def gcd(self, a, b):
        if not (isinstance(a, int) and isinstance(b, int)):
            raise ValueError("GCD is only defined for integers")
        a, b = abs(a), abs(b)
        while b:
            a, b = b, a % b
        return a
    
    def average(self, numbers):
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        return sum(numbers) / len(numbers)

# Simple command-line interface
if __name__ == "__main__":
    calc = Calculator()
    print("Simple Calculator - v0")
    print("Available operations: add, subtract, multiply, divide, power, sqrt, factorial, absolute, modulus, gcd, average")
    
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
        elif op == 'factorial':
            try:
                n = int(input("Enter number: "))
                result = calc.factorial(n)
                print(f"{n}! = {result}")
            except ValueError as e:
                print(f"Error: {e}")
        elif op == 'absolute':
            try:
                a = float(input("Enter number: "))
                result = calc.absolute(a)
                print(f"|{a}| = {result}")
            except ValueError as e:
                print(f"Error: {e}")
        elif op == 'modulus':
            try:
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                result = calc.modulus(a, b)
                print(f"{a} % {b} = {result}")
            except ValueError as e:
                print(f"Error: {e}")
        elif op == 'gcd':
            try:
                a = int(input("Enter first number: "))
                b = int(input("Enter second number: "))
                result = calc.gcd(a, b)
                print(f"GCD({a}, {b}) = {result}")
            except ValueError as e:
                print(f"Error: {e}")
        elif op == 'average':
            try:
                numbers = list(map(float, input("Enter numbers separated by space: ").split()))
                result = calc.average(numbers)
                print(f"Average = {result}")
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
            except ValueError as e:
                print(f"Error: {e}")