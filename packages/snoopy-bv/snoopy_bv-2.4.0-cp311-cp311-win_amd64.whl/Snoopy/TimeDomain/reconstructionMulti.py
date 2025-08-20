"""
    Handle reconstruction from multiple wif file (wifm object)

    Should work with class deriving from ReconstructionABC

"""

import numpy as np
import pandas as pd
from Snoopy.TimeDomain import ReconstructionABC
from Snoopy import Spectral as sp

from .reconstruction1st import ReconstructionWif_pyABC

class ReconstructionMulti(ReconstructionWif_pyABC):

    def __init__(self, ReconstructionModel, wifm, *args, **kwargs):
        self._methodName = "__call__"
        if "methodName" in kwargs:
            self._methodName = kwargs.get("methodName")
            del kwargs["methodName"]
        self.ReconstructionList = [ReconstructionModel(wifm.getWifAtIndex(i), *args, **kwargs)
                                   for i in range(wifm.getNWifs())]
        self.wifm = wifm

    def getData(self):
        try:
            return self.ReconstructionList[0].getData()
        except:
            return None

    def __call__(self, time, *args, **kwargs):
        """Reconstruction

        First argument is mandatorily the time
        """
        if not isinstance(time, (np.ndarray,) ) :  # One time step at a time
            iWif = self.wifm.getWifIndex(time)
            return getattr(self.ReconstructionList[iWif], self._methodName)( time, *args, **kwargs )
        else : # Vectorized version
            bounds = self.wifm.getBounds()
            timeArrays = splitTime(time, bounds, time)
            argsArray = [ splitTime(time, bounds, arg ) for arg in args ]
            kwargsArray = { key : splitTime(time, bounds, value ) for key, value in kwargs.items() }

            res = []
            for iWif in range(len( timeArrays )) :
                tmpArg = [  argsArray[iargs][iWif] for iargs in range(len(args)) ]
                tmpKwargs = { key : val[iWif] for key, val in kwargsArray.items()  }
                ires = getattr(self.ReconstructionList[iWif], self._methodName)( timeArrays[iWif], *tmpArg , **tmpKwargs )
                res.append( ires )

            return np.concatenate( res )

    def evalDf( self, time , *args, **kwargs ) :
        """Same as __call__, but return pd.DataFrame with time as index
        """
        return pd.DataFrame( index = time , data = self( time, *args, **kwargs ), columns = sp.modesIntsToNames(self.getModes()) )


    def getModes(self) :
        return self.ReconstructionList[0].getModes()





def splitTime( timeVect, bounds, valueArray ) :
    """Split time vector according to bound
    """
    if timeVect[0] < bounds[0,0] or timeVect[-1] > bounds[-1,1] :
        raise(Exception("out of time bounds"))
    return [valueArray[  np.where( (timeVect < up) & (timeVect >= down )) ] for down, up in bounds]
