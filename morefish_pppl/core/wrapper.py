import functools
import warnings

def deprecated(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(f"Call to deprecated function {func.__name__}.", category=DeprecationWarning)
        return func(*args, **kwargs)
    return wrapper

@deprecated
def old_function(x, y):
    return x + y

# Test the deprecated function
result = old_function(3, 4)
print(result)