from os import PathLike
import json

import numpy
import h5py

from ..tasks.integrate import MultiConfigIntegrateSinglePattern
from ..tasks.nexus import SaveNexusMultiPattern1D

from .xrpd_theory import Setup
from .xrpd_theory import Measurement
from .xrpd_theory import RadialPattern


def test_multiintegrate1d(
    imageSetup1SampleA: Measurement, setup1: Setup, xSampleA: RadialPattern
):
    configs = [
        {"nbpt_rad": 50, "unit": "2th_rad"},
        {"nbpt_rad": 50, "unit": "q_A^-1"},
        {"nbpt_rad": 100, "unit": "q_A^-1"},
    ]
    integration_options = {**setup1.integration_options, **xSampleA.integration_options}
    inputs = {
        "image": imageSetup1SampleA.image,
        "detector": setup1.detector,
        "detector_config": setup1.detector_config,
        "geometry": setup1.geometry,
        "energy": setup1.energy,
        "integration_options": integration_options,
        "configs": configs,
    }

    task = MultiConfigIntegrateSinglePattern(inputs=inputs)
    task.execute()
    output_values = task.get_output_values()

    assert len(output_values["radial_units"]) == 3
    for unit, config in zip(output_values["radial_units"], configs):
        assert unit == config["unit"]

    assert len(output_values["radial"]) == 3
    for x, config in zip(output_values["radial"], configs):
        assert len(x) == config["nbpt_rad"]

    assert len(output_values["intensity"]) == 3
    for y, config in zip(output_values["intensity"], configs):
        assert len(y) == config["nbpt_rad"]

    assert len(output_values["info"]) == 3
    for info, config in zip(output_values["info"], configs):
        assert info["nbpt_rad"] == config["nbpt_rad"]
        assert info["unit"] == config["unit"]


def test_multiintegrate2d(
    imageSetup1SampleA: Measurement, setup1: Setup, xSampleA: RadialPattern
):
    configs = [
        {"nbpt_rad": 100, "unit": "q_A^-1"},
        {"nbpt_rad": 100, "unit": "q_A^-1", "nbpt_azim": 360},
    ]
    integration_options = {**setup1.integration_options, **xSampleA.integration_options}
    inputs = {
        "image": imageSetup1SampleA.image,
        "detector": setup1.detector,
        "detector_config": setup1.detector_config,
        "geometry": setup1.geometry,
        "energy": setup1.energy,
        "integration_options": integration_options,
        "configs": configs,
    }

    task = MultiConfigIntegrateSinglePattern(inputs=inputs)
    task.execute()
    output_values = task.get_output_values()

    assert len(output_values["radial_units"]) == 2
    assert output_values["radial_units"][0] == "q_A^-1"
    assert output_values["radial_units"][1] == "q_A^-1"

    assert len(output_values["radial"]) == 2
    assert output_values["radial"][0].shape == (100,)
    assert output_values["radial"][1].shape == (100,)

    assert len(output_values["azimuthal"]) == 2
    assert output_values["azimuthal"][0] is None
    assert output_values["azimuthal"][1].shape == (360,)

    assert len(output_values["intensity"]) == 2
    assert output_values["intensity"][0].shape == (100,)
    assert output_values["intensity"][1].shape == (360, 100)

    assert len(output_values["info"]) == 2
    assert output_values["info"][0]["nbpt_rad"] == 100
    assert "nbpt_azim" not in output_values["info"][0]
    assert output_values["info"][1]["nbpt_rad"] == 100
    assert output_values["info"][1]["nbpt_azim"] == 360


def test_multisave(tmpdir: PathLike, setup1: Setup):
    npt_list = (50, 100, 200)
    inputs = {
        "url": str(tmpdir / "result.h5"),
        "x_list": [numpy.arange(npt) for npt in npt_list],
        "y_list": [numpy.random.random(npt) for npt in npt_list],
        "xunits": ["2th_deg", "q_A^-1", "q_A^-1"],
        "header_list": [
            {
                "energy": 10.2,
                "detector": setup1.detector,
                "detector_config": setup1.detector_config,
                "geometry": setup1.geometry,
                "npt_radial": npt,
            }
            for npt in npt_list
        ],
    }

    task = SaveNexusMultiPattern1D(inputs=inputs)
    task.execute()

    with h5py.File(str(tmpdir / "result.h5")) as root:
        assert set(root["results"].keys()) == {
            "measurement",
            "integrate_0",
            "integrate_1",
            "integrate_2",
            # "instrument",
            # "dummy",
        }

        for i, (npt, unit) in enumerate(zip(npt_list, inputs["xunits"])):
            nxprocess = root[f"results/integrate_{i}"]
            numpy.testing.assert_array_equal(
                nxprocess[f"integrated/{unit.split('_')[0]}"],
                inputs["x_list"][i],
            )
            numpy.testing.assert_array_equal(
                nxprocess["integrated/intensity"], inputs["y_list"][i]
            )
            numpy.testing.assert_array_equal(
                root[f"results/measurement/integrated_{i}"], inputs["y_list"][i]
            )

            config = json.loads(nxprocess["configuration"]["data"][()])
            assert set(config) == {
                "ewoks_version",
                "energy",
                "detector",
                "detector_config",
                "geometry",
                "npt_radial",
            }
            numpy.testing.assert_array_equal(config["npt_radial"], npt)
