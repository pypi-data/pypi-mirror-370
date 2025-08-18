# Lightweight version checker using PyPI JSON API.
# Importing 'requests' inside the function keeps import-time failures away.

from __future__ import annotations

def check_latest_version(package_name: str = "ryn", auto_warn: bool = True):
    """Compare installed version with PyPI and optionally print a hint.

    Returns:
        Tuple[bool|None, str|None, str|None]
    """
    try:
        import importlib.metadata
        current_version = importlib.metadata.version(package_name)
        try:
            import requests  # Imported lazily
            resp = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
            resp.raise_for_status()
            latest_version = resp.json()["info"]["version"]
        except Exception:
            return None, current_version, None
        if current_version != latest_version:
            if auto_warn:
                print(
                    f"[Update] A newer version ({latest_version}) is available. "
                    f"You are using {current_version}."
                )
            return False, current_version, latest_version
        return True, current_version, latest_version
    except Exception:
        # Any failure should not break imports
        return None, None, None
