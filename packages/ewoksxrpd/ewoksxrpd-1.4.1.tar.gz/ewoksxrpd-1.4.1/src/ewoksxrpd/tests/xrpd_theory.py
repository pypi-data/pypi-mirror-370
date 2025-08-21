from typing import Any, Optional
from dataclasses import dataclass, field

import numpy
import pyFAI.units
import pyFAI.calibrant
from numpy.typing import ArrayLike

from .. import pyfai_api


@dataclass(frozen=True)
class RadialPattern:
    x: ArrayLike = field(repr=False)
    low_limit: float
    high_limit: float
    units: str

    @property
    def integration_options(self) -> dict:
        return {
            "radial_range_min": self.low_limit,
            "radial_range_max": self.high_limit,
            "nbpt_rad": self.x.size,
            "unit": self.units,
        }


@dataclass(frozen=True)
class AzimuthalPattern:
    x: ArrayLike = field(repr=False)
    low_limit: float
    high_limit: float
    units: str = "chi_deg"

    @property
    def integration_options(self) -> dict:
        return {
            "azimuth_range_min": self.low_limit,
            "azimuth_range_max": self.high_limit,
            "nbpt_azim": self.x.size,
        }


@dataclass(frozen=True)
class IntensityPattern:
    y: ArrayLike = field(repr=False)
    monitor: float
    theory: Any


@dataclass(frozen=True)
class Measurement:
    image: ArrayLike = field(repr=False)
    monitor: float


@dataclass(frozen=True)
class Calibration:
    image: ArrayLike = field(repr=False)
    calibrant: str


@dataclass(frozen=True)
class Setup:
    version: Optional[int]
    detector: str
    energy: float  # keV
    geometry: dict

    @property
    def wavelength(self) -> float:  # Angstrom
        return pyFAI.units.hc / (self.energy * 1e10)

    @property
    def detector_config(self) -> dict:
        return {}

    def load_detector_config(self) -> dict:
        detector_object = pyFAI.detectors.detector_factory(self.detector)
        return detector_object.get_config()

    @property
    def integration_options(self) -> dict:
        if not self.version:
            return {}
        return {"version": self.version}


def calibration(
    name: str, ai: pyfai_api.AzimuthalIntegrator, setup: Setup
) -> Calibration:
    calibrant = pyFAI.calibrant.get_calibrant(name)
    calibrant.set_wavelength(setup.wavelength)
    # W = FWHM^2 in rad
    FWHM = 0.2  # deg
    W = numpy.radians(FWHM) ** 2
    image = calibrant.fake_calibration_image(ai, Imax=100, W=W)
    return Calibration(image=image, calibrant=name)


def measurement(
    ai: pyfai_api.AzimuthalIntegrator,
    xpattern,
    ypattern,
    mult=2,
):
    x = xpattern.x
    y = mult * ypattern.y
    monitor = mult * ypattern.monitor
    image = ai.calcfrom1d(x, y, dim1_unit=xpattern.units, mask=ai.mask)
    return Measurement(image=image, monitor=monitor)


def measurement2d(
    ai: pyfai_api.AzimuthalIntegrator,
    radial: RadialPattern,
    azimuthal: AzimuthalPattern,
    intensity: IntensityPattern,
):
    image = ai.calcfrom2d(
        intensity.y,
        radial.x,
        azimuthal.x,
        dim1_unit=radial.units,
        dim2_unit=azimuthal.units,
        mask=ai.mask,
    )
    return Measurement(image=image, monitor=intensity.monitor)
