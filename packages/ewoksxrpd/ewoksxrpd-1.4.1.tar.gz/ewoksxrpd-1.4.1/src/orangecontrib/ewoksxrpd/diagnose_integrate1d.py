from ewoksxrpd.tasks.diagnostics import DiagnoseIntegrate1D
from ewoksxrpd.gui.image_viewer import ImageViewer
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_diagnose_integrate1d


__all__ = ["OWDiagnoseIntegrate1D"]


class OWDiagnoseIntegrate1D(OWTriggerWidget, ewokstaskclass=DiagnoseIntegrate1D):
    name = "DiagnoseIntegrate1D"
    description = "Diagnose 1D integration of a single diffraction pattern"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_diagnose_integrate1d(
            self.get_default_input_values()
        )
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        layout = self._get_main_layout()
        self._image_viewer = ImageViewer()
        layout.addWidget(self._image_viewer)
        super()._init_main_area()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._update_output_file()

    def _update_output_file(self):
        filename = self.get_task_input_value("filename")
        self._image_viewer.load_image(filename)
