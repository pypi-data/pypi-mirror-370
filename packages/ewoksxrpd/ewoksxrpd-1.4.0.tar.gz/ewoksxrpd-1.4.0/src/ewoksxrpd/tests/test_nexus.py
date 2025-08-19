import json

import numpy
import h5py
from silx.io.dictdump import nxtodict
from silx.io.utils import h5py_read_dataset
from ewoksorange.tests.utils import execute_task

from orangecontrib.ewoksxrpd.nexus import OWSaveNexusPattern1D


def test_save_nexus_task(tmpdir, setup1, bliss_lab6_scan):
    assert_save_nexus(tmpdir, setup1, None, bliss_lab6_scan)


def test_save_nexus_widget(tmpdir, setup1, qtapp, bliss_lab6_scan):
    assert_save_nexus(tmpdir, setup1, qtapp, bliss_lab6_scan)


def assert_save_nexus(tmpdir, setup1, qtapp, bliss_lab6_scan):
    bliss_scan_url = f"{bliss_lab6_scan}::/2.1"
    inputs = {
        "url": str(tmpdir / "result.h5"),
        "x": numpy.linspace(1, 60, 60),
        "y": numpy.random.random(60),
        "xunits": "2th_deg",
        "header": {
            "energy": 10.2,
            "detector": setup1.detector,
            "geometry": setup1.geometry,
        },
        "metadata": {"dummy": {"test": "test"}},
        "bliss_scan_url": bliss_scan_url,
        "retry_timeout": 5,
    }

    execute_task(
        OWSaveNexusPattern1D.ewokstaskclass if qtapp is None else OWSaveNexusPattern1D,
        inputs=inputs,
    )

    with h5py.File(str(tmpdir / "result.h5")) as root:
        expected = {"instrument", "measurement", "integrate", "dummy"}
        nxprocess = root["results/integrate"]
        assert set(root["results"].keys()) == expected
        numpy.testing.assert_array_equal(nxprocess["integrated/2th"], inputs["x"])
        numpy.testing.assert_array_equal(nxprocess["integrated/intensity"], inputs["y"])
        numpy.testing.assert_array_equal(
            root["results/measurement/integrated"], inputs["y"]
        )

        configuration = nxprocess["configuration"]
        expected_keys = {"ewoks_version", "energy", "detector", "geometry"}
        if configuration.attrs["NX_class"] == "NXnote":
            config = json.loads(configuration["data"][()])
        else:
            config = nxtodict(configuration)
            expected_keys.update({"@NX_class", "energy@units"})
        assert set(config) == expected_keys
        numpy.testing.assert_array_equal(config["energy"], inputs["header"]["energy"])
        assert h5py_read_dataset(root["results/dummy/test"]) == "test"
