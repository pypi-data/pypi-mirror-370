#!/usr/bin/env python3
"""
Generates IV and (optional) IT plots using power supplies connected by RS232.

Tests will be run concurrently on *ALL* detected PSUs unless
otherwise specified.

Supported power supplies:

    hvpsu : keithley 2410, 2614b; ISEG SHQ 222M, 224M

Safety:

To protect devices under test, the script ensures that the rate of change of
voltage is strictly limited to no more than one 10V step per second.

The script sets the current limit on the power supply, and will stop the
test early if the leakage current exceeds a slightly lower figure.
"""

import argparse
import collections
import concurrent.futures as cf
import contextlib
import csv
import ctypes
import datetime
import functools
import itertools
import logging
import math
import multiprocessing as mp    # Process, Queue
import os
import pathlib
import platform
import random
import socket
import statistics as stat
import sys
import threading
import time

import matplotlib
# agg is used only for writing plots to files, not to the window manager
# this option is set to avoid problems running the script on remote hosts
# over ssh, matplotlib.use must be called in this exact position
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import serial
import zmq

from yoctopuce import yocto_api as yapi
from yoctopuce import yocto_temperature as ytemp
from yoctopuce import yocto_humidity as yhumi

from mmcb import common
from mmcb import lexicon
from mmcb import sequence


##############################################################################
# command line option handler
##############################################################################

def check_settling_time(val):
    """
    Check settling time is reasonable.

    --------------------------------------------------------------------------
    args
        val : float
            allowable percentage deviation from mean
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = float(val)
    if not 0.25 <= val <= 10:
        raise argparse.ArgumentTypeError(
            f'{val}: settling time should between 0.25 and 10 seconds.')
    return val


def check_minutes(val):
    """
    check basic validity of minutes value

    --------------------------------------------------------------------------
    args
        val : float
            allowable percentage deviation from mean
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = int(val)
    if not 0 <= val <= 2880:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'hold time in minutes should be less than 2880 (48 hours)')
    return val


def check_percent(val):
    """
    check basic validity of percentage value

    --------------------------------------------------------------------------
    args
        val : float
            allowable percentage deviation from mean
    --------------------------------------------------------------------------
    returns : float
    --------------------------------------------------------------------------
    """
    val = float(val)
    if val >= 1000:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'percentage deviation from the mean should be less than 1000')
    return val


def check_psunum(val):
    """
    check basic validity of number

    --------------------------------------------------------------------------
    args
        val : int
            number of power supplies to emulate
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = int(val)
    if val <= 0:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'number of emulated power supplies should be 1 or more')
    return val


def check_samples(val):
    """
    check basic validity of number of samples

    --------------------------------------------------------------------------
    args
        val : int
            number of samples
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = int(val)
    if not 10 <= val <= 100:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'number of samples should be between 10 and 100')
    return val


def check_stepsize(val):
    """
    Expect int step size

    --------------------------------------------------------------------------
    args
        val : int
            step size in volts
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = abs(int(val))
    if not 1 <= val <= 10:
        raise argparse.ArgumentTypeError(
            f'{val}: value should be between 1 and 10')
    return val


def check_voltage(val):
    """
    check basic validity of relative movement value

    --------------------------------------------------------------------------
    args
        val : int
            bias voltage
    --------------------------------------------------------------------------
    returns : int
    --------------------------------------------------------------------------
    """
    val = int(val)
    if not -1100 <= val <= 1100:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'voltage should be between -1100V and 1100V')
    return val


def check_arguments(settings):
    """
    handle command line options

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns
        settings : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Script to generate IV (and optionally IT) plots using\
        Keithley 2410 and 2614b power supplies over RS232. ISEG SHQ\
        222M and 224M power supplies may also be used though these are slow\
        to converge to set voltages (and may never converge when the set\
        voltage is in the region -10 <= V <= 10) hence the test may take a\
        long time to complete. If detected, data from YoctoPuce humidity and\
        PT100 temperature sensors will be incorporated into exported data and\
        (appropriate) plots. Tests will be run concurrently on *ALL* detected\
        high-voltage PSUs unless specifically excluded using --alias. Support\
        requests to: Alan Taylor, Physics Dept.,\
        University of Liverpool, avt@hep.ph.liv.ac.uk')
    parser.add_argument(
        'voltage', nargs='?', metavar='voltage',
        help='value in volts',
        type=check_voltage, default=None)
    parser.add_argument(
        '--stepsize', nargs=1, metavar='stepsize',
        help='Use a constant step size between 1V and 10V, the sign is not\
        important as the script will decide this itself. The default if\
        this option is not specified is to use smaller\
        step sizes when close to zero volts,\
        from 0 to +/-10 with 1V steps,\
        then -10 to +/-50 with 5V steps,\
        then -50 to +/-N with 10V steps.',
        type=check_stepsize, default=None)
    parser.add_argument(
        '--range', nargs=1, metavar='filename',
        help='Rather than using the step size parameters detailed in\
        the --stepsize option above, read a range and step definition from\
        a CSV file. Multiple ranges with different step sizes may be defined.\
        The file format is as follows. Comments starting with # are\
        supported - on any line if a # is found, it and any text to the right\
        are ignored. Blank lines are allowed. Valid lines contain either (1)\
        a single value that defines the default step size in volts that\
        applies over the entire range from 0V to the maximum test voltage\
        (only provide this type of line once, valid value is any integer from\
        1 to 10), and (2) three comma-separated values: start, stop, step\
        (provide as many of these as required - the step size should be\
        between 1 and 10). The sign of any of the supplied numbers will be\
        ignored since the script uses the range and step definitions to\
        build a generic number sequence appropriate for forward or reverse\
        bias operation.',
        type=common.check_file_exists, default=None)
    parser.add_argument(
        '--omitreturn',
        action='store_true',
        help='Only record data outbound (typically 0V to -nV) and do not\
        record data for the return (typically -nV to 0V). By default the\
        script records data for both outbound and return.')
    parser.add_argument(
        '--atlas',
        action='store_true',
        help='Enable various adjustments for the ATLAS project. When returning\
        to the original voltage after testing, add in an additional delay\
        between each voltage step to help avoid the current limit being\
        exceeded.')
    parser.add_argument(
        '--hold', nargs=1, metavar='minutes',
        help='After the initial outbound IV test, perform an IT test for the\
        given number of minutes, logging the current values and timestamps.\
        A value of 0 will hold indefinitely until the user manually\
        terminates the test with by pressing the \'q\' key followed by enter',
        type=check_minutes, default=None)

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '-f', '--front',
        action='store_true',
        help='Use front output on PSU.')
    group1.add_argument(
        '-r', '--rear',
        action='store_true',
        help='Use rear output on PSU.')

    # --json requires --itk_serno to be set
    parser.add_argument(
        '--itk_serno', nargs=1, metavar='itk_serno',
        help='ATLAS ITk Pixel module serial number. Add this detail to plot\
        titles and to the JSON file output (see --json).',
        default='')
    parser.add_argument(
        '--json',
        action='store_true',
        help='Write a JSON file for each PSU channel that acquires data.')

    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset PSU before setting voltage. This is a diagnostic feature\
        to address topical issues, and should not normally be required')
    parser.add_argument(
        '--forwardbias',
        action='store_true',
        help='Allow the script to create voltage sequences containing\
        positive voltages. As a safety feature, by default the script only\
        allows reverse bias, limiting the output to voltages from 0 to -nV and\
        preventing positive voltage outputs.')
    parser.add_argument(
        '--settle',
        action='store_true',
        help='At each voltage step, monitor PSU current values until they\
        become stable, then capture final value. If the value does not\
        stabilise, a mean value of the last few values is returned.\
        Parameters are --pc and --samples. Explicitly setting either of\
        those parameters implies --settle.')
    parser.add_argument(
        '--settling_time', nargs=1, metavar='settling_time',
        help='Manually set the time between setting the voltage and measuring\
        the voltage and current.',
        type=check_settling_time, default=[2.0])
    parser.add_argument(
        '--pc', nargs=1, metavar='percentage',
        help='the percentage deviation of individual values from the mean\
        that is deemed acceptable, the default value is 5). Setting this\
        value implies --settle.',
        type=check_percent, default=None)
    parser.add_argument(
        '--samples', nargs=1, metavar='samples',
        help='samples is the total number of times data is captured from the\
        PSU for each voltage step. Sensible values are probably less than\
        100. The default (and minimum) value is 10. Setting this value\
        implies --settle.',
        type=check_samples, default=None)
    parser.add_argument(
        '--sense', nargs=1, metavar='sensor_name',
        help='Specify the name of the environmental sensor to receive data\
        from as it appears in sense.py logs. This option ONLY applies to the\
        ATLAS inner tracker (ITK) pixels multi-module cycling box.',
        default=None)
    parser.add_argument(
        '-l', '--limit', nargs=1, metavar='threshold',
        help='The threshold value above which limiting action will be taken.\
        This is the compliance value to be set on the PSU channel, when this\
        value is reached the PSU channel changes from being a constant voltage\
        source to become a constant current source. The default value if unset\
        is 10uA; the minimum possible value is 1nA. Values can be specified\
        with either scientific (10e-9) or engineering notation (10n).',
        type=common.check_current, default=[10e-6])
    parser.add_argument(
        '--label', nargs=1, metavar='plot_label',
        help='if just a single PSU is being used, use this text on the plot\
        instead of the PSU serial number. Use speech marks around the label if\
        it contains spaces.',
        default=None)
    parser.add_argument(
        '--alias', nargs=1, metavar='filename',
        help='Substitute power supply channel identifiers for human readable\
        descriptions in plots and log files, and allow power supply channels\
        to be individually disabled. This option reads in a CSV file where\
        each line consists of five fields: enable, model, serial number,\
        channel identifier, and description. Use the model and serial number\
        as reported by detect.py. Anything after a # is treated as a comment.\
        If the enable field is left empty that will enable the power supply\
        channel (use no/off/disable to disable it). The channel identifier\
        should be omitted for single channel power supplies.',
        type=common.check_file_exists, default=None)
    parser.add_argument(
        '--svg', action='store_true',
        help='Plot to the Scalable Vector Graphics (SVG) file format instead\
        of the default Portable Network Graphics (PNG). For the kind of\
        sparse plots typically generated by this script, SVG files are\
        better quality, have smaller file sizes, and render faster than PNG.')
    parser.add_argument(
        '-i', '--initial', action='store_true',
        help='Return power supply to its initial voltage after completion of\
        test.')
    parser.add_argument(
        '-d', '--debug', nargs=1, metavar='number',
        help='Allow testing of the script when a power supply is not\
        available. The number indicates the quantity of single channel power\
        supplies to emulate.',
        type=check_psunum, default=None)

    args = parser.parse_args()

    if args.json and not args.itk_serno:
        parser.error("--json requires --itk_serno to be set")

    handle_complex_arguments(settings, args)
    handle_simple_arguments(settings, args)


def handle_complex_arguments(settings, args):
    """
    handle command line arguments that:

    (1) cannot be combined
    (2) affect the values of other arguments
    (3) have values that require transformation

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        args : argparse.Namespace
            command line arguments and values
    --------------------------------------------------------------------------
    returns
        settings : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    # do not change settings if none given
    if args.front:
        settings['rear'] = False
    elif args.rear:
        settings['rear'] = True

    if args.voltage is not None:
        # perform basic safety checks
        if not args.forwardbias and args.voltage > 0:
            sys.exit('to enable positive voltages use --forwardbias')
        elif args.forwardbias and args.voltage < 0:
            sys.exit('to enable negative voltages omit --forwardbias')
        else:
            settings['voltage'] = args.voltage
    else:
        # set sensible defaults
        settings['voltage'] = 80 if args.forwardbias else -80

    if args.settle or args.samples or args.pc:
        settings['settle'] = True

    if args.atlas:
        settings['atlas'] = True

    if args.pc:
        settings['pc'] = args.pc[0] / 100

    if args.alias:
        filename = args.alias[0]
        common.read_aliases(settings, filename)

    if args.range:
        filename = args.range[0]
        sequence.read_user_range_step_file(settings, filename)

    if args.stepsize:
        settings['stepsize'] = args.stepsize[0]
        if args.atlas:
            print('--stepsize overrides default behaviour for --atlas')

    settings['current_limit'] = args.limit[0]
    settings['settling_time'] = args.settling_time[0]


def handle_simple_arguments(settings, args):
    """
    handle command line arguments that require a simple assignment

    These assignments could be performed manually which would make the
    code trivial to follow but rather long. The implementation here works well
    as the number of (simple) command line arguments grows.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        args : argparse.Namespace
            command line arguments and values
    --------------------------------------------------------------------------
    returns
        settings : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    # collate all possible command line arguments and their respective values
    all_command_line_arguments = ((argument, getattr(args, argument))
                                  for argument in dir(args))

    # limit the selection to command line options that:
    #
    # (1) have values that can be stored without transformation
    # (2) the user has actually specified
    stored_as_boolean = frozenset(
        ('forwardbias', 'initial', 'json', 'omitreturn', 'reset', 'svg')
    )
    stored_as_list = frozenset(
        ('debug', 'hold', 'label', 'samples', 'sense', 'itk_serno')
    )
    simple_assignments = stored_as_boolean.union(stored_as_list)
    shortlist = ((argument, value)
                 for argument, value in all_command_line_arguments
                 if argument in simple_assignments and value)

    # assign given arguments and values to settings
    for argument, value in shortlist:
        try:
            settings[argument] = value[0]
        except TypeError:
            # object is not subscriptable (does not belong to stored_as_list)
            settings[argument] = value


##############################################################################
# logging debug messages
##############################################################################

def write_debug_information_to_log():
    """
    Write basic information about the environment to the log file (but not to
    the screen).

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    # Ensure that the command line invocation could be copied and pasted back
    # into the terminal by wrapping strings with spaces with speech marks.
    sav = (
        f'"{a}"' if ' ' in a else a
        for a in sys.argv
    )

    common.log_with_colour(logging.DEBUG, f'invocation: {" ".join(sav)}')
    common.log_with_colour(logging.DEBUG, f'platform: {platform.platform()}')
    messages = [
        f'python: {platform.python_version()}',
        f'pyserial: {serial.VERSION}',
        f'matplotlib: {matplotlib.__version__}'
    ]
    common.log_with_colour(logging.DEBUG, ', '.join(messages))


##############################################################################
# utilities
##############################################################################

def scale_timestamps(timestamps):
    """
    Amend timestamps so the start of the experiment is zero, and scale values
    so they are sensible for human-readable plot axes.

    --------------------------------------------------------------------------
    args
        timestamps : list of floats
            values in seconds since the epoch
            e.g.
            [1627383466.9587026, 1627383472.445601, 1627383476.924957, ...]
    --------------------------------------------------------------------------
    returns
        values : list of floats
            e.g.
            [0.0, 0.09144830703735352, 0.16610424121220907, ...]
        units : string
            'minutes' or 'hours'
    --------------------------------------------------------------------------
    """
    mintimestamp = min(timestamps)
    minutes_of_available_data = (max(timestamps) - mintimestamp) / 60

    if minutes_of_available_data > 180:
        scale = 3600
        units = 'hours'
    else:
        scale = 60
        units = 'minutes'

    values = [(t - mintimestamp) / scale for t in timestamps]

    return values, units


##############################################################################
# set psu values
##############################################################################

def configure_psu(settings, pipeline, ser, dev):
    """
    Set the initial conditions for the power supply.

    Keithley: With the range being used, voltages can only be specified to two
    decimal places, though setting digits in the second decimal place is
    unreliable (read back values do not always match) so limit values to be
    set to 1 decimal place.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns : bool, float, float
        success (True if the device was found, False otherwise)
        measured_voltage
        measured_current
    --------------------------------------------------------------------------
    """
    # constrain the voltage to be set to the given number of decimal places
    voltage = common.decimal_quantize(0, settings['decimal_places'])

    if settings['reset'] and dev.manufacturer == 'keithley':
        # reset to default conditions, output off
        command_string = lexicon.power(dev.model, 'reset')
        common.send_command(pipeline, ser, dev, command_string)

        # allow device time to complete reset before sending more commands
        time.sleep(0.5)

    # set voltage to zero and set compliance
    if dev.manufacturer == 'keithley':
        # limit the number of characters sent
        # e.g. reduce 7.999999999999999e-05 to '8.00e-05'
        compliance = f'{settings["current_limit"]:.2e}'
        command_string = lexicon.power(dev.model, 'configure',
                                       voltage, compliance,
                                       channel=dev.channel)
        common.send_command(pipeline, ser, dev, command_string)

    elif dev.manufacturer == 'iseg':
        command_string = lexicon.power(dev.model, 'set auto ramp',
                                       channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

        command_string = lexicon.power(dev.model, 'set char delay')
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

        volts_per_second = 20
        command_string = lexicon.power(dev.model,
                                       'set voltage max rate of change',
                                       volts_per_second,
                                       channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    # change front/rear routing if requested, otherwise do not change it
    if settings['rear'] is not None and dev.model == '2410':
        destination = 'REAR' if settings['rear'] else 'FRON'
        command_string = lexicon.power('2410', 'set route', destination)
        common.send_command(pipeline, ser, dev, command_string)

    # set output on (Keithley only, ISEG SHQ hardware only switch on front panel)
    if dev.manufacturer == 'keithley':
        command_string = lexicon.power(dev.model, 'output on', channel=dev.channel)
        common.send_command(pipeline, ser, dev, command_string)

    # allow a little time for the current to settle before reading
    time.sleep(1)

    return read_psu_and_verify(settings, pipeline, ser, voltage, dev)


def in_compliance(ser, pipeline, dev):
    """
    Check if the power supply channel reports it is in compliance - i.e. the
    set current limit has been exceeded - and it is now acting as a constant
    current source instead of a constant voltage source.

    Note that for the ISEG SHQ with the uA range selected, a current overflow
    (OVERFLOW on display) transient is often seen when ramping down to a low
    voltage, may need to check a second time to be sure.

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        incomp : bool
            True if the PSU is in compliance
    --------------------------------------------------------------------------
    """
    incomp = report_status = False
    command_string = lexicon.power(dev.model, 'check compliance', channel=dev.channel)
    response = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.model == '2410':
        if response in {'0', '1'}:
            incomp = response == '1'
        else:
            report_status = True

    elif dev.model == '2614b':
        if response in {'true', 'false'}:
            incomp = response == 'true'
        else:
            report_status = True

    elif dev.manufacturer == 'iseg':
        if '=ERR' in response:
            incomp = '=ERR' in response
            # clear the error by repeating the reading (must read response)
            common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if report_status:
        message = f'{dev.ident}, problem reading compliance status'
        common.log_with_colour(logging.WARNING, message)

    return incomp


def read_psu_set_voltage(pipeline, ser, dev):
    """
    Read the voltage that the PSU has been asked to output (rather than the
    actual instantaneous voltage measured at the output terminals).

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        set_volt : float or None
            float if the value could be read or None if it could not
    --------------------------------------------------------------------------
    """
    set_volt = None

    command_string = lexicon.power(dev.model, 'read set voltage', channel=dev.channel)
    local_buffer = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.manufacturer == 'iseg' and dev.model == 'shq':
        set_volt = common.iseg_value_to_float(local_buffer)

    elif dev.manufacturer == 'keithley' and dev.model in {'2410', '2614b'}:
        if dev.model == '2410':
            # e.g. '-5.000000E+00,-1.005998E-10,+9.910000E+37,+1.185742E+04,+2.150800E+04'
            item = next(iter(local_buffer.split(',')))
        else:
            # e.g. '-5.00000e+00'
            item = local_buffer

        try:
            set_volt = float(item)
        except (TypeError, ValueError):
            common.log_with_colour(logging.WARNING, f'{dev.ident}, problem reading set voltage')

    return set_volt


def read_psu_and_verify(settings, pipeline, ser, desired_voltage, dev):
    """
    Verify that the set voltage read back from the psu matches the
    desired value, then return the measured voltage and current.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        desired_voltage : decimal.Decimal
            voltage that was set
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        success : bool
            True if a matching voltage was read back
        measured_voltage : float
        measured_current : float
    --------------------------------------------------------------------------
    """
    set_volt = read_psu_set_voltage(pipeline, ser, dev)
    if set_volt is not None:
        set_voltage = common.decimal_quantize(set_volt, settings['decimal_places'])

        if set_voltage == desired_voltage:
            success = True
        else:
            success = False
            common.log_with_colour(logging.WARNING,
                                   'set voltage differs from voltage read back')

        measured_voltage, measured_current = common.read_psu_measured_vi(pipeline, ser, dev)
    else:
        success = False
        measured_voltage = measured_current = None

    return success, measured_voltage, measured_current


def current_limit(settings, pipeline, measured_current,
                  measured_voltage, set_voltage, ser, dev):
    """
    Test whether the measured leakage current has exceeded one of two limits,
    both related to the maximum leakage current value supplied as an argument
    to command line option --limit <n>.

    (1) Soft limit: has the measured leakage current exceeded a threshold
    value, calculated as a percentage of <n>

    (2) Hard limit: has the power supply channel - having had its current limit
    set to <n> - reported its compliance bit has been set.

    General notes on Keithley 2410 behaviour:

    When the device reports compliance, current is clamped to a value below -
    not at - the set limit, e.g. for this contrived scenario using a 2nA
    limit:

    INFO : 2410 4343654, IV, -10, V, -9.578194e+00, V, -1.954002e-09, A
    WARNING : 2410 4343654 reports compliance
    INFO : 2410 4343654, IV, -15, V, -1.058404e+01, V, -1.954872e-09, A
    WARNING : 2410 4343654 reports compliance
    WARNING : 2410 4343654 set and measured voltage differ

    And sometimes the device does not report compliance, even when it is
    clearly operating as a current source (10nA limit here):

    INFO : 2410 4343654, IV, -15, V, -1.290832e+01, V, -9.956312e-09, A
    WARNING : 2410 4343654 leakage current exceeded soft limit
    WARNING : 2410 4343654 set and measured voltage differ

    The hard limit test employs an additional check of whether the measured
    voltage differs from the set voltage, an indication that the power supply
    may have changed from being a constant voltage source to a constant
    current source. This additional check is necessary since bit 14 of the
    measurement event register - which indicates compliance - seems to be set
    as the leakage current approaches the compliance limit, rather than
    actually reaching it.

    Using miniterm to monitor bit 14 with :STAT:MEAS?, and gradually
    increasing the reverse bias voltage it can be seen that bit 14 is set
    before the compliance limit is reached and before the "Cmpl" text flashes
    on the front panel display.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        measured_current : float
        measured_voltage : float
        set_voltage : float
        ser : serial.Serial
            reference for serial port
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns : bool
        True if either limit has been exceeded, False otherwise
    --------------------------------------------------------------------------
    """
    # the soft limit is set as a percentage of the value provided by command
    # line option --limit (or default value)
    soft_limit = abs(measured_current) >= abs(settings['current_limit'])
    if soft_limit:
        common.log_with_colour(logging.WARNING,
                               f'{dev.ident} leakage current exceeded soft limit')

    # always run this test even if the soft limit has been exceeded, as it's
    # valuable to have the power supply channel compliance status reported in
    # the log for debugging purposes
    hard_limit = in_compliance(ser, pipeline, dev)
    if hard_limit:
        common.log_with_colour(logging.WARNING, f'{dev.ident} reports compliance')

    if dev.manufacturer != 'iseg':
        # setting exact voltages for ISEG devices may be troublesome

        asv = abs(set_voltage)
        margin = 1 if asv > 10 else max(asv * 0.1, 0.1)
        lower_bound = asv - margin
        upper_bound = asv + margin
        within_bounds = lower_bound < abs(measured_voltage) < upper_bound

        if not within_bounds:
            common.log_with_colour(logging.WARNING,
                                   f'{dev.ident} set and measured voltage differ')

        if dev.model == '2410':
            # see the function docstring above for why this additional check is
            # necessary
            hard_limit = hard_limit and not within_bounds

    return soft_limit or hard_limit


##############################################################################
# threads
##############################################################################

def check_key(graceful_quit):
    """
    Identify whether the user has decided to stop testing early by pressing
    'q' then 'enter' (both key presses required to avoid an accidental quit),
    and set a flag in shared memory as True indicating this has occurred.

    The status of this flag can be read from within the individual threads
    operating the power supplies, which can then handle exiting gracefully.

    --------------------------------------------------------------------------
    args
        graceful_quit : multiprocessing.Value(ctypes.c_bool, False)
            shared memory containing a single boolean value to indicate
            whether the user has requested the script terminate early
    --------------------------------------------------------------------------
    returns : no explicit return
        graceful_quit : multiprocessing shared memory may be amended
    --------------------------------------------------------------------------
    """
    while True:
        try:
            line = sys.stdin.read(1).lower()
        except AttributeError:
            pass
        else:
            if line == 'q':
                common.log_with_colour(logging.INFO, 'user requested graceful quit')
                graceful_quit.value = True


def liveplot(pipeline, zmq_skt):
    """
    Receive data from all power supplies under test, and send the data to
    an external plotter (liveplot.py).

    To avoid dropped data packets ZeroMQ REQ/REP is the pattern used, though
    the desired behaviour is really PUB/SUB. PUB/SUB is unreliable in its
    basic form, and can't be used. With REQ/REP liveplot.py is obliged to
    reply to the message this thread sends, but that reply can be discarded.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        zmq_skt : zmq.sugar.socket.Socket
            ZeroMQ socket to communicate with an external live-plotting script
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    while True:
        message_tx = pipeline.liveplot.get()

        # sentinel value to quit
        if message_tx is None:
            break

        # send message then attempt to receive reply
        try:
            zmq_skt.send_json(message_tx)
        except zmq.error.ZMQError:
            # liveplot.py is not running
            pass
        else:
            # receive and discard reply from liveplot.py
            with contextlib.suppress(zmq.error.ZMQError):
                zmq_skt.recv_json()


def sense(pipeline, zmq_skt, settings):
    """
    Receive data packets from sense.py via ZeroMQ REQ/REP, and place them on a
    queue for processing later.

    If a zmq.error.ZMQError exception occurs while attempting to bind to a
    socket, this is almost always caused by a previous invocation of this
    script having been forcibly terminated. When the current invocation tries
    to bind, this will fail.

    In this case the user should find the PID owning the port currently, in
    the case below this is 32539:

    pi@raspberrypi:~/dev/1d-phantom/utilities $ sudo netstat -ltnp
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address Foreign Address State  PID/Program name
    tcp        0      0 0.0.0.0:5556  0.0.0.0:*       LISTEN 32539/python3
    tcp        0      0 0.0.0.0:22    0.0.0.0:*       LISTEN 776/sshd
    tcp        0      0 127.0.0.1:631 0.0.0.0:*       LISTEN 27597/cupsd
    tcp        0      0 127.0.0.1:25  0.0.0.0:*       LISTEN 992/exim4
    tcp6       0      0 :::22         :::*            LISTEN 776/sshd
    tcp6       0      0 ::1:631       :::*            LISTEN 27597/cupsd
    tcp6       0      0 ::1:25        :::*            LISTEN 992/exim4

    pi@raspberrypi:~/dev/1d-phantom/utilities $ ps -ef | grep 32539
    pi  1977  1624  0 17:33 pts/19 00:00:00 grep --color=auto 32539
    pi 32539 31217  0 16:07 pts/13 00:00:26 python3 ./iv.py -5 --sense hyt221_x
    pi 32546 32539  0 16:07 pts/13 00:00:00 python3 ./iv.py -5 --sense hyt221_x

    And we can regain access by killing the PID:

    kill -9 32539

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        zmq_skt : zmq.sugar.socket.Socket
            ZeroMQ socket to communicate with external environmental sensing
            script
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns : no explicit return
        pipeline.sense_dict : multiprocessing.Manager().dict()
            repository for the most recently acquired environmental data
            received from sense.py
    --------------------------------------------------------------------------
    """
    # configure communication with sense.py
    # Use REP/REQ (with handshaking) instead of PUB/SUB to avoid packet loss
    port = 5556
    try:
        zmq_skt.bind(f'tcp://*:{port}')
    except zmq.error.ZMQError as zerr:
        message = f'ZeroMQ: {zerr} when binding to port {port}'
        common.log_with_colour(logging.WARNING, message)
        message = 'ZeroMQ: find PID of current owner with: sudo netstat -ltnp'
        common.log_with_colour(logging.WARNING, message)
    else:
        try:
            while True:
                # receive message from sense.py, this intentionally blocks hence
                # why this is a daemon thread
                message = zmq_skt.recv_json()

                if message is not None and settings['sense'] is not None:
                    valid = {k: v for k, v in message.items() if settings['sense'] in k}
                    if valid:
                        pipeline.sense_dict = valid

                # send a minimal message back to sense.py for handshake
                zmq_skt.send_json(None)
        except zmq.error.ZMQError:
            zmq_skt.close()


##############################################################################
# generation of fake data for --debug <n> command line option
##############################################################################

def debug_generate_data(settings, ivtdat):
    """
    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
    --------------------------------------------------------------------------
    returns
        ivtdat : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    # outbound iv
    debug_iv_test(settings, ivtdat)

    # hold stability
    debug_hold_stability(settings, ivtdat)

    # return iv
    if not settings['omitreturn']:
        debug_iv_test(settings, ivtdat, reverse=True)


def debug_hold_stability(settings, ivtdat):
    """
    Generate simulated hold stability data.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
    --------------------------------------------------------------------------
    returns
        ivtdat : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    hold = settings['hold']
    voltage = settings['voltage']

    if hold is not None and hold >= 1:
        ivtdat.hold_voltage = voltage
        variation = random.uniform(1, 1.05)

        for minute in range(hold):
            ivtdat.hold_current.append(noisy(diode(voltage, variation)))
            ivtdat.hold_timestamp.append(noisy(minute))


def debug_iv_test(settings, ivtdat, reverse=False):
    """
    Generate simulated IV test data with the voltage sequence in the order
    given.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
        reverse : boolean
            reverse number sequence if True, False otherwise
    --------------------------------------------------------------------------
    returns
        ivtdat : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    start = 0
    stop = settings['voltage']
    variation = random.uniform(1, 1.1)

    if reverse:
        # this is a ramp-down IV
        # manually mark the point where the ramp-down data starts
        ivtdat.set_voltage.append('split')
        ivtdat.measured_current.append('split')
        ivtdat.measured_voltage.append('split')
        ivtdat.measured_timestamp.append('split')
        start, stop = stop, start

    variablestep = settings['stepsize'] is None
    for voltage in sequence.test_run(start, stop, settings['stepsize'],
                                     variablestep=variablestep,
                                     bespoke_sequence_lut=settings['bespoke_sequence_lut']):
        vpsu = noisy(voltage)
        ipsu = diode(vpsu, variation)

        ivtdat.set_voltage.append(voltage)
        ivtdat.measured_current.append(ipsu)
        ivtdat.measured_voltage.append(vpsu)
        ivtdat.measured_timestamp.append(time.time())


def diode(voltage, variation):
    """
    A very rough approximation of the leakage current of a reverse biased
    diode.

    --------------------------------------------------------------------------
    args
        voltage : numeric
        variation : float
            this value, when held constant over a range of voltages, allows
            this function to be used to generate a series of subtly different
            curves, approximating the variation that might be expected in a
            test environment
    --------------------------------------------------------------------------
    returns : float
        leakage current
    --------------------------------------------------------------------------
    """
    return pow(abs(float(voltage)), 0.25) * -0.5e-8 * variation


def noisy(value):
    """
    Add a small amount of noise to the supplied argument.

    --------------------------------------------------------------------------
    args
        value : float
    --------------------------------------------------------------------------
    returns : float
    --------------------------------------------------------------------------
    """
    adjust = value * 0.005
    return random.uniform(value - adjust, value + adjust)


##############################################################################
# temperature and humidity sensing
##############################################################################

def add_environmental_string(text, sensor_readings, unit):
    """
    Append temperature data to log string.

    --------------------------------------------------------------------------
    args
        text : string
            e.g. '2614b 4428182 a, IV, -2, V, -1.99294e+00, V, 4.76837e-14, A'
        sensor_readings : dict
            e.g. {'PT100MK1-DC3D6': 22.31, 'PT100MK1-DC392': 19.16}
        unit : string
            '\u00b0C' or 'RH%' for temperature and humidity respectively
    --------------------------------------------------------------------------
    returns : string
        e.g.
            ('2614b 4428182 a, IV, -2, V, -1.99294e+00, V, 4.76837e-14, A, '
             'PT100MK1-DC3D6, 22.31, °C, PT100MK1-DC392, 19.45, °C')
    --------------------------------------------------------------------------
    """
    strings = (f'{name}, {reading:.2f}, {unit}'
               for name, reading in sensor_readings.items())

    return ', '.join(itertools.chain([text], strings))


def get_environmental_data(settings, pipeline):
    """
    Get environmental data from the appropriate source.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
    --------------------------------------------------------------------------
    returns
        temp : dict
        humi : dict
    --------------------------------------------------------------------------
    """
    if settings['sense'] is None:
        # read directly from Yoctopuce sensors
        temp = read_environment(settings['temperature_sensors'], pipeline)
        humi = read_environment(settings['humidity_sensors'], pipeline)
    elif settings['sense'] and pipeline.sense_dict:
        # receive data sent by sense.py using ZeroMQ
        temp = {
            k.split('_temperature')[0]: v
            for k, v in pipeline.sense_dict.items()
            if '_temperature' in k
        }
        humi = {
            k.split('_relative_humidity')[0]: v
            for k, v in pipeline.sense_dict.items()
            if '_relative_humidity' in k
        }
    else:
        temp = {}
        humi = {}

    return temp, humi


def register_hub(location):
    """
    Initialise the Yoctopuce API to use sensor modules from the given
    location.

    If argument location contains an IP address, the call to
    yapi.YAPI.RegisterHub will take 20 seconds to time-out if there is
    no response.

    It cannot be inferred from a return value of yapi.YAPI.SUCCESS that
    sensor modules will be found in the given location.

    --------------------------------------------------------------------------
    args
        location : string
            either 'usb' or an ip address e.g. '192.168.0.200'
    --------------------------------------------------------------------------
    returns
        registered : boolean
            True if the API initialisation was successful, False otherwise.
    --------------------------------------------------------------------------
    """
    registered = False
    errmsg = yapi.YRefParam()

    try:
        registered = yapi.YAPI.RegisterHub(location, errmsg) == yapi.YAPI.SUCCESS
    except ImportError:
        common.log_with_colour(logging.WARNING, 'yoctopuce: unable to import YAPI shared library')
        if sys.platform == 'darwin':
            message = ('allow libyapi.dylib in macOS System Preferences, '
                       'Security and Privacy, General')
            common.log_with_colour(logging.WARNING, f'yoctopuce: {message}')

    else:
        if not registered:
            common.log_with_colour(logging.WARNING, f'yoctopuce: {errmsg.value}')

    return registered


def yoctopuce_api_set(settings):
    """
    Initialise the Yoctopuce API to use sensor modules attached to a
    YoctoHub-Ethernet if one is present. Otherwise, defer to USB connected
    sensor modules.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns
        registered : boolean
            True if the API initialisation was successful, False otherwise.
    --------------------------------------------------------------------------
    """
    registered = False

    # Preferentially configure the Yoctopuce API to access sensor modules via
    # a YoctoHub-Ethernet at the given IP address.
    #
    # The call to register_hub will take 10 seconds to time out if there is no
    # response from a YoctoHub-Ethernet at the given IP address, so check that
    # a basic connection attempt is successful before calling.
    #
    # The YoctoHub-Ethernet should respond to connection attempts on
    # ports 80 and 4444.
    ip_address = settings['temperature_ip']
    ports = {80, 4444}
    if any(port_responsive(ip_address, port) for port in ports):
        registered = register_hub(ip_address)

    # fall back to allowing the API to access Yoctopuce modules connected to
    # local USB ports
    if not registered:
        registered = register_hub('usb')

    return registered


def detect_yoctopuce_sensors(settings):
    """
    Detect environmental sensors applicable to the test environment.

    PT100 sensors are used for temperature monitoring, and a Yocto-Meteo-V2
    is used for humidity monitoring. The Sensiron SHT35 based Yocto-Meteo-V2
    also contains pressure and temperature sensors which are ignored; pressure
    isn't important for this experiment, and its temperature sensor can't
    measure below -45°C which limits its utility when working with dry ice.

    This is run before any IV testing threads are run, hence the API can be
    accessed without using the lock.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns
        settings : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    if not yoctopuce_api_set(settings):
        return

    # collect temperature sensors
    # ytemp.YTemperature.FirstTemperature() will find *all* modules
    # capable of reading temperature including dedicated temperature
    # modules (Yocto-PT100) as well as modules that acquire multiple
    # parameters (Yocto-Meteo-V2)
    sensors = {}
    sensor = ytemp.YTemperature.FirstTemperature()
    while sensor is not None:
        if sensor.isOnline():
            name = sensor.get_friendlyName().partition('.')[0]

            sensors[name] = sensor
            common.log_with_colour(logging.INFO,
                                   f'yoctopuce: temperature sensor found: {name}')

        sensor = sensor.nextTemperature()

    # write found sensors to settings, display for user
    if sensors:
        settings['temperature_sensors'] = sensors
    else:
        common.log_with_colour(logging.WARNING,
                               'yoctopuce: no temperature sensors found')

    # collect humidity sensors
    sensors = {}
    sensor = yhumi.YHumidity.FirstHumidity()
    while sensor is not None:
        if sensor.isOnline():
            name = sensor.get_friendlyName().partition('.')[0]
            sensors[name] = sensor
            common.log_with_colour(logging.INFO,
                                   f'yoctopuce: humidity sensor found: {name}')
        sensor = sensor.nextHumidity()

    # write found humidity sensors to settings, display for user
    if sensors:
        settings['humidity_sensors'] = sensors
    else:
        common.log_with_colour(logging.WARNING,
                               'yoctopuce: no humidity sensors found')


def port_responsive(host, port):
    """
    Establish whether the port at the given ip address is responsive to a
    connection attempt. A timeout period of 2 seconds is used.

    In essence, check if the node is present without having to handle the
    platform dependent nature of ping.
    --------------------------------------------------------------------------
    args
        host : string
            local IPV4 address e.g. '192.168.0.200'
        port : int
            port number, e.g. 22
    --------------------------------------------------------------------------
    returns : bool
        True if node is responsive, False otherwise
    --------------------------------------------------------------------------
    """
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.settimeout(2)

    with contextlib.closing(skt) as sock:
        return sock.connect_ex((host, port)) == 0


def read_environment(sensor_details, pipeline):
    """
    Read environmental data (temperature or humidity) from given Yoctopuce
    sensors.

    This function is called from within threads, and there is a risk that the
    Yoctopuce API could be accessed concurrently, hence the presence of the
    lock here.

    --------------------------------------------------------------------------
    args
        sensor_details : dictionary
            {sensor_name: sensor_identifier, ...}
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
    --------------------------------------------------------------------------
    returns
        results : dict
            e.g. {'PT100MK1-DC3D6': 22.31, 'PT100MK1-DC392': 19.16}
    --------------------------------------------------------------------------
    """
    results = {}

    if sensor_details is not None:
        with pipeline.yapiaccess:
            results = {name: sensor.get_currentValue()
                       for name, sensor in sensor_details.items()
                       if sensor.isOnline()}

    return results


def report_environmental_issues(ivtdat, dev, test_iv, outbound=True):
    """
    --------------------------------------------------------------------------
    args
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
        dev : instance of class common.Channel()
            contains details of a device and its serial port
        test_iv : bool
            True = data from IV test, False = data from IT test
        outbound : bool
            For lists that may contain a 'split' marker, outbound = True
            selects items before the marker, False selects items after the
            marker. For other lists, this is ignored.
    --------------------------------------------------------------------------
    returns : none
        entries may be made in the log file
    --------------------------------------------------------------------------
    """
    tolerance_symbol = chr(177)
    degree_symbol = chr(176)
    # allow up to +/- 5% around mean
    ten_percent = 0.05
    categories = {'temperature': f'{degree_symbol}C', 'humidity': 'RH%'}

    for category, units in categories.items():
        # measurement is in the following generic form:
        # {'PT100MK1-DC3D6': [21.25, 21.25, 21.26, 21.26, ..., 21.24],
        # 'PT100MK1-DC392': [20.9, 20.92, 20.92, 20.94, ..., 20.94]}
        measurement = ivtdat.extract_environmental_data(category, test_iv, outbound)

        for sensor, readings in measurement.items():
            try:
                mean = stat.mean(readings)
            except stat.StatisticsError:
                continue

            outliers = (r for r in readings if not math.isclose(r, mean,
                                                                rel_tol=ten_percent,
                                                                abs_tol=0.5))
            if any(outliers):
                message = (f'{dev.ident}, {sensor} ({category} {units}), '
                           f'{tolerance_symbol}5% tolerance exceeded')
                common.log_with_colour(logging.WARNING, message)


##############################################################################
# run test profile
##############################################################################

def get_iv_data_from_psu(dev, settings, pipeline, graceful_quit):
    """
    Apply the given range of bias voltages with given step size and read back
    the respective leakage currents.

    Exit early if leakage current exceeds software current limit.
    --------------------------------------------------------------------------
    args
        dev : instance of class common.Channel()
            contains details of a device and its serial port
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        graceful_quit : multiprocessing.Value(ctypes.c_bool, False)
            shared memory containing a single boolean value to indicate
            whether the user has requested the script terminate early
    --------------------------------------------------------------------------
    returns
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
    --------------------------------------------------------------------------
    """
    ivtdat = common.Packet(
        dev.manufacturer,
        dev.model,
        dev.serial_number,
        dev.channel,
        dev.ident,
        settings['itk_serno'],
    )

    ##########################################################################
    # DEBUG - ignore power supplies, generate data internally
    ##########################################################################
    if settings['debug'] is not None:
        debug_generate_data(settings, ivtdat)
        return ivtdat
    ##########################################################################

    with serial.Serial(port=dev.port) as ser:
        ser.apply_settings(dev.config)

        if dev.model == '2410':
            command_string = lexicon.power(dev.model, 'clear event registers')
            common.send_command(pipeline, ser, dev, command_string)

        # obtain starting voltage
        initial_voltage = read_psu_set_voltage(pipeline, ser, dev)
        if initial_voltage is not None:
            common.log_with_colour(logging.INFO,
                                   (f'{dev.ident}, initial psu voltage is '
                                    f'{common.si_prefix(initial_voltage)}V'))

            ###################################################################
            # (1) gradually move from starting voltage to one step from zero
            target_voltage = 0
            start = True
            transition_voltage(settings, pipeline, initial_voltage,
                               target_voltage, ser, dev, start)

            # set to zero volts, configure range, set compliance etc...
            configure_psu(settings, pipeline, ser, dev)

            ###################################################################
            common.log_with_colour(logging.WARNING,
                                   (f'{dev.ident}, during IV test phase, '
                                    'press \'q\' then \'enter\' '
                                    'to exit the test early'))

            ###################################################################
            # (2) gather data for IV plot
            # (part 1) ramp-up IV test (typically 0V to -nV)
            proceed_with_testing, early_termination_voltage = \
                run_iv_test(settings, pipeline, ser, ivtdat, graceful_quit, dev)

            if proceed_with_testing:
                # report environmental status only if variance is excessive
                report_environmental_issues(ivtdat, dev, test_iv=True, outbound=True)

                # (part 2) hold for number of minutes specified
                hold_stability(settings, pipeline, graceful_quit, ser,
                               read_psu_set_voltage(pipeline, ser, dev),
                               ivtdat, dev)

                # report environmental status only if variance is excessive
                report_environmental_issues(ivtdat, dev, test_iv=False)

                if not settings['omitreturn']:
                    # (part 3) ramp-down IV test (typically -nV to 0V)
                    run_iv_test(settings, pipeline, ser, ivtdat, graceful_quit, dev,
                                intercept=early_termination_voltage, reverse=True)

                    # report environmental status only if variance is excessive
                    report_environmental_issues(ivtdat, dev, test_iv=True, outbound=False)

            ###################################################################
            # (3) bring the power supply's voltage back to its initial state
            # if it's safe to do so, otherwise move to 0V
            if proceed_with_testing and settings['initial']:
                target_voltage = initial_voltage
                log_message = 'returning to initial psu voltage'
            else:
                target_voltage = 0
                log_message = 'moving to 0V'

            voltage_after_iv = read_psu_set_voltage(pipeline, ser, dev)
            if voltage_after_iv != initial_voltage:
                if voltage_after_iv is not None:
                    common.log_with_colour(logging.INFO, f'{dev.ident}, {log_message}')
                    start = False
                    transition_voltage(settings, pipeline, voltage_after_iv,
                                       target_voltage, ser, dev, start)
                else:
                    if target_voltage == 0:
                        log_message = log_message.replace('moving', 'move')
                    else:
                        log_message = log_message.replace('returning', 'return')

                    common.log_with_colour(logging.ERROR, f'{dev.ident}, cannot {log_message}')
        else:
            common.log_with_colour(logging.WARNING,
                                   f'{dev.ident}, cannot be read from, check output')

    return ivtdat


def hold_stability(settings, pipeline, graceful_quit, ser, voltage, ivtdat, dev):
    """
    Perform an IT test for the given duration.

    FIXME : this function needs to use time.monotonic() for sleep delays only

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        graceful_quit : multiprocessing.Value(ctypes.c_bool, False)
            shared memory containing a single boolean value to indicate
            whether the user has requested the script terminate early
        ser : serial.Serial
            reference for serial port
        voltage : float
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        ivtdat : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    hold_minutes = settings['hold']
    if hold_minutes is None:
        return

    indefinite = hold_minutes == 0
    sample_period_seconds = 5

    ###########################################################################
    # display voltage hold (I-T) summary
    ###########################################################################

    hold_sta_raw = datetime.datetime.now(datetime.UTC)
    hold_end_raw = hold_sta_raw + datetime.timedelta(minutes=hold_minutes)
    hold_end = hold_end_raw.isoformat().split('.')[0].replace('T', ' ')

    if indefinite:
        tdesc = 'indefinitely'
    else:
        suffix = '' if hold_minutes == 1 else 's'
        tdesc = f'for {hold_minutes} minute{suffix} until {hold_end} UTC'

    common.log_with_colour(
        logging.INFO,
        f'{dev.ident}, IT, holding at {voltage:.0f}V {tdesc}'
    )

    ###########################################################################

    ivtdat.hold_voltage = voltage
    timestamp_mono = time.monotonic()
    end_time_mono = timestamp_mono + hold_minutes * 60

    while timestamp_mono < end_time_mono or indefinite:
        if graceful_quit.value:
            break

        _, ipsu = common.read_psu_measured_vi(pipeline, ser, dev)

        # add environmental data if available
        temp, humi = get_environmental_data(settings, pipeline)

        ivtdat.hold_current.append(ipsu)
        ivtdat.hold_timestamp.append(time.time())
        ivtdat.hold_temperature.append(temp)
        ivtdat.hold_humidity.append(humi)

        text = f'{dev.ident}, IT, {ipsu:>13.6e}, A'
        text = add_environmental_string(text, temp, '\u00b0C')
        common.log_with_colour(
            logging.INFO,
            add_environmental_string(text, humi, 'RH%')
        )

        timestamp_mono = common.rate_limit(
            timestamp_mono, sample_period_seconds
        )


def rate_limit_delay(settings, previous_voltage, next_voltage):
    """
    Supply a delay sufficient for the rate of change of voltage not to exceed
    10V/s in standard configuration, or 2V/s using the ATLAS workaround.

    In principle, this function allows the delay between small voltage steps
    (1V, 5V) to be shorter, reducing the time to perform the whole test, which
    has value when using iv.py and a supporting script to cycle the
    bias voltage between 0V and -1100V several hundred times.

    However, since this script may be used with different power supplies with
    varying performance - to be cautious - a minimum settling time is enforced.
    If HV-cycling becomes common usage, it may be beneficial to write minimum
    settling times for each power supply type (derived from empirical testing)
    in the cache file written by detect.py, to take advantage of time savings.

    Note that this is NOT the settling time between setting the voltage and
    reading back V/I. That is handled in common.set_psu_voltage_and_read().

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        previous_voltage : numeric
        next_voltage : numeric
    --------------------------------------------------------------------------
    returns
        duration : numeric
            value in seconds
    --------------------------------------------------------------------------
    """
    if settings['atlas']:
        duration = 5
    else:
        max_voltage_step = 10

        try:
            delta_v = abs(next_voltage - previous_voltage)
        except TypeError:
            # previous_voltage is None
            delta_v = max_voltage_step

        duration = delta_v / max_voltage_step

    return duration


def run_iv_test(settings, pipeline, ser, ivtdat, graceful_quit, dev,
                intercept=None, reverse=False):
    """
    Run IV test with the voltage sequence in the order given.

    Notes on function time delays:

    (1) Before the measurement: settling time. The time between setting the
        voltage and subsequently measuring the voltage and current.

    (2) After the measurement: rate limit. An additional delay that serves to
        limit the average rate of change in volts per second.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        ivtdat : instance of class Packet
            contains data for a given power supply channel's IV and IT curves
        graceful_quit : multiprocessing.Value(ctypes.c_bool, False)
            shared memory containing a single boolean value to indicate
            whether the user has requested the script terminate early
        dev : instance of class common.Channel()
            contains details of a device and its serial port
        intercept : int or None
            if this function is being called a second time after the previous
            run terminated early because of a software current over-limit
            event, the voltage the previous run terminated at can be
            supplied here to avoid subjecting the chip to a potentially
            damaging large step voltage change
        reverse : boolean
            reverse number sequence if True, False otherwise
    --------------------------------------------------------------------------
    returns
        proceed_with_testing : boolean
            True when at least one voltage did not trigger a software current
            limit event, False otherwise
        last_successful_voltage : int or None
            None if test terminates normally, or int if not
        ivtdat : no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    prv = pri = None
    buf = collections.deque([], 3)

    start = 0
    stop = settings['voltage'] if intercept is None else intercept
    if reverse:
        # this is a ramp-down IV, manually mark the point where the ramp-down
        # data starts
        ivtdat.set_voltage.append('split')
        ivtdat.measured_current.append('split')
        ivtdat.sigma_current.append('split')
        ivtdat.measured_voltage.append('split')
        ivtdat.measured_timestamp.append('split')
        ivtdat.measured_temperature.append('split')
        ivtdat.measured_humidity.append('split')
        start, stop = stop, start
        suffix = '(return)'
    else:
        suffix = '(outbound)'

    common.log_with_colour(logging.INFO, f'{dev.ident}, IV, running test {suffix}')

    early_termination = False
    last_successful_voltage = None
    padding = len(str(settings['voltage']))
    variablestep = settings['stepsize'] is None
    for voltage in sequence.test_run(start, stop, settings['stepsize'],
                                     variablestep=variablestep,
                                     bespoke_sequence_lut=settings['bespoke_sequence_lut']):
        if graceful_quit.value:
            break

        # set parameters for voltage/time rate limiting
        time_0 = time.monotonic()
        duration = rate_limit_delay(settings, last_successful_voltage, voltage)

        # obtain readings from power supply
        # set voltage -> settling time -> read back values
        vpsu, ipsu = common.set_psu_voltage_and_read(
            settings, pipeline, voltage, ser, dev, settings['settling_time']
        )

        if settings['settle']:
            vpsu, ipsu, sigma_current = settle(settings, pipeline, ser, vpsu, ipsu, dev)
        else:
            sigma_current = 0.0

        if vpsu is None or ipsu is None:
            graceful_quit.value = True
            break

        # send data packet to liveplot.py
        pipeline.liveplot.put([dev.ident, voltage, ipsu, reverse])

        # display summary of power supply readings
        text = (f'{dev.ident}, IV, '
                f'{voltage:>{padding}d}, V, '
                f'{vpsu:>13.6e}' + ', V, '
                f'{ipsu:>13.6e}' + ', A')

        # add environmental data if available
        temp, humi = get_environmental_data(settings, pipeline)

        text = add_environmental_string(text, temp, '\u00b0C')
        common.log_with_colour(logging.INFO,
                               add_environmental_string(text, humi, 'RH%'))

        # current limit protection (absolute threshold)
        over_threshold = current_limit(settings, pipeline,
                                       ipsu, vpsu, voltage, ser, dev)

        # rate of change of leakage current (breakdown detection)
        # only check when voltage is moving away from 0V
        if not reverse and not over_threshold:
            if prv is not None:
                try:
                    gradient = abs((pri - ipsu) / (prv - vpsu))
                except ZeroDivisionError:
                    gradient = 0
                    common.log_with_colour(logging.INFO,
                                           (f'{dev.ident}, IV, '
                                            f'previous ({prv:.6e}V) and prevailing ({vpsu:.6e}V) '
                                            'voltages are identical'))

                if len(buf) == buf.maxlen and gradient > stat.mean(buf) * 20 and abs(ipsu) > 2e-09:
                    common.log_with_colour(logging.INFO,
                                           (f'{dev.ident}, IV, '
                                            'leakage current excessive rate of change'))
                buf.append(gradient)
            prv, pri = vpsu, ipsu

        # store data in all cases
        ivtdat.set_voltage.append(voltage)
        ivtdat.measured_current.append(ipsu)
        ivtdat.sigma_current.append(sigma_current)
        ivtdat.measured_voltage.append(vpsu)
        ivtdat.measured_timestamp.append(time.time())
        ivtdat.measured_temperature.append(temp)
        ivtdat.measured_humidity.append(humi)

        if not over_threshold and voltage != 0:
            # mark this as a safe voltage to quickly return to,
            # in case there is a problem at the next voltage
            last_successful_voltage = voltage

        if not reverse and over_threshold:
            # one or more limits have been exceeded on the outbound IV
            # return to last safe voltage level and exit from this test early
            #
            # do not force exit for return IV, since the voltage is reducing
            # anyway
            early_termination = True
            if last_successful_voltage is not None:
                common.log_with_colour(logging.INFO,
                                       (f'{dev.ident}, IV, '
                                        'returning to last safe voltage '
                                        f'({last_successful_voltage:d}V)'))
                common.set_psu_voltage(settings, pipeline, last_successful_voltage,
                                       ser, dev)
            break

        # voltage/second rate limit
        tdif = time.monotonic() - time_0
        if tdif < duration:
            time.sleep(duration - tdif)

    if (early_termination and last_successful_voltage is None) or graceful_quit.value:
        common.log_with_colour(logging.INFO, f'{dev.ident}, IV, halting further testing')
        proceed_with_testing = False
    else:
        proceed_with_testing = True

    return proceed_with_testing, last_successful_voltage


def settle(settings, pipeline, ser, initial_voltage, initial_current, dev):
    """
    This function averages successive readings to smooth noisy IV curves.

    When used with large sample counts, it can also be used to obtain more
    reliable results from devices that require long settling times, where
    current values read shortly after a change of voltage are not likely to be
    representative of stable operating conditions.

    Method:

    Measured current and voltage values are read from the PSU in quick
    succession and loaded into a fixed-size N-element LIFO queue. Once the
    queue is full, a test is made to see if all contained values are within a
    given distance from their mean value. If the test passes, the function
    terminates early.

    If the test fails, another current/voltage pair is loaded (discarding the
    oldest entry in the process) and the test is repeated.  This process is
    repeated a user-specified number of times.

    In both cases, the mean values of the voltages and currents contained in
    the queues are returned.

    The function is tolerant to problems reading values from the PSU, though
    any such occurrence should be rare.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        initial_voltage : float
        initial_current : float
        dev : instance of class common.Channel()
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        final_value : tuple
            (True, float, float) if satisfactory result found otherwise
            (False, None, None)
    --------------------------------------------------------------------------
    """
    # no need to clear these deques since stale values will be pushed out
    # before any calculations are performed
    dev.measured_voltages.append(initial_voltage)
    dev.measured_currents.append(initial_current)

    rel_tol = settings['pc']
    max_samples = settings['samples']
    max_attempts = max_samples * 2
    samples_received = 1
    attempts = 1

    while samples_received < max_samples and attempts < max_attempts:
        attempts += 1

        volt, curr = common.read_psu_measured_vi(pipeline, ser, dev)
        if volt is None:
            continue

        samples_received += 1
        dev.measured_voltages.append(volt)
        dev.measured_currents.append(curr)

        if samples_received >= dev.window_size:
            meai = stat.mean(dev.measured_currents)
            similar = (math.isclose(i, meai, rel_tol=rel_tol) for i in dev.measured_currents)
            if all(similar):
                break

    if samples_received >= dev.window_size:
        final_value = stat.mean(dev.measured_voltages), stat.mean(dev.measured_currents), stat.stdev(dev.measured_currents)
    else:
        final_value = None, None, None
        common.log_with_colour(logging.WARNING, f'{dev.ident}, underflow')

    return final_value


def transition_voltage(settings, pipeline, initial_voltage,
                       target_voltage, ser, dev, start):
    """
    Handle voltage transitions (1) before commencement of IV testing, and (2)
    after.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        initial_voltage : float
            set voltage at present
        target_voltage : float
            voltage to transition to
        ser : serial.Serial
            reference for serial port
        dev : instance of class common.Channel()
            contains details of a device and its serial port
        start : bool
            True if this is the initial voltage to 0V transition,
            or the end-of-test 0V to initial voltage transition
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    # don't perform transition if voltages are closer than 1mV
    if math.isclose(initial_voltage, target_voltage, abs_tol=0.001):
        return

    message = (f'{dev.ident}, transitioning '
               f'from {common.si_prefix(initial_voltage)}V '
               f'to {common.si_prefix(target_voltage)}V')
    common.log_with_colour(logging.INFO, message)

    if dev.manufacturer == 'keithley':
        number_sequence = sequence.to_start if start else sequence.to_original
        timestamp = None
        duration = 5 if settings['atlas'] else 1
        step = 10

        for voltage in number_sequence(initial_voltage, target_voltage, step):
            timestamp = common.rate_limit(timestamp, duration)
            common.set_psu_voltage(settings, pipeline, voltage, ser, dev)

        if start:
            time.sleep(duration)

    elif dev.manufacturer == 'iseg':
        # use power supply's internal ramp feature to avoid having manage
        # the ISEG SHQ's tardy response time

        # read voltage rate of change
        command_string = lexicon.power(dev.model,
                                       'read max rate of change',
                                       channel=dev.channel)
        max_vroc = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

        # set voltage rate of change for ramp
        volts_per_second = 2 if settings['atlas'] else 10
        command_string = lexicon.power(dev.model,
                                       'set voltage max rate of change',
                                       volts_per_second,
                                       channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

        # auto ramp will progress towards the given voltage at the given rate
        command_string = lexicon.power(dev.model,
                                       'set voltage',
                                       target_voltage,
                                       channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

        # wait to reach given voltage
        common.wait_for_voltage_to_stabilise(ser, pipeline, dev, target_voltage)

        # revert voltage rate of change to original value
        command_string = lexicon.power(dev.model,
                                       'set voltage max rate of change',
                                       max_vroc,
                                       channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    common.log_with_colour(logging.INFO, f'{dev.ident}, transition complete')


##############################################################################
# save files
##############################################################################

def save_data(data, filename):
    """
    Write recorded data to mass storage.

    --------------------------------------------------------------------------
    args
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        filename : string
            filename without extension
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    logging.info('Saving data')

    # compressed python pickle format, for post-processing
    common.data_write(data, f'{filename}.pbz2')

    # generic csv
    with open(f'{filename}.csv', 'w', encoding='utf-8') as csvfile:
        row = csv.writer(csvfile)
        common.write_consignment_csv(data, row)


##############################################################################
# plot (power supply data)
##############################################################################

def create_plots(settings, data, filename, session):
    """
    Create and write plots to mass storage.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        filename : string
            filename without extension
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    logging.info('Creating plots')

    # create directory for plots
    directory = f'{filename}_plots'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # create list of colours from a ten-entry colour map
    #
    # the blue colour at index 0 is used for the temperature y-axis in function
    # save_individual_stability_plots(), so omit this initial blue from the
    # palette used for plotting other curves
    #
    # see: https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
    colors = [plt.cm.tab10(x) for x in range(1, 10)]

    # set matplotlib defaults
    matplotlib.rcParams.update({
        # remove chartjunk
        'axes.spines.top': False,
        'axes.spines.right': False,
        # fontsize of the x and y labels
        'axes.labelsize': 'medium',
        # fontsize of the axes title
        'axes.titlesize': 'medium',
        # fontsize of the tick labels
        'xtick.labelsize': 'small',
        'ytick.labelsize': 'small',
        # fontsize of plot-line labels
        'legend.fontsize': 'xx-small'})

    # plot all IV curves
    save_combined_iv_plot(settings, colors, data, directory, session)
    save_individual_iv_plots(settings, colors, data, directory, session)

    # plot all leakage current stability curves
    save_combined_stability_plot(settings, colors, data, directory, session)
    save_individual_stability_plots(settings, colors, data, directory, session)

    # plot environmental data for iv outbound, it, and iv return as appropriate
    save_environmental_plots(settings, data, directory, session)


def save_combined_iv_plot(settings, colors, data, directory, session):
    """
    Create a single plot containing all the IV curves from all power supply
    channels.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        colors : list
            matplotlib colour map
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        directory : string
            directory to write plot to
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if len(data.packets) < 2:
        return

    fig, axis = plt.subplots(1, 1)

    for packet, color in zip(data.packets, itertools.cycle(colors)):
        outbound_v, return_v = common.list_split(packet.set_voltage)
        outbound_i, return_i = common.list_split(packet.measured_current)
        lt_out = '.-' if len(outbound_v) <= 30 else '-'

        if return_v or return_i:
            # outbound and return curves
            lt_ret = '.--' if len(return_v) <= 30 else '--'
            axis.plot(outbound_v, outbound_i, lt_out,
                      linewidth=0.5, markersize=1, color=color,
                      label=f'{packet.ident} outbound')
            axis.plot(return_v, return_i, lt_ret,
                      linewidth=0.5, markersize=1, color=color,
                      label=f'{packet.ident} return')
        else:
            # outbound curve only
            axis.plot(outbound_v, outbound_i, '-',
                      linewidth=0.5, markersize=1, color=color,
                      label=packet.ident)

    if len(data.packets) <= 12:
        axis.legend()

    if not data.forwardbias:
        axis.invert_xaxis()
        axis.invert_yaxis()

    axis.set_xlabel('bias voltage (V)')
    axis.set_ylabel('leakage current (A)')

    title_items = [
        'IV',
        data.label,
        ', '.join(x for x in [pathlib.Path(session).name, settings['itk_serno']] if x),
    ]
    plot_title = '\n'.join(x for x in title_items if x)
    axis.set_title(plot_title)

    axis.yaxis.set_major_formatter(EngFormatter(places=1))
    axis.xaxis.set_major_formatter(EngFormatter(places=0))

    plt.tight_layout()
    common.save_plot(settings, os.path.join(directory, 'iv_all'))

    plt.close(fig)


def save_individual_iv_plots(settings, colors, data, directory, session):
    """
    Create a separate plot for each individual power supply channel.
    each plot contains outbound and return IV curves.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        colors : list
            matplotlib colour map
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        directory : string
            directory to write plot to
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    for packet, color in zip(data.packets, itertools.cycle(colors)):
        fig, axis = plt.subplots(1, 1)

        outbound_v, return_v = common.list_split(packet.set_voltage)
        outbound_i, return_i = common.list_split(packet.measured_current)
        lt_out = '.-' if len(outbound_v) <= 30 else '-'

        if return_v or return_i:
            # outbound and return curves
            lt_ret = '.--' if len(return_v) <= 30 else '--'
            axis.plot(outbound_v, outbound_i, lt_out,
                      linewidth=0.5, markersize=1, color=color,
                      label='outbound')
            axis.plot(return_v, return_i, lt_ret,
                      linewidth=0.5, markersize=1, color=color,
                      label='return')
        else:
            # outbound curve only
            axis.plot(outbound_v, outbound_i, lt_out,
                      linewidth=0.5, markersize=1, color=color)

            if len(return_v) > 1:
                axis.legend()

        if not data.forwardbias:
            axis.invert_xaxis()
            axis.invert_yaxis()

        axis.set_xlabel('bias voltage (V)')
        axis.set_ylabel('leakage current (A)')

        title_items = [
            f'IV, {packet.ident}',
            data.label,
            ', '.join(x for x in [pathlib.Path(session).name, settings['itk_serno']] if x),
        ]
        plot_title = '\n'.join(x for x in title_items if x)
        axis.set_title(plot_title)

        axis.yaxis.set_major_formatter(EngFormatter(places=1))
        axis.xaxis.set_major_formatter(EngFormatter(places=0))

        plt.tight_layout()

        # replace spaces so files are easier to work with on the command line
        safe = packet.ident.replace(' ', '_')
        common.save_plot(settings, os.path.join(directory, f'iv_{safe}'))

        plt.close(fig)


def save_combined_stability_plot(settings, colors, data, directory, session):
    """
    Create a single plot containing all the IT curves from all power supply
    channels.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        colors : list
            matplotlib colour map
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        directory : string
            directory to write plot to
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    test_not_requested = data.hold is None
    insufficient_packets = len(data.packets) < 2
    some_data_missing = not all(packet.hold_voltage for packet in data.packets)
    if test_not_requested or insufficient_packets or some_data_missing:
        return

    fig, axis = plt.subplots(1, 1)

    for packet, color in zip(data.packets, itertools.cycle(colors)):
        initial_timestamp = min(packet.hold_timestamp)
        itt = [(x - initial_timestamp) / 60 for x in packet.hold_timestamp]
        linetype = '.-' if len(packet.hold_timestamp) <= 30 else '-'
        axis.plot(itt, packet.hold_current, linetype,
                  label=packet.ident, linewidth=0.5, markersize=1, color=color)

    axis.yaxis.set_major_formatter(EngFormatter(places=3))
    axis.invert_yaxis()
    axis.set_ylabel('leakage current (A)')
    axis.set_xlabel('time (minutes)')
    axis.legend()

    # title of plot
    title_items = [
        f'IT, {data.packets[0].hold_voltage:.0f}V',
        data.label,
        ', '.join(x for x in [pathlib.Path(session).name, settings['itk_serno']] if x),
    ]
    plot_title = '\n'.join(x for x in title_items if x)
    axis.set_title(plot_title)

    plt.tight_layout()
    common.save_plot(settings, os.path.join(directory, 'it_all'))

    plt.close(fig)


def save_individual_stability_plots(settings, colors, data, directory, session):
    """
    Create a separate plot for each individual power supply channel.
    each plot contains outbound and return IT curves.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        colors : list
            matplotlib colour map
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        directory : string
            directory to write plot to
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if data.hold is None or not all(packet.hold_voltage for packet in data.packets):
        return

    for packet, color in zip(data.packets, itertools.cycle(colors)):
        fig, axis = plt.subplots(1, 1)

        initial_timestamp = min(packet.hold_timestamp)
        itt = [(x - initial_timestamp) / 60 for x in packet.hold_timestamp]
        linetype = '.-' if len(packet.hold_timestamp) <= 30 else '-'
        axis.plot(itt, packet.hold_current,
                  linetype, linewidth=0.5, markersize=1, color=color)

        axis.yaxis.set_major_formatter(EngFormatter(places=3))
        axis.invert_yaxis()
        axis.set_ylabel('leakage current (A)')
        axis.set_xlabel('time (minutes)')

        # title of plot
        title_items = [
            f'IT, {packet.hold_voltage:.0f}V, {packet.ident}',
            data.label,
            ', '.join(x for x in [pathlib.Path(session).name, settings['itk_serno']] if x),
        ]
        plot_title = '\n'.join(x for x in title_items if x)
        axis.set_title(plot_title)

        plt.tight_layout()

        # replace spaces so files are easier to work with on the command line
        safe = packet.ident.replace(' ', '_')
        common.save_plot(settings, os.path.join(directory, f'it_{safe}'))

        plt.close(fig)


##############################################################################
# plot (environmental data)
##############################################################################

def save_environmental_plots(settings, data, directory, session):
    """
    Plot environmental data for each power supply channel on the same plot for
    iv outbound, it, and iv return.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        data : instance of common.Consignment()
            contains data for the whole data acquisition session
        directory : string
            directory to write plot to
        session : string
            date and time string, e.g. '20210719_143439'
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    # three plots: iv outbound, it, iv return
    options = [
        (True, True, 'IV outbound'),
        (False, True, 'IT'),
        (True, False, 'IV return')]

    # data.packets may contain multiple PSU channels
    for packet in data.packets:
        for test_iv, outbound, title in options:

            # Extract data for this individual plot. it_y1 and it_y1 are dicts
            # and may contain data for multiple sensors
            it_x = packet.extract_timestamp_data(test_iv, outbound)
            it_y1 = packet.extract_environmental_data('temperature', test_iv, outbound)
            it_y2 = packet.extract_environmental_data('humidity', test_iv, outbound)

            # assemble axes to plot
            y_axes = {'temperature (°C)': it_y1, 'humidity (RH%)': it_y2}
            y_axes_to_plot = {k: v for k, v in y_axes.items() if v}
            if len(y_axes_to_plot) > 1:
                # set matplotlib defaults
                matplotlib.rcParams.update({'axes.spines.right': True})

            # omit plots with incomplete data
            no_x_axis = not it_x
            no_y_axis = not y_axes_to_plot
            if no_x_axis or no_y_axis:
                continue

            # adjust timestamps so zero is the start of the experiment, and
            # they are scaled for readability.
            it_x, units = scale_timestamps(it_x)

            # plot
            fig, host = plt.subplots(figsize=(8, 4))
            fig.subplots_adjust(right=0.75)
            lwi = 0.4
            msi = 0.6
            tkw = {'size': 4, 'width': 1.5}

            # y-axes for temperature, humidity or both?
            for index, (axis_title, axis_data) in enumerate(y_axes_to_plot.items()):

                if index == 0:
                    color = 'g'
                    for sensor_name, sensor_data in axis_data.items():

                        # handle any missing initial sensor data
                        it_x_local = it_x[-len(sensor_data):]

                        host.step(it_x_local, sensor_data, color=color, where='post',
                                  linewidth=lwi, markersize=msi, label=sensor_name)

                    host.yaxis.label.set_color(color)
                    host.tick_params(axis='y', colors=color, **tkw)
                    host.set_ylabel(axis_title)
                else:
                    color = 'r'
                    par2 = host.twinx()
                    for sensor_name, sensor_data in axis_data.items():

                        # handle any missing initial sensor data
                        it_x_local = it_x[-len(sensor_data):]

                        par2.step(it_x_local, sensor_data, color=color, where='post',
                                  linewidth=lwi, markersize=msi, label=sensor_name)

                    par2.yaxis.label.set_color(color)
                    par2.tick_params(axis='y', colors=color, **tkw)
                    par2.set_ylabel(axis_title)

            host.set_xlabel(f'elapsed time ({units})')

            host.tick_params(axis='x', **tkw)

            title_items = [f'{title} environment, {session}', data.label, settings['itk_serno']]
            plot_title = '\n'.join(x for x in title_items if x)
            host.set_title(plot_title)

            plt.tight_layout()

            filename = f'{title}_env'.lower().replace(' ', '_')
            common.save_plot(settings, os.path.join(directory, filename))


##############################################################################
# main
##############################################################################

def main():
    """
    Collects IV and IT data from high-voltage power supplies over RS232.
    """
    # date and time to the nearest second when the script was started
    session = common.timestamp_to_utc(time.time())

    # ensure all files are contained in a directory
    if not os.path.exists(session):
        os.makedirs(session)
    session = os.path.join(session, session)

    settings = {
        'alias': None,
        'atlas': False,
        'bespoke_sequence_lut': None,
        'current_limit': None,
        'debug': None,
        'decimal_places': 1,
        'forwardbias': False,
        'hold': None,
        'humidity_sensors': None,
        'ignore': None,
        'initial': False,
        'itk_serno': '',
        'json': False,
        'label': None,
        'omitreturn': False,
        'pc': 0.05,
        'rear': None,
        'reset': None,
        'samples': 10,
        'sense': None,
        'settle': False,
        # default is set in the command line handler
        'settling_time': None,
        'stepsize': None,
        'svg': False,
        'temperature_ip': '192.168.0.200',
        'temperature_sensors': None,
        'voltage': 0,
        }

    ##########################################################################
    # read command line arguments
    ##########################################################################

    check_arguments(settings)

    ##########################################################################
    # establish which power supply channels to use, or generate some fake
    # channels if the user has requested debug
    ##########################################################################

    if settings['debug'] is not None:
        # create <n> number of power supplies on unique ports, to match the
        # value given in --debug <n>
        psus = None
        channels = []
        for serial_number in range(settings['debug']):
            port = f'debug_port_{serial_number}'
            serno = str(1234567 + serial_number)

            channels.append(common.Channel(port=port, config=None,
                                           serial_number=serno, model='debug',
                                           manufacturer='debug', channel=[],
                                           category='debug', release_delay=None,
                                           alias=None))
    else:
        # read all high-voltage power supplies from cache
        psus = common.cache_read(['hvpsu'])

        # convert the serial port centric cache entries to power supply
        # channels, and remove any channels the user doesn't want to use
        all_channels = common.ports_to_channels(settings, psus)
        channels = common.exclude_channels(settings, all_channels)

        if not channels:
            sys.exit('no devices to test')

    ##########################################################################
    # zeromq simple request-reply for interaction with external scripts
    ##########################################################################

    context = zmq.Context(io_threads=2)

    # liveplot.py interaction
    zmq_skt = context.socket(zmq.REQ)
    # zmq.RCVTIMEO and zmq.SNDTIMEO specified in units of milliseconds
    zmq_skt.setsockopt(zmq.RCVTIMEO, 200)
    zmq_skt.setsockopt(zmq.SNDTIMEO, 200)
    zmq_skt.setsockopt(zmq.DELAY_ATTACH_ON_CONNECT, 1)
    port = 5555
    try:
        zmq_skt.connect(f'tcp://localhost:{port}')
    except zmq.error.ZMQError as zerr:
        message = f'ZeroMQ: {zerr} when connecting to port {port}'
        common.log_with_colour(logging.WARNING, message)
        message = 'ZeroMQ: find PID of current owner with: sudo netstat -ltnp'
        common.log_with_colour(logging.WARNING, message)

    # sense.py interaction
    zmq_skt2 = context.socket(zmq.REP)

    ##########################################################################
    # enable logging to file and screen
    ##########################################################################

    log = f'{session}.log'
    logging.basicConfig(
        filename=log,
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s : %(message)s')
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # enable logging to screen
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # set logging time to UTC to match session timestamp
    logging.Formatter.converter = time.gmtime

    ##########################################################################
    # set up resources for threads
    ##########################################################################

    graceful_quit = mp.Value(ctypes.c_bool, False)

    class Production:
        """
        Queues and locks to support threaded operation.

        RS232 will not tolerate concurrent access. portaccess is used to
        prevent more than one thread trying to interact with the same RS232
        port at the same time for multi-channel power supplies. For
        simplicity, locks are created for all power supplies, even if they
        only have a single channel.

        The Python Yoctopuce API is not thread safe.
        """
        keypress_queue = mp.Queue()
        liveplot = mp.Queue()
        # maxsize is set to 1 to ensure the environmental data available to
        # this script is the most recently acquired from sense.py. We don't
        # care about older data acquisitions.
        sense = mp.Queue(maxsize=1)
        sense_dict = mp.Manager().dict()
        portaccess = {port: threading.Lock()
                      for port in {channel.port for channel in channels}}
        yapiaccess = threading.Lock()

    pipeline = Production()

    # input_thread: keypress detection for early test termination
    input_thread = threading.Thread(target=check_key, daemon=True,
                                    args=(graceful_quit, ))
    input_thread.start()

    # livp: collate sampled data points and send them to an external plotter
    livp = threading.Thread(target=liveplot, args=(pipeline, zmq_skt))
    livp.start()

    # sens: receive environmental data from sense.py
    sens = threading.Thread(target=sense, daemon=True, args=(pipeline, zmq_skt2, settings))
    sens.start()

    ##########################################################################
    # Commit command line invocation and core environment to log
    ##########################################################################

    write_debug_information_to_log()

    ##########################################################################
    # Check status of outputs and interlock (inhibit) on all power supplies
    ##########################################################################

    common.initial_power_supply_check(settings, pipeline, psus, channels)

    ##########################################################################
    # detect presence of temperature and humidity sensors
    ##########################################################################

    if not settings['debug']:
        if not settings['sense']:
            detect_yoctopuce_sensors(settings)
        else:
            message = 'direct access to Yoctopuce sensors disabled'
            common.log_with_colour(logging.INFO, message)
            message = ('listening for environmental data from '
                       f'sensor: {settings["sense"]}')
            common.log_with_colour(logging.INFO, message)

            # sense.py typically transmits data every 5 seconds. There's a
            # chance that if it and this script are started at the same time,
            # when this script records its first data point, no environmental data
            # will have been received yet. Provide a basic mitigation for this.
            for _ in itertools.repeat(None, 5):
                if pipeline.sense_dict:
                    break
                time.sleep(1)
            else:
                message = f'no data matching {settings["sense"]} being received from sense.py'
                common.log_with_colour(logging.WARNING, message)

    ##########################################################################
    # run iv test on all power supply channels concurrently
    ##########################################################################

    pipeline.liveplot.put('reset')

    if channels:
        common.log_with_colour(logging.INFO, 'Collecting IV data')

    environmental_data_present = bool(settings['temperature_sensors'])\
        or bool(settings['humidity_sensors'])
    consignment = common.Consignment(settings['label'], settings['alias'],
                                     settings['forwardbias'], settings['hold'],
                                     environmental_data_present)

    _gidfp_pf = functools.partial(get_iv_data_from_psu, settings=settings,
                                  pipeline=pipeline, graceful_quit=graceful_quit)
    with cf.ThreadPoolExecutor() as executor:
        board_iv = (executor.submit(_gidfp_pf, channel) for channel in channels)
        for future in cf.as_completed(board_iv):
            consignment.packets.append(future.result())

    ##########################################################################
    # release resources for YoctoPuce API and threads
    ##########################################################################

    if not settings['debug'] and not settings['sense']:
        yapi.YAPI.FreeAPI()

    # terminate thread for sending data to external plotter
    pipeline.liveplot.put(None)
    livp.join()

    ##########################################################################
    # save data and generate plots
    ##########################################################################

    if not channels:
        return

    consignment.remove_bad_packets()

    # ensure data is arranged in serial number order
    # this keeps the line colours of tested chips consistent across plots
    consignment.packets.sort()

    # add the user's label to the base filename
    filename = session
    if consignment.safe_label:
        filename = f'{session}_{consignment.safe_label}'

    if settings['json']:
        consignment.write_json_files(session)

    save_data(consignment, filename)
    create_plots(settings, consignment, filename, session)

    logging.info('Finished')


##############################################################################
if __name__ == '__main__':
    main()
