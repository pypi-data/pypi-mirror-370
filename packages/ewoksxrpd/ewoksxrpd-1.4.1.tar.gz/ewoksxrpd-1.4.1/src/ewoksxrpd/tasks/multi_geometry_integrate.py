from ewoksdata.data.bliss import get_image
from typing import Tuple
from pyFAI.goniometer import Goniometer
from pyFAI.units import Unit
from .base_integrate import BaseIntegrate
from .utils import integrate_utils, pyfai_utils


class Integrate2DMultiGeometry(
    BaseIntegrate,
    input_names=["goniometer_file", "positions", "images"],
    output_names=[
        "info",
        "radial",
        "azimuthal",
        "intensity",
        "intensity_error",
        "radial_units",
        "azimuthal_units",
    ],
):
    def run(self):
        raw_integration_options = self._get_ewoks_pyfai_options()
        multi_geometry_options, integrate2d_options = (
            pyfai_utils.split_multi_geom_and_integration_options(
                raw_integration_options
            )
        )

        goniometer = Goniometer.sload(self.inputs.goniometer_file)
        mg_ai = goniometer.get_mg(self.inputs.positions, **multi_geometry_options)
        images = get_image(self.inputs.images)
        result = mg_ai.integrate2d(images, **integrate2d_options)

        self.outputs.radial = result.radial
        self.outputs.azimuthal = result.azimuthal
        self.outputs.intensity = result.intensity
        self.outputs.intensity_error = integrate_utils.get_intensity_error(result)

        result_unit: Tuple[Unit, Unit] = result.unit
        radial_unit, azim_unit = result_unit
        self.outputs.radial_units = radial_unit.name
        self.outputs.azimuthal_units = azim_unit.name

        self.outputs.info = pyfai_utils.compile_integration_info(
            raw_integration_options
        )
