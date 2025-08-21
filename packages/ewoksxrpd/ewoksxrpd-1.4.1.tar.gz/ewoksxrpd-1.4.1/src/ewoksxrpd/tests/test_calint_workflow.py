import os
import numpy
from ewoks import execute_graph
from silx.io.dictdump import dicttonx, nxtodict

from ..pyfai_api import AzimuthalIntegrator

from .xrpd_theory import Setup
from .xrpd_theory import Calibration
from .xrpd_theory import Measurement
from .xrpd_theory import RadialPattern
from .xrpd_theory import IntensityPattern
from .test_calibrate import guess_fit_parameters


def calibintworkflow():
    nodes = [
        {
            "id": "calib_multidistance",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.calibrate.CalibrateMulti",
        },
        {
            "id": "calib_guess",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.calibrate.CalculateGeometry",
        },
        {
            "id": "calib_singledistance",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.calibrate.CalibrateSingle",
        },
        {
            "id": "detect_mask",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.mask.MaskDetection",
        },
        {
            "id": "subtract_background",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.background.SubtractBackground",
        },
        {
            "id": "integrate1d",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.integrate.IntegrateSinglePattern",
        },
        {
            "id": "calib_integrate1d",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.integrate.IntegrateSinglePattern",
        },
        {
            "id": "diagnose_multicalib",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.diagnostics.DiagnoseCalibrateMultiResults",
        },
        {
            "id": "diagnose_singlecalib",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.diagnostics.DiagnoseCalibrateSingleResults",
        },
        {
            "id": "integrate1d_plot",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.diagnostics.DiagnoseIntegrate1D",
        },
        {
            "id": "diagnose_integrate1d",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.diagnostics.DiagnoseIntegrate1D",
        },
        {
            "id": "save_ascii",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.ascii.SaveAsciiPattern1D",
        },
        {
            "id": "save_nexus",
            "task_type": "class",
            "task_identifier": "ewoksxrpd.tasks.nexus.SaveNexusPattern1D",
        },
    ]
    links = [
        {
            "source": "calib_multidistance",
            "target": "calib_guess",
            "data_mapping": [
                {"source_output": "parametrization", "target_input": "parametrization"},
                {"source_output": "parameters", "target_input": "parameters"},
            ],
        },
        {
            "source": "calib_multidistance",
            "target": "diagnose_multicalib",
            "data_mapping": [
                {"source_output": "rings", "target_input": "rings"},
                {"source_output": "parametrization", "target_input": "parametrization"},
                {"source_output": "parameters", "target_input": "parameters"},
                {"source_output": "detector", "target_input": "detector"},
                {"source_output": "detector_config", "target_input": "detector_config"},
            ],
        },
        {
            "source": "calib_guess",
            "target": "calib_singledistance",
            "data_mapping": [
                {"source_output": "geometry", "target_input": "geometry"},
                {"source_output": "energy", "target_input": "energy"},
            ],
        },
        {
            "source": "calib_singledistance",
            "target": "integrate1d",
            "data_mapping": [
                {"source_output": "geometry", "target_input": "geometry"},
                {"source_output": "energy", "target_input": "energy"},
                {"source_output": "detector", "target_input": "detector"},
                {"source_output": "detector_config", "target_input": "detector_config"},
            ],
        },
        {
            "source": "calib_singledistance",
            "target": "calib_integrate1d",
            "data_mapping": [
                {"source_output": "geometry", "target_input": "geometry"},
                {"source_output": "energy", "target_input": "energy"},
                {"source_output": "detector", "target_input": "detector"},
                {"source_output": "detector_config", "target_input": "detector_config"},
            ],
        },
        {
            "source": "calib_singledistance",
            "target": "diagnose_singlecalib",
            "data_mapping": [
                {"source_output": "geometry", "target_input": "geometry"},
                {"source_output": "energy", "target_input": "energy"},
                {"source_output": "detector", "target_input": "detector"},
                {"source_output": "detector_config", "target_input": "detector_config"},
                {"source_output": "rings", "target_input": "rings"},
            ],
        },
        {
            "source": "subtract_background",
            "target": "integrate1d",
            "data_mapping": [
                {"source_output": "image", "target_input": "image"},
                {"source_output": "monitor", "target_input": "monitor"},
            ],
        },
        {
            "source": "detect_mask",
            "target": "integrate1d",
            "data_mapping": [{"source_output": "mask", "target_input": "mask"}],
        },
        {
            "source": "calib_integrate1d",
            "target": "diagnose_integrate1d",
            "data_mapping": [
                {"source_output": "radial", "target_input": "x"},
                {"source_output": "intensity", "target_input": "y"},
                {"source_output": "radial_units", "target_input": "xunits"},
            ],
        },
        {
            "source": "calib_singledistance",
            "target": "diagnose_integrate1d",
            "data_mapping": [
                {"source_output": "energy", "target_input": "energy"},
            ],
        },
        {
            "source": "integrate1d",
            "target": "integrate1d_plot",
            "data_mapping": [
                {"source_output": "radial", "target_input": "x"},
                {"source_output": "intensity", "target_input": "y"},
                {"source_output": "radial_units", "target_input": "xunits"},
            ],
        },
        {
            "source": "integrate1d",
            "target": "save_ascii",
            "data_mapping": [
                {"source_output": "radial", "target_input": "x"},
                {"source_output": "intensity", "target_input": "y"},
                {"source_output": "intensity_error", "target_input": "yerror"},
                {"source_output": "radial_units", "target_input": "xunits"},
                {"source_output": "info", "target_input": "header"},
            ],
        },
        {
            "source": "integrate1d",
            "target": "save_nexus",
            "data_mapping": [
                {"source_output": "radial", "target_input": "x"},
                {"source_output": "intensity", "target_input": "y"},
                {"source_output": "intensity_error", "target_input": "yerror"},
                {"source_output": "radial_units", "target_input": "xunits"},
                {"source_output": "info", "target_input": "header"},
            ],
        },
    ]

    return {"graph": {"id": "calint"}, "nodes": nodes, "links": links}


def test_calint_workflow(
    generate_examples,
    tmpdir,
    imageSetup1Calibrant1: Calibration,
    setup1: Setup,
    imageSetup2Calibrant1: Calibration,
    setup2: Setup,
    aiSetup1: AzimuthalIntegrator,
    image1Setup1SampleB: Measurement,
    image2Setup1SampleB: Measurement,
    imageSetup1SampleA: Measurement,
    xSampleA: RadialPattern,
    ySampleA: IntensityPattern,
):
    if generate_examples:
        from pathlib import Path
        from shutil import rmtree

        import ewoksxrpd

        tmpdir = Path(ewoksxrpd.__path__[0]).parent / "examples"
        rmtree(tmpdir / "data", ignore_errors=True)
        rmtree(tmpdir / "results", ignore_errors=True)
        rmtree(tmpdir / "transient", ignore_errors=True)

    datadir = tmpdir / "data"
    datadir.mkdir()
    resultdir = tmpdir / "results"
    resultdir.mkdir()
    transientdir = tmpdir / "transient"
    transientdir.mkdir()

    calibrant = imageSetup1Calibrant1.calibrant
    detector = setup1.detector
    geometry0, energy0 = guess_fit_parameters(
        setup1.geometry, setup1.energy, aiSetup1, []
    )

    # Calibration data
    mcalib_images, mcalib_positions = _multidistance_calibration_data(
        datadir, imageSetup1Calibrant1, setup1, imageSetup2Calibrant1, setup2
    )
    scalib_image = mcalib_images[0]
    scalib_position = mcalib_positions[0]

    # Mask data
    tnorm = image1Setup1SampleB.monitor
    maskimage1, maskmonitor1, maskimage2, maskmonitor2 = _mask_data(
        datadir, tnorm, image1Setup1SampleB, image2Setup1SampleB, setup1
    )

    # Background+sample data
    backgroundimage, background_monitor, sampleimage, samplemonitor = _holder_data(
        datadir,
        tnorm,
        imageSetup1SampleA,
        image1Setup1SampleB,
        image2Setup1SampleB,
        setup1,
    )

    refmonitor = ySampleA.monitor
    integration_options = xSampleA.integration_options

    inputs = [
        # multi distance calibration
        {"id": "calib_multidistance", "name": "images", "value": mcalib_images},
        {"id": "calib_multidistance", "name": "positions", "value": mcalib_positions},
        {"id": "calib_multidistance", "name": "positionunits_in_meter", "value": 1e-2},
        {"id": "calib_multidistance", "name": "detector", "value": detector},
        {"id": "calib_multidistance", "name": "geometry", "value": geometry0},
        {"id": "calib_multidistance", "name": "energy", "value": energy0},
        {"id": "calib_multidistance", "name": "calibrant", "value": calibrant},
        # single distance calibration plot
        {"id": "diagnose_multicalib", "name": "images", "value": mcalib_images},
        {
            "id": "diagnose_multicalib",
            "name": "positions",
            "value": mcalib_positions,
        },
        {
            "id": "diagnose_multicalib",
            "name": "positionunits_in_meter",
            "value": 1e-2,
        },
        {"id": "diagnose_multicalib", "name": "calibrant", "value": calibrant},
        {
            "id": "diagnose_multicalib",
            "name": "filename",
            "value": str(resultdir / "diagnose_multicalib.png"),
        },
        # calibration guess
        {"id": "calib_guess", "name": "position", "value": scalib_position},
        # single distance calibration
        {"id": "calib_singledistance", "name": "image", "value": scalib_image},
        {"id": "calib_singledistance", "name": "detector", "value": detector},
        {"id": "calib_singledistance", "name": "calibrant", "value": calibrant},
        {"id": "calib_singledistance", "name": "fixed", "value": ["energy"]},
        # single distance calibration plot
        {"id": "diagnose_singlecalib", "name": "image", "value": scalib_image},
        {"id": "diagnose_singlecalib", "name": "calibrant", "value": calibrant},
        {
            "id": "diagnose_singlecalib",
            "name": "filename",
            "value": str(resultdir / "diagnose_singlecalib.png"),
        },
        # detect mask
        {"id": "detect_mask", "name": "image1", "value": maskimage1},
        {"id": "detect_mask", "name": "monitor1", "value": maskmonitor1},
        {"id": "detect_mask", "name": "image2", "value": maskimage2},
        {"id": "detect_mask", "name": "monitor2", "value": maskmonitor2},
        # subtract background
        {"id": "subtract_background", "name": "image", "value": sampleimage},
        {"id": "subtract_background", "name": "monitor", "value": samplemonitor},
        {"id": "subtract_background", "name": "background", "value": backgroundimage},
        {
            "id": "subtract_background",
            "name": "background_monitor",
            "value": background_monitor,
        },
        # integrate
        {
            "id": "integrate1d",
            "name": "integration_options",
            "value": integration_options,
        },
        {"id": "integrate1d", "name": "reference", "value": refmonitor},
        # integrate calibrant
        {"id": "calib_integrate1d", "name": "image", "value": scalib_image},
        # plot integrate calibrant
        {"id": "diagnose_integrate1d", "name": "calibrant", "value": calibrant},
        {
            "id": "diagnose_integrate1d",
            "name": "filename",
            "value": str(resultdir / "diagnose_integrate1d.png"),
        },
        # save result
        {
            "id": "save_ascii",
            "name": "filename",
            "value": str(resultdir / "result_integrate1d.dat"),
        },
        {
            "id": "save_ascii",
            "name": "metadata",
            "value": {
                "name": "S-220323-00006",
                "doi": "4590be84-3493-4bd2-91fe-4cf39cfcf71f",
            },
        },
        {
            "id": "save_nexus",
            "name": "url",
            "value": str(resultdir / "result_integrate1d.h5"),
        },
        {
            "id": "save_nexus",
            "name": "metadata",
            "value": {
                "sample": {
                    "@NX_class": "NXsample",
                    "name": "S-220323-00006",
                    "doi": "4590be84-3493-4bd2-91fe-4cf39cfcf71f",
                }
            },
        },
        {
            "id": "integrate1d_plot",
            "name": "filename",
            "value": str(resultdir / "result_integrate1d.png"),
        },
    ]

    outputs = [
        {"id": "integrate1d", "name": "radial"},
        {"id": "integrate1d", "name": "intensity"},
        {"id": "integrate1d", "name": "radial_units"},
    ]

    workflow = calibintworkflow()

    result = execute_graph(
        workflow,
        inputs=inputs,
        outputs=outputs,
        varinfo={"root_uri": str(transientdir / "result.nx"), "scheme": "nexus"},
    )

    assert result["radial_units"] == xSampleA.units
    numpy.testing.assert_allclose(xSampleA.x, result["radial"], rtol=1e-6)
    atol = ySampleA.y.max() * 0.01
    numpy.testing.assert_allclose(ySampleA.y, result["intensity"], atol=atol)

    radial_values, intensity, yerror = numpy.loadtxt(
        str(resultdir / "result_integrate1d.dat")
    ).T
    numpy.testing.assert_array_equal(radial_values, result["radial"])
    numpy.testing.assert_array_equal(intensity, result["intensity"])
    assert numpy.isnan(yerror).all()

    adict = nxtodict(str(resultdir / "result_integrate1d.h5"))
    diffractogram = adict["results"]["integrate"]["integrated"]
    numpy.testing.assert_array_equal(diffractogram["2th"], result["radial"])
    numpy.testing.assert_array_equal(diffractogram["intensity"], result["intensity"])
    assert numpy.isnan(diffractogram["intensity_errors"]).all()

    assert os.path.isfile(str(resultdir / "diagnose_multicalib.png"))
    assert os.path.isfile(str(resultdir / "diagnose_singlecalib.png"))
    assert os.path.isfile(str(resultdir / "diagnose_integrate1d.png"))
    assert os.path.isfile(str(resultdir / "result_integrate1d.png"))

    if generate_examples:
        from ewokscore import load_graph

        import matplotlib.pyplot as plt

        taskgraph = load_graph(calibintworkflow(), inputs=inputs)
        taskgraph.dump(str(tmpdir / "xrpd_workflow.json"), indent=2)
        plt.show()


def _multidistance_calibration_data(
    datadir, imageSetup1Calibrant1, setup1, imageSetup2Calibrant1, setup2
):
    mcalib_images = list()
    mcalib_positions = list()
    images = [
        (
            imageSetup1Calibrant1.image,
            setup1.geometry["dist"] * 100,
        ),
        (
            imageSetup2Calibrant1.image,
            setup2.geometry["dist"] * 100,
        ),
    ]
    data = {"@NX_class": "NXroot", "@default": "1.1"}
    filename = str(datadir / "calib.h5")
    for i, (image, detz) in enumerate(images, 1):
        data[f"{i}.1"] = {
            "@default": "plotselect",
            "instrument": {
                "@NX_class": "NXinstrument",
                "pilatus1": {
                    "@NX_class": "NXdetector",
                    "data": image,
                },
                "positioners": {"detz": detz, "detz@units": "cm"},
            },
            "title": "sct 1",
            "measurement": {">pilatus1": "../instrument/pilatus1/data"},
            "plotselect": {
                "@NX_class": "NXdata",
                "@signal": "data",
                ">data": "../instrument/pilatus1/data",
            },
        }
        mcalib_images.append(f"silx://{filename}?path=/{i}.1/measurement/pilatus1")
        mcalib_positions.append(
            f"silx://{filename}?path=/{i}.1/instrument/positioners/detz"
        )
    dicttonx(data, filename, update_mode="add")

    return mcalib_images, mcalib_positions


def _mask_data(datadir, tnorm, image1Setup1SampleB, image2Setup1SampleB, setup1):
    detz = setup1.geometry["dist"] * 100

    images = [
        (image1Setup1SampleB.image, image1Setup1SampleB.monitor),
        (image2Setup1SampleB.image, image2Setup1SampleB.monitor),
    ]
    data = {"@NX_class": "NXroot", "@default": "1.1"}
    for i, (image, I0) in enumerate(images, 1):
        data[f"{i}.1"] = {
            "@default": "plotselect",
            "instrument": {
                "@NX_class": "NXinstrument",
                "pilatus1": {
                    "@NX_class": "NXdetector",
                    "data": image,
                },
                "I0": {
                    "@NX_class": "NXdetector",
                    "data": I0,
                },
                "positioners": {"detz": detz, "detz@units": "cm"},
            },
            "title": f"sct {I0/tnorm}",
            "measurement": {
                ">pilatus1": "../instrument/pilatus1/data",
                ">I0": "../instrument/I0/data",
            },
            "plotselect": {
                "@NX_class": "NXdata",
                "@signal": "data",
                ">data": "../instrument/pilatus1/data",
            },
        }
    filename = str(datadir / "mask.h5")
    dicttonx(data, filename, update_mode="add")
    maskimage1 = f"silx://{filename}?path=/1.1/measurement/pilatus1"
    maskmonitor1 = f"silx://{filename}?path=/1.1/measurement/I0"
    maskimage2 = f"silx://{filename}?path=/2.1/measurement/pilatus1"
    maskmonitor2 = f"silx://{filename}?path=/2.1/measurement/I0"

    return maskimage1, maskmonitor1, maskimage2, maskmonitor2


def _holder_data(
    datadir, tnorm, imageSetup1SampleA, image1Setup1SampleB, image2Setup1SampleB, setup1
):
    detz = setup1.geometry["dist"] * 100
    assert imageSetup1SampleA.monitor == image1Setup1SampleB.monitor
    images = [
        (image2Setup1SampleB.image, image2Setup1SampleB.monitor),
        (
            imageSetup1SampleA.image + image1Setup1SampleB.image,
            imageSetup1SampleA.monitor,
        ),
    ]
    data = {"@NX_class": "NXroot", "@default": "2.1"}
    for i, (image, I0) in enumerate(images, 1):
        data[f"{i}.1"] = {
            "@default": "plotselect",
            "instrument": {
                "@NX_class": "NXinstrument",
                "pilatus1": {
                    "@NX_class": "NXdetector",
                    "data": image,
                },
                "I0": {
                    "@NX_class": "NXdetector",
                    "data": I0,
                },
                "positioners": {"detz": detz, "detz@units": "cm"},
            },
            "title": f"sct {I0/tnorm}",
            "measurement": {
                ">pilatus1": "../instrument/pilatus1/data",
                ">I0": "../instrument/I0/data",
            },
            "plotselect": {
                "@NX_class": "NXdata",
                "@signal": "data",
                ">data": "../instrument/pilatus1/data",
            },
        }
    filename = str(datadir / "holder.h5")
    dicttonx(data, filename, update_mode="add")
    backgroundimage = f"silx://{filename}?path=/1.1/measurement/pilatus1"
    background_monitor = f"silx://{filename}?path=/1.1/measurement/I0"
    sampleimage = f"silx://{filename}?path=/2.1/measurement/pilatus1"
    samplemonitor = f"silx://{filename}?path=/2.1/measurement/I0"

    return backgroundimage, background_monitor, sampleimage, samplemonitor
