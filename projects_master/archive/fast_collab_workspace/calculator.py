"""
Simple Calculator Module

Architecture:
- Main Calculator class with basic operations
- Each operation as a separate method for modularity
- Error handling for division by zero and invalid inputs
- Support for basic operations: add, subtract, multiply, divide
"""

class Calculator:
    """Simple calculator with basic arithmetic operations"""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers"""
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b with zero division protection"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def calculate(self, operation: str, a: float, b: float) -> float:
        """
        Perform calculation based on operation string
        
        Args:
            operation: One of '+', '-', '*', '/'
            a: First number
            b: Second number
            
        Returns:
            Result of the calculation
            
        Raises:
            ValueError: For invalid operation or division by zero
        """
        operations = {
            '+': self.add,
            '-': self.subtract,
            '*': self.multiply,
            '/': self.divide
        }
        
        if operation not in operations:
            raise ValueError(f"Invalid operation: {operation}")
        
        return operations[operation](a, b)


def simple_calculator(expression: str) -> float:
    """
    Parse and evaluate a simple expression like "2 + 3"
    
    Args:
        expression: String containing number operator number
        
    Returns:
        Result of the calculation
        
    Example:
        >>> simple_calculator("2 + 3")
        5.0
    """
    parts = expression.strip().split()
    
    if len(parts) != 3:
        raise ValueError("Expression must be in format: number operator number")
    
    try:
        a = float(parts[0])
        operator = parts[1]
        b = float(parts[2])
    except (ValueError, IndexError):
        raise ValueError("Invalid expression format")
    
    calc = Calculator()
    return calc.calculate(operator, a, b)


if __name__ == "__main__":
    calc = Calculator()
    
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"10 - 4 = {calc.subtract(10, 4)}")
    print(f"5 * 6 = {calc.multiply(5, 6)}")
    print(f"15 / 3 = {calc.divide(15, 3)}")
    
    print(f"\nUsing simple_calculator function:")
    print(f"simple_calculator('10 + 5') = {simple_calculator('10 + 5')}")
    print(f"simple_calculator('20 / 4') = {simple_calculator('20 / 4')}")