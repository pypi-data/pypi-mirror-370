import numpy
from ewoksorange.tests.utils import execute_task

from ..pyfai_api import AzimuthalIntegrator

from orangecontrib.ewoksxrpd.mask import OWMaskDetection

from .xrpd_theory import Measurement


def test_mask_detection_task(
    image1Setup1SampleB: Measurement,
    image2Setup1SampleB: Measurement,
    aiSetup1: AzimuthalIntegrator,
):
    assert_mask_detection(image1Setup1SampleB, image2Setup1SampleB, aiSetup1, None)


def test_mask_detection_widget(
    image1Setup1SampleB: Measurement,
    image2Setup1SampleB: Measurement,
    aiSetup1: AzimuthalIntegrator,
    qtapp,
):
    assert_mask_detection(image1Setup1SampleB, image2Setup1SampleB, aiSetup1, qtapp)


def assert_mask_detection(
    image1Setup1SampleB: Measurement,
    image2Setup1SampleB: Measurement,
    aiSetup1: AzimuthalIntegrator,
    qtapp,
):
    inputs = {
        "image1": image1Setup1SampleB.image,
        "monitor1": image1Setup1SampleB.monitor,
        "image2": image2Setup1SampleB.image,
        "monitor2": image2Setup1SampleB.monitor,
    }
    results = execute_task(
        OWMaskDetection.ewokstaskclass if qtapp is None else OWMaskDetection,
        inputs=inputs,
    )

    expected = aiSetup1.detector.get_mask()
    numpy.testing.assert_array_equal(results["mask"], expected)

    inputs["smooth"] = 5
    results = execute_task(
        OWMaskDetection.ewokstaskclass if qtapp is None else OWMaskDetection,
        inputs=inputs,
    )

    borders = results["mask"] - expected
    assert not (borders == 0).all(), "smoothing should add masked pixels"
    assert not (borders < 0).any(), "smoothing should never remove masked pixels"
