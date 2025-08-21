"""
Data structures related to sensors, to support environmental data logging for
the ATLAS inner tracker (ITK) pixels multi-module cycling box.

This script is expected to run on a Raspberry Pi.

The following sensors (I2C unless otherwise stated) are supported, and
connected together with the Qwiic system and the TCA9548A-based multiplexer:

    BME680
    HYT221
    Atlas NTC         via ADS1015 12-bit ADC
    SMC ZSE30A-01-F   via PCF8591  8-bit ADC
    SMC PFM725S-F01-F via ADS1015 12-bit ADC
    SHT40/41/45
    SHTC3 for connectivity testing only

Qwiic multiplexer documentation can be found here:

https://qwiic-tca9548a-py.readthedocs.io/en/latest/
https://www.sparkfun.com/qwiic

Qwiic wiring - looking into the front of connector, with the connector pins
visible:

wire_col    pin    function    comments
black       1      GND         connector left
red         2      3V3 VCC
blue        3      SDA
yellow      4      SCL         connector right

Install dependencies after building Python 3.10 from source:

python3.10 -m pip install setuptools wheel numpy pandas matplotlib zmq serial
python3.10 -m pip install sparkfun-qwiic-tca9548a
python3.10 -m pip install Adafruit-Blinka
python3.10 -m pip install adafruit-circuitpython-bme680
python3.10 -m pip install adafruit-circuitpython-shtc3
python3.10 -m pip install adafruit-circuitpython-pcf8591
python3.10 -m pip install adafruit-circuitpython-ads1x15
python3.10 -m pip install smbus

Manually install:

git clone https://github.com/pimoroni/mcp9600-python
cd mcp9600-python
in file library/mcp9600/__init__.py make these changes:

From:

CHIP_ID = 0x40
I2C_ADDRESSES = list(range(0x60, 0x68))
I2C_ADDRESS_DEFAULT = 0x66
I2C_ADDRESS_ALTERNATE = 0x67

To:

CHIP_ID = 0x41
I2C_ADDRESSES = list(range(0x65, 0x67))
I2C_ADDRESS_DEFAULT = 0x67
I2C_ADDRESS_ALTERNATE = 0x67

Also edit the PYTHON="..." line in install.sh to point to the correct Python
version, if it's not python3.

sudo ./install.sh --unstable
"""

import contextlib
from dataclasses import dataclass
import itertools
import logging
import math
import statistics
import sys
import time

import board
import busio
import adafruit_bme680
import adafruit_sht4x
import adafruit_shtc3
import adafruit_pcf8591.pcf8591 as PCF
from adafruit_pcf8591.analog_in import AnalogIn as pcf_in
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn as ads_in
import smbus
import mcp9600
from cedargrove_nau7802 import NAU7802

from mmcb.common import UNIT

try:
    I2C_BOARD = board.I2C()
except ValueError:
    sys.exit('board: I2C initialisation failed')

I2C_SMBUS = smbus.SMBus(1)
I2C_BUSIO = busio.I2C(board.SCL, board.SDA)


@dataclass
class Sensor:
    """
    Container for data from a single sensor obtained from the user-supplied
    configuration file.
    """

    __slots__ = {
        'name': 'Short name string used to identify the sensor in log files.',
        'multiplexer_i2c_address': 'I2C address of the multiplexer the sensor is attached to.',
        'multiplexer_channel': 'Channel number of the multiplexer the sensor is attached to.',
        'sensor_i2c_address': 'I2C address of the sensor.',
        'thermocouple_type': 'If applicable to the sensor type, a single string character.',
        'analogue_input': 'If applicable to the sensor type, analogue multiplexer input channel.',
    }

    def __init__(
        self,
        name,
        qmux_i2c,
        qmux_chan,
        i2c_addr,
        thermocouple_type,
        analogue_input,
    ):
        """
        Receives arguments taken from a single line read from the
        configuration file.
        """
        self.name = name

        # user may use either case for thermocouple types
        try:
            self.thermocouple_type = thermocouple_type.upper()
        except AttributeError:
            self.thermocouple_type = thermocouple_type

        try:
            self.multiplexer_i2c_address = int(qmux_i2c, 0)
        except (TypeError, ValueError):
            self.multiplexer_i2c_address = None

        try:
            self.multiplexer_channel = int(qmux_chan)
        except (TypeError, ValueError):
            self.multiplexer_channel = None

        try:
            self.sensor_i2c_address = int(i2c_addr, 0)
        except (TypeError, ValueError):
            self.sensor_i2c_address = None

        try:
            self.analogue_input = int(analogue_input)
        except (TypeError, ValueError):
            self.analogue_input = None

    # Sufficient to allow a list of class instances to be sorted such that
    # device selection changes of state are minimised when iterating.
    # E.g. group sensors by multiplexer, then by multiplexer channel, and
    # finally by sensor i2c address.
    def __lt__(self, value):

        # [(s1, v1), (s2, v2), (s3, v3)]
        comparisons = [
            (self.multiplexer_i2c_address, value.multiplexer_i2c_address),
            (self.multiplexer_channel, value.multiplexer_channel),
            (self.sensor_i2c_address, value.sensor_i2c_address),
        ]

        # Replace every None value with a numeric that is neither a valid i2c
        # address nor a valid multiplexer channel number. None values are
        # seen for sensors directly connected to the I2C bus for
        # multiplexer_i2c_address and multiplexer_channel. This change
        # ensures that the "<" comparison isn't broken by non-numeric values,
        # and that sensors directly connected to the I2C bus are not mixed in
        # with those attached via multiplexers.

        def fix(pair):
            return (256 if c is None else c for c in pair)

        # (s1, s2, s3), (v1, v2, v3)
        sel, val = zip(*map(fix, comparisons))

        return sel < val

    # Equality based on analogue input is provided to allow the coexistence
    # of more than one sensor (e.g. multi-analogue-input devices such as the
    # ADS1015) with matching locations in the config file, e.g.
    #
    # smcpfm, flow1, 0x72, 0,,,2
    # smcpfm, flow2, 0x72, 0,,,3
    #
    # or
    #
    # smcpfm, flow1,,,,,2
    # smcpfm, flow2,,,,,3
    #
    # Normally, two or more entries with (1) matching mux/channel entries or
    # (2) directly connected to the i2c bus refer to different hardware, and
    # would be rejected to avoid a hardware conflict. In this context,
    # multiple entries refer to different analogue inputs on the same
    # hardware, and no hardware conflict exists.
    def __eq__(self, value):
        return (
            self.multiplexer_i2c_address,
            self.multiplexer_channel,
            self.sensor_i2c_address,
            self.analogue_input,
        ) == (
            value.multiplexer_i2c_address,
            value.multiplexer_channel,
            value.sensor_i2c_address,
            value.analogue_input,
        )

    def __str__(self):
        try:
            multiplexer_i2c_address_text = hex(self.multiplexer_i2c_address)
        except TypeError:
            multiplexer_i2c_address_text = f'{self.multiplexer_i2c_address}'

        try:
            i2c_address_text = hex(self.sensor_i2c_address)
        except TypeError:
            i2c_address_text = f'{self.sensor_i2c_address}'

        items = [
            self.name,
            multiplexer_i2c_address_text,
            self.multiplexer_channel,
            i2c_address_text,
            self.thermocouple_type,
            self.analogue_input,
        ]

        return ', '.join(f'{x}' for x in items)

    # sufficient to allow the use of isinstance()
    def __hash__(self):
        return hash(
            (
                self.multiplexer_i2c_address,
                self.multiplexer_channel,
                self.sensor_i2c_address,
            )
        )

    def default_i2c_address_if_unset(self, i2c_def_addr):
        """
        If the user did not specify the sensor I2C address in the
        configuration file, it will be entered as None. In that case use the
        default I2C address for the sensor.
        """
        if self.sensor_i2c_address is None:
            self.sensor_i2c_address = i2c_def_addr


##############################################################################
# sensors - data acquisition hardware
#
# Note that __init__() in the following classes initialises based on the
# (sanity-checked) information the user provided in the config file. The
# activate() member function subsequently probes/configures the hardware
# itself.
##############################################################################


class Ads1015(Sensor):
    """
    SparkFun Qwiic 12-bit ADC and analogue multiplexer (ADS1015)

    https://www.sparkfun.com/products/15334

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.
    """

    description = 'SparkFun Qwiic 12-bit ADC and analogue multiplexer (ADS1015)'
    i2c_min = i2c_default = 0x48
    i2c_max = 0x4B
    # when checked, ADS.P0 was 0, ADS.P1 was 1, etc... so this LUT is probably
    # unnecessary
    supported_analogue_inputs = {0: ADS.P0, 1: ADS.P1, 2: ADS.P2, 3: ADS.P3}

    def __init__(self, *args):
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.

        This function will FAIL SILENTLY if the device is not reachable.
        """
        with contextlib.suppress(OSError, ValueError):
            ads1015 = ADS.ADS1015(I2C_BOARD)
            ads1015.mode = ADS.Mode.SINGLE
            self._instance = ads_in(
                ads1015, self.supported_analogue_inputs[self.analogue_input]
            )

    def missing(self):
        """Check if the hardware is present and operational."""
        return self._instance is None

    def read(self):
        """Read voltage from ADC."""
        try:
            voltage = self._instance.voltage
        except (OSError, AttributeError):
            voltage = None

        return voltage


class Bme680(Sensor):
    """
    Gas sensor measuring relative humidity, barometric pressure, ambient
    temperature and gas (VOC) [1].

    I2C address: single link on rear of board, 0x76 if link shorted,
    0x77 if left open circuit [2].

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.

    [1] https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme680/
    [2] https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/
        arduino-wiring-test#i2c-wiring-2957118-2
    """

    description = 'Adafruit BME680 Temperature, Humidity, Pressure and Gas Sensor'
    i2c_min = 0x76
    i2c_max = i2c_default = 0x77

    def __init__(self, *args):
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """Creates an instance that will be used for future sensor access."""
        with contextlib.suppress(OSError, RuntimeError, ValueError):
            self._instance = adafruit_bme680.Adafruit_BME680_I2C(I2C_BOARD)

    def missing(self):
        """Check if the hardware is present and operational."""
        return self._instance is None

    def read(self):
        """
        Read data from sensor.

        Each call to 'temperature' 'relative_humidity' and 'pressure' initiate a
        read of all parameters from the sensor. However, because these three
        sequential calls occur within 0.1s (the default refresh rate is 10Hz), the
        initial call to 'temperature' fetches the data from the sensor, and the
        subsequent two calls to 'relative_humidity' and 'pressure' simply use the
        data fetched by the 'temperature' call.

        Note that there's the potential for an infinite loop in the Adafruit API:
        class Adafruit_BME680, method _perform_reading().

        while not new_data:
            data = self._read(_BME680_REG_MEAS_STATUS, 17)
            new_data = data[0] & 0x80 != 0
            time.sleep(0.005)

        https://github.com/adafruit/Adafruit_CircuitPython_BME680/blob/main/
                adafruit_bme680.py

        --------------------------------------------------------------------------
        args : none
        --------------------------------------------------------------------------
        returns : dict
            temperature (degrees Celsius), relative humidity (%), pressure (hPa)
            e.g. {'bme_ambient_temperature': 21.4923046875,
                  'bme_ambient_relative_humidity': 41.58673354909264,
                  'bme_ambient_pressure': 1029.1443145220119} or None
        --------------------------------------------------------------------------
        """
        retval = temp_dc = rhum_pc = pres_hpa = None

        with contextlib.suppress(UnboundLocalError, OSError):
            temp_dc = self._instance.temperature

        with contextlib.suppress(UnboundLocalError, OSError):
            rhum_pc = float(self._instance.relative_humidity)

        with contextlib.suppress(UnboundLocalError, OSError):
            pres_hpa = self._instance.pressure

        if all(x is not None for x in (temp_dc, rhum_pc, pres_hpa)):
            retval = {
                f'{self.name} {UNIT.temperature}': temp_dc,
                f'{self.name} {UNIT.relative_humidity}': rhum_pc,
                f'{self.name} {UNIT.pressure}': pres_hpa,
            }

        return retval


class Hyt221(Sensor):
    """
    Innovative Sensor Technology (IST) HYT-221 sensor.

    API courtesy of https://github.com/joppiesaus/python-hyt/

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.

    https://www.ist-ag.com/sites/default/files/downloads/hyt221.pdf
    """

    description = (
        'Innovative Sensor Technology HYT 221 Digital Humidity and Temperature Module'
    )
    i2c_min = i2c_max = i2c_default = 0x28

    def __init__(self, *args):
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)

    @staticmethod
    def activate():
        """No activation process is required for this sensor."""
        return

    def missing(self):
        """Check if the hardware is present and operational."""
        return self.read() is None

    def read(self):
        """
        Read data from sensor.

        --------------------------------------------------------------------------
        args : none
        --------------------------------------------------------------------------
        returns : dict
            temperature in degrees Celsius, relative humidity (%)
            e.g. {'hyt221_ch1_env_temperature': 20.54934993590917,
                  'hyt221_ch1_env_relative_humidity': 0.09766221082829762} or None
        --------------------------------------------------------------------------
        """
        retval = None

        delay = 0.05
        time.sleep(delay)

        # wake up the device
        try:
            I2C_SMBUS.write_byte(self.sensor_i2c_address, 0x00)
        except OSError:
            return retval

        time.sleep(delay)

        # read four bytes
        try:
            reading = I2C_SMBUS.read_i2c_block_data(self.sensor_i2c_address, 0x00, 4)
        except OSError:
            pass
        else:
            rhum_pc = ((reading[0] & 0x3F) * 0x100 + reading[1]) * (100.0 / 16383.0)
            temp_dc = (
                165.0 / 16383.0 * ((reading[2] * 0x100 + (reading[3] & 0xFC)) >> 2) - 40
            )
            retval = {
                f'{self.name} {UNIT.temperature}': temp_dc,
                f'{self.name} {UNIT.relative_humidity}': rhum_pc,
            }

        return retval


class Mcp9601(Sensor):
    """
    MCP9601 thermocouple amplifier

    Read the thermocouple temperature from the Adafruit MCP9601 using the
    Pimoroni MCP9600 API. Do not use the Adafruit API.

    ---

    From https://learn.adafruit.com/adafruit-mcp9601:

    "We use the MCP96L01 in this breakout which has ±2.0°C/±4.0°C (typ./max.)
    thermocouple accuracy (which is not including the innate inaccuracy of
    thermocouples, K thermocouples have about ±2°C to ±6°C accuracy)"

    "[ADC] resolution of ±0.0625 °C"

    From https://learn.adafruit.com/adafruit-mcp9601/python-circuitpython:

    "The MCP9601 does not like zero-length writes directed to it, and will
    often not respond (it will NAK instead of ACK). This means it will often
    not respond to probes by `i2c.scan()` and similar scans of the I2C bus."

    ---

    Since the API is for the MCP9600 rather than the MCP9601, need to make a
    small change before installation:

    git clone https://github.com/pimoroni/mcp9600-python
    cd mcp9600-python
    in file library/mcp9600/__init__.py change:
        the chip id to 0x41
        the default i2c address to 0x67
    sudo ./install.sh --unstable

    I2C address:
    0x65 (22k jumper shorted)
    0x66 (43k jumper shorted)
    0x67 default

    https://learn.adafruit.com/adafruit-mcp9601/pinouts#i2c-logic-pins-3101074-3

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.
    """

    description = 'Adafruit MCP9601 I2C Thermocouple Amplifier'
    i2c_min = 0x65
    i2c_max = i2c_default = 0x67

    # {type: (min_temp_deg_c, max_temp_deg_c), ...}
    supported_thermocouple_types = {
        'K': (-200, 1372),
        'J': (-150, 1200),
        'T': (-200, 400),
        'N': (-150, 1300),
        'E': (-200, 1000),
        'S': (250, 1664),
        'B': (1000, 1800),
        'R': (250, 1664),
    }

    def __init__(self, *args):
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None
        self.tmin = self.tmax = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.
        """
        try:
            self._instance = mcp9600.MCP9600(self.sensor_i2c_address)
        except (OSError, RuntimeError):
            pass
        else:
            # The test setup here will have temperatures nowhere near the edge
            # of the range for the thermocouples. Since we do (rarely) see
            # extreme values returned from the API, filter out the majority of
            # those cases by constraining the min/max bounds.
            self._instance.set_thermocouple_type(self.thermocouple_type)
            self.tmin, self.tmax = self.supported_thermocouple_types[self.thermocouple_type]

    def missing(self):
        """Check if the hardware is present and operational."""
        return self._instance is None

    def read(self):
        """
        Read value from sensor.

        The call to get_hot_junction_temperature() returns the thermocouple
        temperature. Its counterpart, get_cold_junction_temperature() returns
        the MCP9601's onboard temperature sensor (ambient).

        It is possible for the API call to return temperatures that are out of
        range for the configured thermocouple type, and this has been
        observed (sporadically) in the test environment as extreme values
        below absolute zero. None is returned in place of such aberrant
        values.

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : dict
            temperature in degrees Celsius
            e.g. {'TCk2_M1_vc_temperature': 20.1875} or None
        ----------------------------------------------------------------------
        """
        retval = None
        attempts = 5

        if self._instance is not None:
            for _ in itertools.repeat(None, attempts):
                try:
                    temp_dc = self._instance.get_hot_junction_temperature()
                except OSError:
                    pass
                else:
                    if self.tmin <= temp_dc <= self.tmax:
                        retval = {f'{self.name} {UNIT.temperature}': temp_dc}
                        break

                    logging.debug('%s, aberrant value: %s', self.name, temp_dc)
                    time.sleep(0.04)
            else:
                logging.debug('%s, read attempts exceeded', self.name)

        return retval


class Nau7802(Sensor):
    """
    Adafruit 24-Bit ADC (NAU7802)

    https://www.adafruit.com/product/4538
    https://github.com/CedarGroveStudios/CircuitPython_NAU7802

    Used with strain gauges in this context. It is ASSUMED that there is no
    load acting on the strain gauge when this class is initialised.

    Unfortunately, this is another sensor that cannot have its dependencies
    automatically installed via pip.

    From the GitHub repo above, file cedargrove_nau7802.py needs to be
    manually copied into either (1) /usr/local/lib/python3.9/dist-packages if
    the OS's python3 is being used, or (2) into your python virtual
    environment which typically would be something like the following on
    64-bit Raspberry Pi OS: $PATH_TO_VENV/lib/python3.9/site-packages/

    This class was adapted from the repo file: examples/nau7802_simpletest.py
    """

    description = 'Adafruit 24-Bit ADC (NAU7802)'
    i2c_min = i2c_default = i2c_max = 0x2A
    active_channels = 2

    def __init__(self, *args):
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.

        This function will FAIL SILENTLY if the device is not reachable.
        """
        try:
            self._instance = NAU7802(
                board.I2C(),
                address=self.i2c_default,
                active_channels=self.active_channels,
            )
        except OSError:
            pass
        else:
            # zero all channels
            success = []
            for channel in range(1, self.active_channels + 1):
                self._instance.channel = channel
                success.append(self._instance.calibrate('INTERNAL'))
                success.append(self._instance.calibrate('OFFSET'))

            calibration_success = all(success)
            print('calibration_success', calibration_success)

    def missing(self):
        """Check if the hardware is present and operational."""
        return self._instance is None or not self._instance.available()

    def read(self, samples=4):
        """
        Read voltage from ADC. There's some indication from the API's author
        that we should take multiple readings.

        Ignore channel 2 for the moment.

        Returns signed 24-bit int.
        """
        buffer = []
        max_attempts = samples * 4
        retval = None

        self._instance.channel = 1
        for _ in itertools.repeat(None, max_attempts):
            try:
                value = self._instance.read()
            except OSError:
                pass
            else:
                buffer.append(value)

            if len(buffer) == samples:
                retval = {
                    f'{self.name} {UNIT.strain}': int(statistics.mean(buffer))
                }
                break

        return retval


class Pcf8591(Sensor):
    """
    The PCF8591 is an 8-bit ADC with four analog inputs.

    I2C address:
        0x48 default
        0x49 - 0x4f using links A0, A1 and A2

    https://learn.adafruit.com/adafruit-pcf8591-adc-dac/pinouts#analog-pins-3067027-5

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.
    """

    description = 'PCF8591 8-bit ADC with four analog inputs'
    i2c_min = i2c_default = 0x48
    i2c_max = 0x4F
    # when checked, PCF.A0 was 0, PCF.A1 was 1, etc... so this LUT is probably
    # unnecessary
    supported_analogue_inputs = {0: PCF.A0, 1: PCF.A1, 2: PCF.A2, 3: PCF.A3}

    def __init__(self, *args):
        """Initialises with data from the user-supplied configuration file."""
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.

        This function ASSUMES that the device is reachable on the I2C bus;
        any setting of multiplexer/channel is the responsibility of the
        caller.

        This will fail silently - since not all sensors need to create an
        instance, and the interface should be consistent - hence the caller
        should call missing() to determine whether the sensor is present.
        """
        try:
            pcf8591_instance = PCF.PCF8591(I2C_BOARD)
        except (OSError, ValueError):
            pass
        else:
            self._instance = pcf_in(
                pcf8591_instance, self.supported_analogue_inputs[self.analogue_input]
            )

    def missing(self):
        """Check if the hardware is present and operational."""
        return self._instance is None

    def read(self):
        """
        Read ADC value.
        """
        try:
            raw_adc_value = self._instance.value
        except (OSError, AttributeError):
            raw_adc_value = None

        return raw_adc_value


class Sht4x(Sensor):
    """
    Support added for the 2025 MUonE test beam.

    SHT41: https://www.adafruit.com/product/5776
    SHT45: https://www.adafruit.com/product/5665

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.
    """

    description = 'Sensiron SHT4x digital humidity and temperature sensor'
    i2c_min = i2c_max = i2c_default = 0x44

    def __init__(self, *args):
        """
        Initialises with data from the user-supplied configuration file.

        The API uses the hardwired default I2C address. The call to
        default_i2c_address_if_unset is made to keep the stored details
        consistent, even though they will not be used.
        """
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.
        """
        try:
            self._instance = adafruit_sht4x.SHT4x(I2C_BOARD)

        except (OSError, RuntimeError, ValueError):
            self._instance = None

        else:
            self._instance.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

    def missing(self):
        """Check if the hardware is obviously missing."""
        return self._instance is None

    def read(self):
        """
        Read sensor.

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : dict
            temperature in degrees Celsius, relative humidity (%)
            e.g. {'shtc3_temperature': 20.26735030214246,
                  'shtc3_relative_humidity': 0.09766221082829762} or None
        ----------------------------------------------------------------------
        """
        retval = None

        if self._instance is not None:
            temp_dc, rhum_pc = self._instance.measurements
            retval = {
                f'{self.name} {UNIT.temperature}': temp_dc,
                f'{self.name} {UNIT.relative_humidity}': rhum_pc,
            }

        return retval


class Shtc3(Sensor):
    """
    This device is not part of the test setup, and is only used for testing the
    I2C bus and multiplexers.

    https://www.adafruit.com/product/4636

    Functions activate() and read() ASSUME that the sensor is reachable on the
    I2C bus. It is the caller's responsibility to ensure that if the sensor is
    attached via a multiplexer, that the latter is appropriately configured.
    """

    description = 'Sensiron SHTC3 digital humidity and temperature sensor'
    i2c_min = i2c_max = i2c_default = 0x70

    def __init__(self, *args):
        """
        Initialises with data from the user-supplied configuration file.

        The API uses the hardwired default I2C address. The call to
        default_i2c_address_if_unset is made to keep the stored details
        consistent, even though they will not be used.
        """
        super().__init__(*args)
        self.default_i2c_address_if_unset(self.i2c_default)
        self._instance = None

    def activate(self):
        """
        Creates an instance that will be used for future sensor access.
        """
        try:
            self._instance = adafruit_shtc3.SHTC3(I2C_BUSIO)
        except (OSError, RuntimeError, ValueError):
            self._instance = None

    def missing(self):
        """Check if the hardware is obviously missing."""
        return self._instance is None

    def read(self):
        """
        Read SHTC3 sensor.

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : dict
            temperature in degrees Celsius, relative humidity (%)
            e.g. {'shtc3_temperature': 20.26735030214246,
                  'shtc3_relative_humidity': 0.09766221082829762} or None
        ----------------------------------------------------------------------
        """
        retval = None

        if self._instance is not None:
            temp_dc, rhum_pc = self._instance.measurements
            retval = {
                f'{self.name} {UNIT.temperature}': temp_dc,
                f'{self.name} {UNIT.relative_humidity}': rhum_pc,
            }

        return retval


##############################################################################
# sensors - acquire data through other devices
##############################################################################


class AtlasNtc(Ads1015):
    """
    Reads from an ADS1015 12-bit ADC and analogue multiplexer.
    """

    description = 'Atlas NTC Thermistor'

    def read(self):
        """
        Read a temperature value from an NTC mounted on the SLHC Atlas
        Common Hybrid V3.8.

        Test with chiller operational:

        chiller set point          :   -25      deg C
        chiller internal temp      :   -25      deg C
        ADC voltage (ADS1015)      :     2.3041 V
        Calculated NTC resistance  : 64147      ohms
        Calculated NTC temperature :   -18.937  deg C
        TCk2_M1_vc                 :   -18.062  deg C
        TCt1_M1_flex               :   -15.188  deg C

        chiller set point          :   -30      deg C
        chiller internal temp      :   -30      deg C
        ADC voltage (ADS1015)      :     2.5221 V
        Calculated NTC resistance  : 79918      ohms
        Calculated NTC temperature :   -23.460  deg C
        TCk2_M1_vc                 :   -22.375  deg C
        TCt1_M1_flex               :   -19.188  deg C

        ----------------------------------------------------------------------
        args : none
        ----------------------------------------------------------------------
        returns : dict
            temperature in degrees Celsius
            e.g. {'ntc_temperature': -61.19908797184263} or None
        ----------------------------------------------------------------------
        """
        voltage = super().read()

        try:
            r_ohms = self._volts_to_ohms(voltage)
            temp_dc = self._ohms_to_degc(r_ohms)
        except TypeError:
            retval = None
        else:
            retval = {f'{self.name} {UNIT.temperature}': temp_dc}

        return retval

    ##########################################################################
    # support functions
    ##########################################################################

    @staticmethod
    def _degc_to_ohms(degc):
        """
        Inverse of Steinhart–Hart. UNUSED: left here for future reference.

        ----------------------------------------------------------------------
        args
            deg_c : float
                value in degrees C
        ----------------------------------------------------------------------
        returns : float
            value in ohms
        ----------------------------------------------------------------------
        """
        A = 0.8676453371787721e-3
        B = 2.541035850140508e-4
        C = 1.868520310774293e-7
        k_zero_deg = 273.15
        temp = degc + k_zero_deg

        x = (1 / C) * (A - 1 / temp)
        y = math.sqrt(((B / (3 * C)) ** 3) + ((x**2) / 4))
        r = math.exp(math.pow(y - x / 2, 1 / 3) - math.pow(y + x / 2, 1 / 3))

        return r

    @staticmethod
    def _ohms_to_degc(resistance):
        """
        Use Steinhart–Hart: 1 / T = A + B * ln(R) + C * ln(R) ** 3

        ----------------------------------------------------------------------
        args
            resistance : float
                value in ohms
        ----------------------------------------------------------------------
        returns
            deg_c : float
                value in degrees C
        ----------------------------------------------------------------------
        """
        A = 0.8676453371787721e-3
        B = 2.541035850140508e-4
        C = 1.868520310774293e-7
        k_zero_deg = 273.15

        try:
            l_res_ohms = math.log(resistance)
        except (TypeError, ValueError):
            deg_c = None
        else:
            deg_c = 1 / (A + B * l_res_ohms + C * l_res_ohms**3) - k_zero_deg

        return deg_c

    @staticmethod
    def _volts_to_ohms(adcv):
        """
        NTC at 605216 ohms is approximately -60 degC, aim for 3.8V at the ADC input
        at this point. NTC at 25 deg C should be 10k ohms.

        For -60 deg C, NTC resistance = 605216
        adcv = (vcc * r_rtc) / (r_ntc + r_ref)
             = (4.1 * 605216) / (605216 + 50000)
             = 2481385.6 / 655216
             = 3.78712608

        To find r_ntc from adcv:
        adcv = (vcc * r_rtc) / (r_ntc + r_ref)
        adcv = vcc / (1 + r_ref / r_ntc)
        (1 + r_ref / r_ntc) = vcc / adcv
        r_ref / r_ntc = vcc / adcv - 1
        r_ref / (vcc / adcv - 1) = r_ntc

        ----------------------------------------------------------------------
        args
            adcv : float
                value in volts
        ----------------------------------------------------------------------
        returns : float
            value in degrees C or None
        ----------------------------------------------------------------------
        """
        r_ref = 50000
        vcc = 4.1
        try:
            r_ntc = r_ref / (vcc / adcv - 1)
        except ZeroDivisionError:
            # the power supply is probably turned off
            r_ntc = None

        return r_ntc


class SmcZse30A01F(Pcf8591):
    """
    Reads from a PCF8591 8-bit ADC.

    This class is deprecated and will be removed in a future version of this
    software. Use class SmcZse30A01F12 for new designs.
    """

    description = 'SMC ZSE30A-01-F Digital Pressure Switch'

    def read(self):
        """
        Read a pressure (vacuum) value from an SMC ZSE30A-01-F pressure sensor
        connected to input channel 0 of an Adafruit PCF8591 8-bit ADC.

        The ADC is configured to occupy the default I2C address 0x48, so can
        be attached to the mux daisy-chain connector.

        ASSUMES that the multiplexer/channel is reachable on the I2C bus.

        --------------------------------------------------------------------------
        args : none
        --------------------------------------------------------------------------
        returns : dict
            pressure in kPa, e.g. {'smc_vacuum': -0.3395540799999992} or None
        --------------------------------------------------------------------------
        """
        raw_adc_value = super().read()

        try:
            pres_kpa = self._adc_to_pressure(raw_adc_value)
        except TypeError:
            retval = None
        else:
            retval = {f'{self.name} {UNIT.vacuum}': pres_kpa}

        return retval

    ##########################################################################
    # support functions
    ##########################################################################

    @staticmethod
    def _adc_to_pressure(adc):
        """
        ADC value to pressure conversion assuming the voltage is not dropped over
        the default 300 ohm load resistor, but with the following arrangement to
        keep the voltage at the ADC input less than 3.3V.

        (Vout from sensor) 150 ohm resistor (V ADC) 150 ohm resistor (0V)

        SMC display    ADC value
        -64.0 kPa      42496
         +0.1 kPa      12032

        wolfram alpha website query:
            linear fit {{12032,0.2},{42496,-64.0}}
        Mathematica:
            Normal[LinearModelFit[{{12032,0.2},{42496,-64.0}}, x^Range[0, 1], x]]

        Solution:
            25.5563 - 0.00210741 x

        --------------------------------------------------------------------------
        args
            adc : int
                The value read from the PCF8591 8-bit ADC is 16-bits wide. The
                top byte contains the 8-bit conversion value, the lower byte is
                always zero.
        --------------------------------------------------------------------------
        returns : float
            pressure in kPa
        --------------------------------------------------------------------------
        """
        return 25.5563 - 0.00210741 * adc


class SmcZse30A01F12(Ads1015):
    """
    Reads from an Ads1015 12-bit ADC.
    """

    description = 'SMC ZSE30A-01-F Digital Pressure Switch'

    def read(self):
        """
        Read a pressure (vacuum) value from an SMC ZSE30A-01-F pressure sensor
        connected to a SparkFun Qwiic 12-bit ADC and analogue multiplexer
        (ADS1015).

        ASSUMES that the multiplexer/channel is reachable on the I2C bus.

        --------------------------------------------------------------------------
        args : none
        --------------------------------------------------------------------------
        returns : dict
            pressure in kPa, e.g. {'smc_vacuum': -0.3395540799999992} or None
        --------------------------------------------------------------------------
        """
        voltage = super().read()

        try:
            pres_kpa = self._volts_to_pressure(voltage)
        except TypeError:
            retval = None
        else:
            retval = {f'{self.name} {UNIT.vacuum}': pres_kpa}

        return retval

    ##########################################################################
    # support functions
    ##########################################################################

    @staticmethod
    def _volts_to_pressure(adcv):
        """
        ADC voltage to pressure conversion assuming the voltage is not dropped
        over the default 300 ohm load resistor, but uses a potential divider
        to keep the voltage at the ADC input less than the 3.3V supply voltage.
        The maximum load impedance should be 300 ohms, and the current at
        full-scale driven in to the load is 20mA.

        (Vout from sensor) 150 ohm resistor (V ADC) 150 ohm resistor (0V)

        The voltage at the top of the potential divider is
        V = IR = 0.02 * 300 = 6V which means a maximum of 3V at the ADC input.

        SMC display    voltage
        -99.2 kPa      2.9400897244178594
         +0.1 kPa      0.5920180669576097

        wolfram alpha website query:
            linear fit {{0.5920180669576097, 0.1},{2.9400897244178594, -99.2}}
        Mathematica:
            Normal[LinearModelFit[{
                {0.5920180669576097, 0.1}, {2.9400897244178594, -99.2}},
                x^Range[0, 1], x]]
        Solution:
            25.1365 - 42.29 x

        --------------------------------------------------------------------------
        args
            adcv : float
                value in volts
        --------------------------------------------------------------------------
        returns : float
            pressure in kPa
        --------------------------------------------------------------------------
        """
        return 25.1365 - 42.29 * adcv


class SmcPfm725SF01F(Ads1015):
    """
    Placeholder class for upcoming PFM725S-F01-F device.
    """

    description = 'SMC PFM725S-F01-F 2-Color Digital Flow Switch, Integrated Display'

    def read(self):
        """
        --------------------------------------------------------------------------
        args : none
        --------------------------------------------------------------------------
        returns : dict
            flow rate in litres per minute, range of values 0.5 to 25 for this
            model. E.g. {'smc_flowrate': 0.734} or None
        --------------------------------------------------------------------------
        """
        voltage = super().read()

        try:
            flow_rate = self._volts_to_flow_rate(voltage)
        except TypeError:
            retval = None
        else:
            retval = {f'{self.name} {UNIT.flow_rate}': flow_rate}

        return retval

    ##########################################################################
    # support functions
    ##########################################################################

    @staticmethod
    def _volts_to_flow_rate(adcv):
        """
        Theoretical linear relationship from datasheet:

        For dry air: 25l/s max flow rate (20mA) 0l/s (4mA).
        Load impedance range 50-600 ohms.

        Assuming that current flows through a 150 ohm resistor, where 20mA will
        yield ~3V, the relationship should look something like this:

        dry air flow rate (l/s)    Current (mA)    Voltage (V)
        25                         20              3.00
         0                          4              0.60

        wolfram alpha website query:
            linear fit {{0.6, 0},{3, 25}}
        Mathematica:
            Normal[LinearModelFit[{{0.6, 0}, {3, 25}}, x^Range[0, 1], x]]
        Solution:
            10.4167 x - 6.25

        Measured relationship:

        voltage = [0.6, 0.646, 0.66, 0.67, 0.68, 0.69, 0.694, 0.746,
            0.788, 0.838, 0.888, 0.934, 0.98, 1.032, 1.078, 1.172, 1.268,
            1.37, 1.464, 1.558, 1.656, 1.746, 1.846, 1.94, 2.038, 2.134,
            2.226, 2.29, 2.32, 2.42, 2.51, 2.61, 2.71, 2.82, 2.91, 3]
        flow_rate = [0, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.5, 2, 2.5, 3, 3.5,
            4, 4.5, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 17.7,
            18, 19, 20, 21, 22, 23, 24, 25]

        solution from numpy polynomial fit

        10.425474162729426 x -6.247711690827281

        clamp value to zero since this is appropriate to the test environment

        ----------------------------------------------------------------------
        args
            adcv : float
                value in volts
        ----------------------------------------------------------------------
        returns : float
            flow rate value in litres per minute
        ----------------------------------------------------------------------
        """
        return max(0.0, 10.425474162729426 * adcv - 6.247711690827281)
