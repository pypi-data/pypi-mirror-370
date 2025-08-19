from AnyQt import QtWidgets
from silx.gui.plot import Plot2D
from ewoksdata.data import bliss

from ewoksxrpd.tasks.background import SubtractBackground
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.tasks.utils import data_utils
from ewoksxrpd.gui.forms import input_parameters_background


__all__ = ["OWSubtractBackground"]


class OWSubtractBackground(OWTriggerWidget, ewokstaskclass=SubtractBackground):
    name = "SubtractBackground"
    description = "Subtract background in 2D"
    icon = "icons/widget.png"
    want_main_area = True

    def __init__(self, *args, **kwargs) -> None:
        self._tabs = QtWidgets.QTabWidget()
        super().__init__(*args, **kwargs)

    def _init_forms(self):
        parameter_info = input_parameters_background(self.get_default_input_values())
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        layout = self._get_main_layout()
        layout.addWidget(self._tabs)
        for name in ("Image", "Background", "Subtracted"):
            self._tabs.addTab(Plot2D(), name)
        super()._init_main_area()

    def _refresh_non_form_input_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_input_widgets()
            self._refresh_input_plots()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._refresh_output_plots()

    def _refresh_input_plots(self):
        if self._tabs.count() == 0:
            return
        inputs = self.get_task_input_values()
        self._update_image(inputs)
        self._update_background(inputs)

    def _refresh_output_plots(self):
        if self._tabs.count() == 0:
            return
        outputs = self.get_task_output_values()
        self._update_subtracted(outputs)

    def _update_image(self, inputs):
        plot = self._tabs.widget(0)
        plot.remove(kind="image")
        image = inputs.get("image")
        if data_utils.is_data(image):
            plot.addImage(bliss.get_image(image, retry_timeout=0))

    def _update_background(self, inputs):
        plot = self._tabs.widget(1)
        plot.remove(kind="image")
        image = inputs.get("background")
        if data_utils.is_data(image):
            plot.addImage(bliss.get_image(image, retry_timeout=0))

    def _update_subtracted(self, outputs):
        plot = self._tabs.widget(2)
        plot.remove(kind="image")
        image = outputs.get("image")
        if data_utils.is_data(image):
            plot.addImage(bliss.get_image(image, retry_timeout=0))
