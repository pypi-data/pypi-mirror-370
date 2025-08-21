try:
    from pyFAI.ext._convolution import gaussian_filter  # noqa F401
except ImportError:
    from scipy.ndimage.filters import gaussian_filter  # noqa F401
