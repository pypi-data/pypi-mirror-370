"""Distributions making used of JIT and parallelisation
"""

import numba as nb
import numpy as np
from scipy.stats._continuous_distns import weibull_min_gen

@nb.vectorize( [ nb.float64(nb.float64, nb.float64) ] , nopython = True , target = "parallel", fastmath=True)
def _weibull_min_pdf(x, c) :
    if x > 0 and c > 0:
        return c * x**(c - 1) * np.exp( -x**c)
    else :
        return 0.0

@nb.vectorize( [ nb.float64(nb.float64, nb.float64) ] , nopython = True , target = "parallel", fastmath=True)
def _weibull_min_logpdf(x, c) :
    if x > 0 and c > 0:
        return np.log(c) + (c - 1)*np.log(x) - x**c
    else :
        return -np.inf

class weibull_min_p_gen(weibull_min_gen) :
    def _pdf(self, x, c) :
        return _weibull_min_pdf(x, c)

    def _logpdf(self, x, c) :
        return _weibull_min_logpdf(x, c)


weibull_min_p = weibull_min_p_gen()
weibull_min_p.name = "weibull_min"