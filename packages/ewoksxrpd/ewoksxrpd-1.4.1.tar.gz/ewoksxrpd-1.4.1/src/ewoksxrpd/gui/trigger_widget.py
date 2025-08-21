from contextlib import contextmanager
import logging
from typing import Dict, Mapping, Optional, Tuple
from AnyQt import QtWidgets
from ewoksorange.bindings import OWEwoksWidgetOneThread
from ewoksorange.bindings import ow_build_opts
from ewoksorange.gui.parameterform import ParameterForm


logger = logging.getLogger(__name__)


class OWTriggerWidget(OWEwoksWidgetOneThread, **ow_build_opts):
    def __init__(self, *args, **kwargs) -> None:
        self._input_form: Optional[ParameterForm] = None
        self._output_form: Optional[ParameterForm] = None
        super().__init__(*args, **kwargs)
        self._init_ui()

    def _init_ui(self):
        """Create widgets for input and output."""
        self._init_forms()
        self._init_control_area()
        self._add_input_form_widget()
        self._init_main_area()
        self._add_output_form_widget()
        self._refresh_non_form_input_widgets()
        self._refresh_non_form_output_widgets()

    def _init_forms(self) -> None:
        pass

    def _init_control_area(self) -> None:
        """Buttons to trigger execution and refresh."""
        super()._init_control_area()
        layout = self._get_control_layout()
        refresh = QtWidgets.QPushButton("Refresh")
        layout.addWidget(refresh)
        refresh.released.connect(self._refresh_widgets)

    def _add_input_form_widget(self) -> None:
        if self._input_form is not None:
            layout = self._get_control_layout()
            layout.addWidget(self._input_form)

    def _add_output_form_widget(self) -> None:
        if self._output_form is not None:
            layout = self._get_main_layout()
            layout.addWidget(self._output_form)

    def task_output_changed(self) -> None:
        self._refresh_output_widgets()
        super().task_output_changed()

    def handleNewSignals(self) -> None:
        self._refresh_input_widgets()
        super().handleNewSignals()

    def _create_input_form(self, parameter_info: dict) -> None:
        assert self._input_form is None
        form = ParameterForm(self.controlArea)
        for name, info in parameter_info.items():
            form.addParameter(
                name, **info, value_change_callback=self._input_form_edited
            )
        self._input_form = form
        self._refresh_input_form()

    def _create_output_form(self, parameter_info: dict) -> None:
        assert self._output_form is None
        form = ParameterForm(self.mainArea)
        for name, info in parameter_info.items():
            form.addParameter(name, **info)
        self._output_form = form
        self._refresh_output_form()

    def _refresh_widgets(self) -> None:
        self._refresh_input_widgets()
        self._refresh_output_widgets()

    def _refresh_input_widgets(self) -> None:
        self._refresh_input_form()
        self._refresh_non_form_input_widgets()

    def _refresh_output_widgets(self) -> None:
        self._refresh_output_form()
        self._refresh_non_form_output_widgets()

    def _refresh_non_form_input_widgets(self) -> None:
        pass

    def _refresh_non_form_output_widgets(self) -> None:
        pass

    def _refresh_input_form(self) -> None:
        """Set form values and disable rows with values from previous tasks"""
        if self._input_form is None:
            return

        # Set form value to default or dynamic inputs
        values, checked = self._values_to_form(self.get_task_input_values())
        self._input_form.set_parameter_values(values)
        self._input_form.set_parameters_checked(checked)

        # Disable form parameters with dynamic inputs
        disabled_names = self.get_dynamic_input_names()
        enabled = self._enabled_to_form(
            {name: name not in disabled_names for name in self.get_input_names()}
        )
        self._input_form.set_parameters_enabled(enabled)

    def _refresh_output_form(self) -> None:
        """Set form values"""
        if self._output_form is None:
            return
        # Set form value to task outputs
        values, checked = self._values_to_form(self.get_task_output_values())
        self._output_form.set_parameter_values(values)
        self._output_form.set_parameters_checked(checked)

    def _input_form_edited(self) -> None:
        """Store enabled form values as default inputs"""
        values = self._input_form.get_parameter_values()
        enabled = self._input_form.get_parameters_enabled()
        checked = self._input_form.get_parameters_checked()
        values = {k: v for k, v in values.items() if enabled[k]}
        parameters = self._values_from_form(values, checked)
        self.update_default_inputs(**parameters)

    def _values_from_form(
        self, values: Mapping, checked: Dict[str, bool], output: bool = False
    ) -> Mapping:
        return values

    def _values_to_form(
        self, values: Mapping, output: bool = False
    ) -> Tuple[Mapping, Dict[str, bool]]:
        return values, dict()

    def _enabled_to_form(
        self, enabled: Dict[str, bool], output: bool = False
    ) -> Dict[str, bool]:
        return enabled

    @contextmanager
    def _capture_errors(self, msg="widget update failed"):
        try:
            yield
        except Exception:
            logger.exception(msg)
