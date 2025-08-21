"""Tools for setting up matplotlib for plotting Pegasus++ data."""

import matplotlib as mpl
import numpy as np


def _register_hawley_colormap() -> None:
    """Create and register the Hawley color map.

    This function computes the colormap created by John Hawley and registers it with
    matplotlib under the name 'hawley'.
    """
    # Compute the colors to use
    color_indices = [
        (0, 0, 127),
        (0, 3, 255),
        (0, 255, 255),
        (128, 128, 128),
        (255, 255, 0),
        (255, 0, 0),
        (135, 0, 0),
    ]

    color_range = np.linspace(0, 1, 256)

    colors = [
        (color_range[idx[0]], color_range[idx[1]], color_range[idx[2]])
        for idx in color_indices
    ]

    # Create the colormap dictionary
    positions = np.linspace(0, 1, len(colors))
    cmap_dict: dict[str, list[tuple[float, float, float]]] = {
        "red": [],
        "green": [],
        "blue": [],
    }
    for pos, color in zip(positions, colors, strict=True):
        cmap_dict["red"].append((pos, color[0], color[0]))
        cmap_dict["green"].append((pos, color[1], color[1]))
        cmap_dict["blue"].append((pos, color[2], color[2]))

    # Convert dictionary into a colormap and register it with matplotlib
    hawley_cmap = mpl.colors.LinearSegmentedColormap("hawley", cmap_dict, 256)
    mpl.colormaps.register(cmap=hawley_cmap, force=True)
