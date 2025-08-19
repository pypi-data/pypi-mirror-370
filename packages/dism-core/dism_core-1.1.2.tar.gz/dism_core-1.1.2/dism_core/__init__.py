import logging

from .template import Template
from .validation.isvc import InferenceServiceValidator


logger = logging.getLogger(__name__)


try:
    from ._version import __version__, __version_tuple__
except ImportError:
    logger.warning(
        "The correct version of dism-core could not be resolved. This is likely due to "
        "a broken installation. The package needs to be correctly built, so that "
        "the build-system properly generates the version file. "
    )
    __version__ = "unknown"
    __version_tuple__ = (0, 0, "unknown")


__all__ = [
    "InferenceServiceValidator",
    "Template",
    "__version__",
    "__version_tuple__",
]
