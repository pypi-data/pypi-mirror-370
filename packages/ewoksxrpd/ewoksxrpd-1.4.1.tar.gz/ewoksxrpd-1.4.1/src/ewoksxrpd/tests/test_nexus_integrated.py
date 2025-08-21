import importlib.metadata
import json

import h5py
import numpy
import pytest
from ewoksorange.tests.utils import execute_task
from silx.io.utils import h5py_read_dataset

from orangecontrib.ewoksxrpd.nexus_integrated import OWSaveNexusIntegrated


@pytest.fixture
def common_inputs(tmpdir, setup1, bliss_lab6_scan):
    bliss_scan_url = f"{bliss_lab6_scan}::/2.1"

    return {
        "url": str(tmpdir / "result.h5"),
        "radial": numpy.linspace(1, 60, 60),
        "intensity": numpy.random.random((10, 60)),
        "radial_units": "2th_deg",
        "info": {
            "energy": 10.2,
            "detector": setup1.detector,
            "detector_config": setup1.detector_config,
            "geometry": setup1.geometry,
        },
        "metadata": {"dummy": {"test": "test"}},
        "bliss_scan_url": bliss_scan_url,
        "retry_timeout": 5,
    }


def test_save_nexus_task(common_inputs):
    assert_save_nexus_no_azimuth(common_inputs, None)


def test_save_nexus_task_with_azimuth(common_inputs):
    assert_save_nexus_with_azimuth(common_inputs, None)


def test_save_nexus_widget(common_inputs, qtapp):
    assert_save_nexus_no_azimuth(common_inputs, qtapp)


def test_save_nexus_widget_with_azimuth(common_inputs, qtapp):
    assert_save_nexus_with_azimuth(common_inputs, qtapp)


def assert_save_nexus_no_azimuth(common_inputs, qtapp):
    inputs = {
        "radial": numpy.linspace(1, 60, 60),
        "intensity": numpy.random.random((10, 60)),
        **common_inputs,
    }

    execute_task(
        (
            OWSaveNexusIntegrated.ewokstaskclass
            if qtapp is None
            else OWSaveNexusIntegrated
        ),
        inputs=inputs,
    )

    with h5py.File(inputs["url"]) as root:
        expected = {"instrument", "measurement", "integrate", "dummy"}
        nxprocess = root["results/integrate"]
        assert set(root["results"].keys()) == expected
        assert "azimuthal" not in nxprocess
        assert "intensity_errors" not in nxprocess
        numpy.testing.assert_array_equal(nxprocess["integrated/2th"], inputs["radial"])
        numpy.testing.assert_array_equal(
            nxprocess["integrated/intensity"], inputs["intensity"]
        )
        numpy.testing.assert_array_equal(
            root["results/measurement/integrated"], inputs["intensity"]
        )
        config = json.loads(nxprocess["configuration/data"][()])
        numpy.testing.assert_array_equal(config["energy"], inputs["info"]["energy"])
        assert h5py_read_dataset(root["results/dummy/test"]) == "test"


def assert_save_nexus_with_azimuth(common_inputs, qtapp):
    inputs = {
        "radial": numpy.linspace(1, 60, 60),
        "azimuthal": numpy.linspace(1, 100, 100),
        "intensity": numpy.random.random((10, 100, 60)),
        **common_inputs,
    }

    execute_task(
        (
            OWSaveNexusIntegrated.ewokstaskclass
            if qtapp is None
            else OWSaveNexusIntegrated
        ),
        inputs=inputs,
    )

    with h5py.File(inputs["url"]) as root:
        expected = {"instrument", "measurement", "integrate", "dummy"}
        nxprocess = root["results/integrate"]
        assert set(root["results"].keys()) == expected
        assert "intensity_errors" not in nxprocess
        numpy.testing.assert_array_equal(nxprocess["integrated/2th"], inputs["radial"])
        numpy.testing.assert_array_equal(
            nxprocess["integrated/chi"], inputs["azimuthal"]
        )
        numpy.testing.assert_array_equal(
            nxprocess["integrated/intensity"], inputs["intensity"]
        )
        numpy.testing.assert_array_equal(
            root["results/measurement/integrated"], inputs["intensity"]
        )
        config = json.loads(nxprocess["configuration/data"][()])
        numpy.testing.assert_array_equal(config["energy"], inputs["info"]["energy"])
        assert h5py_read_dataset(root["results/dummy/test"]) == "test"


def test_save_nexus_without_info(common_inputs, qtapp):
    inputs = {
        "radial": numpy.linspace(1, 60, 60),
        "azimuthal": numpy.linspace(1, 100, 100),
        "intensity": numpy.random.random((10, 100, 60)),
        **common_inputs,
    }
    inputs.pop("info")

    execute_task(
        (
            OWSaveNexusIntegrated.ewokstaskclass
            if qtapp is None
            else OWSaveNexusIntegrated
        ),
        inputs=inputs,
    )

    with h5py.File(inputs["url"]) as root:
        expected = {"instrument", "measurement", "integrate", "dummy"}
        nxprocess = root["results/integrate"]
        assert set(root["results"].keys()) == expected
        assert "intensity_errors" not in nxprocess
        numpy.testing.assert_array_equal(nxprocess["integrated/2th"], inputs["radial"])
        numpy.testing.assert_array_equal(
            nxprocess["integrated/chi"], inputs["azimuthal"]
        )
        numpy.testing.assert_array_equal(
            nxprocess["integrated/intensity"], inputs["intensity"]
        )
        numpy.testing.assert_array_equal(
            root["results/measurement/integrated"], inputs["intensity"]
        )
        assert h5py_read_dataset(root["results/dummy/test"]) == "test"
        config = json.loads(nxprocess["configuration/data"][()])
        assert config == {"ewoks_version": importlib.metadata.version("ewoks")}
        assert h5py_read_dataset(nxprocess["program"]) == "pyFAI"
