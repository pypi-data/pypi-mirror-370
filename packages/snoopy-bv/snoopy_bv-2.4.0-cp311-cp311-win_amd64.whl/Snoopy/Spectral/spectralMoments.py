from Snoopy import Spectral as sp

import _Spectral


class SpectralMoments( _Spectral.SpectralMoments ):

    def getSpectralStats(self):
        """SpectralStats instance from m0s and m2s.

        Returns
        -------
        sp.SpectralStats
            return SpectralStats instance (vectorized on all sea-state and coefficients)
        """

        return sp.SpectralStats( self.getM0s() , self.getM2s() )

