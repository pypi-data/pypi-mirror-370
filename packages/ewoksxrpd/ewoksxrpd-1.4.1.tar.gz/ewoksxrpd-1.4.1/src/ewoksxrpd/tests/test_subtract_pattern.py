import h5py
import numpy
import pytest
from silx.io.dictdump import dicttonx

from ewoksxrpd.tasks.subtract_pattern import SubtractBackgroundPattern

NXDATA_METADATA = {
    "@NX_class": "NXdata",
    "@axes": [".", "q"],
    "@interpretation": "spectrum",
    "@signal": "intensity",
}


@pytest.mark.parametrize("background_factor", (1, 0.1))
def test_normal_execution(tmp_path, background_factor):
    q = numpy.linspace(0.01, 10, 100, dtype=numpy.float64)
    input_data = 2 * numpy.ones((2, 100), dtype=numpy.float32)
    background_data = numpy.ones((1, 100), dtype=numpy.float32)

    # Create input file
    input_filename = tmp_path / "input.h5"
    input_nxdata = {
        **NXDATA_METADATA,
        "q": q,
        "q@units": "A^-1",
        "intensity": input_data,
        "points": [0, 1],
    }
    dicttonx(input_nxdata, input_filename, "/entry/process/integrated")

    # Create background file
    bg_filename = tmp_path / "background.h5"
    bg_nxdata = {
        **NXDATA_METADATA,
        "q": q,
        "q@units": "A^-1",
        "intensity": background_data,
    }
    dicttonx(bg_nxdata, bg_filename, "/entry/process/integrated")

    inputs = {
        "nxdata_url": f"{input_filename}::/entry/process/integrated",
        "background_nxdata_url": f"{bg_filename}::/entry/process/integrated",
        "background_factor": background_factor,
    }
    task = SubtractBackgroundPattern(inputs={**inputs})
    task.execute()

    assert (
        task.get_output_value("nxdata_url")
        == f"{input_filename}::/entry/process_subtracted/integrated"
    )

    with h5py.File(input_filename, "r") as h5file:
        subtracted_intensity = h5file["/entry/process_subtracted/integrated/intensity"][
            ()
        ]
        numpy.testing.assert_allclose(
            subtracted_intensity,
            numpy.ones((2, 100), dtype=numpy.float32) * (2 - background_factor),
        )
        numpy.testing.assert_allclose(
            h5file["/entry/process/integrated/q"][()],
            h5file["/entry/process_subtracted/integrated/q"][()],
        )
        numpy.testing.assert_allclose(
            h5file["/entry/process/integrated/points"][()],
            h5file["/entry/process_subtracted/integrated/points"][()],
        )
        for name, value in inputs.items():
            stored_value = h5file["/entry/process_subtracted/configuration"][name][()]
            if isinstance(stored_value, bytes):
                stored_value = stored_value.decode()
            assert stored_value == value


def test_with_different_shape_background(tmp_path):
    input_q = numpy.linspace(0.01, 10, 100, dtype=numpy.float64)
    input_data = 2 * numpy.ones((2, 100), dtype=numpy.float32)

    input_filename = tmp_path / "input.h5"
    input_nxdata = {
        **NXDATA_METADATA,
        "q": input_q,
        "q@units": "A^-1",
        "intensity": input_data,
    }
    dicttonx(input_nxdata, input_filename, "/entry/integrated")

    background_q = numpy.linspace(0.01, 10, 50, dtype=numpy.float64)
    background_data = 2 * numpy.ones((2, 50), dtype=numpy.float32)
    bg_filename = tmp_path / "background.h5"
    bg_nxdata = {
        **NXDATA_METADATA,
        "q": background_q,
        "q@units": "A^-1",
        "intensity": background_data,
    }
    dicttonx(bg_nxdata, bg_filename, "/entry/integrated")

    task = SubtractBackgroundPattern(
        inputs={
            "nxdata_url": f"{input_filename}::/entry/integrated",
            "background_nxdata_url": f"{bg_filename}::/entry/integrated",
        }
    )
    with pytest.raises(RuntimeError) as exception:
        task.execute()
    original_exception = exception.value.__cause__
    assert isinstance(original_exception, ValueError)
    assert "not compatible with data pattern" in str(original_exception)


def test_with_different_unit_background(tmp_path):
    q = numpy.linspace(0.01, 10, 100, dtype=numpy.float64)
    input_data = 2 * numpy.ones((2, 100), dtype=numpy.float32)
    background_data = numpy.ones((1, 100), dtype=numpy.float32)

    # Create input file
    input_filename = tmp_path / "input.h5"
    input_nxdata = {
        **NXDATA_METADATA,
        "q": q,
        "q@units": "A^-1",
        "intensity": input_data,
    }
    dicttonx(input_nxdata, input_filename, "/entry/integrated")

    # Create background file
    bg_filename = tmp_path / "background.h5"
    bg_nxdata = {
        **NXDATA_METADATA,
        "q": q,
        "q@units": "nm^-1",
        "intensity": background_data,
    }
    dicttonx(bg_nxdata, bg_filename, "/entry/integrated")

    task = SubtractBackgroundPattern(
        inputs={
            "nxdata_url": f"{input_filename}::/entry/integrated",
            "background_nxdata_url": f"{bg_filename}::/entry/integrated",
        }
    )
    with pytest.raises(RuntimeError) as exception:
        task.execute()
    original_exception = exception.value.__cause__
    assert isinstance(original_exception, ValueError)
    assert "not compatible with data pattern" in str(original_exception)
