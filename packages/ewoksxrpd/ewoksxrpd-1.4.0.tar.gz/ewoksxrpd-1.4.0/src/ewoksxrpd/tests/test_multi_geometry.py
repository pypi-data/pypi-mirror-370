import json
from pathlib import Path
from typing import Any
from typing import Dict

import h5py
import numpy
import pytest
from silx.io.url import DataUrl

from ..tasks.integrate import IntegrateBlissScan
from ..tasks.multi_geometry_integrate import Integrate2DMultiGeometry
from . import xrpd_theory


@pytest.fixture
def gonio_file(tmp_path: Path) -> Path:
    gonio_json = {
        "content": "Goniometer calibration v2",
        "detector": "Pilatus1M",
        "wavelength": 2.6379616687914948e-11,
        "param": [
            2.0062960356379422,
            0.015883422992655393,
            0.8216006393975213,
            0.002164173240804926,
            -0.0031180017089310853,
            0.0063336570464145835,
            0.004297460651999008,
        ],
        "param_names": ["dist", "poni1", "poni2", "rot1", "rot2", "rot_x", "rot_y"],
        "pos_names": ["pos"],
        "trans_function": {
            "content": "GeometryTransformation",
            "param_names": ["dist", "poni1", "poni2", "rot1", "rot2", "rot_x", "rot_y"],
            "pos_names": ["pos"],
            "dist_expr": "dist",
            "poni1_expr": "poni1 + rot_x*cos(pos) - rot_y*sin(pos)",
            "poni2_expr": "poni2 + rot_x*sin(pos) + rot_y*cos(pos)",
            "rot1_expr": "+rot1*cos(pos) - rot2*sin(pos)",
            "rot2_expr": "+rot1*sin(pos) + rot2*cos(pos)",
            "rot3_expr": "pos",
            "constants": {"pi": 3.141592653589793},
        },
    }
    filename = tmp_path / "gonio.json"
    with open(filename, "w") as f:
        json.dump(gonio_json, f)

    return filename


@pytest.fixture
def image_data_url(
    imageSetup1Calibrant1: xrpd_theory.Calibration, tmp_path: Path
) -> DataUrl:
    assert isinstance(imageSetup1Calibrant1, xrpd_theory.Calibration)
    images = numpy.zeros(shape=(10, *imageSetup1Calibrant1.image.shape))
    for i in range(10):
        images[i] = imageSetup1Calibrant1.image
    h5_path = tmp_path / "output.h5"
    dataset_path = "/entry/data"
    with h5py.File(h5_path, "w") as h5file:
        h5file.create_dataset(dataset_path, data=images)
    return DataUrl(file_path=str(h5_path), data_path=dataset_path)


def test_multi_geometry_task(image_data_url: DataUrl, gonio_file: Path):
    task = Integrate2DMultiGeometry(
        inputs={
            "goniometer_file": gonio_file,
            "integration_options": {"npt_rad": 300, "npt_azim": 180},
            "images": image_data_url.path(),
            "positions": [*numpy.linspace(0, 360, 10)],
        }
    )

    task.execute()

    assert task.get_output_value("radial").shape == (300,)
    assert task.get_output_value("azimuthal").shape == (180,)
    assert task.get_output_value("intensity").shape == (180, 300)


def test_integration_options_consistency(
    bliss_task_inputs: Dict[str, Any],
    image_data_url: DataUrl,
    gonio_file: Path,
    tmp_path: Path,
):
    N_2TH = 300
    N_CHI = 180
    RADIAL_MIN = 0
    RADIAL_MAX = 50
    integration_options = {
        "nbpt_rad": N_2TH,
        "nbpt_azim": N_CHI,
        "radial_range_min": 0,
        "radial_range_max": 50,
    }

    mg_task = Integrate2DMultiGeometry(
        inputs={
            "goniometer_file": gonio_file,
            "integration_options": integration_options,
            "images": image_data_url.path(),
            "positions": [*numpy.linspace(0, 360, 10)],
        }
    )

    mg_task.execute()

    radial = mg_task.get_output_value("radial")
    assert radial.shape == (N_2TH,)
    assert radial.min() > RADIAL_MIN
    assert radial.max() < RADIAL_MAX
    assert mg_task.get_output_value("azimuthal").shape == (N_CHI,)
    assert mg_task.get_output_value("intensity").shape == (N_CHI, N_2TH)

    sg_task = IntegrateBlissScan(
        inputs={
            **bliss_task_inputs,
            "integration_options": {
                **integration_options,
                "integrator_name": "integrate2d_ng",
            },
            "output_filename": tmp_path / "output.h5",
        }
    )

    sg_task.execute()

    with h5py.File(tmp_path / "output.h5", "r") as h5file:
        n_frames = len(h5file["/2.1/measurement/p3"])
        integrated_grp = h5file["/2.1/p3_integrate/integrated"]
        assert isinstance(integrated_grp, h5py.Group)

        radial = integrated_grp["2th"][()]
        assert radial.shape == (N_2TH,)
        assert radial.min() > RADIAL_MIN
        assert radial.max() < RADIAL_MAX
        assert integrated_grp["chi"].shape == (N_CHI,)
        assert integrated_grp["intensity"].shape == (n_frames, N_CHI, N_2TH)
