from functools import wraps

def calculate_weld_tab_properties(func):
    """
    Decorator to recalculate weld tab properties after a method call.
    This is useful for methods that modify the weld tab geometry or material.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_weld_tab_properties()
        return result
    return wrapper
