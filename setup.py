#! /usr/bin/python3
# -*- coding: utf-8 -*-

# LUCA setup script using cx_Freeze.
# Taken from https://github.com/le717/SSS

from cx_Freeze import setup, Executable
import sys
import os

# Append build to the arguments. Just type "python setup.py" and it will compile
if len(sys.argv) == 1: sys.argv[1:] = ["build"]

# Compile into the proper folder depending on the architecture
# Based on code from the Python help file (platform module) and my own tests
if sys.maxsize == 2147483647:
    destfolder = "Compile/Windows32"
else:
    destfolder = "Compile/Windows64"

build_exe_options = {"build_exe": destfolder}

setup(
    name = "LUCA",
    version = "0.2",
    author = "Brickever",
    description = "LEGO Universe Creation (Lab) Archiver",
    license = "GNU GPLv3",
    options = {"build_exe": build_exe_options},
    executables = [Executable("LUCA.py", targetName="LUCA.exe")]
)