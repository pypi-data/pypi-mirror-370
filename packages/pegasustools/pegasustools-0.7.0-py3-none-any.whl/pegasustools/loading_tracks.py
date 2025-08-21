"""Provides the utilities required to deal with particle track data."""

import concurrent.futures
import multiprocessing
import typing
from pathlib import Path
from timeit import default_timer
from typing import Any

import numpy as np
import polars as pl

from .pt_logging import setup_pt_logger


def _remove_restart_overlaps(
    overlapped_arr: np.typing.ArrayLike, time_idx: int
) -> np.typing.ArrayLike:
    mask = np.ones(overlapped_arr.shape[0], dtype="bool")
    # Generate the mask by iterating through the time array backwards and only choosing
    # rows that monotonically decrease in time
    current_min_time = np.inf
    for i, time in reversed(list(enumerate(overlapped_arr[:, time_idx]))):
        if time < current_min_time:
            current_min_time = time
        else:
            mask[i] = False

    # Mask out the overlapping data
    return overlapped_arr[mask]


def _get_ascii_particle_ids(path: Path) -> tuple[int, int, int]:
    file_name = path.stem.split(".")

    # Block ID
    block_id = int(file_name[-2])

    # Particle ID
    particle_id = int(file_name[-3])

    # Species IDs
    length_with_species = 5
    if len(file_name) == length_with_species:
        species_id_str = file_name[-4]
        if species_id_str == "p":
            species_id = 0
        elif species_id_str[0] == "m":
            # offset by 1 account for protons having ID = 0
            species_id = int(species_id_str[1:]) + 1
        else:
            msg = f"The filename {path} has an invalid species ID."
            raise ValueError(msg)
    elif len(file_name) == length_with_species - 1:
        species_id = 0
    else:
        msg = f"The file {path} name does not match an ASCII track file."
        raise ValueError(msg)

    return species_id, particle_id, block_id


def _ascii_track_reader(
    file_path: Path, particle_id_max: int, species_id_min: int, species_id_max: int
) -> pl.DataFrame:
    """Load the track data from an ascii file at file_path.

    Parameters
    ----------
    file_path : Path
        The path to the .track.dat file
    particle_id_max : int
        The maximum value of the particle ID in the entire dataset.
    species_id_min : int
        The minimum value of the species ID in the entire dataset.
    species_id_max : int
        The maximum value of the species ID in the entire dataset.
    """
    logger = setup_pt_logger()
    # ===== Load the data =====
    with file_path.open() as track_file:
        # Read the header
        header = track_file.readline().split()
        column_headers = track_file.readline().split()

        # Verify the headers
        fiducial_header_start = [
            "#",
            "Pegasus++",
            "track",
            "data",
            "for",
        ]
        if header[:5] != fiducial_header_start:
            logger.critical(
                "The file at %s is not a Pegasus++ .track.dat file.", str(file_path)
            )

        # Parse column names
        column_headers = column_headers[1:]  # cut out the comment character
        column_schema = tuple(
            (name.split("=")[-1], pl.datatypes.Float32) for name in column_headers
        )

        # Load the file
        data = np.loadtxt(track_file, dtype=np.float32)

    # ===== Look for restarts and remove the duplicated data via masking =====
    time_idx = column_schema.index(("time", pl.datatypes.Float32))
    data = _remove_restart_overlaps(data, time_idx)

    # ===== Compute mu, convert to dataframe, and compute delta mu =====
    # Compute mu
    data, column_schema = _compute_magnetic_moment(data, column_schema)

    # Convert to dataframe
    data_df = pl.from_numpy(data, schema=column_schema)

    # Compute delta mu
    data_df = data_df.with_columns(
        delta_mu_abs=(pl.col("mu") - pl.col("mu").shift()).abs()
    )

    # Determine the various particle IDs
    species_id, particle_id, block_id = _get_ascii_particle_ids(file_path)

    # Compute the global particle ID
    n_particles = particle_id_max + 1
    n_species = species_id_max - species_id_min + 1
    global_particle_id = (
        (species_id - species_id_min)
        + particle_id * n_species
        + block_id * n_species * n_particles
    )

    # Add in the ID columns
    data_df = data_df.insert_column(0, pl.lit(species_id).alias("species"))
    data_df = data_df.insert_column(0, pl.lit(block_id).alias("block_id"))
    data_df = data_df.insert_column(0, pl.lit(global_particle_id).alias("particle_id"))

    return data_df  # noqa: RET504


def _ascii_tracks_to_parquet(
    files_to_read: list[Path],
    output_directory: Path,
    particle_id_max: int,
    species_id_min: int,
    species_id_max: int,
) -> None:
    # Convert the ascii track files to parquet and get the mins & maxes for IDs
    particle_data = pl.concat(
        [
            _ascii_track_reader(f, particle_id_max, species_id_min, species_id_max)
            for f in files_to_read
        ]
    )

    # Write the dataframe to a parquet file.
    id_min = particle_data["particle_id"].min()
    id_max = particle_data["particle_id"].max()
    output_name = (
        (files_to_read[0].stem.split(".")[0]) + f"_particles_{id_min}_{id_max}.parquet"
    )
    particle_data.write_parquet(output_directory / output_name)


def _process_ascii_filenames(
    source_dir: Path, num_processes: int, max_parquet_size: int
) -> tuple[np.typing.ArrayLike, int, int, int]:
    # Setup logging
    logger = setup_pt_logger()

    # Get list of binary files
    logger.info("Gathering list of .track.dat files.")
    files_to_read = list(source_dir.glob("*.track.dat"))

    # Check that it actually found some .track.dat files
    if len(files_to_read) == 0:
        msg = f"No .track.dat files found in {source_dir}"
        raise FileNotFoundError(msg)
    logger.info("Found %i .track.dat files.", len(files_to_read))

    # Find the maximum particle ID, minimum and maximum species id
    particle_id_max = int(-1e9)
    species_id_max = int(-1e9)
    species_id_min = int(1e9)
    for path in files_to_read:
        # Get the IDs for this file
        species_id, particle_id, _ = _get_ascii_particle_ids(path)

        # Determine mins and maxes
        particle_id_max = max(particle_id_max, particle_id)
        species_id_max = max(species_id_max, species_id)
        species_id_min = min(species_id_min, species_id)

    # Sort the paths based on the global particle ID
    def global_id(file_path: Path) -> int:
        species_id, particle_id, block_id = _get_ascii_particle_ids(file_path)
        n_particles = particle_id_max + 1
        n_species = species_id_max - species_id_min + 1
        return (
            (species_id - species_id_min)
            + particle_id * n_species
            + block_id * n_species * n_particles
        )

    files_to_read = sorted(files_to_read, key=global_id)

    # Maximum file sizes
    max_parquet_size = max_parquet_size * int(1e6)  # Convert from MB to Bytes
    max_ascii_size = np.array([f.stat().st_size for f in files_to_read]).max()
    # divide by 3 to account for space savings when converting from ascii to binary
    max_ascii_size = max_ascii_size / 3

    # Determine the number of chunks so that the files aren't too large and it's an
    # exact multiple of num_processes
    chunk_size = int(max_parquet_size / max_ascii_size)
    num_chunks = int(np.ceil(len(files_to_read) / chunk_size))
    while True:
        if num_chunks % num_processes == 0:
            break
        num_chunks = num_chunks + 1

    # Split the list of files into even chunks
    file_blocks = np.array_split(np.array(files_to_read), num_chunks)

    return file_blocks, particle_id_max, species_id_min, species_id_max


def collate_tracks_from_ascii(
    num_processes: int,
    source_dir: Path,
    destination_dir: Path,
    *,
    max_parquet_size: int = 2000,
) -> None:
    """Collate the .track.dat files in a directory into ordered files.

    Parameters
    ----------
    num_processes : int
        The number of processes to use.
    source_dir : Path
        The path to the directory with the .track.dat files
    destination_dir : Path
        The path with filename where the parquet files should be created. It will be
        created if it doesn't exist.
    max_parquet_size : int, optional
        The maximum parquet file size in MB. This is only approximate and the actual
        file size might be smaller to help with load balancing. By default 2000MB
    """
    # Setup logging
    logger = setup_pt_logger()

    # Process the file names and get some basic statistics
    file_blocks, particle_id_max, species_id_min, species_id_max = (
        _process_ascii_filenames(source_dir, num_processes, max_parquet_size)
    )

    # Create destination directory if it doesn't already exist
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Spawning new processes instead of forking is required for polars
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=num_processes, mp_context=multiprocessing.get_context("spawn")
    ) as executor:
        logger.info(
            "ProcessPoolExecutor launched with %i processes. "
            "Using %i Polars threads each.",
            num_processes,
            pl.thread_pool_size(),
        )
        # Convert the binary files to parquet and get the mins & maxes for IDs
        logger.info("Starting to convert ASCII track files into parquet.")
        start = default_timer()
        futures = [
            executor.submit(
                _ascii_tracks_to_parquet,
                f,
                destination_dir,
                particle_id_max,
                species_id_min,
                species_id_max,
            )
            for f in file_blocks
        ]
        # Check for exceptions
        _ = [future.result() for future in futures]
    logger.info("Conversion complete. Elapsed time: %.2fs", default_timer() - start)


# =============================================================================
# Collating function for binary .track_mpiio_optimized files
# =============================================================================
def _binary_get_column_names_missing_header(
    num_columns: int,
) -> tuple[tuple[str, Any], ...]:
    # Determine which columns are in this dataset
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

    return tuple(column_schema)


def _binary_get_column_names_included_header(
    line_2: str, line_3: str
) -> tuple[int, tuple[tuple[str, Any], ...]]:
    # Get the number of columns
    num_columns = int(line_2.rstrip().split()[-1])

    # Get the names of the columns
    column_names = line_3.rstrip().split()[1:]

    # Build the schema
    int_t = pl.datatypes.Int64
    float_t = pl.datatypes.Float64

    # The datasets that have type int instead of float
    int_datasets = ("particle_id", "block_id", "species")

    column_schema = []
    for name in column_names:
        if name in int_datasets:
            column_schema.append((name, int_t))
        else:
            column_schema.append((name, float_t))

    return num_columns, tuple(column_schema)


def _compute_magnetic_moment(
    data: np.typing.ArrayLike,
    column_schema: tuple[tuple[str, Any], ...],
) -> tuple[np.typing.ArrayLike, tuple[tuple[str, Any], ...]]:
    """Compute the magnetic moment.

    Parameters
    ----------
    data : np.typing.ArrayLike
        The np array of data loaded from a track file
    column_schema : tuple[tuple[str, Any], ...]
        The schema of the columns. A tuple of tuples with each tuple containing the
        column name and type.

    Returns
    -------
    tuple[np.typing.ArrayLike, tuple[tuple[str, Any], ...]]
        The new dataset with mu and the schema of the columns, now with an entry for mu.
    """

    class _Wildcard:  # noqa: PLW1641
        def __eq__(self, anything: object) -> bool:
            return anything in (pl.datatypes.Float64, pl.datatypes.Float32)

    v_start = column_schema.index(("v1", _Wildcard()))
    b_start = column_schema.index(("B1", _Wildcard()))
    u_start = column_schema.index(("U1", _Wildcard()))

    # specific velocities
    specific_velocities = (
        data[:, v_start : v_start + 3] - data[:, u_start : u_start + 3]
    )

    # Magnetic fields
    magnetic_fields = data[:, b_start : b_start + 3]

    velocities_sqr = (specific_velocities**2).sum(axis=1)
    magnetic_magnitude = np.sqrt((magnetic_fields**2).sum(axis=1))

    # specific field-parallel velocity
    velocity_prl = (specific_velocities * magnetic_fields).sum(
        axis=1
    ) / magnetic_magnitude

    # mu invariant
    mu = 0.5 * (velocities_sqr - velocity_prl**2) / magnetic_magnitude

    # append mu to data
    mu = np.expand_dims(mu, axis=1)
    data = np.hstack((data, mu))

    # Expand the column nameds and schema to include mu
    dtype = column_schema[v_start][1]
    column_schema = (*column_schema, ("mu", dtype))

    return data, column_schema


def _estimate_num_rows(
    data: np.typing.ArrayLike,
) -> tuple[int, tuple[tuple[str, Any], ...]]:
    # Determine the size of each row
    abs_allowed_err = 5.0e-13
    int_to_float_offset = 0.001
    for i in range(17, 24):
        diff1 = np.abs((data[i] - np.floor(data[i])) - int_to_float_offset)
        diff2 = np.abs((data[i + 1] - np.floor(data[i + 1])) - int_to_float_offset)

        if diff1 < abs_allowed_err and diff2 < abs_allowed_err:
            num_columns = i
            break

    # Get the list of column names
    column_schema = _binary_get_column_names_missing_header(num_columns)

    return num_columns, column_schema


def _binary_track_reader(input_file_path: Path, parquet_path: Path) -> pl.DataFrame:
    """Convert binary track file to parquet file. Computes the magnetic moment too.

    Parameters
    ----------
    input_file_path : Path
        The path to the `.track_mpiio_optimized` file.
    parquet_path : Path
        The directory to write the parquet file to.

    Returns
    -------
    pl.DataFrame
        The species min & max and the particle_id max
    """
    logger = setup_pt_logger()
    logger.debug("Starting with file %s", input_file_path)

    # Open the file
    with input_file_path.open(mode="rb") as track_file:
        # first read the header, accounting for the two different possible versions
        _ = track_file.readline()
        line_2_bytes = track_file.readline()

        # Check if line_2 is binary or part of the header
        is_ascii = True
        try:
            line_2 = line_2_bytes.decode("ascii")
        except UnicodeDecodeError:
            is_ascii = False

        if is_ascii and "Number of variables = " in line_2:
            # This is the new version of track files with the complete header

            # Finish processing the header info
            line_3 = track_file.readline().decode("ascii")
            num_columns, column_schema = _binary_get_column_names_included_header(
                line_2, line_3
            )

            # Load the binary part of the file
            data = np.fromfile(track_file, dtype=np.float64)

        else:
            # This is the old version of track files with the incomplete header
            track_file.seek(0)
            _ = track_file.readline()

            # Load the entire remaining file
            data = np.fromfile(track_file, dtype=np.float64)

            # Determine the number of columns and generate the schema
            num_columns, column_schema = _estimate_num_rows(data)

    # Reshape to the proper shape
    num_rows = data.shape[0] // num_columns
    data = data.reshape((num_rows, num_columns))

    # Compute mu
    data, column_schema = _compute_magnetic_moment(data, column_schema)

    # Convert to dataframe
    output_df = pl.from_numpy(data, schema=column_schema)

    # Get mins and maxes
    mins = output_df.select(pl.col("species")).min()
    maxes = output_df.select(pl.col("particle_id"), pl.col("species")).max()

    # Write to disk
    output_df.write_parquet(parquet_path)

    logger.debug("Finished with file %s", input_file_path)

    return pl.DataFrame(
        {
            "species_mins": mins["species"].item(),
            "species_maxes": maxes["species"].item(),
            "particle_id_maxes": maxes["particle_id"].item(),
            "num_rows": num_rows,
        }
    )


def _compute_global_ids(
    parquet_path: Path, species_min: int, species_max: int, particles_max: int
) -> pl.DataFrame:
    """Compute a global particle ID based on the species, particle, and block IDs.

    Parameters
    ----------
    parquet_path : Path
        The path to the parquet file.
    species_min : int
        The minimum value in the species column.
    species_max : int
        The maximum value in the species column.
    particles_max : int
        The maximum value in the particle_id column.

    Returns
    -------
    pl.DataFrame
        The unique global IDs in this file.
    """
    logger = setup_pt_logger()

    # Load the dataframe
    logger.debug("Starting %s", parquet_path)
    output_df = pl.read_parquet(parquet_path)

    # Compute new IDs
    n_species = species_max - species_min + 1
    n_particles = particles_max + 1
    output_df = output_df.with_columns(
        particle_id=(pl.col("species") - species_min)
        + (pl.col("particle_id") * n_species)
        + (pl.col("block_id") * n_species * n_particles)
    )

    # Sort
    output_df = output_df.sort(["particle_id", "time"])

    # Get the unique IDs
    unique_ids = output_df["particle_id"].unique()

    # Write to disk
    output_df.write_parquet(parquet_path)

    logger.debug("finished with %s", parquet_path)

    return unique_ids


def _collect_particles_and_compute_delta_mu(
    parquet_paths: tuple[Path, ...], chunk: tuple[int, int]
) -> Path:
    """Gather all data points for particles into single files and compute delta mu.

    This function takes a list of parquet files and a range of particle IDs then finds
    all the data for every particle in that range and collects it all into a single
    file. It then sorts that data according to particle ID and time and computes the
    change in mu at each time step. Results are written to new parquet files.

    Parameters
    ----------
    parquet_paths : tuple[Path, ...]
        The paths to the parquet files
    chunk : tuple[int, int]
        The IDs of the particles to collect. The first element is the low limit and the
        second element is the upper limit, both inclusive.

    Returns
    -------
    Path
        The path to the file that was written.
    """
    logger = setup_pt_logger()
    logger.debug("Starting with particle range %i-%i", chunk[0], chunk[1])

    # Filter to find all the particles in the chunk
    selected_particles = (
        pl.scan_parquet(parquet_paths)
        .filter(pl.col("particle_id").is_between(chunk[0], chunk[1]))
        .collect(engine="streaming")
    )

    # Sort the particle data
    selected_particles = selected_particles.sort(["particle_id", "time"])
    # Compute delta mu
    selected_particles = selected_particles.with_columns(
        delta_mu_abs=pl.when(pl.col("particle_id") == pl.col("particle_id").shift())
        .then((pl.col("mu") - pl.col("mu").shift()).abs())
        .otherwise(None)
    )

    # Write the results
    output_name = (
        "_".join(parquet_paths[0].stem.split("_")[:-2])
    ) + f"_particles_{chunk[0]}_{chunk[1]}.parquet"
    output_path = parquet_paths[0].parent / output_name
    selected_particles.write_parquet(output_path)

    logger.debug("Finished with particle range %i-%i", chunk[0], chunk[1])

    return output_path


def _verify_binary_track_collation(
    collected_paths: typing.Sequence[Path],
    num_chunks: int,
    n_rows_raw: int,
) -> None:
    """Verify that writing the parquet files went correctly.

    Parameters
    ----------
    collected_paths : typing.Sequence[Path]
        The paths to the final parquet files.
    num_chunks : int
        The number of chunks/files that should have been written
    n_rows_raw : int
        The number of rows in the original data.

    Raises
    ------
    RuntimeError
        If the number of files is incorrect or they are corrupt.
    """
    # Now we verify that the results are correct, or that there is at least the
    # correct number of files and they have the correct number of rows
    fix_msg = (
        "This is likely caused by insufficient memory leading to a silent crash. "
        "Try rerunning with at least 90GB of memory per CPU."
    )
    # Check for the correct number of files
    missing_files = False
    existing_count = 0
    for path in collected_paths:
        if not path.exists():
            missing_files = True
        else:
            existing_count += 1

    if (len(collected_paths) != num_chunks) or missing_files:
        msg = (
            "The final number of particle files is not correct. It should be "
            f"{num_chunks} but is {len(collected_paths)}. {fix_msg}"
        )
        raise RuntimeError(msg)

    # Check for the correct number of rows written
    try:
        n_rows_written = (
            pl.scan_parquet(collected_paths).select(pl.len()).collect().item()
        )
    except pl.exceptions.ComputeError as err:
        msg = f"One or more of the parquet files is corrupt. {fix_msg}"
        raise RuntimeError(msg) from err
    if n_rows_written != n_rows_raw:
        msg = (
            "The final number of rows written is not correct. It should be "
            f"{n_rows_raw} but only {n_rows_written} were written. {fix_msg}"
        )
        raise RuntimeError(msg)


def collate_tracks_from_binary(
    num_processes: int,
    source_dir: Path,
    destination_dir: Path,
    *,
    restart_collect: bool = False,
) -> None:
    """Collate the .track_mpiio_optimized files in a directory into ordered files.

    Parameters
    ----------
    num_processes : int
        The number of processes to use.
    source_dir : Path
        The path to the directory with the .track_mpiio_optimized files
    destination_dir : Path
        The path with filename where the parquet files should be created. It will be
        created if it doesn't exist.
    restart_collect : bool, optional
       Only run the final collection stage. Intended to be used to restart if the
       collection step fails due to running out of memory, by default False
    """
    # Setup logging
    logger = setup_pt_logger()

    # Get list of binary files
    logger.info("Gathering list of .track_mpiio_optimized files.")
    files_to_read = sorted(source_dir.glob("*.track_mpiio_optimized"))

    # Create destination directory if it doesn't already exist
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Make a tuple of the parquet files that will be generated
    parquet_paths = tuple(
        destination_dir / ("_".join(f.stem.split(".")) + "_temp.parquet")
        for f in files_to_read
    )

    # Spawning new processes instead of forking is required for polars
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=num_processes, mp_context=multiprocessing.get_context("spawn")
    ) as executor:
        logger.info(
            "ProcessPoolExecutor launched with %i processes. "
            "Using %i Polars threads each.",
            num_processes,
            pl.thread_pool_size(),
        )
        # Convert the binary files to parquet and get the mins & maxes for IDs
        start = default_timer()
        if not restart_collect:
            futures = [
                executor.submit(
                    _binary_track_reader,
                    files_to_read[i],
                    parquet_paths[i],
                )
                for i in range(len(files_to_read))
            ]

            # Check for errors and collect results
            extrema = pl.concat([future.result() for future in futures])
            logger.info(
                "Initial Conversion complete. Elapsed time: %.2fs",
                default_timer() - start,
            )

            # Compute the min & max IDs
            mins = extrema.select(pl.col("species_mins")).min()
            maxes = extrema.select(
                pl.col("species_maxes"), pl.col("particle_id_maxes")
            ).max()
            logger.info("Finished with determining min & max IDs")

            # Compute the new global IDs and get a list of all unique IDs.
            global_ids_start = default_timer()
            futures = [
                executor.submit(
                    _compute_global_ids,
                    path,
                    mins["species_mins"].item(),
                    maxes["species_maxes"].item(),
                    maxes["particle_id_maxes"].item(),
                )
                for path in parquet_paths
            ]
            # Check for errors and wait for it to complete
            _ = [future.result() for future in futures]
            logger.info(
                "Computing global IDs and sorting complete. Elapsed time: %.2fs",
                default_timer() - global_ids_start,
            )

            # Compute the number of rows that should be written
            n_rows_raw = extrema.select(pl.col("num_rows")).sum().item()
        else:
            # if this is a restart run then we need to get the number of rows that
            # should be written from the intermediate parquet files
            logger.info("collecting the number of raw rows")
            n_rows_raw = (
                pl.scan_parquet(parquet_paths)
                .select(pl.len())
                .collect(engine="streaming")
                .item()
            )

        # Get a sorted Series that consists of all the unique particle IDs
        logger.info("collecting unique IDs")
        unique_ids = (
            pl.scan_parquet(parquet_paths)
            .select(pl.col("particle_id"))
            .unique()
            .collect(engine="streaming")
            .to_series()
            .sort()
        )

        # Determine work group ranges
        num_chunks = len(parquet_paths)
        start_idx = 0
        step = int(np.ceil(len(unique_ids) / num_chunks))

        ranges = []
        while True:
            stop = start_idx + step
            if stop < len(unique_ids):
                ranges.append((unique_ids[start_idx], unique_ids[stop]))
                start_idx = stop + 1
            else:
                ranges.append((unique_ids[start_idx], unique_ids[-1]))
                break
        logger.info("Finished with determining work group ranges")

        # Collect data for each block of particles into a single parquet file
        collect_start = default_timer()
        futures = [
            executor.submit(_collect_particles_and_compute_delta_mu, parquet_paths, r)
            for r in ranges
        ]
        # Check for errors and collect results
        collected_paths = [future.result() for future in futures]

        logger.info(
            "Collecting particles into their own files complete. Elapsed time: %.2fs",
            default_timer() - collect_start,
        )

    # Now we verify that the results are correct, or that there is at least the
    # correct number of files and they have the correct number of rows
    _verify_binary_track_collation(collected_paths, len(ranges), n_rows_raw)
    logger.info("Number of output files and rows verified")

    # Clean up the temporary files
    delete_temps_start = default_timer()
    for path in parquet_paths:
        path.unlink()
    logger.info(
        "Deleting temporary files complete. Elapsed time: %.2fs",
        default_timer() - delete_temps_start,
    )

    logger.info(
        "Finished sorting and collecting particle data. Total time:: %.2fs",
        default_timer() - start,
    )
