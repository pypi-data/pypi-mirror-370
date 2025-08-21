"""
Data structures relating to building and using the experiment's test
environment, to support environmental data logging for the ATLAS inner
tracker(ITK) pixels multi-module cycling box.

This script is expected to run on a Raspberry Pi.
"""

import collections
import contextlib
import functools
import itertools
import logging
import math
import time

import qwiic_tca9548a

from mmcb import sensors
from mmcb.common import UNIT


class TestEnvironment:
    """
    Contains test setup hardware configuration information.

    Functions provided here read the configuration file, build the data
    structures to store it, check the configuration, probe the hardware
    to check if everything stated by the configuration file is present and
    operational, and finally to return readings from all attached sensors.
    """

    __slots__ = {
        '_sensors': (
            'A list containing class instances of all the sensors in the test setup.'
        ),
        '_multiplexer_instance': (
            'dict: instances of qwiic_tca9548a.QwiicTCA9548A() used to '
            'communicate with Qwiic multiplexers.'
        ),
        '_unique_mux_addresses': (
            'The set of unique multiplexer I2C addresses used by a number of '
            'reporting functions called by _check_for_configuration_issues().'
        ),
    }

    def __init__(self, configuration_file):
        """
        Read the test setup from a configuration file and build an internal
        representation of all devices found to exist.
        """

        ######################################################################
        # read and diagnose user configuration
        ######################################################################

        self._read_configuration_file(configuration_file)
        configuration_ok = self._check_for_configuration_issues()

        if configuration_ok:

            ##################################################################
            # initialise sensor hardware and basic functionality tests
            ##################################################################

            self._remove_missing_qwiic_multiplexers()

            # Sort sensors by multiplexer I2C address then mux channel order
            # to avoid having to enable and disable the mux channel every
            # time a sensor is read.
            self._sensors.sort()

            self._check_multiplexer_connected_sensors_present()
            self._check_directly_attached_sensors_present()

    def __str__(self):
        return '\n'.join(f'{s}' for s in self._sensors)

    ##########################################################################
    # file i/o
    ##########################################################################

    def _read_configuration_file(self, configuration_file):
        """
        Read in a configuration CSV file that describes the test setup.

        Each line of the CSV files defines a single sensor.

        The CSV fields are:

        (1) sensor_type - Mandatory field. See mapping variable below for
        details.(2) sensor_name - Mandatory field.(3) qmux_i2c

        The I2C address of the Qwiic multiplexer the sensor is attached to.
        Leave this field empty if the sensor is connected directly to the I2C
        bus.

        (4) qmux_chan

        The Qwiic multiplexer channel the sensor is attached to. Leave this
        field empty if the sensor is connected directly to the I2C bus.

        (5) i2c_addr

        The I2C address of the sensor.

        This field supports two configurations: (a) Each multiplexer channel
        may host a chain of sensors with I2C addresses unique to the
        multiplexer channel, or (b) a sensor directly connected to the I2C
        bus.

        If omitted, this value will be assumed to be the default I2C address
        of the sensor_type.

        (6) thermocouple_type

        Only applicable to thermocouples. Leave this field empty for other
        sensor types.

        (7) analogue_input

        Only applicable to sensor types read via an ADS1015 12-bit ADC and
        analogue multiplexer.

        Example configuration file:

        hyt221, hyt221_ch0_M1,  0x71, 0
        hyt221, hyt221_ch1_env, 0x71, 1
        hyt221, hyt221_ch2,     0x71, 2
        smc,    smc,            0x71, 4
        ntc,    ntc,            0x71, 5,,,2
        tc,     TCk1_env,       0x71, 6, 0x67, K
        tc,     TCk2_M1_vc,     0x71, 6, 0x66, K
        tc,     TCt1_M4_vc,     0x71, 6, 0x65, T
        tc,     TCk3_M2_vc,     0x71, 7, 0x66, K
        tc,     TCk3_M3_vc,     0x71, 7, 0x65, K

        ----------------------------------------------------------------------
        args
            configuration_file : string
                file that exists
        ----------------------------------------------------------------------
        returns
            sensors : list of class instances
            e.g.
                [Hyt221(), Hyt221(), Hyt221(), SmcZse30A01F(), AtlasNtc(),
                 Mcp9601(), Mcp9601(), Mcp9601(), Mcp9601(), Mcp9601()]
        ----------------------------------------------------------------------
        """
        # sensor_type to class mapping
        mapping = {
            'bme680': sensors.Bme680,
            'hyt221': sensors.Hyt221,
            'nau7802': sensors.Nau7802,
            'ntc': sensors.AtlasNtc,
            'sht4x': sensors.Sht4x,
            'shtc3': sensors.Shtc3,
            'smcpfm': sensors.SmcPfm725SF01F,
            'smczse': sensors.SmcZse30A01F,
            'smczse12': sensors.SmcZse30A01F12,
            'tc': sensors.Mcp9601,
        }

        # used for a crude validity check for CSV line length
        lower_bound, upper_bound = 2, 7

        self._sensors = []

        with open(configuration_file, "r", encoding="utf-8") as csvfile:
            for row in csvfile:
                no_comment = row.split("#")[0]

                row = [field.strip() for field in no_comment.split(",")]
                rowlen = len(row)

                if lower_bound <= rowlen <= upper_bound:
                    # (1) pad the list with None values to ensure successful unpacking
                    # (2) convert empty strings to None
                    parts = (
                        x if x else None
                        for x, _ in itertools.zip_longest(
                            row, itertools.repeat(None, upper_bound)
                        )
                    )

                    sensor_type = next(parts)
                    if sensor_type == 'smczse':
                        print(
                            f'sensor_type={sensor_type} is deprecated '
                            '(reads with PCF8591 8-bit ADC)\n'
                            'Use smczse12 instead (reads with Ads1015 12-bit ADC)'
                        )

                    try:
                        self._sensors.append(mapping[sensor_type](*parts))
                    except KeyError:
                        print(f"unknown sensor type: {sensor_type}")

    ##########################################################################
    # report issues in user-supplied configuration
    ##########################################################################

    def _report_duplicate_sensor_names(self):
        """
        Report any duplicate sensor names. These should be unique to avoid
        data being overwritten.
        """
        retval = True

        sensor_names = (sensor.name for sensor in self._sensors)
        counts = collections.Counter(sensor_names)
        duplicates = [k for k, v in counts.items() if v > 1]
        if duplicates:
            retval = False
            print(f'duplicate sensor names: {", ".join(duplicates)}')

        return retval

    def _report_mux_i2c_not_in_range(self):
        """
        Report any Qwiic multiplexer I2C address outside the allowable range.

        https://learn.sparkfun.com/tutorials/qwiic-mux-hookup-guide
        """
        retval = True

        mux_address_range = range(0x70, 0x77 + 1)
        bad_mux_addresses = {
            a for a in self._unique_mux_addresses if a not in mux_address_range
        }

        if bad_mux_addresses:
            retval = False
            print(
                'Qwiic multiplexer I2C addresses must be in range '
                f'{hex(min(mux_address_range))}-{hex(max(mux_address_range))}, '
                f'found: {", ".join(hex(x) for x in bad_mux_addresses)}'
            )

        return retval

    def _report_mux_channel_not_in_range(self):
        """
        Report and Qwiic multiplexer channels outside the allowable range.
        """
        retval = True

        channel_range = range(8)

        sensors_attached_to_multiplexers = {
            sensor
            for sensor in self._sensors
            if sensor.multiplexer_i2c_address in self._unique_mux_addresses
        }

        for sensor in sensors_attached_to_multiplexers:
            try:
                bad = sensor.multiplexer_channel not in channel_range
            except TypeError:
                retval = False
                print(
                    f'{sensor.description}, {sensor.name} bad mux channel: '
                    f'{sensor.multiplexer_channel}'
                )
            else:
                if bad:
                    retval = False
                    print(
                        f'{sensor.description}, {sensor.name} bad mux channel: '
                        f'{sensor.multiplexer_channel}'
                    )

        return retval

    def _report_mux_missing_address_or_channel(self):
        """Report if the user did not supply both required parameters."""
        retval = True

        for sensor in self._sensors:
            pair = (sensor.multiplexer_i2c_address, sensor.multiplexer_channel)
            if len([x for x in pair if x is None]) == 1:
                retval = False
                print(
                    f'{sensor.description}: '
                    'mux address and channel are both required'
                )

        return retval

    def _report_mux_conflicting_i2c_addresses_within_channels(self):
        """
        Report I2C address conflicts within multiplexer channels.

        Note that sensors on a mux channel with identical i2c addresses
        are not regarded as duplicates if their analogue input channels are
        different.
        """
        retval = True

        for mux_address in self._unique_mux_addresses:
            sensors_on_this_mux = [
                sensor
                for sensor in self._sensors
                if sensor.multiplexer_i2c_address == mux_address
            ]
            unique_channels_on_this_mux = {
                sensor.multiplexer_channel for sensor in sensors_on_this_mux
            }

            for mux_channel in unique_channels_on_this_mux:
                sensors_on_this_mux_channel = (
                    sensor
                    for sensor in sensors_on_this_mux
                    if sensor.multiplexer_channel == mux_channel
                )

                # worst case (1 mux, fully populated channel):
                #     math.comb(255, 2) (n=32385)
                # typical: less than 8 devices per mux channel (n=28)
                duplicates = {
                    sensor1.sensor_i2c_address
                    for sensor1, sensor2 in itertools.combinations(
                        sensors_on_this_mux_channel, 2
                    )
                    if sensor1 == sensor2
                }

                if duplicates:
                    retval = False
                    print(
                        f'conflicting I2C addresses found on mux {hex(mux_address)} '
                        f'channel {mux_channel}: {", ".join(hex(x) for x in duplicates)}'
                    )
        return retval

    def _report_mux_conflict_with_directly_connected_sensors(self):
        """
        Report any i2c address clashes between multiplexers and directly
        connected sensors.
        """
        retval = True

        directly_attached_sensors = {
            sensor.sensor_i2c_address
            for sensor in self._sensors
            if sensor.multiplexer_i2c_address is None
        }

        duplicates = directly_attached_sensors.intersection(self._unique_mux_addresses)

        if duplicates:
            retval = False
            print(
                'conflicting i2c addresses found between mux '
                'and directly attached sensors: '
                f'{", ".join(hex(x) for x in duplicates)}'
            )

        return retval

    def _report_i2c_bus_directly_connected_conflicting_addresses(self):
        """
        Report identical i2c addresses on sensors directly connected to the
        i2c bus. This check is for sensors ONLY. Address clashes between
        multiplexers and sensors are detected in
        _report_mux_conflict_with_directly_connected_sensors.
        """
        retval = True

        # no need to check both multiplexer_i2c_address and multiplexer_channel
        directly_connected = (
            sensor
            for sensor in self._sensors
            if sensor.multiplexer_i2c_address is None
        )
        duplicates = [
            sensor1
            for sensor1, sensor2 in itertools.combinations(directly_connected, 2)
            if sensor1 == sensor2
        ]

        if duplicates:
            retval = False
            print(
                'conflicting i2c addresses found on directly attached sensors: '
                f'{", ".join(hex(x.sensor_i2c_address) for x in duplicates)}'
            )

        return retval

    def _report_conflicting_i2c_addresses_between_channels_and_directly_connected(self):
        """
        Report conflicting i2c addresses between sensors directly attached to
        the I2C bus and those attached via a multiplexer. The latter will
        conflict when the multiplexer/channel is selected.
        """
        retval = True

        i2c_addresses_via_mux = set()

        for mux_address in self._unique_mux_addresses:
            sensors_on_this_mux = [
                sensor
                for sensor in self._sensors
                if sensor.multiplexer_i2c_address == mux_address
            ]
            unique_channels_on_this_mux = {
                sensor.multiplexer_channel for sensor in sensors_on_this_mux
            }

            for mux_channel in unique_channels_on_this_mux:
                i2c_addresses_on_this_mux_channel = [
                    sensor.sensor_i2c_address
                    for sensor in sensors_on_this_mux
                    if sensor.multiplexer_channel == mux_channel
                ]

                i2c_addresses_via_mux.update(i2c_addresses_on_this_mux_channel)

        i2c_addresses_of_directly_attached = {
            sensor.sensor_i2c_address
            for sensor in self._sensors
            if sensor.multiplexer_i2c_address is None
        }

        duplicates = i2c_addresses_via_mux.intersection(
            i2c_addresses_of_directly_attached
        )

        if duplicates:
            retval = False
            print(
                'I2C address conflict between directly attached and '
                f'multiplexer channel attached sensors: {", ".join(hex(x) for x in duplicates)}'
            )

        return retval

    def _report_analogue_mux_channels_out_of_range(self):
        """
        Report analogue multiplexer channels out of range, and that the sensor
        needs to have an analogue channel specified.
        """

        retval = True
        sensors_with_multiple_inputs = [sensors.Ads1015, sensors.Pcf8591]

        for sensor in self._sensors:
            check = functools.partial(isinstance, sensor)
            if any(map(check, sensors_with_multiple_inputs)):
                if sensor.analogue_input not in sensor.supported_analogue_inputs:
                    retval = False
                    inputs = ', '.join(
                        map(str, sensor.supported_analogue_inputs)
                    )
                    print(
                        f'{sensor.description}: analogue input not in '
                        f'{inputs}: {sensor.analogue_input}'
                    )

        return retval

    def _report_sensor_i2c_addresses_out_of_range(self):
        """Report sensor I2C addresses out of range."""

        retval = True

        for sensor in self._sensors:
            # Suppress TypeError since the I2C address may be None at this
            # point. If so, it will be changed to the default I2C address later.
            with contextlib.suppress(TypeError):
                if not sensor.i2c_min <= sensor.sensor_i2c_address <= sensor.i2c_max:
                    retval = False
                    print(
                        f'{sensor.description}, I2C address out of range '
                        f'{hex(sensor.i2c_min)}-{hex(sensor.i2c_max)}: '
                        f'{hex(sensor.sensor_i2c_address)}'
                    )

        return retval

    def _report_sensor_unsupported_thermocouple_type(self):
        """Report missing or unsupported thermocouple type."""

        retval = True

        for sensor in self._sensors:
            if isinstance(sensor, sensors.Mcp9601):
                if sensor.thermocouple_type not in sensor.supported_thermocouple_types:
                    retval = False
                    print(
                        f'{sensor.description} {sensor.name} '
                        f'unrecognised thermocouple type: {sensor.thermocouple_type}'
                    )

        return retval

    def _check_for_configuration_issues(self):
        """
        Make reasonable efforts to identify problems with user-supplied data
        before any attempt is made to communicate with the test setup
        hardware.

        Report findings to the user and terminate if there are any issues,
        since they cannot be fixed without user intervention.

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns
            self._unique_mux_addresses
                no explicit return
        ----------------------------------------------------------------------
        """
        # this will be used in a number of the report functions called below
        self._unique_mux_addresses = {
            sensor.multiplexer_i2c_address
            for sensor in self._sensors
            if sensor.multiplexer_i2c_address is not None
        }

        reports = (
            self._report_duplicate_sensor_names,
            self._report_mux_i2c_not_in_range,
            self._report_mux_channel_not_in_range,
            self._report_mux_missing_address_or_channel,
            self._report_mux_conflicting_i2c_addresses_within_channels,
            self._report_mux_conflict_with_directly_connected_sensors,
            self._report_i2c_bus_directly_connected_conflicting_addresses,
            self._report_conflicting_i2c_addresses_between_channels_and_directly_connected,
            self._report_analogue_mux_channels_out_of_range,
            self._report_sensor_i2c_addresses_out_of_range,
            self._report_sensor_unsupported_thermocouple_type,
        )
        results = [report() for report in reports]
        configuration_ok = all(results)
        if not configuration_ok:
            self._sensors.clear()
            print(
                'Please rectify issue(s) with the configuration file and/or test setup.'
            )

        return configuration_ok

    ##########################################################################
    # remove configured hardware that cannot be found
    ##########################################################################

    def _remove_missing_qwiic_multiplexers(self):
        """Remove sensors attached to missing Qwiic multiplexers."""
        self._multiplexer_instance = {}

        for mux_address in self._unique_mux_addresses.copy():

            # The constructor for .QwiicTCA9548A() doesn't check the device
            # exists, therefore doesn't raise an exception or display an error
            i2c_mux = qwiic_tca9548a.QwiicTCA9548A(mux_address)

            # .is_connected() prints an error if the mux cannot be found:
            # "Error connecting to Device: 71, [Errno 121] Remote I/O error".
            # It doesn't raise an exception, but does correctly return False.
            if i2c_mux.is_connected():
                self._multiplexer_instance[mux_address] = i2c_mux
            else:
                print(f'qwiic mux not found at I2C address {hex(mux_address)}')
                self._unique_mux_addresses.remove(mux_address)

                for sensor in self._sensors.copy():
                    if sensor.multiplexer_i2c_address == mux_address:
                        self._sensors.remove(sensor)
                        print(f'removing sensor {sensor.name}')

    def _check_multiplexer_connected_sensors_present(self):
        """
        Check if multiplexer-attached devices are responsive.

        ASSUME that sensors have been sorted by mux i2c address then by
        mux channel number. This allows the list of sensors to be traversed
        minimising the number of changes of mux/channel configuration.

        The initial instances required to access the sensors are created
        during the traversal.
        """

        sensors_attached_to_multiplexers = [
            s for s in self._sensors if s.multiplexer_i2c_address
        ]

        address = self._sequence_change(
            s.multiplexer_i2c_address for s in sensors_attached_to_multiplexers
        )
        channel = self._sequence_change(
            s.multiplexer_channel for s in sensors_attached_to_multiplexers
        )

        i2c_mux = None
        for sensor in sensors_attached_to_multiplexers:

            mux_change, _ = next(address)
            chan_change, mux_chan_previous = next(channel)

            if mux_change:
                i2c_mux = self._multiplexer_instance[sensor.multiplexer_i2c_address]
                i2c_mux.disable_all()

            if chan_change:
                if mux_chan_previous is not None and not mux_change:
                    i2c_mux.disable_channels(mux_chan_previous)

                i2c_mux.enable_channels(sensor.multiplexer_channel)
                time.sleep(0.05)

            sensor.activate()
            if sensor.missing():
                self._sensors.remove(sensor)

        # ensure all channels are off on exit
        if i2c_mux is not None:
            i2c_mux.disable_all()

    def _check_directly_attached_sensors_present(self):
        """
        Check if directly attached sensors are responsive.

        The initial instances required to access the sensors are created
        during the traversal.
        """
        directly_attached_sensors = (
            s for s in self._sensors if not s.multiplexer_i2c_address
        )

        for sensor in directly_attached_sensors:
            sensor.activate()

            if sensor.missing():
                self._sensors.remove(sensor)

    ##########################################################################
    # read sensors
    ##########################################################################

    def read_all_sensors(self):
        """
        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns
            data_for_current_timestamp: dict
            e.g. {
                'timestamp': 1650734619.065016,
                'smc_vacuum': -0.3395540799999992,
                'ntc_temperature': -61.19908797184263,
                'hyt221_ch0_M1_temperature': 20.26735030214246,
                'hyt221_ch0_M1_relative_humidity': 0.0,
                'hyt221_ch1_env_temperature': 20.54934993590917,
                'hyt221_ch1_env_relative_humidity': 0.09766221082829762,
                'hyt221_ch2_temperature': 20.579564182384175,
                'hyt221_ch2_relative_humidity': 0.0,
                'TCk1_env_temperature': 20.125,
                'TCk2_M1_vc_temperature': 20.1875,
                'TCt1_M4_vc_temperature': 21.0625,
                'TCk3_M2_vc_temperature': 22.0,
                'TCk3_M3_vc_temperature': 21.875
            }
        ----------------------------------------------------------------------
        """
        data_for_current_timestamp = {'timestamp': time.monotonic()}

        sensors_attached_to_multiplexers = [
            s for s in self._sensors if s.multiplexer_i2c_address
        ]

        address = self._sequence_change(
            s.multiplexer_i2c_address for s in sensors_attached_to_multiplexers
        )
        channel = self._sequence_change(
            s.multiplexer_channel for s in sensors_attached_to_multiplexers
        )

        i2c_mux = None
        for sensor in sensors_attached_to_multiplexers:

            mux_change, _ = next(address)
            chan_change, mux_chan_previous = next(channel)

            if mux_change:
                with contextlib.suppress(AttributeError):
                    i2c_mux.disable_all()
                i2c_mux = self._multiplexer_instance[sensor.multiplexer_i2c_address]
                i2c_mux.disable_all()

            if chan_change:
                if mux_chan_previous is not None and not mux_change:
                    i2c_mux.disable_channels(mux_chan_previous)

                i2c_mux.enable_channels(sensor.multiplexer_channel)

            if not sensor.missing():
                try:
                    value = sensor.read()
                except (OSError, TypeError):
                    logging.debug('%s could not be read', sensor.name)
                else:
                    if value is None:
                        logging.debug('%s could not be read', sensor.name)
                    else:
                        data_for_current_timestamp.update(value)

        # ensure all channels are off on exit
        if i2c_mux is not None:
            i2c_mux.disable_all()

        # read directly connected sensors

        directly_attached_sensors = (
            s for s in self._sensors if not s.multiplexer_i2c_address
        )
        for sensor in directly_attached_sensors:
            time.sleep(0.05)
            try:
                data_for_current_timestamp.update(sensor.read())
            except (OSError, TypeError):
                logging.debug('%s could not be read', sensor.name)

        if len(data_for_current_timestamp) == 1:
            data_for_current_timestamp.clear()

        return data_for_current_timestamp

    ##########################################################################
    # support functions
    ##########################################################################

    @staticmethod
    def _sequence_change(number_sequence):
        """
        Used for flagging changes in the incoming number series.

        ASSUMING the number sequence is sorted, this may be used - for example -
        to indicate when channel numbers change. At which point a command can be
        issued to make the change on the hardware.

        e.g. given an incoming generator supplying these multiplexer channel
        numbers:

        (0, 1, 2, 2, 2, 3, 3)

        Changes would be indicated thus:

        ((True, ...), (True, ...), (True, ...), (False, ...), (False, ...),
        (True, ...), (False, ...))

        ----------------------------------------------------------------------
        args
            number_sequence : generator
        ----------------------------------------------------------------------
        yields : tuple (bool, int)
            (True, ...) if the current number in the sequence differed from
            its predecessor, (False, ...) otherwise.
        ----------------------------------------------------------------------
        """
        last = None

        for number in number_sequence:
            if number != last:
                yield True, last
                last = number
            else:
                yield False, last

    ##########################################################################
    # dew point
    ##########################################################################

    def calculate_dew_points(self, data_for_current_timestamp):
        """
        Calculate dew point data from a dictionary of sensor values.

        Dew points are only calculated for sensors that supply both relative
        humidity and temperature; there's no mixing of data from different
        sensors.

        Note that the internal _dew_point method which this method relies
        upon, returns values low values clamped to -71 degrees Celsius, which
        is the figure for the dry air supply in the cleanroom. This is to
        cope with some sensors reporting zero RH% in dry conditions due to
        limited resolution, which would in turn lead to dew point figures
        that would be impossible to realise in the test environment.

        ----------------------------------------------------------------------
        args
            data_for_current_timestamp : dict
                e.g.
                {'timestamp': 1651224444.4431129,
                 'hyt221_ch0_M1_temperature': 20.277421717634134,
                 'hyt221_ch0_M1_relative_humidity': 0.0,
                 'hyt221_ch1_env_temperature': 20.60977842885918,
                 'hyt221_ch1_env_relative_humidity': 0.0, ...}
        ----------------------------------------------------------------------
        returns
            dew_point_calculations: dict
                e.g.
                {'bme_ambient_calculated_dew_point': 7.317889854346651,
                 'hyt221_ch2_calculated_dew_point': -71,
                 'hyt221_ch1_env_calculated_dew_point': -71,
                 'hyt221_ch0_M1_calculated_dew_point': -71,
                 'sht_ambient_calculated_dew_point': 8.439206561314366}
        ----------------------------------------------------------------------
        """
        dew_point_calculations = {}

        rhu = f' {UNIT.relative_humidity}'
        tdc = f' {UNIT.temperature}'
        # find all keys containing relative humidity or temperature
        columns_of_interest = {
            c for c in data_for_current_timestamp if rhu in c or tdc in c
        }

        # find all sensors that collect both relative humidity and temperature
        sensor_rhp = {c.rsplit(rhu)[0] for c in columns_of_interest if rhu in c}
        sensor_dgc = {c.rsplit(tdc)[0] for c in columns_of_interest if tdc in c}
        sensor_dew = sensor_rhp.intersection(sensor_dgc)

        # create new columns with calculated dew points
        for sensor in sensor_dew:
            # find keys for relative humidity and temperature for this sensor
            source_columns = {x for x in columns_of_interest if sensor in x}

            try:
                column_humi = next(x for x in source_columns if rhu in x)
                column_temp = next(x for x in source_columns if tdc in x)
            except StopIteration:
                continue

            # make it clear this is not directly acquired data
            new_column_title = f'{sensor} {UNIT.calculated_dew_point}'

            # calculate dew point, add new key with this information
            temp = data_for_current_timestamp[column_temp]
            humi = data_for_current_timestamp[column_humi]
            dew_point_calculations[new_column_title] = self._dew_point(temp, humi)

        return dew_point_calculations

    @staticmethod
    def _dew_point(tdc, rhp, arden_buck=True):
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

        ----------------------------------------------------------------------
        args
            tdc : float
                temperature degrees Celsius
            rhp : float
                relative humidity percentage
            arden_buck : bool
                choice of algorithm
        ----------------------------------------------------------------------
        returns : float
            dew point degrees Celsius
        ----------------------------------------------------------------------
        """
        # constants
        # a = 6.1121 # mbar
        b = 18.678
        c = 257.14  # °C
        d = 234.5  # °C

        try:
            if arden_buck:
                # accurate
                ymtrh = math.log(
                    (rhp / 100) * math.exp((b - tdc / d) * (tdc / (c + tdc)))
                )
                tdp = (c * ymtrh) / (b - ymtrh)
            else:
                # approximation (Magnus formula)
                ytrh = math.log(rhp / 100) + (b * tdc) / (c + tdc)
                tdp = (c * ytrh) / (b - ytrh)
        except ValueError:
            # clamp the dew point values to -71 which is the figure for the dry air
            # supply in the cleanroom. This is to cope with some sensors reporting
            # zero RH% in dry conditions due to limited resolution.
            tdp = -71.0

        # Sensors returning RH% values very close to zero due to limited
        # resolution can be problematic. So again as above, clamp the dew point
        # values to -71 deg C.
        return max(tdp, -71.0)
