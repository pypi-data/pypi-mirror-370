# Re-export public entry points
from . import data  # noqa: F401
from . import model  # noqa: F401
from . import trainer  # noqa: F401
from .update_checker import check_latest_version  # noqa: F401

# Trigger a lightweight version check on import (non-fatal).
check_latest_version("ryn")

# Package metadata
__all__ = ["data", "model", "trainer"]
__version__ = "0.1.0"
__description__ = "Ryn SDK: data, model, and trainer interfaces"
