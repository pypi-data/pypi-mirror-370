"""Tests for the contents of loading_hst.py."""

import re
from pathlib import Path

import numpy as np
import polars as pl
import polars.testing
import pytest

import pegasustools as pt


def test_load_hst_file() -> None:
    """Test load_hst_file."""
    # Setup paths
    hst_path = Path(__file__).parent.resolve() / "data" / "test_load_hst_file.hst"

    # Mock up a .hst file
    column_header = (
        "# [1]=time     [2]=dt       [3]=mass     [4]=1-mom    [5]=2-mom    "
        "[6]=3-mom    [7]=1-KE     [8]=2-KE     [9]=3-KE     [10]=tot-E   [11]=mu"
        "      [12]=1-ME    [13]=2-ME    [14]=3-ME    [15]=etaheat [16]=nuheat  \n"
    )
    with hst_path.open("w") as hst_file:
        hst_file.write("# Athena++ history data\n")
        hst_file.write(column_header)

        # generate random data
        seed = 42
        prng = np.random.default_rng(seed)
        hst_arr = prng.uniform(-1, 1, (1000, 16)).astype(np.float32)

        # sort so that the time entries are monotonically increasing
        sort_idxs = np.argsort(hst_arr[:, 0])
        hst_arr = hst_arr[sort_idxs]

        # Save to an ASCII file
        np.savetxt(hst_file, hst_arr, delimiter=" ", fmt="% 6.5e")

    # Convert to dataframe
    schema = [name.split("=")[1] for name in column_header.split()[1:]]
    fiducial_df = pl.from_numpy(hst_arr, schema)

    # Load the data
    test_df = pt.load_hst_file(hst_path)

    # Verify correctness
    polars.testing.assert_frame_equal(test_df, fiducial_df)


def test_load_hst_file_invalid_file() -> None:
    """Test that load_hst_file raises an exception when it should."""
    # Setup paths
    hst_path = (
        Path(__file__).parent.resolve() / "data" / "test_load_hst_file_invalid_file.hst"
    )
    with hst_path.open("w") as hst_file:
        hst_file.write("# This is an invalid header\nline 2\n")

    err_msg = (
        f"The file at {hst_path} does not have the correct header to be a hst file."
    )
    with pytest.raises(RuntimeError, match=re.escape(err_msg)):
        pt.load_hst_file(hst_path)
