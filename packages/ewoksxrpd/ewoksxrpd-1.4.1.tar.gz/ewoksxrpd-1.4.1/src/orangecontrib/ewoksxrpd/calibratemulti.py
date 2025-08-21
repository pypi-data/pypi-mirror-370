from typing import Dict, Iterable, List, Mapping, Tuple
from AnyQt import QtWidgets
from silx.gui.plot import ScatterView, PlotWidget
from ewokscore.missing_data import is_missing_data
from ewoksdata.data import bliss

from ewoksxrpd.tasks.calibrate import CalibrateMulti
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui import plots
from ewoksxrpd.tasks.utils import data_utils
from ewoksxrpd.tasks.calibrate import calculate_geometry
from ewoksxrpd.gui.forms import input_parameters_calibratemulti
from ewoksxrpd.gui.forms import output_parameters_calibratemulti
from ewoksxrpd.gui.forms import pack_geometry
from ewoksxrpd.gui.forms import unpack_geometry
from ewoksxrpd.gui.forms import unpack_enabled_geometry
from ewoksxrpd.gui.forms import pack_parametrization
from ewoksxrpd.gui.forms import unpack_parametrization
from ewoksxrpd.gui.forms import unpack_enabled_parametrization

__all__ = ["OWCalibrateMulti"]


class OWCalibrateMulti(OWTriggerWidget, ewokstaskclass=CalibrateMulti):
    name = "CalibrateMulti"
    description = "Multi-distance calibration"
    icon = "icons/widget.png"
    want_main_area = True

    def __init__(self, *args, **kwargs) -> None:
        self._tabs = QtWidgets.QTabWidget()
        self._show = {
            "output_rings": True,
            "detected_rings": False,
        }
        self._legends = list()
        self._cache = list()
        self._fixed_tabs = 0
        super().__init__(*args, **kwargs)

    def _init_forms(self):
        parameter_info = input_parameters_calibratemulti(
            self.get_default_input_values()
        )
        self._create_input_form(parameter_info)
        parameter_info = output_parameters_calibratemulti()
        self._create_output_form(parameter_info)

    def _init_control_area(self):
        super()._init_control_area()
        layout = self._get_control_layout()

        w = QtWidgets.QPushButton("Accept refined")
        layout.addWidget(w)
        w.released.connect(self._accept_refined_parameters)

        self._show_output_rings_widget = w = QtWidgets.QCheckBox("Refined rings")
        w.setChecked(self._show["output_rings"])
        layout.addWidget(w)
        w.released.connect(self._set_show_output_rings)

        self._show_detected_rings_widget = w = QtWidgets.QCheckBox("Detected rings")
        w.setChecked(self._show["detected_rings"])
        layout.addWidget(w)
        w.released.connect(self._set_show_detected_rings)

    def _set_show_output_rings(self):
        self._show["output_rings"] = self._show_output_rings_widget.isChecked()
        self._refresh_non_form_output_widgets()

    def _set_show_detected_rings(self):
        self._show["detected_rings"] = self._show_detected_rings_widget.isChecked()
        self._refresh_non_form_output_widgets()

    def _init_main_area(self):
        layout = self._get_main_layout()
        layout.addWidget(self._tabs)
        self._fixed_tabs = 1
        self._tabs.addTab(self._output_form, "Parametrization")
        super()._init_main_area()
        self._refresh_non_form_input_widgets()
        self._refresh_non_form_output_widgets()

    def _add_output_form_widget(self):
        pass

    def _refresh_non_form_input_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_input_widgets()
            self._refresh_input_plots()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._refresh_output_plots()

    def _accept_refined_parameters(self):
        parametrization = self.get_task_output_value("parametrization")
        parameters = self.get_task_output_value("parameters")
        position = self.get_task_input_value("reference_position")
        if not parametrization or not parameters:
            return
        if is_missing_data(position):
            position = 0
        else:
            position = bliss.get_data(position, retry_timeout=0)
        parametrization = data_utils.data_from_storage(parametrization)
        parameters = data_utils.data_from_storage(parameters)
        geometry, energy = calculate_geometry(parametrization, parameters, position)
        self.update_default_inputs(energy=energy, geometry=geometry)
        self._refresh_input_widgets()

    def _input_form_edited(self):
        super()._input_form_edited()
        fixed = [
            k for k, v in self._input_form.get_parameters_checked().items() if not v
        ]
        self.update_default_inputs(fixed=fixed)
        self._refresh_non_form_input_widgets()

    def _refresh_input_plots(self):
        self._update_tabs()
        nplots = self._get_nplots()
        if not nplots:
            return None
        inputs = self.get_task_input_values()
        for plot_index in range(nplots):
            self._update_image(inputs, plot_index)

    def _refresh_output_plots(self):
        nplots = self._get_nplots()
        if not nplots:
            return None
        outputs = self.get_task_output_values()
        inoutputs = {**self.get_task_input_values(), **outputs}
        for plot_index in range(nplots):
            self._update_detected_rings(outputs, plot_index)
            self._update_output_rings(inoutputs, plot_index)

    def _update_image(self, inputs, plot_index):
        image = inputs["images"][plot_index]
        if isinstance(image, str):
            cache = self._cache[plot_index]
            previous_image_url = cache.get("image")
            if previous_image_url == image:
                return
            cache["image"] = image
        self._remove_from_plot("image", plot_index)
        if not data_utils.is_data(image):
            return
        image = bliss.get_image(image, retry_timeout=0)
        self._legends[plot_index]["image"] = [
            plots.plot_image(self._get_plot(plot_index), image, legend="image")
        ]

    def _update_output_rings(self, values, plot_index):
        self._remove_from_plot("output_rings", plot_index)
        if not self._show["output_rings"]:
            return
        self._legends[plot_index]["output_rings"] = self._update_theoretical_rings(
            values, "output", plot_index
        )

    def _update_theoretical_rings(self, values, legend, plot_index) -> List[str]:
        energy = values.get("energy")
        detector = values.get("detector")
        detector_config = values.get("detector_config")
        calibrant = values.get("calibrant")
        parametrization = values.get("parametrization")
        parameters = values.get("parameters")
        positions = values.get("positions")
        if (
            not energy
            or not detector
            or not calibrant
            or not parametrization
            or not parameters
            or not positions
        ):
            return
        position = bliss.get_data(positions[plot_index], retry_timeout=0)
        parametrization = data_utils.data_from_storage(parametrization)
        parameters = data_utils.data_from_storage(parameters)
        geometry, energy = calculate_geometry(parametrization, parameters, position)
        plot = self._get_plot(plot_index)
        return plots.plot_theoretical_rings(
            plot,
            detector,
            calibrant,
            energy,
            geometry,
            detector_config=detector_config,
            max_rings=None,
            legend=legend,
        )

    def _update_detected_rings(self, values, plot_index):
        self._remove_from_plot("detected_rings", plot_index)
        if not self._show["detected_rings"]:
            return
        rings = values.get("rings")
        if not rings:
            return
        rings = data_utils.data_from_storage(rings)
        plot = self._get_plot(plot_index)
        self._legends[plot_index]["detected_rings"] = plots.plot_detected_rings(
            plot, rings[str(plot_index)]
        )

    def _remove_from_plot(self, name: str, plot_index: int) -> None:
        legends = self._legends[plot_index].pop(name, list())
        if legends:
            plot = self._get_plot(plot_index)
            for legend in legends:
                plot.remove(legend=legend)

    def _values_from_form(
        self, values: Mapping, checked: Dict[str, bool], output: bool = False
    ) -> Mapping:
        values = pack_geometry(values, checked)
        if output:
            values = pack_parametrization(values)
        return values

    def _values_to_form(
        self, values: Mapping, output: bool = False
    ) -> Tuple[Mapping, Dict[str, bool]]:
        values, checked = unpack_geometry(values)
        if output:
            values = unpack_parametrization(values)
        return values, checked

    def _enabled_to_form(
        self, enabled: Dict[str, bool], output: bool = False
    ) -> Dict[str, bool]:
        enabled = unpack_enabled_geometry(enabled)
        if output:
            enabled = unpack_enabled_parametrization(enabled)
        return enabled

    def _get_nplots(self) -> Iterable[PlotWidget]:
        return self._tabs.count() - self._fixed_tabs

    def _get_plot(self, plot_index) -> PlotWidget:
        return self._tabs.widget(plot_index + self._fixed_tabs).getPlotWidget()

    def _update_tabs(self):
        images = self.get_task_input_value("images")
        if images:
            images = [data_utils.get_image(image, retry_timeout=0) for image in images]
            positions = self.get_task_input_value("positions")
            if positions:
                positions = [
                    data_utils.get_data(position, retry_timeout=0)
                    for position in positions
                ]
            else:
                positions = list()
            positions += [float("nan")] * max(len(images) - len(positions), 0)
        else:
            images = list()
            positions = list()

        xunits_in_m = self.get_task_input_value("positionunits_in_meter")  # xunits/m
        if not xunits_in_m:
            xunits_in_m = 1e-3  # xunits/m
        dunits_in_m = 1e-2  # dunits/m
        positions = [
            f"Position = {position*xunits_in_m/dunits_in_m:.06f} cm"
            for position in positions
        ]

        ntabs = self._tabs.count()
        nfixed = self._fixed_tabs
        nplots = ntabs - nfixed
        nadd = len(images) - nplots

        if nadd == 0:
            pass
        elif nadd > 0:
            for tab_index in range(ntabs, ntabs + nadd):
                plot_index = tab_index - nfixed
                self._tabs.addTab(ScatterView(), positions[plot_index])
                self._legends.append(dict())
                self._cache.append(dict())
        else:
            for tab_index in range(ntabs - 1, ntabs + nadd - 1, -1):
                plot_index = tab_index - nfixed
                self._tabs.removeTab(tab_index)
                del self._legends[plot_index]
                del self._cache[plot_index]

        for plot_index, position in enumerate(positions):
            tab_index = plot_index + nfixed
            self._tabs.setTabText(tab_index, position)
