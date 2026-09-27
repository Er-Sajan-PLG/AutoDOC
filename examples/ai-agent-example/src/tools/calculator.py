"""Bounded arithmetic on two integers, not expression evaluation."""

def add(a: int, b: int) -> int:
    """Add two integers; booleans and other inputs are not accepted."""
    if type(a) is not int or type(b) is not int:
        raise ValueError('two integers required')
    return a + b
