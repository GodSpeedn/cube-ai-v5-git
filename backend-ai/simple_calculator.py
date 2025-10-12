#!/usr/bin/env python3
"""
Simple Python Calculator
A basic calculator that can perform arithmetic operations.
"""

import sys
import re
from typing import Union, List

class SimpleCalculator:
    """A simple calculator class that can perform basic arithmetic operations."""
    
    def __init__(self):
        self.history: List[str] = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Subtract two numbers."""
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Multiply two numbers."""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero!")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def power(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """Raise a to the power of b."""
        result = a ** b
        self.history.append(f"{a} ^ {b} = {result}")
        return result
    
    def square_root(self, a: Union[int, float]) -> float:
        """Calculate square root of a number."""
        if a < 0:
            raise ValueError("Cannot calculate square root of negative number!")
        result = a ** 0.5
        self.history.append(f"√{a} = {result}")
        return result
    
    def evaluate_expression(self, expression: str) -> Union[int, float]:
        """Evaluate a mathematical expression safely."""
        # Remove whitespace
        expression = expression.replace(" ", "")
        
        # Validate expression (only allow numbers, operators, and parentheses)
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            raise ValueError("Invalid characters in expression!")
        
        try:
            # Use eval for simple expressions (in a real app, use a proper parser)
            result = eval(expression)
            self.history.append(f"{expression} = {result}")
            return result
        except ZeroDivisionError:
            raise ValueError("Cannot divide by zero!")
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()
    
    def show_menu(self):
        """Display the calculator menu."""
        print("\n" + "="*50)
        print("           SIMPLE PYTHON CALCULATOR")
        print("="*50)
        print("1. Add")
        print("2. Subtract") 
        print("3. Multiply")
        print("4. Divide")
        print("5. Power")
        print("6. Square Root")
        print("7. Evaluate Expression")
        print("8. Show History")
        print("9. Clear History")
        print("0. Exit")
        print("="*50)

def main():
    """Main calculator function."""
    calc = SimpleCalculator()
    
    print("Welcome to Simple Python Calculator!")
    
    while True:
        calc.show_menu()
        
        try:
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == "0":
                print("Thank you for using Simple Python Calculator!")
                break
            elif choice == "1":
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                result = calc.add(a, b)
                print(f"Result: {result}")
            elif choice == "2":
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                result = calc.subtract(a, b)
                print(f"Result: {result}")
            elif choice == "3":
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                result = calc.multiply(a, b)
                print(f"Result: {result}")
            elif choice == "4":
                a = float(input("Enter first number: "))
                b = float(input("Enter second number: "))
                result = calc.divide(a, b)
                print(f"Result: {result}")
            elif choice == "5":
                a = float(input("Enter base number: "))
                b = float(input("Enter exponent: "))
                result = calc.power(a, b)
                print(f"Result: {result}")
            elif choice == "6":
                a = float(input("Enter number: "))
                result = calc.square_root(a)
                print(f"Result: {result}")
            elif choice == "7":
                expression = input("Enter mathematical expression: ")
                result = calc.evaluate_expression(expression)
                print(f"Result: {result}")
            elif choice == "8":
                history = calc.get_history()
                if history:
                    print("\nCalculation History:")
                    for i, entry in enumerate(history, 1):
                        print(f"{i}. {entry}")
                else:
                    print("No calculations in history.")
            elif choice == "9":
                calc.clear_history()
                print("History cleared!")
            else:
                print("Invalid choice! Please enter a number between 0-9.")
                
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\n\nCalculator interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()

