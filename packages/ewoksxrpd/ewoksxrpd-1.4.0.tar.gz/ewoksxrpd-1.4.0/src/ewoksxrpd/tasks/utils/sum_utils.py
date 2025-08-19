from __future__ import annotations
import h5py
import numpy


class ImageSum:
    def __init__(self, shape) -> None:
        self.shape = shape
        self.summed_image = numpy.zeros(shape)
        self.summed_monitor = None
        self.nb_images = 0

    def add_to_sum(self, image: numpy.ndarray, monitor: int | None):
        self.summed_image += image
        if monitor is not None:
            if self.summed_monitor is None:
                self.summed_monitor = 0
            self.summed_monitor += monitor
        self.nb_images += 1

    def reset(self):
        self.summed_image = numpy.zeros(self.shape)
        self.summed_monitor = None
        self.nb_images = 0


def generate_range(start: int, end_arg: int | None, nitems: int) -> range:
    end = nitems if end_arg is None else end_arg + 1

    if (end - start) > nitems:
        raise ValueError(
            f"Asked range ({start},{end}) is bigger than number of items ({nitems})"
        )

    return range(start, end)


def save_sum(
    nxdata: h5py.Group, name: str, image_sum: ImageSum
) -> tuple[h5py.Dataset, h5py.Dataset | None]:
    nxdata.create_dataset(f"{name}_nb_images", data=image_sum.nb_images)

    image_dset = nxdata.create_dataset(name, data=image_sum.summed_image)
    if "signal" not in nxdata:
        nxdata.attrs["signal"] = name

    summed_monitor = image_sum.summed_monitor
    if summed_monitor is None:
        return image_dset, None
    monitor_dset = nxdata.create_dataset(f"{name}_monitor", data=summed_monitor)
    return image_dset, monitor_dset
