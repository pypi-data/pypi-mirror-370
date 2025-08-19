def factorial(n):
    """Calculate the factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# Example usage
if __name__ == "__main__":
    # Test the function
    for num in [0, 1, 5, 10]:
        print(f"factorial({num}) = {factorial(num)}")