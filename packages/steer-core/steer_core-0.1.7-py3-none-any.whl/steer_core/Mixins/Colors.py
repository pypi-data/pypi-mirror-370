import numpy as np
import plotly.colors as pc

import pandas as pd
import numpy as np

class ColorMixin:
    """
    A class to manage colors, including conversion between hex and RGB formats,
    and generating color gradients.
    """
    @staticmethod
    def rgb_tuple_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    @staticmethod
    def get_colorway(color1, color2, n):
        """
        Generate a list of n hex colors interpolated between two HTML hex colors.

        Parameters
        ----------
        color1 : str
            The first color in HTML hex format (e.g., '#ff0000').
        color2 : str
            The second color in HTML hex format (e.g., '#0000ff').
        n : int
            The number of colors to generate in the gradient.
        """
        # Convert hex to RGB (0–255)
        rgb1 = np.array(pc.hex_to_rgb(color1))
        rgb2 = np.array(pc.hex_to_rgb(color2))

        # Interpolate and convert to hex
        colors = [
            ColorMixin.rgb_tuple_to_hex(tuple(((1 - t) * rgb1 + t * rgb2).astype(int)))
            for t in np.linspace(0, 1, n)
        ]

        return colors

