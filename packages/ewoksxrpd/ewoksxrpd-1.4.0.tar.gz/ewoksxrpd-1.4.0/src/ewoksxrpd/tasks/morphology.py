import numpy
from numpy.typing import ArrayLike
from numbers import Number

try:
    from pyFAI.ext import morphology

    def binary_dilation(mask: ArrayLike, hwhm: Number):
        fwhm = int(round(2.0 * hwhm))
        return morphology.binary_dilation(mask.astype(numpy.int8), fwhm)

except ImportError:
    from scipy.ndimage import morphology

    def binary_dilation(mask: ArrayLike, hwhm: Number):
        fwhm = int(round(2.0 * hwhm))
        my, mx = numpy.ogrid[-fwhm : fwhm + 1, -fwhm : fwhm + 1]
        grow = (mx * mx + my * my) <= (4.0 * hwhm * hwhm)
        return morphology.binary_dilation(mask, grow)
