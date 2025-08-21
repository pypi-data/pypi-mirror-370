import os
import time
from contextlib import ExitStack
from typing import Optional, Iterator, Generator, Tuple, Any

import h5py
from ewokscore import Task
from blissdata.h5api import dynamic_hdf5

from .data_access import TaskWithDataAccess
from .utils.sum_utils import save_sum
from .utils.sum_utils import ImageSum
from .utils.sum_utils import generate_range
from .utils.data_utils import hdf5_url

SUM_TYPES = ["per_scan", "all_scans", "both"]


class SumBlissScanImages(
    TaskWithDataAccess,
    input_names=["filename", "scan", "detector_name", "output_filename"],
    optional_input_names=[
        "monitor_name",
        "subscan",
        "scan_memory_url",
        "output_process",
        "background_step",
    ],
    output_names=["output_uri", "monitor"],
):
    """Sum images of a single camera of a single Bliss scan"""

    def run(self):
        with ExitStack() as stack:
            self._run_in_stack(stack)

    def _run_in_stack(self, stack: ExitStack):
        filename: str = self.inputs.filename
        scan: int = self.inputs.scan
        subscan = self.get_input_value("subscan", 1)
        detector_name: str = self.inputs.detector_name
        output_filename: str = self.inputs.output_filename
        output_nxentry_url = hdf5_url(output_filename, f"/{scan}.{subscan}")
        monitor_name: Optional[str] = self.get_input_value("monitor_name", None)
        output_nxprocess_name: str = self.get_input_value("output_process", "sum")
        background_step: bool = self.get_input_value("background_step", 1)

        if self.inputs.scan_memory_url:
            raise NotImplementedError("data from memory not supported yet")
        else:
            lima_iterator_context = self.iter_bliss_data(
                filename,
                scan,
                lima_names=[detector_name],
                subscan=subscan,
            )
            lima_iterator = stack.enter_context(lima_iterator_context)

            with dynamic_hdf5.File(
                filename, lima_names=[detector_name], **self.get_retry_options()
            ) as root:
                data_name = f"{scan}.{subscan}/instrument/{detector_name}/data"
                # getting the shape should block until the end of the scan
                dataset_shape = root[data_name].shape
                nb_points_in_scan = dataset_shape[0]

            if monitor_name:
                counter_iterator_context = self.iter_bliss_data(
                    filename,
                    scan,
                    counter_names=[monitor_name],
                    lima_names=[],
                    subscan=subscan,
                )
                counter_iterator = stack.enter_context(counter_iterator_context)
            else:
                counter_iterator = (
                    {monitor_name: None} for _ in range(nb_points_in_scan)
                )

        with self.open_h5item(output_nxentry_url, mode="a", create=True) as nxentry:
            nxprocess = nxentry.create_group(output_nxprocess_name)
            nxprocess.attrs["NX_class"] = "NXprocess"
            nxprocess.attrs["default"] = "results"
            nxdata = nxprocess.create_group("results")
            nxdata.attrs["NX_class"] = "NXdata"

            scan_sum = None
            summed_indices = []

            tstart = time.time()
            for scan_index, ctrdata in iterate_scan_with_skip(
                counter_iterator, background_step
            ):
                limadata = next(lima_iterator)

                image = limadata[detector_name]
                if scan_sum is None:
                    scan_sum = ImageSum(image.shape)

                scan_sum.add_to_sum(image, monitor=ctrdata[monitor_name])
                summed_indices.append(scan_index)

            if scan_sum is None:
                tend = time.time()
                raise RuntimeError(
                    f"No scan data yielded within {tend-tstart:03f} from {filename}::/{scan}.{subscan}"
                )

            image_dset, monitor_dset = save_sum(
                nxdata,
                name=f"Scan{scan}-Images{summed_indices[0]}-{summed_indices[-1]}",
                image_sum=scan_sum,
            )

            self.outputs.output_uri = f"{nxdata.file.filename}::{image_dset.name}"
            if monitor_dset is not None:
                self.outputs.monitor = scan_sum.summed_monitor
            else:
                self.outputs.monitor = None


def iterate_scan_with_skip(
    scan_iterator: Iterator[Any], step: int
) -> Generator[Tuple[int, Any], None, None]:
    """
    :param scan_iterator: iterate over all scan points
    :param step: -1 means no skipping, 0 means skipping the first, N>0 means skipping every N points starting from 0
    :yields: the non-skipped scan index and corresponding data
    """
    if step < 0:  # no skipping
        for scan_index, data in enumerate(scan_iterator):
            yield scan_index, data
    elif step == 0:  # skip the first
        for scan_index, data in enumerate(scan_iterator):
            if scan_index == 0:
                continue
            yield scan_index, data
    else:  # skip every N points, starting from zero
        block_size = step + 1
        for scan_index, data in enumerate(scan_iterator):
            if (scan_index % block_size) == 0:
                continue
            yield scan_index, data


class SumImages(
    Task,
    input_names=["filename", "detector_name", "output_filename"],
    optional_input_names=[
        "start_scan",
        "end_scan",
        "start_image",
        "end_image",
        "block_size",
        "monitor_name",
        "output_entry",
        "output_process",
        "sum_type",
    ],
    output_names=["output_uris", "monitor_uris"],
):
    """Sum images of a single camera from a Bliss scan file

    For each scan, images are added in blocks of `block_size` images (one block with all images by default).

    The result contains:
        * the block sums when sum_type=per_scan or sum_type=both
        * the sum of the block sums when sum_type=all_scans or sum_type=both
    """

    def run(self):
        filename: str = self.inputs.filename
        detector_name: str = self.inputs.detector_name
        output_filename: str = self.inputs.output_filename
        start_scan: int = self.get_input_value("start_scan", 1)
        end_scan: Optional[int] = self.get_input_value("end_scan", None)
        start_image: int = self.get_input_value("start_image", 0)
        end_image: Optional[int] = self.get_input_value("end_image", None)
        block_size: Optional[int] = self.get_input_value("block_size", None)
        monitor_name: Optional[str] = self.get_input_value("monitor_name", None)
        output_entry: str = self.get_input_value("output_entry", "processing")
        output_process: str = self.get_input_value("output_process", "sum")
        sum_type: str = self.get_input_value("sum_type", "per_scan")

        if sum_type not in SUM_TYPES:
            raise TypeError(
                f"sum_type must be one of the following values: {SUM_TYPES}. Got {sum_type} instead."
            )
        save_scan_sums = sum_type == "per_scan" or sum_type == "both"
        save_full_sum = sum_type == "all_scans" or sum_type == "both"

        same_h5file = os.path.abspath(os.path.normpath(filename)) == os.path.abspath(
            os.path.normpath(output_filename)
        )
        if same_h5file:
            mode = "a"
        else:
            mode = "r"

        with h5py.File(filename, mode=mode) as h5infile:
            nscans = len(h5infile)
            scan_range = generate_range(start_scan, end_scan, nscans + 1)

            first_scan_name = list(h5infile.keys())[0]
            nimages, *detector_shape = h5infile[
                f"{first_scan_name}/measurement/{detector_name}"
            ].shape
            image_range = list(generate_range(start_image, end_image, nimages))

            scan_sum = ImageSum(detector_shape)
            full_sum = ImageSum(detector_shape)

            with h5py.File(output_filename, mode="a") as h5outfile:
                out_entry = h5outfile.require_group(output_entry)
                out_entry.attrs.setdefault("NX_class", "NXentry")
                out_entry.attrs["default"] = output_process
                out_process = out_entry.create_group(output_process)
                out_process.attrs["NX_class"] = "NXprocess"
                out_process.attrs["default"] = "results"
                out_results = out_process.create_group("results")
                out_results.attrs["NX_class"] = "NXdata"

                output_uris: list[str] = []
                monitor_uris: list[str] = []
                for scan_number in scan_range:
                    scan_images = h5infile[
                        f"{scan_number}.1/measurement/{detector_name}"
                    ]
                    scan_monitor = (
                        h5infile[f"{scan_number}.1/measurement/{monitor_name}"]
                        if monitor_name
                        else None
                    )
                    assert isinstance(scan_images, h5py.Dataset)
                    if scan_monitor is not None:
                        assert isinstance(scan_monitor, h5py.Dataset)

                    for image_number in image_range:
                        image = scan_images[image_number]
                        monitor = scan_monitor[image_number] if scan_monitor else None
                        scan_sum.add_to_sum(image, monitor)
                        full_sum.add_to_sum(image, monitor)

                        if save_scan_sums and scan_sum.nb_images == block_size:
                            name = f"Scan{scan_number}-Images{image_number - scan_sum.nb_images + 1}-{image_number}"
                            image_dset, monitor_dset = save_sum(
                                out_results, name=name, image_sum=scan_sum
                            )
                            output_uris.append(f"{output_filename}::{image_dset.name}")
                            if monitor_dset is not None:
                                monitor_uris.append(
                                    f"{output_filename}::{monitor_dset.name}"
                                )

                            # Move to next sum
                            scan_sum.reset()

                    if save_scan_sums and scan_sum.nb_images > 0:
                        name = f"Scan{scan_number}-Images{image_number - scan_sum.nb_images + 1}-{image_number}"
                        image_dset, monitor_dset = save_sum(
                            out_results, name=name, image_sum=scan_sum
                        )
                        output_uris.append(f"{output_filename}::{image_dset.name}")
                        if monitor_dset is not None:
                            monitor_uris.append(
                                f"{output_filename}::{monitor_dset.name}"
                            )

                if save_full_sum:
                    name = f"Sum of scans {scan_range.start} to {scan_range.stop - scan_range.step}"
                    image_dset, monitor_dset = save_sum(
                        out_results, name=name, image_sum=full_sum
                    )
                    output_uris.append(f"{output_filename}::{image_dset.name}")
                    if monitor_dset is not None:
                        monitor_uris.append(f"{output_filename}::{monitor_dset.name}")

        self.outputs.output_uris = output_uris
        if monitor_uris:
            self.outputs.monitor_uris = monitor_uris
        else:
            self.outputs.monitor_uris = None
