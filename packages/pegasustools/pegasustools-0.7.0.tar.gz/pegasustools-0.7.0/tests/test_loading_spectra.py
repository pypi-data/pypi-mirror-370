"""Tests for the contents of loading_spectra.py."""

import re
from pathlib import Path

import numpy as np
import polars as pl
import polars.testing
import pytest

import pegasustools as pt


def test_PegasusSpectralData_init() -> None:
    """Test pt.PegasusSpectralData constructor."""
    # Setup path
    file_path = (
        Path(__file__).parent.resolve() / "data" / "test_PegasusSpectralData.spec"
    )

    for header_type in (True, False):
        # Create the file
        time, fiducial_data, meshblock_locations = generate_random_spec_file(
            file_path,
            seed=42,
            num_meshblocks=7,
            new_header=header_type,
        )

        # Load test data
        test = pt.PegasusSpectralData(file_path)

        # Verify the metadata
        assert time == test.time
        assert test.n_prp == 200
        assert test.n_prl == 400
        assert test.max_w_prp == 4.0
        assert test.max_w_prl == 4.0

        # Verify the spectra
        np.testing.assert_array_max_ulp(fiducial_data, test.data, maxulp=0)

        # Verify the meshblock locations
        polars.testing.assert_frame_equal(
            meshblock_locations, test.meshblock_locations, abs_tol=0.0
        )


def test_PegasusSpectralData_file_wrong_shape() -> None:
    """Test pt.PegasusSpectralData if the file is the wrong shape."""
    # Setup path
    file_path = (
        Path(__file__).parent.resolve()
        / "data"
        / "test_PegasusSpectralDat_wrong_shape.spec"
    )

    # Create the file
    _ = generate_random_spec_file(file_path, seed=42, num_meshblocks=7)

    n_prp = 17
    err_msg = (
        f"The file {file_path} does not have the right number of "
        "elements for the values of self.__n_prl = 400 and "
        f"self.__n_prp = {n_prp} provided."
    )
    with pytest.raises(ValueError, match=re.escape(err_msg)):
        _ = pt.PegasusSpectralData(file_path, n_prp=n_prp)


def generate_random_spec_file(
    file_path: Path,
    num_meshblocks: int,
    seed: int | None = None,
    num_parallel: int = 400,
    num_perpendicular: int = 200,
    *,
    new_header: bool = False,
) -> tuple[float, np.typing.NDArray[np.float64], pl.DataFrame]:
    """Write a .spec file with random data for testing.

    Parameters
    ----------
    file_path : Path
        The path to the file to write.
    num_meshblocks : int
        The number of meshblocks
    seed : int | None, optional
        The seed for the PRNG, by default None which uses system entropy.
    num_parallel : int, optional
        n_prl from the peginput file, by default 400
    num_perpendicular : int, optional
        n_prp from the peginput file, by default 200
    new_header: bool, optional
        Whether to use the old header or the new header that includes n_prp, n_prl,
        w_prp_max, w_prl_max.

    Returns
    -------
    tuple[float, np.typing.NDArray[np.float64]]
        _description_
    """
    # Open file
    with file_path.open("wb") as spec_file:
        # Setup PRNG
        rng = np.random.default_rng(seed)

        # Write header
        time = rng.random()
        spec_file.write(
            (f"Particle distribution function at time = {time}\n").encode("ascii")
        )
        if new_header:
            spec_file.write(
                f"Histogram size in wprl = {num_parallel}\n".encode("ascii")
            )
            spec_file.write(
                f"Histogram size in wprp = {num_perpendicular}\n".encode("ascii")
            )
            spec_file.write("Max value of wprl/vth0 = 4\n".encode("ascii"))
            spec_file.write("Max value of wprp/vth0 = 4\n".encode("ascii"))

        # Generate random data
        header_size = 6
        spec_data = rng.random(
            (num_meshblocks, header_size + num_perpendicular * num_parallel),
            dtype=np.float64,
        )

        # Save the data
        spec_data.flatten().tofile(spec_file)

        # trim off the header and reshape to the actual shape that the loader
        # will return
        headers = spec_data[:, :header_size]
        spec_data = spec_data[:, header_size:]
        spec_data = spec_data.reshape((num_meshblocks, num_perpendicular, num_parallel))

        # Create the meshblock header dataframe
        meshblock_locations = pl.from_numpy(
            headers,
            schema=("x1min", "x1max", "x2min", "x2max", "x3min", "x3max"),
        )

    return time, spec_data, meshblock_locations
