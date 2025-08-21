#!/usr/bin/env python3
"""
Set the voltage on a power supply connected by RS232.

All power supplies supported by detect.py are usable by this script.

the script will return an appropriate unix return value on completion, so
the return value can be used by the shell, e.g.

./psuset.py -50 && ./capture2.py -t 60
"""

import argparse
import logging
import math
import sys
import threading
import time
import types

import serial
import numpy as np

from mmcb import common
from mmcb import lexicon
from mmcb import sequence


##############################################################################
# command line option handler
##############################################################################

def check_voltage(val):
    """
    check voltage range

    --------------------------------------------------------------------------
    args
        val : float
            bias voltage
    --------------------------------------------------------------------------
    returns : float
    --------------------------------------------------------------------------
    """
    val = float(val)
    if not -1100 <= val <= 1100:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'voltage value should be between -1100 and 1100')
    return val


def check_settlingtime(val):
    """
    check settling time

    --------------------------------------------------------------------------
    args
        val : float
            settling time in seconds
    --------------------------------------------------------------------------
    returns : float
    --------------------------------------------------------------------------
    """
    val = float(val)
    if not 0.0 <= val <= 60.0:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'settling time value should be between 0 and 60 seconds')
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
        description='Set voltage and/or current limit of a single power\
        supply channel connected by RS232. Currently supported PSUs are: Hameg\
        (Rohde & Schwarz) HMP4040; Keithley 2410, 2614b; ISEG SHQ 222M, 224M;\
        and Agilent E3647A, E3634A (the latter may also be branded Keysight\
        or Hewlett-Packard). When multiple power supplies are\
        connected, use command line options --manufacturer, --model,\
        --serial, --channel and --port to identify the individual power\
        supply. For brevity, specify the minimum number of identifying\
        parameters to uniquely identify the device; if there is only one\
        single-channel power supply attached, just specify the voltage to be\
        set. Note that ISEG power supplies can take a long time to settle to\
        final values, and at low voltages they may never converge to the set\
        voltage.')
    parser.add_argument(
        'voltage', nargs='*', metavar='voltage',
        help='value in volts, values range -1100 to +1100',
        type=check_voltage, default=None)
    parser.add_argument(
        '--manufacturer', nargs=1, metavar='manufacturer',
        choices=['agilent', 'hameg', 'iseg', 'keithley'],
        help='PSU manufacturer.',
        default=None)
    parser.add_argument(
        '--model', nargs=1, metavar='model',
        choices=['2410', '2614b', 'e3634a', 'e3647a', 'hmp4040', 'shq'],
        help='PSU model.',
        default=None)
    parser.add_argument(
        '--serial', nargs=1, metavar='serial',
        help='PSU serial number. A part of the serial may be supplied if it\
        is unique amongst connected devices.',
        default=None)
    parser.add_argument(
        '--channel', nargs=1, metavar='channel',
        choices=['1', '2', '3', '4', 'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D'],
        help='PSU channel number. These can be specified numerically or\
        alphabetically.',
        default=None)
    parser.add_argument(
        '--port', nargs=1, metavar='port',
        help='Serial port identifier. This is useful where multiple Agilent/\
        Keysight/Hewlett-Packard power supplies are connected, since they do\
        not provide a serial number over RS232. A part of the serial may be\
        supplied if it is unique amongst connected devices.',
        default=None)
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset power supply before setting voltage (Keithley 2410).')
    parser.add_argument(
        '-i', '--immediate',
        action='store_true',
        help='On high-voltage power supplies, set the specified voltage\
            immediately. By default the voltage will ramp from the current\
            value to the specified value (Keithley and ISEG). For low-voltage\
            power supplies the specified voltage is always set immediately\
            unless --peltier is used with the HMP4040.')
    parser.add_argument(
        '-l', '--limit', nargs=1, metavar='current_limit',
        help='Set the power supply channel current limit.\
        Values can be specified with either scientific (10e-9) or\
        engineering notation (10n). Supported for Keithley 2410, 2614b;\
        Rohde & Schwarz HMP4040. For the latter, the minimum value is 1mA.',
        type=common.check_current)
    parser.add_argument(
        '-p', '--peltier',
        action='store_true',
        help='Use gradual voltage changes for HMP4040.')
    parser.add_argument(
        '-v', '--voltspersecond', nargs=1, metavar='rateofchange',
        help='When not using --immediate, this option sets the rate of change\
            in volts per second. The default is 10V/s (Keithley and ISEG).')
    parser.add_argument(
        '-s', '--settlingtime', nargs=1, metavar='settlingtime',
        help='Custom settling time in seconds between asserting voltage\
        and reading back. Default is 0.5s.',
        type=check_settlingtime, default=[0.5])
    parser.add_argument(
        '--forwardbias',
        action='store_true',
        help='For HV supplies biassing detectors it is expected negative\
        voltages will be used, so by default user requests for positive values\
        will be suppressed, unless this option is used. Implemented for the\
        Keithley 2410/2614b only.')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '-f', '--front',
        action='store_true',
        help='Use front output (Keithley 2410).')
    group1.add_argument(
        '-r', '--rear',
        action='store_true',
        help='Use rear output (Keithley 2410).')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument(
        '--on',
        action='store_true',
        help='Turn PSU (channel) output on, by default the script leaves the\
            power supply output unchanged (Keithley and Agilent).')
    group2.add_argument(
        '--off',
        action='store_true',
        help='Turn PSU output off, by default the script leaves the power\
            supply output unchanged (Keithley and Agilent).')

    group3 = parser.add_mutually_exclusive_group()
    group3.add_argument(
        '--verbose',
        action='store_true',
        help='Display all power supply channels detected, and search terms\
        supplied')
    group3.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal text output during normal operation')

    args = parser.parse_args()

    settings['verbose'] = args.verbose
    settings['quiet'] = args.quiet

    # default: leave power supply settings unchanged
    if args.front:
        settings['rear'] = False
    elif args.rear:
        settings['rear'] = True

    # default: leave power supply settings unchanged
    if args.on:
        settings['on'] = True
    elif args.off:
        settings['on'] = False

    if args.reset:
        settings['reset'] = args.reset

    if args.immediate:
        settings['immediate'] = args.immediate

    if args.forwardbias:
        settings['forwardbias'] = args.forwardbias

    if args.peltier:
        settings['peltier'] = args.peltier

    # voltage will always be present
    if args.voltage is not None and len(args.voltage) == 1:
        settings['voltage'] = args.voltage[0]

    if args.serial:
        settings['serial'] = args.serial[0]

    if args.channel:
        settings['channel'] = args.channel[0].lower()

    if args.manufacturer:
        settings['manufacturer'] = args.manufacturer[0]

    if args.model:
        settings['model'] = args.model[0]

    if args.port:
        settings['port'] = args.port[0]

    if args.voltspersecond:
        settings['voltspersecond'] = int(args.voltspersecond[0])

    if args.limit:
        settings['current_limit'] = args.limit[0]

    settings['settlingtime'] = args.settlingtime[0]


##############################################################################
# set psu values
##############################################################################

def read_measured_voltage(settings, pipeline, ser, dev):
    """
    read the voltage as measured at the psu output terminals

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        success : bool
    --------------------------------------------------------------------------
    """
    measured_voltage = None

    if dev.manufacturer == 'iseg':
        command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
        local_buffer = common.atomic_send_command_read_response(pipeline, ser, dev,
                                                                command_string)

        measured_voltage = common.iseg_value_to_float(local_buffer)

    elif dev.manufacturer == 'keithley':
        command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
        local_buffer = common.atomic_send_command_read_response(pipeline, ser, dev,
                                                                command_string)

        if local_buffer is not None:
            separator = ',' if dev.model == '2410' else None
            items = (float(x) for x in local_buffer.split(separator))

            try:
                measured_voltage = next(items)
            except (StopIteration, ValueError):
                message = f'{dev.ident} problem reading measured voltage'
                common.log_with_colour(logging.WARNING, message)

    elif dev.manufacturer in {'agilent', 'hameg'}:
        if dev.model == 'e3634a':
            command_string = lexicon.power(dev.model, 'set remote')
            common.send_command(pipeline, ser, dev, command_string)

        command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
        local_buffer = common.atomic_send_command_read_response(pipeline, ser, dev,
                                                                command_string)

        try:
            volt = float(local_buffer)
        except ValueError:
            pass
        else:
            measured_voltage = common.decimal_quantize(volt, settings['decimal_places'])

    return measured_voltage


def check_measured_voltage(settings, pipeline, ser, dev, set_voltage):
    """
    compare the voltage as measured at the psu output terminals to the
    given voltage

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
        set_voltage : decimal.Decimal
    --------------------------------------------------------------------------
    returns
        success : bool
    --------------------------------------------------------------------------
    """
    success = False
    measured_voltage = read_measured_voltage(settings, pipeline, ser, dev)

    # comparison
    if measured_voltage is not None:
        set_voltage = common.decimal_quantize(set_voltage, settings['decimal_places'])
        measured_voltage = common.decimal_quantize(measured_voltage, settings['decimal_places'])

        volt = common.si_prefix(measured_voltage)
        common.log_with_colour(logging.INFO, f'measured: {volt}V')

        if set_voltage == measured_voltage:
            success = True

    return success


def current_limit(settings, pipeline, ser, dev):
    """
    Set and check current limit on Hameg HMP4040, Keithley 2614b and 2410.

    HMP4040 notes:

    The PSU seems to support setting of values down to 100uA for current limit
    values < 1A, and down to 1mA for current limit >= 1A. However, support
    seems patchy. 0.9992A, 0.0012 and 1.2m set correctly, but 0.0002A, 0.0002
    and 0.2m do not. So limit this to 1mA (3 decimal places) to avoid
    confusion.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if dev.model not in ('hmp4040', '2614b', '2410'):
        return

    # set current limit
    if dev.model == 'hmp4040':
        dec_places = 3
        compliance = f'{settings["current_limit"]:.{dec_places}f}'
    else:
        compliance = f'{settings["current_limit"]:e}'

    command_string = lexicon.power(dev.model, 'set current limit',
                                   compliance, channel=dev.channel)
    common.send_command(pipeline, ser, dev, command_string)

    # read back current limit from PSU
    command_string = lexicon.power(dev.model, 'get current limit', channel=dev.channel)
    response = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)
    one_percent = 0.005
    onehundred_microamps = 0.0001
    close_enough = math.isclose(float(response), settings['current_limit'],
                                rel_tol=one_percent, abs_tol=onehundred_microamps)

    # report current limit
    message = ('requested current limit '
               f'{common.si_prefix(settings["current_limit"])}A, '
               f'set to {common.si_prefix(response)}A')
    if close_enough:
        common.log_with_colour(logging.INFO, message)
    else:
        common.log_with_colour(logging.WARNING, message)


def hmp4040_constant_current(ser, pipeline, dev):
    """
    Check if HMP4040 channel is configured for constant current.

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
    returns : bool
    --------------------------------------------------------------------------
    """
    assert dev.manufacturer == 'hameg', 'function only callable for Hameg PSU'

    command_string = lexicon.power(dev.model, 'read channel mode', channel=dev.channel)
    register = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    try:
        regval = int(register)
    except ValueError:
        retval = False
    else:
        constant_curr = (regval & (1 << 0)) != 0
        retval = constant_curr

    return retval


def configure_lvpsu(settings, pipeline, ser, dev):
    """
    Set the power supply voltage and read back the value to confirm it has
    been correctly set.

    Handles: Agilent E3634A, E3647A; Hameg HMP4040.

    For Agilent, though the low range is set by default, if the voltage value
    submitted exceeds the range threshold by over a volt or so, the PSU will
    automatically select the high range.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        success : bool
            True if the device was found, False otherwise
    --------------------------------------------------------------------------
    """
    success = False

    if settings['reset']:
        if dev.manufacturer == 'hameg':
            # reset to default conditions, output off
            # allow device time to complete reset before sending more commands
            command_string = lexicon.power(dev.model, 'reset')
            common.send_command(pipeline, ser, dev, command_string)
            common.log_with_colour(logging.INFO, 'reset')
            time.sleep(0.2)
        else:
            message = f'{dev.manufacturer} {dev.model}: reset not supported'
            common.log_with_colour(logging.WARNING, message)

    # set and verify current limit
    if settings['current_limit'] is not None:
        current_limit(settings, pipeline, ser, dev)

    # change output on/off if requested, otherwise do not change it
    if settings['on'] is not None:
        comtxt = 'output on' if settings['on'] else 'output off'
        command_string = lexicon.power(dev.model, comtxt, channel=dev.channel)
        common.atomic_send_command_read_response(pipeline, ser, dev, command_string)
        common.log_with_colour(logging.INFO, comtxt)

    # set voltage
    if settings['voltage'] is None:
        # success is not modified before this point
        return True

    # constrain the voltage to be set to the given number of decimal places
    voltage = common.decimal_quantize(settings['voltage'], settings['decimal_places'])

    if voltage < 0:
        message = f'{dev.manufacturer} {dev.model}: cannot use a negative voltage'
        common.log_with_colour(logging.ERROR, message)
    else:
        message = f'voltage set to {common.si_prefix(voltage)}V'
        common.log_with_colour(logging.INFO, message)

    if dev.manufacturer == 'hameg' and settings['peltier']:
        measured_voltage = read_measured_voltage(settings, pipeline, ser, dev)
        if measured_voltage is not None:
            transition_voltage(settings, pipeline, measured_voltage, voltage, ser, dev)
    else:
        common.set_psu_voltage(settings, pipeline, voltage, ser, dev)

    # Agilent E3647A seems to require a minimum of half a second to apply
    # the setting before any further RS232 interaction is reliable
    time.sleep(0.5)

    # Arguably the voltage set for the channel should be read back too, so
    # for the case where the channel output is off, some confirmation that
    # the value has been set correctly can be given to the user.
    #
    # check measured voltage (can only be read back if output is on)
    if not common.report_output_status(ser, pipeline, dev):
        # allow a little time for the voltage to settle before reading
        time.sleep(settings['settlingtime'])

        if dev.manufacturer == 'hameg' and hmp4040_constant_current(ser, pipeline, dev):
            # When configured as a constant current source, the measured
            # voltage will not match the set voltage
            success = True
        else:
            success = check_measured_voltage(settings, pipeline, ser, dev, voltage)
    else:
        message = 'with PSU output switched off, set voltage cannot be read back'
        common.log_with_colour(logging.WARNING, message)
        common.log_with_colour(logging.WARNING, 'assuming all is well')
        success = True

    return success


def configure_hvpsu(settings, pipeline, ser, dev):
    """
    Amend power supply settings. If a change of voltage has been requested,
    read back the value to confirm it has been correctly set.

    Process requests relevant to the selected power supply in this order:

    * reset
    * set range
    * select front/rear output
    * output on/off
    * set voltage

    Handles: Keithley 2410, 2614b; ISEG SHQ.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        success : bool
            True if the device was found, False otherwise
    --------------------------------------------------------------------------
    """
    success = False

    # ------------------------------------------------------------------------
    # protection against accidental forward bias operation
    # ------------------------------------------------------------------------

    if settings['voltage'] > 0 and not settings['forwardbias']:
        common.log_with_colour(
            logging.ERROR,
            'HV PSU positive voltage specified without --forwardbias'
        )
        return success

    if settings['voltage'] < 0 and settings['forwardbias']:
        common.log_with_colour(
            logging.ERROR,
            'HV PSU negative voltage specified with --forwardbias'
        )
        return success

    # ------------------------------------------------------------------------

    if dev.manufacturer == 'keithley':
        command_string = lexicon.power(dev.model, 'clear event registers')
        common.send_command(pipeline, ser, dev, command_string)

    if settings['reset']:
        if dev.manufacturer == 'keithley' and dev.model == '2410':
            # reset to default conditions, output off
            # allow device time to complete reset before sending more commands
            common.log_with_colour(logging.INFO, 'reset')
            command_string = lexicon.power(dev.model, 'reset')
            common.send_command(pipeline, ser, dev, command_string)
            time.sleep(0.2)
        else:
            message = f'{dev.manufacturer} {dev.model}: reset not supported'
            common.log_with_colour(logging.WARNING, message)

    # set and verify current limit
    if settings['current_limit'] is not None:
        current_limit(settings, pipeline, ser, dev)

    # set voltage
    if settings['voltage'] is not None:
        # as a general rule this script should avoid making changes to the
        # user's power supply settings, since the context it's being used in
        # may be unclear. However, for this project the highest voltage range
        # will always be used, and it is not unreasonable to set it here.
        #
        # It would be more correct for 'configure range' to be performed
        # immediately after a reset (above, selectively). Performing it here
        # (always) is more friendly to the user, e.g. if the user has just
        # switched on the power supply (it may well be in a low voltage range)
        # and runs this script with a high voltage, it will generate a series
        # of
        # "settings conflict" errors (on the 2410) as the script tries to set
        # voltages higher than the current range allows.
        common.log_with_colour(logging.INFO, 'configure range')
        command_string = lexicon.power(dev.model, 'configure range', channel=dev.channel)
        common.send_command(pipeline, ser, dev, command_string)

    # Change front/rear routing if requested, otherwise do not change it.
    #
    # Since changing this setting will turn the output off, it must be performed
    # before processing any user request to turn the output on or off.
    if settings['rear'] is not None:
        if dev.manufacturer == 'keithley' and dev.model == '2410':
            destination = 'REAR' if settings['rear'] else 'FRON'
            command_string = lexicon.power(dev.model, 'set route', destination)
            common.send_command(pipeline, ser, dev, command_string)
        else:
            message = f'{dev.manufacturer} {dev.model}: front/rear not supported'
            common.log_with_colour(logging.WARNING, message)

    # change output on/off if requested, otherwise do not change it
    if settings['on'] is not None:
        if dev.manufacturer == 'keithley':
            comtxt = 'output on' if settings['on'] else 'output off'
            common.log_with_colour(logging.INFO, comtxt)
            command_string = lexicon.power(dev.model, comtxt, channel=dev.channel)
            common.atomic_send_command_read_response(pipeline, ser, dev, command_string)
        else:
            message = f'{dev.manufacturer} {dev.model}: output on/off not supported'
            common.log_with_colour(logging.WARNING, message)

    ##############################################################################
    # set voltage
    if settings['voltage'] is None:
        # success is not modified before this point
        return True

    # constrain the voltage to be set to the given number of decimal places
    voltage = common.decimal_quantize(settings['voltage'], settings['decimal_places'])
    message = f'setting voltage: {common.si_prefix(voltage)}V'
    common.log_with_colour(logging.INFO, message)

    # set voltage
    if settings['immediate']:
        common.set_psu_voltage(settings, pipeline, voltage, ser, dev)
    else:
        measured_voltage = read_measured_voltage(settings, pipeline, ser, dev)
        if measured_voltage is not None:
            transition_voltage(settings, pipeline, measured_voltage, voltage, ser, dev)

    # check set voltage (can only be read back if output is on)
    if not common.report_output_status(ser, pipeline, dev):
        # allow a little time for the voltage to settle before reading
        time.sleep(settings['settlingtime'])
        success = check_measured_voltage(settings, pipeline, ser, dev, voltage)
    else:
        # keithley 2410, 2614b
        message = 'with PSU output switched off, set voltage cannot be read back'
        common.log_with_colour(logging.WARNING, message)
        common.log_with_colour(logging.WARNING, 'assuming all is well')
        success = True

    return success


def transition_voltage(settings, pipeline, initial_voltage, target_voltage, ser, dev):
    """
    Gradual voltage transitions.

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
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if initial_voltage != target_voltage:
        message = f'{dev.ident}, transitioning from {initial_voltage}V to {target_voltage}V'
        common.log_with_colour(logging.INFO, message)

        if dev.manufacturer == 'iseg':
            # use power supply's internal ramp feature to avoid having manage
            # the ISEG SHQ's tardy response time

            # read voltage rate of change
            command_string = lexicon.power(dev.model,
                                           'read max rate of change',
                                           channel=dev.channel)
            max_vroc = common.atomic_send_command_read_response(pipeline, ser, dev,
                                                                command_string)

            # set voltage rate of change for ramp
            if settings['voltspersecond'] is None:
                volts_per_second = 10
            else:
                volts_per_second = settings['voltspersecond']

            command_string = lexicon.power(dev.model,
                                           'set voltage max rate of change',
                                           volts_per_second,
                                           channel=dev.channel)
            common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

            # auto ramp will progress towards the given voltage at the given rate
            command_string = lexicon.power(dev.model,
                                           'set voltage',
                                           abs(target_voltage),
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

        elif dev.manufacturer == 'keithley':
            timestamp = None
            duration = 1 if settings['voltspersecond'] is None else 10 / settings['voltspersecond']
            step = 10

            for voltage in sequence.to_original(initial_voltage, target_voltage, step):
                timestamp = common.rate_limit(timestamp, duration)
                common.set_psu_voltage(settings, pipeline, voltage, ser, dev)

            common.log_with_colour(logging.INFO, f'{dev.ident}, transition complete')

        elif dev.model == 'hmp4040':
            # quick addition - special case for Peltier usage
            # aim for 2V in 30s, 1.5s per 0.1V step
            initial_voltage = float(initial_voltage)
            target_voltage = float(target_voltage)
            timestamp = None
            step = 0.1 if target_voltage > initial_voltage else -0.1
            duration = 30 / (2 / abs(step))

            for voltage in np.arange(initial_voltage + step, target_voltage + step, step):
                timestamp = common.rate_limit(timestamp, duration)
                common.set_psu_voltage(settings, pipeline, voltage, ser, dev)


##############################################################################
# main
##############################################################################

def main():
    """ set the voltage on a power supply connected by RS232 """

    status = types.SimpleNamespace(success=0, unreserved_error_code=3)

    success = False
    settings = {
        'alias': None,
        'channel': None,
        'current_limit': None,
        'debug': None,
        'decimal_places': 2,
        'forwardbias': False,
        'immediate': False,
        'manufacturer': None,
        'model': None,
        'on': None,
        'peltier': False,
        'port': None,
        'quiet': False,
        'rear': None,
        'reset': False,
        'serial': None,
        'settlingtime': 0.5,
        'verbose': None,
        'voltage': None,
        'voltspersecond': 10
        }

    check_arguments(settings)

    ##########################################################################
    # enable logging to screen
    ##########################################################################

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s : %(message)s')

    # enable logging to screen
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set logging time to UTC to match session timestamp
    logging.Formatter.converter = time.gmtime

    ##########################################################################
    # filter power supplies from cache leaving just a single channel
    ##########################################################################

    psus = common.cache_read(['hvpsu', 'lvpsu'])
    channels = common.ports_to_channels(settings, psus)

    if settings['verbose']:
        print('detected power supply channels:')
        for channel in channels:
            print(channel)
        print('search terms:')
        maxlen = max(len(x) for x in settings)
        for setting, value in settings.items():
            print(f'{setting:>{maxlen}} {value}')

    if not common.unique(settings, psus, channels):
        print('could not identify a single power supply channel')
        print('check use of --manufacturer, --model, --serial, --port, and --channel')
        sys.exit()

    ##########################################################################
    # set up resources for threads
    #
    # this is overkill since only one power supply channel will be used
    # but does allow the same well-tested interface employed by other scripts
    # in the suite to be used
    ##########################################################################

    class Production:
        """ Locks to support threaded operation. """
        portaccess = {port: threading.Lock()
                      for port in {channel.port for channel in channels}}

    pipeline = Production()

    ##########################################################################
    # Check status of outputs and interlock (inhibit) on all power supplies
    ##########################################################################

    common.initial_power_supply_check(settings, pipeline, psus, channels, psuset=True)

    ##########################################################################
    # display details of selected power supply
    ##########################################################################

    try:
        channel = channels[0]
    except IndexError:
        pass
    else:
        text = f'selected power supply: {channel.manufacturer} {channel.model}'
        if channel.serial_number:
            text += f' s.no. {channel.serial_number}'
        if channel.channel:
            text += f' channel {channel.channel}'
        if settings['port'] is not None:
            text += f' port {channel.port}'
        common.log_with_colour(logging.INFO, text, quiet=settings['quiet'])

        ##########################################################################
        # set values on given power supply channel
        ##########################################################################

        setpsu = {'lvpsu': configure_lvpsu, 'hvpsu': configure_hvpsu}

        with serial.Serial(port=channel.port) as ser:
            ser.apply_settings(channel.config)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            success = setpsu[channel.category](settings, pipeline, ser, channel)
            if success:
                common.log_with_colour(
                    logging.INFO, 'operation successful',
                    quiet=settings['quiet']
                )

    return status.success if success else status.unreserved_error_code


##############################################################################
if __name__ == '__main__':
    sys.exit(main())
