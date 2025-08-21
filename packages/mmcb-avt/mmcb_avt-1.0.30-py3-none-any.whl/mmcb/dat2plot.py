#!/usr/bin/env python3
"""
Generates two plots from a pandas DataFrame.

The first shows raw acquired data, the second provide distributions of sampled
data.
"""

import argparse
import datetime
import itertools
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
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
        the raw data and summary statistics.')
    parser.add_argument(
        'filename', nargs=1, metavar='filename',
        help='Specify the file to plot. Supported file extensions:\
        h5 (HDF5 with Blosc Zstandard compression),\
        dat (Pandas CSV with ZIP compression),\
        pbz2 (Python Pickle, bzip2 compression).',
        type=str)

    return parser.parse_args()


##############################################################################
# plot
##############################################################################

def plot_raw(data, units, infile, unique_units, colour_map, marks):
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
        unique_units : set
            A separate subplot is created for each unit in this set.
            e.g. {'DP°C', 'hPa', 'RH%', 'kPa', '°C'}
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

    y_axis_label_prefix = {
        '°C': 'temperature (°C)',
       'RH%': 'relative humidity (RH%)',
       'DP°C': 'calculated dew point (°C)',
       'kPa': 'vacuum (kPa)',
       'lps': 'flow rate (l/s)',
       'hPa': 'pressure (hPa)',
    }

    num_plots = len(unique_units)
    # for 3 subplots a 12 x 8 size works well, use this as a basis for other
    # numbers of plots
    y_size = (8 / 3) * num_plots

    fig, axes = plt.subplots(nrows=num_plots, ncols=1, sharex=True, figsize=(12, y_size))

    # avoid crash when there is only one subplot
    try:
        len(axes)
    except TypeError:
        axes = [axes]

    for index, unit in enumerate(unique_units):
        ccc = (c for c in data.columns if unit == c.split(' ')[-1])
        columns = sorted(ccc, key=lambda x: x.lower())
        mcmap = [
            colour_map.get(c.split(' ')[0], '#000000')
            for c in columns
        ]
        myax = data.plot(
            kind='line', x='timestamp', y=columns, ax=axes[index],
            alpha=lal, linewidth=lwi, color=mcmap
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
    plt.savefig(f'{basename_no_ext}_raw.pdf')


def plot_summary(data, units, infile, unique_units):
    """
    Creates a summary statistics plot with the same basic structure as that
    created by plot_raw().

    --------------------------------------------------------------------------
    args
        data : pandas.DataFrame
        units : string
            description of x-axis (time) units
        infile : string
            filename of stored pandas dataframe
        unique_units : set
            A separate subplot is created for each unit in this set.
            e.g. {'DP°C', 'hPa', 'RH%', 'kPa', '°C'}
    --------------------------------------------------------------------------
    returns : no explicit return
            plot written to local filestore
    --------------------------------------------------------------------------
    """
    y_axis_label_prefix = {
        '°C': 'temperature (°C)',
       'RH%': 'relative humidity (RH%)',
       'DP°C': 'calculated dew point (°C)',
       'kPa': 'vacuum (kPa)',
       'lps': 'flow rate (l/s)',
       'hPa': 'pressure (hPa)',
    }

    num_plots = len(unique_units)

    # for 3 subplots a 12 x 12 size works well, use this as a basis for other
    # numbers of plots
    y_size = 4.5 * num_plots

    fig, axes = plt.subplots(nrows=num_plots, ncols=1, figsize=(12, y_size),
                             constrained_layout=True)

    # avoid crash when there is only one subplot
    try:
        len(axes)
    except TypeError:
        axes = [axes]

    for index, unit in enumerate(unique_units):
        ccc = (c for c in data.columns if unit == c.split(' ')[-1])
        columns = sorted(ccc, key=lambda x: x.lower())
        data.plot(kind='box', y=columns, ax=axes[index], showfliers=False)

        yal_prefix = y_axis_label_prefix.get(unit)
        yal = unit if yal_prefix is None else yal_prefix
        axes[index].set_ylabel(yal)

    axes[-1].set_xlabel('sensor')

    acquisition_duration = f'{data["timestamp"].max():.1f}'
    if acquisition_duration == '1.0':
        units = units[:-1]
    fig.suptitle(f'{infile}: {acquisition_duration} {units} of data')

    # descriptive x-axis labels may be long and collide unless angled.
    for i in range(num_plots):
        for tick in axes[i].get_xticklabels():
            tick.set_rotation(30)

    basename_no_ext = os.path.splitext(os.path.basename(infile))[0]
    plt.savefig(f'{basename_no_ext}_stat.pdf')


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
# main
##############################################################################

def main():
    """
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
    # generate dew point columns for appropriate sensors

    try:
        columns_of_interest = {
            x for x in data.columns if 'RH%' in x or '°C' in x
        }
    except NameError:
        # no data was read in from the user-specified file
        return

    sensor_rhp = {c.split(' ')[0] for c in columns_of_interest if 'RH%' in c}
    sensor_dgc = {c.split(' ')[0] for c in columns_of_interest if '°C' in c}
    sensor_dew = sensor_rhp.intersection(sensor_dgc)

    # Avoid divide by zero in dew_point function later, since the BME680 seems
    # to return zero for relative humidity in dry conditions due to limited
    # resolution.
    for column in {c for c in columns_of_interest if 'RH%' in c}:
        data[column].replace(0.0, 0.001, inplace=True)

    # create new columns with calculated dew points
    for sensor in sensor_dew:
        source_columns = {x for x in columns_of_interest if sensor in x}

        try:
            column_temp = next(x for x in source_columns if '°C' in x)
            column_humi = next(x for x in source_columns if 'RH%' in x)
        except StopIteration:
            continue

        new_column_title = f'{sensor} DP°C'

        # problems when BME680 RH% = 0
        data[new_column_title] = common.dew_point(data[column_temp], data[column_humi])

    # Since RH% values at zero were changed to a small non-zero value above,
    # clamp the dew point values to -71 which is the figure for the dry air
    # supply in the cleanroom.
    for column in {x for x in data.columns if 'DP°C' in x}:
        data[column] = np.where((data[column] < -71), -71.0, data[column])

    ##########################################################################
    # work out how many plots are required - one for each different unit

    unique_units = {x.split(' ')[-1] for x in data.columns}
    unique_units.discard('timestamp')

    ##########################################################################
    # colour map - make sure sensor colours are the same in all subplots
    #
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.line.html
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html

    # get all unique sensor names and assign a colour
    unique_sensor_name = {x.split(' ')[0] for x in data.columns if x != 'timestamp'}
    colours = [plt.cm.tab10(x) for x in range(10)]
    colour_map = dict(zip(sorted(unique_sensor_name), itertools.cycle(colours)))

    # assign each dataframe column a colour based on its sensor
    cmap = {}
    columns = {x for x in data.columns if x != 'timestamp'}
    for column in columns:
        try:
            matching_sensor = next(x for x in unique_sensor_name if x in column)
        except StopIteration:
            continue

        cmap[column.split(' ')[0]] = colour_map[matching_sensor]

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
    plot_raw(data, units, infile, unique_units, cmap, marks)

    # Summary statistics plot with the same basic structure as the plot above.
    plot_summary(data, units, infile, unique_units)


##############################################################################
if __name__ == '__main__':
    main()
