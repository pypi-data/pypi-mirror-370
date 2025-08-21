import numpy as np
from Snoopy import TimeDomain as td
from Snoopy import Spectral as sp
from matplotlib import pyplot as plt
import _TimeDomain

class RetardationFunctionsHistory( _TimeDomain.RetardationFunctionsHistory ):

    @classmethod
    def FromHydroStar( cls , hstar_file , trad , dt , wCut , wInf, extrap=1) :
        """Construct retardation function from HydroStar output
        
        Parameters
        ----------
        cls : TYPE
            DESCRIPTION.
        hstar_file : TYPE
            DESCRIPTION.
        trad : TYPE
            DESCRIPTION.
        dt : TYPE
            DESCRIPTION.
        wCut : TYPE
            DESCRIPTION.
        wInf : TYPE
            DESCRIPTION.
        extrap : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """

        import xarray

        h5_data = xarray.open_dataset( hstar_file )
        waveDamp = h5_data["WaveDamping"].transpose().transpose( "Frequency", "Body_i", "Body_j", "Mode_i", "Mode_j" , "Heading" )
        
        #Select heading  (closest to head sea)
        speed = h5_data.attrs["SPEED"]
        headrad = np.deg2rad(h5_data.Heading.values)
        ihead = np.cos( headrad ).argmax()
        encFreq = sp.w2we( waveDamp.Frequency.values , b = headrad[ihead], speed = speed )

        params = td.RetardationParameters(  trad , dt , wCut , wInf, extrap )
        h5_data.close()
        return cls ( encFreq, 
                     waveDamp[ :, 0 , 0 , :, :, ihead ].values, 
                     params
                   )

    def plot(self, ax=None, imode = 0 , jmode = 0):
        if ax is None : 
            fig, ax = plt.subplots()

        trad = self.getRetardationDuration()
        ax.plot( self.getTimeInstants(trad) ,  self.getHistory(trad)[: , imode, jmode] )
        ax.set_xlabel("Time")
        ax.set_ylabel("K")
        return ax
    
    def plotDampingRecalculation(self,imode = 0 , jmode = 0,  ax = None)  :
        if ax is None : 
            fig, ax = plt.subplots()

        freq = self.getFrequencies()
        ax.plot( freq, self.getDamping()[: , imode, jmode]  , label ="Original" )
        ax.plot( freq,  self.reComputeDamping(freq)[: , imode, jmode]  , label ="Re-calculated" )
        ax.legend()
        return ax
        

