from typing import List

import dataclasses
from dataclasses import dataclass


@dataclass
class GliderCommandResults:

    iter: int = None

    def _list_type_fields(self):
        return [f for f in dataclasses.fields(self) if f.name not in ['iter']]

    def extend(self, other):
        for f in self._list_type_fields():
            val = getattr(self, f.name)
            if val is None:
                val = []
                setattr(self, f.name, val)
            val.extend(getattr(other, f.name))

    def append(self, **kwargs):
        consumed = []
        for f in self._list_type_fields():
            if f.name not in kwargs:
                continue
            val = getattr(self, f.name)
            if val is None:
                val = []
                setattr(self, f.name, val)
            val.append(kwargs[f.name])
            consumed.append(f.name)
        if set(consumed) != set(kwargs.keys()):
            raise ValueError

@dataclass
class OptimizeAdcResults(GliderCommandResults):
    delayNs: List[int] = None
    position: List[int] = None
    adcSum: List[float] = None
    status: List[int] = None
    errors: List[str] = None
    cavity: List[int] = None


@dataclass
class SteppingPOIResults(GliderCommandResults):
    analog1AdcSum: List[float] = None
    analog2AdcSum: List[float] = None
    status: List[int] = None
    errors: List[str] = None
    wavenumber: List[float] = None
    acquiredPulsesNumber: List[int] = None
    cavity: List[int] = None
    laserDwellMs: List[int] = None
    postDwellMs: List[int] = None


@dataclass
class SteppingPOIResultWithAnalogBuffers(SteppingPOIResults):
    analog1BufferAddress: List[float] = None
    analog2BufferAddress: List[float] = None


@dataclass
class MockCommandResults(GliderCommandResults):
    myList: List[int] = None
