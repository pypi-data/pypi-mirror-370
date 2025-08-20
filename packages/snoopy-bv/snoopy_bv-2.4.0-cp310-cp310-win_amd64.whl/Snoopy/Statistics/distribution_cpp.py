import _Statistics
from .dist import DistGen

"""

   Different "API" available :

       - dist_c  : Pure Snoopy distribution (implemented in c++), mimic scipy API, but parametrization might be different and all method not available.
       - dist_patched : Same as Scipy, with only _pdf and _logpdf re-implemented in cpp
       - dist_p : Same as Scipy, with only _pdf and _logpdf re-implemented in python and vectorize with numba (target == parallel)

   Eventually, it seems that the latest speed-up option is both the lighter and more efficient. This file is for c++ distribution.



   Those distribution are not imported on Snoopy.Statistic loading to save loading time if not needed (vectorization can take time).
"""



class DistGenCpp( DistGen ):
    @property
    def nDof(self) :
        return self.get_nDof()


#Rayleigh distribution, different from scipy (floc=0)
class Rayleigh(_Statistics.Rayleigh, DistGenCpp) :
    pass
rayleigh_c = Rayleigh()
rayleigh_c.name = "rayleigh_c"          # TODO : move to c++
rayleigh_c.scipy_name = "rayleigh"          # TODO : move to c++



#Rayleigh distribution **n
class Rayleigh_n(_Statistics.Rayleigh_n, DistGenCpp) :
    pass


#------- Re-implement most method for weibull_min
class Weibull(_Statistics.Weibull, DistGenCpp) :
    pass
weibull_min_c = Weibull()
weibull_min_c.name = "weibull_min_c"      # TODO : move to c++
weibull_min_c.scipy_name = "weibull_min"  # TODO : move to c++
weibull_min_c.numargs = 1


#------- Re-implement most method for genextreme
class Genextreme(_Statistics.Genextreme, DistGenCpp) :
    pass
geneextreme_c = Genextreme()
geneextreme_c.name = "genexteme_c"    # TODO : move to c++
geneextreme_c.scipy_name = "geneextreme"  # TODO : move to c++


class Gengamma(_Statistics.Gengamma, DistGenCpp) :
    pass
gengamma_c = Gengamma()
#-------  Gengamma patch scipy with c++ pdf and cdf:
from scipy.stats._continuous_distns import gengamma_gen
class gengamma_gen_patched(gengamma_gen) :
    def _pdf(self, *args, **kwargs) :
        return gengamma_c._pdf(*args, **kwargs)
    def _logpdf(self, *args, **kwargs) :
        return gengamma_c._logpdf(*args, **kwargs)
gengamma_patched = gengamma_gen_patched()
gengamma_patched.name = "gengamma_patched"


#-------  Pearson3 patch scipy for pdf and nnlf
tmp = _Statistics.Pearson3()
from scipy.stats._continuous_distns import pearson3_gen
class pearson3_gen_patched(pearson3_gen) :
    def _pdf(self, *args, **kwargs) :
        return tmp._pdf( *args, **kwargs)

    def _logpdf(self, *args, **kwargs) :
        return tmp._logpdf( *args, **kwargs)


pearson3_patched = pearson3_gen_patched()
pearson3_patched.name = "pearson3_patched"
