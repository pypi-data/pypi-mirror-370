import numpy as np
import pandas as pd
from Snoopy import logger
from . import _xmax_log



def nnlf(dist, theta, x, penaltyCoef ):
    """Negative log-likelyhood.

    Parameters
    ----------
    dist : scipy.stats.rv_continous
        Distribution model
    theta : List[float] 
        Distribution parameters.
    x : array like
        Data sample
    penaltyCoef : float
        Penalty coefficient for log-likelyhood (when value is not supported by the distribution). Significantly helps with MLE. 
        Base penalty is maximum possible value with double.
        scipy default behavior corresponds to penaltyCoef=1
        
    Returns
    -------
    float
        Negative log likelyhood
    """
    if penaltyCoef is None :
        return -np.sum(dist.logpdf(x,*theta))
    else :
        # if np.isnan(theta).any() :
        #     return np.inf
        logpdf = dist.logpdf(x,*theta)
        id_ok = np.where( np.isfinite( logpdf ) )
        n_bad = len(x) - len( id_ok[0] )
        return -np.sum(logpdf[ id_ok ]) + n_bad * penaltyCoef * _xmax_log

class DistGen(object):
    """Distribution Generator

       Aim is to provide a class compatible (duck typing) with scipy.stats.rv_continous.

    """

    def fit_loc_scale( self , sample , *args  ):
        """Estimate loc and scale based on data mean and variance, for given shape (*args)
        (kind of moment method)

        Use as starting value for fit

        Same as scipy
        """

        loc0, scale0 = 0. , 1.
        mu =  self.mean( *args, loc = loc0, scale = scale0 )
        mu2 = self.var( *args, loc = loc0, scale = scale0 )

        muhat = sample.mean()
        mu2hat  = sample.var()

        Shat = np.sqrt(mu2hat / mu2)
        Lhat = muhat - Shat*mu
        if not np.isfinite(Lhat):
            Lhat = 0
        if not (np.isfinite(Shat) and (0 < Shat)):
            Shat = 1
        return Lhat, Shat

    def sf(self, x, *args, **kwargs):
        return 1. - self.cdf(x, *args, **kwargs)

    def isf(self, p, *args, **kwargs):
        return self.ppf(1. - p, *args, **kwargs)

    def fit(self, sample, *args, **kwargs):
        from Pluto.statistics.fit_mle_fun import fit_mle_gen
        return fit_mle_gen(self, sample, *args, **kwargs)

    def fit_moment(self, sample, *args, **kwargs):
        from Pluto.statistics.fit_moment_fun import fit_moment
        return fit_moment(self, sample, *args, **kwargs)

    def nnlf(self, theta, x, penaltyCoef=1):
        """Negative log-likelyhood.

        Parameters
        ----------
        theta : list
            Distribution parameters.
        x : array like
            Data sample

        Returns
        -------
        float
            Negative log likelyhood
        """
        return nnlf( self, theta , x , penaltyCoef )


    def nnlf_bins( self , theta , edges, count, penaltyCoef = None  ):
        """Negative log-likelyhood.

        Parameters
        ----------
        theta : list
            Distribution parameters.
        edges : array like
            Bin edges
        count : array like
            Count in each bins

        Returns
        -------
        float
            Negative log likelyhood
        """
        from Pluto.statistics import nnlf_bins # Move to binned_basics to Snoopy ?
        return nnlf_bins( self , theta, edges, count, penaltyCoef = penaltyCoef )



    def stats(self, *args, moments = "mv", **kwargs ):
        r = []
        for m in moments :
            if m == "m" :
                r.append( self.mean(*args, **kwargs) )
            elif m == "v":
                r.append( self.std(*args, **kwargs)**2 )
            elif m == "s":
                r.append( self.skewness(*args, **kwargs) )
            elif m == "k":
                r.append( self.kurtosis(*args, **kwargs) )

        if len(moments) == 1 :
            return r[0]
        return r




    def skewness(self, *args, **kwargs) :
        from statsmodels.stats.moment_helpers import mnc2mc
        u1, u2, u3 = mnc2mc( [ self.moment(i, *args, **kwargs) for i in [1,2,3]])
        return u3 / u2**(3./2.)

    def kurtosis(self, *args, **kwargs) :
        from statsmodels.stats.moment_helpers import mnc2mc
        u1, u2, u3, u4 = mnc2mc( [ self.moment(i, *args, **kwargs) for i in [1,2,3,4]] )
        return u4 / u2**2 - 3

    def central_moment(self, n, *args, **kwargs):
        from statsmodels.stats.moment_helpers import mnc2mc
        return mnc2mc( [ self.moment(i, *args, **kwargs) for i in [1,2,3,4]] ) [n-1]


    def _penalized_nnlf(self , theta, x) : # Same API as scipy
        logpdf = self.logpdf(x,*theta)
        id_ok = np.where( np.isfinite( logpdf ) )
        n_bad = len(x) - len( id_ok[0] )
        return -np.sum(logpdf[ id_ok ]) + n_bad * _xmax_log

    def __call__(self, *coefs):
        return FrozenDist(self, *coefs)

class FrozenDistABC(object):

    # Should be overloaded
    def pdf(self, x):
        raise(NotImplementedError)

    def cdf(self, x):
        raise(NotImplementedError)

    def cdf_numeric(self, x):
        """Compute cdf by numerical integration of the pdf
        """
        from scipy.integrate import quad
        return quad( self.pdf, -np.inf, x  )[0]


    def sf(self, x):
        return 1. - self.cdf(x)

    def ppf(self, p):
        """
           If not overloaded, solve sf(x) = p  numerically
        """
        from scipy.optimize import root_scalar
        if not isinstance(p, np.ndarray) :
            res = root_scalar(lambda x: self.cdf(x) - p, x0=5.0, fprime=lambda x: self.pdf(x) - 1, method = "newton")
            if not res.converged :
                res = root_scalar(lambda x: self.cdf(x) - p, x0=5.0, fprime=lambda x: self.pdf(x) - 1, method = "brentq", bracket = [0 , 100])
                if not res.converged :
                    logger.warning("ppf not converged with brent or Newton")
            return res.root
        else :
            res = np.array( [ self.ppf( x ) for x in p ] )
        return res

    def isf(self, p):
        return self.ppf(1. - p)

    def bic(self, x, nDof = None):
        if nDof is None :
            nDof = self.dist.nDof

        return np.log(len(x)) * nDof + 2. * self.nnlf(x)

    def logpdf(self, x):
        return np.log(self.pdf(x))


    def rvs(self, size):
        r = np.random.rand(size)
        return self.isf(r)




class FrozenDist(FrozenDistABC):
    """
       Same as dist, but coefficient are "embedded"
    """

    def __init__(self, dist, *coefs):
        self.dist = dist
        self.args = coefs

    def argsSe(self):
        return pd.Series(  index = self.dist.paramsName, data = self.args )

    def __str__(self):
        return self.dist.name + " " + " ".join("{:.3f}".format(i) for i in self.args)

    def pdf(self, x):
        return self.dist.pdf(x, *self.args)

    def logpdf(self, x):
        return self.dist.logpdf(x, *self.args)

    def cdf(self, x):
        return self.dist.cdf(x, *self.args)

    def ppf(self, p):
        if hasattr(self.dist, "ppf"):
            return self.dist.ppf(p, *self.args)
        else :
            return FrozenDistABC.ppf( self, p)

    def stats(self, moments = "mv") :
        return self.dist.stats(*self.args, moments = moments)

    def isf(self, p):
        return self.ppf(1.-p)

    def moment(self, n):
        return self.dist.moment(n, *self.args)

    def central_moment(self, n):
        return self.dist.central_moment(n, *self.args)

    def mean(self) :
        return self.dist.mean(*self.args)

    def std(self) :
        return self.dist.std(*self.args)

    def skewness(self) :
        return self.dist.skewness(*self.args)

    def kurtosis(self) :
        return self.dist.kurtosis(*self.args)

    def sf(self, p):
        return self.dist.sf(p, *self.args)

    def nnlf(self, x, penaltyCoef = 1):
        return self.dist.nnlf(self.args, x, penaltyCoef=penaltyCoef)

    @property
    def nDof(self):
        return self.dist.nDof