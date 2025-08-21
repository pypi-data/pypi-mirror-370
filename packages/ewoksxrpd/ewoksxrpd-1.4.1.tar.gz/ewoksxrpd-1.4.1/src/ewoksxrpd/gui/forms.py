from typing import Dict, Mapping, Sequence, Tuple
from . import serialize

from pyFAI.detectors import ALL_DETECTORS
from pyFAI.calibrant import ALL_CALIBRANTS
from ewokscore import missing_data


_GEOMETRY_KEYS = "dist", "poni1", "poni2", "rot1", "rot2", "rot3"
_ENERGY_GEOMETRY_KEYS = ("energy",) + _GEOMETRY_KEYS
_PARAMETRIZATION_KEYS = (
    "dist_expr",
    "param_names",
    "poni1_expr",
    "poni2_expr",
    "pos_names",
    "rot1_expr",
    "rot2_expr",
    "rot3_expr",
    "wavelength_expr",
)
_PARAMETERS_KEYS = (
    "arot1",
    "arot2",
    "arot3",
    "dist_offset",
    "dist_scale",
    "energy",
    "poni1_offset",
    "poni1_scale",
    "poni2_offset",
    "poni2_scale",
)


def input_parameters_calibratesingle(values: Mapping) -> dict:
    parameters = dict()
    _add_data_singlecalib(parameters)
    _add_energy_geometry(parameters, values)
    _add_calib_energy_geometry(parameters, values)
    parameters["max_rings"] = {
        "label": "# Rings (can be a sequence)",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    _add_detector_input(parameters)
    parameters["ring_detector"] = {
        "label": "Detector for the ring extraction. Leave this empty to use the same detector.",
        "value_for_type": list(ALL_DETECTORS),
        "serialize": str.lower,
    }
    _add_calibrant_input(parameters)
    _apply_values(parameters, values)
    return parameters


def output_parameters_calibratesingle() -> dict:
    parameters = dict()
    _add_energy_geometry(parameters, dict())
    return parameters


def input_parameters_calibratemulti(values: Mapping) -> dict:
    parameters = dict()
    _add_data_multicalib(parameters)
    _add_energy_geometry(parameters, values)
    _add_calib_energy_geometry(parameters, values)
    parameters["max_rings"] = {
        "label": "# Rings",
        "value_for_type": 0,
        "serialize": serialize.posint_serialize,
        "deserialize": serialize.posint_deserialize,
    }
    _add_detector_input(parameters)
    _add_calibrant_input(parameters)
    _apply_values(parameters, values)
    return parameters


def output_parameters_calibratemulti() -> dict:
    parameters = dict()
    _add_parametrization(parameters, dict())
    return parameters


def input_parameters_integrate1d(values: Mapping) -> dict:
    parameters = dict()
    _add_data_integrate1d(parameters)
    _add_energy_geometry(parameters, values)
    _add_detector_input(parameters)
    parameters["integration_options"] = {
        "label": "Integrate Options",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["fixed_integration_options"] = {
        "label": "Fixed Integrate Options",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_integrateblissscan(values: Mapping, saving: bool = False) -> dict:
    parameters = dict()
    _add_data_integrateblissscan(parameters)
    _add_energy_geometry(parameters, values)
    _add_detector_input(parameters)
    parameters["integration_options"] = {
        "label": "Integrate Options",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["fixed_integration_options"] = {
        "label": "Fixed Integrate Options",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    if saving:
        parameters["output_filename"] = {
            "label": "Output filename",
            "value_for_type": "",
            "select": "file",
        }
        parameters["nxprocess_as_default"] = {
            "label": "Mark Result as Default",
            "value_for_type": False,
        }
    _apply_values(parameters, values)
    return parameters


def input_parameters_ascii(values: Mapping) -> dict:
    parameters = {
        "filename": {"label": "Output file", "value_for_type": "", "select": "newfile"}
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_nexus(values: Mapping) -> dict:
    parameters = {
        "url": {"label": "Output file", "value_for_type": "", "select": "h5group"},
        "nxprocess_as_default": {
            "label": "Mark Result as Default",
            "value_for_type": False,
        },
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_background(values: Mapping) -> dict:
    parameters = {
        "image": {"label": "Image", "value_for_type": "", "select": "h5dataset"},
        "monitor": {"label": "Monitor", "value_for_type": "", "select": "h5dataset"},
        "background": {
            "label": "Background",
            "value_for_type": "",
            "select": "h5dataset",
        },
        "background_monitor": {
            "label": "Background Monitor",
            "value_for_type": "",
            "select": "h5dataset",
        },
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_mask(values: Mapping) -> dict:
    parameters = {
        "image1": {"label": "Image 1", "value_for_type": "", "select": "h5dataset"},
        "monitor1": {"label": "Monitor 1", "value_for_type": "", "select": "h5dataset"},
        "image2": {"label": "Image 2", "value_for_type": "", "select": "h5dataset"},
        "monitor2": {"label": "Monitor 2", "value_for_type": "", "select": "h5dataset"},
        "smooth": {
            "label": "Smooth width",
            "value_for_type": 0,
        },
        "monitor_ratio_margin": {
            "label": "Ratio margin",
            "value_for_type": "",
            "serialize": serialize.float_serialize,
            "deserialize": serialize.float_deserialize,
        },
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_calculategeometry(values: Mapping) -> dict:
    parameters = {
        "position": {"label": "Position", "value_for_type": "", "select": "h5dataset"},
    }
    _apply_values(parameters, values)
    return parameters


def output_parameters_calculategeometry() -> dict:
    parameters = dict()
    _add_energy_geometry(parameters, dict())
    return parameters


def input_parameters_diagnose_integrate1d(values: Mapping) -> dict:
    parameters = dict()
    _add_calibrant_input(parameters)
    _add_diagnostics_output(parameters)
    _apply_values(parameters, values)
    return parameters


def input_parameters_diagnose_singlecalib(values: Mapping) -> dict:
    parameters = dict()
    _add_data_singlecalib(parameters)
    _add_calibrant_input(parameters)
    _add_diagnostics_output(parameters)
    _apply_values(parameters, values)
    return parameters


def input_parameters_diagnose_multicalib(values: Mapping) -> dict:
    parameters = dict()
    _add_diagnostics_output(parameters)
    parameters["positions"] = {
        "label": "Positions",
        "select": "h5datasets",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["positionunits_in_meter"] = {
        "label": "Position Units (meter)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    _apply_values(parameters, values)
    return parameters


def input_parameters_pyfai_config(values: Mapping) -> dict:
    parameters = dict()
    parameters["filename"] = {
        "label": "Poni file",
        "value_for_type": "",
        "select": "file",
    }
    _add_energy_geometry(parameters, dict())
    _add_calibrant_input(parameters)
    _add_detector_input(parameters)
    parameters["mask"] = {
        "label": "Mask file",
        "value_for_type": "",
        "select": "file",
    }
    parameters["darkflatmethod"] = {
        "label": "Dark-Flat Method",
        "value_for_type": ["counts"],
        "select": "choices",
    }
    parameters["integration_options"] = {
        "label": "Integrate Options",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    _apply_values(parameters, values)
    return parameters


def output_parameters_pyfai_config() -> dict:
    parameters = dict()
    _add_energy_geometry(parameters, dict())
    _add_detector_output(parameters)
    _add_calibrant_output(parameters)
    return parameters


def _add_diagnostics_output(parameters: dict) -> None:
    parameters["filename"] = {
        "label": "Output file",
        "value_for_type": "",
        "select": "newfile",
    }


def _add_energy_geometry(parameters: dict, values: Mapping) -> None:
    values = _unpack(values, _GEOMETRY_KEYS, "geometry")

    parameters["energy"] = {
        "label": "Energy (keV)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["dist"] = {
        "label": "Distance (cm)",
        "value_for_type": "",
        "serialize": serialize.cm_serialize,
        "deserialize": serialize.cm_deserialize,
    }
    parameters["poni1"] = {
        "label": "Poni1 (cm)",
        "value_for_type": "",
        "serialize": serialize.cm_serialize,
        "deserialize": serialize.cm_deserialize,
    }
    parameters["poni2"] = {
        "label": "Poni2 (cm)",
        "value_for_type": "",
        "serialize": serialize.cm_serialize,
        "deserialize": serialize.cm_deserialize,
    }
    parameters["rot1"] = {
        "label": "Rot1 (deg)",
        "value_for_type": "",
        "serialize": serialize.degrees_serialize,
        "deserialize": serialize.degrees_deserialize,
    }
    parameters["rot2"] = {
        "label": "Rot2 (deg)",
        "value_for_type": "",
        "serialize": serialize.degrees_serialize,
        "deserialize": serialize.degrees_deserialize,
    }
    parameters["rot3"] = {
        "label": "Rot3 (deg)",
        "value_for_type": "",
        "serialize": serialize.degrees_serialize,
        "deserialize": serialize.degrees_deserialize,
    }


def _add_calib_energy_geometry(parameters: dict, values: Mapping):
    values = _unpack(values, _GEOMETRY_KEYS, "geometry")
    fixed = values.pop("fixed", None)

    if not fixed:
        fixed = list()
    for name in _ENERGY_GEOMETRY_KEYS:
        parameters[name].update(
            {
                "checked": name not in fixed,
                "checkbox_label": "refine",
            }
        )

    parameters["robust"] = {
        "label": "Robust",
        "value_for_type": True,
    }


def _add_parametrization(parameters: dict, values: Mapping) -> None:
    values = _unpack(values, _PARAMETRIZATION_KEYS, "parametrization")
    values = _unpack(values, _PARAMETERS_KEYS, "parameters")

    parameters["energy"] = {
        "label": "energy (keV)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["wavelength_expr"] = {
        "label": "wavelength (m) =",
        "value_for_type": "",
    }

    parameters["dist_offset"] = {
        "label": "dist_offset (cm)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["dist_scale"] = {
        "label": "dist_scal",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["dist_expr"] = {
        "label": "dist (m) =",
        "value_for_type": "",
    }

    parameters["poni1_offset"] = {
        "label": "poni1_offset (cm)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["poni1_scale"] = {
        "label": "poni1_scale",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["poni1_expr"] = {
        "label": "poni1 (m) =",
        "value_for_type": "",
    }

    parameters["poni2_offset"] = {
        "label": "poni2_offset (cm)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["poni2_scale"] = {
        "label": "poni2_scale",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["poni2_expr"] = {
        "label": "poni2 (m) =",
        "value_for_type": "",
    }

    parameters["arot1"] = {
        "label": "arot1 (rad)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["rot1_expr"] = {
        "label": "rot1 (rad) =",
        "value_for_type": "",
    }

    parameters["arot2"] = {
        "label": "arot2 (rad)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["rot2_expr"] = {
        "label": "rot2 (rad) =",
        "value_for_type": "",
    }

    parameters["arot3"] = {
        "label": "arot3 (drad)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["rot3_expr"] = {
        "label": "rot3 (rad) =",
        "value_for_type": "",
    }


def _add_detector_input(parameters: dict) -> None:
    parameters["detector"] = {
        "label": "Detector",
        "value_for_type": list(ALL_DETECTORS),
        "serialize": str.lower,
    }
    parameters["detector_config"] = {
        "label": "Detector parameters",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }


def _add_detector_output(parameters: dict) -> None:
    parameters["detector"] = {
        "label": "Detector",
        "value_for_type": "",
        "serialize": str.lower,
    }
    parameters["detector_config"] = {
        "label": "Detector parameters",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }


def _add_calibrant_input(parameters: dict) -> None:
    parameters["calibrant"] = {
        "label": "Calibrant",
        "value_for_type": list(ALL_CALIBRANTS.all),
    }


def _add_calibrant_output(parameters: dict) -> None:
    parameters["calibrant"] = {
        "label": "Calibrant",
        "value_for_type": "",
    }


def output_parameters_calib(parameters: dict):
    _add_energy_geometry(parameters, dict())


def _add_data_singlecalib(parameters: dict) -> None:
    parameters["image"] = {
        "label": "Pattern",
        "value_for_type": "",
        "select": "h5dataset",
    }


def _add_data_multicalib(parameters: dict) -> None:
    parameters["images"] = {
        "label": "Patterns",
        "value_for_type": "",
        "select": "h5datasets",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["positions"] = {
        "label": "Positions",
        "value_for_type": "",
        "select": "h5datasets",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["reference_position"] = {
        "label": "Reference Position",
        "value_for_type": "",
        "select": "h5dataset",
    }
    parameters["sample_position"] = {
        "label": "Sample position",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["positionunits_in_meter"] = {
        "label": "Position Units (meter)",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }


def _add_data_integrate1d(parameters: dict) -> None:
    parameters["image"] = {
        "label": "Pattern",
        "value_for_type": "",
        "select": "h5dataset",
    }
    parameters["monitor"] = {
        "label": "Monitor",
        "value_for_type": "",
        "select": "h5dataset",
    }
    parameters["reference"] = {
        "label": "Reference",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["mask"] = {"label": "Mask", "value_for_type": "", "select": "h5dataset"}
    _add_detector_input(parameters)


def _add_data_integrateblissscan(parameters: dict) -> None:
    parameters["filename"] = {
        "label": "Bliss filename",
        "value_for_type": "",
        "select": "file",
    }
    parameters["scan"] = {"label": "Scan number", "value_for_type": 0}
    parameters["subscan"] = {"label": "Sub scan number", "value_for_type": 0}

    parameters["detector_name"] = {"label": "Detector name", "value_for_type": ""}
    parameters["counter_names"] = {
        "label": "Counter names",
        "value_for_type": "",
        "serialize": serialize.json_dumps,
        "deserialize": serialize.json_loads,
    }
    parameters["monitor"] = {
        "label": "Monitor",
        "value_for_type": "",
        "select": "h5dataset",
    }
    parameters["reference"] = {
        "label": "Reference",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["mask"] = {"label": "Mask", "value_for_type": "", "select": "h5dataset"}
    _add_detector_input(parameters)

    parameters["retry_timeout"] = {
        "label": "retry_timeout",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }

    parameters["retry_period"] = {
        "label": "retry_period",
        "value_for_type": "",
        "serialize": serialize.float_serialize,
        "deserialize": serialize.float_deserialize,
    }
    parameters["demo"] = {"label": "demo", "value_for_type": False}
    return parameters


def _apply_values(parameters: dict, values: Mapping) -> None:
    for k, v in values.items():
        if k in parameters:
            parameters[k]["value"] = v


def unpack_geometry(values: Mapping) -> Tuple[Mapping, Dict[str, bool]]:
    values = _unpack(values, _GEOMETRY_KEYS, "geometry")
    fixed = values.pop("fixed", None)
    if fixed:
        checked = {name: name not in fixed for name in _ENERGY_GEOMETRY_KEYS}
    else:
        checked = dict()
    return values, checked


def unpack_enabled_geometry(enabled: Dict[str, bool]) -> Dict[str, bool]:
    values = _unpack_enabled(enabled, _GEOMETRY_KEYS, "geometry")
    return values


def pack_geometry(values: Mapping, checked: Dict[str, bool]) -> dict:
    values = _pack(values, _GEOMETRY_KEYS, "geometry")
    if checked:
        values["fixed"] = [k for k, v in checked.items() if not v]
    else:
        values["fixed"] = missing_data.MISSING_DATA
    return values


def unpack_parametrization(values: Mapping) -> dict:
    values = _unpack(values, _PARAMETRIZATION_KEYS, "parametrization")
    values = _unpack(values, _PARAMETERS_KEYS, "parameters")
    return values


def unpack_enabled_parametrization(enabled: Dict[str, bool]) -> Dict[str, bool]:
    values = _unpack_enabled(enabled, _PARAMETRIZATION_KEYS, "parametrization")
    values = _unpack_enabled(enabled, _PARAMETERS_KEYS, "parameters")
    return values


def pack_parametrization(values: Mapping) -> dict:
    values = _pack(values, _PARAMETRIZATION_KEYS, "parametrization")
    values = _pack(values, _PARAMETERS_KEYS, "parameters")
    return values


def _pack(values: Mapping, keys: Sequence[str], pack_key: str) -> dict:
    result = {k: v for k, v in values.items() if k not in keys}
    packed = {
        k: v
        for k, v in values.items()
        if k in keys and not missing_data.is_missing_data(v)
    }
    if len(packed) == len(keys):
        result[pack_key] = packed
    else:
        result[pack_key] = missing_data.MISSING_DATA
    return result


def _unpack(values: Mapping, keys: Sequence[str], pack_key: str) -> dict:
    result = dict(values)
    packed = result.pop(pack_key, None)
    if packed:
        result.update(packed)
    else:
        result.update({k: missing_data.MISSING_DATA for k in keys})
    return result


def _unpack_enabled(
    enabled: Dict[str, bool], keys: Sequence[str], pack_key: str
) -> Dict[str, bool]:
    result = dict(enabled)
    packed = result.pop(pack_key, None)
    if packed is not None:
        result.update({k: packed for k in keys})
    return result
