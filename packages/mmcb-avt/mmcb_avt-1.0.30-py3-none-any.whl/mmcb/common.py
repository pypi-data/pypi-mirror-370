"""
Common functions

callable functions from this file:

    atomic_send_command_read_response
    cache_read
    check_current
    check_file_exists
    check_ports_accessible
    data_read
    data_write
    decimal_quantize
    dew_point
    exclude_channels
    initial_power_supply_check
    interpret_numeric
    iseg_value_to_float
    list_split
    log_with_colour
    missing_ports
    ports_to_channels
    rate_limit
    read_aliases
    read_psu_measured_vi
    report_output_status
    round_safely
    rs232_port_is_valid
    save_plot
    send_command
    set_psu_voltage
    set_psu_voltage_and_read
    si_prefix
    stage_speed
    synchronise_psu
    timestamp_to_utc
    time_axis_adjustment
    unique
    wait_for_voltage_to_stabilise
    write_consignment_csv

data structures:

    ANSIColours
    Channel
    Consignment
    DEVICE_CACHE
    Packet
    UNIT
"""

import argparse
import bz2
import collections
import contextlib
import copy
import datetime
import decimal
import itertools
import json
import logging
import os
import pickle
import re
import sys
import time
import types

import matplotlib
# agg is used only for writing plots to files, not to the window manager
# this option is set to avoid problems running scripts on remote hosts
# over ssh, matplotlib.use must be called in this exact position
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import serial

from mmcb import lexicon


##############################################################################
# data structures
##############################################################################


DEVICE_CACHE = os.path.expanduser('~/.cache.json')


UNIT = types.SimpleNamespace(
    calculated_dew_point='DP\u00b0C',
    flow_rate='lps',
    pressure='hPa',
    relative_humidity='RH%',
    strain='arbitrary',
    temperature='\u00b0C',
    vacuum='kPa',
)


class ANSIColours:
    """
    ANSI 3/4 bit terminal escape sequences

    https://en.wikipedia.org/wiki/ANSI_escape_code
    """
    # foreground colours
    FG_BRIGHT_BLACK = '\033[90m'
    FG_BRIGHT_RED = '\033[91m'
    FG_BRIGHT_GREEN = '\033[92m'
    FG_BRIGHT_YELLOW = '\033[93m'
    FG_BRIGHT_BLUE = '\033[94m'
    FG_BRIGHT_MAGENTA = '\033[95m'
    FG_BRIGHT_CYAN = '\033[96m'
    FG_BRIGHT_WHITE = '\033[97m'

    FG_BLACK = '\033[30m'
    FG_RED = '\033[31m'
    FG_GREEN = '\033[32m'
    FG_YELLOW = '\033[33m'
    FG_BLUE = '\033[34m'
    FG_CYAN = '\033[35m'
    FG_MAGENTA = '\033[36m'
    FG_WHITE = '\033[37m'

    # background colours
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # attributes
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BLINK = '\033[5m'
    UNDERLINE = '\033[4m'


class Packet:
    """
    This class holds all data acquired from a single power supply channel
    during a single run of iv.py.

    The IV and IT data may represent one of the following three scenarios:

    * A single outbound IV
    * A single outbound IV and IT
    * An outbound IV, IT, and return IV
    """
    __slots__ = {
        'manufacturer': 'The manufacturer of the power supply.',
        'model': 'The model name of the power supply.',
        'serial_number': 'The serial number of the power supply.',
        'channel': 'Which power supply channel was data acquired from.',
        'ident': 'hardware identifier string or user supplied alias',
        'set_voltage': 'IV data: list of set voltages.',
        'measured_current': 'IV data: list of measured leakage currents at each set voltage',
        'sigma_current': 'Standard deviation of each measured leakage current figure.',
        'measured_voltage': 'IV data: list of measured bias voltages at each set voltage',
        'measured_timestamp': 'IV data: timestamp of each data acquisition',
        'measured_temperature': 'IV data: temperature (°C) at each data acquisition',
        'measured_humidity': 'IV data: humidity (RH%) at each data acquisition',
        'hold_voltage': 'IT data: constant set voltage for IT test',
        'hold_current': 'IT data: list of measured leakage currents at each set voltage',
        'hold_timestamp': 'IT data: timestamp of each data acquisition',
        'hold_temperature': 'IT data: temperature (°C) at each data acquisition',
        'hold_humidity': 'IT data: humidity (RH%) at each data acquisition',
        'itk_serno': 'ATLAS Itkpix module serial number IF SUPPLIED'}

    def __init__(self, manufacturer, model, serial_number, channel, ident, itk_serno):
        self.manufacturer = manufacturer
        self.model = model
        self.serial_number = serial_number
        self.channel = channel
        self.ident = ident
        self.itk_serno = itk_serno
        self.set_voltage = []
        self.measured_current = []
        self.sigma_current = []
        self.measured_voltage = []
        self.measured_timestamp = []
        self.measured_temperature = []
        self.measured_humidity = []
        self.hold_voltage = None
        self.hold_current = []
        self.hold_timestamp = []
        self.hold_temperature = []
        self.hold_humidity = []

    def __repr__(self):
        return (f'Packet('
                f'manufacturer="{self.manufacturer}", '
                f'model="{self.model}", '
                f'serial_number="{self.serial_number}", '
                f'channel="{self.channel}", '
                f'ident="{self.ident}", '
                f'set_voltage={self.set_voltage}, '
                f'measured_current={self.measured_current}, '
                f'measured_voltage={self.measured_voltage}, '
                f'sigma_current={self.sigma_current}, '
                f'measured_timestamp={self.measured_timestamp}, '
                f'measured_temperature={self.measured_temperature}, '
                f'measured_humidity={self.measured_humidity}, '
                f'hold_voltage={self.hold_voltage}, '
                f'hold_current={self.hold_current}, '
                f'hold_timestamp={self.hold_timestamp}, '
                f'hold_temperature={self.hold_temperature}, '
                f'hold_humidity={self.hold_humidity})')

    def __str__(self):
        # verbose power supply identifier
        identifier = f'{self.manufacturer} {self.model}'
        if self.serial_number:
            identifier += f' s.no. {self.serial_number}'
        if self.channel:
            identifier += f' channel {self.channel}'

        # number of data points in IV and IT tests
        try:
            split_index = self.measured_current.index('split')
        except ValueError:
            outbound_iv_len = len(self.measured_current)
            return_iv_len = 0
        else:
            outbound_iv_len = len(self.measured_current[:split_index])
            return_iv_len = len(self.measured_current[split_index + 1:])

        out_iv_text = f'Outbound IV data points : {outbound_iv_len}'
        hold_it_text = f'IT data points : {len(self.hold_current)}'
        ret_iv_text = f'Return IV data points : {return_iv_len}'

        return '\n'.join([identifier, out_iv_text, hold_it_text, ret_iv_text])

    # sufficient to allow a list of class instances to be sorted
    def __lt__(self, value):
        return (f'{self.model}{self.serial_number}{self.channel}'
                < f'{value.model}{value.serial_number}{value.channel}')

    def extract_environmental_data(self, category, test_iv, outbound=True):
        """
        Extract measurements from their originally stored state to one that is
        more readily usable for data analysis.

        For the desired data source, the dict within the list represents
        measurements from all the available sensors within the category at a
        given point in time (for IT tests) or per voltage step (for IV tests).

        e.g.
        [{'PT100MK1-DC3D6': 22.31, 'PT100MK1-DC392': 19.16}, ...]

        These lists may have had a 'split' marker added by function
        run_iv_test() in iv.py if both outbound and return IV tests were
        requested.

        ----------------------------------------------------------------------
        args
            category : string
                'temperature' or 'humidity'
            test_iv : bool
                True = data from IV test, False = data from IT test
            outbound : bool
                For lists that may contain a 'split' marker, outbound = True
                selects items before the marker, False selects items after the
                marker. For other lists, this is ignored.
        ----------------------------------------------------------------------
        returns : dict
            e.g.
            {'PT100MK1-DC3D6': [21.25, 21.25, 21.26, 21.26, ..., 21.24],
             'PT100MK1-DC392': [20.9, 20.92, 20.92, 20.94, ..., 20.94]}
        ----------------------------------------------------------------------
        """
        assert category in {'temperature', 'humidity'}, 'unknown category'

        # select original data source
        temp = category == 'temperature'
        if test_iv:
            var = self.measured_temperature if temp else self.measured_humidity
            out, ret = list_split(var)
            var = out if outbound else ret
        else:
            var = self.hold_temperature if temp else self.hold_humidity

        # transform selected data
        summary = collections.defaultdict(list)

        for measurement in var:
            for sensor, reading in measurement.items():
                summary[sensor].append(reading)

        # return transformed data source
        return dict(summary)

    def extract_timestamp_data(self, test_iv, outbound=True):
        """
        Extract timestamps to match data obtained by
        self.extract_environmental_data.

        ----------------------------------------------------------------------
        args
            test_iv : bool
                True = data from IV test, False = data from IT test
            outbound : bool
                For lists that may contain a 'split' marker, outbound = True
                selects items before the marker, False selects items after the
                marker. For other lists, this is ignored.
        ----------------------------------------------------------------------
        returns : list
            e.g.
                [21.25, 21.25, 21.26, 21.26, ..., 21.24]
        ----------------------------------------------------------------------
        """
        # select original data source
        if test_iv:
            out, ret = list_split(self.measured_timestamp)
            var = out if outbound else ret
        else:
            var = self.hold_timestamp

        return var

    @staticmethod
    def _unpack_environmental_data(data, first_only=True):
        """
        The iv.py software is written to accumulate environmental data
        (temperature/humidity) from all Yoctopuce sensors that acquire those
        parameters. The supplied data is grouped by data point, return the
        supplied data grouped by sensor to make it easier to process.

        ----------------------------------------------------------------------
        args
            data : list of dict
                e.g.
                    [
                        {"METEOMK2-12E3A7": 46.2},
                        {"METEOMK2-12E3A7": 46.0},
                        ...
                        {"METEOMK2-12E3A7": 46.0},
                        {"METEOMK2-12E3A7": 46.0},
                    ]

                This data is a list of dicts, where each dict contains all
                sensors that returned a reading for that data point.
            first_only : bool
                Only return data for the first sensor found, this is used to
                make sure that we have
        ----------------------------------------------------------------------
        returns : dict or list of values
            e.g.
                for multiple sensors:
                {
                    "METEOMK2-12E3A7": [46.2, 46.0, ... 46.0, 46.0],
                    "METEOMK2-12E3B4": [45.1, 45.2, ... 45.4, 45.3],
                }
                for a single sensor:
                [46.2, 46.0, ... 46.0, 46.0]

        Returned data is grouped by sensor. If there is only one sensor, there
        is little value in tagging the values with the sensor they came from,
        so a list is returned. If there is more than one sensor, then the data
        is returned grouped by sensor.

        ----------------------------------------------------------------------
        """
        # grouped by data point -> grouped by sensor
        sendat = collections.defaultdict(list)

        for point in data:
            for sensor, values in point.items():
                sendat[sensor].append(values)

        sendat = dict(sendat)

        # if there's only one sensor, just return a list of its values
        lsendat = len(sendat)
        if lsendat == 1:
            return next(iter(sendat.values()))
        elif lsendat > 1 and first_only:
            logging.info(
                '_unpack_environmental_data: arbitrary sensor chosen (from n=%s)',
                lsendat
            )
            return next(iter(sendat.values()))

        return sendat

    def write_json(self, session):
        """
        Write JSON file to mass storage for ATLAS Itkpix.

        Only data for the outbound IV test is transferred to the JSON file.
        Return IV and IT information, if present, is omitted.

        Refer to specification:
        https://itk.docs.cern.ch/pixels/sensors/upload_tests_sensor_PDB/

        Institute codes:
        https://itk.docs.cern.ch/general/Production_Database/Institute_Codes/
        """
        filename = f'{session}_{self.itk_serno}.json'

        # only interested in 'outbound IV': ignore any 'return IV' data
        osvo, _rsvo = list_split(self.set_voltage)
        omcu, _rmcu = list_split(self.measured_current)
        ocsi, _rcsi = list_split(self.sigma_current)
        omvo, _rmvo = list_split(self.measured_voltage)
        omti, _rmti = list_split(self.measured_timestamp)
        omte, _rmte = list_split(self.measured_temperature)
        omhu, _rmhu = list_split(self.measured_humidity)

        # Convert current measurements to uA
        omcu[:] = [x * 1000000 for x in omcu]

        # iv.py can be run in forward or reverse bias, present values as
        # positive polarity
        furthest_from_zero = max(osvo, key=abs)
        if furthest_from_zero < 0:
            for outbound_var in [osvo, omcu, ocsi, omvo]:
                outbound_var[:] = [-x for x in outbound_var]

        # check number of data points in array match
        temp = self._unpack_environmental_data(omte)
        humi = self._unpack_environmental_data(omhu)

        losvo = len(osvo)
        lomcu = len(omcu)
        locsi = len(ocsi)
        ltemp = len(temp)
        lhumi = len(humi)

        if not losvo == lomcu == locsi == ltemp == lhumi:
            logging.info(
                'write_json: IV_ARRAY length mismatch: svo %s, mcu %s, csi %s, temp %s, humi %s',
                losvo, lomcu, locsi, ltemp, lhumi
            )
            logging.info(
                'write_json: refer to https://itk.docs.cern.ch/pixels/sensors/'
                'upload_tests_sensor_PDB/#iv-checking-your-data-input'
            )
            logging.info('write_json: malformed JSON file created')

        # "Date/time format should be: YYYY-MM-DD followed by a 'T' then the hour,
        # then a colon followed by the minute then a Z e.g."
        # '2025-03-26T13:14Z'
        #
        # See https://docs.python.org/3/library/datetime.html
        #     #strftime-and-strptime-format-codes
        #
        # The Z indicates zulu time (UTC/GMT)
        #
        # dts = datetime.datetime.fromtimestamp(min(omti), datetime.UTC).strftime('%Y-%m-%dT%H:%MZ')
        dts = datetime.datetime.utcfromtimestamp(min(omti)).strftime('%Y-%m-%dT%H:%MZ')

        # Create the JSON file even if it's malformed, to help the user
        # diagnose the issue.
        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(
                {
                    'component': self.itk_serno,
                    'test': 'IV',
                    'institution': 'LIV',
                    'date': dts,
                    'prefix': 'uA',
                    'depletion_voltage': max(osvo),
                    'IV_ARRAY': {
                        'voltage': osvo,
                        'current': omcu,
                        'sigma current': ocsi,
                        'temperature': temp,
                        'humidity': humi,
                      }
                },
                outfile,
            )


class Consignment:
    """
    Contains data for an entire data acquisition session, which may include
    packets from multiple power supplies, each of which may have multiple
    channels.
    """
    __slots__ = {
        'label': 'Plot title string.',
        'safe_label': ('Either a simplified version of the label string that may be\n'
                       'appended to a filename and is easy to work with on the command\n'
                       'line, or None'),
        'aliases': ('A dictionary containing mappings between power supply channel\n'
                    'hardware identifiers and user-submitted descriptions of each\n'
                    'channel\'s purpose.'),
        'forwardbias': ('A boolean indicating whether the user specified forward bias\n'
                        'operation.'),
        'hold': 'A boolean indicating whether the user specified an IT test',
        'environmental_data_present': ('A boolean indicating that environmental sensors'
                                       'are presented.'),
        'packets': ('A list containing the data packets captured during an entire\n'
                    'data acquisition session.')}

    def __init__(self, label, aliases, forwardbias, hold, environmental_data_present):
        self.label = label
        self.aliases = aliases
        self.forwardbias = forwardbias
        self.hold = hold
        self.environmental_data_present = environmental_data_present
        self.packets = []

        # create a safe and easy to work with label for appending to a
        # filename later
        if self.label:
            self.safe_label = ''.join(c
                                      for c in self.label.replace(' ', '-')
                                      if c not in r'<>:"/\|?*')
        else:
            self.safe_label = None

    def __repr__(self):
        return (f'Consignment('
                f'label="{self.label}", '
                f'aliases={self.aliases}, '
                f'forwardbias={self.forwardbias}, '
                f'hold={self.hold}, '
                f'environmental_data_present={self.environmental_data_present})')

    def __str__(self):
        pretty = [f'label: {self.label}', f'safe_label: {self.safe_label}',
                  f'aliases: {self.aliases}', f'forwardbias: {self.forwardbias}',
                  f'hold: {self.hold}',
                  f'environmental_data_present: {self.environmental_data_present}',
                  f'number of packets: {len(self.packets)}']

        return '\n'.join(pretty)

    def remove_bad_packets(self):
        """
        Only retain usable packets. This operation should be performed before
        attempting to plot or store data.
        """
        self.packets = [packet
                        for packet in self.packets
                        if packet is not None and len(packet.set_voltage) > 1]

    def write_json_files(self, session):
        """
        Write all packet data to filestore.
        """
        for packet in self.packets:
            packet.write_json(session)


class Channel:
    """
    Handle power supplies on a per-channel basis.
    """
    __slots__ = {
        'port': 'Serial port on which to communicate with the power supply.',
        'config': 'Serial port configuration parameters.',
        'serial_number': 'The serial number of the power supply.',
        'model': 'The model name of the power supply.',
        'manufacturer': 'The manufacturer of the power supply.',
        'channel': 'Which power supply channel to use.',
        'category': 'Tailor behaviour for high or low voltage use.',
        'release_delay': 'Delay between sequential serial port interactions.',
        'ident': 'hardware identifier string or user supplied alias.',
        'window_size': 'Size of measured_voltages and measured_currents queues.',
        'measured_voltages': 'Queue to store voltages for smoothing.',
        'measured_currents': 'Queue to store currents for smoothing.'}

    def __init__(self, port, config, serial_number, model, manufacturer,
                 channel, category, release_delay, alias):
        self.port = port
        self.config = config
        self.serial_number = serial_number
        self.model = model
        self.manufacturer = manufacturer
        self.channel = channel
        self.category = category
        self.release_delay = release_delay
        self.window_size = 10
        self.measured_voltages = collections.deque([], self.window_size)
        self.measured_currents = collections.deque([], self.window_size)

        _parameters = (self.model, self.serial_number, self.channel)
        _ident_key = '_'.join(p for p in _parameters if p).lower()
        _text = ' '.join(p for p in _parameters if p).lower()
        try:
            _text = alias.get(_ident_key, _text)
        except AttributeError:
            # alias is None
            pass
        finally:
            self.ident = _text

    def __repr__(self):
        return (f'Channel('
                f'port="{self.port}", config={self.config}, '
                f'serial_number="{self.serial_number}", '
                f'model="{self.model}", '
                f'manufacturer="{self.manufacturer}", '
                f'channel="{self.channel}", '
                f'category="{self.category}", '
                f'release_delay={self.release_delay}, '
                f'ident="{self.ident}")')

    def __str__(self):
        description = f'{self.manufacturer} {self.model} s.no. {self.serial_number}'
        description += f' ch. {self.channel}' if self.channel else ''
        return description

    # sufficient to allow a list of class instances to be sorted
    def __lt__(self, value):
        return (f'{self.model}{self.serial_number}{self.channel}'
                < f'{value.model}{value.serial_number}{value.channel}')

    # sufficient to allow a class instance to be removed from a list
    def __eq__(self, value):
        return (f'{self.model}{self.serial_number}{self.channel}'
                == f'{value.model}{value.serial_number}{value.channel}')


##############################################################################
# file i/o
##############################################################################

def _file_is_compressed(filename):
    """
    Determine if a data file is compressed from its extension.

    --------------------------------------------------------------------------
    args
        filename : string
    --------------------------------------------------------------------------
    returns
        restored_progress : boolean
            True if the filename extension indicates a compressed file,
            False otherwise
    --------------------------------------------------------------------------
    """
    return 'bz2' in os.path.splitext(filename)[-1].lower()


def configcache_read(filename):
    """
    Retrieve previously stored serial port configuration and attached devices
    from human-readable cache file.

    --------------------------------------------------------------------------
    args
        filename : string
    --------------------------------------------------------------------------
    returns
        restored_progress : dict
            deserialized cached data or None
    --------------------------------------------------------------------------
    """
    restored_progress = None

    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as infile:
            try:
                restored_progress = json.load(infile)
            except json.JSONDecodeError:
                sys.exit(f'exiting: problem reading data from {filename}')

    return restored_progress


def configcache_write(data, filename):
    """
    Store serial port configuration and attached devices to cache in
    human-readable form.

    --------------------------------------------------------------------------
    args
        data : dict
            a record each detected device, its respective category and
            serial port configuration.
        filename : string
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    with open(filename, 'w', encoding='utf-8') as outfile:
        try:
            json.dump(data, outfile)
        except TypeError:
            sys.exit(f'exiting: problem writing data to {filename}')


def data_read(filename):
    """
    Retrieve previously stored data from file.

    --------------------------------------------------------------------------
    args
        filename : string
    --------------------------------------------------------------------------
    returns
        restored_progress : unpickled data or None
    --------------------------------------------------------------------------
    """
    restored_progress = None

    if os.path.isfile(filename):
        file_read = bz2.open if _file_is_compressed(filename) else open

        with file_read(filename, 'rb') as infile:
            try:
                restored_progress = pickle.load(infile)
            except (pickle.UnpicklingError, AttributeError, EOFError,
                    ImportError, IndexError, TypeError):
                sys.exit(f'exiting: problem reading data from {filename}')

    return restored_progress


def data_write(data, filename):
    """
    Store data to file for later retrieval.

    --------------------------------------------------------------------------
    args
        data : data structure to store
        filename : string
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    file_write = bz2.open if _file_is_compressed(filename) else open

    with file_write(filename, 'wb') as outfile:
        try:
            pickle.dump(data, outfile)
        except pickle.PicklingError:
            sys.exit(f'exiting: problem writing data to {filename}')


def read_aliases(settings, filename):
    """
    Read in alias file, and write results to settings:
        (1) create a dictionary of aliases
        (2) create a dictionary of channels to ignore

    Comments starting with a # are allowed.

    e.g.

    # Keithley 2614b
    ,2614b,4428182,a,layer front # blue pcb v1.0a
    ,2614b,4428182,b,layer rear  # green pcb v1.0b
    # Keithley 2410 (borrowed from cleanroom)
    ,2410,4343654,,neutron detector
    off,2410,1390035,,layer external # off-axis

    which would generate aliases as indicated in the log:

    INFO : alias 2614b_4428182_a -> layer front
    INFO : alias 2614b_4428182_b -> layer rear
    INFO : alias 2410_4343654 -> neutron detector

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        filename : string
            filename with extension
    --------------------------------------------------------------------------
    returns
        settings : dict
            no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    if os.path.exists(filename):
        alias = {}
        ignore = {}

        with open(filename, 'r', encoding='utf-8') as csvfile:
            for line_num, row in enumerate(csvfile):
                # remove comments
                no_comment = row.split('#')[0].strip()

                # separate comma separated values
                fields = (field.strip() for field in no_comment.split(','))
                try:
                    enable, model, serialnum, channel, description = fields
                except ValueError:
                    # not enough values to unpack
                    if no_comment:
                        print(f'line {line_num} (expected 5 fields): {no_comment}')
                    continue

                identifier = '_'.join(x for x in [model, serialnum, channel] if x).lower()

                if description:
                    alias[identifier] = description.replace('"', '').replace('\'', '')

                if enable.lower() in {'no', 'off', 'disable'}:
                    ignore[identifier] = True

        settings['alias'] = alias if alias else None
        settings['ignore'] = ignore if ignore else None
    else:
        print(f'file {filename} could not be read from')


def save_plot(settings, filename):
    """
    Save plot to mass storage in the requested file format.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        filename : string
            filename without extension
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if settings['svg']:
        plt.savefig(f'{filename}.svg')
    else:
        plt.savefig(f'{filename}.png', dpi=400)


def write_consignment_csv(consignment, row):
    """
    Write recorded data in consignment to mass storage.

    ASSUMES a file has been opened for writing.

    --------------------------------------------------------------------------
    args
        consignment : instance of class Consignment
            contains data for the whole data acquisition session
        row : csv.writer
            writer object responsible for converting data to delimited strings
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    # --label: write label if user has supplied it
    if consignment.label is not None:
        row.writerow(itertools.chain(['label'], [consignment.label]))

    # --alias: write aliases if user has supplied them
    if consignment.aliases is not None:
        for channel_identifier, alias in consignment.aliases.items():
            row.writerow(itertools.chain(['alias'], [channel_identifier], [alias]))

    stored_as_dict = {'measured_temperature', 'hold_temperature',
                      'measured_humidity', 'hold_humidity'}
    not_iterable = {'channel', 'hold_voltage', 'ident',
                    'manufacturer', 'model', 'serial_number'}

    # write all data packets
    for packet in consignment.packets:

        # extract data from instance of class Packet in (key, value) pairs
        # if the value contains something
        # use __slots__ to maintain ordering
        packet_data = {k: getattr(packet, k) for k in packet.__slots__
                       if getattr(packet, k)}

        for field, item in packet_data.items():
            if field in not_iterable:
                row.writerow(itertools.chain([field], [item]))
            elif field in stored_as_dict:
                # list will contain dicts that need to be extracted, e.g.
                # [{'PT100MK1-DC3D6': 20.52, 'PT100MK1-DC392': 19.9},
                #  {'PT100MK1-DC3D6': 20.52, 'PT100MK1-DC392': 19.89}, ...]
                tmd = collections.defaultdict(list)
                for temp_measurement in item:
                    if temp_measurement != 'split':
                        for sensor, reading in temp_measurement.items():
                            tmd[sensor].append(reading)
                    else:
                        for sensor in tmd:
                            tmd[sensor].append(temp_measurement)

                # write the rows to the csv file
                for sensor, measurements in tmd.items():
                    row.writerow(itertools.chain([f'{field} ({sensor})'], measurements))
            else:
                # item is a plain list
                row.writerow(itertools.chain([field], item))


##############################################################################
# identifier/alias management
##############################################################################

def _alias_to_log(settings):
    """
    Enter the mapping of power supply channel identifiers to aliases into the
    log.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if settings['alias'] is not None:
        for ident, alias in settings['alias'].items():
            logging.info('alias: %s -> %s', ident, alias)


def _lookup_reference(packet, use_channel=True, separator=' '):
    """
    For the given data packet, return the hardware identifier for its power
    supply channel.

    --------------------------------------------------------------------------
    args
        packet : instance of class Channel
            Contains data for a given power supply channel's IV and IT curves.
        use_channel : bool
            If True, use channel identifier in returned string.
            Useful to disable when working at power supply level
            rather than channel-level, e.g. when checking power supply
            interlocks and creating error logs that would be misleading if
            they contained a channel identifier.
        separator : string
            Separator character used between values, typically ' ' or '_'.
    --------------------------------------------------------------------------
    returns : string
        e.g.
            use_channel=True
                '2410 1272738' (single channel)
                '2614b 4428182 b' (dual channel)
            use_channel=False
                '2410 1272738' (single channel)
                '2614b 4428182' (dual channel)
    --------------------------------------------------------------------------
    """
    text = f'{packet.model}'
    if packet.serial_number:
        text += f'{separator}{packet.serial_number}'
    if packet.channel and use_channel:
        text += f'{separator}{packet.channel}'

    return text


def _lookup_decorative(alias, packet):
    """
    Decorative print of the power supply channel with its alias (if it
    exists).

    --------------------------------------------------------------------------
    args
        alias : dictionary
            maps aliases to power supply channel identifiers
        packet : packet : instance of class Packet or class Channel
            contains data for a given power supply channel's IV and IT curves
    --------------------------------------------------------------------------
    returns : string
        e.g.
        'keithley 2614b s.no. 4428182 channel b (layer rear)'
        or
        'keithley 2614b s.no. 4428182 channel a'
    --------------------------------------------------------------------------
    """
    parameters = (packet.model, packet.serial_number, packet.channel)
    ident_key = '_'.join(p for p in parameters if p).lower()

    dtext = f'{packet.manufacturer} {packet.model}'
    if packet.serial_number:
        dtext += f' s.no. {packet.serial_number}'
    if packet.channel:
        dtext += f' channel {packet.channel}'

    try:
        atext = alias[ident_key]
    except (KeyError, TypeError):
        suffix = ''
    else:
        suffix = f' ({atext})'

    return f'{dtext}{suffix}'


##############################################################################
# utilities
##############################################################################


def decimal_quantize(value, decimal_places):
    """
    Returns a decimal rounded to the user-specified number of decimal places.

    --------------------------------------------------------------------------
    args
        value : numeric or string representation of numeric
        decimal_places : positive integer
    --------------------------------------------------------------------------
    returns : decimal.Decimal
    --------------------------------------------------------------------------
    """
    value = decimal.Decimal(value)

    # 0: '0', 1: '0.1', 2: '0.01' etc...
    decplc = f'{pow(10, -decimal_places):.{decimal_places}f}'

    return value.quantize(decimal.Decimal(decplc), rounding=decimal.ROUND_HALF_UP)


def dew_point(tdc, rhp):
    """
    Calculate the dew point given temperature and humidity.

    https://en.wikipedia.org/wiki/Dew_point

    Murray, F. W., 1967, On the Computation of Saturation Vapor Pressure

    Magnus, Tetens : pressure in mbar
    t = 20.1 (deg C)
    u = 7.5
    v = 237.3
    w = 0.7858 (vapor pressure in mbar)

    In [25]: math.pow(10, (t * u)/(t + v) + w)
    Out[25]: 23.521463268069194

    For low temperature and low pressure with accuracy, use Goff-Gratch.

    --------------------------------------------------------------------------
    args
        tdc : float
            temperature degrees Celsius
        rhp : float
            relative humidity percentage
    --------------------------------------------------------------------------
    returns : float
        dew point degrees Celsius
    --------------------------------------------------------------------------
    """
    # constants
    # a = 6.1121 # mbar
    b = 18.678
    c = 257.14  # °C
    d = 234.5   # °C

    ymtrh = np.log((rhp / 100) * np.exp((b - tdc / d) * (tdc / (c + tdc))))
    tdp = (c * ymtrh) / (b - ymtrh)

    return tdp


def interpret_numeric(val):
    """
    Convert numbers in either engineering or scientific notation from string
    form to a float.

    Useful resource: https://regex101.com

    --------------------------------------------------------------------------
    args
        val : string
    --------------------------------------------------------------------------
    returns
        success : bool
        val : float if conversion was successful, otherwise return the
            problematic string
    --------------------------------------------------------------------------
    """
    success = True

    eng_notation = re.match(r'^[+\-]?\d*\.?\d*[yzafpnumkMGTPEZY]$', val)
    sci_notation = re.match(r'^[+\-]?(?:\d+\.|\d+\.\d+|\.\d+|\d+)(?:[eE][+\-]?\d+)?$', val)

    if eng_notation is not None:
        value = float(eng_notation[0][:-1])
        suffix = eng_notation[0][-1]
        val = value * pow(10, 'yzafpnum kMGTPEZY'.find(suffix) * 3 - 24)
    elif sci_notation is not None:
        val = float(sci_notation[0])
    else:
        success = False

    return success, val


def iseg_value_to_float(value):
    """
    For values read back from ISEG SHQ power supplies.

    While set voltages are specified as positive-only magnitudes (with
    polarity defined by the hardware switch on the rear panel), the values
    read back have the correct polarity.

    e.g.

    Set PSU channel 1 voltage to 120V with:

    D1=120 (sets voltage)
    G1 (requests power supply to ramp up to given voltage)

    poll G1 until it responds with S1=ON

    U1 returns with (polarity, significand, signed exponent):
    -01200-01

    which this function returns as -120.0

    --------------------------------------------------------------------------
    args
        value : string
            response from ISEG command
    --------------------------------------------------------------------------
    returns
        fvalue : float
    --------------------------------------------------------------------------
    """
    fvalue = None
    significand, exponent = value[:-3], value[-3:]

    with contextlib.suppress(ValueError):
        fvalue = float(f'{significand}e{exponent}')

    return fvalue


def list_split(data):
    """
    Split list at the 'split' marker.

    --------------------------------------------------------------------------
    args
        data : list
    --------------------------------------------------------------------------
    returns
        out : list
        ret : list
    --------------------------------------------------------------------------
    """
    try:
        split_index = data.index('split')
    except ValueError:
        out = data
        ret = []
    else:
        out = data[:split_index]
        ret = data[split_index + 1:]

    return out, ret


def round_safely(start, stop, step, first=True):
    """
    Round the value to the given step "in the direction of travel" so the
    resultant value is always contained within the bounds of start and stop.

    --------------------------------------------------------------------------
    args
        start : numeric (int, float or decimal.Decimal)
            start value of the number sequence
        stop : numeric (int, float or decimal.Decimal)
            stop value of the number sequence
        step : int
            step size
        first : bool
            if True, round the start value, if False, round the stop value
    --------------------------------------------------------------------------
    returns : int
        rounded and aligned value
    --------------------------------------------------------------------------
    """
    step = abs(step)
    value, step = (float(start), step) if first else (float(stop), -step)
    return int(value - (value % -step if start < stop else value % step))


def si_prefix(value, dec_places=3, compact=True):
    """
    Provide an approximation of the given number in engineering
    representation, to the given number of decimal places, with the SI
    (Systeme Internationale) unit prefix appended.

    --------------------------------------------------------------------------
    args
        value : string, float or int
            numeric value
        dec_places : int
            number of decimal places to display
        compact : bool
            if True remove trailing zeros from number, if the remainder is a
            whole number, remove the trailing decimal point
            e.g.
            103.100 -> 103.1
             10.000 ->  10
    --------------------------------------------------------------------------
    returns : string or None
        value with SI unit prefix
    --------------------------------------------------------------------------
    """
    # make sure the number is in scientific notation
    # then separate value and exponent
    try:
        significand, exponent = f'{float(value):e}'.lower().split('e')
    except TypeError:
        return None

    significand = float(significand)
    exponent = int(exponent)

    # align with 10**3 boundaries
    while exponent % 3 != 0:
        exponent -= 1
        significand *= 10

    if -24 <= exponent <= 24:
        # derive SI unit prefix
        if exponent == 0:
            prefix = ''
        else:
            prefix = 'yzafpnum kMGTPEZY'[8 + exponent // 3]

        # remove trailing zeroes
        # if the number is a whole number, remove the trailing decimal point as well
        significand = f'{significand:.{dec_places}f}'
        if compact:
            # avoid rstrip('0.') to ensure '0.0' doesn't become ''
            significand = significand.rstrip('0').rstrip('.')
    else:
        # handle the case where the supplied value is too large or too small
        prefix = ''
        significand = float(value)

    return f'{significand}{prefix}'


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


def time_axis_adjustment(data):
    """
    Generate the parameters necessary to transform absolute UNIX-style epoch
    timestamps to relative timestamps with human-readable units.

    --------------------------------------------------------------------------
    args
        data : pandas.DataFrame
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

    return units


##############################################################################
# command line argument processing
##############################################################################

def check_current(val):
    """
    Checks current values.

    Note that the Keithley 2410 will not allow compliance values to be set
    to less than 0.1% of the measurement range, p.18-69 (p.449 in PDF).

    --------------------------------------------------------------------------
    args
        val : string
    --------------------------------------------------------------------------
    returns
        val : float
    --------------------------------------------------------------------------
    """
    success, val = interpret_numeric(val)

    if not success:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'should be a value in engineering or scientific notation')

    if val < 1e-9:
        raise argparse.ArgumentTypeError(
            f'{val}: '
            'is too small for range of the power supply')

    return val


def check_file_exists(filename):
    """
    check if file exists

    --------------------------------------------------------------------------
    args
        val : string
            filename, e.g. '20200612_132725_psuwatch.log'
    --------------------------------------------------------------------------
    returns : string
    --------------------------------------------------------------------------
    """
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError(f'{filename}: file does not exist')

    return filename


##############################################################################
# cache import
##############################################################################

def _logprint(uselog, level, message):
    """
    Display via logging module or print as appropriate.

    --------------------------------------------------------------------------
    args
        uselog : bool
            use logging if True, print otherwise
        level : int
            logging level e.g. logging.DEBUG
        text : string
            text to display
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if uselog:
        log_with_colour(level, message)
    else:
        print(message)


def cache_read(device_types=None, uselog=False, quiet=True):
    """
    Get the details of all the given devices from the cache, and in the process
    transform the dictionary from having device types as keys, to having
    port names as keys.

    --------------------------------------------------------------------------
    args
        device_types : list or None
            device types to search cache for e.g. ['hvpsu', 'lvpsu']
            valid types are: controller, daq, hvpsu, lvpsu
            if this is None, do not check for validity, import all devices
        uselog : bool
            use print if False (default), otherwise use the logging module
        quiet : bool
            no printing
    --------------------------------------------------------------------------
    returns
        found : dict
            {port: ({port_config}, device_type, device_serial_number), ...}
    --------------------------------------------------------------------------
    """
    cache = configcache_read(DEVICE_CACHE)

    if cache is None:
        _logprint(
            uselog,
            logging.CRITICAL,
            'please run detect.py before using this script (cache missing)'
        )
        sys.exit()

    # if the plaform differs from the platform the cache was created on, the
    # serial port data contained in the cache will almost certainly be wrong
    cached_platform = cache.pop('platform', None)
    if cached_platform is not None and cached_platform != sys.platform.lower():
        _logprint(
            uselog,
            logging.CRITICAL,
            'please run detect.py before using this script (platform mismatch)'
        )
        sys.exit()

    found = {}
    for device_type, device_details in cache.items():
        if device_types is not None and device_type not in device_types:
            continue

        serial_config = device_details[0]

        # there may be multiple devices for this device type
        for device in device_details[1]:
            port, manufacturer, model, serial_number, _, channels, release_delay = device
            found[port] = (serial_config, device_type, serial_number, model, manufacturer,
                           channels, release_delay)
            snu = serial_number if serial_number else 'unknown'
            if not quiet:
                _logprint(
                    uselog, logging.INFO,
                    f'cache: {manufacturer} {model} serial number {snu} on {port}'
                )

    if not found:
        _logprint(
            uselog,
            logging.CRITICAL,
            f'cache did not contain any matching devices: {", ".join(device_types)}'
        )
        sys.exit()

    return found


def ports_to_channels(settings, found):
    """
    Convert the per-port data structure read from the cache file (as written
    by detect.py), and convert it to a per-channel data structure that is
    necessary for scripts that need to manage multiple-channel power supplies.

    Ignores anything in 'found' that isn't a power supply.

    --------------------------------------------------------------------------
    args
        settings : dict
            contains core information about the test environment
        found : dict
            {port: ({port_config}, device_type,
                    device_serial_number, model, channels), ...}
            e.g.
            {'/dev/cu.usbserial-AH06DY15': ({'baudrate': 9600, 'bytesize': 8,
                                             'parity': 'N', 'stopbits': 1,
                                             'xonxoff': False, 'dsrdtr': False,
                                             'rtscts': False, 'timeout': 1,
                                             'write_timeout': 1,
                                             'inter_byte_timeout': None},
                                            'hvpsu',
                                            '1272738',
                                            '2614b',
                                            'keithley',
                                            ['a', 'b'])}
    --------------------------------------------------------------------------
    returns
        channels : list containing instances of class Channel
            e.g.
            [Channel(port="/dev/cu.usbserial-AH06DY15",
                     config={'baudrate': 9600, 'bytesize': 8, 'parity': 'N',
                             'stopbits': 1, 'xonxoff': False, 'dsrdtr': False,
                             'rtscts': False, 'timeout': 1,
                             'write_timeout': 1, 'inter_byte_timeout': None},
                     serial_number="4428182", model="2614b",
                     manufacturer="keithley", channel="a", category="hvpsu"),
             Channel(port="/dev/cu.usbserial-AH06DY15",
                     config={'baudrate': 9600, 'bytesize': 8, 'parity': 'N',
                             'stopbits': 1, 'xonxoff': False, 'dsrdtr': False,
                             'rtscts': False, 'timeout': 1,
                             'write_timeout': 1, 'inter_byte_timeout': None},
                     serial_number="4428182", model="2614b",
                     manufacturer="keithley", channel="b", category="hvpsu")]
    --------------------------------------------------------------------------
    """
    channels = []

    for port, details in found.items():
        (config, device_type, serial_number, model,
         manufacturer, psu_channels, release_delay) = details

        if device_type not in {'hvpsu', 'lvpsu'}:
            continue

        for channel in psu_channels:
            channels.append(Channel(port, config, serial_number,
                                    model, manufacturer, channel,
                                    device_type, release_delay,
                                    settings['alias']))

    return channels


def exclude_channels(settings, channels):
    """
    Exclude power supply channels from testing that the user has
    specified using the --alias command line option. The default is to leave
    a channel off.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        channels : list containing instances of class Channel
            e.g.
            [Channel(port="/dev/cu.usbserial-AH06DY15",
                     config={'baudrate': 9600, 'bytesize': 8, 'parity': 'N',
                             'stopbits': 1, 'xonxoff': False, 'dsrdtr': False,
                             'rtscts': False, 'timeout': 1,
                             'write_timeout': 1, 'inter_byte_timeout': None},
                     serial_number="4428182", model="2614b",
                     manufacturer="keithley", channel="a", category="hvpsu"),
             Channel(port="/dev/cu.usbserial-AH06DY15",
                     config={'baudrate': 9600, 'bytesize': 8, 'parity': 'N',
                             'stopbits': 1, 'xonxoff': False, 'dsrdtr': False,
                             'rtscts': False, 'timeout': 1,
                             'write_timeout': 1, 'inter_byte_timeout': None},
                     serial_number="4428182", model="2614b",
                     manufacturer="keithley", channel="b", category="hvpsu")]
    --------------------------------------------------------------------------
    returns
        channels : list containing instances of class Channel
            e.g. see above
    --------------------------------------------------------------------------
    """
    try:
        return [channel
                for channel in channels
                if _lookup_reference(channel, separator='_') not in settings['ignore']]
    except TypeError:
        return channels


##############################################################################
# motion controller
##############################################################################

def stage_speed(controller_type, stage, speed):
    """
    mm4006 does not have a command to return the stage type, so assume that
    the stage is an ims400ccha as this matches the experimental setup.

    --------------------------------------------------------------------------
    args
        controller_type : string
            name of the controller
        stage : string
            name of the stage
        speed : string
            'slow', 'normal' or 'fast'
    --------------------------------------------------------------------------
    returns : tuple (int, int)
        acceleration, max_velocity
    --------------------------------------------------------------------------
    """
    ils150 = {'slow': (5, 2), 'normal': (5, 5), 'fast': (10, 10)}
    ims400 = {'slow': (6, 4), 'normal': (6, 8), 'fast': (6, 12)}
    accvel = {'ils150pp': ils150, 'ims400': ims400}

    if 'mm4006' in controller_type and 'unknown' in stage:
        stage = 'ims400'

    return accvel[stage][speed]


##############################################################################
# serial port interaction
##############################################################################

def rs232_port_is_valid(com):
    """
    Detect if serial port is an FTDI device.

    Compare each string to each variable; a match in any one is sufficient
    for the whole test to pass. The values in com may be None, 'n/a' or the
    text supplied by a detected device.

    The FTDI USB to RS232 adapter deployed in the test environment is:
    Startech Network Adapter ICUSB2321F
    https://www.startech.com/en-us/cards-adapters/icusb2321f
    https://uk.rs-online.com/web/p/serial-converters-extenders/1238048/

    Oncology Systems Limited (OSL) recommended USB to RS232 adaptor for IBA
    products is also based on an FTDI chipset (untested):
    https://www.delock.de/produkt/61460/merkmale.html?setLanguage=en

    --------------------------------------------------------------------------
    args
        com : stlp.ListPortInfo
            contains human-readable information regarding the serial port
    --------------------------------------------------------------------------
    returns
        success : bool
            True if this is an FTDI device, False otherwise
    --------------------------------------------------------------------------
    """
    # The Digilent Nexys 4 Artix-7 FPGA Trainer Board used as part of the
    # neutron detector setup shares data with Sam's Windows DAQ application
    # via a shared UART/JTAG USB port. This uses an onboard FTDI device, so
    # ensure no scripts in this suite will interact with it.
    if com.hwid == 'USB VID:PID=0403:6010 SER=210274552605B':
        return False

    success = False
    test_strings = ('FTDI', 'FT232R', 'FT232R')
    test_variables = (com.manufacturer, com.product, com.description)

    for tstr, tvar in zip(test_strings, test_variables):
        try:
            test = tstr in tvar
        except TypeError:
            pass
        else:
            success = success or test
            if test:
                break

    return success


def atomic_send_command_read_response(pipeline, ser, dev, command):
    """
    Atomic send serial port command and receive reply.

    Each serial port associated with a power supply has a lock, and power
    supplies are managed on a per-channel basis. The locks are used to ensure
    that threads controlling channels on multiple-channel PSUs do not attempt
    to use their shared serial port at the same time.

    An exception on the initial serial port write should not happen unless
    the serial port has been disconnected from the computer.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
        command : bytes
            command to be sent via RS232 to the power supply
    --------------------------------------------------------------------------
    returns
        response : string or None
            returned command string
    --------------------------------------------------------------------------
    """
    # only proceed if no other thread is using this port
    with pipeline.portaccess[dev.port]:
        # if this is a multiple-channel psu, allow some settling time before
        # accessing the serial port
        with contextlib.suppress(TypeError):
            time.sleep(dev.release_delay)

        try:
            ser.write(command)
        except serial.SerialException:
            response = None
            message = f'{dev.ident}, cannot access serial port'
            log_with_colour(logging.ERROR, message)
        else:
            # attempt to read back response
            try:
                response = ser.readline()
            except serial.SerialException:
                response = None
                message = f'{dev.ident}, cannot access serial port'
                log_with_colour(logging.ERROR, message)
            else:
                if dev.manufacturer == 'iseg':
                    # ISEG SHQ replies with local echo on first line
                    # and response on the second line
                    response = ser.readline()

    # AttributeError: handle case where response is None
    with contextlib.suppress(AttributeError):
        response = response.strip().decode('utf-8', errors='replace')

    return response


def send_command(pipeline, ser, dev, command):
    """
    Send serial port command only.

    This is typically used where a response is not expected from the power
    supply and attempting to read a response will only result in a "long" wait
    for the serial port to time out. In general do not use this function with
    ISEG power supplies, since they always echo something, and whatever that
    is needs to be consumed to prevent problems later.

    Each serial port associated with a power supply has a lock, and power
    supplies are managed on a per-channel basis. The locks are used to ensure
    that threads controlling channels on multiple-channel PSUs do not attempt
    to use their shared serial port at the same time.

    An exception on the initial serial port write should not happen unless
    the serial port has been disconnected from the computer.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
        command : bytes
            command to be sent via RS232 to the power supply
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    with pipeline.portaccess[dev.port]:
        # if this is a multiple-channel psu, allow some settling time before
        # accessing the serial port
        with contextlib.suppress(TypeError):
            time.sleep(dev.release_delay)

        try:
            ser.write(command)
        except serial.SerialException:
            message = f'{dev.ident}, cannot access serial port'
            log_with_colour(logging.ERROR, message)


def check_ports_accessible(found, channels, close_after_check=True):
    """
    Check that all the ports listed in cache entries can be successfully
    opened.

    This attempts to open unique serial ports. Hence, for multiple-channel
    devices, only a single attempt is made to open its port.

    --------------------------------------------------------------------------
    args
        found : dict
            {port: ({port_config}, device_type,
                    device_serial_number, model), ...}
            e.g.
            {'/dev/cu.usbserial-AH06DY15': ({'baudrate': 9600, 'bytesize': 8,
                                             'parity': 'N', 'stopbits': 1,
                                             'xonxoff': False, 'dsrdtr': False,
                                             'rtscts': False, 'timeout': 1,
                                             'write_timeout': 1,
                                             'inter_byte_timeout': None},
                                            'hvpsu',
                                            '1272738',
                                            '2410')}
        channels : list containing instances of class Channel
        close_after_check : bool
            defaults to True, psustat.py sets this to False to keep checked
            ports open.
    --------------------------------------------------------------------------
    returns
        spd : dict
            {port: serial_port_identifier, ...}
            E.g.
            {'/dev/ttyUSB0': Serial<id=0xaf4e9c70, open=True>
                             (port='/dev/ttyUSB0', baudrate=9600, bytesize=8,
                              parity='N', stopbits=1, timeout=1,
                              xonxoff=False, rtscts=True, dsrdtr=False),
             '/dev/ttyUSB1': Serial<id=0xaf553b50, open=True>
                             (port='/dev/ttyUSB1', baudrate=9600, bytesize=8,
                              parity='N', stopbits=1, timeout=1,
                              xonxoff=False, rtscts=False, dsrdtr=False)}
            This is ignored by most callers, it's only currently used by
            psustat.py.
        channels : list containing instances of class Channel
            no explicit return - mutable type amended in place
    --------------------------------------------------------------------------
    """
    port_missing = False

    spd = {}
    for port, value in found.items():
        config, *_ = value

        ser = serial.Serial()
        ser.apply_settings(config)
        ser.port = port
        try:
            ser.open()
        except (FileNotFoundError, OSError, serial.SerialException):
            port_missing = True
            message = f'could not open port {port}'
            log_with_colour(logging.ERROR, message)
            break
        else:
            if close_after_check:
                ser.close()
            else:
                spd[port] = ser

    if port_missing:
        # remove everything from channels to prevent any data being taken
        # given that it's probably better to have the user fix the problem
        # with the test configuration, rather than continuing the test
        # with part(s) of the setup inactive
        channels.clear()
        message = 'not all serial ports listed in the cache were accessible'
        log_with_colour(logging.ERROR, message)
        message = 'check connections and/or run ./detect.py'
        log_with_colour(logging.ERROR, message)

    return spd


def missing_ports(found):
    """
    Check that all the ports listed in cache entries can be successfully
    opened.

    --------------------------------------------------------------------------
    args
        found : dict
            {port: ({port_config}, device_type,
                    device_serial_number, model), ...}
            e.g.
            {'/dev/cu.usbserial-AH06DY15': ({'baudrate': 9600, 'bytesize': 8,
                                             'parity': 'N', 'stopbits': 1,
                                             'xonxoff': False, 'dsrdtr': False,
                                             'rtscts': False, 'timeout': 1,
                                             'write_timeout': 1,
                                             'inter_byte_timeout': None},
                                            'hvpsu',
                                            '1272738',
                                            '2410')}
    --------------------------------------------------------------------------
    returns
        port_missing : bool
            True if at least one port could not be successfully opened,
            False otherwise
    --------------------------------------------------------------------------
    """
    port_missing = False

    for port, value in found.items():
        config, *_ = value

        ser = serial.Serial()
        ser.apply_settings(config)
        ser.port = port
        try:
            ser.open()
        except (FileNotFoundError, serial.SerialException):
            port_missing = True
            print(f'could not open port {port}')
        else:
            ser.close()

    return port_missing


##############################################################################
# power supply interaction
##############################################################################

def _channel_mismatch(cache, user):
    """
    Check for a match between the channel identifier from the cache and the
    one supplied by the user.

    Users are likely to incorrectly specify channel identifiers, since some
    manufacturers use letters and some use numbers. If there is an
    alphanumeric mismatch between cache and user values, this alone should not
    be sufficient to remove the channel.

    --------------------------------------------------------------------------
    args
        cache : string, single character
            channel identifier read from cache, e.g. '1', '2', 'a' or 'b'
        user : string, single character
            channel identifier from command line, e.g. '1', '2', 'a' or 'b'
    --------------------------------------------------------------------------
    returns : bool
        True if the two arguments match, False otherwise
    --------------------------------------------------------------------------
    """
    cache_alpha = cache.isalpha()
    if cache_alpha != user.isalpha():
        if cache_alpha:
            user = chr(ord(user) - ord('1') + ord('a'))
        else:
            user = str(ord(user) - ord('a') + 1)

    return cache != user


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
        check_ports_accessible(psus, channels)

        for dev in channels:
            message = f'enabled: {_lookup_decorative(settings["alias"], dev)}'
            log_with_colour(logging.INFO, message)

            with serial.Serial(port=dev.port) as ser:
                ser.apply_settings(dev.config)

                # try to ensure consistent state
                # clear FTDI output buffer state before sending
                ser.reset_output_buffer()
                # clear PSU state
                if dev.model == '2614b':
                    command_string = lexicon.power(dev.model, 'terminator only',
                                                   channel=dev.channel)
                    send_command(pipeline, ser, dev, command_string)
                # clear FTDI input buffer state
                ser.reset_input_buffer()
                # arbitrary settle time before proceeding
                time.sleep(0.5)

                # ensure serial port communication with PSU
                # this is for ISEG SHQ only, on a per-PSU basis
                if not port_used[dev.port]:
                    synchronise_psu(ser, pipeline, dev)

                # check power supply output
                # but don't do this if called from psuset.py, since the user
                # of that script may be issuing a command to turn a
                # power supply channel output on
                if not psuset:
                    outstat.append(report_output_status(ser, pipeline, dev))

                # check interlock
                # this is per-PSU on Keithley, per-channel on ISEG
                if ((not port_used[dev.port] or dev.manufacturer == 'iseg')
                        and dev.manufacturer not in {'agilent', 'hameg'}):
                    intstat.append(_report_interlock_status(ser, pipeline, dev))

                if dev.manufacturer == 'iseg':
                    polstat.append(_report_polarity_status(settings, ser, pipeline, dev, psuset))

                ser.reset_input_buffer()
                ser.reset_output_buffer()

            port_used[dev.port] += 1

        if any(outstat):
            message = 'all power supply outputs must be on to proceed'
            log_with_colour(logging.ERROR, message)
            channels.clear()

        if any(intstat):
            message = 'all power supply interlocks must be inactive to proceed'
            log_with_colour(logging.ERROR, message)
            channels.clear()

        if any(polstat):
            if psuset:
                message = 'set voltage should agree with polarity switch to proceed'
                log_with_colour(logging.ERROR, message)
            else:
                message = 'all polarity switches must agree with --forwardbias to proceed'
                log_with_colour(logging.ERROR, message)

            channels.clear()
    else:
        message = '--debug: any connected power supplies will be ignored'
        log_with_colour(logging.WARNING, message)
        message = '--debug: IV data will generated internally'
        log_with_colour(logging.WARNING, message)


def rate_limit(timestamp, duration):
    """
    Sleep the thread to limit the rate of change of voltage to the
    device under test. The execution time of the thread is taken into account
    to ensure that the rate of change of voltage is not limited more than
    necessary.

    --------------------------------------------------------------------------
    args
        timestamp : float
            value previously returned by time.monotonic()
        duration : float
            nominal delay time in seconds required to not exceed the desired
            volts-per-second rate limit
    --------------------------------------------------------------------------
    returns : float
        value returned by time.monotonic(), this value will be returned to
        this function at the next call as argument timestamp
    --------------------------------------------------------------------------
    """
    if timestamp is not None:
        tdiff = time.monotonic() - timestamp
        if tdiff < duration:
            time.sleep(duration - tdiff)
    else:
        time.sleep(duration)

    return time.monotonic()


def read_psu_measured_vi(pipeline, ser, dev):
    """
    Read the voltage and current as measured at the psu output terminals
    from a high voltage power supply.

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
        measured_voltage : float or None
        measured_current : float or None
    --------------------------------------------------------------------------
    """
    measured_voltage = measured_current = None

    if dev.manufacturer in {'agilent', 'iseg'}:
        convert = iseg_value_to_float if dev.manufacturer == 'iseg' else float

        command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
        local_buffer = atomic_send_command_read_response(pipeline, ser, dev, command_string)
        with contextlib.suppress(ValueError):
            measured_voltage = convert(local_buffer)

        command_string = lexicon.power(dev.model, 'read current', channel=dev.channel)
        local_buffer = atomic_send_command_read_response(pipeline, ser, dev, command_string)
        with contextlib.suppress(ValueError):
            measured_current = convert(local_buffer)

        if measured_voltage is None or measured_current is None:
            measured_voltage = measured_current = None

    elif dev.manufacturer == 'keithley':
        command_string = lexicon.power(dev.model, 'read measured vi', channel=dev.channel)
        local_buffer = atomic_send_command_read_response(pipeline, ser, dev, command_string)

        if local_buffer is not None:
            separator = ',' if dev.model == '2410' else None
            items = (float(x) for x in local_buffer.split(separator))

            try:
                measured_voltage = next(items)
                measured_current = next(items)
            except (StopIteration, ValueError):
                measured_voltage = measured_current = None
                message = f'{dev.ident} problem reading measured vi'
                log_with_colour(logging.WARNING, message)

    return measured_voltage, measured_current


def _report_interlock_status(ser, pipeline, dev):
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
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    assert dev.manufacturer not in {'agilent', 'hameg'},\
        'function not callable for Agilent or Hameg PSU'

    fail = False
    interlock_set = False

    command_string = lexicon.power(dev.model, 'check interlock', channel=dev.channel)
    register = atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.manufacturer == 'iseg':
        # Interlocks are per-channel for ISEG SHQ, so include the channel
        # identifier in the ident string. For consistency with Keithley below
        # do not report the alias to the user.
        ident = _lookup_reference(dev)
        interlock_set = '=INH' in register
    else:
        # Interlocks are per-PSU for Keithley, so omit the channel identifier
        # if it exists.
        ident = _lookup_reference(dev, use_channel=False)
        try:
            regval = int(float(register))
        except ValueError:
            message = f'{ident}, problem checking interlock'
            log_with_colour(logging.WARNING, message)
            fail = True
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
                else:
                    message = f'{ident}, problem checking interlock'
                    log_with_colour(logging.WARNING, message)

    if interlock_set:
        message = f'{ident}, interlock active'
        log_with_colour(logging.WARNING, message)
        fail = True

    return fail


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
    output = atomic_send_command_read_response(pipeline, ser, dev, command_string)

    if dev.manufacturer == 'iseg':
        if '=ON' not in output:
            log_with_colour(logging.WARNING, f'{dev.ident}, output off')
            fail = True

    elif dev.manufacturer in {'agilent', 'hameg', 'keithley'}:
        try:
            outval = int(float(output))
        except ValueError:
            message = f'{dev.ident}, problem checking output'
            log_with_colour(logging.WARNING, message)
            fail = True
        else:
            if outval in {0, 1}:
                if outval == 0:
                    message = f'{dev.ident}, output off'
                    log_with_colour(logging.WARNING, message)
                    fail = True
            else:
                message = f'{dev.ident}, problem checking output'
                log_with_colour(logging.WARNING, message)
                fail = True

    return fail


def _report_polarity_status(settings, ser, pipeline, dev, psuset):
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
        settings : dictionary
            contains core information about the test environment
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
        psuset : bool
            selects the error message depending on the caller
    --------------------------------------------------------------------------
    returns
        fail : bool
            True if the channel's hardware-set polarity was found to conflict
            with the user's forward/reverse bias command line setting,
            False otherwise
    --------------------------------------------------------------------------
    """
    assert dev.model == 'shq', 'function only callable for ISEG SHQ PSU'

    fail = False
    message = ''

    command_string = lexicon.power(dev.model, 'check module status', channel=dev.channel)
    register = atomic_send_command_read_response(pipeline, ser, dev, command_string)

    try:
        polarity_negative = int(register) & 4 == 0
    except ValueError:
        fail = True
        message = f'{dev.ident} problem checking polarity'
        log_with_colour(logging.WARNING, message)
    else:
        poltxt = 'negative' if polarity_negative else 'positive'
        polvol = 'negative' if settings['voltage'] < 0 else 'positive'

        if psuset:
            if settings['voltage'] > 0 != polarity_negative:
                fail = True
                message = (f'{dev.ident}, conflict between set voltage ({polvol}) '
                           f'and rear panel polarity switch ({poltxt})')

        elif settings['forwardbias'] == polarity_negative:
            # forwardbias is a setting from iv.py
            fail = True
            message = (f'{dev.ident}, forward bias setting ({settings["forwardbias"]}) '
                       f'conflicts with rear panel channel polarity switch ({poltxt})')

        if fail:
            log_with_colour(logging.WARNING, message)

    return fail


def set_psu_voltage(settings, pipeline, voltage, ser, dev):
    """
    Set voltage on PSU.

    For the Keithley 2410's 1kV range, voltages can only be specified to two
    decimal places, though setting digits in the second decimal place is
    unreliable (read back values do not always match) so values should be
    limited to one decimal place.

    The ISEG SHQ ramps voltage to the desired value instead of setting it
    instantaneously, therefore poll status to check it has reached the
    desired.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        voltage : int
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    target_voltage = voltage
    if dev.manufacturer == 'iseg':
        # ISEG sets output channel polarity with hardware screws on the
        # rear panel, all voltages issued to the PSU have to be positive.
        voltage = abs(voltage)

    # constrain the voltage to be set to the given number of decimal places
    voltage = decimal_quantize(voltage, settings['decimal_places'])

    # set voltage
    command_string = lexicon.power(dev.model, 'set voltage', voltage, channel=dev.channel)
    if dev.manufacturer in {'agilent', 'keithley', 'hameg'}:
        send_command(pipeline, ser, dev, command_string)
    elif dev.manufacturer == 'iseg':
        atomic_send_command_read_response(pipeline, ser, dev, command_string)
        wait_for_voltage_to_stabilise(ser, pipeline, dev, target_voltage)

    if dev.manufacturer == 'agilent':
        command_string = lexicon.power(dev.model, 'clear event registers', channel=dev.channel)
        atomic_send_command_read_response(pipeline, ser, dev, command_string)


def set_psu_voltage_and_read(settings, pipeline, voltage, ser, dev, settling_time=2):
    """
    Set voltage on PSU then read back the measured voltage and current.

    For the Keithley 2410's 1kV range, voltages can only be specified to two
    decimal places, though setting digits in the second decimal place is
    unreliable (read back values do not always match) so values should be
    limited to one decimal place.

    The ISEG SHQ ramps voltage to the desired value instead of setting it
    instantaneously, therefore poll status to check it has reached the
    desired.

    --------------------------------------------------------------------------
    args
        settings : dictionary
            contains core information about the test environment
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        voltage : int
        ser : serial.Serial
            reference for serial port
        dev : instance of class Channel
            contains details of a device and its serial port
        settling_time : int
            seconds
    --------------------------------------------------------------------------
    returns float, float
        measured_voltage, measured_current
    --------------------------------------------------------------------------
    """
    set_psu_voltage(settings, pipeline, voltage, ser, dev)

    time.sleep(settling_time)

    return read_psu_measured_vi(pipeline, ser, dev)


def synchronise_psu(ser, pipeline, dev):
    """
    Only executed for ISEG SHQ power supplies.

    "In order to assure synchronisation between the computer and the supply,
    <CR><LF> has to be sent as first command."

    RS-232 Interface Programmers Guide for SHQ Devices, p.3

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
    returns : none
    --------------------------------------------------------------------------
    """
    if dev.manufacturer == 'iseg':
        command_string = lexicon.power(dev.model, 'synchronise')
        atomic_send_command_read_response(pipeline, ser, dev, command_string)


def unique(settings, psus, channels):
    """
    Remove all power supply channels that do not match the command line
    options that specifically identify which power supply channel to set:

    --manufacturer
    --model
    --serial
    --channel
    --port

    Two measures are used to limit the amount of typing the user has to
    perform:

    (1) for --serial and --port: allow the user to enter
    partial information, e.g. where there are two power supplies:

    cache: keithley 2410 serial number 4343654 on /dev/cu.usbserial-AH06DY15
    cache: keithley 2614b serial number 4428182 on /dev/cu.usbserial-AH06DWHE

    using --serial 654 would be sufficient to identify the keithley 2410
    since 654 does not appear in the other serial number.

    (2) for --channel, allow the user to mix up alphabetic and numeric
    identifiers, so the following pairings are viewed as equivalent:

    '1' and 'a'
    '2' and 'b'

    --------------------------------------------------------------------------
    args
        settings : dict
            contains core information about the test environment
        psus : dict
            {port: ({port_config}, device_type, device_serial_number), ...}
            contents of the cache filtered by hvpsu and lvpsu categories
        channels : list
            contains instances of class Channel, one for each
            power supply channel
    --------------------------------------------------------------------------
    returns
        single : bool
            True if only a single channel is left, False otherwise
        psus : dict
            no explicit return, mutable type amended in place
        channels : list
            no explicit return, mutable type amended in place
    --------------------------------------------------------------------------
    """
    # user supplied command line values
    user = (settings['manufacturer'], settings['model'], settings['serial'],
            settings['port'], settings['channel'])

    # tests for manufacturer, model, serial_number and port
    def generic(cached_values, user_value):
        return user_value not in cached_values

    test = (generic, generic, generic, generic, _channel_mismatch)

    for channel in copy.deepcopy(channels):
        cache = (channel.manufacturer, channel.model, channel.serial_number,
                 channel.port, channel.channel)
        if any(t(c, u) for c, u, t in zip(cache, user, test) if u is not None):
            channels.remove(channel)

    single = len(channels) == 1
    if single:
        # discard surplus entries in psus data structure: only retain power
        # supplies with ports matching those remaining in channels
        channel_ports = {channel.port for channel in channels}
        for psu_port in set(psus):
            if psu_port not in channel_ports:
                del psus[psu_port]

    return single


def wait_for_voltage_to_stabilise(ser, pipeline, dev, target_voltage):
    """
    Because ISEG SHQ ramps up voltage instead of setting it instantaneously,
    need to poll status to check it has reached its destination.

    Note that even when the response to the command contains ON - indicating
    that the power supply deems that the voltage set has been reached - the
    front panel display and the measured voltage both indicate that there is
    still some additional settling time.

    The front panel display has less resolution available than the value read
    back over the serial port connection, and does show some rounding errors.

    FIXME - note that the ISEG SHQ often doesn't want to settle to the set
    voltage value, particularly in the -5 < n < 5 range. e.g. d1=1, then check
    with d1 '00010-10' to indicate the PSU has understood the command, then
    minutes later u1 still shows it has not converged '-00022-01'. It may be
    better to simply perform a ramp and sample at 1s intervals. The ISEG SHQ
    222M (2x 2kV / 6mA) seems to perform better in this regard than the ISEG
    SHQ 224M (2x 4kV / 3mA)

    --------------------------------------------------------------------------
    args
        ser : serial.Serial
            reference for serial port
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        dev : instance of class Channel
            contains details of a device and its serial port
        target_voltage : numeric
            FIXME the sign of this argument may not match the measured voltage
            as read back from the instrument - the caller should make sure it
            matches
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    assert dev.model == 'shq', 'function only callable for ISEG SHQ PSU'
    target_voltage = float(target_voltage)

    while True:
        command_string = lexicon.power(dev.model, 'check output', channel=dev.channel)
        local_buffer = atomic_send_command_read_response(pipeline, ser, dev, command_string)

        if '=ON' in local_buffer:
            break

        time.sleep(0.5)

    # the psu voltage may still need to stabilise
    for _ in itertools.repeat(None, 16):
        command_string = lexicon.power(dev.model, 'read voltage', channel=dev.channel)
        local_buffer = atomic_send_command_read_response(pipeline, ser, dev, command_string)
        measured_voltage = iseg_value_to_float(local_buffer)

        diff = abs(abs(target_voltage) - abs(measured_voltage))
        if diff <= 0.5 or diff < abs(target_voltage) * 0.04:
            break

        time.sleep(1)
    else:
        mev = f'{si_prefix(measured_voltage)}V'
        tav = f'{si_prefix(target_voltage)}V'
        message = (f'{dev.ident}, measured voltage {mev} '
                   f'did not converge to set voltage {tav}')
        log_with_colour(logging.WARNING, message)


##############################################################################
# logging
##############################################################################

def log_with_colour(level, message, quiet=False):
    """
    Write messages to the log file. This can be safely called from threads,
    but NOT from processes.

    "Thread Safety

    The logging module is intended to be thread-safe without any special work
    needing to be done by its clients. It achieves this though using threading
    locks; there is one lock to serialize access to the module’s shared data,
    and each handler also creates a lock to serialize access to its underlying
    I/O."

    https://docs.python.org/3/library/logging.html#thread-safety

    --------------------------------------------------------------------------
    args
        level : int
            logging level e.g. logging.DEBUG
        message : string
            message to be sent to the log file
        quiet : bool
            do not log
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    if quiet:
        return

    if level == logging.WARNING:
        message = (f'{ANSIColours.FG_BLACK}{ANSIColours.BG_YELLOW}'
                   f'{ANSIColours.BOLD}{message}{ANSIColours.ENDC}')
    elif level in {logging.ERROR, logging.CRITICAL}:
        message = (f'{ANSIColours.FG_WHITE}{ANSIColours.BG_RED}'
                   f'{ANSIColours.BOLD}{message}{ANSIColours.ENDC}')

    logging.log(level, message)
