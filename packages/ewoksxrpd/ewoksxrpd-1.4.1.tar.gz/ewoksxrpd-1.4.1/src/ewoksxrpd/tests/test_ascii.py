import re
import zipfile

import h5py
import numpy
import pytest
from ewoksorange.tests.utils import execute_task
from silx.io.dictdump import dicttonx

from orangecontrib.ewoksxrpd.ascii import OWSaveAsciiPattern1D

from ..tasks.ascii import SaveAsciiMultiPattern1D
from ..tasks.ascii import SaveNexusPatternsAsAscii


def test_save_ascii_task(tmpdir, setup1):
    assert_save_ascii(tmpdir, setup1, None)


def test_save_ascii_widget(tmpdir, setup1, qtapp):
    assert_save_ascii(tmpdir, setup1, qtapp)


def assert_save_ascii(tmpdir, setup1, qtapp):
    inputs = {
        "filename": str(tmpdir / "result.dat"),
        "x": numpy.linspace(1, 60, 60),
        "y": numpy.random.random(60),
        "xunits": "2th_deg",
        "header": {
            "energy": 10.2,
            "detector": setup1.detector,
            "detector_config": setup1.detector_config,
            "geometry": setup1.geometry,
        },
        "metadata": {"name": "mysample"},
    }

    execute_task(
        OWSaveAsciiPattern1D.ewokstaskclass if qtapp is None else OWSaveAsciiPattern1D,
        inputs=inputs,
    )

    x, y = numpy.loadtxt(str(tmpdir / "result.dat")).T
    numpy.testing.assert_array_equal(x, inputs["x"])
    numpy.testing.assert_array_equal(y, inputs["y"])

    with open(tmpdir / "result.dat") as f:
        lines = list()
        for line in f:
            if not line.startswith("#"):
                break
            lines.append(line)
    lines = "".join(lines)

    for key in (
        "detector",
        "energy",
        "distance",
        "center dim0",
        "center dim1",
        "rot1",
        "rot2",
        "rot3",
        "xunits",
    ):
        assert f"{key} =" in lines
    assert "name = mysample" in lines
    m = re.findall("energy = (.+) keV", lines)
    assert len(m) == 1
    assert float(m[0]) == inputs["header"]["energy"]


def test_save_multi_ascii(tmpdir, setup1):
    inputs = {
        "filenames": [str(tmpdir / "result1.dat"), str(tmpdir / "result2.dat")],
        "x_list": [numpy.linspace(1, 60, 60), numpy.linspace(1, 60, 60)],
        "y_list": [numpy.random.random(60), numpy.random.random(60)],
        "yerror_list": [numpy.random.random(60), numpy.random.random(60)],
        "xunits_list": ["2th_deg", "2th_rad"],
        "header_list": [
            {
                "energy": 10.2,
                "detector": setup1.detector,
                "geometry": setup1.geometry,
            },
            {
                "energy": 9.8,
                "detector": setup1.detector,
                "geometry": setup1.geometry,
            },
        ],
        "metadata_list": [{"name": "mysample"}, {"name": "mysample"}],
    }

    execute_task(SaveAsciiMultiPattern1D, inputs=inputs)

    for (
        filename,
        input_x,
        input_y,
        input_yerror,
        input_header,
        input_metadata,
    ) in zip(
        inputs["filenames"],
        inputs["x_list"],
        inputs["y_list"],
        inputs["yerror_list"],
        inputs["header_list"],
        inputs["metadata_list"],
    ):
        x, y, yerror = numpy.loadtxt(filename).T
        numpy.testing.assert_array_equal(x, input_x)
        numpy.testing.assert_array_equal(y, input_y)
        numpy.testing.assert_array_equal(yerror, input_yerror)

        with open(filename) as f:
            lines = list()
            for line in f:
                if not line.startswith("#"):
                    break
                lines.append(line)
        lines = "".join(lines)

        for key in (
            "detector",
            "energy",
            "distance",
            "center dim0",
            "center dim1",
            "rot1",
            "rot2",
            "rot3",
            "xunits",
        ):
            assert f"{key} =" in lines
        for k, v in input_metadata.items():
            assert f"{k} = {v}" in lines
        matches = re.findall("energy = (.+) keV", lines)
        assert len(matches) == 1
        assert float(matches[0]) == input_header["energy"]


def test_SaveNexusPatternsAsAscii_single_pattern(tmp_path):
    """Test with a 1D signal, no errors and no "points" axis"""
    input_filename = str(tmp_path / "input.h5")
    nxdata_content = {
        "@NX_class": "NXdata",
        "@axes": ["q"],
        "@interpretation": "spectrum",
        "@signal": "intensity",
        "intensity": 2 * numpy.ones(100, dtype=numpy.float32),
        "q": numpy.linspace(0.01, 10, 100, dtype=numpy.float64),
        "q@units": "A^-1",
    }
    dicttonx(nxdata_content, input_filename, "/entry/integrated")

    task = SaveNexusPatternsAsAscii(
        inputs={
            "nxdata_url": f"{input_filename}::/entry/integrated",
            "output_filename_template": str(tmp_path / "output_%04d.xye"),
        }
    )
    task.execute()

    expected_filepath = tmp_path / "output_0000.xye"
    assert task.outputs.filenames == (str(expected_filepath),)

    # Check header
    text = expected_filepath.read_text().splitlines()
    assert "# xunits = A^-1" in text, "xunit is missing or wrong"

    # Check data
    assert numpy.array_equal(
        numpy.loadtxt(expected_filepath),
        # Expected array content:
        numpy.transpose(
            [
                nxdata_content["q"],
                nxdata_content["intensity"],
            ]
        ),
    ), "Saved data differs from original data"


def test_SaveNexusPatternsAsAscii_multi_patterns(
    tmp_path, multi_integrated_pattern_file
):
    """Test with a 2D signal, no errors and no "points" axis"""

    task = SaveNexusPatternsAsAscii(
        inputs={
            "nxdata_url": f"{multi_integrated_pattern_file}::/entry/integrated",
            "output_filename_template": str(tmp_path / "output_%04d.xye"),
            "header": {"info": "test"},
        }
    )
    task.execute()

    expected_filepaths = (
        tmp_path / "output_0000.xye",
        tmp_path / "output_0001.xye",
    )
    assert task.outputs.filenames == tuple(str(p) for p in expected_filepaths)

    with h5py.File(multi_integrated_pattern_file, "r") as h5file:
        input_q = h5file["/entry/integrated/q"][()]
        input_intensity = h5file["/entry/integrated/intensity"][()]

    for index, filepath in enumerate(expected_filepaths):
        # Check header
        text = filepath.read_text().splitlines()
        assert "# point =" not in text, "No point header expected"
        assert "# xunits = A^-1" in text, "xunit is missing or wrong"
        assert "# info = test" in text, "Header information is missing"

        # Check data
        assert numpy.array_equal(
            numpy.loadtxt(filepath),
            # Expected array content:
            numpy.transpose(
                [
                    input_q,
                    input_intensity[index],
                ]
            ),
        ), "Saved data differs from original data"


def test_SaveNexusPatternsAsAscii_multi_patterns_with_errors_and_points(tmp_path):
    """Test with a 2D signal, errors and a first "points" axis"""
    input_filename = str(tmp_path / "input.h5")
    nxdata_content = {
        "@NX_class": "NXdata",
        "@axes": ["points", "q"],
        "@interpretation": "spectrum",
        "@signal": "intensity",
        "intensity": 2 * numpy.ones((2, 100), dtype=numpy.float32),
        "intensity_errors": numpy.ones((2, 100), dtype=numpy.float32),
        "q": numpy.linspace(0.01, 10, 100, dtype=numpy.float64),
        "q@units": "A^-1",
        "points": [0, 1],
    }
    dicttonx(nxdata_content, input_filename, "/entry/integrated")

    task = SaveNexusPatternsAsAscii(
        inputs={
            "nxdata_url": f"{input_filename}::/entry/integrated",
            "output_filename_template": str(tmp_path / "output_%04d.xye"),
            "header": {"info": "test"},
        }
    )
    task.execute()

    expected_filepaths = (
        tmp_path / "output_0000.xye",
        tmp_path / "output_0001.xye",
    )
    assert task.outputs.filenames == tuple(str(p) for p in expected_filepaths)

    for index, filepath in enumerate(expected_filepaths):
        # Check header
        text = filepath.read_text().splitlines()
        assert (
            f"# point = {nxdata_content['points'][index]}" in text
        ), "Corresponding point value is missing or wrong"
        assert "# xunits = A^-1" in text, "xunit is missing or wrong"
        assert "# info = test" in text, "Header information is missing"

        # Check data
        assert numpy.array_equal(
            numpy.loadtxt(filepath),
            # Expected array content:
            numpy.transpose(
                [
                    nxdata_content["q"],
                    nxdata_content["intensity"][index],
                    nxdata_content["intensity_errors"][index],
                ]
            ),
        ), "Saved data differs from original data"


def test_SaveNexusPatternsAsAscii_zip(tmp_path, multi_integrated_pattern_file):
    """Test save as a ZIP file"""

    zip_filename = str(tmp_path / "archive.zip")
    task = SaveNexusPatternsAsAscii(
        inputs={
            "nxdata_url": f"{multi_integrated_pattern_file}::/entry/integrated",
            "output_filename_template": "output_%04d.xye",
            "output_archive_filename": zip_filename,
            "header": {"info": "test"},
        }
    )
    task.execute()

    assert task.outputs.filenames == (zip_filename,)

    extracted_path = tmp_path / "zip_content"
    zipf = zipfile.ZipFile(zip_filename)
    zipf.extractall(path=extracted_path)

    expected_filenames = "output_0000.xye", "output_0001.xye"
    assert tuple(zipf.namelist()) == expected_filenames

    with h5py.File(multi_integrated_pattern_file, "r") as h5file:
        input_q = h5file["/entry/integrated/q"][()]
        input_intensity = h5file["/entry/integrated/intensity"][()]

    for index, filename in enumerate(expected_filenames):
        filepath = extracted_path / filename
        # Check header
        text = filepath.read_text().splitlines()
        assert "# point =" not in text, "No point header expected"
        assert "# xunits = A^-1" in text, "xunit is missing or wrong"
        assert "# info = test" in text, "Header information is missing"

        # Check data
        assert numpy.array_equal(
            numpy.loadtxt(filepath),
            # Expected array content:
            numpy.transpose(
                [
                    input_q,
                    input_intensity[index],
                ]
            ),
        ), "Saved data differs from original data"


def test_overwrite_SaveNexusPatternsAsAscii(tmp_path, multi_integrated_pattern_file):
    expected_filepaths = (
        tmp_path / "output_0000.xye",
        tmp_path / "output_0001.xye",
    )

    for filepath in expected_filepaths:
        filepath.touch()
        assert filepath.exists()

    inputs = {
        "nxdata_url": f"{multi_integrated_pattern_file}::/entry/integrated",
        "output_filename_template": str(tmp_path / "output_%04d.xye"),
        "header": {"info": "test"},
    }

    task_without_overwrite = SaveNexusPatternsAsAscii(inputs=inputs)
    with pytest.raises(RuntimeError) as exc:
        task_without_overwrite.execute()
        assert isinstance(exc.__cause__, FileExistsError)

    task = SaveNexusPatternsAsAscii(
        inputs={
            **inputs,
            "overwrite": True,
        }
    )
    task.execute()

    assert task.outputs.filenames == tuple(str(p) for p in expected_filepaths)


def test_overwrite_zip_SaveNexusPatternsAsAscii(
    tmp_path, multi_integrated_pattern_file
):
    zip_filename = tmp_path / "archive.zip"
    zip_filename.touch()
    assert zip_filename.exists()

    inputs = {
        "nxdata_url": f"{multi_integrated_pattern_file}::/entry/integrated",
        "output_filename_template": "output_%04d.xye",
        "output_archive_filename": zip_filename,
        "header": {"info": "test"},
    }
    task_without_overwrite = SaveNexusPatternsAsAscii(inputs=inputs)
    with pytest.raises(RuntimeError) as exc:
        task_without_overwrite.execute()
        assert isinstance(exc.__cause__, FileExistsError)

    task = SaveNexusPatternsAsAscii(
        inputs={
            **inputs,
            "overwrite": True,
        }
    )
    task.execute()

    assert task.outputs.filenames == (zip_filename,)

    extracted_path = tmp_path / "zip_content"
    zipf = zipfile.ZipFile(zip_filename)
    zipf.extractall(path=extracted_path)

    expected_filenames = "output_0000.xye", "output_0001.xye"
    assert tuple(zipf.namelist()) == expected_filenames
