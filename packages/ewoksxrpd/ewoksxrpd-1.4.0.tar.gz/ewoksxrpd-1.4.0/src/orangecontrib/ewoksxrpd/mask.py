import numpy
from AnyQt import QtWidgets
from silx.gui.plot import Plot2D
from ewoksdata.data import bliss

from ewoksxrpd.tasks.mask import MaskDetection
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.tasks.utils import data_utils
from ewoksxrpd.gui.forms import input_parameters_mask


__all__ = ["OWMaskDetection"]


class OWMaskDetection(OWTriggerWidget, ewokstaskclass=MaskDetection):
    name = "MaskDetection"
    description = "Detect 'bad' detector pixels"
    icon = "icons/widget.png"
    want_main_area = True

    def __init__(self, *args, **kwargs) -> None:
        self._tabs = QtWidgets.QTabWidget()
        super().__init__(*args, **kwargs)

    def _init_forms(self):
        parameter_info = input_parameters_mask(self.get_default_input_values())
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        layout = self._get_main_layout()
        layout.addWidget(self._tabs)
        for name in ("Image 1", "Image 2", "Ratio"):
            self._tabs.addTab(Plot2D(), name)
        super()._init_main_area()

    def _refresh_non_form_input_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_input_widgets()
            self._refresh_mixed_plots()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._refresh_mixed_plots()

    def _refresh_mixed_plots(self):
        if self._tabs.count() == 0:
            return
        inputs = self.get_task_input_values()
        outputs = self.get_task_output_values()
        self._update_image(0, inputs, outputs)
        self._update_image(1, inputs, outputs)
        self._update_ratio(inputs, outputs)

    def _update_image(self, idx, inputs, outputs):
        plot = self._tabs.widget(idx)
        plot.remove(kind="image")

        image = inputs.get(f"image{idx+1}")
        if not data_utils.is_data(image):
            return
        plot.addImage(bliss.get_image(image, retry_timeout=0))

        mask = outputs.get("mask")
        if not data_utils.is_data(mask):
            return
        plot.setSelectionMask(mask)

    def _update_ratio(self, inputs, outputs):
        plot = self._tabs.widget(2)
        plot.remove(kind="image")
        monitor1 = inputs.get("monitor1")
        monitor2 = inputs.get("monitor2")
        image1 = inputs.get("image1")
        image2 = inputs.get("image2")
        if (
            not monitor1
            or not monitor2
            or not data_utils.is_data(image1)
            or not data_utils.is_data(image2)
        ):
            return
        image1 = bliss.get_image(image1, retry_timeout=0)
        image2 = bliss.get_image(image2, retry_timeout=0)
        monitor1 = bliss.get_data(monitor1, retry_timeout=0)
        monitor2 = bliss.get_data(monitor2, retry_timeout=0)
        with numpy.errstate(divide="ignore", invalid="ignore"):
            if monitor2 > monitor1:
                ratio = image2 / image1
            else:
                ratio = image1 / image2
        plot.addImage(ratio)
        mask = outputs.get("mask")
        if not data_utils.is_data(mask):
            return
        plot.setSelectionMask(mask)
