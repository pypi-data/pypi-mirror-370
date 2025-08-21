#!/usr/bin/env python3
"""
Reads in a file containing a Pandas DataFrame (environmental sensing data)
with either a .pbz2 (compressed Python Pickle) file or a .dat extension.
Creates a ROOT file containing the raw data, processed data, and plots for
each quantity against time.
"""

import argparse
import array
import math
import os

import numpy as np
import pandas as pd
import ROOT

from mmcb import common


##############################################################################
# command line option handler
##############################################################################

def check_arguments():
    """
    handle command line options

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns
        parser.parse_args()
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Reads in a file containing environmental sensing data.\
        Creates a ROOT file containing the raw data, processed data, and\
        plots for each quantity against time.')
    parser.add_argument(
        'filename', nargs=1, metavar='filename',
        help='Specify the file to convert. Supported file extensions:\
        h5 (HDF5 with Blosc Zstandard compression),\
        dat (Pandas CSV with ZIP compression),\
        pbz2 (Python Pickle, bzip2 compression).',
        type=str)

    return parser.parse_args()


##############################################################################
# utilities
##############################################################################

def clean(column_title):
    """
    Clean up (simplify) column titles so they'll be displayed without issue
    by rootbrowse.

    --------------------------------------------------------------------------
    args
        column_title : string
            e.g. 'TCt1_M1_flex °C'
    --------------------------------------------------------------------------
    returns
        ct : string
            e.g. 'TCt1_M1_flex_degC'
    --------------------------------------------------------------------------
    """
    ct = column_title.replace('°', 'deg').replace('%', 'PC').replace(' ', '_')
    ct = ct.encode('ascii', errors='ignore').decode("ascii")

    return ct


##############################################################################
# main
##############################################################################

def main():
    """
    Reads in a file containing a Pandas DataFrame (environmental sensing data)
    with either a .pbz2 (compressed Python Pickle) file or a .dat extension.
    Creates a ROOT file containing the raw data, processed data, and plots
    for each quantity against time.
    """

    ##########################################################################
    # read file
    ##########################################################################

    args = check_arguments()
    infile = args.filename[0]
    print(f'reading {infile}')
    file_extension = os.path.splitext(infile)[-1]

    if file_extension == '.h5':
        with pd.HDFStore(infile, 'r') as hdf:
            data = pd.DataFrame(hdf['key'])
    elif file_extension == '.dat':
        # deprecated file format - support retained for archived data
        data = pd.read_csv(infile, compression='zip')
    elif file_extension == '.pbz2':
        # deprecated file format - support retained for archived data
        data = common.data_read(infile)
    else:
        print(f'unrecognised file extension {file_extension}')
        return

    ##########################################################################
    # make sure rootls -t <filename> gives identical results whether the .dat
    # was written by this script or by sense.py
    ##########################################################################

    try:
        data = data[sorted(data.columns)]
    except NameError:
        # no data was read in from the user-specified file
        return

    ##########################################################################
    # save raw data
    ##########################################################################

    outfile = f'{os.path.splitext(infile)[0]}.root'
    print(f'writing {outfile}')
    rootfile = ROOT.TFile.Open(outfile, 'RECREATE', 'data acquired')

    # use ZSTD compression level 5 (int value 505) for the whole file
    # see: https://root.cern.ch/doc/master/Compression_8h_source.html
    rootfile.SetCompressionSettings(ROOT.RCompressionSetting.EDefaults.kUseGeneralPurpose)
    rootfile.cd()

    column_titles_text = ':'.join(clean(d) for d in data.columns)
    ntuple_raw = ROOT.TNtuple('raw_data', 'Atlas RD53 Environmental Sensing (RAW)',
                              column_titles_text)

    for _index, row_contents in data.iterrows():
        ntuple_raw.Fill(array.array('f', row_contents))

    ##########################################################################
    # generate dew point column(s)
    #
    # ... but only for sensors that generate all the required data
    # themselves. Data from different sensors are not mixed.
    ##########################################################################

    columns_of_interest = {x for x in data.columns if 'RH%' in x or '°C' in x}

    # shortlist sensors suitable for dew point calculation
    sensor_rhp = {c.split(' ')[0] for c in columns_of_interest if 'RH%' in c}
    sensor_dgc = {c.split(' ')[0] for c in columns_of_interest if '°C' in c}
    sensor_dew = sensor_rhp.intersection(sensor_dgc)

    # Avoid divide by zero in dew_point function later, since the BME680 seems
    # to frequently return zero for relative humidity in dry conditions.
    for column in {c for c in columns_of_interest if 'RH%' in c}:
        data[column] = data[column].replace(0.0, 0.001)

    # create new columns with calculated dew points
    for sensor in sorted(sensor_dew):
        source_columns = {x for x in columns_of_interest if sensor in x}

        try:
            column_temp = next(x for x in source_columns if '°C' in x)
            column_humi = next(x for x in source_columns if 'RH%' in x)
        except StopIteration:
            continue

        new_column_title = f'{sensor} DP°C'
        data[new_column_title] = common.dew_point(data[column_temp], data[column_humi])

    # Since RH% values at zero were changed to a small non-zero value above,
    # clamp the dew point values to -71 which is the figure for the dry air
    # supply in the cleanroom.
    for column in {x for x in data.columns if 'DP°C' in x}:
        data[column] = np.where((data[column] < -71), -71.0, data[column])

    ##########################################################################
    # adjust the x-axis so it starts at zero and is in human readable units
    ##########################################################################

    units = common.time_axis_adjustment(data)

    ##########################################################################
    # store processed and calculated data
    ##########################################################################

    column_titles_text = ':'.join(clean(d) for d in data.columns)
    ntuple = ROOT.TNtuple('processed_data', 'Atlas RD53 Environmental Sensing (PROCESSED)',
                          column_titles_text)

    for _index, row_contents in data.iterrows():
        ntuple.Fill(array.array('f', row_contents))

    ##########################################################################
    # create plots from the processed and calculated data
    ##########################################################################

    ts = data['timestamp'].tolist()
    tsa = array.array('f', ts)

    for column in (c for c in data.columns if c != 'timestamp'):
        unit = column.split(' ')[-1]
        if 'DP°C' in unit:
            unit = 'calculated dew point (#circC)'
        elif '°' in unit:
            unit = 'temperature (#circC)'
        elif 'RH%' in unit:
            unit = f'humidity ({unit})'
        elif 'Pa' in unit:
            unit = f'pressure ({unit})'

        # don't ask ROOT to plot data with NaN values
        values = array.array('f', data[column].tolist())
        ts = []
        va = []
        for t, v in zip(tsa, values):
            if not math.isnan(v):
                ts.append(t)
                va.append(v)

        graph = ROOT.TGraph(len(ts), array.array('f', ts), array.array('f', va))
        graph.GetXaxis().CenterTitle()
        graph.GetYaxis().CenterTitle()
        clean_column = clean(column)
        graph.SetTitle(f'{clean_column};elapsed time ({units});{unit}')
        graph.Write(clean_column)

    # Write the data from the TFile to the actual file on disk.
    rootfile.cd()
    rootfile.Write()
    rootfile.Close()


##############################################################################
if __name__ == '__main__':
    main()
