import os
import h5py
from silx.gui.plot import Plot1D
from silx.io.url import DataUrl

from ewoksxrpd.tasks.nexus import SaveNexusPattern1D
from ewoksxrpd.gui.trigger_widget import OWTriggerWidget
from ewoksxrpd.gui.forms import input_parameters_nexus


__all__ = ["OWSaveNexusPattern1D"]


class OWSaveNexusPattern1D(OWTriggerWidget, ewokstaskclass=SaveNexusPattern1D):
    name = "SaveNexusPattern1D"
    description = "Save a 1D diffraction pattern in Nexus HDF5 format"
    icon = "icons/widget.png"
    want_main_area = True

    def _init_forms(self):
        parameter_info = input_parameters_nexus(self.get_default_input_values())
        self._create_input_form(parameter_info)

    def _init_main_area(self):
        self._plot = Plot1D()
        self.mainArea.layout().addWidget(self._plot)
        super()._init_main_area()

    def _refresh_non_form_output_widgets(self):
        with self._capture_errors():
            super()._refresh_non_form_output_widgets()
            self._update_plot()

    def _update_plot(self):
        self._plot.remove(kind="curve")

        url = self.get_task_input_value("url")
        url = self.get_task_input_value("external_url", url)
        if not url:
            return
        url = DataUrl(url)
        if not os.path.exists(url.file_path()):
            return

        nxprocess_name = self.get_task_input_value("nxprocess_name")

        with h5py.File(url.file_path(), "r") as nxroot:
            data_path = url.data_path() or "results"
            nxprocess = nxroot[data_path].get(nxprocess_name)
            if nxprocess is None:
                return
            nxdata = nxprocess.get("integrated")
            if nxdata is None:
                return
            attrs = dict(nxdata.attrs)
            if {"axes", "signal"} - attrs.keys():
                return

            xname = attrs["axes"][0]
            yname = attrs["signal"]
            x = nxdata[xname]
            xunits = x.attrs["units"]
            y = nxdata[yname]

            curve = self._plot.addCurve(
                x[()], y[()], xlabel=f"{xname} ({xunits})", ylabel=yname
            )
            self._plot.setActiveCurve(curve)
