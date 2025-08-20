"""
Time domain module
"""
import sys


from .oneDof import OneDof
from .TimeSignals import getPSD, bandPass, slidingFFT,  fftDf, getRAO, reSample, rampDf
from .upCross import upCrossMinMax, plotUpCross, getUpCrossID , getDownCrossID, getUpCrossDist, plotUpCrossDist, peaksMax, getPeaksBounds, UpCrossAnalysis
from .srs import ShockResponseSpectrum
from .decluster import Decluster
from .decayTest import DecayAnalysis
from .concat_time_series import ConcatTimeSeries

from _TimeDomain import *

from .reconstruction1st import ReconstructionWif, ReconstructionWifLocal,ReconstructionRao, ReconstructionRaoLocal
from .reconstructionRaoFFT import ReconstructionRaoLocalFFT
from .reconstructionQtf import ReconstructionQtf, ReconstructionQtfLocal
from .reconstructionMulti import ReconstructionMulti
from .radiation import RetardationFunctionsHistory
from .slammingVelocity import getSlammingVelocity



import os
TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")