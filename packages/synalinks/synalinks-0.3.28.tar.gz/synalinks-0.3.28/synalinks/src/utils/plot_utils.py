# License Apache 2.0: (c) 2025 Yoan Sallami (Synalinks Team)

import numpy as np
from matplotlib import colormaps


def generate_distinct_colors(n):
    """Generate n distinct colors using a colormap.

    Args:
        n (int): The number of colors to generate
    """
    if n <= 10:
        # Use qualitative colormap for small number of categories
        cmap = colormaps["Set3"]
        colors = [cmap(i) for i in np.linspace(0, 0.9, n)]
    else:
        # Use HSV colormap for larger number of categories
        cmap = colormaps["hsv"]
        colors = [cmap(i) for i in np.linspace(0, 1, n, endpoint=False)]
    return colors
