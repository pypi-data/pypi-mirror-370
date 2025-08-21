"""
Read Athena++ output data files.
"""

# Python modules
import re
import struct
import sys
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3

# Other Python modules
import numpy as np

# Load HDF5 reader
try:
    import h5py
except ImportError:
    pass


# ========================================================================================


def track(filename, raw=False):
    """Read .hst files and return dict of 1D arrays."""

    # Read data
    with open(filename, 'r') as data_file:
        # Find header
        header_found = False
        multiple_headers = False
        header_location = None
        line = data_file.readline()
        while len(line) > 0:
            lsp = line.split()
            if lsp[2] == 'track':
                if header_found:
                    multiple_headers = True
                else:
                    header_found = True
                header_location = data_file.tell()
            line = data_file.readline()
        if multiple_headers:
            warnings.warn('Multiple headers found; using most recent data', AthenaWarning)
        if header_location is None:
            raise AthenaError('No header found')

        # Parse header
        data_file.seek(header_location)
        header = data_file.readline()
        data_names = re.findall(r'\[\d+\]=(\S+)', header)
        if len(data_names) == 0:
            raise AthenaError('Header could not be parsed')

        # Prepare dictionary of results
        data = {}
        for name in data_names:
            data[name] = []

        # Read data
        for line in data_file:
            for name, val in zip(data_names, line.split()):
                data[name].append(float(val))

    # Finalize data
    for key, val in data.iteritems():
        data[key] = np.array(val)
    if not raw:
        if data_names[0] != 'time':
            raise AthenaError(
                'Cannot remove spurious data because time column could not be' +
                ' identified')
        branches_removed = False
        while not branches_removed:
            branches_removed = True
            for n in range(1, len(data['time'])):
                if data['time'][n] <= data['time'][n-1]:
                    branch_index = np.where(data['time'][:n] >= data['time'][n])[0][0]
                    for key, val in data.iteritems():
                        data[key] = np.concatenate((val[:branch_index], val[n:]))
                    branches_removed = False
                    break
    return data


# ========================================================================================


def tab(filename, raw=False, dimensions=None):
    """Read .tab files and return dict or array."""

    # Check for valid number of dimensions
    if raw and not (dimensions == 1 or dimensions == 2 or dimensions == 3):
        raise AthenaError('Improper number of dimensions')
    if not raw and dimensions is not None:
        warnings.warn('Ignoring specified number of dimensions', AthenaWarning)

    # Parse header
    if not raw:
        data_dict = {}
        with open(filename, 'r') as data_file:
            line = data_file.readline()
            attributes = re.search(r'time=(\S+)\s+cycle=(\S+)\s+variables=(\S+)', line)
            line = data_file.readline()
            headings = line.split()[1:]
        data_dict['time'] = float(attributes.group(1))
        data_dict['cycle'] = int(attributes.group(2))
        data_dict['variables'] = attributes.group(3)
        if headings[0] == 'i' and headings[2] == 'j' and headings[4] == 'k':
            headings = headings[1:2] + headings[3:4] + headings[5:]
            dimensions = 3
        elif ((headings[0] == 'i' and headings[2] == 'j') or
              (headings[0] == 'i' and headings[2] == 'k') or
              (headings[0] == 'j' and headings[2] == 'k')):
            headings = headings[1:2] + headings[3:]
            dimensions = 2
        elif headings[0] == 'i' or headings[0] == 'j' or headings[0] == 'k':
            headings = headings[1:]
            dimensions = 1
        else:
            raise AthenaError('Could not parse header')

    # Go through lines
    data_array = []
    with open(filename, 'r') as data_file:
        first_line = True
        for line in data_file:

            # Skip comments
            if line.split()[0][0] == '#':
                continue

            # Extract cell indices
            vals = line.split()
            if first_line:
                i_min = i_max = int(vals[0])
                if dimensions == 2 or dimensions == 3:
                    j_min = j_max = int(vals[2])
                if dimensions == 3:
                    k_min = k_max = int(vals[4])
                num_entries = len(vals) - dimensions
                first_line = False
            else:
                i_max = max(i_max, int(vals[0]))
                if dimensions == 2 or dimensions == 3:
                    j_max = max(j_max, int(vals[2]))
                if dimensions == 3:
                    k_max = max(k_max, int(vals[4]))

            # Extract cell values
            if dimensions == 1:
                vals = vals[1:]
            if dimensions == 2:
                vals = vals[1:2] + vals[3:]
            if dimensions == 3:
                vals = vals[1:2] + vals[3:4] + vals[5:]
            data_array.append([float(val) for val in vals])

    # Reshape array based on number of dimensions
    if dimensions == 1:
        array_shape = (i_max-i_min+1, num_entries)
        array_transpose = (1, 0)
    if dimensions == 2:
        array_shape = (j_max-j_min+1, i_max-i_min+1, num_entries)
        array_transpose = (2, 0, 1)
    if dimensions == 3:
        array_shape = (k_max-k_min+1, j_max-j_min+1, i_max-i_min+1, num_entries)
        array_transpose = (3, 0, 1, 2)
    data_array = np.transpose(np.reshape(data_array, array_shape), array_transpose)

    # Finalize data
    if raw:
        return data_array
    else:
        for n, heading in enumerate(headings):
            data_dict[heading] = data_array[n, ...]
        return data_dict

# ========================================================================================


class AthenaError(RuntimeError):
    """General exception class for Athena++ read functions."""
    pass


class AthenaWarning(RuntimeWarning):
    """General warning class for Athena++ read functions."""
    pass
