import importlib.metadata
import os
import sys
from typing import Optional


try:
    __version__ = importlib.metadata.version("nqs_sdk")
except importlib.metadata.PackageNotFoundError:
    # If package is not installed, try to read version from pyproject.toml
    try:
        # Use tomllib for Python 3.11+ or tomli for earlier versions
        if sys.version_info >= (3, 11):
            import tomllib
        else:
            raise ImportError("Python 3.11 or later is required to use this package.")

        # Find the pyproject.toml file
        # Start with the directory of this file and go up until we find pyproject.toml
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root: Optional[str] = current_dir
        while project_root and not os.path.exists(os.path.join(project_root, "pyproject.toml")):
            parent = os.path.dirname(project_root)
            if parent == project_root:  # Reached the root directory
                project_root = None
                break
            project_root = parent

        if project_root:
            pyproject_path = os.path.join(project_root, "pyproject.toml")
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                __version__ = pyproject_data.get("project", {}).get("version")
            if __version__ is None:
                from nqs_sdk.nqs_sdk import version as core_version

                # fallback to core version written in Rust binary
                __version__ = core_version()
        else:
            __version__ = "unknown - pyproject.toml not found"
    except Exception as e:
        __version__ = f"unknown - error reading version: {str(e)}"
