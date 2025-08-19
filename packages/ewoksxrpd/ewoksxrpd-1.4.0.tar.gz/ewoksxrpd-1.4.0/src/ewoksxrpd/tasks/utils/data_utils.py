import os
from typing import Mapping, Union, Optional
from typing_extensions import TypeGuard
from numbers import Number

import h5py
import numpy
import fabio.edfimage
import fabio.tifimage
from silx.io.url import DataUrl
from blissdata.h5api import dynamic_hdf5


def hdf5_url(file_name: str, data_path: str) -> str:
    if not os.path.isabs(file_name):
        file_name = os.path.abspath(file_name)
    return f"silx://{file_name}?path={data_path}"


def is_data(data) -> TypeGuard[Union[numpy.ndarray, Number, str, list]]:
    if isinstance(data, (numpy.ndarray, Number)):
        return True
    if isinstance(data, (str, list)) and data:
        return True
    return False


def data_from_storage(data, remove_numpy=True):
    if isinstance(data, numpy.ndarray):
        if not remove_numpy:
            return data
        elif data.ndim == 0:
            return data.item()
        else:
            return data.tolist()
    elif isinstance(data, Mapping):
        return {
            k: data_from_storage(v, remove_numpy=remove_numpy)
            for k, v in data.items()
            if not k.startswith("@")
        }
    else:
        return data


def create_hdf5_link(
    parent: h5py.Group,
    link_name: str,
    target: Union[h5py.Dataset, h5py.Group],
    relative: bool = True,
    raise_on_exists: bool = False,
    overwrite: bool = False,
) -> None:
    """
    :param parent: HDF5 group in which the link will be created
    :param link_name: relative HDF5 path of the link source with respect to :code:`parent`
    :param target: absolute HDF5 path of the link target
    :param relative: determines whether the external or internal link is absolute or relative.
                     Internal links that refer upwards are not supported and will always be absolute.
    :param raise_on_exists: raise exception when :code:`link_name` already exists
    :param overwrite: Set to True to allow overwriting existing link_name
    """
    link = hdf5_link_object(
        _get_hdf5_filename(parent.file),
        parent.name,
        link_name,
        _get_hdf5_filename(target.file),
        target.name,
        relative=relative,
    )
    if link is None:
        # Link refers to itself
        return
    if overwrite and link_name in parent:
        del parent[link_name]
    if link_name in parent and not raise_on_exists:
        # Name already exists and is not necessarily equivalent to the link we want to create
        return
    parent[link_name] = link


def _get_hdf5_filename(file_obj) -> str:
    try:
        return file_obj.filename
    except AttributeError:
        # to be fixed in blissdata
        return file_obj._retry_handler.file_obj.filename


def hdf5_link_object(
    parent_filename: str,
    parent_name: str,
    link_name: str,
    target_filename: str,
    target_name: str,
    relative: bool = True,
) -> Union[None, h5py.ExternalLink, h5py.SoftLink]:
    """
    :param parent_filename: HDF5 filename in which the link will be created
    :param parent_name: absolute HDF5 group path in :code:`parent_filename`
    :param link_name: relative HDF5 path of the link source with respect to :code:`parent_name`
    :param target_filename: HDF5 filename in which the link target is located
    :param target_name: absolute HDF5 path in :code:`target_filename` of the link target
    :param relative: determines whether the external or internal link is absolute or relative.
                     Internal links that refer upwards are not supported and will always be absolute.
    :returns: Internal or external link object to be used to create the HDF5 link.
              Returns :code:`None` when the link refers to itself.
    """
    abs_parent_filename = os.path.abspath(parent_filename)
    target_is_absolute = os.path.isabs(target_filename)
    if target_is_absolute:
        abs_target_filename = target_filename
    else:
        abs_target_filename = os.path.join(
            os.path.dirname(abs_parent_filename), target_filename
        )

    # Internal link
    if os.path.normpath(abs_parent_filename) == os.path.normpath(abs_target_filename):
        link_full_name = _normalize_hdf5_item_name(parent_name, link_name)
        target_name = _normalize_hdf5_item_name(target_name)
        if link_full_name == target_name:
            # Link refers to itself
            return
        if not relative:
            return h5py.SoftLink(target_name)
        rel_target_name = os.path.relpath(target_name, parent_name)
        if ".." in rel_target_name:
            # Internal links upwards are not supported
            return h5py.SoftLink(target_name)
        return h5py.SoftLink(rel_target_name)

    # External link
    if relative:
        target_filename = os.path.relpath(
            abs_target_filename, os.path.dirname(abs_parent_filename)
        )
    else:
        target_filename = abs_target_filename
    return h5py.ExternalLink(target_filename, target_name)


def _normalize_hdf5_item_name(*parts) -> str:
    name = "/".join([s for part in parts for s in part.split("/") if s])
    return f"/{name}"


def link_bliss_scan(
    outentry: h5py.Group, bliss_scan_url: Union[str, DataUrl], **kwargs
):
    if isinstance(bliss_scan_url, str):
        bliss_scan_url = DataUrl(bliss_scan_url)
    file_path = bliss_scan_url.file_path()
    data_path = bliss_scan_url.data_path()
    out_filename = outentry.file.filename
    ext_filename = os.path.relpath(out_filename, os.path.dirname(file_path))
    if ".." in ext_filename:
        ext_filename = file_path
    with dynamic_hdf5.File(file_path, mode="r", **kwargs) as root:
        inentry = root[data_path]
        # Wait until the file has finished writing
        _ = inentry["end_time"]
        # Link to the entire group
        for groupname in ("instrument", "sample"):
            try:
                if groupname in outentry or groupname not in inentry:
                    continue
            except Exception:  # fixed by bliss PR !5435
                continue
            create_hdf5_link(outentry, groupname, inentry[groupname])

        # Link to all sub groups
        for groupname in ("measurement",):
            if groupname not in inentry:
                continue
            igroup = inentry[groupname]
            if groupname in outentry:
                ogroup = outentry[groupname]
            else:
                ogroup = outentry.create_group(groupname)
                ogroup.attrs["NX_class"] = igroup.attrs["NX_class"]
            for name in igroup.keys():
                if name in ogroup:
                    continue
                if name not in ogroup:
                    create_hdf5_link(ogroup, name, igroup[name])


def convert_to_3d(data: Union[numpy.ndarray, Number, str, list]):
    data_arr = numpy.array(data)

    if data_arr.ndim >= 3:
        return data_arr

    if data_arr.ndim == 2:
        return data_arr.reshape(1, *data_arr.shape)

    if data_arr.ndim == 1:
        return data_arr.reshape(1, 1, *data_arr.shape)

    return data_arr.reshape(1, 1, 1)


def save_image(
    data: numpy.ndarray,
    save_path: str,
    save_name: str,
    monitor_data: Optional[Number] = None,
    metadata: Optional[dict] = None,
    ext: str = "edf",
) -> str:
    normalized_data = data / monitor_data if monitor_data else data

    header = dict(
        Summed_monitor_counts=str(monitor_data) if monitor_data else "nan",
        **(metadata if metadata else {}),
    )

    ext = ext.lower()
    img_filepath = f"{save_path}/{save_name}.{ext}"
    if ext.lower() == "edf":
        Image = fabio.edfimage.EdfImage
    elif ext == "tiff" or ext == "tif":
        Image = fabio.tifimage.TifImage
    else:
        raise ValueError(f"Unsupported ext {ext}. Only supports EDF and TIFF.")

    img = Image(data=normalized_data, header=header)
    img.write(img_filepath)

    return img_filepath
