"""
Wave kinematic module
"""
import sys
import os
from _WaveKinematic import set_logger_level, add_logger_callback
from .streamFunction import StreamFunction
from . import waveKinematic
mod = sys.modules[__name__]
for name in waveKinematic.availableWaveKinematic :
    setattr( mod , name , getattr( waveKinematic , name ) )
    
from .variableBathymetry import VariableBathymetry , check_second_order_flat

TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")