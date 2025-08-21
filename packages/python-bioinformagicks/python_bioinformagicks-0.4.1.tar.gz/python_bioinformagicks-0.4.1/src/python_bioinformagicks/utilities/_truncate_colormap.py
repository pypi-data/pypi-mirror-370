import matplotlib
import numpy as np

def truncate_colormap(
    cmap,
    minval: float = 0.0,
    maxval: float = 1.0,
    n: int = 100
):
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap