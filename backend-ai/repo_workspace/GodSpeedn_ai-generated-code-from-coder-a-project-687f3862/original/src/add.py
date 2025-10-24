def add(a, b):
    """
    Add two numbers and return the result.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Sum of a and b

    Raises:
        TypeError: If either a or b is not a number
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a + b

def subtract(a, b):
    """
    Subtract two numbers and return the result.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Result of a minus b

    Raises:
        TypeError: If either a or b is not a number
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a - b

def multiply(a, b):
    """
    Multiply two numbers and return the result.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Product of a and b

    Raises:
        TypeError: If either a or b is not a number
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    return a * b

def divide(a, b):
    """
    Divide two numbers and return the result.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        float: Result of a divided by b

    Raises:
        TypeError: If either a or b is not a number
        ZeroDivisionError: If b is zero
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b