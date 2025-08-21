from typing import Optional

import h5py
import numpy
import pytest
from ewoksorange.tests.utils import execute_task

from orangecontrib.ewoksxrpd.batchintegrate import OWIntegrateBlissScan


@pytest.mark.parametrize("ndims", [1, 2], ids=["nD1", "nD2"])
@pytest.mark.parametrize("external", [False, True], ids=["noexternal", "external"])
def test_batch_integrate_task(
    ndims, external, bliss_task_inputs, tmp_path, pyfai_integration_version
):
    assert_batch_integrate(
        ndims, bliss_task_inputs, tmp_path, pyfai_integration_version, external=external
    )


@pytest.mark.parametrize("ndims", [1, 2], ids=["nD1", "nD2"])
@pytest.mark.parametrize("external", [False, True], ids=["noexternal", "external"])
def test_batch_integrate_widget(ndims, external, bliss_task_inputs, tmp_path, qtapp):
    assert_batch_integrate(
        ndims, bliss_task_inputs, tmp_path, None, external=external, qtapp=qtapp
    )


@pytest.mark.parametrize("ndims", [1, 2], ids=["nD1", "nD2"])
@pytest.mark.parametrize("external", [False, True], ids=["noexternal", "external"])
def test_bliss_integrate_with_overwrite(ndims, external, bliss_task_inputs, tmp_path):
    assert_batch_integrate(ndims, bliss_task_inputs, tmp_path, None, external=external)
    bliss_task_inputs["overwrite"] = True
    assert_batch_integrate(ndims, bliss_task_inputs, tmp_path, None, external=external)


def assert_batch_integrate(
    ndims,
    bliss_task_inputs,
    tmp_path,
    version: Optional[dict],
    external: bool = False,
    qtapp=None,
):
    inputs = dict(bliss_task_inputs)
    output_filename = str(tmp_path / "result.h5")
    inputs["output_filename"] = output_filename
    if external:
        external_output_filename = str(tmp_path / "data.h5")
        inputs["external_output_filename"] = external_output_filename
    if ndims == 2:
        inputs["integration_options"] = {
            "method": "no_csr_cython",
            "integrator_name": "integrate2d_ng",
            "nbpt_azim": 100,
            "error_model": "poisson",
        }
    else:
        inputs["integration_options"] = {
            "error_model": "azimuthal",
            "method": "no_csr_cython",
            "integrator_name": "sigma_clip_ng",
            "extra_options": {"max_iter": 3, "thres": 0},
        }
    if version:
        inputs["integration_options"]["version"] = version

    outputs = execute_task(
        OWIntegrateBlissScan.ewokstaskclass if qtapp is None else OWIntegrateBlissScan,
        inputs=inputs,
    )

    if external:
        expected_nxdata_url = (
            f"{external_output_filename}::/2.1/p3_integrate/integrated"
        )
    else:
        expected_nxdata_url = f"{output_filename}::/2.1/p3_integrate/integrated"
    assert outputs["nxdata_url"] == expected_nxdata_url

    integration_options = inputs["integration_options"]
    assert outputs["info"]["error_model"] == integration_options["error_model"]
    assert outputs["info"]["integrator_name"] == integration_options["integrator_name"]
    assert outputs["info"]["method"] == integration_options["method"]

    with h5py.File(output_filename) as root:
        data = root["2.1/measurement/p3_integrated"][()]
        if ndims == 2:
            axes = ["points", "chi", "2th"]
        else:
            axes = ["points", "2th"]
        assert root["2.1/p3_integrate/integrated"].attrs["axes"].tolist() == axes
        spectrum0 = data[0]
        for spectrum in data:
            numpy.testing.assert_allclose(spectrum, spectrum0, atol=1)

        # Check links to raw data
        root["2.1/measurement/monitor"][()]
        list(root["2.1/instrument"].keys())
