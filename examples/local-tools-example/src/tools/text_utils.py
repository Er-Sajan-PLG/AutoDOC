"""Pure bounded text operation."""

def uppercase(value):
    if not isinstance(value, str) or len(value) > 1024:
        raise ValueError('text.upper requires at most 1024 characters')
    return value.upper()
