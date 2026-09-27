"""Pure bounded arithmetic."""

def add(a, b):
    if type(a) is not int or type(b) is not int:
        raise ValueError('math.add requires two integers')
    return a + b
