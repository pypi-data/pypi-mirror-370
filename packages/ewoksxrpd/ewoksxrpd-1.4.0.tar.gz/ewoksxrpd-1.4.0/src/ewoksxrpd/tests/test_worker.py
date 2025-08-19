import numpy
import pytest

from ..tasks.worker import persistent_worker


def test_worker_demo():
    integrate_options = {
        "method": "no_csr_cython",
        "nbpt_rad": 4096,
        "unit": "q_nm^-1",
        "error_model": "azimuthal",
        "dist": 0.05,
        "poni1": 0.1,
        "poni2": 0.1,
        "rot1": 0.17453292519943295,
        "rot2": 0,
        "rot3": 0,
        "detector": "Pilatus1M",
        "detector_config": None,
        "wavelength": 1.0332016536100021e-10,
        "integrator_name": "sigma_clip_ng",
        "extra_options": {"max_iter": 3, "thres": 0},
    }

    # Correct Pilatus1M shape
    image = numpy.zeros((1043, 981))

    # lima-camera-simulator < 1.9.10 does not support odd image
    # shapes so blissdemo adds a border
    demo_image = numpy.zeros((1044, 982))

    with persistent_worker(integrate_options, demo=False) as worker:
        worker.process(image)
        with pytest.raises(AssertionError):
            worker.process(demo_image)

    with persistent_worker(integrate_options, demo=True) as worker:
        worker.process(demo_image)
        with pytest.raises(AssertionError):
            worker.process(image)
