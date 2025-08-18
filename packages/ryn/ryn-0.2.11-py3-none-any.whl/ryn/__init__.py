# ryn/__init__.py
from . import data     # noqa: F401
from . import model    # noqa: F401
from . import trainer  # noqa: F401

# Optional: light PyPI update hint on import
try:
    from .update_checker import check_latest_version  # noqa: F401
    check_latest_version("ryn")
except Exception:
    pass

__all__ = ["data", "model", "trainer"]
__version__ = "0.2.11"
__description__ = "Ryn SDK: data, model, and trainer interfaces"
