"""
Tools used to configure the web and cli applications during initialization.

Must not have any dependency other than stdlib, because this module's `ensure_dotenv_pythonpath` may be used (e.g. by `manage.py`) to update the dependency path.
"""
from __future__ import annotations

import logging
import os
import re
import sys
from ctypes.util import find_library
from pathlib import Path

_logger = logging.getLogger(__name__)

def ensure_dotenv_pythonpath():
    if not os.path.exists('.env'):
        return
    
    with open('.env', 'r', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            m = re.match(r'^PYTHONPATH\s*=(.+)$', line)
            if m:
                for path in reversed(m[1].split(';' if sys.platform == 'win32' else ':')):
                    path = str(Path(path.strip()).resolve())
                    if not path in sys.path:
                        sys.path.insert(0, path)


def find_module_apps() -> list[str]:
    app_names: list[str] = []

    # Search in environment variable
    strlist = os.environ.get('MODULES')
    if strlist:
        for app in strlist.strip().split(','):
            if not app in app_names:
                app_names.append(app)

    # Search in 'modules' directory
    modules_dir = Path('modules').absolute()
    if modules_dir.exists():
        for module_dir in sorted(modules_dir.iterdir()):
            for app in _search_apps(module_dir):
                if not str(module_dir) in sys.path:
                    _logger.warning(f"Cannot use module app `{app}`: module `{module_dir}` not in Python path")

                if not app in app_names:
                    app_names.append(app)

    return app_names


def _search_apps(base_path: str|os.PathLike, base_module: str = '', *, max_depth = 2) -> list[str]:
    if not isinstance(base_path, Path):
        base_path = Path(base_path)
    
    if not base_path.exists():
        return []
    elif not base_path.is_dir():
        return []
    elif not re.match(r'^[a-z][a-z0-9_]*$', base_path.name, re.IGNORECASE):
        return []    
    elif base_module:
        if base_path.joinpath('apps.py').exists():
            return [base_module]

    # Recurse
    if max_depth <= 0:
        return []

    apps: list[str] = []
    for sub_path in sorted(base_path.iterdir()):
        sub_module = (f'{base_module}.' if base_module else '') + sub_path.stem
        for app in _search_apps(sub_path, sub_module, max_depth=max_depth - 1):
            apps.append(app)

    return apps


def find_gdal_library_path():
    """
    See: https://docs.djangoproject.com/en/5.2/ref/contrib/gis/install/geolibs/
    """    
    if os.name == "nt":
        lib_names = [
            "libgdal-35", # PostGIS installed with PostgreSQL 17 StackBuilder.
            "gdal309",
            "gdal308",
            "gdal307",
            "gdal306",
            "gdal305",
            "gdal304",
            "gdal303",
            "gdal302",
            "gdal301",
            "gdal300",
        ]
    else:
        lib_names = [
            "gdal",
            "GDAL",
            "gdal3.9.0",
            "gdal3.8.0",
            "gdal3.7.0",
            "gdal3.6.0",
            "gdal3.5.0",
            "gdal3.4.0",
            "gdal3.3.0",
            "gdal3.2.0",
            "gdal3.1.0",
            "gdal3.0.0",
        ]

    for name in lib_names:
        path = find_library(name)
        if path:
            return path


def find_geos_library_path():
    """
    See: https://docs.djangoproject.com/en/5.2/ref/contrib/gis/install/geolibs/
    """
    if os.name == "nt":
        lib_names = [
            "geos_c",
            "libgeos_c", # PostGIS installed with PostgreSQL 17 StackBuilder.
            "libgeos_c-1",
        ]
    else:
        lib_names = [
            "geos_c",
            "GEOS"
        ]
    
    for name in lib_names:
        path = find_library(name)
        if path:
            return path
