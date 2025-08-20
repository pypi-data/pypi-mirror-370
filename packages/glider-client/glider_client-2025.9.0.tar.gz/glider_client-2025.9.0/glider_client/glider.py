# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import dataclasses
import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import List, Any, Dict
from time import time, sleep

import numpy
import requests

from glider_client.commands import GliderCommandDataset, InitializeDataset, SwitchLasingOffDataset, ClearErrorsDataset, \
    RESULTS_COMMANDS

logger = logging.getLogger(__name__)


class GliderRuntimeError(Exception):
    pass


class GliderTimeout(Exception):
    pass


class GliderProtocolError(Exception):
    pass


class GliderProfileConfigurationError(Exception):
    pass


GLI_STATUS_CONNECTING = 'CONNECTING'  # initial state
GLI_STATUS_REQUIRE_FW_UPGRADE = 'REQUIRE FIRMWARE UPGRADE'  # some sub-components require
GLI_STATUS_NOT_INITIALIZED = 'NOT INITIALIZED'  # some motors not initialized or temperature
GLI_STATUS_INITIALIZING = 'INITIALIZING'  # initialization command running
GLI_STATUS_INITIALIZED = 'INITIALIZED'  # motors powered on, temperature stable, not lasing
GLI_STATUS_LASING = 'LASING'  # some laser is on and some temperature is stable
GLI_STATUS_EXECUTING_LASING = 'EXECUTING LASING'  # INITIALIZED and command running
GLI_STATUS_SYSTEM_ERROR = 'SYSTEM ERROR'  # any of the sub-systems is in error state
GLI_STATUS_SYSTEM_EXCURSION = 'SYSTEM EXCURSION'
GLI_STATUS_INTERLOCKED = 'INTERLOCKED'
GLI_STATUS_COMMUNICATION_ERROR = 'COMMUNICATION ERROR'
GLI_STATUS_ANY = 'ANY OPERATIONAL STATUS'

GLI_LASING_STATUS_NOT = 'NOT LASING'
GLI_LASING_STATUS_INIT = 'INIT'
GLI_LASING_STATUS_ARMED = 'ARMED'


def get_glider_level_from_logging_level(logging_level):
    if logging_level <= logging.INFO:
        return LEVEL_INFO
    elif logging_level <= logging.WARNING:
        return LEVEL_WARNING
    else:
        return LEVEL_ERROR


LEVEL_SUCCESS = 'success'
LEVEL_INFO = 'info'
LEVEL_WARNING = 'warning'
LEVEL_ERROR = 'error'
LEVEL_SEVERITY = [LEVEL_ERROR, LEVEL_WARNING, LEVEL_INFO, LEVEL_SUCCESS]


class BitRegister:

    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def _get_bit(self, position):
        return bool(self._value & (1 << position))

    def get_user_msg(self):
        raise NotImplementedError

    def to_dict(self):
        rsp = OrderedDict()
        for a in dir(self):
            if a.startswith('_'):
                continue
            if a not in ['update', 'to_dict', 'get_value',
                         'get_user_msg', 'reset_parameters']:
                rsp[a] = getattr(self, a)
        return rsp

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return '<{}({}:{})>'.format(self.__class__.__name__,
                                    self._value,
                                    ', '.join(['{}={}'.format(k, v)
                                               for k, v in self.to_dict().items()]))


class SettableBitRegister(BitRegister):

    def _set_bit(self, position, value):
        if value:
            self._set_bit_true(position)
        else:
            self._set_bit_false(position)

    def _set_bit_true(self, position):
        self._value |= (1<<position)

    def _set_bit_false(self, position):
        self._value &= ~(1<<position)


def set_bit_register(br):
    return br.get_value()


class CmdParams1(SettableBitRegister):

    def reset_parameters(self):
        """Reset all, except for global parameters (as for instance debug_mode"""
        debug_mode = self.debugMode
        self._value = 0
        self.debugMode = debug_mode

    @property
    def debugMode(self):
        return self._get_bit(0)

    @debugMode.setter
    def debugMode(self, value):
        self._set_bit(0, value)

    @property
    def OUT9AsAnalog1AdcTrigger(self):
        """if this bit is set: OUT_9 on subD connector will output Analog 1 ADC Trigger, else, Process Output signal"""
        return self._get_bit(1)

    @OUT9AsAnalog1AdcTrigger.setter
    def OUT9AsAnalog1AdcTrigger(self, value):
        self._set_bit(1, value)

    @property
    def OUT8AsPositionRange(self):
        """if this bit is set: OUT_8 on subD connector will output DAC boundary signal, else, Tuned Output signal"""
        return self._get_bit(2)

    @OUT8AsPositionRange.setter
    def OUT8AsPositionRange(self, value):
        self._set_bit(2, value)

    @property
    def stageReversedCounting(self):
        """if this bit is set: reverse TIM2 encoder direction by setting sConfig.IC1Polarity = TIM_ICPOLARITY_FALLING;"""
        return self._get_bit(3)

    @stageReversedCounting.setter
    def stageReversedCounting(self, value):
        self._set_bit(3, value)


class S2StatusRegister(BitRegister):

    @property
    def hasErrors(self):
        return self._value != 0

    @property
    def isUnderVoltage(self):
        return self._get_bit(0)

    @property
    def isOverCurrent(self):
        return self._get_bit(1)

    @property
    def isOverVoltage(self):
        return self._get_bit(2)

    @property
    def isOverTemp(self):
        return self._get_bit(3)

    @property
    def isFastOverCurrent(self):
        return self._get_bit(4)

    @property
    def isOutOfPulseOverCurrent(self):
        return self._get_bit(5)

    @property
    def bootFailed(self):
        return self._get_bit(6)

    def to_user_message(self):
        if not self.hasErrors:
            return '{}: OK'.format(self.__class__.__name__)
        return '; '.join([k.replace('is', '') for k, v in self.to_dict().items()
                          if k not in ['hasErrors'] and v is True])


class ECErrorRegister(BitRegister):

    @property
    def hasErrors(self):
        return self._value != 0

    @property
    def initFail(self):
        return self._get_bit(0)

    @property
    def timeoutMotor(self):
        return self._get_bit(1)

    @property
    def positionOutOfBonds(self):
        return self._get_bit(2)

    @property
    def invalidParameters(self):
        return self._get_bit(3)

    @property
    def stopRequest(self):
        return self._get_bit(4)

    @property
    def pulseTimeout(self):
        return self._get_bit(5)

    @property
    def analog2AdcTimeout(self):  # analog 2 >>> adc1
        return self._get_bit(6)

    @property
    def analog1AdcTimeout(self):  # analog 1 >>> adc2
        return self._get_bit(7)

    @property
    def dmaTimeout(self):
        return self._get_bit(8)

    @property
    def uart1Timeout(self):
        return self._get_bit(9)

    @property
    def msmInvalidState(self):
        return self._get_bit(10)

    @property
    def registerOverflow(self):
        return self._get_bit(11)

    @property
    def analog1Clipping(self):
        return self._get_bit(12)

    @property
    def analog2Clipping(self):
        return self._get_bit(13)

    @property
    def outOfMemory(self):
        return self._get_bit(14)

    def get_user_msg(self):
        return ', '.join([str(error_name) for error_name, error_is_set in self.to_dict().items()
                          if error_is_set]) or 'ok'


class ECInterlocksRegister(BitRegister):

    @property
    def userInterlockActive(self):
        return self._get_bit(0)

    @property
    def physicalInterlockActive(self):
        return self._get_bit(1)

    @property
    def tecInterlockActive(self):
        return self._get_bit(2)


class OutsideCalibrationBounds(Exception):
    pass


class WavenumberOutsideCalibrationBounds(OutsideCalibrationBounds):
    pass


class AngleOutsideCalibrationBounds(OutsideCalibrationBounds):
    pass


MONOTONIC_INCREASING = 'increasing'
MONOTONIC_DECREASING = 'decreasing'
NOT_MONOTONIC = 'not monotonic'


def analyse_monotonicity(alist):
    if len(alist) <= 1:
        raise ValueError('Cannot determine monotonicity of a one element list')
    sign = 1
    if alist[1] < alist[0]:
        sign = -1
    if numpy.all(sign * numpy.diff(numpy.array(alist)) > 0):
        return MONOTONIC_INCREASING if sign > 0 else MONOTONIC_DECREASING
    return NOT_MONOTONIC


def interpolate(x, xp, fp):
    if xp[1] < xp[0]:
        return numpy.interp(x, numpy.flip(xp), numpy.flip(fp))
    return numpy.interp(x, xp, fp)


def get_calibration_errors(angle_deg, wavenumber_invcm, power_mW):
    errors = []
    try:
        if type(angle_deg) != list:
            errors.append('"angle_deg" shall be a list')
        if type(wavenumber_invcm) != list:
            errors.append('"wavenumber_invcm" shall be a list')
        if type(power_mW) != list:
            errors.append('"power_mW" shall be a list')
        if errors:
            return errors
        if not (len(angle_deg) == len(wavenumber_invcm) == len(power_mW)):
            errors.append('angle_deg, wavenumber_invcm and power_mW '
                          'columns must have the same size')
            return errors
        if len(angle_deg) <= 1:
            errors.append('calibration list has length {}, '
                          'expected at least 2 elements'.format(len(angle_deg)))
            return errors
        if analyse_monotonicity(angle_deg) == NOT_MONOTONIC:
            errors.append('calibration angles are not monotonic')
        if analyse_monotonicity(wavenumber_invcm) == NOT_MONOTONIC:
            errors.append('wavenumber are not monotonic')
        for c in power_mW:
            try:
                float(c)  # verify it's a float
            except ValueError:
                errors.append('power_mW shall be a list of float, got {}'.format(c)
                              )
                return errors
    except Exception as e:
        logger.exception(e, exc_info=1)
        errors.append(str(e))
    return errors


@dataclass
class GliderCavityProfile:
    index: int
    appliedVoltage: float
    currentLimit: float
    pulsePeriod: float
    pulseWidth: float
    temperature: float
    stage1Angle: float
    stage2Angle: float
    stage3Angle: float
    stage4Angle: float
    maxVoltage: float
    maxDutyCycle: float
    maxCurrent: float
    maxPulseWidth: float
    calibAnglesDeg: list = None
    calibWnInvCm: list = None
    calibPowerMW: list = None

    @property
    def pulsePeriodMCUExternalTriggerFactor(self):
        return 0.95

    def get_errors(self):
        errors = []
        if (self.calibAnglesDeg is not None or
                self.calibWnInvCm is not None or
                self.calibPowerMW is not None):
            errors.extend(get_calibration_errors(angle_deg=self.calibAnglesDeg,
                                                 wavenumber_invcm=self.calibWnInvCm,
                                                 power_mW=self.calibPowerMW))
        return errors

    def get_stage_angle(self, index):
        return getattr(self, 'stage{}Angle'.format(index))

    def is_wavenumber_within_bounds(self, wavenumber):
        return min(self.calibWnInvCm) <= wavenumber <= max(self.calibWnInvCm)

    def is_angle_within_bounds(self, angle):
        return min(self.calibAnglesDeg) <= angle <= max(self.calibAnglesDeg)

    def get_angle_from_wavenumber(self, wavenumber):
        if not self.is_wavenumber_within_bounds(wavenumber):
            raise WavenumberOutsideCalibrationBounds('wavenumber {} outside of '
                                                     'calibration bounds for cavity {}'.format(wavenumber,
                                                                                               self.index))
        return interpolate(numpy.array(wavenumber),
                           numpy.array(self.calibWnInvCm),
                           numpy.array(self.calibAnglesDeg))

    def get_power_from_wavenumber(self, wavenumber):
        if not self.is_wavenumber_within_bounds(wavenumber):
            raise WavenumberOutsideCalibrationBounds('wavenumber {} outside of '
                                                     'calibration bounds for cavity {}'.format(wavenumber,
                                                                                               self.index))
        return interpolate(numpy.array(wavenumber),
                           numpy.array(self.calibWnInvCm),
                           numpy.array(self.calibPowerMW))

    def get_wavenumber_from_angle(self, angle):
        if not self.is_angle_within_bounds(angle):
            raise AngleOutsideCalibrationBounds
        return interpolate(numpy.array(angle),
                           numpy.array(self.calibAnglesDeg),
                           numpy.array(self.calibWnInvCm))

    def get_angle_tolerance_from_wavenumber_tolerance(self,
                                                      wavenumber_tolerance,
                                                      wavenumber_list):
        wavenumber_list = [w for w in wavenumber_list if
                           self.is_wavenumber_within_bounds(w + wavenumber_tolerance / 2.0)
                           and self.is_wavenumber_within_bounds(w - wavenumber_tolerance / 2.0)]
        if not wavenumber_list:
            raise ValueError('Cannot determine motor tolerance from '
                             'the provided wavenumbers and wavenumber tolerance: '
                             'all of them are out of calibration bounds')
        angles_minus = interpolate(numpy.array(wavenumber_list) - wavenumber_tolerance / 2.0,
                                   numpy.array(self.calibWnInvCm),
                                   numpy.array(self.calibAnglesDeg))
        angles_plus = interpolate(numpy.array(wavenumber_list) + wavenumber_tolerance / 2.0,
                                  numpy.array(self.calibWnInvCm),
                                  numpy.array(self.calibAnglesDeg))
        return numpy.max(numpy.abs(angles_plus - angles_minus))


@dataclass
class GliderProfile:
    number: int
    cavityProfiles: Dict[int, GliderCavityProfile] = None

    def get_cavity_and_angle_for_wavenumber(self, wavenumber):
        """Returns best cavity for a given wavenumber, where the best cavity
        is the one which gives the higher power
        """
        candidates = [c for c in self.cavityProfiles.values()
                      if c.is_wavenumber_within_bounds(wavenumber)]
        if not candidates:
            raise WavenumberOutsideCalibrationBounds('wavenumber {} outside '
                                                     'of calibration bounds'.format(wavenumber))
        c = sorted(candidates,
                   key=lambda x: x.get_power_from_wavenumber(wavenumber))[-1]
        return c, c.get_angle_from_wavenumber(wavenumber)

    def get_cavity_profile(self, index):
        if index not in self.cavityProfiles:
            raise ValueError('profile for cavity {} not defined'.format(index))
        return self.cavityProfiles[index]


@dataclass
class BoardConfig:
    usbSerial: str
    devPathTemplate: str
    checkVersions: bool

    def _get_device_path(self, interface):
        return self.devPathTemplate.format(self.usbSerial, interface)


@dataclass
class CavityConfig(BoardConfig):
    index: int
    stageAxis: int
    laserSerial: str
    stageReversedCounting: bool
    pgaDeltaDelay2xNs: int
    pgaDeltaDelay4xNs: int
    pgaDeltaDelay8xNs: int
    pgaDeltaDelay16xNs: int

    @property
    def stagePath(self):
        return self._get_device_path('00')

    @property
    def s2Path(self):
        return self._get_device_path('01')

    @property
    def mcuPath(self):
        return self._get_device_path('02')

    @property
    def tecPath(self):
        return self._get_device_path('03')


@dataclass
class AlignConfig(BoardConfig):

    stage1ReversedCounting: bool
    stage2ReversedCounting: bool
    stage3ReversedCounting: bool
    stage4ReversedCounting: bool

    def get_stage_path(self, index):
        return self._get_device_path('0{}'.format(index - 1))

    def get_stage_reversed_counting(self, index):
        return getattr(self, 'stage{}ReversedCounting'.format(index))


@dataclass
class GliderConfig:
    cavitiesNumber: int = None
    serial: int = None
    cavities: Dict[int, CavityConfig] = None
    align: AlignConfig = None
    profiles: Dict[int, GliderProfile] = None
    version: str = None
    forcePhysicalInterlockActive: bool = False

    def get_cavity_config(self, index) -> CavityConfig:
        return self.cavities[index]

    def get_profile(self, number=None):
        if not self.profiles:
            raise GliderProfileConfigurationError('No glider profiles are configured.')
        if number is None:
            if len(self.profiles) != 1:
                raise GliderProfileConfigurationError('More than one profile configured, '
                                 'please specify profile number')
            return list(self.profiles.values())[0]
        return self.profiles[number]


@dataclass
class UserMessage:
    message: str = None
    level: str = None


@dataclass
class DeviceStatus:
    driverPath: str = None
    driverPathExists: bool = None
    lastCommunicationError: str = None
    requiresUpgrade: bool = None
    isRunning: bool = None
    connectionOK: bool = None
    hasCommunicationErrors: bool = None
    userMessage: UserMessage = None

    @property
    def hasErrors(self):
        return False


@dataclass
class S2Status(DeviceStatus):
    measuredVoltage: float = None
    measuredCurrent: float = None
    pulsePeriod: float = None
    pulseWidth: float = None
    dutyCycle: float = None
    appliedVoltage: float = None
    currentLimit: float = None
    pulsingMode: float = None
    statusRegister: S2StatusRegister = None
    maxVoltage: float = None
    maxDutyCycle: float = None
    maxCurrent: float = None
    maxPulseWidth: float = None
    externalTriggerPulseRepetitions: int = None

    @property
    def isLasing(self):
        return self.pulsingMode != 'off'

    @property
    def hasErrors(self):
        if self.statusRegister:
            return self.statusRegister.hasErrors
        return False


@dataclass
class StageStatus(DeviceStatus):
    driverSerialNumber: str = None
    actualAngle: float = None
    commandAngle: float = None
    motionErrorRegister: Any = None
    statusRegisterLow: Any = None
    statusRegisterHigh: Any = None

    @property
    def isInitialized(self):
        if self.statusRegisterLow:
            if self.statusRegisterLow.isAxisOn is True:
                return True
        return False


    @property
    def hasErrors(self):
        if self.motionErrorRegister:
            return self.motionErrorRegister.hasErrors
        return False

@dataclass
class MCUStatus(DeviceStatus):
    status: str = None
    command: str = None
    mode: str = None
    numberPOI: int = None
    numberAcquisitionsPerPOI: int = None
    POITolerance: int = None
    ecError: ECErrorRegister = None
    machineStatus: str = None
    isActiveEc: bool = None
    currentPOI: int = None
    encoderPosition: int = None
    encoderAngle: float = None
    interlockStatus: ECInterlocksRegister = None
    externalModeTimeout: int = None
    temperature: float = None
    humidity: float = None
    encoderDACMin: int = None
    encoderDACMax: int = None
    cmdParams1: CmdParams1 = None

    @property
    def hasErrors(self):
        if self.ecError:
            return self.ecError.hasErrors

    @property
    def allInterlocksActive(self):
        return (self.interlockStatus.userInterlockActive and
                self.interlockStatus.physicalInterlockActive)


@dataclass
class TECStatus(DeviceStatus):
    measuredTemperature: float = None
    sinkTemperature: float = None
    targetTemperature: float = None
    tecVoltage: float = None
    tecCurrent: float = None
    isStable: bool = None
    isOutputEnabled: bool = None
    status: int = None
    statusLabel: str = None
    hasError: bool = None
    errorNumber: int = None

    def is_temperature_stable(self, temperature):
        if ((not self.hasErrors)
                and self.isOutputEnabled
                and self.isStable):
            if self.targetTemperature == temperature:
                return True
        return False

    @property
    def hasErrors(self):
        return self.status == 3  # almetec.parameters.STATUS_ERROR


@dataclass
class AlignStatus:
    stage1Status: StageStatus = None
    stage2Status: StageStatus = None
    stage3Status: StageStatus = None
    stage4Status: StageStatus = None

    @property
    def hasSubStates(self):
        return self.stage1Status and self.stage2Status and self.stage3Status and self.stage4Status

    @property
    def connectionOK(self):
        if self.hasSubStates:
            return (self.stage1Status.connectionOK and
                    self.stage2Status.connectionOK and
                    self.stage3Status.connectionOK and
                    self.stage4Status.connectionOK)

    @property
    def requiresUpgrade(self):
        if self.hasSubStates:
            return (self.stage1Status.requiresUpgrade or
                    self.stage2Status.requiresUpgrade or
                    self.stage3Status.requiresUpgrade or
                    self.stage4Status.requiresUpgrade)

    @property
    def hasErrors(self):
        if self.hasSubStates:
            return (self.stage1Status.hasErrors or
                    self.stage2Status.hasErrors or
                    self.stage3Status.hasErrors or
                    self.stage4Status.hasErrors)

    @property
    def hasCommunicationErrors(self):
        if self.hasSubStates:
            return (self.stage1Status.hasCommunicationErrors or
                    self.stage2Status.hasCommunicationErrors or
                    self.stage3Status.hasCommunicationErrors or
                    self.stage4Status.hasCommunicationErrors)

    @property
    def isInitialized(self):
        if self.hasSubStates:
            return (self.stage1Status.isInitialized and
                    self.stage2Status.isInitialized and
                    self.stage3Status.isInitialized and
                    self.stage4Status.isInitialized)


@dataclass
class CavityStatus:
    s2: S2Status = None
    stage: StageStatus = None
    mcu: MCUStatus = None
    tec: TECStatus = None

    @property
    def isTECOn(self):
        if self.tec:
            return self.tec.isOutputEnabled
        return False

    @property
    def isStageInitialized(self):
        if self.stage:
            return self.stage.isInitialized
        return False

    @property
    def allInterlocksActive(self):
        if self.mcu:
            return self.mcu.allInterlocksActive
        return False

    @property
    def connectionOK(self):
        if self.hasSubStates:
            return (self.s2.connectionOK and
                    self.stage.connectionOK and
                    self.mcu.connectionOK and
                    self.tec.connectionOK)

    @property
    def requiresUpgrade(self):
        if self.hasSubStates:
            return (self.s2.requiresUpgrade or
                    self.stage.requiresUpgrade or
                    self.mcu.requiresUpgrade or
                    self.tec.requiresUpgrade)

    @property
    def hasErrors(self):
        if self.hasSubStates:
            return (self.s2.hasErrors or
                    self.stage.hasErrors or
                    self.mcu.hasErrors or
                    self.tec.hasErrors)

    @property
    def hasCommunicationErrors(self):
        if self.hasSubStates:
            return (self.s2.hasCommunicationErrors or
                    self.stage.hasCommunicationErrors or
                    self.mcu.hasCommunicationErrors or
                    self.tec.hasCommunicationErrors)

    @property
    def hasSubStates(self):
        return self.s2 and self.stage and self.mcu and self.tec

    @property
    def isLasing(self):
        if self.s2:
            return self.s2.isLasing

    @property
    def isTecOn(self):
        if self.tec:
            return self.tec.isOutputEnabled


@dataclass
class GliderCommandMessage:
    level: str
    message: str


@dataclass
class GliderCommandStatus:
    level: str = None
    messages: List[GliderCommandMessage] = None
    exception: Any = None
    name: str = None
    response: Any = None
    id: str = None
    parameters: None = None
    isExecuting: bool = False
    hasExecuted: bool = False
    result: None = None
    results: List = None
    results_num: int = None
    progress: int = 0

    @classmethod
    def from_dict(cls, mydict, DataSetKlass):
        rsp = cls()
        rsp.level = mydict['level']
        rsp.exception = mydict['exception']
        rsp.name = mydict['name']
        rsp.response = mydict['response']
        rsp.id = mydict['id']
        rsp.parameters = DataSetKlass(**mydict['parameters'])
        rsp.isExecuting = mydict['isExecuting']
        rsp.hasExecuted = mydict['hasExecuted']
        rsp.result = rsp.parameters.get_results_klass()(**mydict['result'])
        rsp.results_num = mydict['results_num']
        rsp.progress = mydict['progress']
        rsp.messages=[GliderCommandMessage(**m) for m in mydict['messages']]
        return rsp

    def add_message(self, message, level=logging.INFO):
        glider_level = get_glider_level_from_logging_level(level)
        self.messages.append(GliderCommandMessage(level=level,
                                                  message=message))
        if not self.level:
            self.level = glider_level
        else:
            if LEVEL_SEVERITY.index(glider_level) < LEVEL_SEVERITY.index(self.level):
                self.level = glider_level


@dataclass
class SystemExcursionEvent:
    time: float
    msg: str



SYSTEM_EXCURSION_EVENT_INTERLOCK_USER = 'user interlock'
SYSTEM_EXCURSION_EVENT_INTERLOCK_PHYSICAL = 'physical interlock'
SYSTEM_EXCURSION_EVENT_INTERLOCK_TEC = 'tec interlock'


SYSTEM_EXCURSION_EVENTS = [SYSTEM_EXCURSION_EVENT_INTERLOCK_PHYSICAL,
                           SYSTEM_EXCURSION_EVENT_INTERLOCK_USER,
                           SYSTEM_EXCURSION_EVENT_INTERLOCK_TEC]



@dataclass
class GliderStatus:
    cavities: Dict[int, CavityStatus] = None
    align: AlignStatus = None
    config: GliderConfig = None
    isCommandRunning: bool = None
    isRunning: bool = None
    isConfigured: bool = None
    selectedProfile: int = None
    outputWavenumber: float = None
    hasSystemExcursionEvents: bool = False
    _operationalStatus: str = None

    @classmethod
    def from_dict(cls, mydict):
        operational_status = mydict['operationalStatus'] if 'operationalStatus' in mydict else mydict['_operationalStatus']
        glider_status = cls(cavities={},
                  isCommandRunning=mydict['isCommandRunning'],
                  isRunning=mydict['isRunning'],
                  isConfigured=mydict['isConfigured'],
                  selectedProfile=mydict['selectedProfile'],
                  outputWavenumber=mydict['outputWavenumber'],
                  _operationalStatus=operational_status)
        for k, v in mydict['cavities'].items():
            cavity_status = CavityStatus()
            glider_status.cavities[int(k)] = cavity_status
            cavity_status.s2 = S2Status(**v['s2'])
            cavity_status.stage = StageStatus(**v['stage'])
            cavity_status.mcu = MCUStatus(**v['mcu'])
            cavity_status.tec = TECStatus(**v['tec'])
        if mydict['align']:
            glider_status.align = AlignStatus(stage1Status=StageStatus(**mydict['align']['stage1Status']),
                                           stage2Status=StageStatus(**mydict['align']['stage2Status']),
                                           stage3Status=StageStatus(**mydict['align']['stage3Status']),
                                           stage4Status=StageStatus(**mydict['align']['stage4Status']))
        glider_status.config = GliderConfig(cavitiesNumber=mydict['config']['cavitiesNumber'],
                                         serial=mydict['config']['serial'],
                                         version=mydict['config']['version'],
                                         cavities={},
                                         profiles={})
        if mydict['config']['align']:
            glider_status.config.align = AlignConfig(**mydict['config']['align'])
        for k, v in mydict['config']['cavities'].items():
            glider_status.config.cavities[int(k)] = CavityConfig(**v)
        for profile_number, profile_values in mydict['config']['profiles'].items():
            profile = GliderProfile(number=profile_values['number'],
                                    cavityProfiles={})
            for cavity_index, cavity_profile_values in profile_values['cavityProfiles'].items():
                profile.cavityProfiles[int(cavity_index)] = GliderCavityProfile(**cavity_profile_values)
            glider_status.config.profiles[int(profile_number)] = profile
        return glider_status

    @property
    def connectionOK(self):
        if self.align and not self.align.connectionOK:
            return False
        for c in self.cavities.values():
            if not c.connectionOK:
                return False
        return True

    def get_profile(self):
        return self.config.get_profile(number=self.selectedProfile)

    @property
    def isAnyTECOn(self):
        for c in self.cavities.values():
            if c.isTECOn:
                return True
        return False

    @property
    def isTemperatureStable(self):
        profile = self.get_profile()
        for cavity_index, cavity in self.cavities.items():
            cavity_profile = profile.get_cavity_profile(cavity_index)
            if not cavity.tec.is_temperature_stable(cavity_profile.temperature):
                return False
        return True

    @property
    def requiresUpgrade(self):
        if self.align and self.align.requiresUpgrade:
            return True
        for c in self.cavities.values():
            if c.requiresUpgrade:
                return True
        return False

    @property
    def hasSubStates(self):
        if self.align and not self.align.hasSubStates:
            return False
        for c in self.cavities.values():
            if not c.hasSubStates:
                return False
        return True

    @property
    def hasErrors(self):
        if self.align and self.align.hasErrors:
            return True
        for c in self.cavities.values():
            if c.hasErrors:
                return True
        return False

    @property
    def hasCommunicationErrors(self):
        if self.align and self.align.hasCommunicationErrors:
            return True
        for c in self.cavities.values():
            if c.hasCommunicationErrors:
                return True
        return False

    @property
    def allInterlocksActive(self):
        for c in self.cavities.values():
            if not c.allInterlocksActive:
                return False
        return True

    @property
    def isShutDown(self):
        if self.align and self.align.isInitialized:
            return False
        for c in self.cavities.values():
            if c.isStageInitialized:
                return False
            if c.isLasing:
                return False
            if c.isTecOn:
                return False
        return True

    @property
    def isInitialized(self):
        if self.align and not self.align.isInitialized:
            return False
        for c in self.cavities.values():
            if not c.isStageInitialized:
                return False
        if not self.isTemperatureStable:
            return False
        return True

    @property
    def isLasing(self):
        for c in self.cavities.values():
            if c.isLasing:
                return True
        return False

    @property
    def lasingStatus(self):
        if self.operationalStatus == GLI_STATUS_INITIALIZING:
            return GLI_LASING_STATUS_INIT
        if self.isAnyTECOn:
            return GLI_LASING_STATUS_ARMED
        return GLI_LASING_STATUS_NOT

    @property
    def operationalStatus(self):
        if self._operationalStatus:
            return self._operationalStatus
        if not self.hasSubStates:
            return GLI_STATUS_CONNECTING
        if self.connectionOK:
            if self.requiresUpgrade:
                return GLI_STATUS_REQUIRE_FW_UPGRADE
            if self.hasErrors:
                return GLI_STATUS_SYSTEM_ERROR
            if self.hasSystemExcursionEvents:
                return GLI_STATUS_SYSTEM_EXCURSION
            if not self.allInterlocksActive:
                return GLI_STATUS_INTERLOCKED
            if self.isInitialized:
                if self.isLasing:
                    if self.isCommandRunning:
                        return GLI_STATUS_EXECUTING_LASING
                    return GLI_STATUS_LASING
                return GLI_STATUS_INITIALIZED
            else:
                if self.isCommandRunning:
                    return GLI_STATUS_INITIALIZING
                return GLI_STATUS_NOT_INITIALIZED
        else:
            if self.hasCommunicationErrors:
                return GLI_STATUS_COMMUNICATION_ERROR
            return GLI_STATUS_CONNECTING


class GliderCommandProxy:

    status = GliderCommandStatus

    def __init__(self, glider, command_id, dataset):
        self.id = command_id
        self.status = None
        self.glider = glider
        self.dataset = dataset

    def update(self):
        rsp = requests.get('{}/api/command'.format(self.glider.url))
        rsp.raise_for_status()
        status = rsp.json()
        if status['id'] != self.id:
            raise Exception('the current running command ID does not '
                            'match the local ID: {} != {}'.format(status['id'],
                                                                  self.id))
        self.status = GliderCommandStatus.from_dict(status,
                                                    DataSetKlass=self.dataset.__class__)

    def _check_status_loaded(self):
        if not self.status:
            raise Exception('status object not loaded, call update()')

    @property
    def hasErrors(self):
        self._check_status_loaded()
        return self.status.level == 'error'

    @property
    def errorMessage(self):
        self._check_status_loaded()
        return self.status.exception

    def stop(self):
        rsp = requests.post('{}/api/command/stop'.format(self.glider.url))
        rsp.raise_for_status()

    @property
    def isExecuting(self):
        self._check_status_loaded()
        return self.status.isExecuting

    @property
    def hasExecuted(self):
        self._check_status_loaded()
        return self.status.hasExecuted

    @property
    def result(self):
        self._check_status_loaded()
        return self.status.result


class Glider:

    def __init__(self, hostname='localhost', port=5000,
                 is_mock=False):
        self._hostname = hostname
        self._port = port
        self.isMock = is_mock
        self.testPhysicalInterlock = None
        self.testUserInterlock = None
        self.testController = None

    @property
    def url(self):
        return 'http://{}:{}'.format(self._hostname, self._port)

    def get_status(self) -> GliderStatus:
        rsp = requests.get('{}/api/status'.format(self.url))
        rsp.raise_for_status()
        return GliderStatus.from_dict(mydict=rsp.json())

    def initialize(self, active_cavity_index=1, timeout=3*60):
        start_time = time()
        status = self.get_status()
        if status.operationalStatus == GLI_STATUS_SYSTEM_ERROR:
            self.clear_errors()
        if status.operationalStatus in [GLI_STATUS_INITIALIZED, GLI_STATUS_LASING, GLI_STATUS_EXECUTING_LASING]:
            return
        self.execute_command(command_dataset=
                                   InitializeDataset(
                                       cavity_index=active_cavity_index),
                                 timeout=timeout)

        while True:
            status = self.get_status()
            if status.operationalStatus in [GLI_STATUS_INITIALIZED, GLI_STATUS_LASING, GLI_STATUS_EXECUTING_LASING]:
                return
            if time() - start_time > timeout:
                raise GliderTimeout('current status is {}'.format(status.operationalStatus))
            sleep(0.1)

    def wait_idle(self, timeout=2):
        start_time = time()
        while time() - start_time < timeout:
            current_status = self.get_status()
            if not current_status.isCommandRunning:
                return
        raise GliderTimeout

    def wait_status(self, target_op_status, timeout=2):
        start_time = time()
        while time() - start_time < timeout:
            current_status = self.get_status()
            if current_status.operationalStatus == target_op_status:
                return
        current_status = self.get_status()
        current_op_status = current_status.operationalStatus
        if current_op_status != target_op_status:
            raise GliderTimeout('glider current state is {}, but {} was expected'.format(current_op_status,
                                                                                        target_op_status))

    def switch_lasing_off(self):
        self.execute_command(command_dataset=SwitchLasingOffDataset())

    def clear_errors(self):
        self.execute_command(command_dataset=ClearErrorsDataset())

    def execute_command(self, command_dataset: GliderCommandDataset, timeout=3*60) -> GliderCommandProxy:
        command_proxy = None
        try:
            command_proxy = self.execute_command_async(command_dataset=command_dataset)
            start_time = time()
            while True:
                if time() - start_time > timeout:
                    raise GliderTimeout
                command_proxy.update()
                if command_proxy.hasExecuted:
                    break
                sleep(0.1)
            command_proxy.update()
            if command_proxy.hasErrors:
                raise GliderRuntimeError(command_proxy.errorMessage)
            return command_proxy
        finally:
            if command_proxy:
                command_proxy.stop()

    def execute_command_async(self, command_dataset: GliderCommandDataset) -> GliderCommandProxy:
        rsp = requests.post('{}/api/command'.format(self.url),
                            params={'command': command_dataset.get_command_name()},
                            json={'parameters': dataclasses.asdict(command_dataset)})
        rsp.raise_for_status()
        msg = rsp.json()
        if msg['level'] == 'error':
            raise GliderRuntimeError(msg['message'])
        return GliderCommandProxy(command_id=msg['command_id'],
                                  glider=self,
                                  dataset=command_dataset)

    def get_last_command_with_results(self):
        rsp = requests.get('{}/api/command/last_result'.format(self.url))
        rsp.raise_for_status()
        return GliderCommandStatus.from_dict(mydict=rsp.json(),
                                             DataSetKlass=RESULTS_COMMANDS[rsp.json()['name']])

    def get_results(self, command_status, result_indexes):
        rsp = requests.get('{}/api/results/{}'.format(self.url,
                                                              command_status.id),
                           params={'ids': result_indexes})
        rsp.raise_for_status()
        return [command_status.parameters.get_results_klass()(**r) for r in rsp.json()]