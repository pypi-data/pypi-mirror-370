from ewoksxrpd.gui import serialize
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_nexus
from ewoksxrpd.tasks.nexus import SaveNexusIntegrated


__all__ = ["OWSaveNexusIntegrated"]


class OWSaveNexusIntegrated(OWTriggerWidget, ewokstaskclass=SaveNexusIntegrated):
    name = "SaveNexusIntegrated"
    description = "Save result from integration in Nexus HDF5 format"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_nexus(self.get_default_input_values())
        parameter_info["radial"] = {
            "label": "Radial values",
            "value_for_type": "",
        }
        parameter_info["intensity"] = {
            "label": "Intensity values",
            "value_for_type": "",
        }
        parameter_info["radial_units"] = {
            "label": "Radial unit",
            "value_for_type": "",
            "serialize": str.lower,
        }
        parameter_info["info"] = {
            "label": "Configuration",
            "value_for_type": "",
            "serialize": serialize.json_dumps,
            "deserialize": serialize.json_loads,
        }
        parameter_info["azimuthal"] = {
            "label": "Azimuthal values",
            "value_for_type": "",
        }
        parameter_info["intensity_error"] = {
            "label": "Intensity errors",
            "value_for_type": "",
        }

        self._create_input_form(parameter_info)
