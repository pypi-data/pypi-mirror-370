import enum
import pytest
from pyFAI.detectors.orientation import Orientation

from ..tasks.utils import pyfai_utils


def test_builtin_types():
    parameters = {
        "key1": 10,
        "key2": "normal",
        "key3": [
            "/gpfs/jazzy",
            "/gpfs/jazzy/",
            "silx:///gpfs/jazzy/path/to/file",
            "/mnt/multipath-shares/path/to/file",
        ],
    }
    parameters["key4"] = {
        "key1": 10,
        "key2": "normal",
        "key3": [
            "/gpfs/jazzy",
            "/gpfs/jazzy/",
            "silx:///gpfs/jazzy/path/to/file",
            "/mnt/multipath-shares/path/to/file",
        ],
    }
    normalized = {
        "key1": 10,
        "key2": "normal",
        "key3": ["/gpfs/jazzy", "/", "silx:///path/to/file", "/path/to/file"],
    }
    normalized["key4"] = {
        "key1": 10,
        "key2": "normal",
        "key3": ["/gpfs/jazzy", "/", "silx:///path/to/file", "/path/to/file"],
    }
    assert pyfai_utils.normalize_parameters(parameters) == normalized


def test_enum_types():
    Color = enum.Enum("Color", ["RED", "GREEN", "BLUE"])

    parameters = {"key1": Orientation.BottomRight, "key2": Color.GREEN}
    normalized = {"key1": Orientation.BottomRight.value, "key2": 2}

    assert pyfai_utils.normalize_parameters(parameters) == normalized


def test_unexpected_type():
    class UnexpectedClass:
        pass

    with pytest.warns(
        UserWarning,
        match="Unexpected pyFAI configuration parameter type",
    ):
        parameters = {"key": UnexpectedClass()}
        _ = pyfai_utils.normalize_parameters(parameters)
