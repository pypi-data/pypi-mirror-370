from typing import Dict, List, Mapping, Optional, Sequence, Tuple
from AnyQt import QtWidgets
from silx.gui.plot import ScatterView, PlotWidget
from ewoksdata.data import bliss

from ewoksxrpd.tasks.calibrate import CalibrateSingle
from ewoksxrpd.tasks.utils import data_utils
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui import plots
from ewoksxrpd.gui.forms import input_parameters_calibratesingle
from ewoksxrpd.gui.forms import output_parameters_calibratesingle
from ewoksxrpd.gui.forms import pack_geometry
from ewoksxrpd.gui.forms import unpack_geometry
from ewoksxrpd.gui.forms import unpack_enabled_geometry


__all__ = ["OWCalibrateSingle"]


class OWCalibrateSingle(OWTriggerWidget, ewokstaskclass=CalibrateSingle):
    name = "CalibrateSingle"
    description = "Single distance calibration"
    icon = "icons/widget.png"
    want_main_area = True

    def __init__(self, *args, **kwargs) -> None:
        self._tabs = QtWidgets.QTabWidget()
        self._show = {
            "input_rings": True,
            "output_rings": False,
            "detected_rings": False,
        }
        self._legends = dict()
        self._cache = dict()
        super().__init__(*args, **kwargs)

    def _init_forms(self):
        parameter_info = input_parameters_calibratesingle(
            self.get_default_input_values()
        )
        self._create_input_form(parameter_info)
        parameter_info = output_parameters_calibratesingle()
        self._create_output_form(parameter_info)

    def _init_control_area(self):
        super()._init_control_area()
        layout = self._get_control_layout()

        w = QtWidgets.QPushButton("Accept refined")
        layout.addWidget(w)
        w.released.connect(self._accept_refined_parameters)

        self._show_input_rings_widget = w = QtWidgets.QCheckBox("Guess rings")
        w.setChecked(self._show["input_rings"])
        layout.addWidget(w)
        w.released.connect(self._set_show_input_rings)

        self._show_output_rings_widget = w = QtWidgets.QCheckBox("Refined rings")
        w.setChecked(self._show["output_rings"])
        layout.addWidget(w)
        w.released.connect(self._set_show_output_rings)

        self._show_detected_rings_widget = w = QtWidgets.QCheckBox("Detected rings")
        w.setChecked(self._show["detected_rings"])
        layout.addWidget(w)
        w.released.connect(self._set_show_detected_rings)

    def _set_show_input_rings(self):
        self._show["input_rings"] = self._show_input_rings_widget.isChecked()
        self._refresh_non_form_input_widgets()

    def _set_show_output_rings(self):
        self._show["output_rings"] = self._show_output_rings_widget.isChecked()
        self._refresh_non_form_output_widgets()

    def _set_show_detected_rings(self):
        self._show["detected_rings"] = self._show_detected_rings_widget.isChecked()
        self._refresh_non_form_output_widgets()

    def _init_main_area(self):
        layout = self._get_main_layout()
        plot = ScatterView()
        w = plot.getPlotWidget()
        w.setGraphXLabel("Dim 2 (pixels)")
        w.setGraphYLabel("Dim 1 (pixels)")
        self._tabs.addTab(plot, "Image")
        layout.addWidget(self._tabs)
        super()._init_main_area()

    def _add_output_form_widget(self):
        self._tabs.addTab(self._output_form, "Refined Geometry")

    def _refresh_non_form_input_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_input_widgets()
            self._refresh_input_plots()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._refresh_output_plots()

    def _accept_refined_parameters(self):
        energy = self.get_task_output_value("energy")
        if energy:
            self.update_default_inputs(energy=energy)
        geometry = self.get_task_output_value("geometry")
        if geometry:
            self.update_default_inputs(geometry=dict(geometry))
        self._refresh_input_widgets()

    def _input_form_edited(self):
        super()._input_form_edited()
        fixed = [
            k for k, v in self._input_form.get_parameters_checked().items() if not v
        ]
        self.update_default_inputs(fixed=fixed)
        self._refresh_non_form_input_widgets()

    def _refresh_input_plots(self):
        if self.plot is None:
            return None
        inputs = self.get_task_input_values()
        self._update_image(inputs)
        self._update_input_rings(inputs)

    def _refresh_output_plots(self):
        if self.plot is None:
            return None
        outputs = self.get_task_output_values()
        self._update_detected_rings(outputs)
        inoutputs = {**self.get_task_input_values(), **outputs}
        self._update_output_rings(inoutputs)

    def _update_image(self, inputs):
        image = inputs.get("image")
        if isinstance(image, str):
            previous_image_url = self._cache.get("image")
            if previous_image_url == image:
                return
            self._cache["image"] = image
        self._remove_from_plot("image")
        if not data_utils.is_data(image):
            return
        image = bliss.get_image(image, retry_timeout=0)
        self._legends["image"] = [plots.plot_image(self.plot, image, legend="image")]

    def _update_input_rings(self, values):
        self._remove_from_plot("input_rings")
        if not self._show["input_rings"]:
            return
        self._legends["input_rings"] = self._update_theoretical_rings(values, "input")

    def _update_output_rings(self, values):
        self._remove_from_plot("output_rings")
        if not self._show["output_rings"]:
            return
        self._legends["output_rings"] = self._update_theoretical_rings(values, "output")

    def _update_theoretical_rings(self, values, legend) -> List[str]:
        energy = values.get("energy")
        geometry = values.get("geometry")
        detector = values.get("detector")
        detector_config = values.get("detector_config")
        calibrant = values.get("calibrant")
        max_rings = values.get("max_rings")
        if isinstance(max_rings, Sequence):
            max_rings = max_rings[-1]
        if not energy or not geometry or not detector or not calibrant:
            return list()
        geometry = data_utils.data_from_storage(geometry)
        return plots.plot_theoretical_rings(
            self.plot,
            detector,
            calibrant,
            energy,
            geometry,
            detector_config=detector_config,
            max_rings=max_rings,
            legend=legend,
        )

    def _update_detected_rings(self, values):
        self._remove_from_plot("detected_rings")
        if not self._show["detected_rings"]:
            return
        rings = values.get("rings")
        if not rings:
            return
        rings = data_utils.data_from_storage(rings)
        self._legends["detected_rings"] = plots.plot_detected_rings(self.plot, rings)

    def _remove_from_plot(self, name: str) -> None:
        legends = self._legends.pop(name, list())
        for legend in legends:
            self.plot.remove(legend=legend)

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

    @property
    def plot(self) -> Optional[PlotWidget]:
        if self._tabs.count() == 0:
            return None
        return self._tabs.widget(0).getPlotWidget()
