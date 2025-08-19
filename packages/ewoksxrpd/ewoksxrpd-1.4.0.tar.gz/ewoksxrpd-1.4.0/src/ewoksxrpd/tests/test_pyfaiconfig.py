import json

import pytest
from ewoks import execute_graph
from ewoksorange.tests.utils import execute_task
from pyFAI.io.ponifile import PoniFile

from orangecontrib.ewoksxrpd.savepyfaiconfig import OWSavePyFaiConfig
from orangecontrib.ewoksxrpd.savepyfaiponifile import OWSavePyFaiPoniFile

from ..tasks.pyfaiconfig import PyFaiConfig, SavePyFaiConfig, SavePyFaiPoniFile


def test_pyfai_config_roundtrip(tmp_path, setup1):
    """Create and save pyFAI configuration"""
    workflow = {
        "graph": {"id": "test_roundtrip"},
        "nodes": [
            {
                "id": "load",
                "task_type": "class",
                "task_identifier": "ewoksxrpd.tasks.pyfaiconfig.PyFaiConfig",
            },
            {
                "id": "save",
                "task_type": "class",
                "task_identifier": "ewoksxrpd.tasks.pyfaiconfig.SavePyFaiConfig",
            },
        ],
        "links": [
            {
                "source": "load",
                "target": "save",
                "data_mapping": [
                    {"source_output": "energy", "target_input": "energy"},
                    {"source_output": "geometry", "target_input": "geometry"},
                    {"source_output": "detector", "target_input": "detector"},
                    {
                        "source_output": "detector_config",
                        "target_input": "detector_config",
                    },
                    {"source_output": "mask", "target_input": "mask"},
                    {
                        "source_output": "integration_options",
                        "target_input": "integration_options",
                    },
                ],
            },
        ],
    }

    output_path = tmp_path / "pyfaiconfig.json"
    mask_filename = str(tmp_path / "mask.edf")
    integration_options = {"error_model": "poisson", **setup1.integration_options}
    result = execute_graph(
        workflow,
        inputs=[
            {"id": "load", "name": "energy", "value": setup1.energy},
            {"id": "load", "name": "geometry", "value": setup1.geometry},
            {"id": "load", "name": "mask", "value": mask_filename},
            {"id": "load", "name": "detector", "value": setup1.detector},
            {"id": "load", "name": "detector_config", "value": setup1.detector_config},
            {"id": "load", "name": "integration_options", "value": integration_options},
            {"id": "save", "name": "output_filename", "value": str(output_path)},
        ],
        outputs=[{"all": False}],
    )
    assert result["filename"] == str(output_path)

    version = setup1.version or 3
    poni = {
        "wavelength": setup1.wavelength,
        "detector": setup1.detector,
        "detector_config": setup1.load_detector_config(),
        **setup1.geometry,
    }
    expected_config = {
        "application": "pyfai-integrate",
        "version": version,
        "do_mask": True,
        "mask_file": mask_filename,
        **integration_options,
    }
    if version >= 4:
        expected_config["poni"] = poni
    else:
        expected_config.update(poni)

    config = json.loads(output_path.read_text())
    assert config == expected_config


def test_SavePyFaiConfig(tmp_path, setup1, qtapp):
    output_path = tmp_path / "pyfaiconfig.json"
    integration_options = {"error_model": "poisson", **setup1.integration_options}
    mask_filename = str(tmp_path / "mask.edf")
    inputs = {
        "output_filename": str(output_path),
        "energy": setup1.energy,
        "geometry": setup1.geometry,
        "detector": setup1.detector,
        "mask": mask_filename,
        "detector_config": setup1.detector_config,
        "integration_options": integration_options,
    }

    result = execute_task(
        SavePyFaiConfig if qtapp is None else OWSavePyFaiConfig,
        inputs=inputs,
    )

    assert result["filename"] == str(output_path)

    version = setup1.version or 3
    poni = {
        "wavelength": setup1.wavelength,
        "detector": setup1.detector,
        "detector_config": setup1.load_detector_config(),
        **setup1.geometry,
    }
    expected_config = {
        "application": "pyfai-integrate",
        "version": version,
        "do_mask": True,
        "mask_file": mask_filename,
        **integration_options,
    }
    if version >= 4:
        expected_config["poni"] = poni
    else:
        expected_config.update(poni)

    config = json.loads(output_path.read_text())
    assert config == expected_config


def test_SavePyFaiConfig_v4(tmp_path, setup1, qtapp):
    output_path = tmp_path / "pyfaiconfig.json"

    bad_poni_info = {
        **setup1.geometry,
        "wavelength": 0.0,
        "detector": "BAD_DETECTOR",
        "detector_config": {"orientation": 1},
    }
    integration_options = {
        "application": "pyfai-integrate",
        "version": 4,
        "error_model": "poisson",
        "poni": bad_poni_info,
    }

    mask_filename = str(tmp_path / "mask.edf")
    inputs = {
        "output_filename": str(output_path),
        "energy": setup1.energy,
        "geometry": setup1.geometry,
        "detector": setup1.detector,
        "mask": mask_filename,
        "detector_config": setup1.detector_config,
        "integration_options": integration_options,
    }

    result = execute_task(
        SavePyFaiConfig if qtapp is None else OWSavePyFaiConfig,
        inputs=inputs,
    )

    assert result["filename"] == str(output_path)
    expected_config = {
        "application": "pyfai-integrate",
        "version": 4,
        "poni": {
            **setup1.geometry,
            "wavelength": setup1.wavelength,
            "detector": setup1.detector,
            "detector_config": setup1.load_detector_config(),
        },
        "do_mask": True,
        "mask_file": mask_filename,
        "error_model": "poisson",
    }
    config = json.loads(output_path.read_text())
    assert config == expected_config


def test_SavePyFaiPoniFile(tmp_path, setup1, qtapp):
    output_path = tmp_path / "pyfaiconfig.json"

    inputs = {
        "output_filename": str(output_path),
        "energy": setup1.energy,
        "geometry": setup1.geometry,
        "detector": setup1.detector,
        "detector_config": setup1.detector_config,
        "integration_options": setup1.integration_options,
    }

    result = execute_task(
        SavePyFaiPoniFile if qtapp is None else OWSavePyFaiPoniFile,
        inputs=inputs,
    )

    assert result["filename"] == str(output_path)

    result_poni = PoniFile(result["filename"])
    expected_poni = PoniFile(
        {
            "wavelength": setup1.wavelength,
            **setup1.geometry,
            "detector": setup1.detector,
            "detector_config": setup1.detector_config,
        }
    )
    assert result_poni.as_dict() == expected_poni.as_dict()


@pytest.mark.parametrize("show_warnings", (True, False))
def test_merging_of_config(tmp_path, caplog, show_warnings):
    energy = 12.5
    filename = tmp_path / "pyfaiconfig.json"
    filename2 = tmp_path / "pyfaiconfig2.json"

    with open(filename, "w") as f:
        json.dump(
            {
                "npt_rad": 100,
                "energy": energy,
            },
            f,
        )

    with open(filename2, "w") as f:
        json.dump(
            {"npt_rad": 400},
            f,
        )

    inputs = {
        "filename": str(filename),
        "filenames": [str(filename2)],
        "integration_options": {"error_model": "poisson"},
        "show_merge_warnings": show_warnings,
    }

    outputs = execute_task(PyFaiConfig, inputs=inputs)

    if show_warnings:
        assert (
            f"New value of 'npt_rad' (400) from {str(filename2)} will overwrite the current value (100)"
            in caplog.text
        )
    else:
        assert caplog.text == ""

    assert outputs["energy"] == energy
    assert outputs["integration_options"] == {"npt_rad": 400, "error_model": "poisson"}
