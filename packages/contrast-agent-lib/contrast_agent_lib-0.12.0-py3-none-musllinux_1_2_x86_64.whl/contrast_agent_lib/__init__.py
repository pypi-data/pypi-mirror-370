import ctypes

import sys
import platform
from os import path

from . import constants

lib_name = "libcontrast_c"
if path.exists("/etc/alpine-release"):
    lib_name += "_musl"

if sys.platform.startswith("darwin"):
    lib_ext = ".dylib"
    if "arm64" in platform.machine():
        lib_name += "_arm64"
else:
    lib_ext = ".so"
    if "aarch64" in platform.machine():
        lib_name += "_aarch64"

lib_path = "".join([path.dirname(__file__), "/libs/", lib_name, lib_ext])
lib_contrast = ctypes.cdll.LoadLibrary(lib_path)

__all__ = ["constants", "lib_contrast"]
