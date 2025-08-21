import os
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import minimize, basinhopping, minimize_scalar
from scipy.integrate import quad, simpson, dblquad
from scipy import interpolate
from scipy.interpolate import interp1d
from Snoopy import Spectral as sp
from Snoopy import Math as sm
import _Spectral
from Snoopy import logger

# Default frequency and heading range
_wmin = 0.1
_wmax = 3.0
_dw = 0.025
_freq = np.arange(_wmin, _wmax + _dw, _dw)
_head = np.deg2rad(np.linspace(0., 360., 72, endpoint = False))
_headClosed = np.deg2rad(np.linspace(0., 360., 73, endpoint = True))




def compareSeaStatePlot(  ss1, ss2  , name_1 = "1", name_2 = "2", freq = _freq ):
    fig, ( (ax2D1, ax2D2) , (axFreq, axHead)) = plt.subplots(nrows = 2, ncols = 2)
    ss1.plot2D(ax=ax2D1, freq = freq)
    ss2.plot2D(ax=ax2D2, freq = freq)
    ax2D1.set_title( f"{name_1:} ($H_s = {ss1.integrate_hs():.1f}m)$")
    ax2D2.set_title( f"{name_2:} ($H_s = {ss2.integrate_hs():.1f}m)$")
    ss1.plot(ax=axFreq, label = name_1, w = freq)
    ss2.plot(ax=axFreq, label = name_2, w = freq)
    ss1.plotHeading(ax=axHead, label = name_1)
    ss2.plotHeading(ax=axHead, label = name_2)
    axFreq.legend(loc=1, prop={"size":6})
    axHead.legend(loc=1, prop={"size":6})
    axHead.set_xlim([0,360.])
    fig.suptitle( "Diff = {:.1%}".format(ss1.diff2D_rel(ss2) ))
    fig.tight_layout( rect=[0, 0.03, 1, 0.95])
    return ( (ax2D1, ax2D2) , (axFreq, axHead))

class SeaStateABC():


    def print_detail(self) :
        hs = self.getHs()
        tz = self.integrate_tz()
        tp = self.find_tp()
        steepness_tz = hs / sp.t2l( tz )
        steepness_tp = hs / sp.t2l( tp )

        st_tz_lim_dnv = 1/10. if tz <= 6 else 1/15.
        st_tp_lim_dnv = 1/15. if tp <= 8 else 1/25.


        if self.isUnidirectional() :
            head = self.getSpectrum(0).heading
        else :
            head = self.integrate_mean_direction()


        return f"""
Hs = {hs:.1f}m
Tz = {tz:.1f}s
Tp = {tp:.1f}s  (Lamnda_p = {sp.t2l( tp ):.1f}m)
Head = {np.rad2deg(head):.1f}
Steepness (tp) = {steepness_tp:.1%} (DNV_LIM = {st_tp_lim_dnv:.1%})
Steepness (tz) = {steepness_tz:.1%} (DNV_LIM = {st_tz_lim_dnv:.1%})

"""


    def steepness_tp(self):
        return self.getHs() / sp.t2l( self.find_tp() )

    def steepness_tz(self):
        return self.getHs() / sp.t2l( self.integrate_tz() )


    def fitParametric1D(self, spectrumModels, coefs_0 = None, solver="global", w = None, **kwargs):
        """Fit (or re-fit a parametric spectrum), using least-square.

        All parameter, including Hs and Tp are free.

        Parameters
        ----------
        spectrumModels : TYPE
            DESCRIPTION.
        coefs_0 : list, optional
            Starting point for the minimization process. The default is None.
        solver : str, optional
            solver type. The default is "global".
        w : array like, optional
            Frequency range on which the error is calculated. The default is None.
        **kwargs : Any
            Keywords argument passed to the minimizer
        Returns
        -------
        Spectral.SeaState
            Fitted seastate


        Example
        -------
               >>> parametricSS = seaState.fitParametric1D( [Jonswap] )

        """
        if w is None :
            w = _freq

        target = self.compute(w)

        if coefs_0 is None :
            coefs_0 = np.concatenate( [  i.getCoefs_0() for i in spectrumModels ] )

        coefs_I = [0]
        for i, s in enumerate(spectrumModels) :
            coefs_I.append( coefs_I[i] + s.getNParams() )

        def errFunc(coefs):
            ss = sp.SeaState( [ s( *coefs[ coefs_I[i] : coefs_I[i+1]] ) for i, s in enumerate(spectrumModels) ]  )

            #Filter out irrealistics seastate :
            if not ss.check() :
                err = np.sum((target[:])**2)
                return 100 + 100*err
            err = np.sum((target[:] - ss.compute( w ))**2)
            return err

        if solver == "local" :
            coefs = minimize(errFunc, coefs_0, method = "Powell", options = {"maxiter" : 20} , **kwargs).x
        elif solver == "global" :
            coefs = basinhopping(errFunc, coefs_0, **kwargs).x
        elif solver == "init" :
            coefs = coefs_0

        #Ensure the coefs remain in bounds
        coefs = np.maximum( coefs, np.concatenate( [  i.getCoefs_min() for i in spectrumModels ] ) )

        return sp.SeaState(  [ s(*coefs[ coefs_I[i] : coefs_I[i+1]]) for i, s in enumerate(spectrumModels) ]  )


    def fitParametric1D_MOM(self, spectrumModel, coefs_0 = None, *args, **kwargs):
        """ Fit with moments
        Assume 1st coefs is hs
        """

        n = spectrumModel.getNParams()

        hs_ = self.integrate_hs()

        if coefs_0 is None :
            coefs_0 = spectrumModel.getCoefs_0()

        target_mom = np.array( [ self.integrate_moment( i ) for i in range(1,n) ] )

        def fun0(coefs) :
            ss = sp.SeaState( spectrumModel( hs_, *coefs ) )
            current_mom = np.array( [ ss.integrate_moment( i ) for i in range(1,n)] )
            res = current_mom - target_mom
            return res

        from scipy.optimize import fsolve

        coefs = fsolve(fun0 , x0 = coefs_0[1:] )

        return sp.SeaState( spectrumModel(  hs_, *coefs ) )


    def diff1D( self , ss , w = None) :
        """Return difference between 1D sea-state (squared)
        """
        if w is None :
            w = np.arange(_wmin, _wmax, _dw)
        return simpson( (self.compute(w)[:] - ss.compute(w)[:])**2  , x=w )


    def diff1D_rel( self, ss , w = None, adim = None) :
        if w is None:
            w = _freq
        if adim is None :
            adim  = self.get_msquare()
        return self.diff1D(ss , w = w ) / adim

    def get_msquare(self, w=None):
        if w is None :
            w = _freq
        return simpson( y = self.compute(w)**2 , x=w )



    def fitParametric2D( self,  spectrumModels, spreadingType, coefs_0 = None , solver = "global", w = None, b = None, method = "Powell", fixedSpreading = None, *args, **kwargs) :
        """Fit a 2D parametric spectrum.

        coefs_0 = Starting coefficient ( hs, tp, gamma, heading, spreadingValue )

        Parameters
        ----------
        spectrumModels : list
            List of spectrum type
        spreadingType : sp.SpreadingType
            Type of spreading.
        coefs_0 : list, optional
            Starting coefficients. The default is None.
        solver : str, optional
            local or global minimize . The default is "global".
        w : np.ndarray, optional
            Frequency discretization. The default is None.
        b : np.ndarray, optional
            Heading discretization. The default is None.
        method : str, optional
            Local minimization method. The default is "Powell".
        fixedSpreading : float, optional
            If spreading value is fixed (if None, spreading is fitted). The default is None.
        *args : *
            argument passed to minimizer.
        **kwargs : **
            keyword argument passed to minimizer.

        Returns
        -------
        sp.SeaState
            Fitted parametric sea-state


        Examples
        --------
        fitted_seastate = ss1.fitParametric2D( [sp.Jonswap], spreadingType = sp.SpreadingType.Cosn ,
                                               coefs_0=[ hs_1*1.1, tp_1*0.8, gamma_1*2 , heading_1*0.9, spreading_1*5] ,
                                               solver = "local"
                                             )

        """
        if coefs_0 is None :
            if fixedSpreading is None :
                spread_0 = 20
                coefs_0 = np.concatenate( [  list(i.getCoefs_0()) + [np.pi] + [spread_0] for i in spectrumModels ] )
            else :
                coefs_0 = np.concatenate( [  list(i.getCoefs_0()) + [np.pi] for i in spectrumModels ] )

        if fixedSpreading is None :
            min_ = np.concatenate( [  list(i.getCoefs_min()) + [0.0] + [2.] for i in spectrumModels ] )
            max_ = np.concatenate( [  list(i.getCoefs_max()) + [2*np.pi] + [60.] for i in spectrumModels ] )
        else :
            min_ = np.concatenate( [  list(i.getCoefs_min()) + [0.0] for i in spectrumModels ] )
            max_ = np.concatenate( [  list(i.getCoefs_max()) + [2*np.pi] for i in spectrumModels ] )

        if method in [ "L-BFGS-B", "TNC", "SLSQP" ] :
            bounds = ( min_, max_ )
        else:
            bounds = None

        if w is None :
            w = _freq

        if b is None :
            b = _head

        w_, b_ = np.meshgrid( w, b  )
        w_ = w_.flatten()
        b_ = b_.flatten()

        coefs_I = [0]
        if fixedSpreading is None:
            for i, s in enumerate(spectrumModels) :
                coefs_I.append( coefs_I[i] + s.getNParams() + 2 )
        else :
            for i, s in enumerate(spectrumModels) :
                coefs_I.append( coefs_I[i] + s.getNParams() + 1 )

        target = self.compute(  w_ , b_  )

        def errFunc(  coefs ) :
            if fixedSpreading is None:
                ss = sp.SeaState( [ s(*coefs[ coefs_I[i] : coefs_I[i+1] - 2 ] ,
                                      heading = coefs[ coefs_I[i+1] - 2 ],
                                      spreading_type = spreadingType ,
                                      spreading_value = coefs[ coefs_I[i+1] - 1 ]
                                 ) for i, s in enumerate(spectrumModels) ]  )
            else :
                ss = sp.SeaState( [ s(*coefs[ coefs_I[i] : coefs_I[i+1] - 1 ] ,
                                      heading = coefs[ coefs_I[i+1] - 1 ],
                                      spreading_type = spreadingType ,
                                      spreading_value = fixedSpreading,
                                 ) for i, s in enumerate(spectrumModels) ]  )

            #Filter out irrealistics seastate :
            if not ss.check() :
                err = np.sum((target[:])**2)
                return 100 + 100*err

            current = ss.compute(  w_, b_  )
            err = np.sum((target[:] - current[:])**2)
            return err


        if solver == "local" :
            res = minimize(errFunc, coefs_0, bounds = bounds, method = method, options = {"maxiter" : 1000} , *args, **kwargs)
            if res.success :
                coefs = res.x
            else :
                print (res)
                raise(Exception("Not able to fit"))
        elif solver == "global" :
            coefs = basinhopping(errFunc, coefs_0,  *args, **kwargs).x
        elif solver == "init" :
            coefs = coefs_0


        if fixedSpreading is None :
            return sp.SeaState( [ s(*coefs[ coefs_I[i] : coefs_I[i+1] - 2 ] ,
                                      heading = coefs[ coefs_I[i+1] - 2 ],
                                      spreading_type = spreadingType ,
                                      spreading_value = coefs[ coefs_I[i+1] - 1 ]
                                 ) for i, s in enumerate(spectrumModels) ]  )

        else :
            return sp.SeaState( [ s(*coefs[ coefs_I[i] : coefs_I[i+1] - 1 ] ,
                                      heading = coefs[ coefs_I[i+1] - 1 ],
                                      spreading_type = spreadingType ,
                                      spreading_value = fixedSpreading
                                 ) for i, s in enumerate(spectrumModels) ]  )



    def diff2D( self, ss, w = None, b = None, adim = None   ):
        """Return difference between 2D sea-state
        """

        if w is None :
            w = _freq

        if adim is None :
            adim  = self.integrate_moment( 0, w = w  )

        if b is None :
            b = _head

        db = b[1] - b[0]
        diff = 0.

        for ib, b in enumerate(b):
            diff += simpson( (self.compute(w,b)[:] - ss.compute(w,b)[:])**2  , x=w )

        return diff * db


    def diff2D_rel( self , ss , wmin = 0.1 , wmax = 2.0 , dw = 0.01 , adim = None) :
        if adim is None :
            adim  = self.get_msquare()
        return self.diff2D( ss ) / adim

    def plotAll(self, w=_freq, b=None):
        fig, ( (ax2D1, axHead) , (axFreq, _)) = plt.subplots(nrows = 2, ncols = 2)
        self.plot2D(ax=ax2D1, freq = w)
        self.plot(ax=axFreq, w = w)
        self.plotHeading(ax=axHead, transpose = True)
        axHead.set_ylim([0,360.])
        ax2D1.set_ylim([0,360.])
        fig.tight_layout( rect=[0, 0.03, 1, 0.95])


    def plotHeading( self, ax = None, b = None, transpose = False, **kwargs ):
        if ax is None:
            fig, ax = plt.subplots()

        if b is None :
            b = np.linspace(0 , 2*np.pi , 100 )
        spread = self.computeSpreading( b )
        if not transpose :
            ax.plot( np.rad2deg(b), spread , **kwargs )
            ax.set_ylim( [ 0., max(spread)] )
            ax.set_xlabel(r"$\beta$ $(deg)$")
            ax.set_ylabel(r"Wave spectral density ($\frac{m^2}{rad/s}$)")
            ax.set_ylim( [0,  max( ax.get_ylim()[1],  np.max(spread)*1.05)  ] )
        else:
            ax.plot( spread,np.rad2deg(b) , **kwargs )
            ax.set_xlim( [0,  max( ax.get_xlim()[1],  np.max(spread)*1.05)  ] )
            ax.set_ylabel(r"$\beta$ $(deg)$")
            ax.set_xlabel(r"Wave spectral density ($\frac{m^2}{rad/s}$)")



    def plot(self, ax=None, w=None, describe = False, **kwargs):
        """Plot spectrum against frequency (integrated over all headings).
        """
        if ax is None:
            fig, ax = plt.subplots()

        if w is None :
            w = np.linspace( *self.get_wrange(0.99) , 200 )

        sw = self.compute(w)
        ax.plot(w, sw, **kwargs )
        ax.set_ylim(bottom=0., top = max( ax.get_ylim()[1],  np.max(sw)*1.05)  )
        ax.set_xlabel(r"$\omega$ $(rad/s)$")
        ax.set_ylabel(r"Wave spectral density ($\frac{m^2}{rad/s}$)")
        if describe :
            ax.set_title( self.__str__() )
        return ax

    def plot2D(self, ax=None, freq=_freq, head=_headClosed, polar=False, heading_convention="starspec", vessel = False, vessel_azimuth = None, **kwargs):
        """Plot the 2D spectrum.

        Parameters
        ----------
        ax : plt.Axes, optional
            Where to plot. The default is None.
        freq : np.ndarray, optional
            Frequencies. The default is _freq.
        head : np.ndarray, optional
            Headings. The default is _headClosed.
        polar : bool, optional
            If True plot is on polar coordinates. The default is False.
        heading_convention : str, optional
            Convention for heading. Among ("meteorological", "local", "starspec"). The default is "starspec".
        vessel : bool, optional
            If true, as the vessel to the plot. The default is False.
        vessel_azimuth : float, optional
            Vessel azimuth is vessel==True and global conventions. The default is None.

        **kwargs : any
             kwargs passed to contourf()

        Returns
        -------
        ax : plt.Axes
            The graph.

        """

        if heading_convention == "meteorological" :
            heading_convention = "starspec"

        from Snoopy.PyplotTools.surfacePlot import mapFunction
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111, polar=polar)

        if polar and heading_convention == "local":
            ax.set_theta_zero_location("W")
            ax.set_theta_direction(1)
        elif polar and heading_convention == "starspec":
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
        elif polar and heading_convention == "snoopy":
            ax.set_theta_zero_location("E")
            ax.set_theta_direction(1)
        elif polar:
            raise(Exception("heading convention not handled"))


        if polar:
            ax = mapFunction(head, freq, lambda x, y: self.compute(y, x),  ax=ax, **kwargs)
            ax.tick_params(axis='y', colors='white')
            ax.set_rlabel_position(90.)
            ax.set_yticks( np.arange( sm.round_nearest(np.min(freq) , 0.1), np.max(freq) , 0.2 ))

            if vessel :
                if heading_convention != "local" and vessel_azimuth is None :
                    raise(Exception("Azimuth of the vessel should be provided when drawing in global coordinate system"))
                drawing = sp.headingConvention.get_vessel_coordinates( vessel_azimuth, convention = heading_convention, scale = 0.1 )

                ax2 = ax.get_figure().add_axes(ax.get_position(), frameon=False, polar=False)
                ax2.set_aspect('equal')
                ax2.tick_params(left = False, bottom = False, labelleft = False , labelbottom = False)
                ax2.grid(False)
                ax2.set(xlim=[-1,1], ylim = [-1,1])
                ax2.plot( drawing[:,0], drawing[:,1], color = "orange" , linewidth = 1)

        else:
            ax = mapFunction(freq, np.rad2deg(head), lambda x, y: self.compute(x, np.deg2rad(y)),  ax=ax, **kwargs)
            ax.set_xlabel(r"$\omega$ $(rad/s)$")
            ax.set_ylabel("Heading (deg)")

        return ax

    def integrate_hs(self, *args, **kwargs) :
        """Compute Hs through numerical integration
        """

        return 4.004 * self.integrate_moment( 0, *args, **kwargs ) ** 0.5

    def integrate_moment(self , n , * , wmin = _wmin, wmax = None, w = None, extrap = True, limit = 200,  epsabs = 1e-4 , epsrel = 1e-4, method = "simpson", exponent = 1, w0 = 0.0 ) :
        """Get max period through numerical solver.
        
        Simpson is much faster than the adaptative method "quad" (benefit of vectorization?).


        Parameters
        ----------
        n : integer
            Moment order
        wmin : float, optional
            integration lower bound (for method=quad). The default is _wmin.
        wmax : float, optional
            integration uppper bound (for method=quad). The default is _wmax.
        w : np.ndarray, optional
            Integration point (for method = simpson). The default is None.
        extrap : TYPE, optional
            Extrapolate to infinity using spectrum tail order information. The default is True.
        limit : TYPE, optional
            Maximum number of iteration (for method=quad). The default is 200.
        epsabs : TYPE, optional
            Tolerance for in(for method=quad). The default is 1e-4.
        epsrel : TYPE, optional
            (for method=quad). The default is 1e-4.
        method : str, optional, among ("simpson" , "quad")
            Integration method. The default is "simpson".
        exponent : integer, optional
            Exponent of  Sw. The default is 1.
        w0 : float, optional
            Integrate moment with respect to w0 . The default is 0.

        Returns
        -------
        res : float
            Spectral moment
        """
        if method == "simpson" : # Simpson, default
            if w is None :
                w = _freq
            wmax = w.max()
            res = simpson( y = self.compute(w)**exponent * (w-w0)**n , x=w )
        elif method == "quad" :
            if wmax is None :
                wmax = np.inf
            res = quad( lambda x : (x-w0)**n * self.compute(x)**exponent , wmin , wmax , limit = limit, epsabs = epsabs, epsrel = epsrel )[0]
        else:
            raise(Exception(method + "not recognized"))

        extrap  = extrap and (wmax is not np.inf )

        if self.get_wmax() < wmax :
            if extrap :
                raise(Exception(f"Reduce integration range so that extrapolation starts from frequency where data are available.\n (wmax={wmax:}, while data are available up to {self.get_wmax():}"))
            else :
                logger.warning(f"Integrating beyond data range\n (wmax={wmax:}, while data are available up to {self.get_wmax():}")

        if extrap and abs(w0) < 1e-5:
            res += self.integrate_moment_tail(n=n, wmax = wmax, exponent=exponent)

        return res

    def integrate_std(self, *args , **kwargs):
        """Compute std of spectrum..
        
        (moment of order 2 with respect to mean period)
        """
        m0 = self.integrate_moment( 0  , *args , **kwargs)
        tm = self.integrate_tm(*args, **kwargs)
        return self.integrate_moment(n=2, w0 = 2*np.pi / tm, *args, **kwargs )**0.5 / m0**0.5


    def integrate_moment_tail( self, n, wmax, exponent = 1 ) :
        """Analytical integrate the moment from the tail.

        Parameters
        ----------
        n : int
            moment order
        wmax : float
            Frequency from which to integrate

        Returns
        -------
        float
            Tail integration
        """

        order = self.getTailOrder()
        if order > 1 :
            logger.info( "Moment asymptotic integration not available" )
            return 0.0
        st = self.compute(wmax)

        return -wmax**(n+1) * st**exponent / (order*exponent + 1 + n)



    def integrate_tz(self, *args, **kwargs):
        """Get mean up-crossing period through numerical integration.
        """
        return 2*np.pi * ( self.integrate_moment(0, *args, **kwargs) / self.integrate_moment(2, *args, **kwargs) )**0.5

    def integrate_tm(self, *args, **kwargs):
        """Get mean up-crossing period through numerical integration.
        """
        return 2*np.pi * ( self.integrate_moment(0, *args, **kwargs) / self.integrate_moment(1, *args, **kwargs) )

    def integrate_t0m1(self, *args, **kwargs):
        """Return mean period based on -1 moment.
        """
        return 2*np.pi * ( self.integrate_moment(-1, *args, **kwargs) / self.integrate_moment(0, *args, **kwargs) )


    def integrate_spectral_peakness(self, variant = None, **kwargs):
        r"""Compute Goda's spectral peakness.

        $$Q_P = \frac{2}{m_0^2} \int_w wS(w)^2 dw$$

        Parameters
        ----------
        variant: str
            if variant=="ECMWF", the integration is done only for the points where S(w)>0.4 S_max
            For the normal integration, no tail integration is done.
        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        peakness : double
            Goda's spectral peakness parameter

        """

        if variant is None :
            m0 = self.integrate_moment( 0, **kwargs )
            g = self.integrate_moment( 1, exponent = 2,  **kwargs )
        elif variant.lower() == "ecmwf" :
            w = kwargs.pop("w" , None)
            if w is None:
                w = np.linspace( 0.1 , 3.0 , 200 )
            dw = w[1] - w[0]
            sw = self.compute(w)
            sw_ = sw[  sw >= 0.4*np.max(sw)]
            w_ = w[ sw >= 0.4*np.max(sw) ]
            m0 = dw * np.sum( sw_ )
            g = dw * np.sum( sw_ ** 2 * w_ )
        else :
            raise(Exception( "variant {variant:} is not known. Should be among ['ecmwf' , None]" ))
        return ( 2 / m0**2) * g


    def integrate_spreading(self, variant = "ww3", wmin = _wmin, wmax = _wmax, n_theta = 101, n_freq = 100, method = "simpson" ) :
        """Return mean directional spread.

        Parameters
        ----------
        variant : str, optional
            Variant, among ('ww3', 'era5'). The default is "ww3".

        Returns
        -------
        spread : float
            Spreading (~radians).
        """

        if variant.lower() in [ "ww3" , "swan"]:
            a = self._cossin(np.cos, wmin=wmin, wmax=wmax, method=method, n_theta=n_theta, n_freq=n_freq)
            b = self._cossin(np.sin, wmin=wmin, wmax=wmax, method=method, n_theta=n_theta, n_freq=n_freq)
            m0 = self.integrate_moment(0, w=np.linspace(wmin, wmax, n_freq), extrap=False)
            return ( 2 * ( 1 - ( (a**2 + b**2) / m0**2 )**0.5)   )**0.5
        elif variant.lower() in ["era5", "ecmwf", "wam"]:
            db = 2*np.pi / n_theta
            t = np.arange( 0, 2*np.pi, db)
            freq = np.linspace( wmin, wmax , n_freq )
            I1 = 0.0
            theta_f = self.integrate_mean_directions( freq )
            for theta in t :
                sw = self.compute(freq, theta)
                integrand = np.cos( theta - theta_f ) * sw[:]
                I1 += simpson(  integrand, x=freq )
            I1 *=  db
            m0 = self.integrate_moment(0, w=np.linspace(wmin, wmax, n_freq), extrap=False)
            return np.sqrt( 2*( 1 - I1 / m0)  )
        else :
            raise(Exception( f"variant {variant:} is not known. Should be among ['ww3' , 'swan', '']" ))


    def _cossin_w( self, fun, w, db = np.deg2rad(5) ) :
        thetas = np.arange( 0, 2*np.pi, db )
        res = np.zeros( w.shape , dtype = float )
        for theta in thetas :
            sw = self.compute( w, theta )
            res += fun(theta) * sw
        return res * db

    def _cossin( self , fun, wmin = 0.1, wmax = 2.0, method = "dblquad", n_theta = 101, n_freq = 100):
        r"""Integrate wave spectrum product with function of theta.

        Parameters
        ----------
        fun : Function
            DESCRIPTION.
        wmin : float, optional
            lower bound for frequency integration. The default is 0.1.
        wmax : float, optional
            Upper bound for frequency integration. The default is 2.0.

        Returns
        -------
        res : float
            \int\int f(\theta) S(\omega, \theta) d\omega d\theta
        """

        if method == "dblquad" :
            res, err = dblquad( lambda y,x :  fun(y) * self.compute(x,y) , wmin , wmax , lambda x: 0 , lambda x: 2*np.pi  )
        elif "simps" in method.lower():
            w = np.linspace( wmin, wmax , n_freq )
            theta = np.linspace( 0., 2 * np.pi, n_theta,  endpoint=True)
            S_int = [ simpson( self.compute(w, t), x=w ) for t in theta ]
            res = simpson( fun(theta) * S_int, x=theta )
        else :
            raise(Exception(f"{method:} not recognized"))
        return res


    def integrate_dominant_direction(self, wmin = _wmin, wmax = _wmax, n_freq = 100, n_theta = 101):
        """Integrate dominant direction (also known as "principal direction), using simpson's rule.
        
        Parameters
        ----------
        wmin : float, optional
            Integration lower bound. The default is _wmin.
        wmax : float, optional
            Integration upper bound. The default is _wmax.
        n_freq : int, optional
            Number of points for the frequency integration. The default is 101.
        n_theta : int, optional
            Number of points for the heading integration. The default is 145.

        Returns
        -------
        float
            The dominant direction (in radian)
        """
        freq = np.linspace(wmin, wmax, n_freq)
        theta = np.linspace(0., 2*np.pi, n_theta)
        S_int = np.array([ simpson( self.compute(freq, t), x=freq ) for t in theta ])

        a2 = simpson( np.cos(theta*2) * S_int, x=theta )
        b2 = simpson( np.sin(theta*2) * S_int, x=theta )

        res2 = 0.5 * (np.arctan2( b2,a2 ) % (2*np.pi))
        return res2

    def integrate_mean_direction(self, **kwargs) :
        """Integrate mean wave direction. 
        
        Sometimes called Vector Mean Direction, and noted VMD.

        Returns
        -------
        float
            Mean wave direction.
        """

        if not self.isSpreaded() :
            logger.warning( "integrate_mean_direction not implemented for non spreaded seastates" )

        return np.arctan2( self._cossin(np.sin, **kwargs) , self._cossin(np.cos, **kwargs) ) % (2*np.pi)

    def integrate_mean_direction_simps( self, wmin = _wmin, wmax = _wmax, n_freq = 100, n_theta = 101 ):
        """Integrate mean wave direction with simpson method (much faster!)
        
        Sometimes called Vector Mean Direction, and noted VMD.

        Parameters
        ----------
        wmin : float, optional
            lower bound for frequency integration. The default is 0.1.
        wmax : float, optional
            Upper bound for frequency integration. The default is 2.0.
        n_freq : int, optional
            Number of points for the frequency integration. The default is 101.
        n_theta : int, optional
            Number of points for the heading integration. The default is 145.

        Returns
        -------
        float
            Mean wave direction.
        """
        freq = np.linspace(wmin, wmax, n_freq)
        theta = np.linspace(0., 2*np.pi, n_theta)
        S_int = [ simpson( self.compute(freq, t), x=freq ) for t in theta ]
        cos_int = simpson( np.cos(theta) * S_int, x=theta )
        sin_int = simpson( np.sin(theta) * S_int, x=theta )
        return np.arctan2(sin_int, cos_int) % (2*np.pi)

    def integrate_mean_directions( self, w, db = np.deg2rad(5) ):
        return np.arctan2( self._cossin_w(np.sin, w, db = db) , self._cossin_w(np.cos, w, db=db) ) % (2*np.pi)


    def find_tp(self, wmax = 5.5):
        """Get Tp numerically
        """
        init  = np.arange(0.3 , 5.5, 0.1)
        i = self.compute( init ).argmax()
        min_w = minimize( lambda x : -self.compute(x) , init[i], bounds = [ (init[i]*0.8 , init[i]*1.2) ] )
        return 2*np.pi / min_w.x[0]


    def getTp(self):
        """Get Tp, either parameter, or defined
        """
        return self.find_tp()


    def energyRange( self, energyRatio , wmin = None, wmax = None, dw = 0.001):
        """Return the smallest range allowing to keep a given energy fraction of the spectrum.

        Parameters
        ----------
        energyRatio : float
            Fraction of energy to maintain (between 0.0 and 1.0)
        wmin : float or None, optional
            Starting lower bound. The default is None.
        wmax : float or None, optional
            Starting upper bound. The default is None.
        dw : float, optional
            Frequency step. The default is 0.001.

        Returns
        -------
        tuple (float, float)
            Lower and upper bounds.
        """
        if wmin is None or wmax is None :
            wmin, wmax = self.get_wrange( energyRatio )
            wmin *= 0.9
            wmax *= 1.1

        freq = np.arange( wmin, wmax , dw )
        
        spec = self.compute( freq )

        energyTarget = (self.getHs()**2 / 16) * energyRatio / dw

        if spec.sum() < energyTarget :
            print (self.getHs() , 4. * spec.sum() * dw)
            raise(Exception( f"Not enougn energy on pre-guessed range {wmin:.1f} {wmax:.1f}" ))

        iwmin = 1
        iwmax = 1
        nbfreq = len(spec)
        itp = spec.argmax()
        while ( spec[ itp-iwmin: itp + iwmax].sum()  < energyTarget ):
            # lower bound has been reached, extend upper bound
            if (itp - iwmin == 0) :
                iwmax = iwmax + 1
            # upper bound has been reached, extend lower bound
            elif itp + iwmax == nbfreq-1 :
                iwmin = iwmin + 1

            # no bound was reached, extend lower bound if it gives more or same amount of energy than upper bound
            elif ( spec[itp - iwmin - 1] >= spec[itp + iwmax + 1]) :
                iwmin = iwmin + 1
            # no bound was reached, extend upper bound if it gives more energy than lower bound
            else:
                iwmax = iwmax + 1

        return freq[itp - iwmin], freq[itp + iwmax]


    def getNormalized(self, wa = None, period = "t0m1", w_ref = None, hs_ref = None) :
        """Normalize the sea-state spectrum.

        Parameters
        ----------
        wa : np.ndarray, optional
            Discretisation of the normalised, tabulated, spectrum.
        period : str, optional
            Period type used to normalise the spectrum. The default is "tm01".
        w_ref : float, optional
            If specified, this frequency is used to normalize the spectrum
        hs_ref : float, optional
            If specified, this significant wave height is used to normalize the spectrum

        Returns
        -------
        sp.WaveTabulatedSpectrum
            The normalised spectrum
        """
        if wa is None :
            wa = np.linspace( 0.2, 3.0, 200 )

        if w_ref is None : 
            if period == "t0m1":
                w_ref = 2*np.pi / self.integrate_t0m1()
            elif period == "tp":
                w_ref = 2*np.pi / self.find_tp()
            elif period == "tm":
                w_ref = 2*np.pi / self.integrate_tm()
            elif period == "tz":
                w_ref = 2*np.pi / self.integrate_tz()
            elif period is None:
                w_ref = 1.0
             
        if hs_ref is None : 
            m0 = self.integrate_moment(0)
        else : 
            m0 = hs_ref**2/16.

        sw_n = self.compute( wa * w_ref ) /  m0 * w_ref
        
        return sp.WaveTabulatedSpectrum(  wa , sw_n )


    def getNormalized_heading(self, head = np.arange( 0., 2*np.pi, np.deg2rad(5) )) :
        m0 = self.integrate_moment(0)
        spread = self.computeSpreading( head )

        se = pd.Series( index = np.mod( np.pi + head - self.integrate_mean_direction(), 2*np.pi),  data = spread / m0  )
        return se.sort_index()

    def get_wmax(self):
        NotImplementedError

    def integrate_eps(self, **kwargs):
        """Compute bandwith parameter.

        Warning : for most of the spectrum, m4 does not converge!

        Truncated eps might sometime be used, then wmax and extrap = False should be passed as argument!

        Parameters
        ----------
        **kwargs : **dict
            Parameters passed to .integrate_moment()

        Returns
        -------
        float
            Eps bandwith parameter
        """
        m0 = self.integrate_moment( 0, **kwargs )
        m2 = self.integrate_moment( 2, **kwargs )
        m4 = self.integrate_moment( 4, **kwargs )

        return (1-m2**2 / (m0*m4))**0.5



class SeaState( SeaStateABC, _Spectral.SeaState ):
    """Parametric , or Semiparametric seastates.
    """

    def __hash__(self) :
        hash_ = 0
        for ispec in range(self.getSpectrumCount()):
            spec = self.getSpectrum(ispec)
            print (self.getSpectrum(ispec))
            if isinstance(  self.getSpectrum(ispec) , sp.Spectrum) :
                hash_ ^= spec.__hash__()
            else :
                raise(Exception("__hash__ not implemented"))
        return hash_


    def getTp(self):
        if self.getType() == sp.SeaStateType.Parametric :
            tpList = np.array( [ self.getSpectrum(i).tp for i in range(self.getSpectrumCount()) ] )
            return tpList[  self.compute(tpList).argmax() ]
        else :
            return self.find_tp()

    def get_wmax(self):
        if self.getType() == sp.SeaStateType.Parametric :
            return 99.
        elif self.getType() == sp.SeaStateType.SemiParametric :
            return np.max([ np.max(self.getSpectrum(i).w) for i in range(self.getSpectrumCount()) ])


    def get_wrange( self, energyRatio = 0.99):
        """Return range to get the main part of the wave spectrum.
        
        More precise range can be obtained with .energyRange()

        Parameters
        ----------
        energyRatio : float, optional
            Approximate amount of energy to be preserved. The default is 0.99.

        Returns
        -------
        tuple
            Frequency range
        """
        if self.getType() in [sp.SeaStateType.Parametric, sp.SeaStateType.SemiParametric] :
            lim = np.array([ self.getSpectrum(i).get_wrange(energyRatio) for i in range(self.getSpectrumCount()) ] )
            return np.min( lim[:,0] ) , np.max( lim[:,1] )
        else :
            logger.warning("Warning, get_wrange is constant for 2D spectrum")
            return 0.2,  2.0


    @classmethod
    def Jonswap( cls, hs=1.0, tp=10.0, gamma = 1.0 , heading=np.pi , spreading_type = sp.SpreadingType.No, spreading_value = 2.0  ):
        """Convenience routine to create a seastate with a single Jonswap spectrum.

        Parameters
        ----------
        hs : float, optional
            Significant wave height. The default is 1.0.
        tp : float, optional
            Peak period. The default is 1.0.
        gamma : float, optional
            Gamma. The default is 1.0.
        heading : float, optional
            Wave heading (in radians). The default is np.pi.
        spreading_type : int, optional
            Spreading Type. The default is sp.SpreadingType.No.
        spreeading_value : TYPE, optional
            Speading parameter value. The default is 2.0.

        Returns
        -------
        SeaState
            Jonswap sea state
        """
        return cls(  sp.Jonswap( hs, tp, gamma ,heading, spreading_type, spreading_value) )


    def __str__(self):
        return "|".join( [ spec.__str__() for spec in self.spectrums ] )


    @property
    def spectrums(self):
        return [ self.getSpectrum(i) for i in range(self.getSpectrumCount())]

    def check(self):
        """Check if the sea-state if plausible.
        """
        for spec in self.spectrums:
            if not sp.ParametricSpectrum.check( spec ) :
                return False

        return True


    def __getstate__(self):
        return [ self.spectrums , self.probability ]

    def __setstate__(self, t):
        self.__init__( t[0], t[1] )

    def hspecString(self, filename=None) :
        """Return the StarSpec string.

        Parameters
        ----------
        filename : str, optional
            File where to write the tabulated data. The default is None.

        Returns
        -------
        str
            Description of the sea-state, StarSpec syntax.
        """
        
        #Fully parametric case :
        if self.getType() == sp.Parametric :
            str_ = " ".join( [self.getSpectrum(iSpec).__str__().upper().replace("HEADING", "WHEADING") for iSpec in range(self.getSpectrumCount()) if (self.getSpectrum(iSpec).getHs()>1.e-5 and self.getSpectrum(iSpec).getTp()>1.e-5)] )
            return str_.replace( "Pierson-Moskowitz".upper(), "JONSWAP GAMMA 1.0")

        #Semi-parametric case :
        elif self.getType() == sp.SeaStateType.SemiParametric:
            nmode = self.getSpectrumCount()
            if nmode == 1:
                sp.WaveTabulatedSpectrum.hspecString( self.getSpectrum(0) , filename = filename )
                return "SPECTRUMFILE {}".format(filename)
            else:
                logger.warning("StarSpec export for multi-modal tabulated spectrum is not fully tested (in both Snoopy and StarSpec)")
                fname_ , ext = os.path.splitext(filename)
                sList = []
                for ispec in range(nmode):
                    fname = f"{fname_:}_{ispec:03}.{ext:}"
                    sp.WaveTabulatedSpectrum.hspecString( self.getSpectrum(ispec) , filename = fname )
                    sList.append(  "SPECTRUMFILE {}".format(fname) )
                return "\n".join(sList)

        else :
            raise(Exception("Should not happen..."))


    @classmethod
    def FromHspecString( cls, line ) :
        """Create sea-state from string (Starspec generic format).

        Parameters
        ----------
        line : str
            StarSpec spectrum definition, for instance "JONSWAP HS 1.0 TP 10.0  GAMMA 1.0 WHEADING 180."

        Returns
        -------
        sp.SeaState
            Snoopy seastate
        """

        #Split line by spectrum
        specList = re.split( r'(JONSWAP\s+|WALLOP\s+|GAUSS\s+|GAMMASPEC\s+|SIMPLEOCHIHUBBLE\s+)' , line )[1:]
        l = [ specList[2*i] + specList[2*i+1] for i in range(int(len(specList) / 2)) ]
        return cls( [ sp.Spectrum.FromHspecString( s ) for s in l ] )


    def getCoefsDict(self) :
        d = {}
        if self.getType() == sp.SeaStateType.Parametric :
            for iSpec, spec in enumerate(self.spectrums) :
                c = spec.getCoefs()
                names = spec.getCoefs_name()
                for i, name, in enumerate(names) :
                    d[ "{}_{}".format(name, iSpec)] = c[i]
                    d[ "{}_{}".format("Heading", iSpec)] = spec.heading
                #d[ "{}_{}".format("sprt", iSpec)] = spec.spreading_type
                d[ "{}_{}".format("sprv", iSpec)] = spec.getSpreadingValue()

        return d


class SeaState2D_Fourier( SeaStateABC, _Spectral.SeaState2D_Fourier ):

    @classmethod
    def From_NDBC( cls, w, a0 , alpha1 , alpha2, r1 , r2, probability = -1 ):
        r"""Construct Seastate from alpha and r coefficient (NDBC variables).

        "NDBC" parametrisation :
        $S(\omega,\theta) = (a0 / (np.pi)) * ( 0.5 + r_1 * cos( \theta - \alpha_1) + r_2 * cos( 2(\theta - \alpha_2) ) )$

        "Classic" parametrisation
        $S(\omega,\theta) = (a0 / (np.pi)) * ( 0.5 + a1 * cos( \theta ) + b1 * sin( \theta ) + a2 * cos( 2*\theta ) + b2 * sin( 2*\theta ))$

        Parameters
        ----------
        w : np.ndarray
            Frequencies (in rad/s).
        a0 : np.ndarray
            a0 (per rad/s, NDBC a0 has to be divided by 2*pi before).
        alpha1 : np.ndarray
            alpha1.
        alpha2 : np.ndarray
            alpha2.
        r1 : np.ndarray
            r1.
        r2 : np.ndarray
            r2.
        probability : float, optional
            Sea-state probability. The default is -1.

        Returns
        -------
        sp.SeaState_Fourier
            The seastate
        """

        a1 = r1 * np.cos( alpha1 )
        b1 = r1 * np.sin( alpha1 )

        a2 = r2 * np.cos( 2*alpha2 )
        b2 = r2 * np.sin( 2*alpha2 )
        return cls( w, a0, a1, b1, a2, b2 , probability = probability )


    def get_wmax(self):
        return np.max(self.w)


class SeaState2D( _Spectral.SeaState2D, SeaStateABC ):

    @classmethod
    def FromDataFrame( cls, df, ndir = None ):
        """Build 2D tabulated spectrum from pandas DataFrame. 

        Handle the heading ends
        df columns are interpreted as heading. Headings need to be equally spaced
        df index as frequency

        Parameters
        ----------
        ndir : int
            The number of desired directions in interval [0°, 360°) (including 0° and excluding 360°)

        Returns
        -------
        sp.SeaState2D
            The seastate
        """
        df_ = df.copy()
        df_.sort_index(axis=1, inplace=True) # make sure headings are ascending

        # convert to degrees, round and reconvert to radians in order to avoid numerical problems
        df_.columns = np.deg2rad(np.round(np.rad2deg(df_.columns), 10))

        #check if heading step is constant
        if not np.allclose(np.diff(df_.columns), np.diff(df_.columns)[0], rtol = 1.e-5):
            raise ValueError("2D spectrum wave directions need to be equally spaced")

        if not np.isclose(2*np.pi, df.columns, rtol = 1.e-5).any() and not np.isclose(0., df.columns, rtol = 1.e-5).any():
            # interpolate between first and last direction to find 0° and 360°
            linearfit = interp1d([df_.columns[-1]-2*np.pi,df_.columns[0]], np.vstack([df_.iloc[:, -1].values, df_.iloc[:, 0].values]), axis=0) # create fit between last and first direction
            df_.loc[:,0.]    = linearfit(0.)   # set 0°
            df_.loc[:,2*np.pi] = df_.loc[:,0.] # set 360°
        elif np.isclose(0., df.columns, rtol = 1.e-5).any():
            df_.loc[:,2*np.pi] = df_.iloc[:,0].values # use iloc because small values sucha as 1.e-14 value are not recognized (Key error)

        elif np.isclose(2*np.pi, df.columns, rtol = 1.e-5).any():
            df_.loc[:,0.] = df_.iloc[:,-1]

        df_.sort_index(axis=1, inplace=True)
        if ndir is None:
            ndir = df_.shape[1]-1

        # if ndir doesn't match number of dirs in dataframe or dirs aren't equally spaced then interpolation is needed.
        if ndir != df_.shape[1]-1 or (not np.allclose(np.diff(df_.columns), np.diff(df_.columns)[0], rtol = 1.e-5)):

            # interpolate to have iso direction starting at 0° and ending at 360° (required by Snoopy)
            new_head = np.linspace( 0 , 2*np.pi , ndir+1, endpoint=True) # final number of direction will include 360°

            for h in new_head[1:-1]:
                if not np.isclose(h, df_.columns, rtol = 1.e-10).any(): df_[h] = np.nan # add missing columns in order to have regular step

            df_.sort_index(axis=1, inplace=True)
            df_.interpolate(inplace = True, axis = 1, method='index') #linear interpolation using the actual column values
            df_ = df_.clip(lower=0.)

            df_.drop([h for h in df_.columns if not np.isclose(h, new_head, rtol = 1.e-10).any()], axis = 1, inplace=True)

        return cls( w = df_.index, b = df_.columns, sw = df_.values )

    def convert_convention(self, convention_in, convention_out, vessel_azimuth = None, vessel_azimuth_out = None):
        """Change seastate heading convention.

        meteorological: 0° means "coming from north" and 90 "coming from east" (=StarSpec)
        oceanographic: 0° means "going to north" and 90 "going to east"

        Parameters
        ----------
        convention_in : str
            Current convention. Among [ "oceanographic", "meteorological", "local" , "starspec"]
        convention_out : str
            Output convention. Among [ "oceanographic", "meteorological", "local" , "starspec"]
        vessel_azimuth : float, optional
            Azimuth in case output convention is "local". The default is None.

        Returns
        -------
        sp.SeaState2D
            The sea-state with heading convention set to "convention_out"
        """

        df = self.toDataFrame()
        df = df.iloc[:, :-1]  # discard 360° heading to avoid duplicates when converting

        if ( convention_in in ["starspec", "meteorological"] and convention_out == "oceanographic") or ( convention_out in ["starspec", "meteorological"] and convention_in == "oceanographic"):
            df.columns = (df.columns-np.pi) % (2*np.pi)

        elif (convention_in in ["starspec", "meteorological"] and convention_out == "local"):
            if vessel_azimuth is None:
                raise(Exception(f"Vessel azimuth should be provided when converting from {convention_in} to {convention_out}"))
            df.columns = sp.headingConvention.local_from_wave_and_vessel( df.columns, vessel_azimuth, convention = "starspec") % (2*np.pi)

        elif (convention_in in ["starspec", "meteorological"] and convention_out in ["starspec", "meteorological"]):
            if vessel_azimuth is None or vessel_azimuth_out is None:
                raise(Exception(f"Current azimuth of the vessel and new azimuth should be provided when converting from {convention_in} to {convention_out}"))
            df.columns = sp.headingConvention.get_new_wave_heading( df.columns, vessel_azimuth, vessel_azimuth_out, convention = "starspec")

        else :
            raise(Exception("Conversion not handled"))

        df.sort_index(axis=1, inplace=True)

        return SeaState2D.FromDataFrame(df)


    def to_csv(self , filename) :
        """Write spectrum to csv file
        
        Parameters
        ----------
        filename : str
            file name
        """
        self.toDataFrame().to_csv(filename)

    def get_wmax(self):
        return np.max(self.w)
    
    
    def get_wrange( self, energyRatio = 0.99):
        """Simply return the frequency bounds in which the discrete sea state is defined.
        """
        return np.min(self.w), np.max(self.w)

    @classmethod
    def Read_csv(cls , filename) :
        """Read 2D seastate from a csv file.
        
        Parameters
        ----------
        filename : str
            file name
        """
        df = pd.read_csv(filename, index_col=0)
        df.columns = df.columns.astype(float)
        return cls.FromDataFrame( df )

    def toDataFrame(self):
        """Store 2D SeaState in a pandas dataframe.
        
        Returns
        -------
        pd.DataFrame
            2D tabulated spectrum as dataframe
        """
        return pd.DataFrame( index = self.w , columns = self.b , data = self.sw )

    def to_1D(self, heading = 0.) :
        """
        Return 1D tabulated seastate
        """
        return sp.SeaState(  sp.WaveTabulatedSpectrum(  w = self.w , sw = self.compute(self.w) , heading = heading )  )


    def toMultiModal(self ) :
        """Convert 2D sea-state to multi-modal unidirectional tabulated spectra

        Useful to use use routines that may not be directy able to deal with 2D spectral.

        For now, no interpolation is performed. Only original data from the 2D spectra is used.

        Returns
        -------
        sp.SeaState
            Seastate with multiple spectra, equivalent to the 2D seastate
        """
        dim = 2*np.pi / len(self.b[:-1])
        specList = [sp.WaveTabulatedSpectrum( self.w , dim*self.sw[:,ib] , b) for ib , b in enumerate(self.b[:-1]) ]
        return sp.SeaState( specList )


    def hspecString( self, filename):
        """Write to StarSpec format.

        Write sea-state in a separated file, and the command line that refers to this file
        Note : For now, SeaState2D has duplicate ending (0 and 360). Only one should be included in StarSpec!
        """

        with open( filename, "w") as f :
            f.write( "w " + " ".join( "{:.4f}".format(w) for w in self.w )  + "\n")
            for ib, b in enumerate(self.b[:-1]) :
                f.write(  "{:.1f} ".format( np.rad2deg(b) )  + " ".join( "{:.4e}".format(self.sw[iw , ib]) for iw in range( len(self.w))))
                f.write("\n")

        return "SPECTRUM3D " + filename

    @classmethod
    def fromHspecString(cls , filename) :
        """Read seastate from StarSpec format.

        Parameters
        ----------
        cls : SeaState2D
            2D sea state.
        filename : string
            full path to file containing sea state in StarSpec format.

        Returns
        -------
        SeaState2D
            2D sea state.
        """

        # attention: in StarSpec format freq are in columns and headings in rows, therefore dataframe needs to be transposed
        df = pd.read_csv(filename, index_col=0, sep = None, engine = 'python')
        df.columns = df.columns.astype(float)
        df.index   = np.deg2rad(df.index.astype(float))
        df = df.T
        return cls.FromDataFrame( df )

    def getMax1D(self):
        """Return number of local maxima of the 1D spectrum.

        Very raw attempt to get number of components
        """
        sw = self.compute(self.w)
        isig = np.where(sw > sw.max()*0.1)
        diff = np.diff( sw[isig] )
        wMax = [ self.w[isig][ij+1] for ij in range(len(diff)) if (diff[ij] > 0 and diff[ij+1] < 0) ]
        swMax = [ self.w[isig][ij+1] for ij in range(len(diff)) if (diff[ij] > 0 and diff[ij+1] < 0) ]
        return pd.DataFrame( index = wMax, data = {"sw":swMax} )

    def _cossin( self , fun, **kwargs ):
        r"""Integrate wave spectrum product with function of theta.

        Parameters
        ----------
        fun : Function
            DESCRIPTION.
        wmin : float, optional
            lower bound for frequency integration. The default is 0.1.
        wmax : float, optional
            Upper bound for frequency integration. The default is 2.0.

        Returns
        -------
        res : float
            \int\int f(\theta) S(\omega, \theta) d\omega d\theta
        """
        t = np.sum( self.sw[ : , :-1 ] * fun( self.b[:-1] ) * self.getDb(), axis = 1 )
        return simpson( t, x=self.w)


    def getDb(self) :
        return self.b[1]-self.b[0]

    def find_tp(self, wmax=5.5, interp="spline"):
        if interp == "spline":
            freq = self.w
            values_data = np.sum(self.sw, axis=1)
            spline = interpolate.InterpolatedUnivariateSpline(freq, values_data)
            i = values_data.argmax()  # to get a first estimation of the highest value
            maximumValue = minimize_scalar(lambda x: -spline(x), bounds=[freq[i-2] , freq[i+2]], method='bounded')
            value = maximumValue.x
        else:  # linear interpolation
            i = np.sum(self.sw, axis=1).argmax()
            value = self.w[i]
        return 2*np.pi / value


if __name__ == "__main__":


    wave_heading = np.deg2rad(90)
    vessel_azimuth = np.pi
    vessel_azimuth_out = np.pi/4+0.05
    convention = "starspec"


    ss = SeaState([
        _Spectral.Jonswap(hs=1.01, tp=10.0, gamma=3.0, heading=np.deg2rad(180.), spreading_type=_Spectral.SpreadingType.Cosn, spreading_value=5.),
        _Spectral.Jonswap(hs=1.0, tp=10.0, gamma=3.0, heading=np.deg2rad(0.), spreading_type=_Spectral.SpreadingType.Cosn, spreading_value=5.),
            ])

    ss = sp.SeaState2D(ss)
    self = ss
    
    dmdir = self.integrate_dominant_direction()
    vmd = self.integrate_mean_direction()
    
    print (wave_heading, np.rad2deg(vmd) , np.rad2deg(dmdir))
    
    
    
    

    
    # ss_loc = ss.convert_convention(convention_in = "starspec", convention_out = "local", vessel_azimuth=vessel_azimuth)
    # ss.plot2D(n=100, cmap="viridis", polar = True, vessel = True, heading_convention = convention, vessel_azimuth=vessel_azimuth).set(title = "Starspec convention")
    # ss_loc.plot2D(n=100, cmap="viridis", polar = True, vessel = True, heading_convention = "local").set(title = "Local convention")

    # ss_SFA = ss.convert_convention(convention_in = "starspec", convention_out = "starspec", vessel_azimuth=vessel_azimuth,vessel_azimuth_out=vessel_azimuth_out)
    # ss_SFA.plot2D(n=100, cmap="viridis", polar = True, vessel = True, heading_convention = convention, vessel_azimuth=vessel_azimuth_out).set(title = f"Starspec convention with new azimuth = {np.rad2deg(vessel_azimuth_out):.1f}°")


