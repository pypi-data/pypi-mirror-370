from scipy.stats import beta
import warnings
import numpy as np


def probN( n, variant = (0.0, 0.0), alphap = None, betap = None):
    """Return exceedance probability of the ranked data.

    (inverse of scipy.stats.mstats.mquantiles)


    Parameters
    ----------
    n : int
        Size of the data vector

    variant : float, tuple or str. 
        Variant for plotting positions parameter. The default is i / (n+1). 

    Returns
    -------
    np.ndarray
        Exceedance probability of the ranked data.



    Note
    ----
    If variant is a tuple (alphap , betap):
    
        Typical values of (alphap,betap) are:
            - (0,1)    : ``p(k) = k/n`` : linear interpolation of cdf
              (**R** type 4)
            - (.5,.5)  : ``p(k) = (k - 1/2.)/n`` : piecewise linear function
              (**R** type 5)
            - (0,0)    : ``p(k) = k/(n+1)`` :
              (**R** type 6)
            - (1,1)    : ``p(k) = (k-1)/(n-1)``: p(k) = mode[F(x[k])].
              (**R** type 7, **R** default)
            - (1/3,1/3): ``p(k) = (k-1/3)/(n+1/3)``: Then p(k) ~ median[F(x[k])].
              The resulting quantile estimates are approximately median-unbiased
              regardless of the distribution of x.
              (**R** type 8)
            - (3/8,3/8): ``p(k) = (k-3/8)/(n+1/4)``: Blom.
              The resulting quantile estimates are approximately unbiased
              if x is normally distributed
              (**R** type 9)
            - (.4,.4)  : approximately quantile unbiased (Cunnane)
            - (.35,.35): APL, used with PWM
            
    if variant is a float: 
            p = (i+(a-1)/2) / (N+a)        
    

    """
    if alphap is not None and betap is not None : 
        warnings.warn("alphap and betap argument are deprecated, please use 'variant = (alphap , betap)' instead", DeprecationWarning, stacklevel=2)
        variant = (alphap , betap)
        
    k = np.arange(1, n+1 , 1)    
    
    if isinstance( variant , tuple ) or isinstance( variant , list ) : 
        alphap , betap = variant        
        return 1 - (k - alphap)/(n + 1 - alphap - betap)
    
    elif isinstance( variant, float) :
        return 1 - ( (k + 0.5*(variant-1) ) / (n + variant)  )
   
    elif variant == "median" : 
        b = beta( k , n - k + 1 )
        return 1 - b.median()
    
    else : 
        raise( "Unknown variant : {variant:}" )
        


        
def probN_ci( n, alpha = 0.05, method = "beta" ):
    """Compute confidence interval for the empirical distribution.
    
    Parameters
    ----------
    n : int
        Number of samples
    alpha : float, optional
        1 - Size of the confidence interval. The default is 0.05.
    method : TYPE, optional
        DESCRIPTION. The default is "n".

    Returns
    -------
    ci_l : np.ndarray
        Lower bound of the CI
    ci_u : np.ndarray
        Upper bound of the CI
    """
    m = np.arange( n, 0, -1 )
    ci_u = np.empty( (n) )
    ci_l = np.empty( (n) )
    if method[:4] == 'jeff':
        for i in range(n):
            ci_l[i], ci_u[i] = beta( m[i]  + 0.5 , 0.5 + n - m[i] ).ppf( [alpha/2 , 1-alpha/2] )  # Jeffrey
    elif method[:4] == 'beta':
        for i in range(n):
            ci_l[i] = beta( m[-i] , 1 + n - m[-i] ).ppf( alpha/2 )
            ci_u[i] = beta( m[-i] + 1 , n - m[-i] ).ppf( 1-alpha/2 )

    return ci_l, ci_u        