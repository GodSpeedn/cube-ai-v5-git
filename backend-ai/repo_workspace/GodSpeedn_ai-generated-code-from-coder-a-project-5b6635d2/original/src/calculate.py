def calculate(operation, num1, num2):
    """
    Performs a basic arithmetic operation on two numbers.

    Args:
        operation (str): The operation to perform ('add', 'subtract', 'multiply', 'divide').
        num1 (float or int): The first number.
        num2 (float or int): The second number.

    Returns:
        float or int: The result of the operation.

    Raises:
        ValueError: If an invalid operation is provided or division by zero occurs.
    """
    if operation == 'add':
        return num1 + num2
    elif operation == 'subtract':
        return num1 - num2
    elif operation == 'multiply':
        return num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            raise ValueError("Cannot divide by zero.")
        return num1 / num2
    else:
        raise ValueError(f"Invalid operation: '{operation}'. Supported operations are 'add', 'subtract', 'multiply', 'divide'.")