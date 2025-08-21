"""Tests for the contents of loading_nbf.py."""

import re
import struct
from pathlib import Path

import numpy as np
import pytest

import pegasustools as pt


@pytest.mark.parametrize("dims", [1, 2, 3])
def test_PegasusNBFData(dims: int) -> None:
    """Test pt.PegasusNBFData with 1D, 2D, & 3D data."""
    # Setup paths
    file_path = (
        Path(__file__).parent.resolve() / "data" / f"test_PegasusNBFData_{dims}d.nbf"
    )

    # Create test file & nbf_data
    fiducial_data = generate_random_nbf_file(file_path, seed=42, dims=dims)

    # Load file
    test_data = pt.PegasusNBFData(file_path)

    # Compare header data
    np.testing.assert_array_max_ulp(fiducial_data.time, test_data.time, maxulp=3)
    assert fiducial_data.big_endian == test_data.big_endian
    assert fiducial_data.num_meshblocks == test_data.num_meshblocks
    assert fiducial_data.list_of_variables == test_data.list_of_variables
    assert fiducial_data.mesh_params == test_data.mesh_params
    assert fiducial_data.meshblock_params == test_data.meshblock_params

    # Compare field data
    for key in test_data.data:
        fid_field = fiducial_data.data[key]
        test_field = test_data.data[key]

        # check the sizes are the same
        assert fid_field.shape == test_field.shape

        # check that all elements are correct
        np.testing.assert_array_max_ulp(np.squeeze(fid_field), test_field, maxulp=0)


def test_PegasusNBFData_too_small() -> None:
    """Test for the exception that should appear if the file is too small."""
    # Setup paths
    file_path = Path(__file__).parent.resolve() / "data" / "too_short.nbf"
    with file_path.open("wb") as file:
        file.write(b"not\nenough\nlines")

    err_msg = f"{file_path} is not a Pegasus++ NBF file."
    with pytest.raises(OSError, match=re.escape(err_msg)):
        pt.PegasusNBFData(file_path)


def test_PegasusNBFData_wrong_first_line() -> None:
    """Test for the incorrect first line exception."""
    # Setup paths
    file_path = Path(__file__).parent.resolve() / "data" / "too_short.nbf"
    with file_path.open("wb") as file:
        file.write(
            b"line 1\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9\n"
        )

    err_msg = f"{file_path} is not a Pegasus++ NBF file."
    with pytest.raises(OSError, match=re.escape(err_msg)):
        pt.PegasusNBFData(file_path)


class MockPegasusNBFData:
    """Mock version of PegasusNBFData."""

    def __init__(
        self,
        time: np.float64,
        num_meshblocks: int,
        list_of_variables: list[str],
        mesh_params: dict[str, np.float32 | int],
        meshblock_params: dict[str, int],
        *,
        big_endian: bool,
    ) -> None:
        """Initialize a MockPegasusNBFData class with the header data.

        Parameters
        ----------
        time : np.float64
            The simulation time in the file.
        big_endian : bool
            True if the data is big endian, False otherwise.
        num_meshblocks : int
            The number of mesh blocks.
        list_of_variables : list[str]
            The list of variables in the NBF files.
        mesh_params : dict[str, np.float32  |  int]
            The mesh parameters.
        meshblock_params : dict[str, int]
            The mesh block parameters.
        """
        # Header variables
        self.time: np.float64 = time
        self.big_endian: bool = big_endian
        self.num_meshblocks: int = num_meshblocks
        self.list_of_variables: list[str] = list_of_variables
        self.mesh_params: dict[str, np.float32 | int] = mesh_params
        self.meshblock_params: dict[str, int] = meshblock_params

        # The dictionary that actually stores the data
        self.data: dict[str, np.typing.NDArray[np.float32]] = {}

        # Setup nbf_data.data member. Note that by the end of the reading these axis
        # will be swapped to x1, x2, x3
        data_shape: tuple[int, int, int] = (
            int(self.mesh_params["nx3"]),
            int(self.mesh_params["nx2"]),
            int(self.mesh_params["nx1"]),
        )
        for key in self.list_of_variables:
            self.data[key] = np.empty(data_shape, dtype=np.float32)


def generate_random_nbf_file(
    path: Path, seed: int | None = None, dims: int = 3
) -> MockPegasusNBFData:
    """Create a MockPegasusNBFData object filled with random data & write it to a file.

    Only intended to help with testing.

    Parameters
    ----------
    path : Path
        The filepath to write the new .nbf file to
    seed : int | None, optional
        The seed to use for the PRNG, by default None which will use OS generated
        entropy
    dims : int, optional
        The number of dimensions of the data, by default 3

    Returns
    -------
    MockPegasusNBFData
        The MockPegasusNBFData object that was written to the file.
    """
    # Setup PRNG
    rng = np.random.default_rng(seed)

    # Determine the number of dimensions
    meshblock_params = {"nx1": 32, "nx2": 16, "nx3": 64}
    if dims < 3:
        meshblock_params["nx3"] = 1
    if dims < 2:
        meshblock_params["nx2"] = 1

    meshblock_per_side = 2
    size = meshblock_per_side * np.array(
        (meshblock_params["nx1"], meshblock_params["nx2"], meshblock_params["nx3"])
    )

    num_meshblocks = int(
        (size[0] / meshblock_params["nx1"])
        * (size[1] / meshblock_params["nx2"])
        * (size[2] / meshblock_params["nx3"])
    )

    # Create header data
    time = np.float64(rng.random(dtype=np.float64))
    list_of_variables = [
        "dens",
        "mom1",
        "mom2",
        "mom3",
        "Bcc1",
        "Bcc2",
        "Bcc3",
        "Ecc1",
        "Ecc2",
        "Ecc3",
    ]
    mesh_params: dict[str, np.float32 | int] = {
        "nx1": size[0],
        "x1min": np.float32(rng.random(dtype=np.float32)),
        "x1max": np.float32(rng.random(dtype=np.float32)),
        "nx2": size[1],
        "x2min": np.float32(rng.random(dtype=np.float32)),
        "x2max": np.float32(rng.random(dtype=np.float32)),
        "nx3": size[2],
        "x3min": np.float32(rng.random(dtype=np.float32)),
        "x3max": np.float32(rng.random(dtype=np.float32)),
    }

    nbf_data = MockPegasusNBFData(
        time=time,
        big_endian=False,
        num_meshblocks=num_meshblocks,
        list_of_variables=list_of_variables,
        mesh_params=mesh_params,
        meshblock_params=meshblock_params,
    )

    # create arrays to write to .nbf file
    for key in list_of_variables:
        nbf_data.data[key] = rng.random(
            (int(mesh_params["nx1"]), int(mesh_params["nx2"]), int(mesh_params["nx3"])),
            dtype=np.float32,
        )

    create_nbf(path, nbf_data)

    return nbf_data


def create_nbf(filepath: Path, nbf_data: MockPegasusNBFData) -> None:
    """Create an NBF file from a MockPegasusNBFData object.

    This is intended solely as a tool to help with testing and, while I believe it is
    correct, it should not be used outside of testing PegasusTools.

    Parameters
    ----------
    filepath : Path
        The path to write the file to
    nbf_data : MockPegasusNBFData
        The MockPegasusNBFData object to write to the file
    """
    header = (
        f"Pegasus++ binary output at time = {nbf_data.time:.14e}\n"
        f"Big endian = {int(nbf_data.big_endian)}\n"
        f"Number of MeshBlocks = {nbf_data.num_meshblocks}\n"
        f"Number of variables = {len(nbf_data.list_of_variables)}\n"
        f"Variables:   {'   '.join(nbf_data.list_of_variables)}   \n"
        f"Mesh:   nx1={nbf_data.mesh_params['nx1']}   x1min={nbf_data.mesh_params['x1min']:.14e}   x1max={nbf_data.mesh_params['x1max']:.14e}\n"  # noqa: E501
        f"        nx2={nbf_data.mesh_params['nx2']}   x2min={nbf_data.mesh_params['x2min']:.14e}   x2max={nbf_data.mesh_params['x2max']:.14e}\n"  # noqa: E501
        f"        nx3={nbf_data.mesh_params['nx3']}   x3min={nbf_data.mesh_params['x3min']:.14e}   x3max={nbf_data.mesh_params['x3max']:.14e}\n"  # noqa: E501
        f"MeshBlock: nx1={nbf_data.meshblock_params['nx1']}   nx2={nbf_data.meshblock_params['nx2']}   nx3={nbf_data.meshblock_params['nx3']}\n"  # noqa: E501
    )

    with filepath.open(mode="wb") as nbf_file:
        # write the header
        nbf_file.write(header.encode("ascii"))

        # Loop through meshblocks and write them one at a time
        meshblock_i = int(
            nbf_data.mesh_params["nx1"] / nbf_data.meshblock_params["nx1"]
        )
        meshblock_j = int(
            nbf_data.mesh_params["nx2"] / nbf_data.meshblock_params["nx2"]
        )
        meshblock_k = int(
            nbf_data.mesh_params["nx3"] / nbf_data.meshblock_params["nx3"]
        )

        for i in range(meshblock_i):
            for j in range(meshblock_j):
                for k in range(meshblock_k):
                    # Write the header
                    meshblock_header = (
                        int(i),  # x1 coordinate of block
                        int(j),  # x2 coordinate of block
                        int(k),  # x3 coordinate of block
                        int(nbf_data.meshblock_params["nx1"]),  # x1 size of block
                        np.float32(0.0),  # min x1
                        np.float32(0.0),  # max x1
                        int(nbf_data.meshblock_params["nx2"]),  # x2 size of block
                        np.float32(0.0),  # min x2
                        np.float32(0.0),  # max x2
                        int(nbf_data.meshblock_params["nx3"]),  # x3 size of block
                        np.float32(0.0),  # min x3
                        np.float32(0.0),  # max x3
                    )
                    nbf_file.write(struct.pack("@4i2fi2fi2f", *meshblock_header))

                    # Write the data

                    # Compute the indices to write to
                    i_start = i * nbf_data.meshblock_params["nx1"]
                    i_end = i_start + nbf_data.meshblock_params["nx1"]
                    j_start = j * nbf_data.meshblock_params["nx2"]
                    j_end = j_start + nbf_data.meshblock_params["nx2"]
                    k_start = k * nbf_data.meshblock_params["nx3"]
                    k_end = k_start + nbf_data.meshblock_params["nx3"]

                    for key in nbf_data.list_of_variables:
                        subset = nbf_data.data[key][
                            i_start:i_end, j_start:j_end, k_start:k_end
                        ]
                        subset = np.swapaxes(subset, 0, 2)
                        subset.flatten().tofile(nbf_file)
