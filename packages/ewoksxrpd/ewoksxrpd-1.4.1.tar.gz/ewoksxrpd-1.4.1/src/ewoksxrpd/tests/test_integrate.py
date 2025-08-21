from os import PathLike

import pytest
import numpy
from ewoksorange.tests.utils import execute_task

from ..tasks.integrate import IntegrateSinglePattern
from orangecontrib.ewoksxrpd.integrate_singlepattern import OWIntegrateSinglePattern
from orangecontrib.ewoksxrpd.diagnose_integrate1d import OWDiagnoseIntegrate1D

from .xrpd_theory import Measurement
from .xrpd_theory import Setup
from .xrpd_theory import RadialPattern
from .xrpd_theory import AzimuthalPattern
from .xrpd_theory import IntensityPattern


@pytest.mark.parametrize("monitor_as_list", [False, True], ids=["scalar", "list"])
def test_integrate1d_task(
    tmpdir: PathLike,
    imageSetup1SampleA: Measurement,
    setup1: Setup,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
    monitor_as_list: bool,
):
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        {"method": "cython"},
        monitor_as_list=monitor_as_list,
    )


def test_integrate1d_widget(
    tmpdir: PathLike,
    imageSetup1SampleA: Measurement,
    setup1: Setup,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
    qtapp,
):
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        qtapp,
        {"method": "cython"},
    )


# from pyFAI.method_registry import IntegrationMethod
# for method in IntegrationMethod._registry:
#    print(f"{method.split}_{method.algo}_{method.impl}")
#
# {split}_{algo}_{impl}{target}
# split: "no", "bbox", "pseudo", "full"
# algo: "histogram", "lut", "csr"
# impl: "python", "cython", "opencl"


def test_sigma_clip_task(
    tmpdir: PathLike,
    imageSetup1SampleA: Measurement,
    setup1: Setup,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
):
    integration_options = {
        "error_model": "azimuthal",
        "method": "no_csr_cython",
        "integrator_name": "sigma_clip_ng",
        "extra_options": {"max_iter": 3, "thres": 0},
    }
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        integration_options,
    )


def test_sigma_clip_widget(
    tmpdir: PathLike,
    imageSetup1SampleA: Measurement,
    setup1: Setup,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
    qtapp,
):
    integration_options = {
        "error_model": "azimuthal",
        "method": "no_csr_cython",
        "integrator_name": "sigma_clip_ng",
        "extra_options": {"max_iter": 3, "thres": 0},
    }
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        qtapp,
        integration_options,
    )


def test_integrate1d_reconfig(
    tmpdir: PathLike,
    imageSetup1SampleA: Measurement,
    setup1: Setup,
    imageSetup2SampleA: Measurement,
    setup2: Setup,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
):
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        {"method": "cython"},
    )
    assert_integrate1d(
        imageSetup2SampleA,
        setup2,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        {"method": "cython"},
    )
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        {"method": "cython"},
    )
    assert_integrate1d(
        imageSetup1SampleA,
        setup1,
        xSampleA,
        ySampleA,
        tmpdir,
        None,
        {"method": "cython"},
    )


def test_integrate2d(
    imageSetup1SampleC: Measurement,
    setup1: Setup,
    radialSampleC: RadialPattern,
    azimuthalSampleC: AzimuthalPattern,
    intensitySampleC: IntensityPattern,
):
    integration_options = {
        **setup1.integration_options,
        **radialSampleC.integration_options,
        **azimuthalSampleC.integration_options,
    }
    inputs = {
        "image": imageSetup1SampleC.image,
        "detector": setup1.detector,
        "geometry": setup1.geometry,
        "energy": setup1.energy,
        "integration_options": integration_options,
    }
    inputs["monitor"] = imageSetup1SampleC.monitor
    inputs["reference"] = intensitySampleC.monitor

    output_values = execute_task(IntegrateSinglePattern, inputs=inputs)

    assert output_values["radial_units"] == radialSampleC.units
    numpy.testing.assert_allclose(radialSampleC.x, output_values["radial"], rtol=1e-6)

    assert output_values["radial_units"] == radialSampleC.units
    numpy.testing.assert_allclose(
        azimuthalSampleC.x, output_values["azimuthal"], rtol=1e-1
    )
    assert output_values["azimuthal_units"] == azimuthalSampleC.units

    assert output_values["intensity"].shape == (
        azimuthalSampleC.x.size,
        radialSampleC.x.size,
    )


def assert_integrate1d(
    measurement: Measurement,
    setup: Setup,
    xpattern: RadialPattern,
    ypattern: IntensityPattern,
    tmpdir: PathLike,
    qtapp,
    integration_options: dict,
    monitor_as_list: bool = False,
):
    integration_options = {
        **setup.integration_options,
        **xpattern.integration_options,
        **integration_options,
    }
    inputs = {
        "image": measurement.image,
        "detector": setup.detector,
        "geometry": setup.geometry,
        "energy": setup.energy,
        "integration_options": integration_options,
    }
    if monitor_as_list:
        inputs["monitors"] = [measurement.monitor, 1, None, 1]
        inputs["references"] = [ypattern.monitor, 1, 1, None]
    else:
        inputs["monitor"] = measurement.monitor
        inputs["reference"] = ypattern.monitor

    output_values = execute_task(
        (
            OWIntegrateSinglePattern.ewokstaskclass
            if qtapp is None
            else OWIntegrateSinglePattern
        ),
        inputs=inputs,
    )

    assert output_values["radial_units"] == xpattern.units
    numpy.testing.assert_allclose(xpattern.x, output_values["radial"], rtol=1e-6)
    atol = ypattern.y.max() * 0.01
    numpy.testing.assert_allclose(ypattern.y, output_values["intensity"], atol=atol)

    # Set show=True to visualize the calibration results
    filename = tmpdir / "diagnose.png"
    inputs = {
        "x": output_values["radial"],
        "y": output_values["intensity"],
        "xunits": output_values["radial_units"],
        "show": False,
        "filename": str(filename),
        # "energy": setup.energy,
        # "calibrant": "LaB6"
    }
    execute_task(
        (
            OWDiagnoseIntegrate1D.ewokstaskclass
            if qtapp is None
            else OWDiagnoseIntegrate1D
        ),
        inputs=inputs,
    )
    assert filename.exists()
