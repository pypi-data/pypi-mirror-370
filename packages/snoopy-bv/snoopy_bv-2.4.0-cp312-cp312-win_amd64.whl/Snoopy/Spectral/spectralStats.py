import numpy as np
from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
from Snoopy import Statistics as st
from Snoopy.Tools import deprecated, renamed_function

"""Spectral statistics

Gathers all routines for short-term statistics based on Rayleigh distribution.
"""


class SpectralStats(object) :
    """All kind of statistics for seakeeping, assuming Rayleigh distribution.

    Constructed from spectral moment m0 and m2.    .
    """

    def __init__(self, m0 , m2) :
        """Initialise SpectralStats.
        
        Parameters
        ----------
        m0 : float or np.ndarray
            Spectral moment of order zero.
        m2 : float or np.ndarray
            Spectral moment of order two.

        Attributes
        ----------
        Rtz : float or np.ndarray
            Up-crossing period (s)
        rayleigh : scipy.stats.rv_frozen
            Rayleigh distribution of maxima (single amplitude)
        m0 : float or np.ndarray
            Spectral moment of order zero.
        m2 : float or np.ndarray
            Spectral moment of order two.
        Rs : float or np.ndarray
            Significant response (range)

        Example
        -------
        >>> spec_stat = sp.SpectralStats( m0 = 1.0, m2 = 0.5 )
        >>> spec_stat.Rs, spec_stat.Rtz # Significant response (range) and mean-upcrossing period
        (4.004, 8.885765876316732)
        >>> spec_stat.rp_to_x( duration = 10800. ) # 3h return value
        3.769154309992481
        """
        self.m0 = m0
        self.m2 = m2
        self._basic()

    def _basic(self):
        #Rayleigh distribution
        self.rayleigh = st.rayleigh_c( self.m0**0.5 )

        #Mean up-crossing period
        self.Rtz = sp.RtzFromM0M2( self.m0,self.m2 )

        self.Rs = 4.004 * self.m0**0.5


    def __getitem__(self, val):
        """Return a slice of SpectralStats

        Parameters
        ----------
        val : slice
            The slice

        Returns
        -------
        SpectralSlice
            The subset

        Example
        -------
        >>> s = sp.SpectralStats(  np.array([1,2]) , np.array([1,2]) )
        >>> s.Rtz
        array([6.28318531, 6.28318531])
        >>> s[0].Rtz
        6.283185307179586
        """
        return self.__class__( self.m0.__getitem__(val) , self.m2.__getitem__(val) )


    def __str__(self ):

        s = f"""Significant amplitude : {self.getAs():.3g}
Up-crossing period : {self.Rtz:.3g}
3 hours values : {self.rp_to_x(10800):.3g}
"""
        return s

    def __imul__(self , scalar) :
        self.m0 = self.m0 * scalar**2
        self.m2 = self.m2 * scalar**2
        self._basic()
        return self

    def __mul__(self , scalar) :
        return SpectralStats( self.m0 * scalar**2, self.m2 * scalar**2 )

    __rmul__ = __mul__


    def __item__(self, slice) :

        return


    @property
    @deprecated(reason = ".rl has been renamed more explicitely : .rayleigh")
    def rl(self):
        return self.rayleigh

    @classmethod
    def FromRsRtz(cls , Rs , Rtz):
        """Compute significant range and mean upcrossing period.

        Parameters
        ----------
        Rs : float
            Significant response (double amplitude)
        Rtz : TYPE
            Mean up-crossing period
        """
        m0 = ( Rs / 4.004 )  ** 2
        m2 = ( 2*np.pi / Rtz )**2 * m0
        return cls( m0 , m2 )

    def getRs(self):
        """Compute significant range.

        Returns
        -------
        float
            Significant response (double amplitude)
        """

        return self.Rs

    def getAs(self):
        """Compute significant amplitude.

        Returns
        -------
        float
            Significant amplitude
        """
        return 2.002 * self.m0**0.5

    def x_to_rp(self, x, formulation = 1):
        """Compute return period of x

        Parameters
        ----------
        x : float
            Value

        formulation : int, default to 1.
            If forumation == 1, P(X_rp, RP) = 1/e., if formulation == 2,

        Returns
        -------
        Float
            Return period (in seconds)

        """
        if formulation == 1 :
            return -self.Rtz / np.log( self.rayleigh.cdf(x) )
        else:
            return self.Rtz / self.rayleigh.sf( x )


    def rp_to_x(self , duration, formulation = 1) :
        """Get response with RP = duration.

        Parameters
        ----------
        m0 : float
            Zero order spectral moment.
        m2 : float
            Second order spectral moment.
        duration : float
            Duration (in seconds).

        Returns
        -------
        float
            amplitude with return period = "duration"
        """

        if formulation == 1 :
            return ( -2*self.m0*np.log( 1-np.exp( -self.Rtz / duration ) ) )**0.5
        elif formulation == 2 :
            p = self.Rtz / duration
            return (2*self.m0*np.log(1/p))**0.5
        else :
            raise(ValueError())


    def nExceed(self, value , duration ):
        """Return expected number of exceedance in given duration.

        Parameters
        ----------
        value : float
            Amplitude.
        duration : float
            Duration (in seconds).

        Returns
        -------
        float
            Number of excedance per duration

        """
        return self.rayleigh.sf(value) * duration / self.Rtz


    def risk_to_x( self , risk, duration ):
        """Amplitude associated to a given risk over a given duration.

        Parameters
        ----------
        risk : float or array
            Risk (between 0. and 1.)
        duration : float
            duration, in seconds
        Returns
        -------
        float
            Amplitude
        """
        return sp.ampFromRisk( risk, duration , self.m0 , self.m2 )

    def p_to_x( self , p, duration ):
        """Amplitude associated to a given risk over a given duration.

        Parameters
        ----------
        p : float or array
            Non-exceedance probability (between 0. and 1.)
        duration : float
            duration, in seconds
        Returns
        -------
        float
            Amplitude
        """
        return sp.ampFromRisk( 1 - p, duration , self.m0 , self.m2 )


    def x_to_risk(self, value, duration):
        """Return the risk of exceeding "value" in the given duration

        Parameters
        ----------
        value : float
            Value for which exceedance probability is desired
        duration : float
            Duration in s.

        Returns
        -------
        float
           risk (exceedance probability)

        """
        return self.getShtMaxDistribution(duration).sf(value)


    def x_to_p(self, value, duration):
        """Return the non-exceedance probability of "value" in the given duration

        Parameters
        ----------
        value : float
            Value for which exceedance probability is desired
        duration : float
            Duration in s.

        Returns
        -------
        float
           risk (exceedance probability)

        """
        return self.getShtMaxDistribution(duration).cdf(value)




    def stdMaxAmplitude(self , duration):
        """Return the standard deviation of the maximum on duration.
        
        The expression is asymptotic (duration >> RTz)

        Parameters
        ----------
        duration : float
            Sea-state duration, in seconds.

        Returns
        -------
        float
            Standard deviation of the maximum on duration.
        """
        return 0.5 * np.pi *  np.sqrt( self.m0 / (3*np.log( duration / self.Rtz )))




    def meanMaxAmplitude( self , duration ):
        """Mean maximum on duration.
        
        The expression is asymptotic (duration >> RTz)

        Parameters
        ----------
        duration : float
            Sea-state duration, in seconds.

        Returns
        -------
        float
            Mean maximum on duration.
        """
        n = duration / self.Rtz
        return (  ( 2*np.log(n))**0.5 + np.euler_gamma / (2*np.log(n))**0.5 ) * self.m0**0.5



    def getShtMaxDistribution( self , duration ) :
        """Return the distribution of the maximum on duration  ( Rayleigh**n ).

        Parameters
        ----------
        duration : float
            Duration of the seastate

        Returns
        -------
        rv_frozen
            Distribution of the duration maxima. (has .pdf, .cdf, .isf ...)

        """
        n = duration / self.Rtz

        return st.Powern( self.rayleigh, n )



    def iHsRatio( self, targetAmp, probIDSS ) :
        """Return the  increased Hs so that the target value probability is probIDSS.

        Parameters
        ----------
        targetAmp
            Amplitude to target
        probIDSS
            Probability of the target amplitude on the Increased Design Sea-State

        Returns
        -------
            Increased Design Sea-State, ratio iHs/Hs
        """
        return idss_hs_ratio( self.m0, targetAmp, probIDSS )


    def sample_each_seastate(self, duration, seed = None) :
        """Sample randomly maximum reponse on sea-state(s)

        Parameters
        ----------
        duration : float
            Sea-state duration

        seed : int
            Seed for random number generator. Default to None (random seed).

        Returns
        -------
        float or array-like
            Sample on each m0/m2 case

        """
        if isinstance( self.Rtz , float) :
            return self.getShtMaxDistribution( duration ).ppf( np.random.default_rng(seed).random(size = 1)[0] )
        else :
            return self.getShtMaxDistribution( duration ).ppf( np.random.default_rng(seed).random( self.Rtz.shape ) )


    def plot_rp(self, ax = None , rp_range = None, formulation = 1, **kwargs):
        """Plot return value agains return period.

        Parameters
        ----------
        ax : plt.Axis, optional
            Where to plot. The default is None.
        rp_range : np.ndarray, optional
            Return period range. The default is None.
        **kwargs : any.
            Keywords argument passed to ax.plot().

        Returns
        -------
        ax : plt.Axis
            The plot
        """

        if ax is None : 
            fig, ax = plt.subplots()

        if rp_range is None : 
            rp_range = np.logspace( 0 , 4, 100)
            
        ax.plot( rp_range, self.rp_to_x( rp_range, formulation = formulation ) , **kwargs )
        ax.set_xscale( "log" )
        return ax

# Compatibility
SpectralStats.ampFromRperiod = renamed_function( SpectralStats.rp_to_x, "ampFromRperiod" )
SpectralStats.riskFromAmp = renamed_function( SpectralStats.x_to_risk, "riskFromAmp")
SpectralStats.ampFromRisk = renamed_function( SpectralStats.risk_to_x, "ampFromRisk" )



@deprecated
def ampFromRperiod( duration, m0, m2 ):
    """Get response with RP = duration.

    Parameters
    ----------
    m0 : float
        Zero order spectral moment.
    m2 : float
        Second order spectral moment.
    duration : float
        Duration (in seconds).

    Returns
    -------
    float
        amplitude with return period = "duration"
    """
    Rtz = sp.RtzFromM0M2(m0 , m2)
    p = Rtz / duration
    return (2*m0*np.log(1/p))**0.5




def nExceed(value , duration , m0, m2) :
    """

    Parameters
    ----------
    value  : float
        Value to be exceeded (single amplitude).
    duration : float
        Duration (in seconds).
    m0 : float
        Zero order spectral moment.
    m2 : float
        Second order spectral moment.

    Returns
    -------
    float
        Number of exceedance expected in duration

    """
    _, Rtz = sp.RsRtzFromM0M2(m0 , m2)
    p = st.rayleigh_c( m0**0.5 ).sf(value)
    return p * duration / Rtz



def RsFromM0(m0):
    """
    Copy of RsFromM0(m0) function from SpectralSht_m.f90

    Significant response (double amplitude)
    """
    return 4.004 * m0**0.5

def AsFromM0(m0):
    """
    Copy of AsFromM0(m0) function from SpectralSht_m.f90

    Significant amplitude (double amplitude)
    """
    return 2.002 * m0**0.5



def RtzFromM0M2(m0, m2):
    """
    Now in cpp

    Copy of AsFromM0(m0) function from SpectralSht_m.f90

    Mean upcrossing-period
    """
    with np.errstate(divide='ignore'): # Ignore 0. / 0. which can easily arise (for instance, roll in head-seas).
        rtz = 2 * np.pi * (m0/m2)**0.5
    return rtz


@deprecated
def ampFromRisk_py( risk, duration, m0, m2 ):
    """ Now in cpp

    Parameters
    ----------
    risk : float
        Exceedance probability.
    duration : float
        Seastate duration (seconds).
    m0 : float
        Zero order spectral moment.
    m2 : float
        Second order spectral moment.

    Returns
    -------
    ampFromRisk : float
        Response value.

    """

    _, Rtz = sp.RsRtzFromM0M2(m0 , m2)
    n = duration / Rtz
    ampFromRisk = ( 2.*m0 * np.log( -1. / ( (1-risk)**(1./n) - 1 ) ) )**0.5
    return ampFromRisk


def msi_from_motion( ss , rao_motion , t) :
    """Compute MSI from seastate and RAO.

    According to McCauley and al. (1976).

    Parameters
    ----------
    ss : sp.SeaState
        SeaState on which the MSI index is tp be evaluated
    rao_motion : sp.Rao
        Vertical motion rao
    t : float
        Time (minutes)

    Returns
    -------
    MSI index

    """
    # TODO check that RAO is motion
    rao_vel = rao_motion.getDerivate( n = 1)
    rSpec = sp.ResponseSpectrum( ss , rao_vel )
    m2 , m4 = rSpec.getM0M2()

    return msi(  m2 , m4 , t  )



def msi(m2_mvt, m4_mvt, t):
    """Compute Motion Sickness Incidence (MSI) according to McCauley and al. (1976).

    Parameters
    ----------
    m2_mvt : float
        Spectral moment of order 2 of vertical motion. (= m0 of velocity)
    m4_mvt : float
        Spectral moment of order 4 of vertical motion. (= m2 of velocity = m0 of acceleration)
    t : float
        t is the time of exposure in minutes

    Returns
    -------
    msi_value : float
        MSI index
    """

    a = 0.798*np.sqrt(m4_mvt) / 9.81
    f = ( 1 / (2 * np.pi) ) * np.sqrt(m4_mvt / m2_mvt)  # Frequency calculated from velocity.
    return msi_McCauley( a , f , t )

def msi_McCauley( acc_rms_g , f, t ):
    """


    Parameters
    ----------
    acc_rms_g : float
        Acceleration (RMS, g)
    f : float
        Wave frequency
    t : float
        Exposure duration (Minutes)

    Returns
    -------
    msi_value : float
        MSI index.

    """
    from scipy import special

    sigma_a = 0.47
    sigma_t = 0.76

    rho = -0.75
    mu_t = 1.46
    mu_a = 0.87 + 4.36*np.log10(f) + 2.73*(np.log10(f))**2

    z_a  = (np.log10(acc_rms_g) - mu_a)/sigma_a
    z_t  = (np.log10(t) - mu_t)/sigma_t
    z_t1 = (z_t - rho*z_a)/np.sqrt(1 - rho**2)

    phi_za  = 0.5*(1 + special.erf(z_a/np.sqrt(2)))
    phi_zt1 = 0.5*(1 + special.erf(z_t1/np.sqrt(2)))

    msi_value = 100*phi_za*phi_zt1

    return msi_value




def mii( seastate, rao_aroll, rao_accy, rao_aheave, duration , check_unit = True ):
    """Return MII criterion (Defined in BV NR-483)


    Parameters
    ----------
    seastate : sp.SeaState
        Seastate considered
    rao_aroll : sp.Rao
        Roll acceleration (in rad/s/s)
    rao_accy : sp.Rao
        Transverse acceleration (including g*theta , "ACCY" keyword in HydroStar)
    rao_heave : sp.Rao
        Heave transfer function
    check_unit : bool
        Check that roll is not in degree (if roll > 1.0 ==> raise exception). Default to True

    Returns
    -------
    MII : float
        exceedances over the considered duration
    """

    if check_unit:
        # TODO : Check that aroll is not crazy (i.e. in degree)
        pass

    # Value specified by BV NR-483. Not meant to be modified (Would be nice to find the original reference).
    h = 1.20
    b = 1.20 * 0.25

    GLFEp = (1/3) * h * rao_aroll - rao_accy - (b/h) * rao_aheave
    GLFEs = (1/3) * h * rao_aroll - rao_accy + (b/h) * rao_aheave

    stat_p = sp.ResponseSpectrum(seastate, GLFEp).getSpectralStats()
    stat_s = sp.ResponseSpectrum(seastate, GLFEs).getSpectralStats()

    a = ( b / h ) * 9.81

    mii_p = stat_p.nExceed(a, duration)
    mii_s = stat_s.nExceed(a, duration)

    return mii_p + mii_s



"""
Routines related to increased design sea-states
"""
def idss_hs_ratio(  m0 , targetAmp, probIDSS ):
    """Return Increased Hs / Hs ratio

    Parameters
    ----------
    m0 : float
        Zero order moment on the original sea-state
    targetAmp : float
        Target value
    probIDSS : float
        Probability of targetAmp on increased design sea-state

    Returns
    -------
    Hs ratio : float
        Ratio iHs / hs, required to have P(targetAmp) = probIDSS on increased design sea-state

    """
    return np.sqrt(- (targetAmp)**2 / ( 2 * m0 * np.log(probIDSS)) )


def idss_convert_rp( rp , rtz, hs, new_hs ):
    """Convert return period on increased sea-state

    Parameters
    ----------
    rp : float
        return period on hs.
    rtz : float
        response mean up-crossing period
    hs : float
        Significant wave height
    new_hs : float
        Significant wave height on the increased sea-state

    Returns
    -------
    float
        Return period on increased sea-state.


    Example
    -------
    >>> rtz = 1.0
    >>> hs_1 = 1.0
    >>> rp_1 = 10800
    >>> hs_2 = 1.1
    >>> rp_2 = convert_rp( rp_1 , rtz , hs_1 , hs_2 )
    >>> x_1 = st.ReturnLevel.rp_to_x_distribution( sp.Jonswap( hs_1 , rtz , 1.0).getLinearCrestDistribution(), rtz , rp_1 )
    >>> x_2 = st.ReturnLevel.rp_to_x_distribution( sp.Jonswap( hs_2 , rtz , 1.0).getLinearCrestDistribution(), rtz , rp_2 )

    x_1 and x_2 will have, by construction, the same return period
    """
    return -rtz / np.log(  1 - (1-np.exp( -rtz / rp ))**(hs/new_hs)**2  )


if __name__ =="__main__":


    rs, rtz = 1, 10
    m0, m2 = sp.m0m2FromRsRtz(rs, rtz)
    stats = SpectralStats( m0 , m2 )
    statsVect = SpectralStats( np.array([m0, m0]) , np.array([m2, m2]) )
    statsVect.nExceed(  statsVect.rp_to_x(  10800 ) , 10800)

    samples = statsVect.sample_each_seastate( 3600 )

    # print (statsVect)
    stats.meanMaxAmplitude(10800)

    from matplotlib import pyplot as plt
    p = np.linspace(0.01,0.99,100)
    fig, ax = plt.subplots()
    ax.plot(  stats.risk_to_x( p, duration = 10800 ) , p )
    ax.set_yscale( "log" )

    statsVect.getShtMaxDistribution(10800).isf( 0.1 )

    np.std(stats.getShtMaxDistribution(1e4).rvs(100000)) / stats.stdMaxAmplitude(1e4)
    
    np.mean(stats.getShtMaxDistribution(1e4).rvs(100000)) / stats.meanMaxAmplitude(1e4)
