from functools import wraps


def calculate_coordinates(func):
    """
    Decorator to recalculate spatial properties after a method call.
    This is useful for methods that modify the geometry of a component.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_coordinates()
        return result
    return wrapper


def calculate_areas(func):
    """
    Decorator to recalculate areas after a method call.
    This is useful for methods that modify the geometry of a component.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_coordinates()
            self._calculate_areas()
        return result
    return wrapper


def calculate_volumes(func):
    """
    Decorator to recalculate volumes after a method call.
    This is useful for methods that modify the geometry of a component.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if hasattr(self, '_update_properties') and self._update_properties:
            self._calculate_bulk_properties()
            self._calculate_coordinates()
        return result
    return wrapper

