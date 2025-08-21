#!/usr/bin/env python3
"""
Generates a raw data plot from a pandas DataFrame - this is dat2plot
adapted for use with the Parylene coater's thermocouples.
"""

import argparse
import datetime
import os

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import tables

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
        description='Reads in a binary data file containing a Pandas\
        DataFrame with environmental sensing data, then generates plots of\
        the raw data, with a separate plot for each parameter. Specifically\
        created for the Parylene coater.')
    parser.add_argument(
        'filename', nargs=1, metavar='filename',
        help='Specify the file to plot. Supported file extensions:\
        h5 (HDF5 with Blosc Zstandard compression),\
        dat (Pandas CSV with ZIP compression),\
        pbz2 (Python Pickle, bzip2 compression).',
        type=str)

    return parser.parse_args()


##############################################################################
# utilities
##############################################################################


def time_axis_adjustment(data, marks):
    """
    Generate the parameters necessary to transform absolute UNIX-style epoch
    timestamps to relative timestamps with human-readable units.

    --------------------------------------------------------------------------
    args
        data : pandas.DataFrame
        marks : dict
    --------------------------------------------------------------------------
    returns
        units : string
        data : pandas.DataFrame
            no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    earliest_timestamp = data['timestamp'].min()
    latest_timestamp = data['timestamp'].max()

    minutes_of_available_data = (latest_timestamp - earliest_timestamp) / 60

    if minutes_of_available_data > 180:
        units = 'hours'
        scale = 3600
    else:
        units = 'minutes'
        scale = 60

    data['timestamp'] = (data['timestamp'] - earliest_timestamp) / scale

    marks_adjusted = {(k - earliest_timestamp) / scale: v for k, v in marks.items()}

    return units, marks_adjusted


##############################################################################
# plot
##############################################################################

def plot_raw(data, units, infile, marks):
    """
    Creates a raw data plot with one subplot for each unique unit of
    measurement for all sensors.

    --------------------------------------------------------------------------
    args
        data : pandas.DataFrame
        units : string
            description of x-axis (time) units
        infile : string
            filename of stored pandas dataframe
        colour_map : dict
            Mapping of column names to colours, where the colour for any given
            column is unique to its sensor. This ensures that sensor colours
            remain constant over multiple subplots.
            e.g.
            {'ntc °C': (0.839, 0.152, 0.156, 1.0),
             'hyt221_ch0_M1 DP°C': (0.172, 0.627, 0.172, 1.0), ...}
    --------------------------------------------------------------------------
    returns : no explicit return
            plot written to local filestore
    --------------------------------------------------------------------------
    """
    lwi = 0.5
    lal = 1

    y_axis_label_prefix = {'°C': 'temperature (°C)',
                           'RH%': 'relative humidity (RH%)',
                           'DP°C': 'calculated dew point (°C)',
                           'kPa': 'vacuum (kPa)',
                           'hPa': 'pressure (hPa)'}

    num_plots = len(data.columns) - 1

    # for 3 subplots a 12 x 8 size works well, use this as a basis for other
    # numbers of plots
    y_size = (8 / 3) * num_plots

    fig, axes = plt.subplots(nrows=num_plots, ncols=1, sharex=True, figsize=(12, y_size))

    # avoid crash when there is only one subplot
    try:
        len(axes)
    except TypeError:
        axes = [axes]

    for index, column in enumerate(x for x in sorted(data.columns) if x != 'timestamp'):
        unit = column.split(' ')[-1]
        myax = data.plot(
            kind='line', x='timestamp', y=column, ax=axes[index],
            alpha=lal, linewidth=lwi
        )

        axes[index].legend(loc='center left', bbox_to_anchor=(1.01, 0.5))

        yal_prefix = y_axis_label_prefix.get(unit)
        yal = unit if yal_prefix is None else yal_prefix
        axes[index].set_ylabel(yal)

        # add day marks (if any)
        ylims = myax.get_ylim()
        for mark, day_name in marks.items():
            myax.vlines(
                mark, ylims[0], ylims[1],
                zorder=-1.0, linewidth=0.5, colors='gray', alpha=0.5
            )
            # add day names to top plot
            if index == 0:
                myax.annotate(
                    day_name,
                    xy=(mark, ylims[1]),
                    xytext=(0, 5),
                    textcoords='offset points',
                    color='gray',
                    size='xx-small'
                )
            myax.set_ylim(ylims)

    axes[-1].set_xlabel(f'elapsed time ({units})')

    fig.suptitle(infile)

    plt.tight_layout()

    basename_no_ext = os.path.splitext(os.path.basename(infile))[0]
    plt.savefig(f'{basename_no_ext}.pdf')


##############################################################################
# main
##############################################################################

def main():
    """
    Generates a raw data plot from a pandas DataFrame - this is dat2plot.py
    adapted for use with the Parylene coater's thermocouples.

    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.html
    """
    # set matplotlib defaults
    matplotlib.rcParams.update({
        'legend.fontsize': 'x-small',
        # fontsize of title
        'legend.title_fontsize': 'x-small'})

    args = check_arguments()
    infile = args.filename[0]
    print(f'reading {infile}')
    file_extension = os.path.splitext(infile)[-1]

    if file_extension == '.h5':
        try:
            with pd.HDFStore(infile, 'r') as hdf:
                data = pd.DataFrame(hdf['key'])
        except tables.exceptions.HDF5ExtError:
            # No need to show the user the HDF5 error backtrace.
            # The filename has alread been printed.
            print('unable to open file')
            return
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
    # plot

    start_timestamp = min(data.timestamp)
    start_date = datetime.datetime.fromtimestamp(start_timestamp)
    end_timestamp = max(data.timestamp)
    end_date = datetime.datetime.fromtimestamp(end_timestamp)

    year, month, day = start_date.year, start_date.month, start_date.day
    mark = datetime.datetime(year=year, month=month, day=day) + datetime.timedelta(days=1)

    marks = {}
    while mark < end_date:
        date_ref = pd.to_datetime(mark)
        dayname = date_ref.day_name()[0]
        day = date_ref.day
        month = date_ref.month
        year = str(date_ref.year)[-2:]
        date_string = f'{year}-{month}-{day} ({dayname})'
        marks[datetime.datetime.timestamp(mark)] = date_string
        mark += datetime.timedelta(days=1)

    if len(marks) > 30:
        marks.clear()

    # Adjust the x-axis so it starts at zero and is in human-readable units.
    units, marks = time_axis_adjustment(data, marks)

    # Creates one subplot for each unique unit of measurement for all sensors.
    plot_raw(data, units, infile, marks)


##############################################################################
if __name__ == '__main__':
    main()
