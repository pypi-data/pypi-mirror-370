"""Copyright (c) 2025 Robert Caddy. All rights reserved.

PegasusTools: Analysis package for the Pegasus PIC code.
"""

# Import all relevant modules into the pegasustools namespacess
from pegasustools.loading_hst import load_hst_file
from pegasustools.loading_nbf import PegasusNBFData
from pegasustools.loading_spectra import PegasusSpectralData
from pegasustools.loading_tracks import (
    collate_tracks_from_ascii,
    collate_tracks_from_binary,
)
from pegasustools.mpl_setup import _register_hawley_colormap
from pegasustools.pt_logging import setup_pt_logger

# Set version
from ._version import version as __version__

# Setup what gets imported with import *
__all__ = [
    "PegasusNBFData",
    "PegasusSpectralData",
    "__version__",
    "collate_tracks_from_ascii",
    "collate_tracks_from_binary",
    "load_hst_file",
    "setup_pt_logger",
]

# Create and register the hawley colormap
_register_hawley_colormap()
