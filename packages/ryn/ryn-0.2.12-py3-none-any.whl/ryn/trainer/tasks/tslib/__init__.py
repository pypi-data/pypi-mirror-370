import os
import sys

# Get the path to the "tslib" folder (i.e. the current __init__.py's parent directory)
TSLIB_ROOT = os.path.dirname(os.path.abspath(__file__))

# Add TSLib root to sys.path so imports like `from models import ...` work
if TSLIB_ROOT not in sys.path:
    sys.path.insert(0, TSLIB_ROOT)
