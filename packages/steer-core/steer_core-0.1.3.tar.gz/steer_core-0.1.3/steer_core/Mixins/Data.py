import numpy as np
from scipy.interpolate import PchipInterpolator


class DataMixin:
    """
    A mixin class to handle data processing and validation for electrode materials.
    Provides methods to calculate properties, check curve directions, and process half-cell curves.
    """
    @staticmethod
    def enforce_monotonicity(array: np.ndarray) -> np.ndarray:
        """
        Enforces a monotonic version of the input array.
        If the array is not monotonic, it is smoothed using cumulative max/min.
        """
        x = np.arange(len(array))
        diff = np.diff(array)

        if np.all(diff >= 0):
            return array  # Already monotonic increasing

        if np.all(diff <= 0):
            return array  # Already monotonic decreasing, reverse it

        # Determine general trend (ascending or descending)
        ascending = array[-1] >= array[0]

        # Sort by x so that PCHIP works (PCHIP requires increasing x)
        # We'll smooth the array using PCHIP, then enforce monotonicity
        interpolator = PchipInterpolator(x, array, extrapolate=False)
        new_array = interpolator(x)

        # Enforce strict monotonicity post-smoothing
        if ascending:
            new_array = np.maximum.accumulate(new_array)
        else:
            new_array = np.minimum.accumulate(new_array)

        return new_array

