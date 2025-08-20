"""
Basic mathematical operations
"""
import requests

def add(a, b):
    """
    Add two numbers.
    
    Args:
        a (int|float): First number
        b (int|float): Second number
        
    Returns:
        int|float: Sum of a and b
        
    Example:
        >>> add(2, 3)
        5
    """
    return a + b


def subtract(a, b):
    """
    Subtract second number from first.
    
    Args:
        a (int|float): First number
        b (int|float): Second number
        
    Returns:
        int|float: Difference of a and b
    """
    return a - b


def multiply(a, b):
    """
    Multiply two numbers.
    
    Args:
        a (int|float): First number
        b (int|float): Second number
        
    Returns:
        int|float: Product of a and b
    """
    return a * b


def divide(a, b):
    """
    Divide first number by second.
    
    Args:
        a (int|float): Dividend
        b (int|float): Divisor
        
    Returns:
        float: Quotient of a and b
        
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def power(base, exponent):
    """
    Raise base to the power of exponent.
    
    Args:
        base (int|float): Base number
        exponent (int|float): Exponent
        
    Returns:
        int|float: base raised to the power of exponent
    """
    return base ** exponent