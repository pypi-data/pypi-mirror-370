import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import InterpolatedUnivariateSpline
from Snoopy import logger
from scipy.stats import beta, linregress
from scipy.integrate import trapezoid
from . import probN, probN_ci

        
        
class ReturnLevel():
    """Compute return period from samples.

    Notes
    -----
    Assumes :
        - independent events
        - that number of events in the duration is always the same.

    All relates to the following definition (probability of not exceeding return value on return period is 1/e) :

        :math:`P(X_{RP}, RP) = 1 / e`

    with:

        :math:`P(X, T) = P_c^{T / Rtz}`

    $P_c$ being the non-exceedance probability on each events (can be up-crossing period)

    :math:`RP = - Rtz / ln( P_c(x) )`

    This is not to be used for POT, where number of threshold exceedances is random (Poisson process)
    """

    def __init__(self, data, duration, variant = (0., 0.), alphap = None , betap = None):
        """Construct ReturnLevel instance

        Parameters
        ----------
        data : array like
            data samples (independent events)
        duration : float
            Total duration covered by the data. If None, duration is retrieve from data index (if Series). Each event thus corresponds to DT = duration / len(data).
        alphap : float, optional
            alpha coefficient for empirical distribution. The default is 0..
        betap : float, optional
            beta coefficient for empirical distribution. The default is 0..

        Example
        ------
        >>> rl = ReturnLevel( data , duration = 10800 )
        >>> rl.rp_to_x( 3600  )
        >>> rl.plot()

        """

        self.data = data

        self._n = len(data)

        if duration is None :
            self._duration = data.index.max() - data.index.min()
        else :
            self._duration = duration
            
        self._variant = variant

        # Empirical exceedance probabilitys
        self._prob = probN(self._n, variant = variant, alphap = alphap , betap = betap)

        # Empirical return period
        self._rp = -duration / (self._n * np.log( 1 - self._prob ))

        # Empirical return values
        self._rv = np.sort(data)

        # Event duration
        self.t_block = duration / self._n

        # Space for interpolator
        self._x_to_rp = None
        self._rp_to_x = None


    @property
    def variant(self):
        return self._variant
    
    
    @variant.setter
    def alphap_betap(self, variant):
        """Setter for alphap and betap.
        """
        #self._rp have to be recalculated and interpolator reset
        #Compare to creating a new object, it just save the data sorting...
        
        self._variant = variant
        self._prob = probN(self._n, variant)
        self._rp = -self._duration / (self._n * np.log( 1 - self._prob ))
        self._x_to_rp = None
        self._rp_to_x = None
        

    @property
    def duration(self) :
        return self._duration



    def bootstrap(self, fun_name, n = 100, **kwargs):
        """boostrap


        Parameters
        ----------
        fun_name : str
            Method name. for instance 'fun_name = rp_to_x'
        n : int, optional
            Number of sample for the bootstrap. The default is 100.
        **kwargs : any
            Argument passed to 'fun_name'

        Returns
        -------
        res : np.ndarray
            Array with bootstrap results

        Note
        ----
        The bootstraping performed here does not allow for an accurate CI in the tail. By construction, the boostrapped samples can not exceed the maximum from the original data. Then, the distribution out from the bootstrap is expected to be biased toward lower values.

        Example
        -------
        >>> rl = ReturnLevel(data , duration)
        >>> rl.bootstrap( fun_name = 'rp_to_x' , rp = 100. , n = 1000  )
        [  151.1, 156.2 , ..., 156.2 ]
        >>> rl.rp_to_x(100.)
        154.0
        """

        res = []
        for i in range(n) :
            rl_ = ReturnLevel( np.random.choice( self.data , size = self._n  ) , duration = self.duration )
            fun = getattr(rl_, fun_name)
            if callable(fun) :
                res.append( fun( **kwargs) )
            else:
                res.append( fun )
        return np.array(res)



    def to_hdf(self, filename):
        """Store object to file (HDF)

        Note : no huge benefit compared to storing data and reconstructing the object, just a bit more convenient.

        Example
        -------
        >>> rl = st.ReturnLevel( data , duration )
        >>> rl.to_hdf( "f.h5" )
        ... later on
        >>> rl = st.ReturnLevel.read_hdf( "f.h5" )

        Parameters
        ----------
        filename : str
            File name
        """
        import h5py
        f = h5py.File( filename, 'w')
        f.create_dataset(name = "_rp" , shape = (len(self._rp)) , dtype = float, data = self._rp )
        f.create_dataset(name = "_rv" , shape = (len(self._rv)) , dtype = float, data = self._rv )
        f.attrs["duration"] = self.duration
        f.close()

    @classmethod
    def read_hdf(cls, filename):
        """Construct from hdf file.

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        ReturnLevel
            The object
        """
        import h5py
        f = h5py.File( filename, 'r')
        _rp =  f["_rp"][:]
        c = cls( data = f["_rv"][:], duration = f.attrs["duration"] )
        f.close()
        c._x_to_rp = None
        c._rp = _rp # Necessary because alphap, betap could be different from the default one
        return c


    @staticmethod
    def pc_to_rp( pc, blockSize):
        """Convert probability of each event to return period

        $RP = - Rtz / ln( P_c(x) )$

        Parameters
        ----------
        pc : float or np.ndarray
            Non-exceedance probability of event
        blockSize : float
            Duration of the 'event'

        Returns
        -------
        float or np.ndarray
            Return period
        """
        return -blockSize / np.log( pc )

    @staticmethod
    def rp_to_pc(rp, blockSize):
        """Convert return period to probability of event.

        $RP = - Rtz / ln( P_c(x) )$

        Parameters
        ----------
        rp : float or np.ndarray
            Return period
        blockSize : float
            Duration of the 'event'

        Returns
        -------
        float or np.ndarray
            Non-exceedance probability of event
        """
        return np.exp(-blockSize / rp)

    @property
    def empirical_rp(self):
        return self._rp

    @property
    def empirical_rv(self):
        return self._rv


    def _build_interp_rp_to_x(self):
        # Build interpolator
        logger.debug("Build return level interpolator")
        self._rp_to_x = InterpolatedUnivariateSpline( self._rp , self._rv, ext = "raise", k = 1 )

    def _build_interp_x_to_rp(self):
        # Handle duplicated data
        logger.debug("Build return level interpolator")
        _, u_index = np.unique(self._rv, return_index=True)
        self._x_to_rp = InterpolatedUnivariateSpline( self._rv[u_index] , self._rp[u_index], ext = "zeros", k = 1)

    def empirical_slope_distribution(self, rp, NbPointRegr, method = "sym"):
        
        index_RP = np.searchsorted(self._rp, v = rp) #we find 1st index in sorted data for which _rp > RP
        if method == "sym":
            #Extract return value points from distrib to perform regression on both sides of RP
            regr_rv = self._rv[index_RP- NbPointRegr//2 :index_RP+ NbPointRegr//2+NbPointRegr%2] #%2 here to ensure that regression is performed on the good number of items even when NbPointRegression not even
            #Extract return period points from distrib to preform regression on both sides of RP
            regr_rp = self._rp[index_RP- NbPointRegr//2 :index_RP+ NbPointRegr//2+NbPointRegr%2]
        
        elif method == "up":
            #Extract return value points from distrib to perform regression above RP
            regr_rv = self._rv[index_RP-1 :index_RP+ NbPointRegr-1] #-1 because index_RP is the first index for which rv is bigger than x_rp
            #Extract return period points from distrib to preform regression above RP
            regr_rp = self._rp[index_RP-1:index_RP+ NbPointRegr-1]
       
        s = linregress(np.log(regr_rp), regr_rv).slope
        
        return(s)
        


    def plot(self, ax = None, scale_rp = lambda x:x, marker = "+" , linestyle = "", transpose = False, scale_y = 1, **kwargs):
        """Plot value against return period.

        Parameters
        ----------
        ax : AxesSubplot, optional
            Where to plot. The default is None.
        scale_rp : fun, optional
            RP scale (for instance, in input data are seconds, but plots is desired in hours). The default is identity.
        marker : str, optional
            Marker. The default is "+".
        linestyle : str, optional
            linestyle. The default is "".
        transpose : bool. The default is False
            If True, Return period is on vertical axis
        **kwargs : any
            Optional argument passed to plt.plot()

        Returns
        -------
        ax : AxesSubplot
            The graph.
        """
        if ax is None :
            fig , ax = plt.subplots()

        x = scale_rp(self._rp )
        y = self._rv * scale_y
        if transpose :
            x, y = y, x
            ax.set_yscale("log")
            ax.set(ylabel = "Return period")
        else:
            ax.set_xscale("log")
            ax.set(xlabel = "Return period")

        ax.plot( x, y,  marker = marker, linestyle = linestyle, **kwargs)

        return ax

    def x_to_rp(self , x) :
        """Return period from return value

        Parameters
        ----------
        x : float
            Return value

        Returns
        -------
        float
            Return period
        """
        if self._x_to_rp is None:
            self._build_interp_x_to_rp()

        if np.max(x) > self._rv[-1]:
            raise(Exception("Point above maximum value in sample"))
            
        return self._x_to_rp(x)

    def rp_to_x(self, rp) :
        """Return value from return period

        Parameters
        ----------
        rp : float
            return period

        Returns
        -------
        float
            return value
        """
        if self._rp_to_x is None:
            self._build_interp_rp_to_x()
        return self._rp_to_x(rp)


    def x_to_rpci( self, alpha, ci_type = "beta" ):
        """Return RP confidence interval for sorted empirical return values, using beta distribution

        Parameters
        ----------
        alpha : float
            Centered confidence interval
        ci_type : str, optional
            How to calculate the CI. The default is "n".

        Returns
        -------
        (np.ndarray, np.ndarray)
            Lower and upper CI.
        """

        i = np.arange(1, self._n + 1, 1)[::-1]

        if ci_type == "beta" :
            betaN = beta( i , self._n + 1 - i )
        elif ci_type == "jeffrey" :
            betaN = beta( i + 0.5 , self._n + 0.5 - i )

        prob_l, prob_u = betaN.ppf( alpha/2 ) , betaN.ppf(1-alpha/2)
        rp_l = -self._duration / (self._n * np.log( 1 - prob_l ))
        rp_u = -self._duration / (self._n * np.log( 1 - prob_u ))

        return rp_l , rp_u


    def rp_to_xci(self, alpha_ci, ci_type = "bootstrap"):
        """Return bootstrapped confidence interval of X at a given RP

        Parameters
        ----------
        alpha : float
            Centered confidence interval.
        ci_type : str, optional
            How to compute the CI. The default is "bootstrap".

        Returns
        -------
        x_low : np.ndarray
            Lower bound of CI associated to self.empirical_rp
        x_up : np.ndarray
            Upper bound of CI associated to self.empirical_rp
        """

        if ci_type == "bootstrap" :
            v = self.bootstrap( fun_name = "empirical_rv" , n = int(50 / alpha_ci)  )
            x_up = np.quantile(v , alpha_ci/2 , axis = 0)
            x_low = np.quantile(v , 1-alpha_ci/2 , axis = 0)
        else :
            # TODO : using beta distribution
            raise(NotImplementedError)
        return x_low , x_up


    def rp_to_xerror(self, rp, ci_type = "bootstrap", n = 200) :
        """Return quadratic error of estimate at RP.

        Parameters
        ----------
        rp : float
            return period

        Returns
        -------
        error : Float
            Relative quadratic error
        """
        logger.warning("rp_to_xerror is experimental")
        x_rp = self.rp_to_x(rp)
        if ci_type == "bootstrap" :
            logger.warning("Boostrapping for empirical quantile is not recommanded")
            # Not expected to provide good results
            res = self.bootstrap("rp_to_x", rp = rp , n = n)
            return np.std(res) / x_rp
        elif ci_type == "beta" :
            # TODO : add warning when cdf in x_scale is far from "closed"
            i = np.arange(1, self._n + 1, 1)
            x = self._rv 
            cdf = 1 - beta( i , self._n + 1 - i ).cdf( np.exp( -self.t_block / rp) )
            return ( ( (x[-1]-x_rp)**2 * cdf[-1]  ) -  ( (x[0]-x_rp)**2 * cdf[0]  ) -  trapezoid( 2*(x-x_rp)*cdf, x=x ) )**0.5 / x_rp
        else : 
            raise(Exception("ci_type not known"))
               



    def plot_ci(self, alpha_ci , ax = None, scale_rp = lambda x:x, ci_type = "beta", alpha = 0.1, scale_y = 1, **kwargs) :
        """Plot confidence interval

        Parameters
        ----------
        alpha_ci : float
            Centered confidence interval.
        ax : AxesSubplot, optional
            Where to plot. The default is None.
        scale_rp : fun, optional
            RP scale (for instance, in input data are seconds, but plots is desired in hours). The default is identity
        ci_type : str, optional
            Variant for the confidence interval, among ["n" , "jeffrey"]. The default is "n".
        alpha : float, optional
            Opacity for the filling of the confidence interval. The default is 0.1.
        scale_y : float
            Scale for y-axis
        **kwargs : any
            Additional arguments passed to .fillbetweenx().

        Returns
        -------
        ax : AxesSubplot
            The graph.
        """

        if ax is None :
            fig , ax = plt.subplots()

        if ci_type in [ "jeffrey", "beta"]:
            rp_l, rp_u = self.x_to_rpci(alpha = alpha_ci , ci_type = ci_type)
            ax.fill_betweenx(self._rv * scale_y, scale_rp(rp_l), scale_rp(rp_u), alpha = alpha, **kwargs)
        elif "bootstrap" in ci_type :
            x_l, x_u = self.rp_to_xci(alpha_ci = alpha_ci , ci_type = ci_type)
            ax.fill_between( scale_rp(self._rp), x_l, x_u, alpha = alpha, **kwargs)
        else:
            raise(ValueError())


        return ax


    @staticmethod
    def plot_distribution( distribution, blockSize, rp_range, ax = None, scale_y = 1.0, transpose = False, scale_rp = lambda x:x, **kwargs):
        """Plot analytical distribution against return period

        Parameters
        ----------
        distribution : scipy.stats.rv_frozen
            Distribution on each event.
        blockSize : float
            duration of each event
        ax : plt.Axis, optional
            Where to plot. The default is None.
        transpose : bool. The default is False
            If True, Return period is on vertical axis

        Returns
        -------
        ax : plt.Axes
            The graph
        """

        if ax is None :
            fig, ax = plt.subplots()

        x, y = scale_rp(rp_range), ReturnLevel.rp_to_x_distribution( distribution, blockSize, rp_range)
        y *= scale_y
        if transpose :
            y, x  = x, y
            ax.set_yscale("log")
        else :
            ax.set_xscale("log")
        ax.plot( x, y, **kwargs)
        return ax


    @staticmethod
    def x_to_rp_distribution( distribution, blockSize, x):
        """Calculate return period of a given value x. x follows "distribution" on each even that has a duration "blockSize".

        Parameters
        ----------
        distribution : scipy.stats.rv_frozen
            Distribution on each event.
        blockSize : float
            duration of each event
        x : float
            Value

        Returns
        -------
        rp : float
            return period
        """

        return -blockSize / np.log( distribution.cdf(x) )

    @staticmethod
    def slope_distribution( distribution, blockSize, rp, d_rp = 0.1 ):
        """Return distribution slope

        Parameters
        ----------
        distribution : stats.rv_frozen
            Analitycal distribution
        blockSize : float
            Block size
        rp : float
            Return period
        d_rp : float, optional
            RP step for differentiation. The default is 0.1.

        Returns
        -------
        float
            slope
        """

        x1 = ReturnLevel.rp_to_x_distribution(distribution, blockSize, rp)
        x2 = ReturnLevel.rp_to_x_distribution(distribution, blockSize, rp + d_rp)

        return (x2-x1) / ( np.log(rp+d_rp) - np.log(rp)  )


    @staticmethod
    def rp_to_x_distribution(distribution, blockSize, rp):
        """Calculate return value x from return period rp. x follows "distribution" on each even that has a duration "blockSize".

        Parameters
        ----------
        distribution : scipy.stats.rv_frozen
            Distribution on each event.
        blockSize : float
            duration of each event
        rp : float or np.ndarray
            return period

        Returns
        -------
        x : float or np.ndarray
            return value
        """
        p_ = 1 - np.exp(-blockSize / (rp))
        return distribution.isf(p_)
    
    
    def plot_probability(self, reference_duration, ax = None, marker = "+" , linestyle = "", **kwargs):
        """
        
        Parameters
        ----------
        reference_duration : float
            Reference duration in which the distribution is plot

        Returns
        -------
        None.

        """
        
        if ax is None :
            fig, ax = plt.subplots()
            
        p = (1-self._prob)**(reference_duration / self.t_block)
        ax.plot( self.empirical_rv , 1-p, marker = marker, linestyle = linestyle, **kwargs )
        ax.set_yscale("log")
        return ax
    
    def plot_probability_ci(self, reference_duration, alpha_ci , ax = None, ci_type = "jeffrey", alpha = 0.1, scale_y = 1, **kwargs) :
        """Plot confidence interval

        Parameters
        ----------
        alpha_ci : float
            Centered confidence interval.
        ax : AxesSubplot, optional
            Where to plot. The default is None.
        ci_type : str, optional
            Variant for the confidence interval, among ["n" , "jeffrey"]. The default is "n".
        alpha : float, optional
            Opacity for the filling of the confidence interval. The default is 0.1.
        **kwargs : any
            Additional arguments passed to .fillbetweenx().

        Returns
        -------
        ax : AxesSubplot
            The graph.
        """
        
        if ax is None :
            fig , ax = plt.subplots()

        if ci_type in ["n" , "jeffrey"]:
            ci_l , ci_u = probN_ci( self._n , alpha = alpha_ci, method = ci_type )
            p_l = (1 - ci_l)**(reference_duration / self.t_block)
            p_u = (1 - ci_u)**(reference_duration / self.t_block)
            ax.fill_between( self.empirical_rv, 1-p_l, 1-p_u, alpha = alpha, **kwargs)
        else : 
            raise(NotImplementedError)
        return ax
            
            
            


# Compatiblity with previous version:
from Snoopy.Tools import renamed_function
ReturnLevel.x_2_rp = renamed_function( ReturnLevel.x_to_rp , "x_2_rp" )
ReturnLevel.rp_2_x = renamed_function( ReturnLevel.rp_to_x , "rp_to_x" )


def xrp_pdf( x, rp, alpha, T_block, dist ):
    """Compute probability density of the empirical return value x, with return period 'rp', knowin simulated time and distribution.

    Parameters
    ----------
    x : float or np.ndarray
        Response value
    rp : float
        return period
    alpha : float
        ratio between data duration and return period
    T_block : float
        Block size (fixed event duration)
    dist : stats.rv_continuous
        Disitribution of event

    Returns
    -------
    float or np.ndarray
        Prability density of x.
    """
    nu = 1 / T_block
    p = np.exp(-1/(nu*rp))
    return dist.pdf( x ) * beta( (nu*alpha*rp+1) * p , (nu*alpha*rp+1)*(1-p) ).pdf(dist.cdf(x))


def xrp_cdf( x, rp, alpha, T_block, dist ):
    """Compute cumulative probability of the empirical return value x, with return period 'rp', knowin simulated time and distribution.

    Parameters
    ----------
    x : float or np.ndarray
        Response value
    rp : float
        return period
    alpha : float
        ratio between data duration and return period
    T_block : float
        Block size (fixed event duration)
    dist : stats.rv_continuous
        Disitribution of event

    Returns
    -------
    float or np.ndarray
        Prability density of x.
    """
    nu = 1 / T_block
    p = np.exp(-1/(nu*rp))
    return beta( (nu*alpha*rp+1) * p , (nu*alpha*rp+1)*(1-p) ).cdf( dist.cdf(x) )



