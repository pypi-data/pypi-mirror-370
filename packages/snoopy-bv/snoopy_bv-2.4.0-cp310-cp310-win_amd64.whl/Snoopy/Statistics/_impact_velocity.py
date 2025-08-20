from Snoopy import Statistics as st
from Snoopy import Spectral as sp
import numpy as np
from Snoopy import logger


class LongTermImpact( st._longTermSD.LongTermRayleighABC ) :


    def __init__( self, ssList, rwe_rao, z , dss = 10800 ):
        """Compute long-term distribution of impact velocity.(i.e. impact velocity conditioned to point emergence on the cycle)

        Parameters
        ----------
        ssList : list
            List of sea-states
        rwe_rao : sp.Rao
            RWE RAO  (not velocity, the derivation is handled within the class)
        z : float, optional
            The position of impact point with regard to the free-surface.
        dss : float, optional
            Sea-state duration. The default is 10800.

        """
        self.rwe_rao = rwe_rao
        self.z = z
        st._longTermSD.LongTermRayleighABC.__init__( self, ssList = ssList, dss = dss, nModes = 1 )


    def _compute_m0s_m2s(self):
        smom = sp.SpectralMoments( self.ssList  , self.rwe_rao, **self.sht_kwargs)
        return smom.getM0s() , smom.getM2s()


    @property
    def longTerm(self):
        if self._lt is None :
            shtStats = self.spectralStats[:,0]
            self._lt = [ st.LongTerm( distributionList = self.impact_velocity_cdf, rTzList = shtStats.Rtz, probabilityList = self._ssProb, dss = self.dss )  ]

        return self._lt


    def impact_velocity_cdf( self, v ) :
        shtStats = self.spectralStats[:,0]
        return 1 - (shtStats.rayleigh.sf( abs(self.z) ) * st.rayleigh_c( shtStats.m2**0.5 ).sf( v ))





class LongTermImpactSL( LongTermImpact ):

    def __init__( self, ssList, rao_sl, rwe_rao, z , bLin, bQuad, dss = 10800 ):
        """Compute long-term distribution of impact velocity.(i.e. impact velocity conditioned to point emergence on the cycle)

        Handle quadratic roll damping.

        Parameters
        ----------
        ssList : list
            List of sea-states
        rao_sl : TYPE
            DESCRIPTION.
        rwe_rao : sp.Rao
            RWE RAO  (not velocity, the derivation is handled within the class)
        z : float, optional
            The position of impact point with regard to the free-surface.
        dss : float, optional
            Sea-state duration. The default is 10800.
        """
        LongTermImpact.__init__(  self, rwe_rao = rwe_rao, ssList = ssList, dss = dss, z=z )

        # Additional data to handle stochastic damping :
        self.bLin = bLin
        self.bQuad = bQuad
        self.rao_sl = rao_sl



    def _compute_m0s_m2s(self):
        smom = sp.SpectralMomentsSL( self.ssList  ,rao_sl = self.rao_sl , raos = [self.rwe_rao] , bLin = self.bLin, bQuad = self.bQuad)
        return smom.getM0s() , smom.getM2s()



if __name__ == "__main__" :


    rwe_rao = sp.Rao( f"{sp.TEST_DATA:}/rao/RWE_175m.rao" )

    ssList = [sp.SeaState.Jonswap( hs , 10.0 , 1.0  , np.pi / 2 ) for hs in np.arange(1,10,2)]

    lt_impact = LongTermImpact(ssList = ssList, rwe_rao = rwe_rao , z = 5.0 , dss = 10800.)

    

    print ( lt_impact.rp_to_x( 25.0 ) )

    print ( lt_impact.longTermSingle().nExceed(  5.279, 25.0 ).sum() )
    
    lt_vel = st._longTermSD.LongTermRao(ssList = ssList, rao = rwe_rao.getDerivate(n=1) ,  dss = 10800)
    print (lt_vel.rp_to_x( 25.0 ))
