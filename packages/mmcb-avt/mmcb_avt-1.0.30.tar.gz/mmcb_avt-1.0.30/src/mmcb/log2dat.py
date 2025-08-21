#!/usr/bin/env python3
"""
Reads the log file created by the environmental sensing script, converts this
to a Pandas DataFrame and saves it to disk in a compressed Python Pickle file
for later analysis.
"""

import argparse
import bz2
import contextlib
import gzip
import lzma
import os
import time

import pandas as pd


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
        description='Reads the log file created by the environmental sensing\
        script, converts this to a Pandas DataFrame and saves it to disk in a\
        compressed Python Pickle file for later analysis. The log file is\
        designed to be human-readable in a terminal window, and because of\
        this parts of the same data acquisition are split over several lines\
        with timestamps that may differ by 10ms or so. Any lines with\
        timestamps that fall within 200ms of each other are combined into a\
        single DataFrame row.')
    parser.add_argument(
        'log', nargs=1, metavar='filename',
        help='Specify the log file to convert',
        type=str)

    return parser.parse_args()


##############################################################################
# utilities
##############################################################################

def open_method(infile):
    """
    Return the appropriate function to open the given file based on its
    extension. This will set the binary mode correctly for compressed files.

    --------------------------------------------------------------------------
    args
        infile : string
            filename of the log file to read
    --------------------------------------------------------------------------
    returns : function
    --------------------------------------------------------------------------
    """
    infile_extension = os.path.splitext(infile)[-1].lower()
    methods = {'.bz2': bz2.open, '.gz': gzip.open,
               '.xz': lzma.open, '.z': gzip.open}

    return methods.get(infile_extension, open)


def get_data_from_log(infile):
    """
    Extracts data from log, yields sensor readings as they are read.

    log entries look like this:

    2020-02-20 12:44:46,927 : INFO : BME280   21.5 °C , METEOMK2-12E3A7   21.2 °C
    2020-02-20 12:44:46,928 : INFO : BME280   31.4 RH%, METEOMK2-12E3A7   31.0 RH%
    2020-02-20 12:44:46,928 : INFO : BME280  999.7 hPa, METEOMK2-12E3A7 1000.0 hPa
    2020-02-20 12:44:52,102 : INFO : BME280   21.5 °C , METEOMK2-12E3A7   21.2 °C
    2020-02-20 12:44:52,108 : INFO : BME280   31.4 RH%, METEOMK2-12E3A7   31.0 RH%
    2020-02-20 12:44:52,108 : INFO : BME280  999.7 hPa, METEOMK2-12E3A7 1000.0 hPa

    --------------------------------------------------------------------------
    args
        infile : string
            filename of the log file to read
    --------------------------------------------------------------------------
    yields
        row_acc : dict
            e.g. {'timestamp': 1603819534.675, 'bme280_0 °C': 19.8,
                  'bme280_1 °C': 19.2, 'bme280_2 °C': 20.6, ...}
    --------------------------------------------------------------------------
    """

    # '2019-10-04 14:17:12,892'
    # note that %f is a value in microseconds, and the figure given in the
    # string is in milliseconds, so later, the string will be padded with
    # three trailing zeroes to correct this
    log_timestamp_format = '%Y-%m-%d %H:%M:%S,%f,%Z'

    # handle opening of compressed log files
    file_read = open_method(infile)

    row_acc = {}
    row = {}

    with file_read(infile) as templog:
        for line in templog.readlines():

            # if the log file is compressed, line will be bytes rather than string
            with contextlib.suppress(AttributeError):
                line = line.decode('utf-8')

            # extract timestamp and convert it to seconds since epoch
            #
            # line = '2020-02-26 17:41:56,861 : INFO : BME280   14.2 °C'
            # timestamp, data = ['2020-02-26 17:41:56,861', 'BME280   14.2 °C']
            try:
                timestamp_raw, datatext = [x.strip() for x in line.split(' : INFO : ')]
            except ValueError:
                continue

            fraction = float('.' + timestamp_raw.rsplit(',')[-1])
            timestamp = timestamp_raw + '000,UTC'
            epoch = time.mktime(time.strptime(timestamp, log_timestamp_format)) + fraction

            # extract for pandas

            # convert this line to dict entries
            sensors = [x.strip().split() for x in datatext.split(',')]
            for sensor in sensors:
                if len(sensor) == 3:
                    row[f'{sensor[0]} {sensor[2]}'] = float(sensor[1])

            # Merge all sequential data acquisition log lines with timestamps
            # within 0.5s into the same DataFrame row, but only if no data
            # would be overwritten in the process. An overwrite could
            # plausibly occur if logs are combined from more than one machine
            # where the same sensor type is in use.
            try:
                dissimilar_acquisition_time = abs(epoch - row_acc['timestamp']) > 0.5
            except KeyError:
                # first line of log file
                row_acc['timestamp'] = epoch
            else:
                conflict = set(row).intersection(set(row_acc))

                if dissimilar_acquisition_time or conflict:
                    # start new acquisition period
                    yield row_acc
                    row_acc.clear()
                    row_acc['timestamp'] = epoch
            finally:
                row_acc.update(row)
                row.clear()


##############################################################################
# main
##############################################################################

def main():
    """
    Reads the log file created by the environmental sensing script, converts
    this to a Pandas DataFrame and saves it to disk as a compressed Python
    Pickle file for later analysis.
    """

    args = check_arguments()
    infile = args.log[0]
    print(f'reading {infile}')

    pdat = pd.DataFrame(dict(x) for x in get_data_from_log(infile))

    outfile = f'{os.path.splitext(infile)[0]}_pandas_csv_zip.dat'
    print(f'writing {outfile}')
    pdat.to_csv(outfile, index=False, compression='zip')


##############################################################################
if __name__ == '__main__':
    main()
