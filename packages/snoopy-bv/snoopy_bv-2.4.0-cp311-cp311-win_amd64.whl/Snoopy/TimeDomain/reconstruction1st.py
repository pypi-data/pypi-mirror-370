import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
import _TimeDomain


class ReconstructionWif_pyABC() :

    def __str__(self):
        s = "Number of components = {}".format( self.nbwave )

        return s

    @property
    def nbwave(self):
        return len(self.getWif().getFrequencies())


    def evalSe( self , time, *args, **kwargs ) :
        """Same as evalDf , but return pandas series, ensure that data is 1D
        """
        return self.evalDf(time, *args, **kwargs).iloc[:,0]

    def evalDf( self, time, *args, **kwargs  ) :
        """Return pandas dataframe, with time as index
        """
        return pd.DataFrame( index = pd.Index(time, name = "time") , data = self( time,*args, **kwargs  ), columns = sp.modesIntsToNames( self.getModes() ) )

    def getModes(self) :
        return [0]


# Python class is before, otherwise CPP methods that implement a throw("NotImplemented") would be prefered
class ReconstructionWif(ReconstructionWif_pyABC, _TimeDomain.ReconstructionWif):
	
    pass

class ReconstructionWifLocal(ReconstructionWif_pyABC, _TimeDomain.ReconstructionWifLocal):
    """Wif time reconstruction class in local"""

    def getElevation_DF(self , time, x , y = 0.):
        S , T = np.meshgrid( x , time  )
        res = self(  T , S , y  )
        df = pd.DataFrame(index = time , columns = x , data = res)
        df.columns.name = "X"
        df.index.name = "Time"
        return df
    
    def getModes(self) :
        return [13]


class ReconstructionRao(_TimeDomain.ReconstructionRao, ReconstructionWif_pyABC):
    """First order time reconstruction class"""

class ReconstructionRaoLocal(_TimeDomain.ReconstructionRaoLocal, ReconstructionWif_pyABC):
    """First order time reconstruction class in local"""
    def getModes(self) :
        return _TimeDomain.ReconstructionRaoLocal.getModes(self)
