"""Test the contents of mpl_setup.py."""

import matplotlib as mpl
import numpy as np

import pegasustools as pt  # noqa: F401


def test_hawley_cmap() -> None:
    """Test that the Hawley colormap is working as intended."""
    # Test that the colormap has been registered with matplotlib
    assert "hawley" in mpl.colormaps

    # Test that the colormap that has been registered is correct by sampling some colors
    fiducial_colors = (
        (
            np.float64(0.0),
            np.float64(0.0),
            np.float64(0.4980392156862745),
            np.float64(1.0),
        ),
        (
            np.float64(0.0),
            np.float64(0.011626297577854671),
            np.float64(0.9940945790080739),
            np.float64(1.0),
        ),
        (
            np.float64(0.0),
            np.float64(1.0),
            np.float64(1.0),
            np.float64(1.0),
        ),
        (
            np.float64(0.5078200692041522),
            np.float64(0.5078200692041522),
            np.float64(0.4960553633217993),
            np.float64(1.0),
        ),
        (
            np.float64(1.0),
            np.float64(1.0),
            np.float64(0.0),
            np.float64(1.0),
        ),
        (
            np.float64(0.9944636678200689),
            np.float64(0.0),
            np.float64(0.0),
            np.float64(1.0),
        ),
        (
            np.float64(0.5294117647058824),
            np.float64(0.0),
            np.float64(0.0),
            np.float64(1.0),
        ),
    )
    positions = np.linspace(0, 1, 7)
    for i, pos in enumerate(positions):
        assert mpl.colormaps["hawley"](pos) == fiducial_colors[i]
