import numpy as np
from matplotlib import pyplot as plt
from math import pi, log
from Snoopy import logger
from Snoopy.TimeDomain import OneDof



class DecayAnalysis(object):

    def __init__(self, se, method="minmax_quad", w_filter = None , n_cycle = 0.2 ):
        """

        Parameters
        ----------
        se : pd.Series
            Decay signal, time is the index
        method : str, optional
            How to average the maxima. The default is "minmax_quad". (NL-ROLL JIP)
        w_filter : float, optional
            high frequency filter (remove noise). The default is None.
        n_cycle : int, optional
            Number of cycle to use for the regression. The default is None.

        """

        # Flip signal so that first extrema is always positive
        if se.max() < -se.min() :
            self.se = -se
            self.flip = True
        else :
            self.se = +se
            self.flip = False

        # Read the mcnSolve test time serie
        self.time = self.se.index.values
        self.motion = self.se.values

        #Method
        self.method = method

        self.n_cycle = n_cycle

        #To be filled
        self.coef = None
        self.maxVal = None
        self.minVal = None

        if w_filter is not None :
            self._smooth( w_filter )

        self._computeExtrema()


    def _smooth(self, w_filter):
        """Low pass filter
        """
        from Snoopy.TimeDomain import bandPass
        logger.debug("Smoothing signal")
        self.se = bandPass( self.se, fmin=None, fmax = w_filter, unit ="rad/s" )
        self.motion = self.se.values




    def _computeExtrema(self):
        """Get extrema through upcrossing analysis
        """
        from Snoopy.TimeDomain import UpCrossAnalysis
        self.upCross = UpCrossAnalysis.FromTs( self.se , threshold = 0.0)

        if len(self.upCross) == 0 :
            raise(Exception("No zero-crossing found. Please check that the decay signal is centered around zero."))

        #Remove max before maximum (and dismiss this 1st max)
        self.upCross = self.upCross.loc[ self.upCross.MaximumTime > self.upCross.MaximumTime.loc[self.upCross.Maximum.idxmax()] , :  ].reset_index()


        # Number of cycle is given explicitely
        if self.n_cycle > 1 :
            self.upCross = self.upCross.iloc[:self.n_cycle]
            self.n_cycle = len(self.upCross)

        # Number of cycle until amplitude is less that a fraction of first cycle
        else :
            ranges = self.upCross.Maximum - self.upCross.Minimum
            ranges /= max(ranges)

            def first_low(ranges, thresh)  :
                for i , r in enumerate(ranges) :
                    if r < thresh : return i
                else:
                    return len(ranges)
            self.upCross = self.upCross.iloc[ : first_low(ranges, self.n_cycle) ]
            self.n_cycle = len(self.upCross)

        self._cycle_count = len(self.upCross)

        self.maxTime = self.upCross.MaximumTime.values
        self.maxVal = self.upCross.Maximum.values
        self.minTime = self.upCross.MinimumTime.values
        self.minVal = self.upCross.Minimum.values



    def getPeriod(self, n=5, method = "minmax"):
        """Calculate and return the resonance period, based on extrema location

        Parameters
        ----------
        n : int, optional
            Number of cycle to use. The default is 5.

        Returns
        -------
        float
            Resonance period
        """

        if method == "minmax" :
            n = min(n, self.n_cycle-1)
            if n <= 1 :
                return np.nan
            T = 0.
            for i in range(n):
                try :
                    T += self.maxTime[i+1] - self.maxTime[i]
                    T += self.minTime[i+1] - self.minTime[i]
                except IndexError:
                    logger.error( f"{i:} / {len(self.maxTime):} , {len(self.upCross) :} , {self.n_cycle:}"  )
                    raise(IndexError)

            return T / (2*n)
        else :
            return self.upCross.Period.mean()

    def plotTimeTrace(self, ax = None):
        # Plot the analysed signal and the extracted maxima
        if ax is None :
            fig, ax = plt.subplots()
        ax.plot(self.time, self.motion, "-")
        if self.maxTime is not None:
            ax.plot(self.maxTime[:], self.maxVal[:], "o")
            ax.plot(self.minTime[:], self.minVal[:], "o")
        ax.set(xlabel = "Time (s)")
        return ax

    def _regression(self):
        """Perform the linear regression to get p and q
        Beq_adim = delta  / ( 4pi**2 + delta**2 )**0.5
        """

        if self.method == "max":  # Max only
            self.n = np.zeros((2, len(self.maxVal)-1))
            for i in range(len(self.n[0, :])):
                self.n[0, i] = (self.maxVal[i+1] + self.maxVal[i]) * 0.5
                delta = -log(self.maxVal[i+1] / self.maxVal[i])
                self.n[1, i] = delta / (4*pi**2 + delta**2)**0.5

        elif self.method == "min":  # Min only
            self.n = np.zeros((2, len(self.minVal)-1))
            for i in range(len(self.n[0, :])):
                self.n[0, i] = -(self.minVal[i+1] + self.minVal[i]) * 0.5
                delta = -log(self.minVal[i+1] / self.minVal[i])
                self.n[1, i] = delta / (4*pi**2 + delta**2)**0.5

        elif "minmax" in self.method :
            self.n = np.zeros((2, 2*(self._cycle_count-1) ))
            for i in range( self._cycle_count-1 ):
                if "quad" in self.method :
                    self.n[0, 2*i] = ( self.maxVal[i+1] * self.maxVal[i] )**0.5
                    self.n[0, 2*i+1] = ( self.minVal[i+1] * self.minVal[i] )**0.5
                elif "ari" in self.method :
                    self.n[0, 2*i] = ( self.maxVal[i+1] + self.maxVal[i] )*0.5
                    self.n[0, 2*i+1] = -( self.minVal[i+1] + self.minVal[i] )*0.5
                else :
                    raise(Exception("Unknown method {self.method:}"))

                delta = -log(self.maxVal[i+1] / self.maxVal[i])
                self.n[1, 2*i] = delta / (4*pi**2 + delta**2)**0.5

                delta = -log(self.minVal[i+1] / self.minVal[i])
                self.n[1, 2*i+1] = delta / (4*pi**2 + delta**2)**0.5

        elif "semi" in self.method :  # Use semi cycle (min and max)
            # TODO Overlap decreement
            nDemi = min(len(self.minVal), len(self.maxVal))
            self.n = np.zeros((2, nDemi))
            for i in range(len(self.n[0, :])):
                if "quad" in self.method :
                    self.n[0, i] = (self.maxVal[i] - self.minVal[i]) * 0.5
                elif "ari" in self.method :
                    self.n[0, i] = (-self.maxVal[i] * self.minVal[i]) ** 0.5
                else :
                    raise(Exception(f"Unknown method {self.method:}"))

                delta = -log(self.maxVal[i] / (-self.minVal[i])) * 2.0
                self.n[1, i] = -delta / (4*pi**2 + delta**2)**0.5

        else:
            raise(Exception("Unknown method {self.method:}"))

        A = np.vstack([self.n[0, :], np.ones(len(self.n[0, :]))]).T
        self.coef = np.linalg.lstsq(A, self.n[1, :] , rcond=None)[0]  # obtaining the parameters
        return self.coef


    def plotRegression(self, ax = None, label = "", data_only = False, reg_only = False, reg_equation = True,
                       data_kwargs = {},
                       fit_kwargs = {},
                       ):

        data_kwargs_ = {"marker" : "o", "label" : "data", "linestyle" : ""}
        data_kwargs_.update(data_kwargs)

        fit_kwargs_ = {"marker" : "", "label" : "regression"}
        fit_kwargs_.update(fit_kwargs)


        # Plot the regression
        if ax is None:
            fig, ax = plt.subplots()

        self._regression()

        # plot data
        if not reg_only :
            logger.debug( data_kwargs)
            ax.plot( self.n[0, :], self.n[1, :], **data_kwargs_)

        if not data_only :
            xi = np.linspace(np.min(self.n[0, :]), np.max(self.n[0, :]), 3)
            line = self.coef[0]*xi + self.coef[1]  # regression line
            ax.plot( xi , line, **fit_kwargs_)
        ax.legend()
        ax.set_title("Decay regression, method = {}".format(self.method))
        ax.set_xlabel("Amplitude")
        ax.set_ylabel("Equivalent damping (% of critical)")
        if reg_equation :
            ax.text( 0.55, 0.25,  "y = {:.2e} * x + {:.2e}".format( self.coef[0] , self.coef[1]) , transform=ax.transAxes  )

        return ax

    def getDimDampingCoef(self, k , T0 = None):
        """Return dimensional damping coefficients

        Parameters
        ----------
        k : float
            Stiffness

        T0 : float
            Resonance period. If None, T0 is calculated from decay

        Returns
        -------
        blin : float
            Linear damping coefficient
        bquad : float
            Quadratic damping coefficient

        """

        if self.coef is None :
            self._regression()

        if T0 is None :
            T0 = self.getPeriod()

        Bcr = self.getCriticalDamping(k=k, T0=T0)

        w0 = 2.*pi / T0
        blin = self.coef[1] * Bcr
        bquad = self.coef[0] * Bcr * 3. * pi / (8*w0)
        return blin, bquad


    def getCriticalDamping(self, k , T0 = None):
        """Compute critical damping, from stiffness

        Parameters
        ----------
        k : float
            Stiffness

        T0 : float
            Resonance period. If None, T0 is calculated from decay

        Returns
        -------
        float
            Critical damping
        """

        if T0 is None :
            T0 = self.getPeriod()
        return T0 * k / pi


    def getDimEqDamping(self, blin, bquad, a, T0 = None):
        """Return equivalent damping from blin, bquad and cycle amplitude.

        Parameters
        ----------
        blin : float
            Linear damping coefficient
        bquad : float
            Quadratic damping coefficient
        a : float
            roll cycle amplitude

        Returns
        -------
        Equivalent damping
        """
        if T0 is None :
            T0 = self.getPeriod()
        w0 = 2.*pi / T0
        return blin + bquad * a * 8 *w0 / (3*np.pi)



    def computeOneDof( self , bl=None , bq=None  ) :
        """Simulate decay with simple one dof model.

        Parameters
        ----------
        bl : float or None, optional
            Linear damping coefficient, if None,the fitted one is used. The default is None.
        bq : float or None, optional
            Quadratic damping coefficient, if None,the fitted one is used. The default is None.

        Returns
        -------
        res : pd.Series
            Numerical decay
        """

        k = 1
        if bl is None or bq is None :
            bl , bq = self.getDimDampingCoef(k)

        max_ , maxTime_ = self.upCross.iloc[0,:].loc[["Maximum" , "MaximumTime"]]
        tr = self.getPeriod()
        m = k * (tr / (2*np.pi) )**2

        # Generate one dof decay
        oneDof = OneDof(m=m, bl=bl, bq=bq, k=k)
        res = oneDof.decay(tMin=maxTime_, tMax=self.time.max(), X0=np.array([max_, 0.]) , t_eval = np.arange(maxTime_,self.time.max(), tr / 40 ))

        return res


    def compareWithFitted(self, ax = None):
        """Plot numerical decay with fitted parameter overlayed with original time trace

        Parameters
        ----------
        ax : matplotlib ax, optional
            Where to plot. The default is None.

        Returns
        -------
        ax : matplotlib ax
            The graph
        """

        if ax is None :
            fig , ax = plt.subplots()
        res = self.computeOneDof( )

        ax.plot(res.index , res.values , label = "Fitted damping")
        self.plotTimeTrace(ax=ax)
        ax.legend()
        return ax














