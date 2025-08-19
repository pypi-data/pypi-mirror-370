from numbers import Number
from typing import List
import numpy
from numpy.typing import ArrayLike

from silx.gui.colors import Colormap
from silx.gui.plot import PlotWidget
from silx.image.marchingsquares import find_contours
import pyFAI
import pyFAI.detectors

from ..pyfai_api import AzimuthalIntegrator
from ..tasks.utils.xrpd_utils import energy_wavelength


def plot_image(plot: PlotWidget, image: ArrayLike, **kwargs) -> str:
    return plot.addImage(image, **kwargs)


def plot_theoretical_rings(
    plot: PlotWidget,
    detector: str,
    calibrant: str,
    energy: Number,
    geometry: dict,
    detector_config=None,
    max_rings=None,
    legend=None,
    **kwargs,
) -> List[str]:
    """Plot theoretical and detected Debye rings"""
    detector_object = pyFAI.detectors.detector_factory(detector, config=detector_config)
    mask = detector_object.mask
    wavelength = energy_wavelength(energy)
    ai = AzimuthalIntegrator(
        detector=detector_object, **geometry, wavelength=wavelength
    )
    calibrant_object = pyFAI.calibrant.get_calibrant(calibrant)
    calibrant_object.set_wavelength(wavelength)

    levels = calibrant_object.get_2th()
    if max_rings:
        if max_rings < 0:
            max_rings = None
    else:
        max_rings = None
    if max_rings:
        levels = levels[:max_rings]
    image = ai.twoThetaArray()
    legends = list()
    if not legend:
        legend = "theory"
    for i, level in enumerate(levels):
        polygons = find_contours(image, level, mask=mask)
        color = None
        for j, polygon in enumerate(polygons):
            x = polygon[:, 1] + 0.5
            y = polygon[:, 0] + 0.5
            s = plot.addCurve(
                x=x,
                y=y,
                legend=f"{legend}-{i}-{j}",
                linestyle="-",
                resetzoom=False,
                color=color,
                **kwargs,
            )
            legends.append(s)
            if j == 0:
                color = plot.getCurve(s).getColor()
    return legends


def plot_detected_rings(
    plot: PlotWidget, rings: dict, legend=None, **kwargs
) -> List[str]:
    legends = list()
    if not legend:
        legend = "detected"
    cm = Colormap(name="jet", normalization="linear", vmin=0, vmax=len(rings))
    for value, (label, points) in enumerate(rings.items()):
        value = numpy.full_like(points["p1"], value * 100)
        legend = plot.addScatter(
            points["p1"],
            points["p0"],
            value,
            legend=f"{legend}_{label}",
            symbol=".",
            colormap=cm,
            **kwargs,
        )
        legends.append(legend)
    return legends
