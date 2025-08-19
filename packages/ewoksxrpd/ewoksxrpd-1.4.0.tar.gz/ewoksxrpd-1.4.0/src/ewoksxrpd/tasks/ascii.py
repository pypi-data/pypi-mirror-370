from __future__ import annotations

import logging
import os
import zipfile
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Mapping
from typing import Sequence
from typing import Tuple

import numpy
from ewokscore import Task

from .utils import zip_utils
from .data_access import TaskWithDataAccess
from .utils.ascii_utils import ensure_parent_folder
from .utils.ascii_utils import save_pattern_as_ascii
from .utils.nexus_utils import IntegratedPattern
from .utils.nexus_utils import read_nexus_integrated_patterns

logger = logging.getLogger(__name__)


__all__ = [
    "SaveAsciiPattern1D",
    "SaveAsciiMultiPattern1D",
    "SaveNexusPatternsAsAscii",
]


class SaveAsciiPattern1D(
    Task,
    input_names=["filename", "x", "y", "xunits"],
    optional_input_names=["header", "yerror", "metadata"],
    output_names=["saved"],
):
    """Save single diffractogram in ASCII format"""

    def run(self):
        header = self.get_input_value("header", dict())
        metadata = self.get_input_value("metadata", dict())
        yerror = self.get_input_value("yerror", None)

        save_pattern_as_ascii(
            self.inputs.filename,
            self.inputs.x,
            self.inputs.y,
            self.inputs.xunits,
            yerror,
            header,
            metadata,
        )
        self.outputs.saved = True


class SaveAsciiMultiPattern1D(
    Task,
    input_names=["filenames", "x_list", "y_list", "xunits_list"],
    optional_input_names=["header_list", "yerror_list", "metadata_list"],
    output_names=["saved"],
):
    def run(self):
        filenames: Sequence[str] = self.inputs.filenames
        x_list: Sequence[numpy.ndarray] = self.inputs.x_list
        y_list: Sequence[numpy.ndarray] = self.inputs.y_list
        xunits_list: Sequence[str] = self.inputs.xunits_list
        header_list: Sequence[Mapping] = self.get_input_value(
            "header_list", len(filenames) * [dict()]
        )
        yerror_list: Sequence[numpy.ndarray] | Sequence[None] = self.get_input_value(
            "yerror_list", len(filenames) * [None]
        )
        metadata_list: Sequence[Dict[str, Any]] = self.get_input_value(
            "metadata_list", len(filenames) * [dict()]
        )

        for args in zip(
            filenames,
            x_list,
            y_list,
            xunits_list,
            yerror_list,
            header_list,
            metadata_list,
        ):
            save_pattern_as_ascii(*args)

        self.outputs.saved = True


class SaveNexusPatternsAsAscii(
    TaskWithDataAccess,
    input_names=["nxdata_url", "output_filename_template"],
    optional_input_names=["header", "enabled", "output_archive_filename", "overwrite"],
    output_names=["filenames"],
):
    """Convert azimuthal integration results from NeXus to ASCII files

    One ASCII file is created for each integration pattern in nxdata_url.
    ASCII files are named from the output_filename_template and the pattern index.

    If output_archive_filename is provided, all ASCII files are stored in a single ZIP file.
    In this case, output_filename_template is the template path of ASCII files inside the ZIP file.

    Required inputs:
    - nxdata_url (str): The url of the NXData group storing the azimuthal integration results
    - output_filename_template (str): A string template containing one '%d' field.
      It is used to generate the filename from the frame number.

    Optional inputs:
    - header (dict): Information to store in ASCII file header (default: {})
    - enabled (bool): True to enable saving as ASCII files, False to skip task (default: True)
    - output_archive_filename (str): Filename of the ZIP file containing all ASCII files.
      If this is None (default) or the empty string, ZIP compression is disabled.
    - overwrite (bool): True to allow overwriting existing ASCII/ZIP files (default: False)

    Outputs:
    - filenames (tuple[str]): The names of the created ASCII files or ZIP file
    """

    def run(self):
        if not self.get_input_value("enabled", True):
            logger.info(
                f"Task {self.__class__.__qualname__} is disabled: No file is saved"
            )
            self.outputs.filenames = tuple()
            return

        output_archive_filename = self.get_input_value("output_archive_filename", None)
        overwrite = self.get_input_value("overwrite", False)
        if output_archive_filename:
            ensure_parent_folder(output_archive_filename)

            mode = "w" if overwrite else "x"
            with zipfile.ZipFile(
                output_archive_filename, mode=mode, compression=zipfile.ZIP_DEFLATED
            ) as zipf:
                with self.open_h5item(self.inputs.nxdata_url) as group:
                    for filename, pattern, metadata in self._export_data(group):
                        with zip_utils.open_in_zipfile(
                            zipf, filename, mode="w"
                        ) as file:
                            save_pattern_as_ascii(
                                file,
                                x=pattern.radial,
                                y=pattern.intensity,
                                xunits=pattern.radial_units,
                                yerror=pattern.intensity_errors,
                                header=self.get_input_value("header", {}),
                                metadata=metadata,
                            )
            self.outputs.filenames = (output_archive_filename,)
        else:
            filenames = []
            with self.open_h5item(self.inputs.nxdata_url) as group:
                for filename, pattern, metadata in self._export_data(group):
                    if not overwrite and os.path.exists(filename):
                        raise FileExistsError(f"File exists: {filename}")
                    save_pattern_as_ascii(
                        filename,
                        x=pattern.radial,
                        y=pattern.intensity,
                        xunits=pattern.radial_units,
                        yerror=pattern.intensity_errors,
                        header=self.get_input_value("header", {}),
                        metadata=metadata,
                    )
                    filenames.append(filename)
                self.outputs.filenames = tuple(filenames)

    def _export_data(self, group) -> Iterator[Tuple[str, IntegratedPattern, dict]]:
        for index, pattern in enumerate(read_nexus_integrated_patterns(group)):
            filename = self.inputs.output_filename_template % index

            if pattern.point is not None:
                metadata = {"point": pattern.point}
            else:
                metadata = {}

            yield filename, pattern, metadata
