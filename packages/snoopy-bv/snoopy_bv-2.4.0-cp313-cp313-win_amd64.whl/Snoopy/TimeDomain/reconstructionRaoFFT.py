import numpy as np
from Snoopy.TimeDomain import ReconstructionRaoLocal
from scipy.interpolate import InterpolatedUnivariateSpline
from Snoopy import logger


class ReconstructionRaoLocalFFT(ReconstructionRaoLocal):

    def __init__(self, wif, rao, dt_approx = 0.2, k = 3, numThreads = 1 ):
        """ Time domain reconstruction of RAOs, using FFT
        Args:
            wif (Wif): Wif object
            rao (Rao): Rao
            dt_approx (float, optional): Time step for FFT Defaults to 0.2.
            k (int, optional): Interpolation order Defaults to 3.

        Returns:
            None.
        """
        ReconstructionRaoLocal.__init__(self, wif, rao )
        self.dw = wif.get_dw()

        if self.dw is None:
            raise(Exception("FFT reconstruction only available for evenly spaced frequencies"))

        self.nmodes = rao.getNModes()
        self.df = self.dw / ( 2 * np.pi)
        self._zero_pad(dt_approx)
        self._irfft()
        self.k = k
        self.repetitionPeriod = 2 * np.pi / self.dw
        self._interpDone = False
        
        if (numThreads > 1) : 
            logger.debug("Only one thread used in ReconstructionRaoLocalFFT for now")


    @classmethod
    def WithBackup(cls, wif, rao, dt_approx = 0.2, k = 3,**kwargs):
        if wif.get_dw() is not None and wif.unidirectional and rao.getForwardSpeed() == 0. :
            return cls(wif, rao, dt_approx = dt_approx, k = k, **kwargs)
        else :
            logger.debug("dw is not constant, ReconstructionRao can not use FFT")
            return ReconstructionRaoLocal(wif, rao, **kwargs)


    def _zero_pad(self, dt) :
        """
        Zero padding in order to get the desired time step
        dt = 1 / ( 2 * fmax)
        """
        wmax_fft_approx = 2 * np.pi / ( 2 * dt )
        self.w = np.arange( 0.0, wmax_fft_approx + self.dw , self.dw)
        self.wmax_fft = np.max(self.w)
        self.dt = 2 * np.pi / ( 2 * self.wmax_fft )
        wmin = np.min(self.getWif().freq)
        wmax = np.max(self.getWif().freq)
        iwmin = np.where( np.isclose(self.w,wmin) )[0][0]
        iwmax = np.where( np.isclose(self.w,wmax) )[0][0]
        self.cmpx = np.zeros( (len(self.w), self.nmodes), dtype = complex )
        self.cmpx[  iwmin : iwmax + 1, : ] = self.getFourierCoefficients()[:,:]


    def _irfft(self):

        nt = (len(self.cmpx) - 1) * 2
        self.ts = np.empty( ( nt , self.nmodes), dtype = float )
        for imode in range(self.nmodes) :
            self.ts[:,imode] = np.fft.irfft( self.cmpx[:,imode] )
        self.ts *= ( len(self.cmpx) - 1 )
        self.time = np.linspace( 0, (1 / self.df) * (1 - 1 / nt), nt  )

    def _interp(self, k):

        self.interpolators = [ InterpolatedUnivariateSpline( self.time , self.ts[:,imode], k=k ) for imode in range(self.nmodes)]
        self._interpDone = True


    def __call__(self, time) :
        if (time[-1] - time[0]) > self.repetitionPeriod:
            logger.warning( "Reconstruction time exceed repetition period" )

        if not self._interpDone:
            self._interp(k=self.k)
        time = time % (self.repetitionPeriod)

        res = np.empty( (len(time), self.nmodes), dtype = float )
        for imode in range(self.nmodes):
            res[:,imode] = self.interpolators[imode]( time )
        return res

    def getDirectFFT(self):
        """Return FFT resuts, without Interpolation"""

        return self.time, self.ts


