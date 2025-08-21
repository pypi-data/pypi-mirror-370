from os import PathLike
from typing import List

import numpy
import pytest

from ewoksorange.tests.utils import execute_task

from .xrpd_theory import Setup
from .xrpd_theory import Calibration
from ..tasks import calibrate
from ..pyfai_api import AzimuthalIntegrator

from orangecontrib.ewoksxrpd.calibratesingle import OWCalibrateSingle
from orangecontrib.ewoksxrpd.calibratemulti import OWCalibrateMulti
from orangecontrib.ewoksxrpd.calculategeometry import OWCalculateGeometry
from orangecontrib.ewoksxrpd.diagnose_singlecalib import (
    OWDiagnoseCalibrateSingleResults,
)
from orangecontrib.ewoksxrpd.diagnose_multicalib import (
    OWDiagnoseCalibrateMultiResults,
)


@pytest.mark.parametrize(
    "fixed",
    [[], ["energy"], ["rot2", "dist"]],
    ids=["fixed=none", "fixed=energy", "fixed=rot2,dist"],
)
def test_calibrate_single_distance_task(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    aiSetup1: AzimuthalIntegrator,
    tmpdir: PathLike,
):
    assert_calibrate_single_distance(
        fixed, imageSetup1Calibrant1, setup1, aiSetup1, tmpdir, None
    )


@pytest.mark.parametrize(
    "fixed",
    [[], ["energy"], ["rot2", "dist"]],
    ids=["fixed=none", "fixed=energy", "fixed=rot2,dist"],
)
def test_calibrate_single_distance_widget(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    aiSetup1: AzimuthalIntegrator,
    tmpdir: PathLike,
    qtapp,
):
    assert_calibrate_single_distance(
        fixed, imageSetup1Calibrant1, setup1, aiSetup1, tmpdir, qtapp
    )


@pytest.mark.parametrize(
    "fixed",
    [[], ["energy"], ["rot2", "dist"]],
    ids=["fixed=none", "fixed=energy", "fixed=rot2,dist"],
)
def test_calibrate_multi_distance_task(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    imageSetup2Calibrant1: Calibration,
    setup2: Setup,
    aiSetup1: AzimuthalIntegrator,
    aiSetup2: AzimuthalIntegrator,
    tmpdir: PathLike,
):
    assert_calibrate_multi_distance(
        fixed,
        imageSetup1Calibrant1,
        setup1,
        imageSetup2Calibrant1,
        setup2,
        aiSetup1,
        aiSetup2,
        tmpdir,
        None,
    )


@pytest.mark.parametrize(
    "fixed",
    [[], ["energy"], ["rot2", "dist"]],
    ids=["fixed=none", "fixed=energy", "fixed=rot2,dist"],
)
def test_calibrate_multi_distance_widget(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    imageSetup2Calibrant1: Calibration,
    setup2: Setup,
    aiSetup1: AzimuthalIntegrator,
    aiSetup2: AzimuthalIntegrator,
    tmpdir: PathLike,
    qtapp,
):
    assert_calibrate_multi_distance(
        fixed,
        imageSetup1Calibrant1,
        setup1,
        imageSetup2Calibrant1,
        setup2,
        aiSetup1,
        aiSetup2,
        tmpdir,
        qtapp,
    )


def test_calibrate_single_multiple_max_rings(
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    aiSetup1: AzimuthalIntegrator,
    tmpdir: PathLike,
):
    fixed = ["energy"]
    geometry0, energy0 = guess_fit_parameters(
        setup1.geometry, setup1.energy, aiSetup1, fixed=fixed
    )
    inputs = {
        "image": imageSetup1Calibrant1.image,
        "geometry": geometry0,
        "detector": setup1.detector,
        "energy": energy0,
        "calibrant": imageSetup1Calibrant1.calibrant,
        "fixed": fixed,
        "max_rings": [2, 4, 6],
    }

    outputs_values = execute_task(
        OWCalibrateSingle.ewokstaskclass,
        inputs=inputs,
        timeout=3,
    )
    assert_calibration(
        False,
        fixed,
        outputs_values["geometry"],
        outputs_values["energy"],
        outputs_values["rings"],
        setup1,
        imageSetup1Calibrant1,
        aiSetup1,
        tmpdir,
    )


def assert_calibrate_single_distance(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    aiSetup1: AzimuthalIntegrator,
    tmpdir: PathLike,
    qtapp: None,
):
    geometry0, energy0 = guess_fit_parameters(
        setup1.geometry, setup1.energy, aiSetup1, fixed=fixed
    )
    inputs = {
        "image": imageSetup1Calibrant1.image,
        "geometry": geometry0,
        "detector": setup1.detector,
        "energy": energy0,
        "calibrant": imageSetup1Calibrant1.calibrant,
        "fixed": fixed,
    }

    outputs_values = execute_task(
        OWCalibrateSingle.ewokstaskclass if qtapp is None else OWCalibrateSingle,
        inputs=inputs,
        timeout=10,
    )
    assert_calibration(
        False,
        fixed,
        outputs_values["geometry"],
        outputs_values["energy"],
        outputs_values["rings"],
        setup1,
        imageSetup1Calibrant1,
        aiSetup1,
        tmpdir,
    )


def assert_calibrate_multi_distance(
    fixed: List[str],
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    imageSetup2Calibrant1: Calibration,
    setup2: Setup,
    aiSetup1: AzimuthalIntegrator,
    aiSetup2: AzimuthalIntegrator,
    tmpdir: PathLike,
    qtapp,
):
    images = [imageSetup1Calibrant1.image, imageSetup2Calibrant1.image]
    positionunits_in_meter = 1e-2  # cm
    positions = [
        setup1.geometry["dist"] / positionunits_in_meter,
        setup2.geometry["dist"] / positionunits_in_meter,
    ]
    geometry0, energy0 = guess_fit_parameters(
        setup1.geometry, setup1.energy, aiSetup1, fixed=fixed
    )
    reference_position = positions[0]

    inputs = {
        "images": images,
        "positions": positions,
        "positionunits_in_meter": positionunits_in_meter,
        "reference_position": reference_position,
        "geometry": geometry0,
        "detector": setup1.detector,
        "energy": energy0,
        "calibrant": imageSetup1Calibrant1.calibrant,
        "fixed": fixed,
    }

    calibresults = execute_task(
        OWCalibrateMulti.ewokstaskclass if qtapp is None else OWCalibrateMulti,
        inputs=inputs,
    )

    assert_calibration(
        True,
        fixed,
        calibresults["geometry"],
        calibresults["energy"],
        calibresults["rings"]["0"],
        setup1,
        imageSetup1Calibrant1,
        aiSetup1,
        tmpdir,
    )

    geometry = dict(calibresults["geometry"])
    shift_in_meter = setup2.geometry["dist"] - setup1.geometry["dist"]
    geometry["dist"] += shift_in_meter
    assert_calibration(
        True,
        fixed,
        geometry,
        calibresults["energy"],
        calibresults["rings"]["1"],
        setup2,
        imageSetup2Calibrant1,
        aiSetup2,
        tmpdir,
    )

    inputs = {
        "parametrization": calibresults["parametrization"],
        "parameters": calibresults["parameters"],
        "position": positions[0],
    }

    calcresults = execute_task(
        OWCalculateGeometry.ewokstaskclass if qtapp is None else OWCalculateGeometry,
        inputs=inputs,
    )

    assert_geometry(
        True,
        fixed,
        calcresults["geometry"],
        calcresults["energy"],
        setup1,
        aiSetup1,
    )

    inputs["position"] = positions[1]
    calcresults = execute_task(
        OWCalculateGeometry.ewokstaskclass if qtapp is None else OWCalculateGeometry,
        inputs=inputs,
    )

    assert_geometry(
        True,
        fixed,
        calcresults["geometry"],
        calcresults["energy"],
        setup2,
        aiSetup2,
    )

    # Set show=True to visualize the calibration results
    filename = tmpdir / "test.png"
    inputs = {
        "images": images,
        "positions": positions,
        "detector": setup1.detector,
        "calibrant": imageSetup1Calibrant1.calibrant,
        "rings": calibresults["rings"],
        "parametrization": calibresults["parametrization"],
        "parameters": calibresults["parameters"],
        "show": False,
        "filename": str(filename),
    }
    execute_task(
        (
            OWDiagnoseCalibrateMultiResults.ewokstaskclass
            if qtapp is None
            else OWDiagnoseCalibrateMultiResults
        ),
        inputs=inputs,
    )
    assert filename.exists()


def assert_calibration(
    multi_distance: bool,
    fixed: List[str],
    geometry: dict,
    energy: float,
    rings: dict,
    setup: Setup,
    calibration: Calibration,
    ai: AzimuthalIntegrator,
    tmpdir: PathLike,
    qtapp=None,
):
    assert_geometry(multi_distance, fixed, geometry, energy, setup, ai)

    filename = tmpdir / "diagnose.png"
    inputs = {
        "image": calibration.image,
        "geometry": geometry,
        "detector": setup.detector,
        "energy": energy,
        "calibrant": calibration.calibrant,
        "rings": rings,
        "show": False,
        "filename": str(filename),
    }

    execute_task(
        (
            OWDiagnoseCalibrateSingleResults.ewokstaskclass
            if qtapp is None
            else OWDiagnoseCalibrateSingleResults
        ),
        inputs=inputs,
        timeout=10,
    )
    assert filename.exists()


def guess_fit_parameters(
    geometry: dict,
    energy: float,
    ai: AzimuthalIntegrator,
    fixed: List[str],
) -> dict:
    """Start fitting with parameters that are reasonably close to the real values"""

    def modify(pname, real_value):
        if pname in fixed:
            return real_value
        elif pname.startswith("rot"):
            # wrong by 1 degree
            return real_value + numpy.radians(0.1)
        elif pname == "dist":
            # wrong by 1 mm
            return real_value + 1e-3
        elif pname == "poni1":
            # wrong by 5 pixels
            return real_value + 5 * ai.detector.pixel1
        elif pname == "poni2":
            # wrong by 5 pixels
            return real_value - 5 * ai.detector.pixel2
        elif pname == "energy":
            # wrong by 50 eV
            return real_value + 50e-3
        else:
            raise ValueError(pname)

    geometry = {
        pname: modify(pname, real_value) for pname, real_value in geometry.items()
    }
    return geometry, modify("energy", energy)


def assert_geometry(
    multi_distance: bool,
    fixed: List[str],
    geometry: dict,
    energy: float,
    setup: Setup,
    ai: AzimuthalIntegrator,
):
    """Energy and distance cannot be distinguished by a single distance calibration"""
    expected_parameters = dict(setup.geometry)
    expected_parameters["energy"] = setup.energy
    parameters = dict(geometry)
    parameters["energy"] = energy
    assert parameters.keys() == expected_parameters.keys()
    for pname, expected in expected_parameters.items():
        if pname in fixed:
            margin = 0
        elif pname.startswith("rot"):
            # wrong by +/- 0.2 degree
            margin = numpy.radians(0.2)
        elif pname == "dist":
            if not multi_distance:
                continue
            # wrong by +/- 50 um
            margin = 50e-6
        elif pname == "energy":
            if not multi_distance:
                continue
            # wrong by +/- 5 eV
            margin = 5e-3
        elif pname == "poni1":
            # wrong by +/- 0.5 pixels
            margin = 0.5 * ai.detector.pixel1
        elif pname == "poni2":
            # wrong by +/- 0.5 pixels
            margin = 0.5 * ai.detector.pixel2
        else:
            raise ValueError(pname)
        refined_value = parameters[pname]
        err_msg = f"{pname}: {refined_value} too far from {expected}"
        assert pytest.approx(expected, abs=margin) == refined_value, err_msg


def test_fixed_parameters_sets():
    all_parameters = {
        "dist_offset",
        "dist_scale",
        "poni1_offset",
        "poni2_offset",
        "arot1",
        "arot2",
        "arot3",
        "poni1_scale",
        "poni2_scale",
        "energy",
    }

    # Release incrementally until we have nothing fixed at the end
    always_fixed_params = set()
    incremental_release_groups = [
        {"dist_offset", "dist_scale"},
        {"poni1_offset", "poni2_offset"},
        {"arot1", "arot2", "arot3"},
        {"poni1_scale", "poni2_scale"},
        {"energy"},
    ]
    fixed_parameter_sets = calibrate._fixed_parameters_sets(
        all_parameters, always_fixed_params, incremental_release_groups
    )
    expected = [
        {
            "poni1_offset",
            "poni2_offset",
            "arot1",
            "arot2",
            "arot3",
            "poni1_scale",
            "poni2_scale",
            "energy",
        },
        {"arot1", "arot2", "arot3", "poni1_scale", "poni2_scale", "energy"},
        {"poni1_scale", "poni2_scale", "energy"},
        {"energy"},
        None,
    ]
    assert fixed_parameter_sets == expected

    # Skip redundant release steps
    always_fixed_params = set()
    incremental_release_groups = [
        set(),
        {"dist_offset", "dist_scale"},
        {"poni1_offset", "poni2_offset"},
        {"arot1", "arot2", "arot3"},
        set(),
        {"arot1", "arot2", "arot3", "poni2_offset"},
        {"poni1_scale", "poni2_scale"},
        {"energy"},
        {"energy"},
        set(),
    ]
    fixed_parameter_sets = calibrate._fixed_parameters_sets(
        all_parameters, always_fixed_params, incremental_release_groups
    )
    expected = [
        {
            "poni1_offset",
            "poni2_offset",
            "arot1",
            "arot2",
            "arot3",
            "poni1_scale",
            "poni2_scale",
            "energy",
        },
        {"arot1", "arot2", "arot3", "poni1_scale", "poni2_scale", "energy"},
        {"poni1_scale", "poni2_scale", "energy"},
        {"energy"},
        None,
    ]
    assert fixed_parameter_sets == expected

    # Release incrementally but keep arot3 and energy fixed
    always_fixed_params = {"arot3", "energy"}
    incremental_release_groups = [
        {"dist_offset", "dist_scale"},
        {"poni1_offset", "poni2_offset"},
        {"arot1", "arot2", "arot3"},
        {"poni1_scale", "poni2_scale"},
        {"energy"},
    ]
    fixed_parameter_sets = calibrate._fixed_parameters_sets(
        all_parameters, always_fixed_params, incremental_release_groups
    )
    expected = [
        {
            "poni1_offset",
            "poni2_offset",
            "arot1",
            "arot2",
            "arot3",
            "poni1_scale",
            "poni2_scale",
            "energy",
        },
        {"arot1", "arot2", "arot3", "poni1_scale", "poni2_scale", "energy"},
        {"arot3", "poni1_scale", "poni2_scale", "energy"},
        {"arot3", "energy"},
    ]
    assert fixed_parameter_sets == expected

    # Release all parameters at once
    always_fixed_params = set()
    incremental_release_groups = [all_parameters]
    fixed_parameter_sets = calibrate._fixed_parameters_sets(
        all_parameters, always_fixed_params, incremental_release_groups
    )
    expected = [None]
    assert fixed_parameter_sets == expected

    # Release all parameters at once but keep energy fixed
    always_fixed_params = {"energy"}
    incremental_release_groups = [all_parameters]
    fixed_parameter_sets = calibrate._fixed_parameters_sets(
        all_parameters, always_fixed_params, incremental_release_groups
    )
    expected = [{"energy"}]
    assert fixed_parameter_sets == expected
