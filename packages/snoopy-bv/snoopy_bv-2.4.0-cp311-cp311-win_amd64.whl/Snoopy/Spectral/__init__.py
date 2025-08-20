import sys
from _Spectral import *

from .seastate import SeaState, SeaState2D, compareSeaStatePlot, SeaState2D_Fourier
from .seaStateList import SeaStatesDF
from .wif import Wif
from .wifm import Wifm
from .rao import Rao, getUnitRao
from .spectralStats import  RsFromM0, AsFromM0, RtzFromM0M2, SpectralStats, msi , msi_from_motion , idss_convert_rp, idss_hs_ratio
from .qtf import Qtf
from .mqtf import MQtf
from .responseSpectrum import ResponseSpectrum, ResponseSpectrum2nd, ResponseSpectrumEncFrequency
from .dampingLinearization import StochasticDamping, SpectralMomentsSL
from .wib import Wib
from .edw import rcwCalc, constrainedWave, Edw_Rao, NewWave
from .dispersion import w2k, k2w, w2we, k2Cp, w2l, w2Cg, l2t, T2Te, t2l, we2w, cp2t, cp2k, t2k, l2w, w2Cp
from . import spectrum
from .spectrum import SpectrumType, Spectrum , specMaker
from .misc import modesIntsToNames, modesIntToMode, modesTypeComponentToIntDict, modesIntToTypeComponentDict,\
         modesDf,modeFromModesTypeComponent,modeToModesTypeComponent
from .spectralStats import ampFromRperiod, ampFromRisk_py
from .headingConvention import plotHeadingConfiguration
from .enc_freq import ContourWeSpeed, ContourWeW, ContourWeW_t
from .spectralMoments import SpectralMoments

mod = sys.modules[__name__]
for name in spectrum.availableSpectra :
    setattr( mod , name , getattr( spectrum , name ) )

from .spreading import Cosn, Wnormal, Cos2s
ParametricSpectrum = spectrum.ParametricSpectrum
import os
TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")
