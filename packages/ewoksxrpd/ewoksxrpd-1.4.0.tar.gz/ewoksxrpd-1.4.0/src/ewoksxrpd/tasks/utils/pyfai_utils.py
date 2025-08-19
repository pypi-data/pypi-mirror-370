import re
import json
import enum
import warnings
import importlib.metadata
from typing import Union, Dict, Optional, Any, Iterator, Tuple, List, NamedTuple
from collections.abc import Mapping, Sequence

import h5py
import numpy
from pyFAI.units import Unit
from pyFAI.io.ponifile import PoniFile
from pyFAI.average import average_images
from silx.io.dictdump import dicttonx
from silx.io.url import DataUrl
from ewokscore.task import TaskInputError
from ewokscore.missing_data import is_missing_data

from .xrpd_utils import energy_wavelength
from .data_utils import data_from_storage
from .data_utils import create_hdf5_link


_PYFAI_VERSION = importlib.metadata.version("pyFAI")
_EWOKS_VERSION = importlib.metadata.version("ewoks")


_REPLACE_PATTERNS = {
    "/gpfs/[^/]+/": "/",
    "/mnt/multipath-shares/": "/",
    "/lbsram/": "/",
}


class AxisInfo(NamedTuple):
    name: str
    units: str

    def to_str(self):
        return f"{self.name}_{self.units}"


def parse_pyfai_units(
    pyfai_unit: Union[Unit, Tuple[Unit, Unit]],
) -> Tuple[AxisInfo, AxisInfo]:
    """
    Parse PyFAI result units into a tuple containing the radial axis info and the azimuthal axis info.
    Handles pyFAI >= 2024.1 units (tuple with radial+azimuthal) and pyFAI < 2024.1 units (only radial unit).

    If no info is available for the azimuthal axis, it will default to name "chi" and unit "deg".
    """
    if isinstance(pyfai_unit, tuple):
        return _parse_pyfai_unit(pyfai_unit[0]), _parse_pyfai_unit(pyfai_unit[1])

    return _parse_pyfai_unit(pyfai_unit), AxisInfo("chi", "deg")


def _parse_pyfai_unit(pyfai_unit: Unit) -> AxisInfo:
    unit_tuple = tuple(pyfai_unit.name.split("_"))
    if len(unit_tuple) != 2:
        raise ValueError(f"Expected unit to be of the form X_Y. Got {pyfai_unit.name}")

    return AxisInfo(*unit_tuple)


def parse_string_units(unit: Union[str, numpy.ndarray]) -> AxisInfo:
    if isinstance(unit, numpy.ndarray):
        unit = unit.item()
    if not isinstance(unit, str):
        raise TypeError(type(unit))
    unit_tuple = tuple(unit.split("_"))
    if len(unit_tuple) != 2:
        raise ValueError(f"Expected unit to be of the form X_Y. Got {unit}")
    return AxisInfo(*unit_tuple)


def read_config(
    filename: Optional[str], replace_patterns: Optional[Dict[str, str]] = None
) -> dict:
    if not filename:
        return dict()
    if filename.endswith(".json"):
        parameters = _read_json(filename)
    else:
        parameters = _read_poni(filename)
    return normalize_parameters(parameters, replace_patterns=replace_patterns)


def _read_json(filename: str) -> dict:
    with open(filename, "r") as fp:
        return json.load(fp)


def _read_poni(filename: str) -> dict:
    return PoniFile(filename).as_dict()


def normalize_parameters(
    parameters: Any, replace_patterns: Optional[Dict[str, str]] = None
) -> Any:
    if replace_patterns is None:
        replace_patterns = _REPLACE_PATTERNS
    if isinstance(parameters, str):
        for pattern, repl in replace_patterns.items():
            parameters = re.sub(pattern, repl, parameters)
        return parameters
    if isinstance(parameters, Mapping):
        return {
            k: normalize_parameters(v, replace_patterns=replace_patterns)
            for k, v in parameters.items()
        }
    if isinstance(parameters, Sequence):
        return [
            normalize_parameters(v, replace_patterns=replace_patterns)
            for v in parameters
        ]
    if isinstance(parameters, enum.Enum):
        return parameters.value
    if isinstance(parameters, (int, float)):
        return parameters
    if parameters is None:
        return None
    warnings.warn(
        f"Unexpected pyFAI configuration parameter type '{type(parameters)}'",
        UserWarning,
    )
    return parameters


def split_worker_and_integration_options(
    ewoks_pyfai_options: Mapping,
) -> Tuple[dict, dict]:
    integration_options = dict(ewoks_pyfai_options)
    worker_keys = "integrator_name", "extra_options", "dummy"
    worker_options = {
        k: integration_options.pop(k) for k in worker_keys if k in integration_options
    }

    nbpt_rad = integration_options.setdefault("nbpt_rad", 1024)

    nbpt_azim = integration_options.setdefault("nbpt_azim", 1)

    worker_options.setdefault("shapeOut", (nbpt_azim, nbpt_rad))

    unit = integration_options.get("unit")
    if unit:
        worker_options["unit"] = unit

    worker_options.setdefault("dummy", float("nan"))
    return worker_options, integration_options


def convert_ewoks_options_to_mg_options(ewoks_pyfai_options: Mapping) -> Dict[str, Any]:
    """Convert Ewoks PyFAI options (WorkerConfig keys) to Multigeometry options (integrate2d parameters)"""
    integration_options = dict(ewoks_pyfai_options)

    npt_rad = integration_options.pop("nbpt_rad", None)
    if npt_rad:
        integration_options["npt_rad"] = npt_rad

    npt_azim = integration_options.pop("nbpt_azim", None)
    if npt_azim:
        integration_options["npt_azim"] = npt_azim

    radial_range_min = integration_options.pop("radial_range_min", None)
    radial_range_max = integration_options.pop("radial_range_max", None)
    if radial_range_min is not None and radial_range_max is not None:
        integration_options["radial_range"] = (radial_range_min, radial_range_max)

    azim_range_min = integration_options.pop("azimuth_range_min", None)
    azim_range_max = integration_options.pop("azimuth_range_max", None)
    if azim_range_min is not None and azim_range_max is not None:
        integration_options["azimuth_range"] = (azim_range_min, azim_range_max)

    return integration_options


def split_multi_geom_and_integration_options(
    ewoks_pyfai_options: Mapping,
) -> Tuple[dict, dict]:
    integration_options = convert_ewoks_options_to_mg_options(ewoks_pyfai_options)

    multi_geometry_keys = ("unit", "radial_range", "azimuth_range", "empty")

    multi_geometry_options = {
        k: integration_options.pop(k)
        for k in multi_geometry_keys
        if k in integration_options
    }

    return multi_geometry_options, integration_options


def extract_images_from_integration_options(
    integration_options: Mapping,
) -> Tuple[
    dict, Optional[numpy.ndarray], Optional[numpy.ndarray], Optional[numpy.ndarray]
]:
    """Extract all image related information from integration options and modify
    integration options accordingly.

    :return: integration options, mask image, flat-field image, dark-current image
    """
    integration_options = dict(integration_options)

    mask = _extract_mask(integration_options)
    flatfield = _extract_flatfield(integration_options)
    darkcurrent = _extract_darkcurrent(integration_options)
    darkflatmethod = integration_options.pop("darkflatmethod", None)

    if darkflatmethod is None:
        return integration_options, mask, flatfield, darkcurrent

    # Flat field correction:
    #   - default: Icor = (I - dark) / flat
    #   - counts:  Icor = (I - dark) / max(flat - dark, 1)

    flat_field = _get_image_urls(integration_options, "flat_field", "do_flat")
    if flat_field:
        flatfield = average_images(
            flat_field, filter_="mean", fformat=None, threshold=0
        )
        integration_options["flat_field"] = None
        integration_options["do_flat"] = False

    dark_current = _get_image_urls(integration_options, "dark_current", "do_dark")
    if dark_current:
        darkcurrent = average_images(
            dark_current, filter_="mean", fformat=None, threshold=0
        )
        integration_options["dark_current"] = None
        integration_options["do_dark"] = False

    if darkflatmethod == "counts":
        if flatfield is not None:
            if darkcurrent is not None:
                flatfield = flatfield - darkcurrent
            flatfield[flatfield < 1] = 1

    return integration_options, mask, flatfield, darkcurrent


def _extract_mask(integration_options: dict) -> Optional[numpy.ndarray]:
    """Integration options related to the mask:

    * mask_file: URL or None
    * do_mask: use mask_file or not
    * mask: URL, array or None (overwrites mask_file and do_mask when not None)
    """
    # Typically from a JSON configuration file
    mask_file = _get_image_urls(integration_options, "mask_file", "do_mask")
    do_mask = bool(mask_file)

    # Typically in memory from a previous calculation
    mask = integration_options.pop("mask", None)
    if isinstance(mask, str):
        mask_file = mask
        mask = None
        do_mask = True

    # Let pyFAI handle URLs (if any) and return in-memory (if any)
    integration_options["mask_file"] = mask_file
    integration_options["do_mask"] = do_mask
    return mask


def _extract_flatfield(integration_options: dict) -> Optional[numpy.ndarray]:
    """Integration options related to the flatfield:

    * flat_field: URL(s) (list of strings or comma separate string) or None
    * do_flat: use flat_field or not
    * flatfield: URL(s) (list of strings or comma separate string), array or None (overwrites flat_field and do_flat when not None)

    When a numpy array is returned, the flat field is removed from the integration options.
    """
    # Typically from a JSON configuration file
    flat_field = _get_image_urls(integration_options, "flat_field", "do_flat")
    do_flat = bool(flat_field)

    # Typically in memory from a previous calculation
    flatfield = integration_options.pop("flatfield", None)
    if isinstance(flatfield, str):
        flatfield = [s.strip() for s in flatfield.split(",")]
    if isinstance(flatfield, Sequence) and isinstance(flatfield[0], str):
        flat_field = flatfield
        flatfield = None
        do_flat = True
    if flatfield is not None:
        flat_field = None
        do_flat = False

    # Let pyFAI handle URLs (if any) and return in-memory (if any)
    integration_options["flat_field"] = flat_field
    integration_options["do_flat"] = do_flat
    return flatfield


def _extract_darkcurrent(integration_options: dict) -> Optional[numpy.ndarray]:
    """Integration options related to the dark-current:

    * dark_current: URL(s) (list of strings or comma separate string) or None
    * do_dark: use flat_field or not
    * darkcurrent: URL(s) (list of strings or comma separate string), array or None (overwrites dark_current and do_dark when not None)

    When a numpy array is returned, the dark current is removed from the integration options.
    """
    # Typically from a JSON configuration file
    dark_current = _get_image_urls(integration_options, "dark_current", "do_dark")
    do_dark = bool(dark_current)

    # Typically in memory from a previous calculation
    darkcurrent = integration_options.pop("darkcurrent", None)
    if isinstance(darkcurrent, str):
        darkcurrent = [s.strip() for s in darkcurrent.split(",")]
    if isinstance(darkcurrent, Sequence) and isinstance(darkcurrent[0], str):
        dark_current = darkcurrent
        darkcurrent = None
        do_dark = True
    if darkcurrent is not None:
        dark_current = None
        do_dark = False

    # Let pyFAI handle URLs (if any) and return in-memory (if any)
    integration_options["dark_current"] = dark_current
    integration_options["do_dark"] = do_dark
    return darkcurrent


def compile_integration_info(ewoks_pyfai_options: Mapping, **extra) -> Dict[str, Any]:
    """Compile information on a pyFAI integration process. Add and rename keys when appropriate."""
    integration_info = dict(ewoks_pyfai_options)

    mask = _extract_mask(integration_info)
    flatfield = _extract_flatfield(integration_info)
    darkcurrent = _extract_darkcurrent(integration_info)

    # Do not save the in-memory make, flat field and dark current
    if mask is not None:
        integration_info["mask_file"] = "[...]"
    if flatfield is not None:
        integration_info["flat_field"] = "[...]"
    if darkcurrent is not None:
        integration_info["dark_current"] = "[...]"

    for k, v in extra.items():
        if v is not None:
            integration_info[k] = v
    wavelength = integration_info.get("wavelength")
    if wavelength is not None:
        integration_info["energy"] = energy_wavelength(wavelength)
    return integration_info


def _get_image_urls(
    integration_options: dict, image_urls_key: str, use_image_urls_key: str
) -> Union[str, List[str], None]:
    """Return image URL(s) (list of strings or comma separate string)
    or `None` when there are no image URL(s) or when the value of
    `"use_image_urls_key"` is explicitly set to `False`.
    """
    image_urls = integration_options.get(image_urls_key, None)
    use_image = integration_options.get(use_image_urls_key, None)
    if use_image is not False and image_urls:
        # Non-empty string or list of strings
        return image_urls


def integration_info_as_text(integration_info: Mapping, **extra) -> List[str]:
    """Convert to a flat list of strings with the format `{key} = {value}`.
    Add keys and units when appropriate.
    """
    flatdict = {"pyfai_version": _PYFAI_VERSION, "ewoks_version": _EWOKS_VERSION}
    flatdict.update(integration_info)
    _add_extra(flatdict, extra)
    flatdict = dict(_flatten_dict(flatdict))

    energy = flatdict.pop("energy", None)
    if energy:
        flatdict["energy"] = f"{energy:.18e} keV"

    wavelength = flatdict.pop("wavelength", None)
    if wavelength is not None:
        flatdict["wavelength"] = f"{wavelength:.18e} m"

    geometry_dist = flatdict.pop("geometry.dist", None)
    if geometry_dist is not None:
        flatdict["distance"] = f"{geometry_dist:.18e} m"

    geometry_poni1 = flatdict.pop("geometry.poni1", None)
    if geometry_poni1 is not None:
        flatdict["center dim0"] = f"{geometry_poni1:.18e} m"

    geometry_poni2 = flatdict.pop("geometry.poni2", None)
    if geometry_poni2 is not None:
        flatdict["center dim1"] = f"{geometry_poni2:.18e} m"

    geometry_rot1 = flatdict.pop("geometry.rot1", None)
    if geometry_rot1 is not None:
        flatdict["rot1"] = f"{geometry_rot1:.18e} rad"

    geometry_rot2 = flatdict.pop("geometry.rot2", None)
    if geometry_rot2 is not None:
        flatdict["rot2"] = f"{geometry_rot2:.18e} rad"

    geometry_rot3 = flatdict.pop("geometry.rot3", None)
    if geometry_rot3 is not None:
        flatdict["rot3"] = f"{geometry_rot3:.18e} rad"

    return [f"{k} = {v}" for k, v in flatdict.items()]


def integration_info_as_nxdict(
    integration_info: Optional[Dict[str, Any]], as_nxnote: bool = True
) -> Dict[str, Any]:
    """Convert to a Nexus dictionary. Add keys and units when appropriate."""
    configuration: Dict[str, Any] = {"ewoks_version": _EWOKS_VERSION}
    if integration_info:
        configuration.update(integration_info)
    nxtree_dict: Dict[str, Any] = {
        "@NX_class": "NXprocess",
        "program": "pyFAI",
        "version": _PYFAI_VERSION,
    }
    if as_nxnote:
        nxtree_dict["configuration"] = {
            "@NX_class": "NXnote",
            "type": "application/json",
            "data": json.dumps(configuration, cls=PyFaiEncoder),
        }
    else:
        configuration["@NX_class"] = "NXcollection"
        nxtree_dict["configuration"] = configuration
        if "energy" in configuration:
            configuration["energy@units"] = "keV"
        if "wavelength" in configuration:
            configuration["wavelength@units"] = "m"
        geometry = configuration.get("geometry", dict())
        if "dist" in geometry:
            geometry["dist@units"] = "m"
        if "poni1" in geometry:
            geometry["poni1@units"] = "m"
        if "poni2" in geometry:
            geometry["poni1@units"] = "m"
        if "rot1" in geometry:
            geometry["rot1@units"] = "rad"
        if "rot2" in geometry:
            geometry["rot2@units"] = "rad"
        if "rot3" in geometry:
            geometry["rot3@units"] = "rad"
    return nxtree_dict


class PyFaiEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (numpy.generic, numpy.ndarray)):
            return obj.tolist()
        if isinstance(obj, DataUrl):
            return obj.path()
        return super().default(obj)


def _flatten_dict(
    adict: Mapping, _prefix: Optional[str] = None
) -> Iterator[Tuple[str, Any]]:
    if _prefix is None:
        _prefix = ""
    for k, v in adict.items():
        k = _prefix + k
        if isinstance(v, Mapping):
            yield from _flatten_dict(v, _prefix=f"{k}.")
        else:
            yield k, v


def _add_extra(adict: Mapping, extra: Mapping):
    for k, v in extra.items():
        if v is not None:
            adict[k] = v


def create_nxprocess(
    parent: h5py.Group,
    link_parent: h5py.Group,
    nxprocess_name: str,
    info: Optional[Dict[str, Any]],
    overwrite: bool = False,
) -> h5py.Group:
    """Create NXprocess group in the external parent with link in the parent when these are different groups."""
    nxtree_dict = integration_info_as_nxdict(info)
    nxprocess_path = f"{parent.name}/{nxprocess_name}"
    dicttonx(nxtree_dict, parent.file, h5path=nxprocess_path, update_mode="modify")
    nxprocess = parent[nxprocess_name]
    create_hdf5_link(link_parent, nxprocess_name, nxprocess, overwrite=overwrite)
    return nxprocess


def create_integration_results_nxdata(
    nxprocess: h5py.Group,
    intensity_dim: int,
    radial: numpy.ndarray,
    radial_units: str,
    azimuthal: Union[numpy.ndarray, None],
    azimuthal_units: str,
    overwrite: bool = False,
) -> h5py.Group:
    group_name = "integrated"
    if overwrite and group_name in nxprocess:
        del nxprocess[group_name]
    nxdata = nxprocess.create_group(group_name)
    nxdata.attrs["NX_class"] = "NXdata"
    nxprocess.attrs["default"] = group_name

    # Axes interpretation
    add_axes_to_nxdata(
        nxdata, intensity_dim, radial, radial_units, azimuthal, azimuthal_units
    )

    return nxdata


def add_axes_to_nxdata(
    nxdata: h5py.Group,
    intensity_dim: int,
    radial: numpy.ndarray,
    radial_units,
    azimuthal: Union[numpy.ndarray, None],
    azimuthal_units,
):
    # Axes names and units
    radial_units = data_from_storage(radial_units, remove_numpy=True)
    try:
        radial_axis = parse_string_units(radial_units)
    except ValueError as e:
        raise TaskInputError(e)
    has_azimuth = not is_missing_data(azimuthal) and azimuthal is not None
    if has_azimuth:
        azimuthal_axis = parse_string_units(azimuthal_units)

    if has_azimuth and intensity_dim == 2:
        nxdata.attrs["axes"] = [azimuthal_axis.name, radial_axis.name]
        nxdata.attrs["interpretation"] = "image"
    elif has_azimuth and intensity_dim == 3:
        nxdata.attrs["axes"] = [".", azimuthal_axis.name, radial_axis.name]
        nxdata.attrs["interpretation"] = "image"
    elif not has_azimuth and intensity_dim == 2:
        nxdata.attrs["axes"] = [".", radial_axis.name]
        nxdata.attrs["interpretation"] = "spectrum"
    elif not has_azimuth and intensity_dim == 1:
        nxdata.attrs["axes"] = [radial_axis.name]
        nxdata.attrs["interpretation"] = "spectrum"
    else:
        raise ValueError("Unrecognized data")

    dset = nxdata.create_dataset(radial_axis.name, data=radial)
    dset.attrs["units"] = radial_axis.units
    if has_azimuth:
        dset = nxdata.create_dataset(azimuthal_axis.name, data=azimuthal)
        dset.attrs["units"] = azimuthal_axis.units
