from functools import wraps

def calculate_bulk_properties(func):
    """
    Decorator to recalculate bulk properties after a method call.
    This is useful for methods that modify the material properties.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_bulk_properties()
        return result
    return wrapper


def calculate_all_properties(func):
    """
    Decorator to recalculate both spatial and bulk properties after a method call.
    This is useful for methods that modify both geometry and material properties.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_all_properties()
        return result
    return wrapper


