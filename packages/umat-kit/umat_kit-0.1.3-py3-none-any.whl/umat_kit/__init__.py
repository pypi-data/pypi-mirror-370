"""
umat_kit: A well-structured toolkit and CLI for UMAT API testing and utilities.

This package exposes modules for programmatic use and provides a Rich-powered CLI.
"""
from __future__ import annotations

# Make legacy absolute imports inside migrated modules work without mass refactors
# Example: modules using `from api import ...` or `from utils import ...` will resolve
# to `umat_kit.api` and `umat_kit.utils` respectively when imported as a package.
import sys as _sys

# Import subpackages first so we can alias them
from . import api as _pkg_api
from . import utils as _pkg_utils
from . import config as _pkg_config

# Alias legacy top-level names used by migrated modules
# After copying, some files contain absolute imports like `from api.x import Y`.
# These aliases map them to the packaged modules so imports resolve.
_sys.modules.setdefault("api", _pkg_api)
_sys.modules.setdefault("utils", _pkg_utils)
_sys.modules.setdefault("config", _pkg_config)

# Also alias the nested utils.utils to "utils" for safety (due to copy structure)
try:
    from .utils import utils as _pkg_utils_utils  # nested module where actual files live
    _sys.modules.setdefault("utils.logger", _pkg_utils_utils.logger)
    _sys.modules.setdefault("utils.terminal_colors", _pkg_utils_utils.terminal_colors)
    _sys.modules.setdefault("utils.validators", _pkg_utils_utils.validators)
    _sys.modules.setdefault("utils.crypto", _pkg_utils_utils.crypto)
except Exception:
    # Non-fatal; standard aliasing above should be enough in most environments
    pass

# Re-export main API types for convenience
# Import from the nested module (api.api) because copied code created an extra level
from .api.api import APIManager, LoginAPI, UserInfoAPI  # type: ignore F401
from .config import config, config_manager  # type: ignore F401

__all__ = [
    "APIManager",
    "LoginAPI",
    "UserInfoAPI",
    "config",
    "config_manager",
]