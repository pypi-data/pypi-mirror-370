"""
Read values from the Keithley DMM6500.

https://docs.python.org/3.6/library/weakref.html#comparing-finalizers-with-del-methods
"""

import threading
import weakref

import serial

from mmcb import common
from mmcb import lexicon


class Production:
    """
    Locks to support threaded operation in the underlying library code (1 lock
    per serial port).
    """

    def __init__(self, instrument_channels):
        """
        -----------------------------------------------------------------------
        args
            instrument_channels : list of <class 'mmcb.common.Channel'>
        -----------------------------------------------------------------------
        returns : none
        -----------------------------------------------------------------------
        """
        self.portaccess = {
            port: threading.Lock()
            for port in {channel.port for channel in instrument_channels}
        }


class Dmm6500:
    """
    Connection and reading from Keithley DMM 6500.
    """

    _cached_instruments = common.cache_read({'instrument'})

    _channels = []
    for _port, _details in _cached_instruments.items():
        (
            _config,
            _device_type,
            _serial_number,
            _model,
            _manufacturer,
            _device_channels,
            _release_delay,
        ) = _details

        for _device_channel in _device_channels:
            _channels.append(
                common.Channel(
                    _port,
                    _config,
                    _serial_number,
                    _model,
                    _manufacturer,
                    _device_channel,
                    _device_type,
                    _release_delay,
                    None,
                )
            )

    _pipeline = Production(_channels)

    try:
        _channel = _channels[0]
    except IndexError:
        pass

    def __init__(self):
        try:
            self._ser = serial.Serial(port=self._channel.port)
        except OSError:
            self.init_failed = True
        else:
            self.init_failed = False
            self._finalizer = weakref.finalize(self, self._ser.close)
            self._ser.apply_settings(self._channel.config)
            self._ser.reset_input_buffer()
            self._ser.reset_output_buffer()

    def remove(self):
        """manual garbage collection: close serial port"""
        self._finalizer()

    @property
    def removed(self):
        """check (indirectly) if the serial port has been closed"""
        return not self._finalizer.alive

    def _send_command(self, command):
        """
        Issue command to instrument.

        -----------------------------------------------------------------------
        args
            command : string
        -----------------------------------------------------------------------
        returns : none
        -----------------------------------------------------------------------
        """
        common.send_command(
            self._pipeline,
            self._ser,
            self._channel,
            lexicon.instrument(self._channel.model, command),
        )

    def configure_read_capacitance(self):
        self._send_command('configure to read capacitance')

    def configure_read_ac_current(self):
        self._send_command('configure to read ac current')

    def configure_read_dc_current(self):
        self._send_command('configure to read dc current')

    def configure_read_resistance(self):
        self._send_command('configure to read resistance')

    def configure_read_temperature(self):
        self._send_command('configure to read temperature')

    def configure_read_dc_voltage(self):
        self._send_command('configure to read dc voltage')

    def configure_read_ac_voltage(self):
        self._send_command('configure to read ac voltage')

    def read_value(self):
        """
        Read the value of the previously configured parameter from the
        instrument.

        -----------------------------------------------------------------------
        args : none
        -----------------------------------------------------------------------
        returns
            value : float or None
        -----------------------------------------------------------------------
        """
        response = common.atomic_send_command_read_response(
            self._pipeline,
            self._ser,
            self._channel,
            lexicon.instrument(self._channel.model, 'read value'),
        )

        try:
            value = float(response)
        except ValueError:
            value = None

        return value
