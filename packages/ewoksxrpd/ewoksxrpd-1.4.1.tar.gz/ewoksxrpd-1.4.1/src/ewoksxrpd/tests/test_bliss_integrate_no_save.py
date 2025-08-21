import numpy
import pytest
from ewoksorange.tests.utils import execute_task

from orangecontrib.ewoksxrpd.blissintegratenosave import OWIntegrateBlissScanNoSave


@pytest.mark.parametrize("ndims", [1, 2])
def test_bliss_integrate_no_save_task(ndims, bliss_task_inputs):
    assert_bliss_integrate_no_save(ndims, bliss_task_inputs)


@pytest.mark.parametrize("ndims", [1, 2])
def test_batch_integrate_no_save_widget(ndims, bliss_task_inputs, qtapp):
    assert_bliss_integrate_no_save(ndims, bliss_task_inputs, qtapp=qtapp)


def assert_bliss_integrate_no_save(ndims, bliss_task_inputs, qtapp=None):
    nb_radial = 550
    nb_azim = 150

    if ndims == 2:
        integration_options = {
            "integrator_name": "integrate2d_ng",
            "nbpt_azim": nb_azim,
            "error_model": "poisson",
        }
    else:
        integration_options = {
            "error_model": "azimuthal",
            "integrator_name": "sigma_clip_ng",
            "extra_options": {"max_iter": 3, "thres": 0},
        }

    inputs = {
        **bliss_task_inputs,
        "integration_options": {
            "nbpt_rad": nb_radial,
            "method": "no_csr_cython",
            **integration_options,
        },
    }
    output_values = execute_task(
        (
            OWIntegrateBlissScanNoSave.ewokstaskclass
            if qtapp is None
            else OWIntegrateBlissScanNoSave
        ),
        inputs=inputs,
    )

    assert output_values["radial_units"] == "2th_deg"
    assert output_values["radial"].shape == (nb_radial,)

    data = output_values["intensity"]
    spectrum0 = data[0]
    for spectrum in data:
        numpy.testing.assert_allclose(spectrum, spectrum0, atol=1)

    if ndims == 2:
        assert output_values["azimuthal"].shape == (nb_azim,)
    else:
        assert output_values["azimuthal"] is None
