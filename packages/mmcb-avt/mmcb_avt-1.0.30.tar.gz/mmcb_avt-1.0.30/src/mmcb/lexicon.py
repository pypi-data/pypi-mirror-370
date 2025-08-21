"""
Common functions related to serial port commands for project devices.

The functions motion() and power() are relatively expensive function calls
as there is a fair amount of substitution to perform for each call. Calls for
write commands (with variable parameters) will cache poorly, e.g. setting
voltage values; constant commands that read voltage/current will cache well.

power() has an LRU cache applied as calls are made very frequently to read
power supply voltage/current/status. Calls to motion(), though similarly
expensive, are relatively sparse.

e.g. for command:

import statistics
import timeit
statistics.mean(timeit.Timer("lexicon.power('2410', 'read measured vi')",
                             setup='import lexicon').repeat(100,1))

timings are:

    2.043e-05s (un-cached)
    4.207e-07s (cached)

Cache performance for: ./iv.py -200 --hold 1

CacheInfo(hits=82, misses=56, maxsize=128, currsize=56)

callable functions from this file:

    motion
    power
"""

import functools


##############################################################################
# motion controller command string generation
##############################################################################

def motion(controller, command, identifier=None, argument1=None, argument2=None):
    """
    generate the requested RS232 command sequence appropriate for the
    motion controller specified

    --------------------------------------------------------------------------
    args
        controller : string
            name of the controller
        command : string
            name of the command to be fetched
        identifier : int
            this may be either the controller axis to which the stage is
            connected (for esp30 or mm4006), or the controller address in the
            case of the smc100
        argument1 : numeric
            a parameter to substitute into the command string
        argument2 : numeric
            a parameter to substitute into the command string
    --------------------------------------------------------------------------
    returns : string
        a valid command that can be sent to the controller over RS232
    --------------------------------------------------------------------------
    """
    terminate = '\r\n'
    axis = address = identifier

    ##########################################################################
    # Language: proprietary
    #
    # "The maximum number of characters allowed on a command line is 80."
    # ESP300.pdf, p. 3-8
    esp30 = {
        'is stage moving': f'{axis}MD?',
        'motor on': f'{axis}MO',
        # p.3.98, response: 1 (ON) 0 (OFF)
        'check motor on': f'{axis}MO?',
        # argument1: decimal.Decimal, absolute position
        'move absolute': f'{axis}PA{argument1}',
        # argument1: decimal.Decimal, relative distance to move
        'move relative': f'{axis}PR{argument1}',
        'move to home position': f'{axis}MO;{axis}OR1',
        'read controller version': 'VE',
        'read error': 'TE?',
        'read position': f'{axis}TP?',
        'read stage identifier': f'{axis}ID?',
        'set speed': (
            # argument1: int, acceleration
            # argument2: int, velocity
            f'{axis}AC{argument1};'
            f'{axis}AG{argument1};'
            f'{axis}VU{argument2};'
            f'{axis}VA{argument2};'
            f'{axis}OL{argument2};'
            f'{axis}OH{argument2}{terminate}'
            f'{axis}AC?;'
            f'{axis}AG?;'
            f'{axis}VU?;'
            f'{axis}VA?;'
            f'{axis}OL?;'
            f'{axis}OH?'),
        'software limits check': f'{axis}ZS?',
        'software limits disable': f'{axis}ZS4H',
        'stop motion': f'{axis}ST'}

    ##########################################################################
    # Language: proprietary
    #
    # "A single command line ... may not exceed 110 characters."
    # MM4K6_701_E3.pdf, p. 3.16
    mm4006 = {
        'is stage moving': f'{axis}TS',
        'motor on': f'{axis}MO',
        # check motor status, MM4K6_701_E3.pdf, p.3.86
        # bit 1 motor status: 0 (ON) 1 (OFF)
        'check motor on': f'{axis}MS',
        # argument1: decimal.Decimal, absolute position
        'move absolute': f'{axis}PA{argument1}',
        # argument1: decimal.Decimal, relative distance to move
        'move relative': f'{axis}PR{argument1}',
        'move to home position': f'{axis}MO;{axis}OR',
        'read controller version': 'VE',
        'read error': 'TE',
        'read position': f'{axis}TP',
        'read stage identifier': f'{axis}TS',
        'set speed': (
            # argument1: int, acceleration
            # argument2: int, velocity
            f'{axis}AC{argument1};'
            f'{axis}VU{argument2};'
            f'{axis}VA{argument2};'
            f'{axis}OL{argument2};'
            f'{axis}OH{argument2}{terminate}'
            f'{axis}AC?;'
            f'{axis}VU?;'
            f'{axis}VA?;'
            f'{axis}OL?;'
            f'{axis}OH?'),
        'stop motion': f'{axis}ST'}

    ##########################################################################
    # Language: proprietary
    smc = {
        'is stage moving': f'{address}TS',
        'motor on': f'{address}MM1',
        'check motor on': f'{address}MM1?',
        # argument1: decimal.Decimal, absolute position
        'move absolute': f'{address}PA{argument1}',
        # argument1: decimal.Decimal, relative distance to move
        'move relative': f'{address}PR{argument1}',
        'move to home position': f'{address}TS{terminate}{address}OR',
        'move to home position 2': '',
        'read controller version': f'{address}VE',
        'read error': f'{address}TE',
        'read position': f'{address}TP',
        'read stage identifier': f'{address}ID?',
        'stop motion': f'{address}ST'}

    instructions = {'esp300': esp30, 'mm4006': mm4006, 'smc': smc}

    # sanity checks
    first = instructions.get(controller)
    assert first is not None, 'unrecognised controller name'
    second = first.get(command)
    assert second is not None, 'unrecognised command'
    cmd_string = instructions[controller][command]
    assert 'None' not in cmd_string, 'missing argument to function'

    return bytes(cmd_string + terminate, 'utf-8')


##############################################################################
# power supply command string generation
##############################################################################

@functools.lru_cache(maxsize=64)
def power(model, command, argument1=None, argument2=None, channel=None):
    """
    generate the requested RS232 command sequence appropriate for the
    power supply specified

    Manufacturers' implementations of Standard Commands for Programmable
    Instruments (SCPI) all seem to have their own quirks, which is why there
    is no generic SCPI command sequence, and each power supply has its own
    dictionary.

    --------------------------------------------------------------------------
    args
        model : string
            power supply model
        command : string
            name of the command to be fetched
        argument1 : numeric/string
            a parameter to substitute into the command string
        argument2 : numeric/string
            a parameter to substitute into the command string
        channel : string
            channel name, the caller is required to use this for
            multichannel power supplies, but may omit it for single-channel
    --------------------------------------------------------------------------
    returns : string
        a valid command that can be sent to the psu over RS232
    --------------------------------------------------------------------------
    """
    terminate = '\n' if model == '2614b' else '\r\n'

    ##########################################################################
    # Language: Standard Commands for Programmable Instruments (SCPI)
    keithley_2410 = {
        # returns '0' (not in compliance) or '1' (in compliance) (p. 18-70)
        'check compliance': ':CURR:PROT:TRIP?',
        # returns '0' (disabled - no restrictions) or '1' (enabled)
        'check interlock': ':OUTP:INT:STAT?',
        # returns '0' (output off) or '1' (output on)
        'check output': ':OUTP?',
        'clear event registers': '*CLS',
        # compliance definitions on p. 6-5
        'configure': (
            # clear all event registers and error queue
            f'*CLS;'
            # when reading status registers, use decimal format
            f':FORM:SREG ASC;'
            # select voltage source
            f':SOUR:FUNC VOLT;'
            # set fixed voltage source mode
            f':SOUR:VOLT:MODE FIXED;'
            # set voltage range to 1000V
            f':SOUR:VOLT:RANG 1000;'
            # set psu to output given voltage
            f':SOUR:VOLT:LEV {argument1};'
            # set power supply's current limit
            f':CURR:PROT {argument2};'
            # set current measurement range to match compliance value
            f':CURR:RANG:UPP {argument2};'
            # and make sure the measurement range stays constant
            f':CURR:RANG:AUTO OFF'),
        'configure range': (
            # clear all event registers and error queue
            '*CLS;'
            # when reading status registers, use decimal format
            ':FORM:SREG ASC;'
            # select voltage source
            ':SOUR:FUNC VOLT;'
            # set fixed voltage source mode
            ':SOUR:VOLT:MODE FIXED;'
            # set voltage range to 1000V
            ':SOUR:VOLT:RANG 1000'),
        'identify': '*CLS;*IDN?',
        'output off': ':OUTP OFF',
        'output on': ':OUTP ON',
        'read measured vi': (
            # set concurrent measurement mode on
            f':FUNC:CONC 1;'
            # measure actual dc voltage and current
            f':FUNC:ON "VOLT:DC","CURR:DC"{terminate}'
            # read value string
            f':READ?'),
        'read set voltage': (
            # disable concurrent measurement mode
            f':FUNC:CONC 0;'
            # measure actual dc current (forces set voltage to appear in index 0)
            f':FUNC:ON "CURR:DC"{terminate}'
            # read value string
            f':READ?'),
        'read voltage': '*CLS;:READ?',
        'reset': '*RST',
        # see p. 18-69 (p. 449 in PDF)
        'get current limit': ':CURR:PROT:LEV?',
        # compliance definitions on p. 6-5
        'set current limit': (
            # set power supply's current limit
            f':CURR:PROT {argument1};'
            # set current measurement range to match compliance value
            f':CURR:RANG:UPP {argument1};'),
        # argument1: power supply output 'ON' or 'OFF'
        'set output': f':OUTP {argument1}',
        # argument1: use power supply 'REAR' or 'FRON' output
        'set route': f':ROUT:TERM {argument1}',
        'set voltage': (
            # clear all event registers and error queue
            f'*CLS;'
            # set psu voltage
            # argument1: decimal.Decimal, voltage
            f':SOUR:VOLT:LEV {argument1}'),
        'set voltage and range': (f':SOUR:FUNC VOLT;'
                                  f':SOUR:VOLT:MODE FIXED;'
                                  f':SOUR:VOLT:RANG 1000;'
                                  # argument1: decimal.Decimal, voltage
                                  f':SOUR:VOLT:LEV {argument1}')}

    ##########################################################################
    # Language: Lua
    keithley_2614b = {
        # example response: 'true' or 'false' (p. 11-238)
        'check compliance': f'print(smu{channel}.source.compliance)',
        # Without hardware interlock: '0.00000e+00'
        # with hardware interlock: '2.04800e+03'
        'check interlock': 'print(status.measurement.condition)',
        # returns '0.00000e+00' (off) or 1.00000e+00' (on)
        'check output': f'print(smu{channel}.source.output)',
        # 2614b also has separate commands for model and serial
        # e.g. m=localnode.model;s=localnode.serialno;print(m,s)
        'clear event registers': 'errorqueue.clear()',
        # argument1: decimal.Decimal, voltage
        'configure': (f'beeper.enable=beeper.OFF;'
                      f'smu{channel}.source.func=smu{channel}.OUTPUT_DCVOLTS;'
                      f'smu{channel}.source.rangev=200;'
                      f'smu{channel}.source.autorangev=smu{channel}.AUTORANGE_OFF;'
                      f'smu{channel}.source.limiti={argument2};'
                      f'smu{channel}.source.levelv={argument1};'
                      f'smu{channel}.measure.autorangei=smu{channel}.AUTORANGE_ON;'
                      f'smu{channel}.source.output=smu{channel}.OUTPUT_ON;'
                      f'display.smu{channel}.measure.func=display.MEASURE_DCAMPS'),
        'configure range': (f'beeper.enable=beeper.OFF;'
                            f'smu{channel}.source.func=smu{channel}.OUTPUT_DCVOLTS;'
                            f'smu{channel}.source.rangev=200;'
                            f'smu{channel}.source.autorangev=smu{channel}.AUTORANGE_OFF;'
                            f'smu{channel}.measure.autorangei=smu{channel}.AUTORANGE_ON;'
                            f'display.smu{channel}.measure.func=display.MEASURE_DCAMPS'),
        # example response '1.00000e-01'
        'get current limit': f'print(smu{channel}.source.limiti)',
        # argument1: decimal.Decimal, voltage
        'set current limit': f'smu{channel}.source.limiti={argument1}',
        # example response: 'Keithley Instruments SMU 2614B - 4428182'
        'identify': ('errorqueue.clear();'
                     'print(localnode.description)'),
        # argument1: string, channel 'a' or 'b'
        'output off': f'smu{channel}.source.output=smu{channel}.OUTPUT_OFF',
        # argument1: string, channel 'a' or 'b'
        'output on': f'smu{channel}.source.output=smu{channel}.OUTPUT_ON',
        'read measured vi': f'print(smu{channel}.measure.v(),'
                            f'smu{channel}.measure.i())',
        # argument1: string, channel 'a' or 'b'
        # example response: '6.43730e-13'
        'read current': f'print(smu{channel}.measure.i())',
        # example response: '4.00000e+00'
        'read set voltage': f'print(smu{channel}.source.levelv)',
        # argument1: string, channel 'a' or 'b'
        # example response: '1.00011e+01'
        'read voltage': f'print(smu{channel}.measure.v())',
        # reset channel defaults
        'reset': 'localnode.reset()',
        # argument1: string, channel 'a' or 'b'
        # argument1: decimal.Decimal, voltage value
        'set voltage': f'smu{channel}.source.levelv={argument1}',
        # used for clearing anything in the PSU's command buffer
        'terminator only': ''}

    ##########################################################################
    # Language: proprietary
    #
    # Cannot chain multiple commands for ISEG SHQ in the same command
    # string as can be done for Keithley - particularly this affects
    # initial configuration - all commands must be called individually.
    iseg_shq = {
        'check compliance': f'S{channel}',
        'check interlock': f'S{channel}',
        'check module status': f'T{channel}',
        'check output': f'S{channel}',
        'configure': '',
        # e.g. returns '484216;3.09;4000V;3mA' for ISEG SHQ 224M (2x 4kV / 2mA)
        'identify': '#',
        'read current': f'I{channel}',
        # read maximum voltage rate of change
        'read max rate of change': f'V{channel}',
        'read voltage': f'U{channel}',
        # for 100V ('D1=100') returns 01000-01, for 1100V (D1='1100') 11000-01
        'read set voltage': f'D{channel}',
        # part of 'configure' for ISEG SHQ
        # set auto ramp
        # (as soon as voltage is set with D command, move to that voltage)
        'set auto ramp': f'A{channel}=8',
        # set inter-character delay to minimum (1ms)
        'set char delay': 'W=1',
        # Unlike Keithley, ISEG sets output channel polarity with hardware
        # screws on the rear panel.
        # All voltages specified must be positive, with a maximum of 2
        # decimal places.
        # argument1: string, channel '1' or '2'
        # argument1: decimal.Decimal, voltage value
        'set voltage': f'D{channel}={argument1}',
        # set maximum voltage rate of change to the fastest available 255V/s
        'set voltage max rate of change': f'V{channel}={argument1}',
        # ISEG SHQ requires an initial CRLF to synchronise
        'synchronise': ''}

    ##########################################################################
    # Language: Standard Commands for Programmable Instruments (SCPI)
    #
    # dual-output DC power supply 0-35V, 0.8A and 0-60V, 0.5A
    # e3647a can accept as many queries as needed with only a single read
    agilent_e3647a = {
        'check output': ':OUTP?',
        'clear event registers': '*CLS',
        'identify': '*IDN?',
        'output off': ':OUTP OFF',
        'output on': ':OUTP ON',
        'read current': f':INST:SEL OUT{channel};:MEAS:CURR?',
        'read measured vi': f':INST:SEL OUT{channel};:MEAS:VOLT?;:MEAS:CURR?',
        'read set voltage': ':VOLT?',
        'read voltage': f':INST:SEL OUT{channel};:MEAS:VOLT?',
        # argument1: decimal.Decimal, voltage value
        'set voltage': (f':INST:SEL OUT{channel};'
                        f':VOLT:RANG LOW;'
                        f':SOUR:VOLT {argument1}')}

    ##########################################################################
    # Language: Standard Commands for Programmable Instruments (SCPI)
    #
    # single-output DC power supply
    # e3634a expects response to be read back after each query and MUST be put
    # into remote mode before MEAS can be used
    agilent_e3634a = {
        'check output': ':OUTP?',
        'clear event registers': '*CLS',
        'identify': '*IDN?',
        'output off': 'OUTP OFF',
        'output on': 'OUTP ON',
        'read current': f'SYST:REM{terminate}MEAS:CURR?',
        'read set voltage': 'VOLT?',
        'read voltage': f':SYST:REM{terminate}:MEAS:VOLT?',
        'set remote': 'SYST:REM',
        # argument1: decimal.Decimal, voltage value
        'set voltage': (f'VOLT:RANG LOW{terminate}'
                        f'SOUR:VOLT {argument1}')}

    ##########################################################################
    # Language: Standard Commands for Programmable Instruments (SCPI)
    #
    # These are branded as Rohde & Schwarz but identify as Hameg
    # quad-output DC power supply, 0-32V, 10A
    hameg_hmp4040 = {
        'check output': f'INST OUT{channel}{terminate}OUTP?',
        'clear event registers': '*CLS',
        'identify': '*IDN?',
        'output off': f'INST OUT{channel}{terminate}OUTP OFF',
        'output on': f'INST OUT{channel}{terminate}OUTP ON',
        'output off all': 'OUTP:GEN OFF',
        'output on all': 'OUTP:GEN ON',
        'read current': f'INST OUT{channel}{terminate}MEAS:CURR?',
        'read set voltage': f'INST OUT{channel}{terminate}VOLT?',
        'read voltage': f'INST OUT{channel}{terminate}MEAS:VOLT?',
        'reset': '*RST',
        'set remote': 'SYST:REM',
        # argument1: decimal.Decimal, voltage value
        # note that a negative sign supplied as part of the voltage value is
        # discarded by the power supply, e.g. -4.1V will set a value of 4.1V
        'set voltage': f'INST OUT{channel}{terminate}SOUR:VOLT {argument1}',
        #
        # Additions for HMP4040 constant current mode.
        #
        # "The R&S HMP switches to the CC mode automatically, when the output
        # current exceeds the maximum value Imax"
        #     HMPSeries_UserManual_en_02.pdf, p.31 (PDF p.46)
        #
        # channel button illuminated with colour:
        #   Green : constant voltage mode (CV)
        #     Red : constant current mode (CC)
        #
        # STAT:QUES:COND? returns a 16-bit register value
        # Bit 0 is set while the instrument is in constant current mode.
        # Bit 1 is set while the instrument is in constant voltage mode.
        'read channel mode': f'STAT:QUES:INST:ISUM{channel}:COND?',
        'get current limit': f'INST OUT{channel}{terminate}CURR?',
        # argument1: float, amps (no scientific representation)
        'set current limit': f'INST OUT{channel}{terminate}CURR {argument1}',
        # argument1: float, amps
        'set current step': f'INST OUT{channel}{terminate}CURR:STEP {argument1}',
        'read current step': f'INST OUT{channel}{terminate}CURR:STEP?',
        'current step down': f'INST OUT{channel}{terminate}CURR DOWN',
        'current step up': f'INST OUT{channel}{terminate}CURR UP'}

    instructions = {
        '2410': keithley_2410, '2614b': keithley_2614b,
        'shq': iseg_shq,
        'e3647a': agilent_e3647a, 'e3634a': agilent_e3634a,
        'hmp4040': hameg_hmp4040
    }

    # sanity checks
    first = instructions.get(model)
    assert first is not None, 'unrecognised model name'
    second = first.get(command)
    assert second is not None, 'unrecognised command'
    cmd_string = instructions[model][command]
    assert 'None' not in cmd_string, 'missing argument to function'

    return bytes(cmd_string + terminate, 'utf-8')


##############################################################################
# general instrumentation
##############################################################################

@functools.lru_cache(maxsize=64)
def instrument(model, command, argument1=None, argument2=None):
    """
    generate the requested RS232 command sequence appropriate for the
    power supply specified

    Manufacturers' implementations of Standard Commands for Programmable
    Instruments (SCPI) all seem to have their own quirks, which is why there
    is no generic SCPI command sequence, and each power supply has its own
    dictionary.

    --------------------------------------------------------------------------
    args
        model : string
            instrument model
        command : string
            name of the command to be fetched
        argument1 : numeric/string
            a parameter to substitute into the command string
        argument2 : numeric/string
            a parameter to substitute into the command string
    --------------------------------------------------------------------------
    returns : string
        a valid command that can be sent to the psu over RS232
    --------------------------------------------------------------------------
    """
    terminate = '\r\n'

    ##########################################################################
    # Language: Standard Commands for Programmable Instruments (SCPI)
    #
    # Note that front/rear terminal usage can only be set using the front
    # panel button
    dmm6500 = {
        'configure to read capacitance': (
            'dmm.measure.func=dmm.FUNC_CAPACITANCE;'
            'dmm.measure.autorange=dmm.ON'
        ),
        'configure to read ac current': (
            'dmm.measure.func=dmm.FUNC_AC_CURRENT;'
            'dmm.measure.autorange=dmm.ON'
        ),
        'configure to read dc current': (
            'dmm.measure.func=dmm.FUNC_DC_CURRENT;'
            'dmm.measure.autorange=dmm.ON'
        ),
        'configure to read resistance': (
            'dmm.measure.func=dmm.FUNC_RESISTANCE;'
            'dmm.measure.autorange=dmm.ON'
        ),
        # Auto range not available for this function.
        # This is just a placeholder, and will need proper configuration later.
        # See reference manual p.14-68 (p.786 in PDF).
        'configure to read temperature': (
            'dmm.measure.func=dmm.FUNC_TEMPERATURE;'
            'dmm.measure.unit=dmm.UNIT_CELSIUS'
        ),
        'configure to read ac voltage': (
            'dmm.measure.func=dmm.FUNC_AC_VOLTAGE;'
            'dmm.measure.unit=dmm.UNIT_VOLT;'
            'dmm.measure.autorange=dmm.ON'
        ),
        'configure to read dc voltage': (
            'dmm.measure.func=dmm.FUNC_DC_VOLTAGE;'
            'dmm.measure.unit=dmm.UNIT_VOLT;'
            'dmm.measure.autorange=dmm.ON'
        ),
        'identify': '*IDN?',
        'read value': 'print(dmm.measure.read())',
        'reset': 'dmm.reset()',
    }

    instructions = {
        'dmm6500': dmm6500,
    }

    # sanity checks
    first = instructions.get(model)
    assert first is not None, 'unrecognised model name'
    second = first.get(command)
    assert second is not None, 'unrecognised command'
    cmd_string = instructions[model][command]
    assert 'None' not in cmd_string, 'missing argument to function'

    return bytes(cmd_string + terminate, 'utf-8')
