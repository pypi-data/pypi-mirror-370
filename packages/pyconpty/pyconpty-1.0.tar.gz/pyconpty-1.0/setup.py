# This code is part of the PyConPTY python package.
# PyConPTY: A Python wrapper for the ConPTY (Windows Pseudo-console) API
# Copyright (C) 2025  MELWYN FRANCIS CARLO

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# For queries, contact me at: melwyncarlo@gmail.com

# pylint: disable=missing-module-docstring

import sys
import platform
from setuptools import setup, Extension

ERROR_MESSAGE = (
    "\n PyConPTY cannot be installed on this particular computer."
    "\n PyConPTY requires Windows 10 Version 1809 Build 17763 "
    "(Windows 10.0.17763) or later.\n"
)

if platform.system().lower().strip() != "windows":
    sys.exit(ERROR_MESSAGE)
version_info_list = list(map(int, platform.version().split(".")))
# Windows 10 Version 1809 Build 17763 (Windows 10.0.17763) Check
if not (
    version_info_list[0] >= 10
    and version_info_list[1] >= 0
    and version_info_list[2] >= 17763
):
    sys.exit(ERROR_MESSAGE)

setup(
    ext_modules=[
        Extension(
            "_pyconptyinternal",
            sources=["src/pyconpty/_pyconptyinternal.c"],
            language="c",
            extra_compile_args=[
                "/O2",
                "/GL",
                "/EHsc",
                "/D_UNICODE",
                "/DUNICODE",
                "/experimental:c11atomics",
                "/std:c17",
                "/external:anglebrackets",
                "/external:W0",
                "/Wall",
                "/WX",
                # Heuristic Inline Expansion
                "/wd4711",
                # Spectre Mitigation
                "/wd5045",
                # For testing only:
                # "/Zi",
                # "/fsanitize=address",
            ],
            # For testing:
            # extra_link_args=["/PROFILE", "/DEBUG:FULL", "/LTCG"],
            # For release:
            extra_link_args=["/DEBUG:NONE", "/LTCG"],
        )
    ]
)
