import numpy as np
from matplotlib import pyplot as plt
import _Spectral

class Spreading_pyABC() :

    def plot( self, ax=None, **kwargs ):
        if ax is None :
            fig, ax = plt.subplots()

        angle = np.linspace(0, np.pi*2, 360)
        ax.plot( np.rad2deg(angle), self.compute(angle), **kwargs )
        return ax


class Cos2s( _Spectral.Cos2s, Spreading_pyABC ) :
    pass

class Wnormal( _Spectral.Wnormal, Spreading_pyABC ) :
    pass

class Cosn( _Spectral.Cosn, Spreading_pyABC ) :

    @staticmethod
    def spreading_to_n(spreading):
        """ For ERA5/ECMWF variant """
        a, b, c, d = 0.19561774, 0.78264583, -0.53213193, 0.57543844
        return (np.log((spreading-a)/b)/c )**(1/d)

    @staticmethod
    def n_to_spreading(n):
        """ For ERA5/ECMWF variant """
        a, b, c, d = 0.19561774, 0.78264583, -0.53213193, 0.57543844
        return a + b * np.exp( c * n**d  )


def swandeg_to_spreading( dspr, spreadingModel  ) :
    """Convert spreading from Swan to Cosn, Wnormal or Cos2s parameter
    """

    from scipy.optimize import root_scalar
    return root_scalar( lambda x :  spreadingModel( x, 0. ).getSwanDeg() - dspr, bracket = [spreadingModel.getMinCoef(), spreadingModel.getMaxCoef() ]  ).root
