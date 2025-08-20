import numba
import numpy as np
from Snoopy.Statistics import FrozenDistABC

@numba.jit( "float64( float64 , float64[:])"  ,nopython = True )
def pdf_s(x , l) :
    expo_ = 0
    for i in range(len(l)):
        expo_ += l[i] * x ** (2*i)
    return np.exp( -1*expo_  )

@numba.jit( "float64[:]( float64[:] , float64[:])"  ,nopython = True )
def pdf_v(x , l) :
    expo_ = np.zeros( (len( x ))  )
    for i in range(len(l)):
        expo_ += l[i] * x ** (2*i)
    return np.exp( -1*expo_  )

def pdf(x , l) :
    if not hasattr(x, '__len__') :
        return pdf_s(x , l)
    else :
        return pdf_v(x , l)

def cdf(x , l) :
    """
    """
    from scipy.integrate import quad
    return quad( lambda x : pdf_s(x , l) , -np.inf , x )[0]


class MaxEntropyDistribution( FrozenDistABC ):
    name = "Exponential"
    def __init__(self, coef) :
        self.coef = coef

    def pdf(self , x) :
        return pdf(x , self.coef)

    def cdf(self , x) :
        return cdf(x , self.coef)
