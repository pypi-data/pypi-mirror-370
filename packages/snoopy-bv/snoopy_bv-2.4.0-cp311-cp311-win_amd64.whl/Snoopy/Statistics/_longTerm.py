"""Routines for long term calculations. Formulas can be found in NI 638 Section 4.3.1

    - LongTermGen class is for general short-term / long-term convolution

       -> LongTerm class is when short-term distribution is calculated using "cycle" distribution ( P_sht = P_cycle**(dss/RTz) ).

          -> LongTermSpectal class is when cycle distribution is Rayleigh


In longTerm and longTermSpectral, several formulations are available. Waves can be considered all independent, or only independent within a sea-state.
"""

import types

import _Statistics
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import root_scalar
from Snoopy import Statistics as st
from Snoopy import logger


class LongTermGen( object ) :
    """Long-term / short-term mix, using directly P_sht(x, dss), which is the probability of exceeding X on a given sea-state over a duration dss.
    """

    def __init__(self , p_sht, probabilityList, dss ):
        """Convolution between short-term distribution and sea-state probability.

        Parameters
        ----------
        p_sht : function, scipy.stats.rv_frozen or list.
            Short-term distribution. Vectorized function, or list of function.
            Can also be given as scipy.rv_frozen of list of scipy.rv_frozen.
        probabilityList : np.ndarray
            Probability of each sea-states
        """
        self.p_sht = p_sht
        self.probabilityList = probabilityList
        self.dss = dss

        # Can be below 1 (The response is considered to be 0 on the missing sea-states)
        if (f := self.probabilityList.sum()) > 1.0 + 1e-10 :
            raise(Exception( f"Sum of probabilityList must be lower than 1.0 {f:}" ))


    def shtProb(self , x):
        """Return short-term probability of x on all sea-state.

        This is used to handle the possibles inputs for p_sht:
            - vector of scalar function
            - vectorized function.
            - vector of stats.rv_frozen
            - vectorized stats.rv_frozen

        Parameters
        ----------
        x : float
            Value

        Returns
        -------
        np.ndarray
            Probability on each sea-state
        """
        if hasattr( self.p_sht , "__iter__" ) :
            if len(self.p_sht) != len(self.probabilityList):
                raise(Exception( "p_sht and probabilityList must have same length" ))
            if hasattr( self.p_sht[0] , "cdf" ):
                return np.array( [ d.cdf( x ) for d in self.p_sht ] )
            else:
                return np.array( [ d( x ) for d in self.p_sht ] )
        else :
            if isinstance(self.p_sht, (types.MethodType, types.FunctionType)):
                return self.p_sht( x )
            else :
                return self.p_sht.cdf( x )

    def x_to_p( self, x, duration ):
        """Return the non-exceedance probability of x in duration (year).

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        float
            cdf  (i.e.  P( x < X )  )
        """
        shtProb = self.shtProb(x)
        duration_s = duration * 365.24 * 24 * 3600
        return _longTermBaseGen( shtProb, self.probabilityList, x, duration_s, self.dss )


    def rp_to_x(self, rp, **kwargs):
        """Return value corresponding to return period "rp".

        Parameters
        ----------
        rp : float
            Return period, in year.

        Returns
        -------
        float
            Return value
        """
        return self.p_to_x( p = np.exp(-1), duration = rp, **kwargs)


    def x_to_rp(self, x):
        """Compute return period of given value.

        Parameters
        ----------
        x : float
            Value.

        Returns
        -------
        float
            Return period
        """
        # Output results should not depends on d_
        # d_ would simplified if equations where developed (not done to be independent on the longterm assumption used in subclass)
        d_ = 1.0
        p = self.x_to_p(x, d_)
        return d_ / -np.log(p)



    def p_to_x(self , p , duration, lower_bound = 0.0, upper_bound = 1e10, x0 = 1.0,  atol = 1e-10, rtol = 1e-12, method = "brentq", preconditioner = None) :
        """Convolution between short-term distribution and sea-state probability.

        Compute the value corresponding to the non-exceedance probability over a given duration.

        Parameters
        ----------
        p: float
            Probability  (cdf, i.e. non-exceedance probability)
        duration: float
            Long term duration (in year)

        Returns
        -------
        float
            Value corresponding to non-exceedance probability p  ( P(x < V) = p )
        """
        logger.debug("Solving for long term START")
        if preconditioner is None :
            def fun(x) :
                return self.x_to_p( x, duration) - p
        else :
            def fun(x) :
                return preconditioner(self.x_to_p( x, duration)) - preconditioner(p)

        try :
            res = root_scalar( fun,
                               bracket = [lower_bound, upper_bound],x0 = x0,
                               method = method,
                               xtol = atol , rtol = rtol)
        except ValueError as e:
            logger.error( f"({lower_bound:}) = {fun(lower_bound):}" )
            logger.error( f"({upper_bound:}) = {fun(upper_bound):}" )
            raise(e)

        logger.debug(f"Solving for long term done {res.function_calls:} STOP")
        return res.root



    def contribution(self , x) :
        """Compute and return contribution factor for each sea-state.

        Parameters
        ----------
        x : float
            Response level for which contribution coefficient are calculated

        Returns
        -------
        array
            Contribution coefficient for all sea-states
        """
        contrib = self.probabilityList * (1. - self.shtProb(x))
        contrib /= np.sum(contrib)
        return contrib


    def plot_rp(self, rp_range, ax=None, scale_y = 1.0, **kwargs):
        """Plot return value against return period.

        Parameters
        ----------
        rp_range : np.ndarray
            Response period range (in year)
            Only range and number of points are considered.

        ax : plt.Axesplt.Axes
            Where to plot

        Returns
        -------
        plt.Axes
            The plot
        """
        if ax is None : 
            fig, ax = plt.subplots()

        # Do not use self.rp_to_x to avoid numerical solving at each point. 
        x_min = self.rp_to_x( np.min(rp_range) )
        x_max = self.rp_to_x( np.max(rp_range) )
        x_range = np.linspace(x_min, x_max, len(rp_range) )

        ax.plot( [self.x_to_rp(x) for x in x_range], x_range * scale_y , **kwargs )
        
        ax.set_xscale("log")
        ax.set(xlabel = "Return period (Years)")
        return ax


    def slope(self, rp, d_rp = 0.1, **kwargs):
        """Compute the slope of the long-term distribution with respect to the log of RP (a.k.a. 'severity factor').

        Parameters
        ----------
        rp : float
            Return period
        d_rp : float, optional
            Step to calculate the slope, by default 0.1

        Returns
        -------
        Float
            The slope value
        """
        x1 = self.rp_to_x(rp, **kwargs)
        x2 = self.rp_to_x(rp + d_rp, **kwargs)
        return (x2-x1) / ( np.log(rp+d_rp) - np.log(rp)  )

def _longTermBaseGen( shtProb,  probabilityList, x, duration_s, dss ):
    if x < 1e-20 :
        return 0.0
    pe_ss = np.sum( probabilityList * (1 - (shtProb)))
    res = (1-pe_ss) ** (duration_s / dss)
    return res




class LongTerm(LongTermGen):
    def __init__( self, distributionList, rTzList, probabilityList, dss = "INDEP", engine = "cpp", numThreads = 1 ) :
        """Convolution between short-term distribution and sea-state probability, given cycle maxima distribution.

        Cycle in each sea-state is considered independant, so that

        .. math:: P_{sht} = P_{cycle}**{dss / Rtz}

        Compute the value corresponding to the non-exceedance probability over a given duration.

        Parameters
        ----------
        distributionList:  Array of distribution object (own a .cdf() function)
            Array of short-term disitribution.
        rTzList: np.array
            List of mean up-crossing periods.
        probabilityList: np.array
            List of sea-state probabilities (sum = 1)
        dss: float, optional
            Seastate duration. The default is "INDEP".
            "INDEP" -> Assuming all waves as independent  ( Formula (2.42) from StarSpec manual )
            float   -> Sea-State duration, waves come by sea-state (in seconds)
        """
        self.distributionList = distributionList
        self._initCommon(rTzList, probabilityList, dss = dss, engine = engine, numThreads=numThreads )


    def _initCommon(self, rTzList, probabilityList, dss = "INDEP" , engine = "python", numThreads = 1) :
        self.rTzList = rTzList
        if isinstance(probabilityList, str) :
            if probabilityList == "iso" :
                self.probabilityList = np.ones( (len(rTzList)), dtype = float ) / len(rTzList)
        else :
            self.probabilityList = probabilityList / probabilityList.sum()

        self.dss = dss
        self.numThreads = numThreads
        self.set_engine( engine )

        # optimization of long term computations
        if len(self.rTzList.shape)==1:
            self.probaOverRtz = self.probabilityList / self.rTzList
        else:
            self.probaOverRtz = self.probabilityList[:,None] / self.rTzList
        self._meanRtz = 1. / np.sum( self.probaOverRtz )

    def set_engine(self, engine):
        self._engine = engine
        if engine == "python" :
            self.lt_base = _longTermBase
        elif engine == "python_small_p" :
            self.lt_base = _longTermBase_small_p
        elif engine == "numba" :
            from numba import float64, jit
            self.lt_base = jit( float64(float64[:], float64[:] , float64[:], float64, float64, float64), nopython=True)(_longTermBase)
        elif engine == "cpp":
            self.lt_base = _Statistics.longTermBase
        elif engine == "cpp_p":
            self.lt_base = lambda *args , **kwargs : _Statistics.longTermBase_p(*args , **kwargs , numThreads = self.numThreads)
        else : 
            raise(Exception(f"Engine {engine:} not known"))

    @property
    def dss(self):
        return self._dss

    @dss.setter
    def dss(self, dss ):
        #Handle the convertion to float (for cpp functions)
        self._dss = dss
        if self._dss == "INDEP" : self._idss = -5.
        elif self._dss == "LARGE_T": self._idss = -15.
        else : self._idss = dss


    def cycleProb(self , x):
        """Return probability of x on all sea-state (in term of cycles).

        This is used to handle the possibles inputs for p_sht:
            - vector of scalar function
            - vectorized function.
            - vector of stats.rv_frozen
            - vectorized stats.rv_frozen
        """
        if hasattr( self.distributionList , "__iter__" ) :
            if hasattr( self.distributionList[0] , "cdf" ):
                return np.array( [ d.cdf( x ) for d in self.distributionList ] )
            else : # the cdf is directy provided
                return np.array( [ d( x ) for d in self.distributionList ] )
        else :
            if isinstance(self.distributionList, (types.MethodType, types.FunctionType)):
                return self.distributionList( x )
            else :
                return self.distributionList.cdf( x )


    def x_to_p( self, x, duration ):
        """Return the non-exceedance probability of x in duration.

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        float
            cdf (  P( x < X )  )
        """
        cycleProb = self.cycleProb(x)
        duration_s = duration * 365.24 * 24 * 3600
        return self.lt_base( cycleProb, self.rTzList, self.probabilityList, x, duration_s, self._idss )


    def x_to_pcycle(self , x, ncycle = None):
        """Return cycle probablity (Equivalent of "PROB" option in Starspec).

        Parameters
        ----------
        x : float
            Value

        Returns
        -------
        pcycle : float
            exceedance probability
        """
        n_exc = np.sum( self.probaOverRtz * ( 1 - self.cycleProb(x)) )
        if ncycle is None :
            n_cyc = 1. / self.meanRtz()

        if not np.isfinite(n_cyc) :
            raise(Exception("Response is zero on some sea-state; do no know how to count cycles. Try lt.correctZeros()."))
        return n_exc / n_cyc


    def x_to_pdf(self, x, eps):
        """Return cycle pdf.

        Parameters
        ----------
        x : float
            Value
        eps : float
            Value

        Returns
        -------
        pdf : float
            probability distribution function
        """
        dn_exc = np.sum( self.probaOverRtz * ( self.cycleProb((x+eps)/2) - self.cycleProb((x-eps)/2) ) )
        return 0.5 * self.meanRtz() * dn_exc / eps


    def meanRtz(self):
        """Return long-term mean up-crossing period.

        Considering all cycle independant, on a duration D, the number of cycle in D / meanRtz()

        Returns
        -------
        float
            Long-term mean up-crossing period
        """
        return self._meanRtz


    def pcycle_to_x(self , p , lower_bound = 0, upper_bound = 1e10, x0 = 1.0,
                           atol = 1e-10, rtol = 1e-12, method = "brentq", preconditioner = None) :
        """Return value with a given probability (in term of cycles exceedance).

        Parameters
        ----------
        pcycle : float
            Cycle exceedance probability

        Returns
        -------
        x : float
            Level with exceedance probability of pcycle
        """
        logger.debug("Solving for long term prob START")
        def fun(x) :
            return self.x_to_pcycle( x ) - p

        res = root_scalar( fun,
                           bracket = [lower_bound, upper_bound],x0 = x0,
                           method = method,
                           xtol = atol , rtol = rtol)
        logger.debug(f"Solving for long term prob done {res.function_calls:} STOP")
        return res.root


    def nExceed( self, x, duration ):
        """Return the number of exceedance on each sea-state over the given duration.

        Note
        ----
        This considers all cycles as independant. (i.e. not grouped per sea-state)

        Parameters
        ----------
        x : float
            Value
        duration : str
            Duration, in year

        Returns
        -------
        np.ndarrays
            The number of exceedance on each sea-state
        """
        duration_s = duration * 365.25 * 24 * 3600.
        n_cycle = duration_s * self.probaOverRtz
        return (1-self.cycleProb(x)) * n_cycle



    def plotMaxDistributionPdf(self , duration, ax = None, **kwargs):
        """Plot long-term maxima density probability.

        Parameters
        ----------
        duration : float
            Duration, in year
        ax : matplotlib axes object, optional
            An axes of the current figure, default None
        **kwargs : any
            Keywords argument passed to ax.plot()

        Returns
        -------
        ax : matplotlib axes object
            axes of the current figure.

        """
        range_ = np.linspace(  self.p_to_x(1e-3, duration) , self.p_to_x(1-1e-3, duration) , 50)
        if ax is None:
            fig, ax = plt.subplots()

        ax.plot( 0.5*(range_[:-1] + range_[1:]) , np.diff([ self.x_to_p(x, duration) for x in range_]), **kwargs  )
        return ax


    def contribution(self , x) :
        """Compute and return contribution factor for each sea-state.

        Parameters
        ----------
        x : float
            Response level for which contribution coefficient are calculated

        Returns
        -------
        array
            Contribution coefficient for all sea-states
        """
        if self._idss > 0.0 :
            contrib = self.probabilityList * (1. - (self.cycleProb(x))**( self.dss / self.rTzList))
        else :
            contrib = self.probaOverRtz * (1-self.cycleProb(x))

        contrib /= np.sum(contrib)
        return contrib


    def fatigue_damage(self, sn_curve, duration):
        """Return cumulative damage on the given duration.
        
        Short-term damage is integrated numerically on each sea state and .

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve
        duration : float
            Duration (years)

        Returns
        -------
        float
            Cumulated fatigue damage.
        """
        raise(NotImplementedError()) # seems ok, but not tested at all.

        dam = 0
        for i, pss in enumerate( self.probabilityList) : 
            dam += sn_curve.damage_from_distribution( stress_range_pdf = self.distributionList[i].pdf, nb_cycles = duration * pss * 365.24*24*3600. / self.rTzList[i] )
        return dam 
    
    def fatigue_life(self, sn_curve):
        """Return fatigue life, in years

        Parameters
        ----------
        sn_curve : SnCurve
            The sn-curve.

        Returns
        -------
        float
            The fatigue life, in year.
        """
        return 1 / self.fatigue_damage(sn_curve, duration = 1)
    

    def fatigue_life_mean_corr(self, sn_curve, ReEQ, s_mean, s_res0):
         """Return fatigue life, in years

         Parameters
         ----------
         sn_curve : SnCurve
             The sn-curve.

         Returns
         -------
         float
             The fatigue life, in year.
         """
         return 1 / self.fatigue_damage_num_mean_corr(sn_curve, ReEQ, s_mean, s_res0, duration = 1)


    def fatigue_life_num(self, sn_curve):
        """Return fatigue life, in years.

        Use numerical integration of the long-term distribution.

        Parameters
        ----------
        sn_curve : SnCurve
            The sn-curve.

        Returns
        -------
        float
            The fatigue life, in year.
        """
        return 1 / self.fatigue_damage_num(sn_curve, duration = 1)


    def fatigue_damage_num( self, sn_curve, duration ):
        """Return cumulative damage on the given duration.

        Damage is integrated numerically using the long-term disitribution of cycles. The implementation is very probabably not optimum in term of CPU cost.

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve
        duration : float
            Duration (years)

        Returns
        -------
        float
            Cumulated fatigue damage.
        """
        def stress_range_pdf(x):
            # Numerically get the pdf from the exceedance probability "x_to_pcycle"
            eps = 0.001
            return self.x_to_pdf(x, eps)

        return sn_curve.damage_from_distribution( stress_range_pdf = stress_range_pdf, nb_cycles = duration * 365.24*24*3600. / self.meanRtz() )


class LongTermSpectral( LongTerm ):

    def __init__( self, rsList, rTzList, probabilityList, dss = "INDEP", engine = "python", numThreads = 1 ) :
        """Compute the non-exceedance probability over a given duration.

        Parameters
        ----------
        rsList:  Array of Rs  (significant range (=4.004*m0**2))
            Array of Rs
        rTzList: np.array
            List of mean up-crossing periods.
        probabilityList: np.array
            List of sea-state probabilities
        dss: float, optional
            Seastate duration. The default is "INDEP".
            "INDEP" -> Assuming all waves as independent  ( Formula (2.42) from StarSpec manual )
            float   -> Sea-State duration, waves come by sea-state (in seconds)

        Example
        -------
        > lta = LongTermSpectral( rsList, rTzList, probabilityList )
        > design_value_at_25_year = lta.p_to_x(  p = 1/np.exp(1) , duration = 25  )
        """
        self._initCommon(rTzList, probabilityList, dss = dss, engine = engine, numThreads=numThreads )
        self.rsList = rsList

        # optimization of long term computations
        self.m0Squared = rsList/4.004


    def correctZeros(self, Rs_default = 1e-12, Rtz_default = 10.) :
        """Handle Rs = 0.0 cases, which trigger numerical issue.

        when Rs == 0.0, it is replaced by RsEps

        Parameters
        ----------
        Rs_default : TYPE
            DESCRIPTION.
        Rtz_default : TYPE
            DESCRIPTION.
        """
        self.m0Squared[ np.where( self.m0Squared == 0 ) ] = Rs_default
        self.rsList[ np.where( self.rsList == 0 ) ] = Rs_default
        self.rTzList[ np.where( self.rTzList == 0 ) ] = Rtz_default
        self._initCommon(self.rTzList, self.probabilityList, dss = self.dss, engine = self._engine, numThreads=self.numThreads )


    def cycleProb(self , x):
        return st.rayleigh_cdf( x  , self.m0Squared)

    def p_to_x(self ,*args, **kwargs) :
        # Better default parameter
        upper_bound = kwargs.pop( "upper_bound", 3*self.rsList.max() )
        if upper_bound < 1e-6:
            return 0.0
        return LongTerm.p_to_x(self , *args, upper_bound = upper_bound, **kwargs)


    def pcycle_to_x(self , *args, **kwargs):
        # Better default parameter
        upper_bound = kwargs.pop( "upper_bound", 3*self.rsList.max() )
        if upper_bound < 1e-6:
            return 0.0
        return LongTerm.pcycle_to_x(self , *args, upper_bound = upper_bound, **kwargs)


    def p_to_x_parallel(self, p , duration, tol = 1e-5, numThreads = None ):
        # Link to cpp function
        import _Statistics
        if numThreads is None :
            numThreads = self.numThreads
        duration_s = duration * 365.24 * 24 * 3600
        res = _Statistics.longTermSpectral_inv_p(  self.rsList, self.rTzList, self.probabilityList, p, duration_s, self._idss, tol = tol, numThreads = numThreads )
        return res

    def fatigue_damage(self, sn_curve, duration):
        """Return cumulative damage on the given duration.

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve
        duration : float
            Duration (years)

        Returns
        -------
        float
            Cumulated fatigue damage.
        """
        dam = 0
        
        for i, pss in enumerate( self.probabilityList) : 
            dam += sn_curve.damage_from_RSRTZ( self.rsList[i], self.rTzList[i], duration = duration * pss * 365.24*24*3600.)
        return dam



    def fatigue_damage_num_mean_corr( self, sn_curve, ReEQ, s_mean, s_res0, duration=1):
        """Return cumulative damage on the given duration.
        obtained with the direct calculation method from NI611, 4.1.5 for plated joints and 4.3.3 for cut edges

        Damage is integrated numerically using the long-term distribution of cycles. The implementation is very probabably not optimum in term of CPU cost.

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve
        ReEQ : float
            Yielding stress (MPa)
        s_mean : float
            mean stress for the loading condition considered (MPa)
        element_type : str
            "plated_joint" or "cut_edge" depending on the element considered
        duration : float
            Duration (years)

        Returns
        -------
        float
            Cumulated fatigue damage.
        """
        def stress_range_pdf(x):
            # Numerically get the pdf from the exceedance probability "x_to_pcycle"
            eps = 0.001
            return self.x_to_pdf(x, eps)

        s_waveHS = self.pcycle_to_x(0.0001, lower_bound=0, upper_bound=10000.0, x0=1.0, atol=1e-4, rtol=1e-6, method='brentq', preconditioner=None) # stress level at p=10^-4

        return sn_curve.damage_from_distribution_corr( stress_range_pdf = stress_range_pdf, nb_cycles = duration * 365.24*24*3600. / self.meanRtz(), ReEQ=ReEQ, s_mean=s_mean, s_res0 = s_res0,s_waveHS=s_waveHS )


def _longTermBase_small_p( shtProb, rTzList, probabilityList, x, duration_s, dss ):
    """
    """
    if dss > 0.0 : # Account for wave dependances in a given sea-state (with duration dss)
        if x < 1e-20 :
            return 0.0
        pe_ss = np.sum( probabilityList * shtProb**( dss / rTzList))
        return (pe_ss) ** (duration_s/dss)
    else:
        raise(NotImplementedError)


def _longTermBase( shtProb, rTzList, probabilityList, x, duration_s, dss ):
    """
    """
    if dss > 0.0 : # Account for wave dependances in a given sea-state (with duration dss)
        if x < 1e-20 :
            return 0.0
        pe_ss = np.sum( probabilityList * (1 - (shtProb)**( dss / rTzList)))
        res = (1-pe_ss) ** (duration_s/dss)  
        
    elif dss < -10 :  # LARGE_T
        v = np.sum( (probabilityList / rTzList) * ( 1 - shtProb) )
        tz_mean = 1. / np.sum( (probabilityList / rTzList) )
        Plt = 1 - tz_mean * v
        Nt = duration_s / tz_mean
        res = Plt ** Nt
    elif dss < 0.0 :  # INDEP
        nss = probabilityList * duration_s / rTzList
        res = np.prod(  shtProb ** nss )
    return res


def squashSpectralResponseList( rsList , rTzList , probabilityList ):
    """Group identical sea-state, and update probability accordingly.

    Parameters
    ----------
    rsList : np.ndarray
        Significant responses
    rTzList : np.ndarray
        response up-crossing period
    probabilityList : np.ndarray or iso.
        Seastate probability

    Returns
    -------
    np.ndarray
        Significant responses
    np.ndarray
        response up-crossing period
    np.ndarray
        Seastate probability
    """
    if isinstance(probabilityList, str) :
        if probabilityList == "iso" :
            probabilityList = np.ones( (len(rTzList)), dtype = float ) / len(rTzList)

    a = pd.DataFrame( data = {"Rs" : rsList, "Rtz" : rTzList, "prob" : probabilityList } )
    arr = a.groupby( ["Rs" , "Rtz"]).prob.sum().reset_index().loc[ : , ["Rs" , "Rtz", "prob"]].values
    return arr[:,0] , arr[:,1] , arr[:,2]




class LongTermConstant(LongTermGen) :
    """Simple long term calculation without short-term variability.
    """

    def __init__(self, responseList, probabilityList, dss):
        """Simple long term calculation without short-term variability.

        Parameters
        ----------
        responseList : np.ndarray
            The constant response in each seastate.
        probabilityList : np.ndarray
            The probability of each seastate.
        dss : float
            The seastate duration.
        """

        self.dss = dss
        self.responseList = responseList

        if isinstance(probabilityList, str) :
            if probabilityList == "iso" :
                self.probabilityList = np.ones( (len(responseList)), dtype = float ) / len(responseList)
        else :
            self.probabilityList = probabilityList / probabilityList.sum()

    def shtProb(self , x):
        return ( x > self.responseList ).astype(int)
        


if __name__ == "__main__":
    lt = LongTermSpectral( np.array([1,100]) , np.array([10,10]), np.array([1,1]) , dss = 10800)

    lt.x_to_rp( lt.rp_to_x(25)  )
    
    lt.plot_rp( rp_range = np.linspace(0.01, 100, 100) )
