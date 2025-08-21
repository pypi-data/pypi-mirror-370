"""Provides the utilities required to load output files from Pegasus++.

This module provides:
- PegasusSpectralData: A class for holding the data loaded from a spectra file
- _load_spectra: A function for loading spectra files
"""

from pathlib import Path

import numpy as np
import polars as pl


class PegasusSpectralData:
    """Holds all the data loaded when loading a spectra file.

    Stores the time data in a private variable accessible via a getter and stores the
    spectra data in a numpy array named `data`
    """

    def __init__(
        self,
        file_path: Path,
        n_prp: int = 200,
        n_prl: int = 400,
        max_w_prp: float = 4.0,
        max_w_prl: float = 4.0,
    ) -> None:
        """Initialize a PegasusSpectralData class with the header data.

        Parameters
        ----------
        file_path : Path
            The file path to the file to load
        n_prp : int, optional
            The value of n_prp used in the peginput file, by default 200. This argument
            is ignored if the spectra file is in the new format that contains this
            information in the header.
        n_prl : int, optional
            The value of n_prl used in the peginput file, by default 400. This argument
            is ignored if the spectra file is in the new format that contains this
            information in the header.
        max_w_prp : float, optional
            The value of max_w_prp used in the peginput file, by default 4.0. This
            argument is ignored if the spectra file is in the new format that contains
            this information in the header.
        max_w_prl : float, optional
            The value of max_w_prl used in the peginput file, by default 4.0. This
            argument is ignored if the spectra file is in the new format that contains
            this information in the header.

        Raises
        ------
        ValueError
            Raised if the file does not have the right number of elements for the
            provided n_prl and n_prp
        """
        # Define member variables
        self.__n_prp: int = n_prp
        self.__n_prl: int = n_prl
        self.__max_w_prp: float = max_w_prp
        self.__max_w_prl: float = max_w_prl
        self.spectra_prp: np.typing.NDArray[np.float64]
        self.spectra_prl: np.typing.NDArray[np.float64]

        # Open the file
        with file_path.open(mode="rb") as spec_file:
            # Load the header
            header = spec_file.readline().decode("ascii")
            second_line_loc = spec_file.tell()
            self.__time: np.float64 = np.float64(header.split()[-1])

            # Check if this is the new spectra format with the complete header
            n_prl_line_bytes = spec_file.readline()

            # Check if line_2 is binary or part of the header
            is_ascii = True
            try:
                n_prl_line = n_prl_line_bytes.decode("ascii")
            except UnicodeDecodeError:
                is_ascii = False

            if is_ascii and "Histogram size in wprl = " in n_prl_line:
                # Now we need to decode the contents of the new header
                self.__n_prl = int(n_prl_line.rstrip().split(" ")[-1])
                self.__n_prp = int(
                    spec_file.readline().decode("ascii").rstrip().split(" ")[-1]
                )
                self.__max_w_prl = float(
                    spec_file.readline().decode("ascii").rstrip().split(" ")[-1]
                )
                self.__max_w_prp = float(
                    spec_file.readline().decode("ascii").rstrip().split(" ")[-1]
                )
            else:
                spec_file.seek(second_line_loc)

            # Load the entire remaining file
            self.data = np.fromfile(spec_file, dtype=np.float64)

            # Get the info to reshape the array
            block_header_size = 6  # The header of each block is 6 elements
            num_row = self.__n_prl * self.__n_prp + block_header_size
            num_col = self.data.size // num_row

            # Check that the file is actually the right size for the number of elements
            # per spectra. Note that this check isn't perfect, it just verifies that the
            # file can be exactly divided by the number of elements provided.
            if self.data.size % num_row != 0:
                err_msg = (
                    f"The file {file_path} does not have the right number of "
                    f"elements for the values of {self.__n_prl = } and "
                    f"{self.__n_prp = } provided."
                )
                raise ValueError(err_msg)

            # Rearrange the data into the correct shape including the header for each
            # meshblock
            self.data = self.data.reshape((num_col, num_row))

            # Slice off the header and main data
            headers = self.data[:, :block_header_size]
            self.data = self.data[:, block_header_size:]

            # Reshape data now that the headers have been removed
            self.data = self.data.reshape((num_col, self.__n_prp, self.__n_prl))

            # Organize the meshblock headers into a DataFrame
            self._meshblock_locations = pl.from_numpy(
                headers,
                schema=("x1min", "x1max", "x2min", "x2max", "x3min", "x3max"),
            )

    # Define getters for header variables
    @property
    def time(self) -> np.float64:
        """Get the simulation time of the spectra file.

        Returns
        -------
        np.float64
            The time in the spectra file
        """
        return self.__time

    @property
    def n_prp(self) -> int:
        """Get n_prp.

        Returns
        -------
        int
            The value of n_prp
        """
        return self.__n_prp

    @property
    def n_prl(self) -> int:
        """Get n_prl.

        Returns
        -------
        int
            The value of n_prl
        """
        return self.__n_prl

    @property
    def max_w_prp(self) -> float:
        """Get max_w_prp.

        Returns
        -------
        int
            The value of max_w_prp
        """
        return self.__max_w_prp

    @property
    def max_w_prl(self) -> float:
        """Get max_w_prl.

        Returns
        -------
        int
            The value of max_w_prl
        """
        return self.__max_w_prl

    @property
    def meshblock_locations(self) -> pl.DataFrame:
        """Get meshblock locations DataFrame.

        Returns
        -------
        pl.DataFrame
            The location data for each meshblock. Keys are:
            - x1min
            - x1max
            - x2min
            - x2max
            - x3min
            - x3max
        """
        return self._meshblock_locations
