import pandas as pd
import _TimeDomain


class ReconstructionQtf(_TimeDomain.ReconstructionQtf):
    """Qtf time reconstruction class in glbal reference frame."""

    def evalDf( self , time , *args, **kwargs) :
        data = self.__call__(time, *args, **kwargs)
        return pd.DataFrame( index = time , data = data , columns = self.getQtf().getModes() )

    def evalSe( self, *args, **kwargs) :
        return self.evalDf(*args, **kwargs).iloc[:,0]

    def getModes(self):
        return self.getQtf().getModes()


class ReconstructionQtfLocal(_TimeDomain.ReconstructionQtfLocal):
    """Qtf time reconstruction class in local reference frame."""

    def evalDf( self , time , *args, **kwargs) :
        data = self.__call__(time, *args, **kwargs)
        return pd.DataFrame( index = time , data = data , columns = self.getQtf().getModes() )

    def evalSe( self, *args, **kwargs) :
        return self.evalDf(*args, **kwargs).iloc[:,0]

    def getModes(self):
        return self.getQtf().getModes()
