#!/usr/bin/env python3
"""
Detect devices present on the serial ports, that are attached via
FTDI USB to RS232 adaptors.  This will write a cache file that can
be used by the other utility scripts.

The script will recognise the following devices, and more than one device of
each type can be detected:

controller : Newport ESP300, MM4006 and SMC100
     lvpsu : Agilent E3647A, E3634A, Hameg (Rohde & Schwarz) HMP4040
     hvpsu : Keithley 2410, 2614b; ISEG SHQ 222M, 224M

The terminator should set to be the same on all devices to make sure each
device can cleanly reject commands intended for other devices. <CRLF> is
expected.
"""

import argparse
import collections
import concurrent.futures as cf
import functools
import itertools
import json
import sys
import time

import serial
import serial.tools.list_ports as stlp

from mmcb import common
from mmcb import lexicon


##############################################################################
# constants
##############################################################################

DEBUG = False

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
        args : <class 'argparse.Namespace'>
            e.g. Namespace(assume=False, nocache=False)
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='A diagnostic tool to detect devices attached to a\
            computer\'s RS232 serial ports via FTDI USB to RS232 adaptors.\
            Devices that are recognised are:\
            Newport ESP300, MM4006 and SMC100 stage controllers;\
            Hameg (Rohde & Schwarz) HMP4040, Keithley 2410/2614B,\
            ISEG SHQ 222M/224M and Agilent E3647A/E3634A PSUs.\
            Writes a cache file containing detected devices that can be used\
            by other scripts in this suite.'
    )
    parser.add_argument(
        '--nocache',
        action='store_true',
        help='do not create cache file from list of detected devices',
    )
    parser.add_argument(
        '--delay_dmm6500',
        action='store_true',
        help='Keithley 2614b may not be detected if tested after DMM 6500'
    )

    return parser.parse_args()


##############################################################################
# detect devices on serial ports
##############################################################################


def find_controller(port, config):
    """
    Check if an ESP300 or mm4006 is present on the given serial port.

    Note that the device's error-FIFO is manually cleared to ensure further
    communications can be processed successfully.

    from reference/ESP300.pdf page 3-7 (page 47 of the PDF):

    "A controller command (or a sequence of commands) has to be terminated with
    a carriage return character. However, responses from the controller are
    always terminated by a carriage return/line feed combination. This setting
    may not be changed."

    Newport MM4006 responds to "VE" with:
    "ve mm4006 controller version  7.01 date 04-02-2003"
    mm4006 ignores rs232 commands when user is in the config menu.

    Note that this function is called quite late in the detection process. By
    the time it is called, this script will already have sent any esp300 or
    mm4006 present on the specified serial port multiple commands it would
    find incomprehensible, even if they were sent at a matching baud rate.
    Hence, the need to clear the ESP300's error FIFO before detection can
    commence.

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_output_buffer()
        ser.reset_input_buffer()

        # manually empty ESP30X's 10 item error FIFO
        # the mm4006 - like the smc100 - only holds the last error
        #
        # FIXME
        #
        # The commands differ: TE? (esp300), TE (mm4006).
        # This does not seem to cause problems with the mm4006, however check
        # how the mm4006 handles this. The esp300 needs to have the FIFO
        # cleared; perhaps the mm4006 is more tolerant in its error handling
        # or it allows (undocumented) use of a trailing '?' for queries.
        #
        # Also investigate possibility of early termination to (slightly)
        # reduce detection time:
        #
        # ESP300.pdf, p. 3-139
        # TE? returns '0' if no error
        #
        # MM4K6_701_E3.pdf, p. 3.143
        # TE returns 'TE@' if no error
        esp300_read_error = lexicon.motion('esp300', 'read error')
        esp300_fifo_size = 10
        for _ in itertools.repeat(None, esp300_fifo_size):
            ser.write(esp300_read_error)
            try:
                ser.readline()
            except serial.SerialException:
                print(f'cannot access serial port {port}')
                ser.close()
                return retval

        # command string is identical for esp300 and mm4006
        ser.write(lexicon.motion('esp300', 'read controller version'))

        # get response
        try:
            controller = ser.readline().decode('utf-8').strip().lower()
        except UnicodeDecodeError:
            ser.close()
        else:
            channels = ['']
            release_delay = None

            # we might have an ESP300 or ESP301 controller/driver
            if 'esp30' in controller:
                manufacturer = 'newport'
                model = controller.partition(' ')[0]
                serial_number = ''
                detected = True
                settings = ser.get_settings()
                retval = (
                    'controller',
                    settings,
                    (
                        port,
                        manufacturer,
                        model,
                        serial_number,
                        detected,
                        channels,
                        release_delay,
                    ),
                )
            elif 'mm4006' in controller:
                manufacturer = 'newport'
                model = controller.split()[1]
                serial_number = ''
                detected = True
                settings = ser.get_settings()
                retval = (
                    'controller',
                    settings,
                    (
                        port,
                        manufacturer,
                        model,
                        serial_number,
                        detected,
                        channels,
                        release_delay,
                    ),
                )

            # no device detected
            ser.close()

    return retval


def find_controller_smc(port, config):
    """
    Check if an SMC100 controller is present on the given serial port.

    The SMC100 controller has non-configurable RS232 settings so handle it
    separately in this function rather than making find_controller()
    overly long.

    Note that the device's error-FIFO is manually cleared to ensure further
    communications can be processed successfully.

    Newport SMC100 responds to 1VE with:
    "1VE SMC_CC - Controller-driver version  3. 1. 2"

    ASSUME that we only have one SMC controller, and it is at address 1.

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_output_buffer()
        ser.reset_input_buffer()

        # the SMC100 retains a record of the last error only
        ser.write(lexicon.motion('smc', 'read error', identifier='1'))
        try:
            ser.readline()
        except serial.SerialException:
            print(f'cannot access serial port {port}')
            ser.close()
            return retval

        ser.write(lexicon.motion('smc', 'read controller version', identifier='1'))

        # get response
        try:
            controller = ser.readline().decode('utf-8').strip().lower()
        except UnicodeDecodeError:
            ser.close()
        else:
            if 'smc' in controller:
                release_delay = None
                channels = ['']
                manufacturer = 'newport'
                model = 'smc'
                serial_number = ''
                detected = True
                settings = ser.get_settings()
                retval = (
                    'controller',
                    settings,
                    (
                        port,
                        manufacturer,
                        model,
                        serial_number,
                        detected,
                        channels,
                        release_delay,
                    ),
                )

            # no device detected
            ser.close()

    return retval


def find_lvpsu(port, config):
    """
    check if any of these devices are present on the given serial port:

           Keysight/Agilent E3647A (dual output)
    Hewlett-Packard/Agilent E3634A (single output)

    notes for this type of PSU:

    a null-modem/crossover adaptor needs to be added to the serial cable

    test commands using miniterm rather than putty, e.g.

    [avt@pc048057 dev]$ miniterm.py --port=/dev/ttyUSB1
    --- Miniterm on /dev/ttyUSB1: 9600,8,N,1 ---
    --- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    Agilent Technologies,E3647A,0,1.7-5.0-1.0

    When using Keysight Connection Expert 2018 on Windows, the Flow control
    setting in Windows Device Manger seems to have no effect. Hardware, None,
    or Xon / Xoff all seem to work.

    in essence, ignore what the manual says about remote mode and dsrstr:

    (1) do not put the PSU into remote mode. Keysight Connection Expert
    2018 doesn't do this on Windows, and it seems to cause problems here
    (2) do not use dsrdtr

    response for Keysight E3634A:

    [avt@pc048057 utilities]$ miniterm.py --port=/dev/ttyUSB0
    --- Miniterm on /dev/ttyUSB0: 9600,8,N,1 ---
    --- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    HEWLETT-PACKARD,E3634A,0,2.4-6.1-2.1

    SYST:VERS? yields the SCPI version e.g. 1997.0
    YYYY.V where the Y represents the year of the version,
    and the V represents the version number for that year.

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # ask device to identify itself
        ser.write(lexicon.power('e3647a', 'identify'))

        # attempt to read back response
        try:
            response = ser.readline()
        except (serial.SerialException, AttributeError):
            print(f'cannot access serial port {port}')
        else:
            response = response.lower()
            if b'agilent' in response or b'hewlett-packard' in response:
                parts = response.decode('utf-8').split(',')
                manufacturer = 'agilent'
                model = parts[1].strip()
                serial_number = ''
                detected = True
                settings = ser.get_settings()

                if model in {'e3647a', 'e3634a'}:
                    if model == 'e3647a':
                        release_delay = 0.01
                        channels = ['1', '2']
                    else:
                        release_delay = None
                        channels = ['']

                    retval = (
                        'lvpsu',
                        settings,
                        (
                            port,
                            manufacturer,
                            model,
                            serial_number,
                            detected,
                            channels,
                            release_delay,
                        ),
                    )
                else:
                    print(f'lvpsu: unrecognised model {model}')

        ser.close()

    return retval


def find_lvpsu_hmp4040(port, config):
    """
    check if any of these devices are present on the given serial port:

    Rohde & Schwarz HMP4040

    response to *IDN?:

    macbook:utilities avt$ python3 -m serial.tools.miniterm

    --- Available ports:
    ---  1: /dev/cu.Bluetooth-Incoming-Port 'n/a'
    ---  2: /dev/cu.SSDC         'n/a'
    ---  3: /dev/cu.usbserial-AH06DY15 'FT232R USB UART'
    --- Enter port index or full name: 3
    --- Miniterm on /dev/cu.usbserial-AH06DY15  9600,8,N,1 ---
    --- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    HAMEG,HMP4040,103781,HW50020001/SW2.51

    Some models also identify as ROHDE&SCHWARZ instead of HAMEG.

    (pve) pi@raspberrypi $ python3 -m serial.tools.miniterm

    --- Available ports:
    ---  1: /dev/ttyAMA0         'ttyAMA0'
    ---  2: /dev/ttyUSB0         'FT232R USB UART - FT232R USB UART'
    --- Enter port index or full name: 2
    --- Miniterm on /dev/ttyUSB0  9600,8,N,1 ---
    --- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    ROHDE&SCHWARZ,HMP4040,120224,HW50020003/SW2.70

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # ask device to identify itself
        ser.write(lexicon.power('hmp4040', 'identify'))

        # attempt to read back response
        try:
            response = ser.readline()
        except (serial.SerialException, AttributeError):
            print(f'cannot access serial port {port}')
        else:
            response = response.lower()
            if b'hameg' in response or b'rohde' in response:
                release_delay = 0.026
                parts = response.decode('utf-8').split(',')
                manufacturer = 'hameg'
                model = parts[1].strip()
                serial_number = parts[2].strip()
                detected = True
                settings = ser.get_settings()
                channels = ['1', '2', '3', '4']
                retval = (
                    'lvpsu',
                    settings,
                    (
                        port,
                        manufacturer,
                        model,
                        serial_number,
                        detected,
                        channels,
                        release_delay,
                    ),
                )

        ser.close()

    return retval


def find_hvpsu(port, config):
    """
    check if one of the following power supplies is present on the given
    serial port

        Keithley 2410
        ISEG SHQ 222M
        ISEG SHQ 224M

    this function also successfully identifies:
    Keithley 6517B electrometer / high resistance meter

    Keithley 2410 response to *IDN?
    KEITHLEY INSTRUMENTS INC.,MODEL 2410,4343654,C34 Sep 21 2016 15:30:00/A02  /K/M
    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(lexicon.power('2410', 'identify'))

        # attempt to read back response
        try:
            response = ser.readline().lower()
        except serial.SerialException:
            print(f'cannot access serial port {port}')
        else:
            if b'keithley' in response:
                release_delay = None
                parts = response.decode('utf-8').split(',')
                manufacturer = parts[0].partition(' ')[0]
                model = parts[1].rpartition(' ')[-1]
                serial_number = parts[2]
                detected = True
                channels = ['']
                settings = ser.get_settings()
                retval = (
                    'hvpsu',
                    settings,
                    (
                        port,
                        manufacturer,
                        model,
                        serial_number,
                        detected,
                        channels,
                        release_delay,
                    ),
                )
            else:
                # check for ISEG SHQ dual-channel power supplies

                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(0.5)

                # send CRLF first for sync
                ser.write(lexicon.power('shq', 'synchronise'))
                ser.readline()  # consume local echo
                ser.readline()  # consume local echo
                ser.readline()  # consume response to command in buffer

                # '#' command: read device identifier
                # device identifier does not contain a model number:
                # serial number;software release;Vout max;Iout max
                # e.g. ISEG SHQ 224M returns '484216;3.09;4000V;3mA'
                # e.g. ISEG SHQ 222M returns '484230;3.10;2000V;6mA'
                ser.write(lexicon.power('shq', 'identify'))
                ser.readline()  # consume local echo
                response = ser.readline()
                parts = [x.strip() for x in response.decode('utf-8').split(';')]
                if len(parts) == 4:
                    release_delay = 0.01
                    manufacturer = 'iseg'
                    model = 'shq'
                    serial_number = parts[0]
                    detected = True
                    channels = ['1', '2']
                    settings = ser.get_settings()
                    retval = (
                        'hvpsu',
                        settings,
                        (
                            port,
                            manufacturer,
                            model,
                            serial_number,
                            detected,
                            channels,
                            release_delay,
                        ),
                    )

        ser.close()

    return retval


def find_hvpsu_2614b(port, config):
    """
    check if a Keithley 2614b is present on the given serial port

    note that the language used for this generation of Keithley is quite
    different from earlier models

    e.g.

    d=localnode.description
    print(d)

    returns:

    Keithley Instruments SMU 2614B - 4428182

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(lexicon.power('2614b', 'identify'))

        # attempt to read back response
        try:
            response = ser.readline().lower()
        except serial.SerialException:
            print(f'cannot access serial port {port}')
        else:
            if b'keithley' in response:
                try:
                    release_delay = 0.01
                    parts = response.decode('utf-8').split()
                    manufacturer = parts[0]
                    model = parts[3]
                    serial_number = parts[5]
                    detected = True
                    channels = ['a', 'b']
                    settings = ser.get_settings()
                    retval = (
                        'hvpsu',
                        settings,
                        (
                            port,
                            manufacturer,
                            model,
                            serial_number,
                            detected,
                            channels,
                            release_delay,
                        ),
                    )
                except IndexError:
                    pass

        ser.close()

    return retval


def find_dmm_6500(port, config):
    """
    check if a Keithley DMM6500 is present on the given serial port

    *IDN? returns:
    KEITHLEY INSTRUMENTS,MODEL DMM6500,04592428,1.7.12b

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    # initialise and open serial port
    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(lexicon.instrument('dmm6500', 'identify'))

        # attempt to read back response
        try:
            response = ser.readline().lower()
        except serial.SerialException:
            print(f'cannot access serial port {port}')
        else:
            if b'keithley' in response:
                try:
                    release_delay = 0.01
                    # ['KEITHLEY INSTRUMENTS', 'MODEL DMM6500', '04592428', '1.7.12b']
                    parts = response.decode('utf-8').lower().split(',')
                    manufacturer = parts[0].split()[0]
                    model = parts[1].split()[-1]
                    serial_number = parts[2]
                    detected = True
                    channels = ['']
                    settings = ser.get_settings()
                    retval = (
                        'instrument',
                        settings,
                        (
                            port,
                            manufacturer,
                            model,
                            serial_number,
                            detected,
                            channels,
                            release_delay,
                        ),
                    )
                except IndexError:
                    pass

        ser.close()

    return retval


def detect_device_on_port(port, tests, configs):
    """
    try all tests on the given port in a bid to identify which category of
    device is present

    --------------------------------------------------------------------------
    args
        port : string
            port name
        tests : dict
            contains the function to call for each category of device
        configs : dict of dicts
            {device_type: serial_port_configuration, ...}
    --------------------------------------------------------------------------
    returns
        retval : tuple
            (category : string,
             settings : dict,
             (port : string,
              manufacturer : string,
              model : string,
              serial_number : string,
              detected : bool,
              channels : list,
              release_delay : float))
    --------------------------------------------------------------------------
    """
    retval = (None, None, (port, None, None, None, None, None, None))

    for test in tests:
        if DEBUG:
            print(f'checking {port} for {test}')

        retval = tests[test](port, configs[test])
        if retval[0] is not None:
            break

        # macOS seems to process serial port events more swiftly than CentOS
        # and Windows 7: need to give the devices enough time to respond
        # between requests
        time.sleep(0.3)

    return retval


##############################################################################
# format detail for detected device
##############################################################################


def display_found(device_type, value, padding):
    """
    print details for a device identified on a serial port

    --------------------------------------------------------------------------
    args
        device_type : string
            e.g. 'hvpsu'
        value : tuple (string, string, string, string, bool)
            e.g. (port, manufacturer, model, serial_number, detected_flag)
        padding : int
            the length of the longest device type
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    port, manufacturer, model, serial_number, *_ = value

    if device_type is None:
        print(f'{"None".rjust(padding)} on {port}: (no device identified)')
    else:
        details = [d for d in (manufacturer, model) if d]
        if serial_number:
            details.append(f's.no. {serial_number}')

        suffix = ' '.join(details)
        print(f'{device_type.rjust(padding)} on {port}: {suffix}')


##############################################################################
# main
##############################################################################


def main():
    """
    detect devices present on the serial ports, that are attached via
    FTDI USB to RS232 adaptors
    """
    args = check_arguments()

    ports = [
        com.device
        for com in stlp.comports()
        if common.rs232_port_is_valid(com)
    ]
    if not ports:
        all_ports = ', '.join(com.device for com in stlp.comports())
        sys.exit(f'No usable serial ports found: {all_ports}')

    if args.delay_dmm6500:
        tests = collections.OrderedDict(
            {
                'lvpsu': find_lvpsu,
                'lvpsu_hmp4040': find_lvpsu_hmp4040,
                'hvpsu': find_hvpsu,
                'hvpsu_2614b': find_hvpsu_2614b,
                'dmm_6500': find_dmm_6500,
                'controller': find_controller,
                'controller_smc': find_controller_smc,
            }
        )
    else:
        tests = collections.OrderedDict(
            {
                'dmm_6500': find_dmm_6500,
                'lvpsu': find_lvpsu,
                'lvpsu_hmp4040': find_lvpsu_hmp4040,
                'hvpsu': find_hvpsu,
                'hvpsu_2614b': find_hvpsu_2614b,
                'controller': find_controller,
                'controller_smc': find_controller_smc,
            }
        )

    # define serial port connection settings for each device
    # see https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    common_configuration = {
        'bytesize': serial.EIGHTBITS,
        'parity': serial.PARITY_NONE,
        'stopbits': serial.STOPBITS_ONE,
        'dsrdtr': False,
        'timeout': 1,
        'write_timeout': 1,
        'inter_byte_timeout': None,
    }
    configs = {
        'hvpsu': {
            'baudrate': 9600,
            'xonxoff': False,
            'rtscts': False,
        },
        'hvpsu_2614b': {
            'baudrate': 57600,
            'xonxoff': False,
            'rtscts': False,
        },
        'dmm_6500': {
            'baudrate': 38400,
            'xonxoff': False,
            'rtscts': False,
        },
        'controller': {
            'baudrate': 19200,
            'xonxoff': False,
            'rtscts': False,
        },
        'controller_smc': {
            'baudrate': 57600,
            'xonxoff': True,
            'rtscts': False,
        },
        'lvpsu': {
            'baudrate': 9600,
            'xonxoff': False,
            'rtscts': False,
        },
        'lvpsu_hmp4040': {
            'baudrate': 9600,
            'xonxoff': False,
            'rtscts': True,
        },
    }
    # create unions of common and device-specific configurations
    configs = {
        device: {**device_specific_configuration, **common_configuration}
        for device, device_specific_configuration in configs.items()
    }

    padding = max(map(len, tests))

    # store creation platform in cache
    found = {'platform': sys.platform.lower()}

    # detect devices on ports
    _ddop_pf = functools.partial(detect_device_on_port, tests=tests, configs=configs)
    with cf.ThreadPoolExecutor() as executor:
        detected = (executor.submit(_ddop_pf, port) for port in ports)
        for future in cf.as_completed(detected):
            key, settings, value = future.result()
            if key not in found:
                found[key] = (settings, [value])
            else:
                found[key][1].append(value)

            display_found(key, value, padding)

    # JSON output
    if args.nocache:
        print(f'\nJSON:\n\n{json.dumps(found)}')
    else:
        common.configcache_write(found, common.DEVICE_CACHE)
        print(f'\nWrote detected configuration to: {common.DEVICE_CACHE}')


##############################################################################
if __name__ == '__main__':
    main()
