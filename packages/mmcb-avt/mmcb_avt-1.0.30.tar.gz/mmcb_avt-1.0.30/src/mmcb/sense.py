#!/usr/bin/env python3
"""
Environmental data logging for the ATLAS inner tracker (ITK) pixels
multi-module cycling box.

This script is expected to run on a Raspberry Pi.
"""

import argparse
import contextlib
import datetime
import functools
import gc
import logging
import os
import time
import warnings

import numpy as np
import pandas as pd
from tables import NaturalNameWarning
import zmq

from mmcb.common import UNIT
from mmcb import configure_environment as ce


##############################################################################
# command line option handler
##############################################################################


def check_file_exists(filename):
    """
    check if file exists

    --------------------------------------------------------------------------
    args
        val : string
            filename, e.g. 'config.txt'
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError(f'{filename}: file does not exist')

    return filename


def check_arguments():
    """
    Handle command line options.

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns : class argparse.ArgumentParser
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='ATLAS inner tracker (ITK) pixels multi-module cycling\
        box environmental logging script. This script logs various parameters\
        including temperature, humidity and pressure from various sensors.\
        Dew points are calculated for all sensors that supply both humidity\
        and temperature; these calculated values are echoed to the screen for\
        information, but are not written to the log file. Sensors are\
        connected by I2C in the current test setup, mostly via Qwiic I2C\
        multiplexer(s). This script will run continuously until terminated.\
        The human-readable log file on mass storage will be updated every\
        data point, and raw data is also streamed to an HDF5 file. If this\
        script was started from a remote client with nohup then use:\
        kill -s INT <PID> or kill -SIGINT <PID> to terminate the script.'
    )
    parser.add_argument(
        'config_filename',
        nargs=1,
        metavar='configuration file',
        help='Specify the file containing the test setup configuration.',
        type=check_file_exists,
        default=None,
    )
    parser.add_argument(
        '--label',
        nargs=1,
        metavar='filename_label',
        help='Add a label suffix to the timestamp when writing to filenames.\
        Use speech marks around the label if it contains spaces.',
        default=None,
    )
    parser.add_argument(
        '-i', '--interval',
        metavar='sampling_interval',
        help=(
            'Set sampling interval in seconds. Default is 10s. '
            'This software will limit the rate at which data is acquired '
            'based on the specified interval. This will provide evenly '
            'spaced data points in the log file as long as the time to '
            'acquire data from all sensors is shorter than the specified '
            'interval period.'
        ),
        default=10,
        type=float,
    )

    return parser.parse_args()


##############################################################################
# utilities
##############################################################################


def environment_string(padding, sensor_details, sensor_reading):
    """
    Create a string for the given sensor and reading such that values will
    align in sequential log entries for the given unit.

    --------------------------------------------------------------------------
    args
        padding : int
            make some effort to keep entries in sequential log lines aligned
        sensor_details : string
            e.g. 'hyt_M1 °C'
        sensor_reading : float
            e.g. 20.438564365500824
    --------------------------------------------------------------------------
    returns : string
        e.g.
            'hyt_M1   20.438 °C'
    --------------------------------------------------------------------------
    """
    name, _, unit = sensor_details.rpartition(' ')
    return f'{name} {sensor_reading:{padding}.3f} {unit:<3}'


def fill_missing(line, reference_fields):
    """
    Make sure the line dict has key/value pairs for every element(key) in set
    reference_fields.

    --------------------------------------------------------------------------
    args
        line : dict
            holds all data points from all connected sensors for the current
            timestamp
        reference_fields : set
            e.g. {'AMBIENT °C', 'OVEN_AIR °C', 'timestamp'}
    --------------------------------------------------------------------------
    returns : none
        line : dict
            mutable type amended in place, no explicit return
    --------------------------------------------------------------------------
    """
    for field in reference_fields:
        if field not in line:
            line[field] = np.nan


def timestamp_to_utc(tref):
    """
    Converts a timestamp into a string in UTC to the nearest second.

    e.g. 1567065212.1064236 converts to '20190829_075332'

    --------------------------------------------------------------------------
    args
        tref : float
            time in seconds since the epoch
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    utc = datetime.datetime.utcfromtimestamp(tref).isoformat().split('.')[0]
    return utc.replace('-', '').replace(':', '').replace('T', '_')


##############################################################################
# generate log lines from dict
##############################################################################


def generate_log_lines(enviro_string, line):
    """
    Generate all the necessary log lines for one point in time. Temperature,
    humidity and pressure each have their own log lines.

    --------------------------------------------------------------------------
    args
        enviro_string : functools.partial
            function that takes a data point and returns a formatted string
            suitable for use as part of a log line
        line : dict
            holds all data points from all connected sensors for the current
            timestamp
    --------------------------------------------------------------------------
    returns : none
        no explicit return: lines written to log file
    --------------------------------------------------------------------------
    """
    for unit in UNIT.__dict__.values():
        string = ', '.join(
            enviro_string(sensor, reading)
            for sensor, reading in line.items()
            if sensor.endswith(f' {unit}')
        )
        if string:
            if UNIT.calculated_dew_point in string:
                # show on-screen only, do not write to log file
                logging.debug(string)
            else:
                logging.info(string)


##############################################################################
# share data with iv.py
##############################################################################


def emit_data(message_tx, zmq_skt):
    """
    Receive acquired environmental data and send it to iv.py.

    To avoid dropped data packets ZeroMQ REQ/REP is the pattern used, though
    the desired behaviour is really PUB/SUB. PUB/SUB is unreliable in its
    basic form, and can't be used. With REQ/REP iv.py is obliged to
    reply to the message this thread sends, but that reply can be discarded.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        zmq_skt : zmq.sugar.socket.Socket
            ZeroMQ socket to communicate with iv.py
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    # send message then attempt to receive reply
    try:
        zmq_skt.send_json(message_tx)
    except zmq.error.ZMQError:
        pass
    else:
        # receive and discard reply from iv.py
        with contextlib.suppress(zmq.error.ZMQError):
            zmq_skt.recv_json()


##############################################################################
def main():
    """
    Read the test setup from a configuration file.
    Build lists of sensors and initialise everything from there.
    Run.
    """

    # This suppresses warnings issued due to characters such as degree
    # symbols being used in column titles, e.g. 'OVEN_AIR °C'. Certain access
    # methods within PyTables rely on these strings matching this regex
    # ^[a-zA-Z_][a-zA-Z0-9_]*$ though non-matching column titles seems to be
    # tolerated reading/writing hdf5 files via Pandas.
    warnings.filterwarnings('ignore', category=NaturalNameWarning)

    ##########################################################################
    # read command line arguments
    ##########################################################################

    args = check_arguments()

    ##########################################################################
    # enable logging to file and screen
    ##########################################################################

    # date and time to the nearest second when the script was started
    filename = timestamp_to_utc(time.time())

    if args.label is not None:
        filename = f'{filename}_{args.label[0].replace(" ", "_")}'

    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    # set the minimum log-level required by any subsequent handler
    logging.getLogger('').setLevel(logging.DEBUG)

    # log to file
    fha = logging.FileHandler(f'{filename}.log')
    fha.setLevel(logging.INFO)
    fha.setFormatter(formatter)
    logging.getLogger('').addHandler(fha)

    # log to screen
    # all calculated figures are DEBUG and therefore shown on screen only
    cha = logging.StreamHandler()
    cha.setLevel(logging.DEBUG)
    cha.setFormatter(formatter)
    logging.getLogger('').addHandler(cha)

    # set logging time to UTC to match session timestamp
    logging.Formatter.converter = time.gmtime

    ##########################################################################
    # zeromq simple request-reply to send environmental data to iv.py
    ##########################################################################

    context = zmq.Context()
    zmq_skt = context.socket(zmq.REQ)
    # zmq.RCVTIMEO and zmq.SNDTIMEO specified in units of milliseconds
    zmq_skt.setsockopt(zmq.RCVTIMEO, 200)
    zmq_skt.setsockopt(zmq.SNDTIMEO, 200)
    zmq_skt.setsockopt(zmq.DELAY_ATTACH_ON_CONNECT, 1)
    # iv.py uses 5555 for communication with liveplot.py
    with contextlib.suppress(zmq.error.ZMQError):
        zmq_skt.connect("tcp://localhost:5556")

    send_data_to_iv_script = functools.partial(emit_data, zmq_skt=zmq_skt)

    ##########################################################################
    # set up environment
    ##########################################################################

    print('Configure test environment: start')
    testenv = ce.TestEnvironment(args.config_filename[0])
    print('Configure test environment: complete')

    padding = len('1000.000')
    enviro_string = functools.partial(environment_string, padding)
    dict_to_log_lines = functools.partial(generate_log_lines, enviro_string)

    ##########################################################################
    # define reference fields
    #
    # The reference fields will be all the keys returned by
    # read_all_sensors(), where key/value pairs represent the sampled
    # parameters and their values for any given timestamp.
    #
    # example returned values from read_all_sensors():
    # {
    #     'timestamp': 1650734619.065016,
    #     'smc_vacuum': -0.3395540799999992,
    #     'ntc_temperature': -61.19908797184263,
    #     ...
    # }
    #
    # for which fields will be {'timestamp', 'smc_vacuum', 'ntc_temperature'}
    #
    ##########################################################################

    print('Initial sensor read')

    fields = set(testenv.read_all_sensors())

    if not fields:
        print('No sensors found, exiting.')
        return

    ##########################################################################
    # acquire data
    ##########################################################################

    print('Acquiring data')
    with pd.HDFStore(f'{filename}.h5', mode='w', complib='blosc:zstd', complevel=5) as datafile:
        with contextlib.suppress(KeyboardInterrupt):
            while True:
                time_0 = time.monotonic()

                measurements = testenv.read_all_sensors()

                send_data_to_iv_script(measurements)

                dew_points = testenv.calculate_dew_points(measurements)
                dict_to_log_lines({**measurements, **dew_points})

                # fields must be identical for when writing to hdf5 files so add
                # any missing fields
                fill_missing(measurements, fields)

                datafile.append(
                    'key',
                    pd.DataFrame([measurements]),
                    format='table',
                    data_columns=True
                )

                # Force garbage collection. Without this, tracemalloc indicates
                # ~/pve/lib/python3.9/site-packages/tables/filters.py:184
                # adds ~3KiB per loop, which can be troublesome for data
                # acquisitions that run for a few weeks.
                gc.collect()

                tdif = time.monotonic() - time_0
                if tdif < args.interval:
                    time.sleep(args.interval - tdif)


##############################################################################
if __name__ == '__main__':
    main()
