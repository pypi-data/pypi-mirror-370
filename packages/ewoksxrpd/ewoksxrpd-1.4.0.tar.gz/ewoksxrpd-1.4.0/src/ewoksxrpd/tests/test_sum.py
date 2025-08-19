import os
from numbers import Integral

import pytest
from ewoksorange.tests.utils import execute_task

from ..tasks import sum


@pytest.mark.parametrize("monitor_name", ("mon", None))
@pytest.mark.parametrize("background_step", [False, True])
def test_sum_bliss_scan(tmpdir, bliss_perkinelmer_scan, monitor_name, background_step):
    inputs = {
        "filename": str(bliss_perkinelmer_scan),
        "detector_name": "perkinelmer",
        "monitor_name": monitor_name,
        "output_filename": str(tmpdir / "output.h5"),
        "scan": 2,
        "background_step": background_step,
    }

    outputs = execute_task(sum.SumBlissScanImages, inputs=inputs)

    assert os.path.isfile(str(tmpdir / "output.h5"))
    assert isinstance(outputs["output_uri"], str)
    if monitor_name is None:
        assert outputs["monitor"] is None
    else:
        assert isinstance(outputs["monitor"], Integral)


@pytest.mark.parametrize("monitor_name", ("mon", None))
def test_sum(tmpdir, bliss_perkinelmer_scan, monitor_name):
    inputs = {
        "filename": str(bliss_perkinelmer_scan),
        "detector_name": "perkinelmer",
        "monitor_name": monitor_name,
        "output_filename": str(tmpdir / "output.h5"),
        "start_scan": 2,
        "end_image": 10,
        "end_scan": 2,
    }

    outputs = execute_task(sum.SumImages, inputs=inputs)

    assert os.path.isfile(str(tmpdir / "output.h5"))
    assert len(outputs["output_uris"]) == 1
    if monitor_name is None:
        assert outputs["monitor_uris"] is None
    else:
        assert len(outputs["monitor_uris"]) == 1


def test_sum_type_both(tmpdir, bliss_perkinelmer_scan):
    inputs = {
        "filename": str(bliss_perkinelmer_scan),
        "detector_name": "perkinelmer",
        "output_filename": str(tmpdir / "output.h5"),
        "start_scan": 2,
        "end_scan": 2,
        "sum_type": "both",
        "monitor_name": "mon",
    }

    outputs = execute_task(
        sum.SumImages,
        inputs=inputs,
    )

    assert os.path.isfile(str(tmpdir / "output.h5"))
    # Scan sum and full sum
    assert len(outputs["output_uris"]) == 2
    assert len(outputs["monitor_uris"]) == 2


@pytest.mark.parametrize("background_step", range(-1, 4))
def test_tscan_background_step(background_step):
    for npoints in range(1, 21):
        total_points, background_step, include_indices, skip_indices = tscan(
            npoints, background_step=background_step
        )
        assert npoints == len(include_indices)
        assert total_points == len(include_indices) + len(skip_indices)

        counter_iterator = range(total_points)
        include_indices2 = [
            i for i, _ in sum.iterate_scan_with_skip(counter_iterator, background_step)
        ]

        assert include_indices == include_indices2


def tscan(npoints: int, background_step: int):
    """
    :param npoints: number of lima images
    :param background_step: -1 means no background, 0 means only one dark, N>0 means a dark every N image
    """

    # Keep this logic as much as possible, even when we can make it cleaner:
    # https://gitlab.esrf.fr/bcu-vercors/id22/id22/-/blob/master/id22/scripts/tscan.py

    last_image = -1
    if background_step > npoints:
        background_step = npoints
    if background_step >= 0:
        if background_step == 0:
            bkg_range = [0]
        else:
            bkg_range = range(0, npoints, background_step)

        # now calculate the real range for bkgd image in total scan
        nb_background = len(bkg_range)
        total_points = npoints + nb_background
        last_image = total_points - 1

        if background_step > 0:
            bkg_range = range(0, total_points, background_step + 1)
    else:
        total_points = npoints
        bkg_range = None

    save_manual = bkg_range is not None  # this is missing in the original code!

    shutter = "OPEN"
    open_indices = list()
    closed_indices = list()
    for iteration in range(total_points):
        # TscanChainPreset.Iterator.start
        if bkg_range and iteration in bkg_range:
            shutter = "CLOSED"

        # Measure scan point `iteration`
        if shutter == "CLOSED":
            closed_indices.append(iteration)
        else:
            assert shutter == "OPEN"
            if not save_manual:
                open_indices.append(iteration)

        # TscanChainPreset.Iterator.stop
        if save_manual and bkg_range is not None:
            if (
                bkg_range is not None
                and iteration not in bkg_range
                and iteration != last_image
            ):
                assert shutter == "OPEN"
                open_indices.append(iteration)
        if bkg_range and iteration in bkg_range:
            shutter = "OPEN"

    # TscanChainPreset.before_stop
    if last_image >= 0:
        open_indices.append(iteration)

    # TscanChainPreset.stop
    shutter = "CLOSED"

    return total_points, background_step, open_indices, closed_indices
