from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Optional

import h5py
from ewokscore.missing_data import is_missing_data
from ewoksdata.data.nexus import select_default_plot
from silx.io.dictdump import dicttonx

from .data_access import TaskWithDataAccess
from .utils import data_utils
from .utils import pyfai_utils

__all__ = ["SaveNexusPattern1D", "SaveNexusIntegrated"]


class _BaseSaveNexusIntegrated(
    TaskWithDataAccess,
    input_names=["url"],
    optional_input_names=[
        "bliss_scan_url",
        "metadata",
        "nxprocess_name",
        "nxmeasurement_name",
        "nxprocess_as_default",
        "external_url",
    ],
    output_names=["saved"],
    register=False,
):
    @property
    def _process_info(self) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    @property
    def _nxprocess_name(self):
        if self.inputs.nxprocess_name:
            return self.inputs.nxprocess_name
        return "integrate"

    @property
    def _nxmeasurement_name(self):
        if self.inputs.nxmeasurement_name:
            return self.inputs.nxmeasurement_name
        return "integrated"

    @contextmanager
    def _save_context(self):
        link_results_nxentry_url = self.inputs.url
        results_nxentry_url = self.get_input_value(
            "external_url", link_results_nxentry_url
        )

        with self.open_h5item(
            results_nxentry_url, mode="a", create=True
        ) as results_nxentry:
            assert isinstance(results_nxentry, h5py.Group)
            with self.open_h5item(
                link_results_nxentry_url, mode="a", create=True
            ) as link_results_nxentry:
                assert isinstance(link_results_nxentry, h5py.Group)
                results_nxprocess = pyfai_utils.create_nxprocess(
                    results_nxentry,
                    link_results_nxentry,
                    self._nxprocess_name,
                    self._process_info,
                )

            yield results_nxprocess

            # Create links
            with self.open_h5item(
                link_results_nxentry_url, mode="a", create=True
            ) as link_results_nxentry:
                bliss_scan_url = data_utils.data_from_storage(
                    self.inputs.bliss_scan_url, remove_numpy=True
                )
                if bliss_scan_url:
                    self.link_bliss_scan(link_results_nxentry, bliss_scan_url)

                results_nxdata = results_nxprocess.get("integrated")
                if results_nxdata is not None:
                    if self.get_input_value("nxprocess_as_default", True):
                        select_default_plot(results_nxdata)

                    intensity = results_nxdata.get("intensity")
                    if intensity is not None:
                        nxmeasurement = results_nxentry.require_group("measurement")
                        nxmeasurement.attrs.setdefault("NX_class", "NXcollection")
                        data_utils.create_hdf5_link(
                            nxmeasurement, self._nxmeasurement_name, intensity
                        )

                        link_nxmeasurement = link_results_nxentry.require_group(
                            "measurement"
                        )
                        link_nxmeasurement.attrs.setdefault("NX_class", "NXcollection")
                        data_utils.create_hdf5_link(
                            link_nxmeasurement, self._nxmeasurement_name, intensity
                        )
                        if self.inputs.metadata:
                            dicttonx(
                                self.inputs.metadata,
                                link_results_nxentry,
                                update_mode="add",
                                add_nx_class=True,
                            )
        self.outputs.saved = True


class SaveNexusPattern1D(
    _BaseSaveNexusIntegrated,
    input_names=["x", "y", "xunits"],
    optional_input_names=["header", "yerror"],
):
    """Save single diffractogram in HDF5/NeXus format"""

    def run(self):
        with self._save_context() as results_nxprocess:
            results_nxdata = pyfai_utils.create_integration_results_nxdata(
                results_nxprocess,
                self.inputs.y.ndim,
                self.inputs.x,
                self.inputs.xunits,
                None,
                None,
            )
            results_nxdata.attrs["signal"] = "intensity"
            results_nxdata["intensity"] = self.inputs.y
            if not self.missing_inputs.yerror:
                results_nxdata["intensity_errors"] = self.inputs.yerror

    @property
    def _process_info(self) -> Optional[Dict[str, Any]]:
        return self.get_input_value("header", None)


class SaveNexusIntegrated(
    _BaseSaveNexusIntegrated,
    input_names=["radial", "intensity", "radial_units"],
    optional_input_names=["info", "azimuthal", "intensity_error", "azimuthal_units"],
):
    """Save 1D or 2D integration diffraction patterns in HDF5/NeXus format"""

    def run(self):
        with self._save_context() as results_nxprocess:
            # Fallback for old workflows that do not specify azimuthal_units but do have azimuthal data
            if is_missing_data(self.inputs.azimuthal_units) and not is_missing_data(
                self.inputs.azimuthal
            ):
                azimuthal_units = "chi_deg"
            else:
                azimuthal_units = self.inputs.azimuthal_units
            results_nxdata = pyfai_utils.create_integration_results_nxdata(
                results_nxprocess,
                self.inputs.intensity.ndim,
                self.inputs.radial,
                self.inputs.radial_units,
                self.inputs.azimuthal,
                azimuthal_units,
            )
            results_nxdata.attrs["signal"] = "intensity"
            results_nxdata["intensity"] = self.inputs.intensity
            if not self.missing_inputs.intensity_error:
                results_nxdata["intensity_errors"] = self.inputs.intensity_error

    @property
    def _process_info(self) -> Optional[Dict[str, Any]]:
        return self.get_input_value("info", None)


class SaveNexusMultiPattern1D(
    _BaseSaveNexusIntegrated,
    input_names=["x_list", "y_list", "xunits"],
    optional_input_names=["header_list", "yerror_list"],
):

    def run(self):
        x_list = self.inputs.x_list
        y_list = self.inputs.y_list
        xunits = self.inputs.xunits

        for i, (x, y, unit) in enumerate(zip(x_list, y_list, xunits)):
            self._current_index = i

            with self._save_context() as results_nxprocess:
                results_nxdata = pyfai_utils.create_integration_results_nxdata(
                    results_nxprocess, y.ndim, x, unit, None, None
                )
                results_nxdata.attrs["signal"] = "intensity"
                results_nxdata["intensity"] = y
                if not self.missing_inputs.yerror_list:
                    results_nxdata["intensity_errors"] = self.inputs.yerror_list[i]

    @property
    def _process_info(self) -> Optional[Dict[str, Any]]:
        header_list = self.get_input_value("header_list", None)
        if header_list is None:
            return None
        return header_list[self._current_index]

    @property
    def _nxprocess_name(self):
        if self.inputs.nxprocess_name:
            name = self.inputs.nxprocess_name
        else:
            name = "integrate"
        return f"{name}_{self._current_index}"

    @property
    def _nxmeasurement_name(self):
        if self.inputs.nxmeasurement_name:
            name = self.inputs.nxmeasurement_name
        else:
            name = "integrated"
        return f"{name}_{self._current_index}"
