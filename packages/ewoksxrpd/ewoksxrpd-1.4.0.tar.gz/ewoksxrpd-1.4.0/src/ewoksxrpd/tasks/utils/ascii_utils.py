from __future__ import annotations

import io
import os
from typing import Any, Dict, Mapping, Union
import numpy

from .data_utils import is_data
from .pyfai_utils import integration_info_as_text


def ensure_parent_folder(filename: str):
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)


def save_pattern_as_ascii(
    filename: str | io.TextIOBase,
    x: numpy.ndarray,
    y: numpy.ndarray,
    xunits: str,
    yerror: Union[numpy.ndarray, None],
    header: Mapping,
    metadata: Dict[str, Any],
) -> None:
    if is_data(yerror):
        data = [x, y, yerror]
        columns = ["x", "intensity", "intensity_error"]
    else:
        data = [x, y]
        columns = ["x", "intensity"]
    data = numpy.stack(data, axis=1)

    lines = integration_info_as_text(header, xunits=xunits, **metadata)
    lines.append(" ".join(columns))

    if isinstance(filename, str):
        ensure_parent_folder(filename)
    numpy.savetxt(filename, data, header="\n".join(lines))
