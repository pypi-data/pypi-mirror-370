#!/usr/bin/env python3
"""
Change power supply polarity supplied to Peltier devices using pairs of SPDT
relays.

Assume we are using a SparkFun Qwiic HAT for Raspberry Pi [1] and one or
more Raspberry Pi Pico Relay Boards [2].

[1] https://www.sparkfun.com/products/14459
[2] https://shop.sb-components.co.uk/products/raspberry-pi-pico-relay-board
"""

import argparse
import sys
import types

from RPi import GPIO

from mmcb.common import ANSIColours


##############################################################################
# data structures
##############################################################################

class Peltier:
    """
    Peltier device.
    """
    __slots__ = {
        'device': 'Numeric identifier for the Peltier device.',
        'board': 'The relay board this device is controlled from.',
        'relay_0': 'The first of the pair of relays controlling this device.',
        'relay_1': 'The second of the pair of relays controlling this device.',
        'gpio': 'Raspberry Pi GPIO pin controlling both relays.'}

    def __init__(self, device, board, relay_0, relay_1, gpio):
        self.device = device
        self.board = board
        self.relay_0 = relay_0
        self.relay_1 = relay_1
        self.gpio = gpio

    def __repr__(self):
        return (f'Peltier('
                f'device={self.device}, '
                f'board={self.board}, '
                f'relay_0={self.relay_0}, '
                f'relay_1={self.relay_1}, '
                f'gpio={self.gpio})')

    def __str__(self):
        on_ansi = f'{ANSIColours.BOLD}{ANSIColours.FG_RED}negative{ANSIColours.ENDC}'
        off_ansi = f'{ANSIColours.BOLD}{ANSIColours.FG_BLUE}positive{ANSIColours.ENDC}'
        relay_stat = on_ansi if self._check_configuration() else off_ansi

        return (f'Peltier {self.device}, board {self.board}, '
                f'relays {self.relay_0} and {self.relay_1} (GPIO {self.gpio:>2}), '
                f'config: {relay_stat}')

    def _check_configuration(self):
        """
        Return a tuple containing the status of both relays controlling this Peltier.
        """
        return GPIO.input(self.gpio)

    def configure_positive(self):
        """
        Set for positive configuration, power supply positive terminal to
        Peltier red wire, power supply negative terminal to Peltier blue
        wire.
        """
        # if already positive, don't do anything
        if self._check_configuration() == GPIO.LOW:
            return True

        GPIO.output(self.gpio, GPIO.LOW)

        return self._check_configuration() == GPIO.LOW

    def configure_negative(self):
        """
        Set for negative configuration, power supply positive terminal to
        Peltier blue wire, power supply negative terminal to Peltier red
        wire.
        """
        # if already negative, don't do anything
        if self._check_configuration() == GPIO.HIGH:
            return True

        GPIO.output(self.gpio, GPIO.HIGH)

        return self._check_configuration() == GPIO.HIGH

    # sufficient to allow a list of class instances to be sorted
    def __lt__(self, value):
        return self.device < value.device


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
        description='Change power supply polarity supplied to a Peltier\
        device using pairs of SPDT relays. With no arguments this script\
        simply reports status of all relays and changes nothing. With just\
        the Peltier device number given, status for that device is given, and\
        again, no changes are made. Note that using just two SPDT\
        relays per Peltier, only configuration of polarity can be set.\
        IMPORTANT: Turning off each Peltier device must be performed using\
        the power supply - the power supply should be turned off before\
        polarity is changed.')
    parser.add_argument(
        'peltier_device_number', nargs='?', metavar='peltier_device_number',
        help='Peltier device identifier.',
        type=int, default=None, choices=[1, 2, 3, 4])

    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument(
        '-p', '--positive',
        action='store_true',
        help='Set positive polarity.')
    group1.add_argument(
        '-n', '--negative',
        action='store_true',
        help='Set negative polarity.')

    return parser.parse_args()


##############################################################################
def main():
    """
    Change power supply polarity supplied to Peltier devices using pairs of
    SPDT relays.
    """
    args = check_arguments()

    return_code = types.SimpleNamespace(
        # Successful operation.
        success=0,
        # Operation not permitted.
        error_eperm=1,
        # I/O error - plausible error code for relays not responding.
        error_eio=5,
        # Invalid - used here for invalid relay configuration
        error_einval=22)

    if not args.peltier_device_number and (args.positive or args.negative):
        print('-p and -n require a peltier device to be specified')
        return return_code.error_eperm

    # each relay board has 4 relays, two per Peltier device
    # {peltier_identifier: [board_identifier, (relay_1, relay_2), gpio], ...}
    peltier_config = {1: [1, (1, 2), 12],  # wire: brown, changed from 21 -> 12 due to faulty GPIO pin 21
                      2: [1, (3, 4), 20],  # wire: violet
                      3: [2, (1, 2), 16],  # wire: black
                      4: [2, (3, 4), 6]}   # wire: yellow

    # configuration of the test setup is incomplete, so only use the relays
    # for devices that are currently in use
    enabled_peltier_devices = {1, 2, 3, 4}

    # if the user has specified an enabled peltier, omit details of other devices
    if args.peltier_device_number:
        # device specified - only print status for the given device if it's enabled
        enabled_peltier_devices = enabled_peltier_devices.intersection({args.peltier_device_number})

    # return promptly with an error code if there are no devices to display
    if not enabled_peltier_devices:
        return return_code.error_eperm

    # basic GPIO configuration
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # create data structures for all required Peltier devices
    # and configure GPIO pins as outputs
    peltier_devices = set()
    for device in enabled_peltier_devices:
        board, (relay_0, relay_1), gpio = peltier_config[device]
        GPIO.setup(gpio, GPIO.OUT)
        peltier_devices.add(Peltier(device, board, relay_0, relay_1, gpio))

    # print current status
    status_check_only = not (args.positive or args.negative)
    if status_check_only:
        for device in sorted(peltier_devices):
            print(device)

        return return_code.success

    # at this point, there will only be one device remaining
    device = peltier_devices.pop()

    # process the user's command
    if args.positive:
        success = device.configure_positive()
    elif args.negative:
        success = device.configure_negative()
    else:
        success = False

    return return_code.success if success else return_code.error_einval


##############################################################################
if __name__ == '__main__':
    sys.exit(main())
