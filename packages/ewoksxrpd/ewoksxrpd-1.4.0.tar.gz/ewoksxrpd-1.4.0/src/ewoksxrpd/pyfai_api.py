from importlib.metadata import version
from packaging.version import Version

PYFAI_VERSION = Version(version("pyFAI"))

if PYFAI_VERSION >= Version("2025.1.0"):
    from pyFAI.integrator.azimuthal import AzimuthalIntegrator  # noqa F401
else:
    from pyFAI.azimuthalIntegrator import AzimuthalIntegrator  # noqa F401

if PYFAI_VERSION >= Version("2025.1.0"):
    from pyFAI.io.integration_config import (
        CURRENT_VERSION as INTEGRATION_SCHEMA_VERSION_MAX,
    )

    INTEGRATION_SCHEMA_VERSION_MIN = 1
elif PYFAI_VERSION >= Version("2024.9.0"):
    INTEGRATION_SCHEMA_VERSION_MAX = 4
    INTEGRATION_SCHEMA_VERSION_MIN = 1
else:
    INTEGRATION_SCHEMA_VERSION_MAX = 3
    INTEGRATION_SCHEMA_VERSION_MIN = 1
