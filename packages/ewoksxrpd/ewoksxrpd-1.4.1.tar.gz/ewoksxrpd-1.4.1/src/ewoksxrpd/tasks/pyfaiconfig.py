import json
import logging
from pathlib import Path
from typing import Union

from pyFAI import method_registry
from pyFAI.io import ponifile
from ewokscore import Task

from .utils import pyfai_utils, xrpd_utils

__all__ = ["PyFaiConfig"]

logger = logging.getLogger(__name__)


class PyFaiConfig(
    Task,
    optional_input_names=[
        "energy",
        "geometry",
        "detector",
        "detector_config",
        "mask",
        "flatfield",
        "darkcurrent",
        "integration_options",
        "filenames",
        "filename",
        "calibrant",
        "darkflatmethod",
        "show_merge_warnings",
    ],
    output_names=[
        "energy",
        "geometry",
        "detector",
        "detector_config",
        "mask",
        "flatfield",
        "darkcurrent",
        "integration_options",
        "calibrant",
    ],
):
    """Parse pyFAI calibration and integration parameters.

    Optional inputs:
    - energy (float|None): Energy in KeV (priority 1)
    - geometry (dict|None): pyFAI geometry information (priority 1)
    - detector (str|None): Name of the detector (priority 1)
    - detector_config (dict|None): Configuration of the detector (priority 1)
    - mask (str|numpy.ndarray|None): Filename or data of the detector mask (priority 1)
    - flatfield (str|numpy.ndarray|None): Filename or data of the detector flat-field (priority 1)
    - darkcurrent (str|numpy.ndarray|None): Filename or data of the detector dark-current (priority 1)
    - integration_options (dict|None): Extra pyFAI worker or integration parameters (priority 2)
    - filenames (Sequence[str]|None): PyFAI poni or json file name (priority 3, last file has highest priority)
    - filename (str|None): PyFAI poni or json file name (priority 4)
    - calibrant (str|None): Calibrant name
    - darkflatmethod (str|None): Dark and flat-field correction method

    Outputs:
    - energy (float): Energy in KeV
    - geometry (dict): pyFAI geometry information
    - detector (str): Name of the detector
    - detector_config (dict): Configuration of the detector
    - mask (str|numpy.ndarray|None): Filename or data of the detector mask
    - flatfield (str|numpy.ndarray|None): Filename or data of the detector flat-field
    - darkcurrent (str|numpy.ndarray|None): Filename or data of the detector dark-current
    - integration_options (dict): Extra pyFAI worker or integration parameters
    - calibrant (str|None): Calibrant name
    """

    def run(self):
        input_values = self.get_input_values()
        merged_options = self.merged_integration_options()

        ##########################################################################
        # Extract poni variables to energy, detector, detector_config and geometry
        ##########################################################################

        if "poni" in merged_options and merged_options.get("version", 0) > 3:
            merged_options.update(merged_options.pop("poni"))

        # energy > merged_options["energy"] > merged_options["wavelength"]
        energy = input_values.get("energy", merged_options.pop("energy", None))
        wavelength = merged_options.pop("wavelength", None)
        if energy is None and wavelength is not None:
            energy = xrpd_utils.energy_wavelength(wavelength)

        # detector > merged_options["detector"]
        detector = merged_options.pop("detector", None)
        if not self.missing_inputs.detector:
            detector = input_values["detector"]

        # detector_config > merged_options["detector_config"]
        detector_config = merged_options.pop("detector_config", None)
        if not self.missing_inputs.detector_config:
            detector_config = input_values["detector_config"]

        geometry = {
            k: merged_options.pop(k)
            for k in ["dist", "poni1", "poni2", "rot1", "rot2", "rot3"]
            if k in merged_options
        }
        if not self.missing_inputs.geometry:
            geometry = input_values["geometry"]

        ############################################
        # Extract image correction related variables
        ############################################

        mask = input_values.get("mask", None)
        flatfield = input_values.get("flatfield", None)
        darkcurrent = input_values.get("darkcurrent", None)
        if not self.missing_inputs.darkflatmethod:
            merged_options["darkflatmethod"] = self.inputs.darkflatmethod

        #################################
        # Normalize error model variables
        #################################

        do_poisson = merged_options.pop("do_poisson", None)
        do_azimuthal_error = merged_options.pop("do_azimuthal_error", None)
        error_model = merged_options.pop("error_model", None)
        if not error_model:
            if do_poisson:
                error_model = "poisson"
            if do_azimuthal_error:
                error_model = "azimuthal"
        if error_model:
            merged_options["error_model"] = error_model

        #######################################
        # Check method and integrator function
        #######################################

        method = merged_options.get("method") or ""
        if not isinstance(method, str):
            method = "_".join([_ for _ in method if isinstance(_, str)])
        pmethod = method_registry.IntegrationMethod.parse(method)

        integrator_name = merged_options.get("integrator_name", "")
        if integrator_name in ("sigma_clip", "_sigma_clip_legacy"):
            logger.warning(
                "'%s' is not compatible with the pyfai worker: use 'sigma_clip_ng'",
                integrator_name,
            )
            merged_options["integrator_name"] = "sigma_clip_ng"
        if "sigma_clip_ng" == integrator_name:
            if pmethod and pmethod.split != "no":
                raise ValueError(
                    "to combine sigma clipping with pixel splitting, use 'sigma_clip_legacy'"
                )

        ################################
        # Extract calibration parameters
        ################################

        calibrant = input_values.get("calibrant", None)

        ################################
        # Extract schema versions
        ################################

        _ = merged_options.pop("poni_version", None)

        # There is also "version" which is the JSON schema version.

        ##########
        # Output
        ##########

        self.outputs.energy = energy
        self.outputs.geometry = geometry
        self.outputs.detector = detector
        self.outputs.detector_config = detector_config
        self.outputs.calibrant = calibrant
        self.outputs.mask = mask
        self.outputs.flatfield = flatfield
        self.outputs.darkcurrent = darkcurrent
        self.outputs.integration_options = merged_options

    def _update_integration_options(
        self, current_options: dict, new_options_source: Union[str, dict]
    ):
        if isinstance(new_options_source, dict):
            new_options = new_options_source
        else:
            new_options = pyfai_utils.read_config(new_options_source)

        if self.get_input_value("show_merge_warnings", False):
            common_keys = current_options.keys() & new_options.keys()
            for key in common_keys:
                logger.warning(
                    f"New value of '{key}' ({new_options[key]}) from {new_options_source} will overwrite the current value ({current_options[key]})!"
                )

        current_options.update(new_options)

    def merged_integration_options(self) -> dict:
        """Merge integration options in this order of priority:

        - filename (lowest priority)
        - filenames[0]
        - filenames[1]
        - ...
        - integration_options (highest priority)
        """
        merged_options = dict()
        filenames = list()
        if self.inputs.filename:
            filenames.append(self.inputs.filename)
        if self.inputs.filenames:
            filenames.extend(self.inputs.filenames)
        for filename in filenames:
            self._update_integration_options(merged_options, filename)
        if self.inputs.integration_options:
            self._update_integration_options(
                merged_options,
                pyfai_utils.normalize_parameters(self.inputs.integration_options),
            )
        return merged_options


class SavePyFaiConfig(
    Task,
    input_names=[
        "output_filename",
        "energy",
        "geometry",
        "detector",
    ],
    optional_input_names=[
        "mask",
        "detector_config",
        "integration_options",
    ],
    output_names=["filename"],
):
    """Save inputs as pyFAI calibration and integration configuration file (.json)

    The configuration is saved as a JSON file following pyFAI configuration format.

    Required inputs:
    - output_filename (str): Name of the file where to save pyFAI configuration. Must include the extension
    - energy (float): Energy in KeV
    - geometry (dict): pyFAI geometry information (poni)
    - detector (str): Name of the detector

    Optional inputs:
    - mask (str): Filename of the mask to used
    - detector_config (dict): Configuration of the detector
    - integration_options (dict): Extra configuration fields

    Outputs:
    - filename (str): Saved filename, same as output_filename
    """

    def run(self):
        integration_options = pyfai_utils.normalize_parameters(
            self.get_input_value("integration_options", {})
        )
        version = integration_options.pop("version", 3)

        config = {
            "application": "pyfai-integrate",
            "version": version,
        }

        poni = _create_ponifile(
            self.inputs.energy,
            self.inputs.geometry,
            self.inputs.detector,
            self.get_input_value("detector_config", {}),
        ).as_dict()
        _ = poni.pop("poni_version", None)

        if version >= 4:
            config["poni"] = poni
        else:
            config.update(poni)

        mask = self.get_input_value("mask", None)
        if mask is not None:
            config["do_mask"] = True
            config["mask_file"] = mask

        for key, value in integration_options.items():
            config.setdefault(key, value)  # Do not override already set keys

        filepath = Path(self.inputs.output_filename).absolute()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(json.dumps(config, indent=4))

        self.outputs.filename = str(filepath)


class SavePyFaiPoniFile(
    Task,
    input_names=[
        "output_filename",
        "energy",
        "geometry",
        "detector",
    ],
    optional_input_names=[
        "detector_config",
    ],
    output_names=["filename"],
):
    """Save inputs as pyFAI PONI file

    Required inputs:
    - output_filename (str): Name of the file where to save pyFAI PONI. Must include extension.
    - energy (float): Energy in KeV
    - geometry (dict): pyFAI geometry information (poni)
    - detector (str): Name of the detector

    Optional inputs:
    - detector_config (dict): Configuration of the detector

    Outputs:
    - filename (str): Saved filename, same as output_filename
    """

    def run(self):
        poni = _create_ponifile(
            self.inputs.energy,
            self.inputs.geometry,
            self.inputs.detector,
            self.get_input_value("detector_config", {}),
        )

        filepath = Path(self.inputs.output_filename).absolute()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open("w", encoding="ascii") as fd:
            poni.write(fd)

        self.outputs.filename = str(filepath)


def _create_ponifile(
    energy: float,
    geometry: dict,
    detector: str,
    detector_config: dict,
) -> ponifile.PoniFile:
    return ponifile.PoniFile(
        {
            **geometry,  # First so other fields overrides it
            "detector": detector,
            "detector_config": detector_config,
            "wavelength": xrpd_utils.energy_wavelength(energy),
        }
    )
