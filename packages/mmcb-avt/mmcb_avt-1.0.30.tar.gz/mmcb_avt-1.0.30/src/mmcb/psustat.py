#!/usr/bin/env python3
"""
Instantaneous snapshot of all power supply channels from devices connected
by FTDI USB to RS232 adaptors.

All power supplies supported by detect.py are usable by this script.
"""

import argparse
import collections
import contextlib
import sys
import time
import threading

from mmcb import common
from mmcb import lexicon


##############################################################################
# command line option handler
##############################################################################

def check_arguments(settings):
    """
    handle command line options

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='Provides an instantaneous snapshot of the\
        configuration and status of power supply channels from all Keithley\
        2410, 2614b; ISEG SHQ 222M, 224M; Agilent e3647a, e3634a; and Hameg\
        (Rohde & Schwarz) HMP4040 power supplies connected by FTDI USB to\
        RS232 adaptors.')
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

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '--sv', action='store_true',
        help='NOT IMPLEMENTED YET. Read set voltage.\
        Only valid if the user has specified a PSU channel.',
    )
    group1.add_argument(
        '--mv', action='store_true',
        help='Read measured voltage. Only valid if the user has specified a PSU channel.',
    )
    group1.add_argument(
        '--si', action='store_true',
        help='NOT IMPLEMENTED YET. Read set current.\
        Only valid if the user has specified a PSU channel.',
    )
    group1.add_argument(
        '--mi', action='store_true',
        help='Read measured current. Only valid if the user has specified a PSU channel.',
    )

    args = parser.parse_args()

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

    select = [
        settings['serial'],
        settings['channel'],
        settings['manufacturer'],
        settings['model'],
        settings['port'],
    ]
    settings['filter'] = any(value is not None for value in select)

    requests = collections.Counter([args.sv, args.mv, args.si, args.mi])

    if settings['filter'] and requests[True] == 0:
        print('select parameter to report with --sv, --mv, --si, --mi')
        sys.exit()

    settings['sv'] = args.sv
    settings['mv'] = args.mv
    settings['si'] = args.si
    settings['mi'] = args.mi


##############################################################################
# utilities
##############################################################################

def hmp4040_constant_voltage_current_status(ser, pipeline, dev, tcolours):
    """
    Query HMP4040 channel for constant voltage/current configuration.

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
        tcolours : class
            contains ANSI colour escape sequences
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    assert dev.manufacturer == 'hameg', 'function only callable for Hameg PSU'

    command_string = lexicon.power(dev.model, 'read channel mode', channel=dev.channel)
    register = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    status_categories = {
        # constant_voltage, constant_current
        (False, False): 'neither constant voltage nor constant current',
        (False, True): f'{tcolours.BOLD}{tcolours.FG_BRIGHT_RED}constant current{tcolours.ENDC}',
        (True, False): f'{tcolours.BOLD}{tcolours.FG_BRIGHT_GREEN}constant voltage{tcolours.ENDC}',
        (True, True): 'both constant voltage and constant current (!)',
        None: 'could not be determined'}

    configuration = None

    try:
        regval = int(register)
    except ValueError:
        pass
    else:
        constant_curr = (regval & (1 << 0)) != 0
        constant_volt = (regval & (1 << 1)) != 0
        configuration = (constant_volt, constant_curr)

    return status_categories[configuration]


def simple_current_limit(ser, pipeline, dev, eng_format=True):
    """
    Query current limit information for HMP4040, 2410, 2614b.

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
    returns : string
    --------------------------------------------------------------------------
    """
    message = None

    if dev.model in ('hmp4040', '2410', '2614b'):
        command_string = lexicon.power(dev.model, 'get current limit', channel=dev.channel)
        response = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)
        if eng_format:
            with contextlib.suppress(ValueError):
                message = f'{common.si_prefix(response)}A'
        else:
            with contextlib.suppress(ValueError):
                message = float(response)

    return message


def simple_output_status(ser, pipeline, dev, tcolours):
    """
    Return the on/off output status of the given power supply channel.

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
        tcolours : class
            contains ANSI colour escape sequences
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    command_string = lexicon.power(dev.model, 'check output', channel=dev.channel)
    output = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    status_categories = {
        True: f'{tcolours.BOLD}on{tcolours.ENDC}',
        False: 'off',
        None: 'could not be determined'}

    channel_on = None

    if dev.manufacturer == 'iseg':
        if any(x in output for x in ['=ON', '=OFF']):
            channel_on = '=ON' in output

    elif dev.manufacturer in {'agilent', 'hameg', 'keithley'}:
        try:
            outval = int(float(output))
        except ValueError:
            pass
        else:
            if outval in {0, 1}:
                channel_on = outval == 1

    return status_categories[channel_on]


def simple_interlock_status(ser, pipeline, dev, tcolours):
    """
    Check status of power supply interlock.

    This is per-PSU on Keithley, per-channel on ISEG.

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
        tcolours : class
            contains ANSI colour escape sequences
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    assert dev.manufacturer not in {'agilent', 'hameg'},\
        'function not callable for Agilent or Hameg PSU'

    status_categories = {
        True: 'active',
        False: f'{tcolours.BOLD}inactive{tcolours.ENDC}',
        None: 'could not be determined'}

    interlock_set = None

    command_string = lexicon.power(dev.model, 'check interlock', channel=dev.channel)
    register = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.manufacturer == 'iseg':
        # Interlocks are per-channel for ISEG SHQ.
        interlock_set = '=INH' in register
    else:
        # Interlocks are per-PSU for Keithley.
        try:
            regval = int(float(register))
        except ValueError:
            pass
        else:
            if dev.model == '2614b':
                # bit 11 (status.measurement.INTERLOCK) p.11-280 (648)
                # Without hardware interlock: '0.00000e+00'
                # with hardware interlock: '2.04800e+03'
                interlock_set = regval & 2048 == 0
            elif dev.model == '2410':
                if regval in {0, 1}:
                    # p.18-9 (389)
                    # returns '0' (disabled - no restrictions) or '1' (enabled)
                    interlock_set = register == 0

    return status_categories[interlock_set]


def simple_polarity_status(ser, pipeline, dev, tcolours):
    """
    Returned string from 'check module status' command appears to be base 10.

    e.g.
        inhibit is bit 5 (0=inactive, 1=active),
        polarity is bit 2 (0=negative, 1=positive)

        For channel 1, with inhibit active (terminator removed from front
        panel inhibit socket) and the polarity switch set to POS on the
        rear panel, the 'S1' command returns '036'

    e.g.
        polarity set to positive: '004', negative: '000'

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
        tcolours : class
            contains ANSI colour escape sequences
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    assert dev.model == 'shq', 'function only callable for ISEG SHQ PSU'

    status_categories = {
        True: 'positive',
        False: 'negative',
        None: f'{tcolours.BG_RED}{tcolours.FG_WHITE}could not be determined{tcolours.ENDC}'}

    polarity_positive = None

    command_string = lexicon.power(dev.model, 'check module status', channel=dev.channel)
    register = common.atomic_send_command_read_response(pipeline, ser, dev, command_string)

    with contextlib.suppress(ValueError):
        polarity_positive = int(register) & 4 != 0

    return status_categories[polarity_positive]


def power_supply_channel_status(settings, pipeline, psus, channels, tcolours):
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
        tcolours : class
            contains ANSI colour escape sequences
    --------------------------------------------------------------------------
    returns
        channels : list
            no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    port_used = collections.defaultdict(int)

    # this function call may change the value of variable channels
    # and returns a dict containing a mapping of ports to the serial ports
    # which have been left open
    spd = common.check_ports_accessible(psus, channels, close_after_check=False)

    for dev in channels:
        read_values = []

        ######################################################################
        # identify channel
        ######################################################################

        if not settings['filter']:
            print()
            print(dev)

        # specify already opened serial port
        ser = spd[dev.port]

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
        time.sleep(0.0)

        # ensure serial port communication with PSU
        # this is for ISEG SHQ only, on a per-PSU basis
        if not port_used[dev.port]:
            common.synchronise_psu(ser, pipeline, dev)

        ##################################################################
        # determine interlock status
        ##################################################################

        if not settings['filter']:
            # this is per-PSU on Keithley, per-channel on ISEG
            # still report it per-channel either way.
            if dev.manufacturer not in {'agilent', 'hameg'}:
                print(f'interlock status: {simple_interlock_status(ser, pipeline, dev, tcolours)}')

        ##################################################################
        # determine output status
        ##################################################################

        out_stat = simple_output_status(ser, pipeline, dev, tcolours)
        set_volt = read_psu_set_voltage(pipeline, ser, dev)

        if settings['filter']:
            if settings['sv']:
                print(set_volt)
        else:
            print(f'output status: {out_stat}')

            if set_volt is None:
                sv_text = 'could not be determined'
            else:
                sv_text = f'{common.si_prefix(set_volt)}V'
            read_values.append(f'set voltage: {sv_text}')

        ##################################################################
        # determine current limit
        ##################################################################

        current_limit = simple_current_limit(ser, pipeline, dev)
        if current_limit is not None:
            if settings['filter']:
                if settings['si']:
                    print(
                        simple_current_limit(ser, pipeline, dev, eng_format=False)
                    )
            else:
                print(f'current limit: {current_limit}')

        ##################################################################
        # report measured values
        ##################################################################

        if 'on' in out_stat:
            mvolt, mcurr = read_psu_vi(pipeline, ser, dev)
            if mvolt is None:
                mvi_text = 'could not be determined'
            else:
                if not settings['filter']:
                    mvi_text = f'{common.si_prefix(mvolt)}V, {common.si_prefix(mcurr)}A'
                else:
                    if settings['mi']:
                        print(mcurr)
                    elif settings['mv']:
                        print(mvolt)

            if not settings['filter']:
                read_values.append(f'measured: {mvi_text}')

        else:
            if settings['filter']:
                if settings['mi'] or settings['mv']:
                    print('None')
            else:
                print('None')

        ##################################################################
        # determine polarity status
        ##################################################################

        if not settings['filter']:
            if dev.manufacturer == 'iseg':
                print(f'polarity: {simple_polarity_status(ser, pipeline, dev, tcolours)}')

        ##################################################################
        # determine constant voltage/current operation
        ##################################################################

        if not settings['filter']:
            if dev.manufacturer == 'hameg':
                print(f'mode: {hmp4040_constant_voltage_current_status(ser, pipeline, dev, tcolours)}')

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        if not settings['filter']:
            print(', '.join(read_values))

        port_used[dev.port] += 1

    # close all the serial ports left open by the call above to
    # common.check_ports_accessible()
    for serial_port in spd.values():
        serial_port.close()


def read_psu_vi(pipeline, ser, dev):
    """
    read measured voltage and current from PSU

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns
        dev : instance of class Channel
            contains details of a device and its serial port
        readings : list
            [(float, float)]
    --------------------------------------------------------------------------
    """
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
        volt = curr = None

    return volt, curr


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
        dev : instance of class Channel
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

        with contextlib.suppress(TypeError, ValueError):
            set_volt = float(item)

    elif dev.manufacturer == 'hameg':
        with contextlib.suppress(ValueError):
            set_volt = float(local_buffer)

    return set_volt


##############################################################################
# main
##############################################################################

def main():
    """
    Instantaneous snapshot of all power supply channels from devices
    connected by FTDI USB to RS232 adaptors.
    """
    settings = {
        'alias': None,
        'channel': None,
        'manufacturer': None,
        'model': None,
        'port': None,
        'serial': None,
        'time': None,
        }

    check_arguments(settings)

    ##########################################################################
    # read cache
    ##########################################################################

    psus = common.cache_read(['hvpsu', 'lvpsu'], quiet=settings['filter'])
    channels = common.ports_to_channels(settings, psus)

    if settings['filter'] and not common.unique(settings, psus, channels):
        print('could not identify a single power supply channel')
        print('check use of --manufacturer, --model, --serial, --port, and --channel')
        sys.exit()

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
        portaccess = {port: threading.Lock()
                      for port in {channel.port for channel in channels}}

    pipeline = Production()

    ##########################################################################
    # Check status of outputs and interlock (inhibit) on all power supplies
    ##########################################################################

    power_supply_channel_status(
        settings, pipeline, psus, channels, common.ANSIColours
    )


##############################################################################
if __name__ == '__main__':
    main()
