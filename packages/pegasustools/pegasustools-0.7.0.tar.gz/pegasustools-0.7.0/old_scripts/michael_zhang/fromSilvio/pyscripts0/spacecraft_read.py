import re
import warnings
from io import open  # Consistent binary I/O from Python 2 and 3
import numpy as np
from matplotlib import pyplot as plt

###################################################
###  READING & CLEANING SPACECRAFT TIME SERIES  ### 
###  -----------[ S.S.Cerri, 2019 ]-----------  ###
###################################################

def spacecraft_read(path_input,problem,spacecraft_id,raw=False):
    """Read spacecraft files and return dict of 1D arrays."""

    print "\n" 
    print " ####################################" 
    print " ## Reading spacecraft time series ##"
    print " ####################################"
    print "\n  spacecraft ID: ",spacecraft_id

    filename = path_input+problem+".spacecraft."+"%05d"%spacecraft_id+".dat"
    print "  file -> ",filename

    

    # Read data
    print "\n  [ reading raw data ]"
    #
    with open(filename, 'r') as data_file:
        # Find header
        header_found = False
        multiple_headers = False
        header_location = None
        line = data_file.readline()
        while len(line) > 0:
            if line == '# Pegasus++ spacecraft data for spacecraft number '+'%d'%spacecraft_id+'\n':
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
    print "\n  [ finalize data ]"
    #
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
     
    print "\n -> spacecraft_read: DONE.\n"
     
    return data


