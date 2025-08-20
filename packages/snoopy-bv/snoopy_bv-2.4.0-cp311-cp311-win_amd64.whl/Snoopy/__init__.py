"""
   Snoopy is an namespace package.
   => Subpackage (like Spectral, Meshing...) can be imported/distributed individually
"""

import sys
import os
import importlib
import logging
from os.path import join
import pkgutil
from .Tools import LogTimerFormatter
from .version import snoopy_tag

__version__ = snoopy_tag

def getDevPath(sharedCodeDir):
    """By default, return 'bin'.
    """
    if sys.platform == "linux":
        pyd_path = os.getenv("SNOOPY_PYD", "lib")
    else:
        pyd_path = os.getenv("SNOOPY_PYD", "bin")
    if "SNOOPY_PYD" in os.environ.keys() :
        logger.info( f"Using .pyd from user defined SNOOPY_PYD {pyd_path:}" )
    return pyd_path


# Create logger for Snoopy
class DualLogger(logging.Logger): # To set level in python and various cpp modules at the same time
    def setLevel(self, level, cpp = [], package="Snoopy", loggerName=""):
        logging.Logger.setLevel(self, level)
        if isinstance(cpp, str ) :
            if cpp == "all":
                cpp = ["Spectral" , "WaveKinematic", "TimeDomain" , "Statistics", "Tools", "Meshing"]
        for c in cpp :
            importlib.import_module(f"{package}.{c:}" ).set_logger_level( level, loggerName )
    
    def addCallbackCppHandler(self, callback, cpp=[], package="Snoopy", loggerName=""):
        if isinstance(cpp, str) and cpp == "all":
            cpp = ["Spectral" , "WaveKinematic", "TimeDomain" , "Statistics",
                   "Tools", "Meshing"]
        for c in cpp :
            importlib.import_module(f"{package}.{c:}" ).add_logger_callback(callback, loggerName)


logger = logging.getLogger(__name__)
logger.__class__ = DualLogger # Promote to "DualLogger", so that setLevel handles cpp spdlog level as well.
if len(logger.handlers) == 0 :  # Avoid re-adding handlers (When script is re-run with spyder for instance)
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(LogTimerFormatter())
    logger.addHandler(c_handler)


logger.setLevel(logging.INFO)

snoopyDir = os.path.abspath(join(os.path.dirname(__file__)))

#Handle path to pyd :
if "base_library.zip" in snoopyDir:  # Freezed case with pyInstaller. TODO : Check that this is still necessary, now that binaries are always copied in 'DLLs'
    pass
elif os.path.exists( os.path.join(snoopyDir, "DLLs") ) : # Case where Snoopy has been installed (in site package)
    #Better option would be to have the setup.py copying the binaries in correct folders. Would avoid messing with sys.path
    sys.path.insert(0, join(snoopyDir, "DLLs"))
else :
    subfolder = getDevPath(snoopyDir)
    logger.debug("dev path : {}".format(subfolder))
    if subfolder is not None:
        sys.path.insert(0, join(snoopyDir, subfolder))


# Make Snoopy a namespage package
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
