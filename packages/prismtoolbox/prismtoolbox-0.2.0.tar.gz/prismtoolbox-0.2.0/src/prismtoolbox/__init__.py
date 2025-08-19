import importlib.metadata
import logging
from ._logging import configure_logger

__version__ = importlib.metadata.version("prismtoolbox")

log = logging.getLogger("prismtoolbox")
configure_logger(log)

from .wsicore import WSI
from .utils import data_utils, qupath_utils, vis_utils

__all__ = ["WSI", "data_utils", "qupath_utils", "vis_utils"]
