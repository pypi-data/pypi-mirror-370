from ewoksorange.bindings import OWEwoksWidgetNoThread
from ewoksorange.gui.parameterform import ParameterForm
from ewoksxrpd.tasks.pyfaiconfig import SavePyFaiPoniFile


__all__ = ["OWSavePyFaiPoniFile"]


class OWSavePyFaiPoniFile(OWEwoksWidgetNoThread, ewokstaskclass=SavePyFaiPoniFile):
    name = "SavePyFaiPoniFile"
    description = "Save pyFAI PONI file"
    icon = "icons/widget.png"
    want_main_area = False

    def __init__(self):
        super().__init__()

        self._parameter_form = ParameterForm(parent=self.controlArea)
        self._parameter_form.addParameter(
            "output_filename",
            label="pyFAI PONI filename (*.poni)",
            value_for_type="",
            select="file",
            value_change_callback=self._inputs_changed,
        )
        self._update_parameter_values()

        self.controlArea.layout().addStretch(1)

    def _inputs_changed(self):
        new_values = self._parameter_form.get_parameter_values()
        self.update_default_inputs(**new_values)

    def _update_parameter_values(self):
        initial_values = self.get_default_input_values()
        self._parameter_form.set_parameter_values(initial_values)
