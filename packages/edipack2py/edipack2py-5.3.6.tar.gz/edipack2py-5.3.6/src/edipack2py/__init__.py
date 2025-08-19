from edipack2py import class_creator
from ctypes import *
import numpy as np

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:  # For Python <3.8
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("edipack2py")
except PackageNotFoundError:
    __version__ = "unknown"

# this ed class contains all the global variables and methods
global_env = class_creator.global_env

