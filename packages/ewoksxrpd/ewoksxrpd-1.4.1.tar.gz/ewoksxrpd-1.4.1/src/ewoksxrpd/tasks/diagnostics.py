import os
import warnings
from numbers import Number
from contextlib import contextmanager

import numpy
import matplotlib
from numpy.typing import ArrayLike

try:
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm, LogNorm
except ModuleNotFoundError:
    plt = SymLogNorm = LogNorm = None

import pyFAI

from .utils import data_utils
from .utils import xrpd_utils
from .utils import pyfai_utils
from .calibrate import calculate_geometry
from .data_access import TaskWithDataAccess
from ..pyfai_api import AzimuthalIntegrator

__all__ = [
    "DiagnoseCalibrateSingleResults",
    "DiagnoseCalibrateMultiResults",
    "DiagnoseIntegrate1D",
]


class _DiagnoseTask(
    TaskWithDataAccess,
    optional_input_names=["show", "pause", "filename", "figsize", "dpi", "fontsize"],
    output_names=["saved"],
    register=False,
):
    def prepare(self):
        matplotlib.rc("font", size=self.get_input_value("fontsize", 22))

    def show(self):
        if self.inputs.show:
            if self.inputs.pause and numpy.isfinite(self.inputs.pause):
                plt.pause(self.inputs.pause)
            else:
                plt.show()
        if self.inputs.filename:
            path = os.path.dirname(self.inputs.filename)
            if path:
                os.makedirs(path, exist_ok=True)
            plt.gcf().savefig(
                self.inputs.filename, dpi=self.get_input_value("dpi", 150)
            )
            self.outputs.saved = True
        else:
            self.outputs.saved = False
        plt.close()


class _DiagnoseCalibrateResults(
    _DiagnoseTask,
    input_names=["detector", "calibrant"],
    optional_input_names=["detector_config", "scaling"],
    register=False,
):
    def plot_calibration(
        self,
        ax1,
        ax2,
        image: ArrayLike,
        control_pts: dict,
        geometry: dict,
        energy: Number,
        title=None,
    ):
        scaling = self.get_input_value("scaling", "symlog").lower()
        if scaling == "symlog":
            colornorm = SymLogNorm(
                1,
                base=10,
                vmin=numpy.nanmin(image),
                vmax=numpy.nanmax(image),
            )
        elif scaling == "log":
            colornorm = LogNorm(
                vmin=numpy.nanmin(image),
                vmax=numpy.nanmax(image),
            )

        if title:
            title = f"{title}: "
        else:
            title = ""

        self.prepare()
        ax1.imshow(image, origin="lower", cmap="inferno", norm=colornorm)
        ax1.set_title(f"{title}Rings")
        if control_pts:
            ax2.imshow(image, origin="lower", cmap="inferno", norm=colornorm)
            ax2.set_title(f"{title}Control points")

        # Calibrant rings on 2D pattern
        detector = data_utils.data_from_storage(self.inputs.detector)
        detector_config = data_utils.data_from_storage(
            self.get_input_value("detector_config", None)
        )
        detector_object = pyFAI.detectors.detector_factory(
            detector, config=detector_config
        )
        calibrant = data_utils.data_from_storage(self.inputs.calibrant)
        calibrant_object = pyFAI.calibrant.get_calibrant(calibrant)
        wavelength = xrpd_utils.energy_wavelength(energy)
        ai = AzimuthalIntegrator(
            detector=detector_object, **geometry, wavelength=wavelength
        )
        calibrant_object.set_wavelength(wavelength)
        tth = calibrant_object.get_2th()
        ttha = ai.twoThetaArray()
        ax1.contour(
            ttha, levels=tth, cmap="autumn", linewidths=1
        )  # linestyles="dashed"

        # Detected points on 2D pattern
        for label, points in control_pts.items():
            ax2.scatter(points["p1"], points["p0"], label=label, marker=".")

    def show(self):
        # Diagnose
        # plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
        plt.tight_layout()
        super().show()


class DiagnoseCalibrateSingleResults(
    _DiagnoseCalibrateResults,
    input_names=["image", "geometry", "energy"],
    optional_input_names=["rings"],
):
    """Quality of a single-distance pyFAI calibration"""

    def run(self):
        if self.inputs.filename:
            if os.path.exists(self.inputs.filename):
                self.outputs.saved = True
                return
        if plt is None:
            raise RuntimeError("'matplotlib' is not installed")

        self.prepare()
        rings = self.inputs.rings
        figsize = self.get_input_value("figsize", (16, 8))
        if rings:
            with _ignore_mpl_thread_warning():
                _, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=figsize)
        else:
            rings = dict()
            with _ignore_mpl_thread_warning():
                _, ax1 = plt.subplots(nrows=1, ncols=1, figsize=figsize)
            ax2 = None

        self.plot_calibration(
            ax1,
            ax2,
            self.get_image(self.inputs.image),
            data_utils.data_from_storage(rings),
            data_utils.data_from_storage(self.inputs.geometry),
            self.inputs.energy,
        )
        self.show()


class DiagnoseCalibrateMultiResults(
    _DiagnoseCalibrateResults,
    input_names=[
        "images",
        "positions",
        "parametrization",
        "parameters",
    ],
    optional_input_names=["show", "pause", "rings"],
):
    """Quality of a multi-distance pyFAI calibration"""

    def run(self):
        if self.inputs.filename:
            if os.path.exists(self.inputs.filename):
                self.outputs.saved = True
                return
        if plt is None:
            raise RuntimeError("'matplotlib' is not installed")
        nimages = len(self.inputs.images)
        rings = self.inputs.rings
        figsize = self.get_input_value("figsize", (16, 8))
        figsize = (figsize[0], figsize[1] * nimages)
        if rings:
            rings = {int(k): v for k, v in rings.items()}
            with _ignore_mpl_thread_warning():
                _, axes = plt.subplots(nrows=nimages, ncols=2, figsize=figsize)
        else:
            rings = {i: dict() for i in range(nimages)}
            with _ignore_mpl_thread_warning():
                _, axes = plt.subplots(
                    nrows=nimages, ncols=1, figsize=(10, 10 * nimages)
                )
            axes = [(ax1, None) for ax1 in axes]

        for image, position, ringsi, (ax1, ax2) in zip(
            self.inputs.images, self.inputs.positions, sorted(rings), axes
        ):
            image = self.get_image(image)
            position = self.get_data(position)
            title = f"position={position}"
            parametrization = data_utils.data_from_storage(self.inputs.parametrization)
            geometry, energy = calculate_geometry(
                parametrization, self.inputs.parameters, position
            )
            control_pts = data_utils.data_from_storage(rings[ringsi])
            self.plot_calibration(
                ax1, ax2, image, control_pts, geometry, energy, title=title
            )
        self.show()


class DiagnoseIntegrate1D(
    _DiagnoseTask,
    input_names=[
        "x",
        "y",
        "xunits",
    ],
    optional_input_names=["calibrant", "energy", "yerror", "scaling"],
):
    """Quality of a pyFAI integration"""

    def run(self):
        if self.inputs.filename:
            if os.path.exists(self.inputs.filename):
                self.outputs.saved = True
                return
        if plt is None:
            raise RuntimeError("'matplotlib' is not installed")
        with _ignore_mpl_thread_warning():
            plt.figure(figsize=(16, 8))
        plt.title("Diffractogram")

        scaling = self.get_input_value("scaling", "squareroot").lower()
        if self.missing_inputs.yerror:
            plt.plot(self.inputs.x, self.inputs.y)
        else:
            yerr = numpy.minimum(3 * self.inputs.y, self.inputs.yerror)
            plt.errorbar(self.inputs.x, self.inputs.y, yerr=yerr)

        plt.yscale(scaling)
        xaxis = pyfai_utils.parse_string_units(self.inputs.xunits)
        plt.xlabel(f"{xaxis.name} ({xaxis.units})")
        plt.ylabel("Intensity")
        if self.inputs.calibrant:
            assert self.inputs.energy, "'energy' task parameter is missing"
            self.plot_calibrant_lines()
        self.show()

    def plot_calibrant_lines(self):
        calibrant = data_utils.data_from_storage(self.inputs.calibrant)
        calibrant = pyFAI.calibrant.get_calibrant(calibrant)
        wavelength = xrpd_utils.energy_wavelength(self.inputs.energy)
        calibrant.set_wavelength(wavelength)

        xvalues = calibrant.get_peaks(unit=self.inputs.xunits)
        mask = (xvalues >= min(self.inputs.x)) & (xvalues <= max(self.inputs.x))
        xvalues = xvalues[mask]
        if xvalues.size:
            yvalues = numpy.interp(xvalues, self.inputs.x, self.inputs.y)
            labels = xrpd_utils.calibrant_ring_labels(calibrant)
            labels = numpy.array(labels[: mask.size])[mask]
            ymin = min(self.inputs.y)
            for label, x, ymax in zip(labels, xvalues, yvalues):
                plt.plot([x, x], [ymin, ymax])
                # plt.text(x, ymax, label)


@contextmanager
def _ignore_mpl_thread_warning():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Starting a Matplotlib GUI outside of the main thread will likely fail.",
            category=UserWarning,
        )
        yield
