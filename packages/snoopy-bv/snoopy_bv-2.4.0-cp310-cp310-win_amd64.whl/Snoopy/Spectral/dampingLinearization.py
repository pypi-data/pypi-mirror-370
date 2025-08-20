import numpy as np
from scipy.optimize import brenth
from scipy.stats import norm
from Snoopy import Math as sm
from Snoopy import logger
from . import ResponseSpectrum, SpectralMoments, Rao
from tqdm import tqdm

_boundary = sm.Interpolators.ExtrapolationType.BOUNDARY


class SpectralMomentsSL( ):
    """Spectral moments calculation, including quadratic damping stochastic linearization.

    Ducktypes SpectralMoments()

    """

    def __init__(self , ssList, rao_sl, raos, bLin, bQuad, num_threads = 1):
        """Spectral moments calculation, including quadratic damping stochastic linearization.

        Parameters
        ----------
        ssList : list
            List of sea-state
        rao_sl : Rao
            Rao on which the linearization is performed. Contains several block corresponding to different linear damping.
        raos : list
            List of Raos on which moments are requested. Each rao contains several block calculated with a range of linear damping.
        bLin : float
            Linear damping coefficient
        bQuad : float
            Quadratic damping coefficicent

        Example
        -------
        >>> rao_sl = sp.Rao( "roll.rao" )
        >>> raos_sl = [ sp.Rao( "rwe_1.rao" ) , sp.Rao( "rwe_2.rao" ) ]
        >>> ssList = [sp.SeaState.Jonswap( hs , 10.0 , 1.0  , np.pi / 2 ) for hs in [ 2.0 , 5.0, 7.0 ]]
        >>> smom_sl = sp.SpectralMomentsSL( ssList , raos, [raos],  bLin = 2e+08 , bQuad = 2e10  )
        >>> smom_sl.beq
        [ 310323490, 417833451,  522729249  ]
        >>> smom_sl.getM0s()

        """
        self.raos = raos
        self.rao_sl = rao_sl

        self.ssList = ssList
        self.bLin = bLin
        self.bQuad = bQuad

        self.bMin, self.bMax = self.rao_sl.getModeCoefficients()[0] , self.rao_sl.getModeCoefficients()[-1]

        self._beq = None

        self._m0s = None
        self._m2s = None
        
        self.num_threads = num_threads


    def _compute_moments(self):
        """Compute moments of 'associated' Raos'.

        Results stored in self._m0s and self._m2s.
        """
        self._m0s = np.zeros( (len(self.ssList), len(self.raos) ) , dtype = float )
        self._m2s = np.zeros( (len(self.ssList), len(self.raos) ) , dtype = float )
        for iss , beq in enumerate(self.beq) :
            rao = Rao([ rao_.getRaoAtModeCoefficients( [beq] , extrapType = _boundary) for rao_ in self.raos ])
            smom = SpectralMoments( [self.ssList[iss] ] , rao)
            self._m0s[iss, : ] = smom.getM0s()[0,:]
            self._m2s[iss, : ] = smom.getM2s()[0,:]


    def getM0s(self):
        """Return m0s."""
        if self._m0s is None :
            self._compute_moments()
        return self._m0s


    def getM2s(self):
        """Return m2s."""
        if self._m2s is None :
            self._compute_moments()
        return self._m2s


    @property
    def beq(self) :
        """Equivalent damping on each sea-state.

        Lazy evaluation

        Returns
        -------
        list
            Equivalent linear damping on each sea-state
        """
        if self._beq is None:
            self._linearize()

        return self._beq


    def _linearize(self):
        """Perform the linearization.

        Interpolate m2.

        Use Brenth algorithm to iterate. Results are stored in self._beq
        """
        from scipy.interpolate import InterpolatedUnivariateSpline
        smom_sl = SpectralMoments( self.ssList , self.rao_sl, num_threads = self.num_threads )
        self._beq = []
        for i in range(len(self.ssList)) :
            m2_interp = InterpolatedUnivariateSpline(  self.rao_sl.getModeCoefficients() , smom_sl.getM2s()[i,:] )
            #Check bounds :
            if self._stochBeq( m2_interp( self.bMin ) )  < self.bMin :
                logger.warning("Saturation Beq = Bmin. Input damping range does not contains the equivalent one.")
                self._beq.append( self.bMin )
            elif self._stochBeq( m2_interp( self.bMax ) ) >= self.bMax :
                logger.warning("Saturation Beq = Bmax. Input damping range does not contains the equivalent one.")
                self._beq.append( self.bMax )
            else :
                self._beq.append(  brenth( lambda b_ :  self._stochBeq( m2 =  m2_interp( b_) ) - b_ , a = self.bMin , b = self.bMax ) )

    def _linearize_slow(self):
        """Perform the linearization.

        Interpolate RAO and calculate m2. Not used : too slow

        Use Brenth algorithm to iterate. Results are stored in self._beq
        """
        self._beq = []
        for ss in tqdm( self.ssList, desc = "Linearise damping on each sea-state" ) :
            #Check bounds :
            if self._stochBeq( self._compute_m2_sl( ss, self.bMin ) ) < self.bMin :
                logger.warning("Saturation Beq = Bmin. Input damping range does not contains the equivalent one.")
                self._beq.append( self.bMin )
            elif self._stochBeq( self._compute_m2_sl( ss, self.bMax ) ) >= self.bMax :
                logger.warning("Saturation Beq = Bmax. Input damping range does not contains the equivalent one.")
                self._beq.append( self.bMax )
            else :
                self._beq.append(  brenth( lambda b_ :  self._stochBeq( m2 =  self._compute_m2_sl(ss, b_) ) - b_ , a = self.bMin , b = self.bMax ) )

    def _compute_m2_sl( self , ss, blin ) :
        """Compute m2 corresponding to a given linear damping."""
        rao_ = self.rao_sl.getRaoAtModeCoefficients( [blin] , extrapType = _boundary)
        smom = SpectralMoments( [ss] , rao_ )
        return smom.getM2s()[0,0]

    def _stochBeq(self,  m2 ) :
        """Return equivalent damping, function of m2."""
        return self.bLin + self.bQuad * (8/np.pi)**0.5 * m2**0.5




class StochasticDamping(  ResponseSpectrum  ) :


    def __init__( self , seaState , raos, bLin, bQuad):
        """Stochastic linearization of the quadratic damping.

        Parameters
        ----------
        seaState : SeaState
            Seastate on which to linearize the damping.
        raos : Rao
            Rao corresponding to the damped mode. Unit has to be consistent with the damping one!
        bLin : float
            Linear damping
        bQuad : float
            Quadratic damping
        """
        self.raos = raos
        self.seaState_ = seaState
        self.bLin = bLin
        self.bQuad = bQuad

        bMin, bMax = self.raos.getModeCoefficients()[0] , self.raos.getModeCoefficients()[-1]

        #Classic stochastic linearization
        #Check bounds :
        if self._stochBeq( self.compute_m2( bMin ) ) < bMin :
            logger.warning("Saturation Beq = Bmin. Input damping range does not contains the equivalent one.")
            self.beq = bMin
        elif self._stochBeq( self.compute_m2( bMax ) ) >= bMax :
            logger.warning("Saturation Beq = Bmax. Input damping range does not contains the equivalent one.")
            self.beq = bMax
        else :
            self.beq = brenth( lambda b_ :  self._stochBeq( m2 =  self.compute_m2(b_) ) - b_ , a = bMin , b = bMax )

        self.m0eq, self.m2eq = self.compute_m2(self.beq, m0=True)

        # Safer to save rao_eq in the object, probably to avoid it to be destroyed, and refererd to in the Cpp (actually does not work otherwise...)
        self.rao_eq = raos.getRaoAtModeCoefficients( [self.beq],  extrapType = _boundary )
        ResponseSpectrum.__init__( self , seaState, self.rao_eq )

    def _stochBeq(self,  m2 ) :
        """Return equivalent damping, function of m2.
        """
        return self.bLin + self.bQuad * (8/np.pi)**0.5 * m2**0.5

    def compute_m2(self , blin, m0 = False) :
        """Compute moment corresponding to a given linear damping.
        """
        rao_ = self.raos.getRaoAtModeCoefficients( [blin] , extrapType = _boundary)
        rSpec = ResponseSpectrum( self.seaState_ , rao_  )
        m2 = rSpec.getM2()
        if not m0 : return m2
        else : return rSpec.getM0() , m2


    def getVDistribution(self):
        return norm(loc = 0 , scale = self.m2eq**0.5)

    def getM0(self, imode = -1):
        return self.m0eq

    def getM2(self, imode = -1):
        return self.m2eq

    def getM0M2(self, imode = -1) :
        return self.m0eq, self.m2eq



