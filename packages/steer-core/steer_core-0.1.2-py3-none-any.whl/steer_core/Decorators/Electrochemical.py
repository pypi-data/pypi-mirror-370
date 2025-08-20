from functools import wraps

def calculate_half_cell_curve(func):
    """
    Decorator to recalculate half-cell curve properties after a method call.
    This is useful for methods that modify the half-cell curve data.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_half_cell_curve()
        return result
    return wrapper


def calculate_half_cell_curves_properties(func):
    """
    Decorator to recalculate half-cell curves properties after a method call.
    This is useful for methods that modify the half-cell curves data.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_half_cell_curves_properties()
        return result
    return wrapper
