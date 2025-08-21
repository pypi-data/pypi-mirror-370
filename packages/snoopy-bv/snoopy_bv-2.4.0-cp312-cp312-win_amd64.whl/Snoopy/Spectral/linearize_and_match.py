import numpy as np
import pandas as pd
from scipy.optimize import brenth
from scipy.stats import norm
from Snoopy import Math as sm
from Snoopy import logger
from . import ResponseSpectrum
from . import StochasticDamping

_boundary = sm.Interpolators.ExtrapolationType.BOUNDARY

#nopython = True
def i2j2( freq , cvalues  , h1Module , sw ):
    """
    Compute I2 and J2, TODO use FFT ?
    """
    dw = freq[1]-freq[0]
    dt_c = 0.2
    tauVect_c = np.arange( -100 , 100. , dt_c )
    nt = len(tauVect_c)
    h_c = np.empty((nt), dtype = complex)
    for i , t in enumerate(tauVect_c) :
        h_c[i] = (dw / (2*np.pi)) * np.sum(  cvalues*np.exp(1j*freq[:] * t)  )
        h_c[i] += (dw / (2*np.pi)) * np.sum(  np.conj(cvalues)*np.exp(-1j*freq[:] * t)  )

    Rttp_c = np.zeros( (  nt  ) , dtype = complex)
    for it , tau_ in enumerate(tauVect_c) :
        Rttp_c[it] =  np.sum( 1j * freq[:] * h1Module[:]**2  * sw[:] * np.exp( 1j*freq[:] * tau_) )  * dw
        Rttp_c[it] += np.sum( -1j * freq[:] * h1Module[:]**2  * sw[:] * np.exp( -1j*freq[:] * tau_) )  * dw

    #Divide by two because our spectrum is one sided
    h_c *= 0.5
    Rttp_c *= 0.5

    i2 =  np.sum(  h_c * Rttp_c   ) * dt_c
    j2 =  dt_c * np.sum( h_c * Rttp_c**3 )

    """
    # Alternate formula, same result
    f2 = np.empty((nt), dtype = complex)
    for i , t in enumerate(tauVect_c) :
        f2[i] = (1j*dw / (2*np.pi)) * np.sum( np.imag(cvalues) * np.exp(1j*freq[:] * t)  )
        f2[i] += (1j*dw / (2*np.pi)) * np.sum( -np.imag(cvalues) * np.exp(-1j*freq[:] * t)  )
    f2 *= 0.5
    j2 =  dt_c * np.sum( f2 * Rttp_c**3 )
    """
    #Coefficient 2 is necessary to get Prevosto results  (does not matter on the ration J2/I2, so that it might be normal)
    return np.real(i2), np.real(j2)


class LinearizeAndMatch( StochasticDamping ) :

    def __init__( self , seaState , raos, bLin, bQuad, loadRao , n = 4 ):
        """Linearize and match


        Parameters
        ----------
        seaState : Spectral.SeaState
            Seastate on which the L&M is applyed.
        raos : Spectral.Rao
            Roll transfer function, at various damping level
        bLin : float
            Linear damping coefficient.
        bQuad : float
            Quadratic damping coefficient.
        loadRao : Spectral.Rao
            Load RAO.
        n : integer, optional
            Number of moments to be matched. The default is 4.


        """
        StochasticDamping.__init__(self , seaState , raos, bLin, bQuad)


        #Load RAO does not depends on damping. If multi block RAO is input take the first one (all block should be identical)
        if loadRao.getNModes() > 1 :
            self.loadRao = loadRao.getRaoAtModeCoefficients( loadRao.getModeCoefficients()[0:1]  )
        else :
            self.loadRao = loadRao

        self.n = n

        #Lin & Match moments, to compute later
        self._moment = None
        self._vmoment = None

        self._maxEntropySolver = None
        self._vMaxEntropySolver = None

        #Coefficients of the exp law (  p(x) = exp(-sum( k_i * x**i )) )
        self._l = None


    def getAlphaGamma( self  ) :
        """Get linear and cubic damping of the cubic equilalent system
        """
        alpha = self.bQuad*(2. * self.m2eq / np.pi)**0.5 + self.bLin
        gamma = self.bQuad * ( 2. / (9*np.pi * self.m2eq ) )**0.5
        return alpha , gamma


    def computeLinAndMatchMoments( self, alphaGamma = None  ) :
        logger.debug("Compute L&M moments")
        from math import factorial

        self._moment = np.empty( ( self.n+1 ) , dtype = "float64" )    # Motion moments
        self._vmoment = np.empty( ( self.n+1 ) , dtype = "float64" )   # Velocity moments

        #Compute alpha and gamma, the linear and cubic coefficient of the cubic equivalent system
        if alphaGamma is None :
            alpha, gamma = self.getAlphaGamma()
        else :
            alpha, gamma = alphaGamma

        #Get transfer function of the linear system
        h1 = self.raos.getRaoAtModeCoefficients(  [alpha] , extrapType = _boundary )

        #Only denominator part
        h1a = h1 / self.loadRao

        rSpecLin = ResponseSpectrum( self.seaState , h1 )
        m0_lin = rSpecLin.getM0()
        m2_lin = rSpecLin.getM2()

        #Compute load spectrum (not wave spectrum !)
        ss = self.seaState
        loadSpec = ResponseSpectrum( ss , self.loadRao )
        sw = loadSpec.get()[:,0]

        #Get correct heading
        spec = self.seaState.getSpectrum(0)
        ihead = np.where( h1.head == spec.heading )[0][0]

        #Get relevant part of the RAO
        freq = h1a.freq[:]
        mod = h1a.module[  ihead, : , 0 ]
        cvalues = h1a.cvalues[ ihead , : , 0]

        #Compute I2, J2 alternate way (ok for i2, not for j2)
        #j2 = j2_( freq , imag_ , mod , sw , dw )
        #i2 = np.sum(  mod**2 * sw * freq * imag_ ) * dw

        #Formula based on correlation
        i2 , j2 = i2j2( freq , cvalues  , mod , sw )

        r =   j2  /  ( m0_lin * m2_lin * i2 )

        logger.debug( f"i2={i2:}, j2={j2:}, r={r:}" )

        self._moment[0]  = 1
        self._vmoment[0] = 1

        for i in range( 1, self.n + 1  ) :
            beta_i = 3. + 2.*(i-1.) * r

            def fun_(beq) :
                m2 = self.compute_m2(beq)
                return alpha  +   beta_i * gamma * m2   - beq

            logger.debug( f"Beta_{i:} = {beta_i:}" )
            beq_i = brenth( fun_ , a = self.raos.coef[0] , b = self.raos.coef[-1] )

            #print ( "Beq_{}/Beq1".format(i) , beq_i / beq1 , beta_i , "it" , fun_.counter)

            #Compute moment E(t**2) = m0
            rao_i = self.raos.getRaoAtModeCoefficients( [beq_i] , extrapType = _boundary )

            m0_i = ResponseSpectrum( self.seaState , rao_i ).getM0()
            self._moment[i] =  (factorial(2*i) / (2**i * factorial(i)) ) *   m0_i**i

            #Compute moment E(v**2) = m0 (v)
            vrao_i = rao_i.getDerivate()
            vm0_i = ResponseSpectrum( self.seaState , vrao_i ).getM0()
            self._vmoment[i] = (factorial(2*i) / (2**i * factorial(i)) ) *   vm0_i**i

        self.i2 = i2
        self.j2 = j2
        return self._moment , self._vmoment

    def iterate(self) :

        """ TODO : Recompute moment with estimated distribution as closure (instead of gaussian)
        from scipy.integrate import quad
        #replace (8/pi)**0.5 which assume gaussian with estimated probability density

        self.vmaxEntropy()
        vdist = self.getVDistribution( method="newton" )

        vrollBound = norm( 0, self.m2eq**0.5 ).isf(1e-9)

        coef = quad( lambda x : vdist.pdf(x) * x**2 * abs(x) , -vrollBound , vrollBound )
        coef /= self._vmoment[1]**1.5
        """

        return


    def _getIntegrationBound(self):
        return norm( 0, self.m0eq**0.5 ).isf(1e-9)

    def _getVIntegrationBound(self):
        return norm( 0, self.m2eq**0.5 ).isf(1e-9)

    def maxEntropy( self, *args, **kwargs ) :
        """Compute exponential coefficient from moments

        Parameters
        ----------
        method : str, optional
            Solver used, among ["Newton", "hybr", "lm", "broyden1", "broyden2", "anderson"]. The default is "hybr".
        itmax : int, optional
            Maximum number of iteration. The default is 500.
        eps : float, optional
            Tolerance. The default is 1e-8.

        Returns
        -------
        None
        """
        #Maximum entropysolver
        logger.debug("Maximum entropy solver")
        from Pluto.statistics.maxEntropySolver import MaxEntropySolver

        #Start with gaussian case values
        l0 = np.array([ -np.log( 1./( self.m0eq**0.5 * (2*np.pi)**0.5 ) ) , 1./( 2*self.m0eq ) ] + (self.n-1) * [0.]  )

        #Integration range
        rollBound = self._getIntegrationBound()
        x = np.linspace(-rollBound , rollBound, 5000)
        self._maxEntropySolver = MaxEntropySolver( mu = self.getMoments() , x = x )
        self._l = self._maxEntropySolver.solve( l0=l0 , *args, **kwargs )
        return self._l


    def getMoments( self ):
        if self._moment is None :
            self.computeLinAndMatchMoments()
        return self._moment

    def getVMoments( self ):
        if self._vmoment is None :
            self.computeLinAndMatchMoments()
        return self._vmoment


    def get_lambdas(self,*args,**kwargs):
        if self._l is None :
            self.maxEntropy(*args,**kwargs)
        return self._l


    def vmaxEntropy( self, method = "hybr" ) :
        #Maximum entropysolver, for velocity
        logger.debug ("Maximum entropy solver")
        from Pluto.statistics.maxEntropySolver import MaxEntropySolver
        from scipy.stats import norm
        l0 = np.array([ -np.log( 1./( self.m2eq**0.5 * (2*np.pi)**0.5 ) ) , 1./( 2*self.m2eq ) ] + (self.n-1) * [0.]  )

        #Integration range
        vrollBound = norm( 0, self.m2eq**0.5 ).isf(1e-9)
        x = np.linspace(-vrollBound , vrollBound, 5000)
        self._vMaxEntropySolver = MaxEntropySolver( mu = self.getVMoments() , x = x )
        self._vl = self._vMaxEntropySolver.solve( l0=l0 , method = method )
        return self._vl

    def getMaxDistribution(self, **kwargs):
        """Return roll maxima distribution

        Parameters
        ----------
        **kwargs : Any
            Argument passed to maximum entropy solver

        Returns
        -------
        dist : Distribution
            Maximum distribution object (contains a cdf method)
        """
        # Not at the beginning of the file to avoid importing Pluto.statistics (time consuming) if not nessesary
        from Pluto.statistics.maxEntropySolver import expPdf
        from Snoopy.Statistics import FrozenDistABC
        _l = self.get_lambdas( **kwargs )
        dist = FrozenDistABC()
        dist.cdf  = lambda x : 1. - expPdf(x,_l) / expPdf(0,_l)
        return dist


    def getDistribution(self, *args, **kwargs):
        """Return roll maxima distribution

        Parameters
        ----------
        **kwargs : Any
            Argument passed to maximum entropy solver

        Returns
        -------
        dist : Distribution
            Maximum distribution object (contains a cdf method)
        """
        return self._maxEntropySolver.getDistribution(*args, **kwargs)


    def getVDistribution(self):
        if self._vMaxEntropySolver is None:
            self.vmaxEntropy()
        return self._vMaxEntropySolver.getDistribution()

    def getMaxMoment(self) :
        from Pluto.statistics.maxEntropySolver import expPdf
        from scipy.integrate import quad
        m1 = 1. / expPdf(0 , self._l)
        m2 = quad( lambda x : x * expPdf(x , self._l) , -np.inf , +np.inf )[0]  / expPdf(0 , self._l)
        m3 = quad( lambda x : x**3 * expPdf(x , self._l) , -np.inf , +np.inf )[0]  / expPdf(0 , self._l)
        return m1, m2, m3

    @staticmethod
    def getCrossMoment( m , v ) :
        cross = pd.DataFrame( index = [0,2,4,6,8] , columns = [0,2,4,6,8] )
        for il , l in enumerate(cross.columns) :
            for ik , k in enumerate(cross.index) :
                cross.loc[ k , l  ] = m[ ik ] * v[ il ]
                if not ( (k == 2 and l == 0) or (l == 2 and k == 0)):
                    cross.loc[ k , l  ] /= (  m[1]**(0.5*k) * v[ 1 ]**(0.5*l)  )
        return cross