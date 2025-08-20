from collections import OrderedDict
from typing import List

from pydantic import model_validator, ConfigDict
from pydantic.dataclasses import dataclass

from glider_client.command_results import GliderCommandResults, OptimizeAdcResults, SteppingPOIResults, \
    SteppingPOIResultWithAnalogBuffers, MockCommandResults
from glider_client.utils.mcu_registers import ANALOG_CHANNEL1, ANALOG_CHANNEL2, ADC_SAMPLING_TIME_DICT_INV, \
    ADC_SAMPLING_TIMES

from glider_client.utils.re import CamelCase_to_snake_case


@dataclass
class GliderCommandDataset:

    @classmethod
    def from_dict(cls, mydict):
        return cls(**mydict)

    def get_results_klass(self):
        return GliderCommandResults

    @classmethod
    def get_command_name(cls):
        return CamelCase_to_snake_case(cls.__name__).replace('_dataset', '')

    __pydantic_config__ = ConfigDict(extra='forbid')


@dataclass
class AdminSetSettingsDataset(GliderCommandDataset):
    cavity_index: int | None
    pulsing_mode: str| None = None
    applied_voltage: float | None = None
    pulse_period: float | None = None
    pulse_width: float | None = None
    current_limit: float | None = None
    stage_angle: float | None = None
    temperature: int | None = None
    pga1_gain: str | None = None
    pga2_gain: str | None = None
    max_current: float | None = None
    max_voltage: float | None = None
    max_duty_cycle: float | None = None
    max_pulse_width: float | None = None
    external_trigger_pulse_repetitions: int | None = None
    out_width: float | None = None   # at present not used, but xc_testing requires it
    duty_cycle: float | None = None  # at present not used, but xc_testing requires it


@dataclass
class AdminMoveAlignMirrorDataset(GliderCommandDataset):
    align_index: int | None
    stage_angle: float | None


@dataclass
class AdminMoveAlignMirrorsDataset(GliderCommandDataset):
    stage1_angle: float | None
    stage2_angle: float | None
    stage3_angle: float | None
    stage4_angle: float | None


@dataclass
class AdminSmartAlignDataset(GliderCommandDataset):
    step: float | None
    mode: str


@dataclass
class AdminUpdateProfileDataset(GliderCommandDataset):
    cavity_index: int
    set_stage_angles: bool = None
    max_current: float | None = None
    max_voltage: float | None = None
    max_duty_cycle: float | None = None
    max_pulse_width: int | None = None
    applied_voltage: float | None = None
    current_limit: float | None = None
    pulse_period: int | None = None
    pulse_width: int | None = None
    temperature: float | None = None
    calibration: str = None
    preview: bool = False


@dataclass
class InitializeDataset(GliderCommandDataset):
    cavity_index : int


def _check_adc_parameters(sampling_time_ns, oversampling, oversampling_shift,
                          channel_name):
    if sampling_time_ns not in ADC_SAMPLING_TIME_DICT_INV:
        raise ValueError('analog{}_sampling_time_ns shall be on of {}, '
                         'but {} was given'.format(channel_name,
                                                   ADC_SAMPLING_TIMES,
                                                   sampling_time_ns))
    if not 1 <= oversampling <= 1024:
        raise ValueError('analog{}_oversampling must be an integer between 1 and 1024, '
                         'but {} was given'.format(channel_name,
                                                   oversampling))
    if not 0 <= oversampling_shift <= 11:
        raise ValueError('analog{}_oversampling_shift must be an integer between 0 and 11, '
                         'but {} was given'.format(channel_name, oversampling_shift))


PGA_GAIN_1X = '1x'
PGA_GAIN_2X = '2x'
PGA_GAIN_4X = '4x'
PGA_GAIN_8X = '8x'
PGA_GAIN_16X = '16x'
MASK_REG_POI1_PGA_GAIN_ANALOG1 = 0x0007 # 0000 0000 0000 0111
MASK_REG_POI1_PGA_GAIN_ANALOG2 = 0x0038 # 0000 0000 0011 1000
PGA_GAIN = OrderedDict({PGA_GAIN_1X: 4,
                        PGA_GAIN_2X: 0,
                        PGA_GAIN_4X: 1,
                        PGA_GAIN_8X: 2,
                        PGA_GAIN_16X: 3,})


def is_valid_pga(pga: int):
    return pga in PGA_GAIN.values()


@dataclass
class OptimizeAdcDataset(GliderCommandDataset):
    wavenumber: float
    tuned_window_invcm: float
    stable_time_in_poi_ms: int
    adc_scan_size_us: int
    adc_step_size_ns: int
    adc_oversampling: int
    adc_oversampling_shift: int
    adc_sampling_time_ns: int
    analog_channel: int
    adc_start_time_ns: int = 0
    analog_pga: int = PGA_GAIN[PGA_GAIN_1X]

    def get_results_klass(self):
        return OptimizeAdcResults

    @model_validator(mode='after')
    def validate(self):
        if self.analog_channel not in [ANALOG_CHANNEL1, ANALOG_CHANNEL2]:
            raise ValueError('analog_channel must be one of {}, '
                             'but {} was give'.format([ANALOG_CHANNEL1, ANALOG_CHANNEL2],
                                                      self.analog_channel))
        _check_adc_parameters(sampling_time_ns=self.adc_sampling_time_ns,
                              oversampling=self.adc_oversampling,
                              oversampling_shift=self.adc_oversampling_shift,
                              channel_name='analog channel {}'.format(self.analog_channel))
        if not is_valid_pga(self.analog_pga):
            raise ValueError('analog_pga must be one of {}, but {} was given'.format(PGA_GAIN.values(),
                                                                                      self.analog_pga))


@dataclass
class SetProfileDataset(GliderCommandDataset):
    number: int


@dataclass
class ShutDownDataset(GliderCommandDataset):
    pass


STEPPING_POI_S2_TRIGGER_MODE_INT_BURST = 'internal_burst'
STEPPING_POI_S2_TRIGGER_MODE_INT_CONTINUOUS = 'internal_continuous'
STEPPING_POI_S2_TRIGGER_MODE_EXT = 'external'

STEPPING_POI_S2_TRIGGER_MODES = [STEPPING_POI_S2_TRIGGER_MODE_INT_BURST,
                                 STEPPING_POI_S2_TRIGGER_MODE_INT_CONTINUOUS,
                                 STEPPING_POI_S2_TRIGGER_MODE_EXT]


@dataclass
class SteppingPoiDataset(GliderCommandDataset):
    poi: List
    tuned_window_invcm: float
    stable_time_in_poi_ms: int
    use_analog1 : bool
    use_analog2 : bool
    analog1_delay_s2m_trigger_ns: int
    analog1_oversampling: int
    analog1_oversampling_shift: int
    analog1_sampling_time_ns: int
    analog2_delay_s2m_trigger_ns: int
    analog2_oversampling: int
    analog2_oversampling_shift: int
    analog2_sampling_time_ns: int
    s2_trigger_mode: str = STEPPING_POI_S2_TRIGGER_MODE_INT_BURST
    s2_external_trigger_timeout_ms: int | None = None
    include_analog_adc_buffers: bool = False
    repetitions: int = 1

    @classmethod
    def from_dict(cls, mydict):
        from glider.drivers.mcu import McuPOI
        rsp = cls(**mydict)
        rsp.poi = [McuPOI(**m) for m in rsp.poi]
        return rsp

    def get_results_klass(self):
        if not self.include_analog_adc_buffers:
            return SteppingPOIResults
        else:
            return SteppingPOIResultWithAnalogBuffers

    @model_validator(mode='after')
    def validate(self):
        if (not self.use_analog1) and (not self.use_analog2):
            raise ValueError('Either use_analog1 or use_analog2 shall be True, or both, '
                             'but both where set to False')
        if self.use_analog1:
            _check_adc_parameters(self.analog2_sampling_time_ns, self.analog2_oversampling,
                                  self.analog2_oversampling_shift, channel_name=1)
        if self.use_analog2:
            _check_adc_parameters(self.analog2_sampling_time_ns, self.analog2_oversampling,
                                  self.analog2_oversampling_shift, channel_name=2)


@dataclass
class SetWavenumberDataset(GliderCommandDataset):
    wavenumber: float
    pulsing_mode: str = 'internal'
    external_trigger_pulse_repetitions: int = 0
    calibrate_mcu_stage_position: bool = True


@dataclass
class MockCommandDataset(GliderCommandDataset):
    parameter: float | None = None
    raise_exception_while_executing: bool = False
    raise_exception_while_initializing: bool = False
    mcu_error_state: int = 0

    def get_results_klass(self):
        return MockCommandResults


@dataclass
class SwitchLasingOffDataset(GliderCommandDataset):
    pass


@dataclass
class ClearErrorsDataset(GliderCommandDataset):
    pass


@dataclass
class ClearEventsDataset(GliderCommandDataset):
    pass


RESULTS_COMMANDS = {'stepping_poi': SteppingPoiDataset,
                    'optimize_adc': OptimizeAdcDataset,
                    'mock_command': MockCommandDataset}


