import numpy as np
from matplotlib import pyplot as plt
from scipy.integrate import quad, simpson
from scipy.optimize import minimize, root_scalar
from scipy.stats import weibull_min
from Snoopy import logger
from Snoopy import Statistics as st
import _Spectral
from . import w2k
from enum import Enum


class SpectrumType(Enum) :
    """Wave spectrum types.
    """

    Wallop      =  1
    Gauss       =  3
    Jonswap     = 4
    WhiteNoise  =  8
    Gamma = 9
    Torsethaugen = 15
    SimpleTorsethaugen = 16
    SimpleOchiHubble = 6
    PiersonMoskowitz = 21
    WaveTabulatedSpectrum = 20
    WaveTabulatedSpectrumOneParam = 30
    LogNormal = 24



availableWindSpectra = ["API",
                        "Davenport",
                        "Harris",
                        "Hino",
                        "Kaimal",
                        "Kareem",
                        "ModifiedHarris",
                        "NPD",
                        "OchiShin",
                        "Queffeulou"]

availableWaveSpectra = list(SpectrumType.__members__.keys())

availableSpectra = availableWindSpectra + availableWaveSpectra

def wConvert( w , target , depth = 0) :
    if target == "lambda" :
        return 2*np.pi / w2k(  w , depth = depth )
    elif target == "T" :
        return 2*np.pi / w
    else :
        return w


class Spectrum() :

    def __hash__(self):
        raise(NotImplementedError)



    def plot(self, ax=None, xAxis="w", wMin=None, wMax=None, n = 200 , energy_ratio=None, *args, **kwargs):
        """Plot spectrum against frequency (integrated over all headings).

        Parameters
        ----------
        ax : plt.ax, optional
            ax where to plot. If None, the ax is created. The default is None.
        xAxis : str, optional
            x axis (among "w", "T", "lambda"). The default is "w".
        wMin : float, optional
            minimum frequency. The default is None.
        wMax : axis, optional
            maximum frequency. The default is None.
        n : integer, optional
            Frequency discretisation. The default is 200
        energyRange : float, optional
            plot energy range. The default is None.

        *args :
            Arguments pass to ax.plot
        **kwargs :
            Arguments pass to ax.plot

        Returns
        -------
        ax : ax
            ax containing the plot.
        """
        if ax is None :
            _, ax = plt.subplots()

        if wMin is None or wMax is None :
            _wMin, _wMax = self.get_wrange(0.95)
            _wMin*=0.8
            _wMax*=1.2
            if energy_ratio is not None :
                _wMin, _wMax = self.energyRange(energy_ratio, wMin*0.8, wMax*1.2)
            if wMax is None : wMax = _wMax
            if wMin is None : wMin = _wMin

        w = np.linspace(wMin, wMax , n)

        spec = self.compute( w )
        ax.plot( wConvert(w , xAxis) , spec , *args, **kwargs)
        ax.set_ylim( bottom = 0. )
        ax.set_xlabel( r"$\omega$ $(rad/s)$" )
        ax.set_ylabel( r"Wave spectral density ($\frac{m^2}{rad/s}$)" )


        return ax

    @staticmethod
    def _findSpectrumClassName(string):
        """Handle case difference between Hspec keywords and spectrum class name
        """
        for i in availableSpectra :
            if string.lower() == i.lower() :
                return i
        else :
            raise( Exception( f"Spectrum {string:} is not available" ) )



    @classmethod
    def _findCoefNames( cls, string ) :
        """Return the snoopy argument names that corresponds to the string
        
        Example
        -------
        >>> sp.Jonswap._findCoefNames( "GAMMA")
        >>> 'gamma'
        >>> sp.Jonswap._findCoefNames( "GAdsdMMA")
        >>> # ==> None
        """
        for i in cls.getCoefs_name() :
            if string.lower() == i.lower() :
                return i
            if "heading" in string.lower() :
                return "heading"
        else :
            return None
            #raise( Exception( f"Spectrum {string:} is not available" ) )

    @classmethod
    def FromHspecString(cls, line ) :
        """Create spectrum from string (Starspec generic format)

        Parameters
        ----------
        line : str
            StarSpec spectrum definition, for instance "JONSWAP HS 1.0 TP 10.0  GAMMA 1.0 WHEADING 180."

        Returns
        -------
        sp.Spectrum
            Snoopy spectrum
        """
        logger.debug("WARNING: FromHspecString: Heading might be interpreted as relative, depending on Spectrum use")
        from Snoopy import Spectral as sp
        l = [i.strip() for i in line.split()]
        specClass = getattr( sp, cls._findSpectrumClassName( l[0]) )

        kwargs = {}
        for i in range( len(l) ):
            c = specClass._findCoefNames( l[i] )
            if c is not None  :
                v = float(l[i+1])
                if c == "heading" :
                    v = np.deg2rad(v)
                kwargs[c] = v
            elif l[i].lower() == "cosn":
                kwargs["spreading_type"] = sp.SpreadingType.Cosn
                kwargs["spreading_value"] = float( l[i+1] )
            elif l[i].lower() == "cos2s":
                kwargs["spreading_type"] = sp.SpreadingType.Cos2s
                kwargs["spreading_value"] = float( l[i+1] )
            elif l[i].lower() == "wnormal":
                kwargs["spreading_type"] = sp.SpreadingType.Wnormal
                kwargs["spreading_value"] = np.deg2rad(float( l[i+1] ))

        return specClass( **kwargs )


    def fitSpectrumShape( self , spectrumModel , coefs_0 = None, w = None  ):
        """Fit a single spectrum, keeping Hs and Tp fixed, using least square.

        Parameters
        ----------
        spectrumModel : Spectral.Spectrum
            Spectrum model to fit
        coefs_0 : array like
            Starting guess.

        Returns
        -------
        sp.Spectrum
            Fitted spectrum

        Example
        -------
        >>> fittedSpec = spec.fitParametric1D( Jonswap )
        """

        # TODO : check that first two parameters are hs and tp
        hs = self.getHs()
        tp = self.getTp()

        if w is None :
            w = np.arange(0.1, 3.0 , 0.005)

        target = self.compute(w)

        coefs_0 = spectrumModel.getCoefs_0()[2:]

        def errFunc(coefs):
            ss = spectrumModel( hs , tp , *coefs)
            if not ss.check() :
                err = np.sum((target[:])**2)
                return 100 + 100*err
            err = np.sum((target[:] - ss.compute( w ))**2)
            return err

        coefs = minimize(errFunc, coefs_0, method = "Powell", options = {"maxiter" : 20} ).x

        try :
            return spectrumModel( hs , tp , *coefs )
        except :# Deal with scipy < 1.4 which does not return list when optimizing on a single variable.
            logger.warning( f"Scipy 1.3 still supported, but updating is recommended\n{type(coefs):}, {coefs:}" )
            return spectrumModel( hs , tp , coefs )



    def integrate_hs(self, *args, **kwargs) :
        """Compute Hs through numerical integration
        """
        return 4.004 * self.integrate_moment( 0, *args, **kwargs ) ** 0.5

    def integrate_moment(self , n , wmin = 0.001, wmax = 5.0 , limit = 200,  epsabs = 1e-4 , epsrel = 1e-4, extrap = True, **kwargs ) :
        """Integrate spectral moments of order n.

        Parameters
        ----------
        n : int
            Moment order
        wmin : float, optional
            Lower bound for integration. The default is 0.001.
        wmax : TYPE, optional
            Upper bound for integration.. The default is 5.0.
        limit : int, optional
            Maximum number of integration iteration. The default is 200.
        epsabs : float, optional
            Absolute tolerance for integration. The default is 1e-4.
        epsrel : float, optional
            Relative tolerance for integration. The default is 1e-4.
        extrap : bool, optional
            Extrapolate integation using spectrum asymptotic behavior. The default is True.
        **kwargs :
            Argument passed do scipy.integrate.quad.

        Returns
        -------
        res : float
            Moment
        """

        res = quad( lambda x : x**n * self.compute(x) , wmin , wmax , limit = 200, epsabs = epsabs, epsrel = epsrel, **kwargs )[0]
        if extrap :
            if self.tailOrder > 0 :
                logger.warn("Spectrum tail order not known, moment integration is truncated")
            else :
                res += self.integrate_moment_tail( n=n , wmax = wmax )
        return res

    def integrate_moment_tail(self, n, wmax):
        """Analitically integrate the tail of the spectrum, using  asymptotic slope.

        Parameters
        ----------
        n : integer
            Moment order
        wmax : float
            Frequency above which to integrate

        Returns
        -------
        float
            The tail integration.
        """
        st = self.compute(wmax)
        return -wmax**(n+1) * st / (self.tailOrder + 1 + n)
        

    def extrap(self, w, wmax):
        st = self.compute(wmax)
        return st  / w**(self.tailOrder)


    def integrate_tz(self, *args, **kwargs):
        """Get mean up-crossing period through numerical integration.
        """
        return 2*np.pi * ( self.integrate_moment(0, *args, **kwargs) / self.integrate_moment(2, *args, **kwargs) )**0.5

    def integrate_tm(self, *args, **kwargs):
        """Get mean up-crossing period through numerical integration
        """
        return 2*np.pi * self.integrate_moment(0, *args, **kwargs) / self.integrate_moment(1, *args, **kwargs)


    def find_tp(self, wmax = 5.5):
        """Get Tp numerically.
        """
        init  = np.arange(0.3 , 5.5, 0.1)
        i = self.compute( init ).argmax()
        min_w = minimize( lambda x : -self.compute(x) , init[i], bounds = [ (init[i]*0.8 , init[i]*1.2) ] )
        return 2*np.pi / min_w.x[0]

    def getSt_tp(self):
        """Return peak period based steepness.
        """
        return self.getHs()*2*np.pi / (9.81 * self.getTp()**2 )

    def getForristallCrestDistribution(self, depth = 0) :
        alpha, beta = self.getForristall_alpha_beta(depth = depth)
        return weibull_min(  beta, 0. , alpha * self.getHs() )


    def getLinearCrestDistribution(self, depth = 0) :
        """Return crest height distribution, assuming linearity (Rayleigh).
        """
        return st.rayleigh_c( self.getHs() / 4 )
        #Much slower :
        #return rayleigh( scale = self.getHs() / 4 )
        #return weibull_min(  2.0, 0. , self.getHs() / 8**0.5 )

    def plotCrestDistribution(self, p_min = 1e-4, ax = None, adimHs = True):

        if ax is None :
            fig, ax = plt.subplots()

        if adimHs :
            adimHs = self.getHs()
            ax.set_xlabel("Crest / Hs")
        else :
            adimHs = 1
            ax.set_xlabel("Crest (m)")

        prange = np.logspace( np.log10(p_min), 1, 50 )
        ax.plot( self.getLinearCrestDistribution().isf(prange) / adimHs, prange, label = "Linear" )
        ax.plot( self.getForristallCrestDistribution().isf(prange) / adimHs, prange, label = "Forristall")
        ax.set_yscale("log")
        ax.set_ylabel("Exceedance probability")
        ax.legend()
        return ax

    @classmethod
    def FromStd( cls , hs , tp , std , *, integration_kwds = {}  , **kwargs):
        param = cls.getCoefs_name()
        if len(param) != 3 or param[0] != "hs" or param[1] != "tp":
            raise(Exception( "FromStd only available for spectrum parametrized with Hs, Tp and one shape parameter" ))

        s_min, s_max = cls.getCoefs_min()[2], cls.getCoefs_max()[2]

        logger.debug( f"{s_min:}, {s_max:}" )

        res = root_scalar( lambda shape : cls( hs , tp , shape ).integrate_std( **integration_kwds ) - std , bracket = [ s_min, s_max ]  )


        return cls( hs , tp , res.root, **kwargs )


    @classmethod
    def FromPeakness( cls , hs , tp , peakness , *, integration_kwds = {}  , **kwargs):

        param = cls.getCoefs_name()
        if len(param) != 3 or param[0] != "hs" or param[1] != "tp":
            raise(Exception( "FromStd only available for spectrum parametrized with Hs, Tp and one shape parameter" ))

        s_min, s_max = cls.getCoefs_min()[2], cls.getCoefs_max()[2]

        res = root_scalar( lambda shape :  cls( hs , tp , shape ).integrate_spectral_peakness( **integration_kwds ) - peakness , bracket = [ s_min, s_max ]  )

        return cls( hs , tp , res.root, **kwargs )


    def integrate_spectral_peakness(self , *args, **kwargs):
        from Snoopy import Spectral as sp
        return sp.SeaState( self ).integrate_spectral_peakness( *args, **kwargs )

    def integrate_std(self , *args, **kwargs):
        from Snoopy import Spectral as sp
        return sp.SeaState( self ).integrate_std( *args, **kwargs )

    def getSerializable(self):
        if hasattr(self, "getSpreadingType") and hasattr(self, "getSpreadingValue"):
            return (self.__class__.__name__,) +  tuple(self.getCoefs()) +\
               (self.heading, int(self.getSpreadingType()), self.getSpreadingValue())
        else:
            return (self.__class__.__name__,) +  tuple(self.getCoefs()) + (self.heading,)

    def __eq__(self, other):
        return self.getSerializable() == other.getSerializable()

    def __neq__(self, other):
        return self.getSerializable() != other.getSerializable()


class ParametricSpectrum(Spectrum):

    #Make the spectra pickable
    def __setstate__(self, t) :
        self.__init__( *t[0], t[1] , t[2], t[3] )

    def __hash__(self):
        #TODO : pass in c++ to have it with seastate.getSpectrum()
        a = tuple(self.__getstate__()[0]) + tuple(self.__getstate__()[1:])
        return hash( a )


    def check(self):
        """ Check if the spectrum if plausible.
        TODO : move in cpp
        """
        #Check steepness
        try :
            if self.getSt() > 0.2 :
                return False
        except :
            pass
        #Check coefficient
        if ( np.array(self.getCoefs()) > np.array(self.getCoefs_max())).any() :
            return False
        if ( np.array(self.getCoefs()) < np.array(self.getCoefs_min())).any() :
            return False

        #Check spreading
        if type(self.spreading) != _Spectral.NoSpread :
            if self.spreading.value < self.spreading.getMinCoef() or self.spreading.value > self.spreading.getMaxCoef():
                return False
            #Avoid too narrow spreading (accuracy issue with regards to standard step size)
            if self.spreading.getStd() < np.deg2rad( 5. ):
                return False

        return True

    def hspecString(self):
        return ( self.__str__().replace("HEADING", "WHEADING") ).upper()


#TODO : replace by loop over available spectra
# Wind Spectra
class API(_Spectral.API, Spectrum):
    pass

class Davenport(_Spectral.Davenport, Spectrum):
    pass

class Harris(_Spectral.Harris, Spectrum):
    pass

class Hino(_Spectral.Hino, Spectrum):
    pass

class Kaimal(_Spectral.Kaimal, Spectrum):
    pass

class Kareem(_Spectral.Kareem, Spectrum):
    pass

class ModifiedHarris(_Spectral.ModifiedHarris, Spectrum):
    pass

class NPD(_Spectral.NPD, Spectrum):
    pass

class OchiShin(_Spectral.OchiShin, Spectrum):
    pass

class Queffeulou(_Spectral.Queffeulou, Spectrum):
    pass

# Wave Spectra
class SimpleOchiHubble(_Spectral.SimpleOchiHubble, ParametricSpectrum) :
    __doc__ = _Spectral.SimpleOchiHubble.__doc__

class SimpleTorsethaugen(_Spectral.SimpleTorsethaugen, ParametricSpectrum) :
    __doc__ = _Spectral.SimpleTorsethaugen.__doc__

class Gamma(_Spectral.Gamma, ParametricSpectrum) :
    __doc__ = _Spectral.Gamma.__doc__

class Gauss(_Spectral.Gauss, ParametricSpectrum) :
    __doc__ = _Spectral.Gauss.__doc__

class Jonswap(_Spectral.Jonswap, ParametricSpectrum) :
    __doc__ = _Spectral.Jonswap.__doc__


    @staticmethod
    def gamma_to_goda(gamma, variant = None):
        if variant is None:
            a,b,c,d =  8.97725419, -7.54430907, -0.07405992,  1.05039568
        elif variant.lower() == "ecmwf":
            a,b,c,d = 13.97405075, -15.7727841,   -0.36225204 ,  1.00166169
        return a + b * np.exp( c * gamma**d  )

    @staticmethod
    def goda_to_gamma(goda, variant = None):
        if variant is None:
            a,b,c,d =  8.97725419, -7.54430907, -0.07405992,  1.05039568
        elif variant.lower() == "ecmwf":
            a,b,c,d = 13.97405075, -15.7727841,   -0.36225204 ,  1.00166169
        return np.maximum( 1, (np.log((goda-a)/b)/c )**(1/d) )

    
    @staticmethod
    def wmin_wmax_over_wp(energy_ratio, gamma):
        """Uses regression to estimate bounds containing a given fraction of the energy.
        """
        wmax = (0.75 + 0.34*np.exp(-0.159*gamma)) * (1 - energy_ratio)**(-1/4)
        wmin =  min( 1.0,  1.09-0.44*energy_ratio )
        return wmin, wmax
    
   
        

class LogNormal(_Spectral.LogNormal, ParametricSpectrum) :
    __doc__ = _Spectral.LogNormal.__doc__


class PiersonMoskowitz(_Spectral.PiersonMoskowitz, ParametricSpectrum) :
    def hspecString(self):
        return ParametricSpectrum.hspecString(self).replace( "Pierson-Moskowitz".upper(), "JONSWAP GAMMA 1.0")

class OchiHubble(_Spectral.OchiHubble, ParametricSpectrum) :
    __doc__ = _Spectral.OchiHubble.__doc__

class Torsethaugen(_Spectral.Torsethaugen, ParametricSpectrum) :
    __doc__ = _Spectral.Torsethaugen.__doc__

class Wallop(_Spectral.Wallop, ParametricSpectrum) :
    __doc__ = _Spectral.Wallop.__doc__

class WhiteNoise(_Spectral.WhiteNoise, ParametricSpectrum) :
    __doc__ = _Spectral.WhiteNoise.__doc__

class WaveTabulatedSpectrum(_Spectral.WaveTabulatedSpectrum, Spectrum) :
    __doc__ = _Spectral.WaveTabulatedSpectrum.__doc__
    def integrate_moment(self, n, extrap = True):
        m = simpson( self.sw * self.w**n , x=self.w)
        if extrap :
            m += self.integrate_moment_tail( n , wmax = self.w.max() )
        return m

    def find_tp(self):
        return 2 * np.pi / self.w[self.sw.argmax()]

    def getHs(self, *args, **kwargs ) :
        return self.integrate_hs(*args, **kwargs)

    def getTz(self, *args, **kwargs ) :
        return self.integrate_tz(*args, **kwargs)

    def __str__( self ):
        return "TABULATED spectrum. HS = {}, TZ = {}\n".format( self.getHs(), self.getTz() )

    @staticmethod
    def getNParams():
        return 2

    @staticmethod
    def getCoefs_name():
        return ['w', 'sw']

    @staticmethod
    def getCoefs_min():
        return [None, None]

    @staticmethod
    def getCoefs_max():
        return [None, None]

    @staticmethod
    def getCoefs_0():
        return [np.array([0., 0.5, 1., 1.5]), np.array([0., 1., 1., 0.])]

    def getCoefs(self):
        return [self.w, self.sw]

    def hspecString( self, filename):
        """
        """
        with open( filename, "w") as f :
            f.write( "#" + self.__str__() + "\n")
            for i, w in enumerate(self.w) :
                f.write( "{:.3f}  {:.4e}\n".format( w , self.sw[i] ) )

        return "SPECTRUMFILE {}  WHEADING {}".format(filename, np.rad2deg(self.heading))


class WaveTabulatedSpectrumOneParam(WaveTabulatedSpectrum):

    def __init__(self, *args):
        array = args[0]
        w = array[:,0]
        ws = array[:,1]
        args = (w, ws, *args[1:])
        super().__init__(*args)

    @property
    def array(self):
        return np.array([self.w, self.sw]).transpose()

    @array.setter
    def array(self, array):
        assert(len(array.shape) == 2)
        self.w = array[:,0]
        self.ws = array[:,1]

    @staticmethod
    def getNParams():
        return 1

    @staticmethod
    def getCoefs_name():
        return ['array']

    @staticmethod
    def getCoefs_min():
        return [None,]

    @staticmethod
    def getCoefs_max():
        return [None,]

    @staticmethod
    def getCoefs_0():
        return [np.array([[0., 0.5, 1., 1.5], [0., 1., 1., 0.]]).transpose(),]

    def getCoefs(self):
        return [self.array,]


def specMaker(  spec = Jonswap ,  fixedCoefs = { "gamma" : 1}  ) :
    """Spectrum class factory.
    Fixed some of the coefficients
    """
    coefsNames = spec.getCoefs_name()
    iFixed = [ name in fixedCoefs.keys() for name in coefsNames  ]

    class spectrumMaker( spec ) :
        def __init__( *args, **kwargs ):
            spec.__init__( *args, **fixedCoefs, **kwargs )

        @staticmethod
        def getCoefs_name() :
            return [name for name in coefsNames if name not in fixedCoefs.keys()]

        def getCoefs(self) :
            return [ c for i, c in enumerate(self.getCoefs()) if i not in iFixed[i] ]

        @staticmethod
        def getNParams() :
            return spec.getNParams() - len(fixedCoefs)

        @staticmethod
        def getCoefs_0() :
            return [ c for i, c in enumerate(spec.getCoefs_0()) if not iFixed[i] ]

        @staticmethod
        def getCoefs_min() :
            return [ c for i, c in enumerate(spec.getCoefs_min()) if not iFixed[i] ]

        @staticmethod
        def getCoefs_max() :
            return [ c for i, c in enumerate(spec.getCoefs_max()) if not iFixed[i] ]

    return spectrumMaker


PM = specMaker( spec = Jonswap, fixedCoefs = { "gamma" : 1}  )

availableSpectra.append("PM")


