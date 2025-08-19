from __future__ import annotations

from dataclasses import dataclass
from typing import Generator
from typing import Union

import h5py
import numpy
from silx.io.nxdata import NXdata


@dataclass
class IntegratedPattern:
    """Store one pyFAI integrated pattern"""

    point: Union[float, int, None]
    radial: numpy.ndarray
    radial_name: str
    radial_units: str
    intensity: numpy.ndarray
    intensity_errors: Union[numpy.ndarray, None]


def read_nexus_integrated_patterns(group: h5py.Group) -> Generator[IntegratedPattern]:
    """Read integrated patterns from a HDF5 NXdata group.

    It reads from both single (1D signal) or multi (2D signal) NXdata.
    """
    nxdata = NXdata(group)
    if not nxdata.is_valid:
        raise RuntimeError(
            f"Cannot parse NXdata group: {group.file.filename}::{group.name}"
        )
    if not (nxdata.signal_is_1d or nxdata.signal_is_2d):
        raise RuntimeError(
            f"Signal is not a 1D or 2D dataset: {group.file.filename}::{group.name}"
        )

    if nxdata.signal_is_1d:
        points = [None]
    else:  # 2d
        if nxdata.axes[0] is None:
            points = [None] * nxdata.signal.shape[0]
        else:
            points = nxdata.axes[0][()]

    if nxdata.axes[-1] is None:
        radial = numpy.arange(nxdata.signal.shape[1])
        radial_name = ""
        radial_units = ""
    else:
        radial_name = nxdata.axes_dataset_names[-1]
        axis_dataset = nxdata.axes[-1]
        radial = axis_dataset[()]
        radial_units = axis_dataset.attrs.get("units", "")

    intensities = numpy.atleast_2d(nxdata.signal)

    if nxdata.errors is None:
        errors = [None] * intensities.shape[0]
    else:
        errors = numpy.atleast_2d(nxdata.errors)

    if (len(points), len(radial)) != intensities.shape:
        raise RuntimeError("Shape mismatch between axes and signal")

    for point, intensity, intensity_errors in zip(points, intensities, errors):
        yield IntegratedPattern(
            point, radial, radial_name, radial_units, intensity, intensity_errors
        )
