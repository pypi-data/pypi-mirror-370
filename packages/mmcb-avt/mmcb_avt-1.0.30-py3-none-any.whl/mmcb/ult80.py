#!/usr/bin/env python3
"""
Thermo Neslab ULT-80 Low Temperature Bath/Circulator RS232.

The controller looks quite primitive and doesn't use line terminators like
other devices in the test setup. Presumably it just looks for the 0xCA start
byte and ignores anything else when it's sent something unpredictable.

If this turns out not to be the case, we can read the list of available FTDI
serial port devices, then exclude any serial ports found in cache.json, then
leave the user to choose which of the remaining serial ports to use.

Refer to the following for RS232 command sequences:
https://www.atecorp.com/atecorp/media/pdfs/data-sheets/neslab-ult-80-95_manual.pdf

Also see 'setup loop' starting on page 10 to enable RS232.

"Enter the Setup Loop from the Operator's Loop by pressing and holding the NO
 key, then press the NEXT ENTER key. Use the YES/NO keys to adjust the
 values. Press the NEXT ENTER key twice to accept the new value."

tunE?
    YES (up triangle)
HEAt
    NEXT (circle)
rtd
    NEXT (circle)
SP
    NEXT (circle)
HIT
    NEXT (circle)
LoT
    NEXT (circle)
r232
    YES (up triangle)
ON
    YES (up triangle) (only if OFF)
    ENTER (circle)
    ENTER (circle)
bAUd
    YES (up) or NO (down) as appropriate - 9600
    ENTER (circle)
    ENTER (circle)
dAtA
    YES (up) or NO (down) as appropriate - 8
    ENTER (circle)
    ENTER (circle)
StoP
    YES (up) or NO (down) as appropriate - 1
    ENTER (circle)
    ENTER (circle)
Par
    YES (up) or NO (down) as appropriate - N
    ENTER (circle)
    ENTER (circle)
Stor (store changes)
    YES (up arrow)

"NOTE: Should you desire to return to the temperature display and abort all
 changes, keep pressing the NEXT ENTER until the display reads Stor, then
 press NO."
"""

import argparse
import sys

import serial
import serial.tools.list_ports as stlp

from mmcb import common


##############################################################################
# command line option handler
##############################################################################

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
        description='Thermo Neslab ULT-80 Low Temperature Bath/Circulator\
        RS232 tool.')

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '-i', '--read_internal_temperature',
        action='store_true',
        help='Read Internal Temperature.')
    group1.add_argument(
        '-r', '--read_setpoint',
        action='store_true',
        help='Read Setpoint (control point).')
    group1.add_argument(
        '-s', '--set_setpoint', nargs=1, metavar='degrees_c',
        help='Set Setpoint (control point).',
        default=None)

    return parser.parse_args()


##############################################################################
# detect ult80 serial port and basic operation
##############################################################################

def find_ult80(port, config):
    """
    Return serial port configuration if the serial port was successfully
    opened.

    --------------------------------------------------------------------------
    args
        port : string
            port name
        config : dict
            serial port configuration
    --------------------------------------------------------------------------
    returns
        retval :
            settings : dict (if port could be opened) or None otherwise
                Note that the dictionary does not contain the serial port
                identifier.
    --------------------------------------------------------------------------
    """
    ser = serial.Serial()
    ser.apply_settings(config)
    ser.port = port

    try:
        ser.open()
    except (OSError, serial.SerialException):
        sys.exit(f'could not open port {port}, exiting.')
    else:
        settings = ser.get_settings()
        ser.close()

    return settings


##############################################################################
# data structures
##############################################################################

class Ult80:
    """
    Thermo Neslab ULT-80 Low Temperature Bath/Circulator RS232.
    """
    _lead_char = 0xca
    _address = 0x0001
    _nbits = 16

    def __init__(self, ser):
        self.ser = ser

    ##########################################################################
    # public functions
    #
    # key:
    #
    # qb = qualifier byte
    #     0x10 : 0.1 precision, no units of measure
    #     0x20 : 0.01 precision, no units of measure
    #     0x11 : 0.1 precision, °C units
    #
    # Example: The temperature of 45.6 °C would be represented by the
    # qualifier 0x11, followed by the 2 bytes 0x01C8 (456 decimal).
    #
    # d1,d2 = 16-bit signed integer of the value being sent or received
    #
    # cs = the checksum of the string
    #
    # "All commands must be entered in the exact format shown in the tables on
    #  the following pages... Controller responses are either the requested
    #  data or an error message. The controller response must be received
    #  before sending the next command."
    #
    # "The host sends a command embedded in a single communications packet,
    #  then waits for the controller’s response. If the command is not
    #  understood or the checksums do not agree, the controller responds with
    #  an error command. Otherwise, the controller responds with the
    #  requested data. If the controller fails to respond within 1 second,
    #  the host should re-send the command."
    ##########################################################################

    def read_internal_temperature(self):
        """
        FUNCTION      : Read Internal Temperature
        MASTER SENDS  : CA 00 01 20 00 DE
        BATH RESPONDS : CA 00 01 20 03 qb d1 d2 cs

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : float (or None if the checksum was incorrect)
        ----------------------------------------------------------------------
        """
        command = 0x2000
        self.ser.write(self._build_command(command))

        return self._read_response()

    def read_setpoint_control_point(self):
        """
        FUNCTION      : Read Setpoint (control point)
        MASTER SENDS  : CA 00 01 70 00 8E
        BATH RESPONDS : CA 00 01 70 03 qb d1 d2 cs

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : float (or None if the checksum was incorrect)
        ----------------------------------------------------------------------
        """
        command = 0x7000
        self.ser.write(self._build_command(command))

        return self._read_response()

    def set_setpoint_control_point(self, deg_c):
        """
        FUNCTION      : Set Setpoint (control point)
        MASTER SENDS  : CA 00 01 F0 02 d1 d2 cs
        BATH RESPONDS : CA 00 01 F0 03 qb d1 d2 cs

        ----------------------------------------------------------------------
        args
            deg_c : float
        ----------------------------------------------------------------------
        returns
            decoded_value : float (or None if the checksum was incorrect)
        ----------------------------------------------------------------------
        """
        command = 0xf002
        self.ser.write(self._build_command(command, deg_c))

        return self._read_response()

    ##########################################################################
    # support functions
    ##########################################################################

    def _build_command(self, command, deg_c=None):
        """
        Build the sequence of bytes expected by the ULT-80 for the required
        command.

        ----------------------------------------------------------------------
        args
            command : int
                2-byte value
            deg_c : float
                temperature in degrees C
        ----------------------------------------------------------------------
        returns : bytes
            Sequence of bytes expected by the ULT-80 for the required command.
        ----------------------------------------------------------------------
        """
        lead_char = [self._lead_char]
        address = list(self._address.to_bytes(2, 'big'))
        command = list(command.to_bytes(2, 'big'))

        data = address + command
        if deg_c is not None:
            temperature = self._encode_temperature(deg_c)
            data += temperature

        return bytes(lead_char + data + [self._create_checksum(data)])

    def _read_response(self, debug_data=None):
        """
        Generic read response, e.g. CA 00 01 F0 03 11 01 2C CD

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns
            decoded_value : float (or None if the checksum was incorrect)
        ----------------------------------------------------------------------
        """
        # read the first five bytes, so the last byte contains the number of
        # following data bytes - 3 in this instance - then the remaining
        # checksum byte.
        # e.g. CA 00 01 F0 03
        if debug_data is None:
            response_part_1 = self.ser.read(size=5)
        else:
            response_part_1 = debug_data[:5]

        if not response_part_1:
            return None

        if debug_data is None:
            bytes_to_read = response_part_1[-1] + 1
            response_part_2 = self.ser.read(size=bytes_to_read)
        else:
            response_part_2 = debug_data[5:]

        # verify response
        response = response_part_1 + response_part_2

        if self._verify_checksum(response):
            qualifier_byte = response_part_2[0]
            encoded_value = response_part_2[1:3]
            decoded_value = self._decode_value(encoded_value, qualifier_byte=qualifier_byte)
        else:
            decoded_value = None

        return decoded_value

    def _twos_complement(self, value):
        """
        Generates the two's complement of the given integer, handles negative
        numbers. Reversible.

        ----------------------------------------------------------------------
        args
            value : int
        ----------------------------------------------------------------------
        returns
            value : int
        ----------------------------------------------------------------------
        """
        if value < 0:
            value = (1 << self._nbits) + value
        else:
            if (value & (1 << (self._nbits - 1))) != 0:
                # most-significant bit set (sign)
                value = value - (1 << self._nbits)

        return value

    def _encode_temperature(self, temperature):
        """
        Express a temperature value (degrees C) as a 16-bit signed value then
        convert to a pair of bytes in high/low order.

        ----------------------------------------------------------------------
        args
            temperature : float
                Temperature in degrees Celsius, positive or negative, only one
                decimal place supported.
        ----------------------------------------------------------------------
        returns : list of two ints
            Each value is a byte value in high/low order.
                e.g.
                    encode_temperature(30) returns
                    [1, 44] or ['0x1', '0x2c']

                    encode_temperature(-10.5) returns
                    [255, 151] or ['0xff', '0x97']
        ----------------------------------------------------------------------
        """
        value = self._twos_complement(int(temperature * 10))

        return list(value.to_bytes(2, 'big'))

    def _decode_value(self, value, qualifier_byte=0x11):
        """
        Decode two-byte value received from ULT-80 into human-readable value.

        ----------------------------------------------------------------------
        args
            value : list of two ints
                contains individual byte values
            qualifier_byte : int
                This will be one of three values:
                    0x10 : 0.1 precision, no units of measure
                    0x20 : 0.01 precision, no units of measure
                    0x11 : 0.1 precision, °C units
        ----------------------------------------------------------------------
        returns
            val : float
        ----------------------------------------------------------------------
        """
        if qualifier_byte not in {0x10, 0x11, 0x20}:
            return None

        denominator = 10 if qualifier_byte in {0x10, 0x11} else 100
        val = self._twos_complement(int.from_bytes(value, 'big')) / denominator

        return val

    @staticmethod
    def _create_checksum(data):
        """
        Generate single byte checksum from data.

        Bitwise inversion of the 1 byte sum of bytes beginning with the most
        significant address byte and ending with the byte preceding the
        checksum. (To perform a bitwise inversion, "exclusive OR" the one
        byte sum with FF hex.)

        ----------------------------------------------------------------------
        args
            data : list of ints
                contains individual byte values, list should only contain data
                for checksumming - no other byte values
        ----------------------------------------------------------------------
        returns : int
            a single byte value
        ----------------------------------------------------------------------
        """
        return (sum(data) & 0xff) ^ 0xff

    def _verify_checksum(self, entire_response):
        """
        Verify checksum from received data.

        ----------------------------------------------------------------------
        args
            entire_response : list of ints
                Contains individual byte values, list should contain all
                received data.
        ----------------------------------------------------------------------
        returns : boolean
            True if checksums match, False otherwise.
        ----------------------------------------------------------------------
        """
        _lead_char, *data, checksum = entire_response

        return self._create_checksum(data) == checksum


##############################################################################
# main
##############################################################################

def main():
    """
    Thermo Neslab ULT-80 Low Temperature Bath/Circulator RS232.
    """
    args = check_arguments()

    # obtain available ports
    all_ports = {com.device for com in stlp.comports() if common.rs232_port_is_valid(com)}
    if not all_ports:
        sys.exit('No usable serial ports found')

    # find ports already allocated to other devices
    cache = common.cache_read()

    # If a port has None in its settings field, then it was not identified by
    # detect.py, and can therefore still be considered for use by this
    # script.
    identified_ports_in_cache = {k for k, v in cache.items() if v[0] is not None}

    # usable ports for this script
    available_ports = all_ports - identified_ports_in_cache

    if len(available_ports) > 1:
        sys.exit(f'Too many ports to choose from: {available_ports}')
    elif not available_ports:
        sys.exit('No usable serial ports available')

    port = available_ports.pop()
    print(f'using port {port}')
    config = {'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1,
              'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 1,
              'write_timeout': 1, 'inter_byte_timeout': None}

    settings = find_ult80(port, config)
    if settings is None:
        sys.exit('Serial port could not be opened')

    with serial.Serial(port=port) as ser:
        ser.apply_settings(settings)

        ult80 = Ult80(ser)

        if args.read_internal_temperature:
            rval = ult80.read_internal_temperature()
            if rval is None:
                print('no response from device')
            else:
                print(f'read_internal_temperature, returned value {rval}°C')

        if args.read_setpoint:
            rval = ult80.read_setpoint_control_point()
            if rval is None:
                print('no response from device')
            else:
                print(f'read_setpoint_control_point, returned value {rval}°C')

        if args.set_setpoint:
            rval = ult80.set_setpoint_control_point(float(args.set_setpoint[0]))
            if rval is None:
                print('no response from device')
            else:
                print(f'set_setpoint_control_point, returned value {rval}°C')


##############################################################################
if __name__ == '__main__':
    main()
