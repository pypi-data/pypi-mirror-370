from __future__ import absolute_import , print_function
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

from Snoopy import Spectral as sp
from Snoopy import TimeDomain as td


class Wib(object):
    """Discretised spectrum, random amplitude.

    n = sum ( a_i * s * cos(w_i) + b_i * s *sin(w_i) )

    Python only (no c++ base class) for now, used in FORM/EDW application only for now

    """
    def __init__(self , freq, head, ab, s, depth = 0) :
        self.freq = freq
        self.head = head
        self.ab = ab
        self.s = s
        self.depth = depth


    def to_dataframe( self ):
        return pd.DataFrame( data = { "Frequency" : self.freq , "U" : self.ab[:self.nbwave] , "V" : self.ab[self.nbwave] , "Heading"  : self.head,  "s" : self.s } )

    def write(self, filename) :
        self.to_dataframe(  ).to_csv(filename)

    @classmethod
    def Read(cls, filename):
        df = pd.read_csv(filename)
        return cls( df.Frequency.values, df.Heading.values,  ab=np.concatenate( [df.U.values, df.V.values] ), s = df.s.values  )


    @property
    def nbwave(self):
        return len(self.freq)

    def plot(self) :
        fig, ax = plt.subplots()
        ax.plot( self.freq, self.s, "o" )
        plt.show()

    def __str__(self) :
        s  = "Number of component = {} * 2\n".format(self.nbwave)
        s += "Hs = {:.2f}\n".format(self.hs())
        s += 'Beta = {}\n'.format(self.beta())
        return s

    def m0(self) :
        return np.sum( 0.5*self.s[:]**2*(self.ab[:self.nbwave]**2+self.ab[self.nbwave:]**2)  )

    def hs(self) :
        return 4.004*self.m0()**0.5

    @property
    def k(self) :
        return sp.w2k( self.freq , self.depth )

    @classmethod
    def SetSeaState(cls, seaState , **kwargs )   :
        if seaState.getSpectrumCount() > 1 :
            raise (NotImplementedError)
        spec = seaState.getSpectrum(0)
        wib_ = Wib.SetSpectrum( spec , **kwargs )
        return wib_

    @classmethod
    def FromWif(cls, wif, seaState) :
        """Construct wib from Wif and SeaState
        """
        dw = wif.freq[1]-wif.freq[0]
        s = ( seaState.compute(wif.freq) * dw )**0.5       
        u=np.empty([len(wif.freq),])
        v=np.empty([len(wif.freq),])     
        for i in range(0,len(wif.freq)):
            if s[i]==0:
                u[i]=0
                v[i]=0
            else:
                u[i] = wif.amp[i] * np.cos( wif.phi[i] ) / s[i]
                v[i] = wif.amp[i] * np.sin( wif.phi[i] ) / s[i]
        ab = np.concatenate(  (u,v)  )
        return cls( freq = wif.freq,  head = wif.head, ab=ab , s = s)        

    def beta(self) :
        return np.sum( self.ab[:self.nbwave]**2 + self.ab[self.nbwave:]**2 )**0.5

    def upCrossingRate(self , beta = None) :
        """Return upcrossing rate (per seconds)

        Parameters
        ----------
        beta : float, optional
            Reliability index, if none current beta is calculated from current amplitudes. The default is None.

        Returns
        -------
        float
            Up-crossing rate.
        """
        
        if beta is None : beta = self.beta()
        t = np.sum( (self.ab[:self.nbwave]**2 + self.ab[self.nbwave:]**2) * self.freq[:]**2 )**0.5
        return t * np.exp( -0.5*beta**2 ) / (2*np.pi*beta)


    @classmethod
    def SetSpectrum( cls, spectrum , *, wmin = 0.1, wmax = 3.0, nbSeed=200, seedID=0 , depth = 0.0 ) :
        from scipy import stats

        freq = np.empty( (nbSeed), dtype = float )
        head = np.empty( (nbSeed), dtype = float )
        ab = np.empty( (2*nbSeed), dtype = float )
        s = np.empty( (nbSeed), dtype = float )  # Sw*dw

        head[:] = spectrum.heading
        gauss = stats.norm( loc = 0. , scale = 1. )
        ab = gauss.rvs( 2*nbSeed )

        #Constant frequency spacing
        freq = np.linspace( wmin , wmax , nbSeed )
        dw = (wmax-wmin) / (nbSeed-1.)
        for i in range(nbSeed):
            s[i] = ( spectrum.compute( freq[i] ) * dw )**0.5

        return cls( freq=freq, head=head, ab=ab, s=s, depth=depth )

        """
        # Constant wave number spacing :
        kmin, kmax =  wmin**2/9.81 , wmax**2/9.81
        dk = (kmax-kmin) / (nbSeed-1.)
        kmin_ = dk * int( kmin / dk )

        if kmin_ == 0 :
            print ("Not enough nbSeed. Min nb seed should be : ", (kmax-kmin)/kmin + 1)
            exit()
        self.freq =  sp.k2w(  np.arange(  kmin_, kmax, dk )  )
        for i in range(self.nbwave):
            self.s[i] = ( sp.w2cg(self.freq[i]) * spectrum.compute( self.freq[i] ) * dk )**0.5
        """


    def timeC(self, tmin, tmax , dt):
        nbdt = int((tmax-tmin)/dt) + 1
        time = np.linspace( tmin , tmax , nbdt )
        response = np.zeros( (nbdt) )
        for iwave in range(self.nbwave):
            response[:] += self.s[iwave] * ( self.ab[iwave]  * np.cos( self.freq[iwave] * time[:]) - self.ab[iwave+self.nbwave]  * np.sin( self.freq[iwave] * time[:] )  )
        return pd.DataFrame( index = time, data = response , columns = ["TimeReconstruction"])

    def getWif(self) :
        #Convert the wib to wif
        amp = self.s[:]*(self.ab[:self.nbwave]**2 + self.ab[self.nbwave:]**2) ** 0.5
        phi = np.arctan2(  self.ab[self.nbwave:] , self.ab[:self.nbwave]  )
        return sp.Wif( self.freq , amp , phi , self.head , depth = self.depth )



if __name__ == "__main__" :

    print ("Run")

    spec = sp.Jonswap( hs = 17.6 , tp = 16.0  , gamma = 1.0 , heading = 0.0 )

    ss = sp.SeaState(spec)

    waveModel = td.FirstOrderKinematic

    wif = sp.constrainedWave(  [ (0., 13.7) , (13.6, 7.6)  ]  , ss,  waveModel = waveModel )

    print ("Done")

    waveModel( wif ).getElevation_SE( np.linspace(-50 , 50 , 2000) , [0,0] ).plot()



