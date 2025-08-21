import os
from AnyQt import QtWidgets

from ewoksxrpd.tasks.ascii import SaveAsciiPattern1D
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_ascii


__all__ = ["OWSaveAsciiPattern1D"]


class OWSaveAsciiPattern1D(OWTriggerWidget, ewokstaskclass=SaveAsciiPattern1D):
    name = "SaveAsciiPattern1D"
    description = "Save a 1D diffraction pattern in ASCII format"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_ascii(self.get_default_input_values())
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        layout = self._get_main_layout()
        self._textedit = QtWidgets.QTextEdit()
        self._textedit.setReadOnly(True)
        layout.addWidget(self._textedit)
        super()._init_main_area()
        self._refresh_non_form_output_widgets()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._update_output_file()

    def _update_output_file(self):
        inputs = self.get_task_input_values()
        filename = inputs.get("filename")
        if not filename or not os.path.isfile(filename):
            self._textedit.clear()
            return

        with open(filename) as f:
            lines = list(f)

        self._textedit.setPlainText("".join(lines))
