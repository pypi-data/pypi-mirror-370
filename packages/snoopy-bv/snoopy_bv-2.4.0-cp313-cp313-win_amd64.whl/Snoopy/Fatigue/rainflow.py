"""
Rainflow counting according to AFNOR.
"""

from Snoopy import TimeDomain as td
import numpy as np

class Rainflow(object):
    """Rainflow analysis.

    According to AFNOR.

    Examples
    -------
    >>> rain = Rainflow(signal)
    >>> cycleRanges = rain()
    """

    def __init__( self, signal=None, extreme=None ):
        """Create a Rainflow analysis.

        Parameters
        ----------
        signal : array-like, optional
            Stress array. The default is None.
        extreme : array-like, optional
            Stress local extrema, calculated from 'signal' of not provided. The default is None.

        Examples
        -------
        >>> rain = Rainflow(signal = signal)
        >>> cycleRanges = rain()
        """
        if signal is not None :
            self.extreme = td.getExtrema(signal)
        elif extreme is not None:
            self.extreme = extreme
        self.nExtreme = len(self.extreme)
        self.nCycle = int(len(self.extreme) / 2)
        self._done = False

    @staticmethod
    def extractCycles( extreme ):
        """Get full and half cycle, from extreme list.

        Parameters
        ----------
        extreme : np.ndarray
            Extrema array.

        Returns
        -------
        np.ndarray, ndarray
            Full cycles, half cycles

        """

        cycleIndex = td.cptrf1(extreme)
        allI = np.arange(len(extreme))
        fullCycle = np.where(cycleIndex[ cycleIndex[ allI ] ] == allI)[0]
        full_1 = np.unique(np.minimum( fullCycle,  cycleIndex[ fullCycle ] ))
        full_2 = cycleIndex[ full_1 ]
        fullCycle = np.vstack( [full_1, full_2] ).T
        residual = np.where(cycleIndex[ cycleIndex[ allI ] ] != allI)[0]
        return extreme[fullCycle], extreme[residual]

    @staticmethod
    def duplicateResidual( residual ) :
        """Duplicate the residual.

        Rainflow analysis of duplicated residual should yield full cycle only.

        Parameters
        ----------
        residual : np.ndarray
            The residual

        Returns
        -------
        duplicatedRes : np.ndarray
            Duplicated residual.
        """

        test1 = ( residual[-1] - residual[-2] ) * ( residual[1] - residual[0] )
        test2 = ( residual[-1] - residual[-2] ) * ( residual[0] - residual[-1] )
        if ( test1 > 0. and test2 < 0. ) :
            duplicatedRes = np.append( residual, residual )
        elif ( test1 > 0. and test2 >= 0. ) :
            duplicatedRes = np.append( residual[:-1], residual[1:] )
            duplicatedRes[-1] = residual[-1]
        elif ( test1 < 0. and test2 >= 0. ) :
            duplicatedRes = np.append( residual, residual[1:] )
        elif ( test1 < 0. and test2 < 0. ) :
            duplicatedRes = np.append( residual[:-1], residual )
            duplicatedRes[-1] = residual[-1]
        else :
            raise(Exception('Junction problem'))
        return duplicatedRes

    def _analysis(self):
        """Perform the whole rainflow counting
        """
        #Rainflow on original extremes
        fullCycle, residual = Rainflow.extractCycles( self.extreme )

        #Rainflow on residual (if any)
        if ( len(residual) > 1 ):
            #Duplicate the resiudal
            duplicatedResidual = Rainflow.duplicateResidual(residual)

            #Rainflow on the residual. (Possible check : residual and residual2 should be identical)
            residualCycle, residual2 = Rainflow.extractCycles( duplicatedResidual )

            #Concatenate residual cycles
            self.allCycle = np.concatenate( [fullCycle, residualCycle] )
        else:
            self.allCycle = fullCycle

        self._done = True


    def __call__(self):
        """Return cycle ranges

        Returns
        -------
        np.ndarray
            Cycle range, sorted.
        """

        if not self._done :
            self._analysis()

        return np.sort(np.abs((self.allCycle[:,1] - self.allCycle[:,0])))



def Nallow_Miner(x, S, m, K):
    """
    Compute number of allowed fatigue cycles per stress range (copy from Pluto)

    Parameters
    ----------
    x : array-like
        List of cycles.
    S : array-like
        SN-curve S parameters (one item per slope)
    m : array-like
        SN-curve m parameters (one item per slope).
    K : array-like
        SN-curve K parameters (one item per slope).

    Returns
    -------
    Nallow : array
        Number of allowwed cycles per stress range.

    """

    Nallow = np.zeros(0)

    #First slope
    v = x[x >= S[0]]
    Nallow = np.append(Nallow, K[0]/v**m[0])

    #Other slopes (if any)
    for step in range(1, len(S), 1):
        v = x[(x >= S[step]) & (x < S[step-1])]
        Nallow = np.append(Nallow, K[step]/v**m[step])

    #Infinite slope
    v = x[x < S[-1]]
    constant = K[-1]/v**m[-1]
    Nallow = np.append(Nallow, np.ones(len(v))*constant)

    return Nallow
