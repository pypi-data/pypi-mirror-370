import numpy as np
from scipy.integrate import dblquad, simpson
from Snoopy.Statistics import Rayleigh_n

def longTerm_spectral_rba( RsTz_pdf, x, duration, dss = 10800 ,rs_min=0.0 , rs_max = np.inf, tz_min=2., tz_max = 50. , n = "auto" ):
    """
    Parameters
    ----------
    RsTz_pdf : callable
        joint probablilty density function of significant response and up-crossing period.
    x : float
        Value for which the cdf is to be calculated
        
    duration : float
        Duration on which the probability of non-exeedance is calculated. In years
        
    dss : flaot, optional
        Sea-state duration. The default is 10800.
        
    n : int, , optional
       number of integration point.  The default is "auto"
       if auto, automatic step is used (dblquad)
       
    Returns
    -------
    cdf
    """

    duration_s = duration * 365.24 * 24 * 3600
    
    if n == "auto" :
        def integrand( rs, tz ) :
            sht_dist = Rayleigh_n( int(dss / tz ) )( rs / 4.0 )
            return RsTz_pdf(rs, tz) * (1-sht_dist.cdf(x))
        res = dblquad( integrand, tz_min , tz_max, rs_min, rs_max  )
        return 1-res[0]

    else : 
        Rs_int = np.linspace( rs_min, rs_max , n )
        Tz_int = np.linspace( tz_min, tz_max , n )
        int_Rs = np.empty( Tz_int.shape , dtype = float )
        for itz in range(n):
            sht_dist = Rayleigh_n( int(dss / Tz_int[itz] ) )  ( Rs_int / 4.0 )
            int_Rs[itz] = simpson( RsTz_pdf(  Rs_int , Tz_int[itz] ) * ( 1 - sht_dist.cdf(x)) , x=Rs_int )
        tot = simpson( int_Rs , x=Tz_int )
        
        
        return (1. - tot) ** ( duration_s / dss )
    
    
def longTerm_spectral_rba_contrib( RsTz_pdf, x, dss = 10800 , rs_min=0.0 , rs_max = np.inf, tz_min=2., tz_max = 50. , n = 100 ):
    
    import pandas as pd
    Rs_int = np.linspace( rs_min, rs_max , n )
    Tz_int = np.linspace( tz_min, tz_max , n )

    df = pd.DataFrame( index = pd.Index(  Rs_int, name = "Rs" ) , 
                       columns = pd.Index( Tz_int , name = "RTz" ), dtype = float)

    for itz in range(n):
        sht_dist = Rayleigh_n( int(dss / Tz_int[itz] ) )  ( df.index.values / 4.0 )
        df.iloc[ : , itz ] = RsTz_pdf(  Rs_int , Tz_int[itz] ) * (1-sht_dist.cdf(x)) 
        
    return df
    
    
    
    
def longTerm_spectral_rba_inv( RsTz_pdf, p, duration, dss = 10800 ,
                               rs_min=0.0 , rs_max = np.inf,
                               tz_min=1.  , tz_max = 50. ,
                               lower_bound = 0, upper_bound = 1e10,
                               n = "auto" ) :
    """
    Parameters
    ----------
    RsTz_pdf : callable
        joint probablilty density function of significant response and up-crossing period.
        
    p : float
    
    duration : float
        Duration on which the probability of non-exeedance is calculated. In years    
        
    dss : flaot, optional
        Sea-state duration. The default is 10800.
        
    n : int, , optional
       number of integration point.  The default is "auto"
       if auto, automatic step is used (dblquad)
       
    Returns
    -------
    x
    """

    from scipy.optimize import root_scalar
    year_to_sec = 3600 * 24 * 365.24
    duration_s = duration * year_to_sec
    res = root_scalar( lambda x  : longTerm_spectral_rba(  RsTz_pdf, x, dss/year_to_sec, dss , rs_min, rs_max, tz_min, tz_max , n ) - p**(dss / duration_s)  , 
                       method = "brentq",
                       bracket = [ lower_bound , upper_bound  ]
               )
    return res.root
                
    
    
    
    
    