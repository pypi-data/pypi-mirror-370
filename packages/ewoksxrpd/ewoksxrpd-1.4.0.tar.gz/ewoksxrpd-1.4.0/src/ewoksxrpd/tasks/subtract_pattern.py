import importlib.metadata
import logging
from pathlib import PosixPath

import h5py
import numpy
from ewoksdata.data.nexus import select_default_plot
from silx.io.url import DataUrl

from .data_access import TaskWithDataAccess
from .utils import pyfai_utils
from .utils.nexus_utils import IntegratedPattern
from .utils.nexus_utils import read_nexus_integrated_patterns

_logger = logging.getLogger(__name__)


def _can_substract_background(
    pattern: IntegratedPattern, background_pattern: IntegratedPattern
) -> bool:
    if pattern.radial_units != background_pattern.radial_units:
        return False

    return pattern.intensity.shape == background_pattern.intensity.shape


class SubtractBackgroundPattern(
    TaskWithDataAccess,
    input_names=["nxdata_url", "background_nxdata_url"],
    optional_input_names=["enabled", "background_factor"],
    output_names=["nxdata_url"],
):
    """
    Subtract an integrated pattern from patterns stored in NeXus and saves the result in a new NeXus process group

    .. code:

        I_pattern_corrected = I_pattern - (I_background_pattern * background_factor)
    """

    def run(self):
        if not self.get_input_value("enabled", True):
            _logger.info(
                f"Task {self.__class__.__qualname__} is disabled: no pattern was subtracted"
            )
            self.outputs.nxdata_url = self.inputs.nxdata_url
            return

        if not isinstance(self.inputs.background_nxdata_url, str):
            raise ValueError(
                f"background_nxdata_url should be a str. Got {type(self.inputs.background_nxdata_url)} instead."
            )
        background_nxdata_url = DataUrl(self.inputs.background_nxdata_url)

        # Using the same file for `background_nxdata_url` and `nxdata_url` raises a "File already open" error when opening `nxdata_url` below
        # As a quick fix, we set the same opening mode for both `open_h5item` for now
        with self.open_h5item(background_nxdata_url, mode="a") as background_nxdata:
            if not isinstance(background_nxdata, h5py.Group):
                raise TypeError(
                    f"{self.inputs.nxdata_url} should point towards a NXData Group."
                )
            background_patterns = list(
                read_nexus_integrated_patterns(background_nxdata)
            )
            background_pattern = background_patterns[0]

        with self.open_h5item(self.inputs.nxdata_url, mode="a") as nxdata:
            if not isinstance(nxdata, h5py.Group):
                raise TypeError(
                    f"{self.inputs.nxdata_url} should point towards a NXData Group."
                )

            subtracted_intensity = numpy.empty(
                nxdata["intensity"].shape, dtype=nxdata["intensity"].dtype
            )

            background_factor = float(self.get_input_value("background_factor", 1))
            background_intensity = background_pattern.intensity * background_factor

            pattern = None
            for i, pattern in enumerate(read_nexus_integrated_patterns(nxdata)):
                if not _can_substract_background(pattern, background_pattern):
                    raise ValueError(
                        f"Background pattern {background_pattern} is not compatible with data pattern {pattern}."
                    )

                subtracted_intensity[i] = pattern.intensity - background_intensity

            if pattern is None:
                raise ValueError(f"No integrated patterns in {nxdata.name}")

            integrated_process = nxdata.parent
            subtracted_process = integrated_process.parent.create_group(
                f"{PosixPath(integrated_process.name).stem}_subtracted"
            )
            subtracted_process.attrs["NX_class"] = "NXprocess"
            subtracted_process["program"] = "ewoksxrpd"
            subtracted_process["version"] = importlib.metadata.version("ewoksxrpd")

            config_group = subtracted_process.create_group("configuration")
            config_group["nxdata_url"] = self.inputs.nxdata_url
            config_group["background_nxdata_url"] = self.inputs.background_nxdata_url
            config_group["background_factor"] = background_factor

            output_nxdata = pyfai_utils.create_integration_results_nxdata(
                subtracted_process,
                subtracted_intensity.ndim,
                pattern.radial,
                f"{pattern.radial_name}_{pattern.radial_units}",
                None,
                "",
            )
            if "points" in nxdata:
                output_nxdata["points"] = h5py.SoftLink(nxdata["points"].name)
                axes = output_nxdata.attrs["axes"]
                output_nxdata.attrs["axes"] = ["points", *axes[1:]]
            output_nxdata.create_dataset("intensity", data=subtracted_intensity)
            output_nxdata.attrs["signal"] = "intensity"
            output_nxdata.create_dataset("background", data=background_intensity)

            select_default_plot(output_nxdata)

            self.outputs.nxdata_url = (
                f"{output_nxdata.file.filename}::{output_nxdata.name}"
            )
