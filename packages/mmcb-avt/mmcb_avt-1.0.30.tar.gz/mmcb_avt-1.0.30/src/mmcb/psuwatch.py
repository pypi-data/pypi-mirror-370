#!/usr/bin/env python3
"""
Monitors the voltage and current of power supplies connected by FTDI USB to
RS232 adaptors. Results are written to the screen and to a log file.

All power supplies supported by detect.py are usable by this script.
"""

import argparse
import collections
import concurrent.futures as cf
import functools
import logging
import threading
import time

import serial

from mmcb import common
from mmcb import lexicon


##############################################################################
# utilities
##############################################################################

def format_reading(settings, tcolours, psu_info):
    """
    format PSU serial number, voltage and current read from PSU
    adding colour to current values that are over given thresholds

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        tcolours : class
            contains ANSI colour escape sequences
        psu_info : tuple (string, string, [(float, float), ...])
            (psu_type, psu_serial_number, [(voltage, current), ])
            e.g. ('hvpsu', '4343654', [(0.0, 5.143E-12), ...])
            may contain readings for more than one power supply output
    --------------------------------------------------------------------------
    returns
        retstr : string
    --------------------------------------------------------------------------
    """
    dev, readings = psu_info

    if dev.category == 'hvpsu':
        warning = settings['hv_warning']
        critical = settings['hv_critical']
    else:
        warning = settings['lv_warning']
        critical = settings['lv_critical']

    colour_start = colour_end = output = ''
    ident = dev.ident.replace(' ', '_')

    for voltage, current in readings:
        if voltage is not None and current is not None:
            if warning is not None:
                if abs(current) > warning:
                    colour_start = tcolours.BG_YELLOW
                    colour_end = tcolours.ENDC
            if critical is not None:
                if abs(current) > critical:
                    colour_start = tcolours.BG_RED + tcolours.FG_WHITE
                    colour_end = tcolours.ENDC
            output += (f' '
                       f'{common.si_prefix(voltage, compact=False).rjust(9)}V '
                       f'{colour_start}'
                       f'{common.si_prefix(current, compact=False).rjust(9)}A'
                       f'{colour_end}')
        else:
            colour_start = tcolours.BG_RED + tcolours.FG_WHITE
            colour_end = tcolours.ENDC
            output += f' {colour_start}None{colour_end}'

    return f'{ident}{output}'


##############################################################################
# command line option handler
##############################################################################

def check_duration(val):
    """
    time between samples in seconds

    --------------------------------------------------------------------------
    args
        val : int
            the runtime of read_psu_vi is typically around 1 second
            so sensible values range from 2 to perhaps 60 seconds
    --------------------------------------------------------------------------
    returns
        val : int
    --------------------------------------------------------------------------
    """
    val = int(val)
    if not 0 <= val <= 60:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'should be a positive numeric value between 0 and 60 (seconds)')
    return val


def check_arguments(settings):
    """
    handle command line options

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Monitors the voltage and current of all Keithley 2410,\
        2614b; ISEG SHQ 222M, 224M; Agilent e3647a, e3634a; and Hameg\
        (Rohde & Schwarz) HMP4040 power supplies connected by\
        FTDI USB to RS232 adaptors.')
    parser.add_argument(
        '--alias', nargs=1, metavar='filename',
        help='By default, serial numbers read from the power supplies over\
        RS232 are used to identify them in the logs. This option allows a CSV\
        file containing aliases to be read in, where each line consists of a\
        serial number then a textual description, separated by a comma\
        e.g. 4120021,LVSC03 red. These aliases are then substituted for the\
        serial numbers in the logs and in filenames as appropriate. Comments\
        starting with a hash "#" are allowed.',
        default=None)
    parser.add_argument(
        '-t', '--time', nargs=1, metavar='seconds',
        help='Time between samples in seconds. if this option is not used,\
            the script will default to sampling as fast as possible,\
            around one sample per second.',
        type=check_duration, default=[1])
    parser.add_argument(
        '--whv', nargs=2, metavar=('threshold', 'threshold'),
        help='For high voltage PSUs, the threshold values above which current\
            readings will be displayed with coloured warning highlights.\
            Values above the lower threshold will be shown in yellow, values\
            above the upper threshold will be shown in red. Values can be\
            specified with either scientific (10e-12) or engineering notation\
            (10p)',
        type=common.check_current, default=(None, None))
    parser.add_argument(
        '--wlv', nargs=2, metavar=('threshold', 'threshold'),
        help='For low voltage PSUs, the threshold values above which current\
            readings will be displayed with coloured warning highlights.\
            Values above the lower threshold will be shown in yellow, values\
            above the upper threshold will be shown in red. Values can be\
            specified with either scientific (10e-12) or engineering notation\
            (10p)',
        type=common.check_current, default=(None, None))

    args = parser.parse_args()

    settings['time'] = args.time[0]

    th1, th2 = args.whv
    if th1 is not None and th2 is not None:
        if th1 > th2:
            th1, th2 = th2, th1
    settings['hv_warning'] = th1
    settings['hv_critical'] = th2

    th1, th2 = args.wlv
    if th1 is not None and th2 is not None:
        if th1 > th2:
            th1, th2 = th2, th1
    settings['lv_warning'] = th1
    settings['lv_critical'] = th2

    if args.alias:
        filename = args.alias[0]
        common.read_aliases(settings, filename)


##############################################################################
# get data from devices on serial ports
##############################################################################

def read_psu_vi(dev, pipeline):
    """
    read voltage and current from PSU

    --------------------------------------------------------------------------
    args
        dev : instance of class Channel
            contains details of a device and its serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
    --------------------------------------------------------------------------
    returns
        dev : instance of class Channel
            contains details of a device and its serial port
        readings : list
            [(float, float)]
    --------------------------------------------------------------------------
    """
    with serial.Serial(port=dev.port) as ser:
        ser.apply_settings(dev.config)
        if dev.manufacturer in {'keithley', 'iseg'}:
            volt, curr = common.read_psu_measured_vi(pipeline, ser, dev)
        elif dev.manufacturer in {'agilent', 'hameg', 'hewlett-packard'}:
            if dev.model == 'e3634a':
                command_string = lexicon.power(dev.model, 'set remote')
                common.send_command(pipeline, ser, dev, command_string)

            command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
            measured_voltage = common.atomic_send_command_read_response(pipeline, ser,
                                                                        dev, command_string)

            command_string = lexicon.power(dev.model, 'read current', channel=dev.channel)
            measured_current = common.atomic_send_command_read_response(pipeline, ser,
                                                                        dev, command_string)
            try:
                volt = float(measured_voltage)
                curr = float(measured_current)
            except ValueError:
                volt = curr = None

            # ignore readings if output is off
            if dev.manufacturer == 'hameg':
                command_string = lexicon.power(dev.model, 'check output', channel=dev.channel)
                output_status = common.atomic_send_command_read_response(pipeline, ser,
                                                                         dev, command_string)
                if output_status == '0':
                    volt = curr = None

        else:
            logging.error('unknown power supply')
            volt = curr = None

    readings = [(volt, curr)]

    return dev, readings


##############################################################################
# moved from common
##############################################################################

def initial_power_supply_check(settings, pipeline, psus, channels, psuset=False):
    """
    Establishes RS232 communications with power supplies (as required).
    Checks status of channel outputs and interlocks (inhibits).

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        psus : dict
            {port: ({port_config}, device_type, device_serial_number), ...}
            contents of the cache filtered by hvpsu category
        channels : list
            contains instances of class Channel, one for each
            power supply channel
        psuset : bool
            selects the error message depending on the caller
    --------------------------------------------------------------------------
    returns
        channels : list
            no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    port_used = collections.defaultdict(int)
    outstat = []
    intstat = []
    polstat = []

    if settings['debug'] is None:
        common.check_ports_accessible(psus, channels)

        for dev in channels.copy():
            # message = f'enabled: {common._lookup_decorative(settings["alias"], dev)}'
            # common.log_with_colour(logging.INFO, message)

            with serial.Serial(port=dev.port) as ser:
                ser.apply_settings(dev.config)

                # try to ensure consistent state
                # clear FTDI output buffer state before sending
                ser.reset_output_buffer()
                # clear PSU state
                if dev.model == '2614b':
                    command_string = lexicon.power(dev.model, 'terminator only',
                                                   channel=dev.channel)
                    common.send_command(pipeline, ser, dev, command_string)
                # clear FTDI input buffer state
                ser.reset_input_buffer()
                # arbitrary settle time before proceeding
                time.sleep(0.5)

                # ensure serial port communication with PSU
                # this is for ISEG SHQ only, on a per-PSU basis
                if not port_used[dev.port]:
                    common.synchronise_psu(ser, pipeline, dev)

                # check power supply output
                # but don't do this if called from psuset.py, since the user
                # of that script may be issuing a command to turn a
                # power supply channel output on
                if not psuset:
                    tmp_stat = report_output_status(ser, pipeline, dev)
                    if tmp_stat:
                        channels.remove(dev)
                    # outstat.append(report_output_status(ser, pipeline, dev))

                # check interlock
                # this is per-PSU on Keithley, per-channel on ISEG
                if ((not port_used[dev.port] or dev.manufacturer == 'iseg')
                        and dev.manufacturer not in {'agilent', 'hameg'}):
                    intstat.append(common._report_interlock_status(ser, pipeline, dev))

                if dev.manufacturer == 'iseg':
                    polstat.append(common._report_polarity_status(settings, ser, pipeline, dev, psuset))

                ser.reset_input_buffer()
                ser.reset_output_buffer()

            port_used[dev.port] += 1

        if any(outstat):
            message = 'all power supply outputs must be on to proceed'
            common.log_with_colour(logging.ERROR, message)
            channels.clear()

        if any(intstat):
            message = 'all power supply interlocks must be inactive to proceed'
            common.log_with_colour(logging.ERROR, message)
            channels.clear()

        if any(polstat):
            if psuset:
                message = 'set voltage should agree with polarity switch to proceed'
                common.log_with_colour(logging.ERROR, message)
            else:
                message = 'all polarity switches must agree with --forwardbias to proceed'
                common.log_with_colour(logging.ERROR, message)

            channels.clear()
    else:
        message = '--debug: any connected power supplies will be ignored'
        log_with_colour(logging.WARNING, message)
        message = '--debug: IV data will generated internally'
        log_with_colour(logging.WARNING, message)


def report_output_status(ser, pipeline, dev):
    """
    Check that the output for the given power supply channel is on.

    While the outputs may be switched on/off over RS232 for all the supported
    power supplies except ISEG SHQ, this is generally used as a check to make
    sure the user has configured the test environment correctly.

    Values returned in variable output:

    +------------------+-----------+---------------+---------------+
    | dev.manufacturer | dev.model | output OFF    | output ON     |
    +------------------+-----------+---------------+---------------+
    | 'agilent'        | 'e3634a'  | '0'           | '1'           |
    | 'agilent'        | 'e3647a'  | '0'           | '1'           |
    | 'hameg'          | 'hmp4040' | '0'           | '1'           |
    | 'iseg'           | 'shq'     | '=OFF'        | '=ON'         |
    | 'keithley'       | '2410'    | '0'           | '1'           |
    | 'keithley'       | '2614b'   | '0.00000e+00' | '1.00000e+00' |
    +------------------+-----------+---------------+---------------+

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        fail : bool
            True if the output was found to be off, False otherwise
    --------------------------------------------------------------------------
    """
    fail = False

    command_string = lexicon.power(dev.model, 'check output', channel=dev.channel)
    output = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.manufacturer == 'iseg':
        if '=ON' not in output:
            # log_with_colour(logging.WARNING, f'{dev.ident}, output off')
            fail = True

    elif dev.manufacturer in {'agilent', 'hameg', 'keithley'}:
        try:
            outval = int(float(output))
        except ValueError:
            message = f'{dev.ident}, problem checking output'
            log_with_colour(logging.ERROR, message)
            fail = True
        else:
            if outval in {0, 1}:
                if outval == 0:
                    # message = f'{dev.ident}, output off'
                    # log_with_colour(logging.WARNING, message)
                    fail = True
            else:
                message = f'{dev.ident}, problem checking output'
                log_with_colour(logging.ERROR, message)
                fail = True

    return fail


##############################################################################
# main
##############################################################################

def main():
    """
    monitor the voltage and current on power supplies contained in the cache file
    created by detect.py
    """
    # date and time to the nearest second when the script was started
    session = common.timestamp_to_utc(time.time())

    # initialise
    settings = {
        'alias': None,
        'debug': None,
        'time': None,
        'hv_warning': None,
        'hv_critical': None,
        'lv_warning': None,
        'lv_critical': None}

    ##########################################################################
    # read command line arguments
    ##########################################################################

    check_arguments(settings)

    ##########################################################################
    # enable logging to file
    ##########################################################################

    log = f'{session}_psuwatch.log'
    logging.basicConfig(
        filename=log,
        level=logging.INFO,
        format='%(asctime)s : %(levelname)s : %(message)s')

    # enable logging to screen
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # set logging time to UTC to match session timestamp
    logging.Formatter.converter = time.gmtime

    ##########################################################################
    # read cache
    ##########################################################################

    # record the details of the power supplies being watched in the log
    psus = common.cache_read(['hvpsu', 'lvpsu'], uselog=True)
    channels = common.ports_to_channels(settings, psus)

    ##########################################################################
    # set up resources for threads
    ##########################################################################

    class Production:
        """
        Queues and locks to support threaded operation.

        RS232 will not tolerate concurrent access. portaccess is used to
        prevent more than one thread trying to write to the same RS232 port at
        the same time for multi-channel power supplies. For simplicity, locks
        are created for all power supplies, even if they only have a single
        channel.
        """
        portaccess = {
            port: threading.Lock()
            for port in {channel.port for channel in channels}
        }

    pipeline = Production()

    ##########################################################################
    # Check status of outputs and interlock (inhibit) on all power supplies
    ##########################################################################

    initial_power_supply_check(settings, pipeline, psus, channels)

    ##########################################################################
    # monitor power supply channels
    ##########################################################################

    _rpvi_pf = functools.partial(read_psu_vi, pipeline=pipeline)

    if channels:
        sample_period_seconds = settings['time']
        timestamp_mono = time.monotonic()

        while True:
            data = []
            with cf.ThreadPoolExecutor() as executor:
                psu_reading = (executor.submit(_rpvi_pf, channel) for channel in channels)
                for future in cf.as_completed(psu_reading):
                    data.append(future.result())

            # this will sort by serial number then channel order
            data.sort()

            # determine text and colour to print for each reading
            line = (format_reading(settings, common.ANSIColours, psu_info) for psu_info in data)
            logging.info(' | '.join(line))

            timestamp_mono = common.rate_limit(
                timestamp_mono, sample_period_seconds
            )


##############################################################################
if __name__ == '__main__':
    main()
