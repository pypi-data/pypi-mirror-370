import os
import pandas as pd
import numpy as np
import _Spectral
from Snoopy import Spectral as sp
from Snoopy import logger

class Wifm(_Spectral.Wifm):
    """Class to handle multiple wif file corresponding to multiple time windows
    """

#     def __init__(self , wifs, timeBounds ):
#         """ Initialize the 'Multi-Wif' object
#         wifs : list of wif object
#         timeStart : time range in which each wif applies
#         """
#         self.wifs = wifs
#         self.timeBounds = timeBounds
# 
    def __str__(self) :
        s =  "Multi-Wif {}\n".format(self.__repr__())
        s += "Number of wifs : {}\n".format( self.getNWifs() )
        timeBounds = self.getBounds()
        s += "Time range     : {} to {}\n".format( timeBounds[0,0], timeBounds[-1,1] )

        #Average Hs
        h = np.array( [ sp.Wif(self.getWifAtIndex(i)).hs for i in range(self.getNWifs()) ] )
        s += "Hs = {:.1f} (mean) {:.1f} (std)\n".format( np.mean( h ), np.std(h) )

        #Average number of component
        h = np.array( [ sp.Wif(self.getWifAtIndex(i)).nbwave for i in range(self.getNWifs()) ] )
        s += "Nb Components = {:.1f} (mean) {:.1f} (std)\n".format( np.mean( h ), np.std(h) )

        #Heading
        h = np.array( [ self.getWifAtIndex(i).getIndependentHeadings() for i in range(self.getNWifs()) ] )
        uniqueHeading = np.rad2deg(np.unique(h.flatten()))
        s += "Heading = {:}".format( uniqueHeading   )

        return s

    def write(self, basename):
        with open(basename+".wifm", "w") as f:
            f.write( "{}, {}, {}\n".format( "#WifFile", "Tmin", "Tmax" ))
            timeBounds = self.getBounds()
            for i in range(self.getNWifs()):
                wif = sp.Wif(self.getWifAtIndex(i))
                wifName = "{}_{:04}.wif".format( basename, i )
                f.write( "{}, {}, {}\n".format( os.path.basename(wifName), timeBounds[i,0], timeBounds[i,1] ) )
                wif.write( wifName )

    def optimize(self, energyRatio):
        wifList = []
        append = wifList.append
        for i in range(self.getNWifs()):
            append(sp.Wif(self.getWifAtIndex(i)).optimize(energyRatio))
        return self.__class__(wifList, self.getBounds())

    @classmethod
    def Read(cls, filename):

        basedir = os.path.dirname(filename)
        data = pd.read_csv( filename, comment = "#", index_col = 0, header = None )
        wifs = np.empty(  (len(data)), dtype = sp.Wif  )
        for i, wifname in enumerate(data.index) :
            if not os.path.isabs( wifname ):
                wifname = os.path.join( basedir, wifname )
            wifs[i] = sp.Wif( wifname )
        return cls( wifs , data.values.astype(float) )


    def offset(self, dt=0., dx=0., dy = 0.) :
        """
        Offset the wif
        """
        for i in range(self.getNWifs()):
            self.getWifAtIndex(i).offset( dt, dx, dy )


    def plotBounds(self, ax):
        
        for x in self.getBounds()[:,1] :
            ax.axvline(x=x)
        return ax
        

    @classmethod
    def FromTs(cls, se, windows_net, overlap, b=0., method = "FFT",  **kwargs  ) :
        """ Compute Wifm from time series
        float windows_net : the windows size that will be used for reconstruction
        float overlap     : overlap used to generate each wif (to ensure continuity)
        """

        logger.info(f"Computing Wifm with {method:}")

        T = se.index.max() - se.index.min()
        nW = int(np.ceil( T / (windows_net) ))

        tmin = se.index.min()
        wifList = []
        bounds = []
        for iw in range(nW)  :
            if iw == 0 :
                start = tmin
                start_wif = start
                end = start + windows_net + 0.5*overlap
                end_wif = start_wif + windows_net + overlap
            elif iw < nW - 1 :
                start = tmin + 0.5*overlap + iw*windows_net
                start_wif = start - 0.5*overlap
                end = start + windows_net
                end_wif = start_wif + windows_net + overlap
            elif iw == nW - 1:
                start = tmin + 0.5*overlap + iw*windows_net
                start_wif = start - 0.5*overlap
                end = se.index.max() + 0.01
                end_wif = end

            wifList.append(  sp.Wif.FromTS( se.loc[float(start_wif) : float(end_wif)],
                                            b=b, method = method,  **kwargs  )  )
            bounds.append( [ start, end  ] )

        return cls(  wifList, np.array(bounds) )
