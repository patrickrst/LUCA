#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    This file is part of LUCA.

    LUCA - LEGO Universe Creation (Lab) Archiver
    Created 2013 Brickever <http://systemonbrick.wordpress.com/>

    LUCA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    LUCA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with LUCA If not, see <http://www.gnu.org/licenses/>.
"""

# LUCA setup script using cx_Freeze.
from cx_Freeze import setup, Executable
import sys

# Freeze into the proper folder depending on the architecture
if sys.maxsize == 2147483647:
    destfolder = "Builds/Windows32"
else:
    destfolder = "Builds/Windows64"

build_exe_options = {"build_exe": destfolder}

setup(
    name="LUCA",
    version="0.4",
    author="Brickever",
    description="LEGO Universe Creation (Lab) Archiver",
    license="GNU GPLv3",
    options={"build_exe": build_exe_options},
    executables=[Executable("LUCA.py", targetName="LUCA.exe")]
)
