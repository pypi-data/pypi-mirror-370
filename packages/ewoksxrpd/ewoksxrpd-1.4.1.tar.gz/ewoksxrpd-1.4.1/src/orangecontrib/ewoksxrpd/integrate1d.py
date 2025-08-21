from typing import Dict, Mapping, Tuple
from silx.gui.plot import Plot1D

from ewoksxrpd.tasks.integrate import Integrate1D
from ewoksxrpd.tasks.utils import data_utils
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_integrate1d
from ewoksxrpd.gui.forms import pack_geometry
from ewoksxrpd.gui.forms import unpack_geometry
from ewoksxrpd.gui.forms import unpack_enabled_geometry

__all__ = ["OWIntegrate1D"]


class OWIntegrate1D(OWTriggerWidget, ewokstaskclass=Integrate1D):
    name = "Integrate1D"
    description = "DEPRECATED. Use IntegrateSinglePattern instead"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_integrate1d(self.get_default_input_values())
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        layout = self._get_main_layout()
        self._plot = Plot1D()
        layout.addWidget(self._plot)
        super()._init_main_area()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._update_plot()

    def _update_plot(self):
        self._plot.remove(kind="curve")

        outputs = self.get_task_output_values()
        x = outputs.get("x")
        y = outputs.get("y")
        xunits = outputs.get("xunits")
        if not xunits or not data_utils.is_data(x) or not data_utils.is_data(y):
            return

        inputs = self.get_task_input_values()
        reference = inputs.get("reference")
        self._plot.addCurve(x, y, xlabel=xunits, ylabel=f"Normalized to {reference}")

    def _values_from_form(
        self, values: Mapping, checked: Dict[str, bool], output: bool = False
    ) -> Mapping:
        return pack_geometry(values, checked)

    def _values_to_form(
        self, values: Mapping, output: bool = False
    ) -> Tuple[Mapping, Dict[str, bool]]:
        return unpack_geometry(values)

    def _enabled_to_form(
        self, enabled: Dict[str, bool], output: bool = False
    ) -> Dict[str, bool]:
        return unpack_enabled_geometry(enabled)
