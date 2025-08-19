from typing import Dict, Mapping, Tuple
from silx.gui.plot import Plot2D
from silx.gui.widgets.FrameBrowser import HorizontalSliderWithBrowser

from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_integrateblissscan
from ewoksxrpd.gui.forms import pack_geometry
from ewoksxrpd.gui.forms import unpack_geometry
from ewoksxrpd.gui.forms import unpack_enabled_geometry
from ewoksxrpd.tasks.integrate import IntegrateBlissScanWithoutSaving
from ewoksxrpd.tasks.utils import data_utils


__all__ = ["OWIntegrateBlissScanNoSave"]


class OWIntegrateBlissScanNoSave(
    OWTriggerWidget, ewokstaskclass=IntegrateBlissScanWithoutSaving
):
    name = "IntegrateBlissScanWithoutSaving"
    description = "1D or 2D integrate data from one detector of a single Bliss scan"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_integrateblissscan(
            self.get_default_input_values(), saving=False
        )
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        super()._init_main_area()

        layout = self._get_main_layout()
        self._plot = Plot2D(parent=self.mainArea)
        layout.addWidget(self._plot)
        self._slider = HorizontalSliderWithBrowser(parent=self.mainArea)
        layout.addWidget(self._slider)
        self._slider.valueChanged[int].connect(self._select_output_image)
        self._plot_data = None

    def _refresh_non_form_output_widgets(self):
        outputs = self.get_task_output_values()
        data = outputs.get("intensity")
        if not data_utils.is_data(data):
            self._plot_data = None
            return
        self._plot_data = data_utils.convert_to_3d(data)
        self._slider.setMaximum(max(len(self._plot_data) - 1, 0))
        self._select_output_image(self._slider.value())

    def _select_output_image(self, select: int):
        if self._plot_data is not None:
            self._plot.addImage(self._plot_data[select], legend="image")

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
