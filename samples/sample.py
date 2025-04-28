# Fibonacci generator using yield
def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b


# List comprehensions example
even_squares = [x**2 for x in range(10) if x % 2 == 0]
