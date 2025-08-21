"""Tests for the contents of loading_tracks.py."""

import re
from pathlib import Path

import numpy as np
import polars as pl
import polars.testing
import pytest

import pegasustools as pt


def test_no_track_dat_found() -> None:
    """Test that collate_tracks_from_ascii raises when no .track.dat file is found."""
    source_directory = Path(__file__).parent.resolve()

    err_msg = f"No .track.dat files found in {source_directory}"
    with pytest.raises(FileNotFoundError, match=re.escape(err_msg)):
        pt.collate_tracks_from_ascii(
            num_processes=1,
            source_dir=source_directory,
            destination_dir=source_directory,
        )


def test_collate_tracks_from_ascii_no_species() -> None:
    """Test the collate_tracks_from_binary function."""
    # Setup paths
    source_directory = (
        Path(__file__).parent.resolve()
        / "data"
        / "test_collate_tracks_from_ascii_no_species"
    )
    parquet_directory = source_directory / "parquet"
    source_directory.mkdir(exist_ok=True)
    parquet_directory.mkdir(exist_ok=True)

    # Generate test data1
    particle_id_max = 4
    block_id_max = 4
    num_files = particle_id_max * block_id_max
    unconcat_fid_data = []
    counter = 0
    for particle_id in range(particle_id_max):
        for block_id in range(block_id_max):
            unconcat_fid_data.append(
                generate_random_track_ascii(
                    source_directory,
                    particle_id,
                    block_id,
                    seed=42 + counter,
                )
            )
            counter += 1

    fiducial_data = pl.concat(unconcat_fid_data)

    # Compute global IDs
    n_particles = len(fiducial_data["particle_id"].unique())
    fiducial_data = fiducial_data.with_columns(
        particle_id=(pl.col("particle_id") + (pl.col("block_id") * (n_particles)))
    )
    # Sort Test Data
    fiducial_data = fiducial_data.sort(["particle_id", "time"])

    # Compute delta mu
    fiducial_data = fiducial_data.with_columns(
        delta_mu_abs=pl.when(pl.col("particle_id") == pl.col("particle_id").shift())
        .then((pl.col("mu") - pl.col("mu").shift()).abs())
        .otherwise(None)
    )

    # Run the code to test
    num_procs = min(num_files, 12)
    pt.collate_tracks_from_ascii(
        num_processes=num_procs,
        source_dir=source_directory,
        destination_dir=parquet_directory,
    )
    test_data = pl.read_parquet(parquet_directory).sort(["particle_id", "time"])

    # Verify the results. Note the high relative error tolerance to account for lost
    # precision going to/from ASCII
    polars.testing.assert_frame_equal(test_data, fiducial_data, rel_tol=1.85e-02)

    # Cleanup the files created
    [f.unlink() for f in source_directory.glob("*.track.dat")]  # type: ignore[func-returns-value]
    [f.unlink() for f in parquet_directory.glob("*.parquet")]  # type: ignore[func-returns-value]


def test_collate_tracks_from_ascii_with_species() -> None:
    """Test the collate_tracks_from_binary function."""
    # Setup paths
    source_directory = (
        Path(__file__).parent.resolve()
        / "data"
        / "test_collate_tracks_from_ascii_with_species"
    )
    parquet_directory = source_directory / "parquet"
    source_directory.mkdir(exist_ok=True)
    parquet_directory.mkdir(exist_ok=True)

    # Generate test data1
    particle_id_max = 4
    block_id_max = 4
    species_ids = ["p", "m00", "m01", "m02"]
    num_files = particle_id_max * block_id_max
    unconcat_fid_data = []
    counter = 0
    for species_id in species_ids:
        for particle_id in range(particle_id_max):
            for block_id in range(block_id_max):
                unconcat_fid_data.append(
                    generate_random_track_ascii(
                        source_directory,
                        particle_id,
                        block_id,
                        species_id=species_id,
                        seed=42 + counter,
                    )
                )
                counter += 1

    fiducial_data = pl.concat(unconcat_fid_data)

    # Compute global IDs
    n_particles = len(fiducial_data["particle_id"].unique())
    species_min = fiducial_data["species"].min()
    species_max = fiducial_data["species"].max()
    n_species = species_max - species_min + 1
    fiducial_data = fiducial_data.with_columns(
        particle_id=(
            (pl.col("species") - species_min)
            + pl.col("particle_id") * n_species
            + pl.col("block_id") * n_species * n_particles
        )
    )

    # Sort Test Data
    fiducial_data = fiducial_data.sort(["particle_id", "time"])

    # Compute delta mu
    fiducial_data = fiducial_data.with_columns(
        delta_mu_abs=pl.when(pl.col("particle_id") == pl.col("particle_id").shift())
        .then((pl.col("mu") - pl.col("mu").shift()).abs())
        .otherwise(None)
    )

    # Run the code to test
    num_procs = min(num_files, 12)
    pt.collate_tracks_from_ascii(
        num_processes=num_procs,
        source_dir=source_directory,
        destination_dir=parquet_directory,
    )
    test_data = pl.read_parquet(parquet_directory).sort(["particle_id", "time"])

    # Verify the results. Note the high relative error tolerance to account for lost
    # precision going to/from ASCII
    polars.testing.assert_frame_equal(test_data, fiducial_data, rel_tol=1.85e-02)

    # Cleanup the files created
    [f.unlink() for f in source_directory.glob("*.track.dat")]  # type: ignore[func-returns-value]
    [f.unlink() for f in parquet_directory.glob("*.parquet")]  # type: ignore[func-returns-value]


def test_collate_tracks_from_binary() -> None:
    """Test the collate_tracks_from_binary function."""
    for header_type in (True, False):
        for num_columns in range(18, 24):
            # Setup paths
            source_directory = (
                Path(__file__).parent.resolve()
                / "data"
                / "test_collate_tracks_from_binary"
            )
            parquet_directory = source_directory / "parquet"
            source_directory.mkdir(exist_ok=True)
            parquet_directory.mkdir(exist_ok=True)

            # Generate test data
            num_files = 3
            fiducial_data = pl.concat(
                [
                    generate_random_track_binary(
                        source_directory / f"test_file_{i}.track_mpiio_optimized",
                        num_columns=num_columns,
                        seed=42 + i,
                        new_header=header_type,
                    )
                    for i in range(num_files)
                ]
            )

            # Compute global IDs
            species_min = fiducial_data["species"].min()
            n_species = len(fiducial_data["species"].unique())
            n_particles = len(fiducial_data["particle_id"].unique())
            fiducial_data = fiducial_data.with_columns(
                particle_id=(pl.col("species") - species_min)
                + (pl.col("particle_id") * n_species)
                + (pl.col("block_id") * n_species * n_particles)
            )
            # Sort Test Data
            fiducial_data = fiducial_data.sort(["particle_id", "time"])

            # Compute delta mu
            fiducial_data = fiducial_data.with_columns(
                delta_mu_abs=pl.when(
                    pl.col("particle_id") == pl.col("particle_id").shift()
                )
                .then((pl.col("mu") - pl.col("mu").shift()).abs())
                .otherwise(None)
            )

            # Run the code to test
            num_procs = min(num_files, 12)
            pt.collate_tracks_from_binary(
                num_processes=num_procs,
                source_dir=source_directory,
                destination_dir=parquet_directory,
            )
            test_data = pl.read_parquet(parquet_directory)

            # Verify the results
            polars.testing.assert_frame_equal(test_data, fiducial_data)

            # Cleanup the files created
            [f.unlink() for f in source_directory.glob("*.track_mpiio_optimized")]  # type: ignore[func-returns-value]
            [f.unlink() for f in parquet_directory.glob("*.parquet")]  # type: ignore[func-returns-value]


def generate_random_track_ascii(
    target_dir_path: Path,
    particle_id: int,
    block_id: int,
    species_id: str | None = None,
    seed: int | None = None,
) -> pl.DataFrame:
    """Generate a .track.dat ASCII file.

    Parameters
    ----------
    target_dir_path : Path
        The path to the directory to write the file to
    particle_id : int
        The particle ID
    block_id : int
        The block ID
    species_id : str, optional
        The species id, defaults to None
    seed : int | None, optional
        The seed for the PRNG, by default None

    Returns
    -------
    pl.DataFrame
        The data written to the ASCII file. Note that errors up to 7 ULP have been
        observed in the write/read process.
    """
    # Setup PRNG
    rng = np.random.default_rng(seed)

    header = (
        f"# Pegasus++ track data for particle with id={particle_id} and mid={block_id}\n"  # noqa: E501
        "# [1]=time     [2]=x1       [3]=x2       [4]=v1       [5]=v2       [6]=v3       [7]=B1       [8]=B2       [9]=B3       [10]=E1       [11]=E2       [12]=E3       [13]=U1       [14]=U2       [15]=U3       [16]=dens\n"  # noqa: E501
    )

    # Figure out the species ID
    species_moniker = "" if species_id is None else f".{species_id}"
    if species_id in [None, "p"]:
        species_id_int = 0
    else:
        assert isinstance(species_id, str)
        species_id_int = int(species_id[1:]) + 1

    # Open file
    file_path = (
        target_dir_path
        / f"test_file{species_moniker}.0{particle_id}.0000{block_id}.track.dat"
    )
    with file_path.open("w") as track_file:
        # Write header
        track_file.write(header)

        # Generate random data
        width = 16
        length = 1000
        track_data = rng.uniform(-1, 1, (width - 1) * length).astype(np.float32)
        track_data = track_data.reshape((length, (width - 1)))

        # Add on the time
        times = np.linspace(0, 10000, num=length).reshape(length, 1)
        track_data = np.append(times, track_data, axis=1)

        # Simulate a restart
        restart_section = track_data[-100:, :]
        track_data_restarted = np.concatenate((track_data, restart_section), axis=0)

        # Save the data
        np.savetxt(track_file, track_data_restarted, delimiter=" ", fmt="%-8.6e")

    # Add the mu data

    # specific velocities
    specific_velocities = track_data[:, 3:6] - track_data[:, 12:15]

    # Magnetic fields
    magnetic_fields = track_data[:, 6:9]

    velocities_sqr = (specific_velocities**2).sum(axis=1)
    magnetic_magnitude = np.sqrt((magnetic_fields**2).sum(axis=1))

    # specific field-parallel velocity
    velocity_prl = (specific_velocities * magnetic_fields).sum(
        axis=1
    ) / magnetic_magnitude

    # mu invariant
    mu = 0.5 * (velocities_sqr - velocity_prl**2) / magnetic_magnitude

    track_data = np.hstack((track_data, mu.reshape(len(mu), 1)))

    # ===== Convert to dataframe =====
    float_t = pl.datatypes.Float32
    column_schema = [
        ("time", float_t),
        ("x1", float_t),
        ("x2", float_t),
        ("v1", float_t),
        ("v2", float_t),
        ("v3", float_t),
        ("B1", float_t),
        ("B2", float_t),
        ("B3", float_t),
        ("E1", float_t),
        ("E2", float_t),
        ("E3", float_t),
        ("U1", float_t),
        ("U2", float_t),
        ("U3", float_t),
        ("dens", float_t),
        ("mu", float_t),
    ]

    track_data_df = pl.from_numpy(track_data, schema=column_schema)
    track_data_df = track_data_df.insert_column(
        0, pl.lit(species_id_int).alias("species")
    )
    track_data_df = track_data_df.insert_column(0, pl.lit(block_id).alias("block_id"))
    track_data_df = track_data_df.insert_column(
        0, pl.lit(particle_id).alias("particle_id")
    )

    return track_data_df  # noqa: RET504


def generate_random_track_binary(  # noqa: PLR0915, C901
    file_path: Path,
    num_columns: int,
    seed: int | None = None,
    *,
    new_header: bool = False,
) -> pl.DataFrame:
    """Generate a .track.dat ASCII file.

    Parameters
    ----------
    file_path : Path
        The path to write the file to
    num_columns : int
        The number of columns to write
    seed : int | None, optional
        The seed for the PRNG, by default None
    new_header: bool, optional
        Whether to use the old header or the new header that includes the column names.

    Returns
    -------
    pl.DataFrame
        The data written to the binary file.
    """
    # Setup PRNG
    rng = np.random.default_rng(seed)

    # Setup column names
    int_t = pl.datatypes.Int64
    float_t = pl.datatypes.Float64
    column_schema = [
        ("particle_id", int_t),
        ("block_id", int_t),
        ("species", int_t),
        ("time", float_t),
        ("x1", float_t),
        ("x2", float_t),
        ("x3", float_t),
        ("v1", float_t),
        ("v2", float_t),
        ("v3", float_t),
        ("B1", float_t),
        ("B2", float_t),
        ("B3", float_t),
        ("E1", float_t),
        ("E2", float_t),
        ("E3", float_t),
        ("U1", float_t),
        ("U2", float_t),
        ("U3", float_t),
        ("dens", float_t),
        ("forcing1", float_t),
        ("forcing2", float_t),
        ("forcing3", float_t),
        ("mu", float_t),
    ]

    match num_columns:
        case 18:  # 1D no forcing
            column_schema.remove(("x2", float_t))
            column_schema.remove(("x3", float_t))
            column_schema.remove(("forcing1", float_t))
            column_schema.remove(("forcing2", float_t))
            column_schema.remove(("forcing3", float_t))
        case 19:  # 2D no forcing
            column_schema.remove(("x3", float_t))
            column_schema.remove(("forcing1", float_t))
            column_schema.remove(("forcing2", float_t))
            column_schema.remove(("forcing3", float_t))
        case 20:  # 3D no forcing
            column_schema.remove(("forcing1", float_t))
            column_schema.remove(("forcing2", float_t))
            column_schema.remove(("forcing3", float_t))
        case 21:  # 1D with forcing
            column_schema.remove(("x2", float_t))
            column_schema.remove(("x3", float_t))
        case 22:  # 2D with forcing
            column_schema.remove(("x3", float_t))
        case 23:  # 3D with forcing
            pass

    # Open file
    with file_path.open("wb") as track_file:
        # Write header
        time = rng.uniform(0, 1000, 1)[0]
        header = f"Particle track output function at time = {time}\n"
        track_file.write(header.encode("ascii"))

        if new_header:
            column_names = "   ".join([column_schema[i][0] for i in range(num_columns)])
            track_file.write(f"Number of variables = {num_columns}\n".encode("ascii"))
            track_file.write(f"Variables:   {column_names}\n".encode("ascii"))

        # Generate random data
        length = 1000
        track_data = rng.uniform(-1, 10, num_columns * length)
        track_data = track_data.reshape((length, num_columns))

        # Modify the three id columns
        track_data[:, 0] = np.floor(track_data[:, 0]) + 0.001
        track_data[:, 1] = np.floor(track_data[:, 1]) + 0.001
        track_data[:, 2] = np.floor(track_data[:, 2]) + 0.001

        # Save the data
        track_data.tofile(track_file)

    # ===== Add the mu data =====

    # Compute v, B, and U indices.
    v_start = 7
    b_start = 10
    u_start = 16
    match num_columns:
        case 18 | 21:  # 1D
            v_start = v_start - 2
            b_start = b_start - 2
            u_start = u_start - 2
        case 19 | 22:  # 2D
            v_start = v_start - 1
            b_start = b_start - 1
            u_start = u_start - 1
        case 20 | 23:  # 3D
            pass

    # specific velocities
    specific_velocities = (
        track_data[:, v_start : v_start + 3] - track_data[:, u_start : u_start + 3]
    )

    # Magnetic fields
    magnetic_fields = track_data[:, b_start : b_start + 3]

    velocities_sqr = (specific_velocities**2).sum(axis=1)
    magnetic_magnitude = np.sqrt((magnetic_fields**2).sum(axis=1))

    # specific field-parallel velocity
    velocity_prl = (specific_velocities * magnetic_fields).sum(
        axis=1
    ) / magnetic_magnitude

    # mu invariant
    mu = 0.5 * (velocities_sqr - velocity_prl**2) / magnetic_magnitude

    track_data = np.hstack((track_data, mu.reshape(len(mu), 1)))

    # ===== Convert to dataframe =====
    return pl.from_numpy(track_data, schema=column_schema)
