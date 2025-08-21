import numpy as np
_xmax_log = np.log(np.finfo(float).max)
import _Statistics
from _Statistics import set_logger_level
from _Statistics import genpareto_2p, omp_set_num_threads, omp_get_max_threads, rayleigh_cdf, normal_pdf
from .empirical_quantiles import probN , probN_ci
from .dist import DistGen, FrozenDistABC
from .statErrors import StatErrors
from ._longTerm import LongTerm, LongTermSpectral, squashSpectralResponseList, LongTermGen
from ._longTermSD import LongTermSD, LongTermRao, LongTermQuadDamping
from ._impact_velocity import LongTermImpact, LongTermImpactSL
from .powern import Powern
from .maxEntropySolver import MaxEntropySolver
from .distribution_cpp import  weibull_min_c, geneextreme_c, rayleigh_c, gengamma_patched, Rayleigh_n, pearson3_patched
from .returnLevel import ReturnLevel
from .discreteSD import DiscreteSD
from ._pot import POT, POT_GPD, rolling_declustering, MeanResidualLife, ThresholdSensitivity
from ._blockMaxima import BM, BM_GEV, BlockSizeSensitivity
from ._diform import DirectIform, DirectIformBM
from ._misc import compact_probability_df
#By default no openmp
omp_set_num_threads(1)

import os
TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")