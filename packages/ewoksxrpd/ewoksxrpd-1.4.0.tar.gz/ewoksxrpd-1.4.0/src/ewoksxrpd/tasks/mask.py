from numbers import Number
import numpy
from numpy.typing import ArrayLike

from ewoksdata.data import bliss

from .morphology import binary_dilation
from .convolution import gaussian_filter
from .data_access import TaskWithDataAccess


__all__ = ["MaskDetection"]


def smooth_mask(mask: ArrayLike, hwhm: Number = 5) -> ArrayLike:
    """
    Extracted from `pyFAI.gui.cli_calibration`
    """
    big_mask = binary_dilation(mask, hwhm)
    sigma = hwhm / numpy.sqrt(2 * numpy.log(2))
    smooth_mask = gaussian_filter(big_mask.astype(numpy.float32), sigma)
    return smooth_mask.astype(bool)


class MaskDetection(
    TaskWithDataAccess,
    input_names=["image1", "monitor1", "image2", "monitor2"],
    optional_input_names=["smooth", "monitor_ratio_margin"],
    output_names=["mask"],
):
    """The pixels with the same ratio as the monitor ratio within an error margin
    are considered "good pixels". The others are masked off.

    The error margin `monitor_ratio_margin` is a fraction of the monitor ratio (0.1 by default).

    Masked pixels have value `1`. The mask can be smoothed with `smooth > 0` to avoid border effects.

    .. code:

        monitor_ratio = monitor_high / monitor_low
        image_ratio = image_high / image_low

        bad = abs(image_ratio - monitor_ratio) > monitor_ratio * monitor_ratio_margin
    """

    def run(self):
        monitor_high = self.get_data(self.inputs.monitor1)
        monitor_low = self.get_data(self.inputs.monitor2)
        image_high = bliss.get_image(self.inputs.image1)
        image_low = bliss.get_image(self.inputs.image2)
        if monitor_high < monitor_low:
            monitor_high, monitor_low = monitor_low, monitor_high
            image_high, image_low = image_low, image_high

        monitor_ratio = monitor_high / monitor_low
        with numpy.errstate(divide="ignore", invalid="ignore"):
            image_ratio = image_high / image_low
        monitor_ratio_margin = self.get_input_value("monitor_ratio_margin", default=0.1)
        threshold = monitor_ratio * monitor_ratio_margin
        mask = numpy.abs(image_ratio - monitor_ratio) > threshold
        mask |= ~numpy.isfinite(image_ratio)

        if self.inputs.smooth:
            mask = smooth_mask(mask, self.inputs.smooth)
        self.outputs.mask = mask.astype(numpy.int8)
