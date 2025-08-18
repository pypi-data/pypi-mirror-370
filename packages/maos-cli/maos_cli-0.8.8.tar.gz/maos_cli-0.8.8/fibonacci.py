def fibonacci(n):
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: The position in the Fibonacci sequence (0-indexed)
    
    Returns:
        The nth Fibonacci number
    """
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


def fibonacci_sequence(count):
    """
    Generate a list of Fibonacci numbers.
    
    Args:
        count: Number of Fibonacci numbers to generate
    
    Returns:
        List of Fibonacci numbers
    """
    if count <= 0:
        return []
    
    sequence = []
    for i in range(count):
        sequence.append(fibonacci(i))
    return sequence


if __name__ == "__main__":
    print("First 10 Fibonacci numbers:")
    print(fibonacci_sequence(10))
    
    print("\nThe 20th Fibonacci number is:", fibonacci(20))