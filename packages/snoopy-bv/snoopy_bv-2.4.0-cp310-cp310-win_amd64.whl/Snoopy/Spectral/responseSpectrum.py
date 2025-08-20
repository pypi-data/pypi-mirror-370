import numpy as np
from scipy.stats import rayleigh, norm
from scipy import interpolate
from scipy import integrate
from matplotlib import pyplot as plt
import pandas as pd
import _Spectral
from Snoopy import Statistics as st
from Snoopy import Spectral as sp


class ResponseSpectrumABC() :

    @property
    def seaState(self):
        return self.getSeaState()

    def getSe(self):
        if len(self.getModes() == 1 ):
            return pd.Series( index = self.getFrequencies(), data = self.get()[:,0] )
        else :
            raise(Exception( "Only 1D data for responseSpectrum.getSe(). Check responseSpectrum.getModes()" ))

    def plot(self, ax = None, *args, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        ax.plot( self.rao.freq , self.get() , *args, **kwargs )
        ax.set_xlabel("Wave frequency (rad/s)")
        ax.set_ylim(bottom = 0.0)
        return ax

    def computeMoment(self) :
        """ Compute spectral moment
        Now in the C++. Temporarily kept for checking purpose
        """
        spec = self.get()
        dw = self.freq[1] - self.freq[0]
        m0 = np.sum(spec[:]) * dw
        m2 = np.sum(spec[:] * self.freq[:]**2 ) * dw
        return m0,m2

    def getDf(self) :
        return pd.DataFrame( index = self.getFrequencies(), data = self.get(), columns = self.modesNames )

    @property
    def modesNames(self):
        if hasattr(self, "getModes") :
            return sp.modesDf.reset_index().set_index("INT_CODE").loc[  self.getModes() , "NAME" ].values
        else :
            return None

    def to_DataFrame(self):
        """Convert to pd.DataFrame object
        """

        return pd.DataFrame( index = pd.Index(self.getFrequencies(), name = "Frequency") , data = self.get() , columns = self.modesNames )


class ResponseSpectrum( ResponseSpectrumABC , _Spectral.ResponseSpectrum ):


    @property
    def rao(self):
        return self.getRao()

    @property
    def freq(self):
        return self.rao.freq


    def computePy( self  ) :
        """ Compute and return response spectrum
        Now moved to c++ (self.get return the response spectrum, lazy evaluation )
        """
        res = np.zeros( (self.rao.nbfreq), dtype = float )
        for spec in self.seaState.spectrums :
            #No spreading
            if spec.spreading_type == _Spectral.SpreadingType.No :
                w_ = self.rao.freq
                sw_ = spec.compute(w_)
                ihead = (np.abs(self.rao.head - spec.heading)).argmin()
                #Compute response spectrum
                res[:] += self.rao.module[:,ihead]**2 * sw_[:]
            elif spec.spreading_type == _Spectral.SpreadingType.Cosn :
                raise(NotImplementedError)
            else :
                raise(NotImplementedError)
        return res

    def getMaxDistribution(self, imode = -1):
        """ Single amplitude maxima distribution

        Returns:
            scipy.stats like distribution: Single amplitude maxima distribution (contains .cdf, .pdf...  attributes).

        """
        return st.rayleigh_c( self.getM0(imode)**0.5 )

    def getRangeDistribution(self, imode = -1):
        """ Double amplitude maxima distribution

        Returns:
            scipy.stats like distribution: Single amplitude maxima distribution (contains .cdf, .pdf...  attributes).

        """
        return st.rayleigh_c( self.getM0(imode)**0.5 * 2.)

    def getDistribution(self, imode = -1 ):
        return norm( loc = 0. , scale = self.getM0(imode)**0.5 )

    def getRs(self, imode = -1):
        """Return significant response (range)
        """
        return 4.004 * self.getM0(imode)**0.5


    def getSpectralStats( self, imode = -1 ):
        """ Return SpectalStats instance
        """
        return sp.SpectralStats( *self.getM0M2() )


    def getTz(self, imode = -1):
        """Return mean up-crossing period
        """
        m0, m2 = self.getM0M2(imode)
        if m2 < 1e-12 :
            return np.nan
        return 2*np.pi * (m0/m2)**0.5




class ResponseSpectrum2nd( ResponseSpectrumABC, _Spectral.ResponseSpectrum2nd) :

    def __init__( self, seaState , rao ) :
        _Spectral.ResponseSpectrum2nd.__init__(self , seaState, rao)

    @property
    def qtf(self):
        return self.getQtf()

    def getSe(self):
        return pd.Series( index = self.getFrequencies(), data = self.get() )

    def getNewmanSe(self, *args, **kwargs):
        return pd.Series( index = self.getFrequencies(), data = self.getNewman(*args, **kwargs) )

    def plot(self, ax = None, *args, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        ax.plot( self.getFrequencies() , self.get(),  *args, **kwargs)
        ax.set_xlabel("Wave frequency (rad/s)")
        return ax




class ResponseSpectrumEncFrequency():
    def __init__(self, seaState, rao, we_min = 0.001, we_max = 5, nwe = 200):
        """Computes the response spectrum for a given range of encounter frequencies 
        
        The Doppler shift and dw0/dwe is evaluated for inifite water depths only!

        Parameters
        ----------
        seaState : Snoopy.Spectral.seastate.SeaState object
            input sea state with one or multiple spectrums.
        rao : Snoopy.Spectral.rao.Rao object
            input rao object that is prepared for spectral calculation
        we_min : float, optional
            minimum encounter frequency [rad/s]
        we_max : float, optional
            maximum encounter frequency [rad/s]
        nwe : int, optional
            number of encounter frequencies to discretize the frequency range

            
        EXAMPLE
        ----------
        >>> import numpy as np
        >>> from Snoopy import Spectral as sp
        >>> from Snoopy import TimeDomain as td
        >>> import matplotlib.pyplot as plt
        >>> rao1_file = 'USCGBE_Panel_400021_axial-stress.rao'
        >>> rao1 = sp.Rao(rao1_file).getSymmetrized().getSorted(duplicatesBounds=True)
        >>> rao = rao1.getRaoForSpectral(wmin = 0.005 , wmax = 4, dw = 0.005, db_deg=5)
        >>> ss = sp.SeaState( sp.Jonswap( hs = 1.0 , tp = 10.0 , gamma = 1.5 , heading = beta , spreading_type=sp.SpreadingType.Cos2s, spreading_value=2 ) )
        >>> wif = sp.Wif(ss, nbSeed = 200, seed = 42)
        >>> temp_ = np.arange(0, 3600*3, 0.5)
        >>> ts_rao1 = td.ReconstructionRaoLocal(wif, rao.getSymmetrized().getSorted(duplicatesBounds=True)).evalSe(temp_)
        >>> psd1df_ = td.getPSD(ts_rao1 , dw = 0.01, dw_zp = 0.001)
        >>> reSpec = ResponseSpectrum_EncFrequency(ss , rao, we_min = 0.001, we_max = 5, nwe = 200)
        >>> plt.plot(psd1df_.index, psd1df_['psd(AXIAL_LINESTRESS)'], '-b')
        >>> plt.plot(reSpec.encFreq, reSpec.resSpecEnc, '--r')
        >>> plt.show()
        """

        if not rao.isReadyForSpectral():
            raise(InterruptedError)
            
        if rao.getDepth() > 1e-3:
            raise(Exception("ResponseSpectrumEncFrequency only available for infinite depth." ))
        
        self.seastate = seaState
        self.rao = rao

        self.encFreq = np.linspace(we_min, we_max, nwe)
        self.speed_over_grav = self.rao.getForwardSpeed() / self.rao.grav
        self._computePy()


    def getSe(self):
        return pd.Series(index = self.encFreq , data = self.resSpecEnc)
    

    def _computePy(self):
        """ Computes the response spectrum with encounter frequency
        """
        self.resSpecEnc = np.zeros( (len(self.encFreq)), dtype = float )

        for spec in self.seastate.spectrums :
            if spec.getSpreadingType() == _Spectral.SpreadingType.No :
                ihead = (np.abs(self.rao.head - spec.heading)).argmin()
                self.resSpecEnc += self._computeResSpectrum_noSpreading(ihead, spec)
            else:
                self.resSpecEnc += self._computeResSpectrum_withSpreading(spec)
    
    def plot(self, ax = None, *args, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        ax.plot( self.encFreq , self.resSpecEnc , *args, **kwargs )
        ax.set_xlabel("Wave frequency (rad/s)")
        ax.set_ylim(bottom = 0.0)
        return ax

    def computeMoment(self) :
        """ Compute spectral moment
        """
        m0 = integrate.simpson(y=self.resSpecEnc, x=self.encFreq)
        m2 = integrate.simpson(y=self.resSpecEnc * self.encFreq[:]**2, x=self.encFreq)
        return m0,m2

    def getM0(self) :
        """ Compute spectral moment
        """
        m0 = integrate.simpson(y=self.resSpecEnc, x=self.encFreq)
        return m0
    
    def getM0M2(self) :
        """ Compute spectral moment
        """
        return self.computeMoment()

    def getSpectralStats( self ):
        """ Return SpectalStats instance
        """
        return sp.SpectralStats( self.computeMoment() )

    def getTz(self):
        """Return mean up-crossing period
        """
        m0, m2 = self.computeMoment()
        if m2 < 1e-12 :
            return np.nan
        return 2*np.pi * (m0/m2)**0.5

    def getRs(self):
        """Return significant response (range)
        """
        return 4.004 * self.getM0()**0.5

    def _computeResSpectrum_noSpreading(self, ihead, spec):
        temp_res = np.zeros( (len(self.encFreq)), dtype = float )

        cos_theta = np.cos(spec.heading)
        twopsi = 2 * self.speed_over_grav * cos_theta
        rao2_headint = interpolate.interp1d(self.rao.freq, self.rao.module[ihead,:,0]**2, bounds_error=False, fill_value=0)

        if spec.heading > np.pi/2 and spec.heading < np.pi*3/2:
            ## head seas
            term1 = np.sqrt(1 - 2 * twopsi * self.encFreq)
            w0 = 1 / twopsi * (1 - term1)
            dw0_dwe = 1 / term1
            temp_res += rao2_headint(w0) * dw0_dwe * spec.compute(w0, spec.heading)
        elif spec.heading == np.pi/2 or spec.heading == np.pi*3/2:
            ## beam sea
            temp_res += rao2_headint(self.encFreq) * spec.compute(self.encFreq, spec.heading)
        else:
            ## following seas 
            term1 = np.sqrt(1 + 2 * twopsi * self.encFreq)
            w03 = 1 / twopsi * (1 + term1)
            dw03_dwe = 1 / term1
            temp_res += rao2_headint(w03) * dw03_dwe * spec.compute(w03, spec.heading)
            for iwe, we in enumerate(self.encFreq):
                if we <= 1 / 2 / twopsi:
                    term2 = np.sqrt(1 - 2 * twopsi * we)
                    w01 = 1 / twopsi * (1 - term2)
                    w02 = 1 / twopsi * (1 + term2)
                    dw012_dwe = 1 / term2
                    temp_res[iwe] += rao2_headint(w01) * dw012_dwe * spec.compute([w01], [spec.heading])[0]
                    temp_res[iwe] += rao2_headint(w02) * dw012_dwe * spec.compute([w02], [spec.heading])[0]

        return temp_res
    
    def _computeResSpectrum_withSpreading(self, spec):
        temp_res = np.zeros( (len(self.encFreq)), dtype = float )
        dtheta = np.mean(np.diff(self.rao.getHeadings()))
        for iTh, theta in enumerate(self.rao.getHeadings()):
            cos_theta = np.cos(theta)
            twopsi = 2 * self.speed_over_grav * cos_theta
            rao2_headint = interpolate.interp1d(self.rao.freq, self.rao.module[iTh,:,0]**2, bounds_error=False, fill_value=0)
            if theta > np.pi/2 and theta < np.pi*3/2:
                ## head seas
                term1 = np.sqrt(1 - 2 * twopsi * self.encFreq)
                w0 = 1 / twopsi * (1 - term1)
                dw0_dwe = 1 / term1
                temp_res += rao2_headint(w0) * dw0_dwe * dtheta * spec.compute(w0, theta)
            elif theta == np.pi/2 or theta == np.pi*3/2:
                ## beam sea
                temp_res += rao2_headint(self.encFreq) * dtheta * spec.compute(self.encFreq, theta)
            else:
                ## following seas 
                term1 = np.sqrt(1 + 2 * twopsi * self.encFreq)
                w03 = 1 / twopsi * (1 + term1)
                dw03_dwe = 1 / term1
                temp_res += rao2_headint(w03) * dw03_dwe * dtheta * spec.compute(w03, theta)
                for iwe, we in enumerate(self.encFreq):
                    if we <= 1 / 2 / twopsi:
                        term2 = np.sqrt(1 - 2 * twopsi * we)
                        w01 = 1 / twopsi * (1 - term2)
                        w02 = 1 / twopsi * (1 + term2)
                        dw012_dwe = 1 / term2
                        temp_res[iwe] += rao2_headint(w01) * dw012_dwe * dtheta * spec.compute([w01], [theta])[0]
                        temp_res[iwe] += rao2_headint(w02) * dw012_dwe * dtheta * spec.compute([w02], [theta])[0]

        return temp_res