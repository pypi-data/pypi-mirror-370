import pandas as pd
import numpy as np
from scipy.stats import rayleigh
from matplotlib import pyplot as plt
from Snoopy.PyplotTools.statPlots import distPlot, rpPlot
from Snoopy import logger

class UpCrossAnalysis( pd.DataFrame ):
    """Class dealing with upcrossing analysis.

    Derive from Pandas dataframe, and is generally constructed from time series.

    Example
    -------

    >>>upCross = UpCrossAnalysis.FromTs( timeSeries )

    """

    def __init__(self, *args, **kwargs) :

        method = kwargs.pop("method", None)

        pd.DataFrame.__init__(self, *args, **kwargs)

        # if "Maximum" not in self.columns :
        #     logger.info("Re-indexed UpCrossAnalysis does not have 'Maximum' as column, return standard dataframe")
        #     self.__class__ = pd.DataFrame

        self.attrs["se"] = None

        self.attrs["method"] = method


    @property
    def se(self) :
        if "se" in self.attrs.keys():
            return self.attrs[ "se" ]

    @property
    def _constructor(self):
        return UpCrossAnalysis

    @classmethod
    def Merge( cls, listUpCross ):
        """Merge several upcrossing analysis.

        Parameters
        ----------
        listUpCross : list of upCrossing anlysis
            list of upCrossing anlysis

        Returns
        -------
        UpCrossAnalysis
            Merged data.

        """
        return UpCrossAnalysis( pd.concat( listUpCross ).reset_index() )


    @classmethod
    def FromTs( cls, se, threshold = "mean", method = "upcross"):
        """Perform up-crossing analysis.

        Parameters
        ----------
        se : pd.Series
            Time-trace to analyse.
        threshold : float, optional
            upcrossing threshold. The default is "mean".

        Returns
        -------
        UpCrossAnalysis
            Up-crossing data

        """
        if isinstance(se, pd.DataFrame) : # Convert single columns pd.DataFrame to to pd.Series
            if se.shape[1] == 1:
                se = se.iloc[:,0]
            else :
                raise(Exception("Input should be pd.Series, or pd.DataFrame with a single column"))

        if method.lower() == "upcross" :
            res = cls(upCrossMinMax( se, threshold = threshold ) , method = method.lower() )
        elif method.lower() == "updown" :
            res = cls(peaksMax( se, threshold = threshold ), method = method.lower() )
        else :
            raise(Exception(f"method '{method:}' not available"))

        res.attrs["se"] = se
        return res



    def plotTime(self , ax = None, **kwargs):
        """Plot time series together with maximum, minimum and cycle bounds
        """
        if ax is None :
            fig, ax = plt.subplots()

        if len(self) > 0 :
            plotUpCross( self, ax=ax,  **kwargs )
        if self.se is not None :
            self.se.plot(ax=ax)
        return ax


    def plotDistribution( self, ax = None, data = "Maximum", addRayleigh = None, **kwargs ):
        """Plot upcrossing distribution

        Parameters
        ----------
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        data : str, optional
            Columns to plot. The default is "Maximum".
        addRayleigh : None, float or "auto", optional
            Plot Rayleight distribution
            addRayleigh == "auto" : standard deviation calculated from time series
            addRayleigh == float : standard deviation given
            addRayleigh == None : Do not plot
            The default is None.

        Returns
        -------
        ax : TYPE
            The graph "ax".
        """

        if ax is None :
            fig, ax = plt.subplots()


        if addRayleigh is not None :
            if addRayleigh == "auto":
                addRayleigh = rayleigh(0.0,  scale = self.se.std() )
            else :
                addRayleigh = rayleigh(0.0,  scale = addRayleigh )

        distPlot( data = self.loc[: , data].values,
                  frozenDist = addRayleigh,
                  ax=ax,
                  **kwargs
                  )
        return ax

    def plotReturnPeriod( self, data = "Maximum", duration = None, ax=None,**kwargs ):
        """Plot return level.

        Parameters
        ----------
        data : str, optional
            "Maximum" or "Minimum". The default is "Maximum".
        duration : float, optional
            Underlying duration, if none, duration is calculated from underlying time-series. The default is None.
        **kwargs : -
            Argument passed to Snoopy.PyplotTools.rpPlot()

        Returns
        -------
        axes
            The plot

        """
        if duration is None :
            duration = self.se.index.max() - self.se.index.min()
        return rpPlot(data = self.loc[: , data].values, duration = duration, frozenDist=None, ax=ax,**kwargs )


    def mapInCycle( self , se,  name = "target", fun = np.max ):
        """Map maxima from other time series on current cycles, add a columns to the input dataframe

        Parameters
        ----------
        se : pd.Series
            Series to map.
        name : str, optional
            Name of the columns to be added. The default is "target".
        fun : function, optional
            Function to apply to the input series. The default is np.max.

        Returns
        -------
        None.

        """
        self.loc[: , name] = np.nan
        for i, row in self.iterrows() :
            self.loc[i , name]  = fun( se.loc[ row.upCrossTime : row.upCrossTime + row.Period  ].values )
        return


    def getWithMinSpacing(self , spacing, correct = True) :
        """Ensure minimum spacing between two events (for "updown" method only)

        Parameters
        ----------
        minSpacing : float
            Spacing between two events

        Returns
        -------
        UpCrossingAnalysis
        """

        from Snoopy.TimeDomain.decluster import minSpacingFilter_array

        if self.attrs["method"] != "updown" :
            raise(Exception( f"getWithMinSpacing not implemented for method {self.attrs['method']:}" ))

        up = self.copy(deep = True)

        time , _  = minSpacingFilter_array( up.MaximumTime.values, value = up.Maximum.values , spacing = spacing )
        upNew = up.set_index( "MaximumTime" ).loc[time, :] #.reset_index()

        up = up.reset_index().set_index("MaximumTime")
        for i, c in upNew.iterrows() :
            for t in up.index.values :
                if abs(i - t) < spacing and i != t :
                    logger.debug(f"Gathering peaks {t:} and {i:}")
                    upNew.loc[i, "upCrossTime"] = min( upNew.loc[i, "upCrossTime"] ,up.loc[t, "upCrossTime"])
                    upNew.loc[i, "downCrossTime"] = max( upNew.loc[i, "downCrossTime"] ,up.loc[t, "upCrossTime"])

        upNew.loc[:, "Period"] = upNew.loc[:, "downCrossTime"] - upNew.loc[:, "upCrossTime"]

        return upNew.reset_index()



def getUpCrossID( array, threshold ) :
    """
    Get the upcrossing indices

    Parameters
    ----------
    array : 1D array
        Time-series
    threshold : float
        Upcrossin threshold.

    Returns
    -------
    array
        upCrossing indexes (numpy 1D array of integer).

    """

    if isinstance(array, pd.Series):
        array = array.values

    if len(np.shape(array)) > 1:
        raise ValueError('array should be one-dimensional')

    isCross = (array[:-1] <= threshold) & (array[1:] > threshold)
    return np.where( isCross )[0]


def getDownCrossID( array, threshold ) :
    """Get the downcrossing indices

       Input :
               array : numpy 1D array
               threshold
       Output :
               upCrossing indexes (numpy 1D array of integer)

    """
    if isinstance(array, pd.Series):
        array = array.values

    if len(np.shape(array)) > 1:
        raise ValueError('array should be one-dimensional')

    isCross = (array[:-1] > threshold) & (array[1:] <= threshold)
    return np.where( isCross )[0]


def getPeaksBounds(se, threshold):
    """Get peaks, identified by the up and down crossing of a threshold
    """
    array = se.values
    up_ = getUpCrossID( array, threshold )
    down_ = getDownCrossID( array, threshold )

    if len(up_) == 0 :
        return np.array([], dtype = int) , np.array([], dtype = int)

    if down_[0] < up_[0] :
        down_ = down_[1:]

    if len(down_) != len(up_):
        up_ = up_[:-1]

    return up_, down_


def peaksMax( se, threshold ) :

    up_, down_ = getPeaksBounds( se, threshold )

    maxIndex = np.empty( up_.shape , dtype = int )

    for i in range(len( up_ )) :
        maxIndex[i] = up_[i] + se.values[ up_[i] : down_[i]+1 ].argmax()

    return pd.DataFrame( data = { "Maximum" : se.iloc[ maxIndex  ] ,
                                  "MaximumTime" : se.index[ maxIndex ] ,
                                  "upCrossTime" : se.index[ up_ ] , "downCrossTime":  se.index[ down_ ],
                                  "Period" : se.index[ down_ ] - se.index[ up_ ]} )



"""
#Numba works but does not accelerate a lot the calculation (replace dtype=int by dtype=int32)
from numba import jit, float64 , int64, int32 , int16
from numba.types import Tuple
@jit(  Tuple((float64[:], float64[:],int32[:],int32[:]))(float64[:] , int64[:]) , nopython = True  )
"""
def minMax(array, upCrossID) :
    """
       Return max and min and position between each cycle
    """
    minimumTime = np.empty( ( len(upCrossID)-1 ) , dtype = int)
    maximumTime = np.empty( ( len(upCrossID)-1 ) , dtype = int)
    for iPoint in range(len(upCrossID)-1) :
        minimumTime[iPoint] = upCrossID[iPoint] + array[ upCrossID[iPoint] : upCrossID[iPoint + 1] ].argmin()
        maximumTime[iPoint] = upCrossID[iPoint] + array[ upCrossID[iPoint] : upCrossID[iPoint + 1] ].argmax()
    minimum =  array[ minimumTime ]
    maximum =  array[ maximumTime ]
    return minimum , maximum , minimumTime , maximumTime


def upCrossMinMax( se, upCrossID = None , threshold = "mean" ) :
    """
       Perform the "whole" upcrossing analysis
    """

    array = se.values

    #Compute threshold if not given
    if threshold == "mean" :
       threshold = np.mean(array)


    #Compute upCrossing index if not given
    if upCrossID is None :
       upCrossID = getUpCrossID( array , threshold = threshold )

    if len(upCrossID) == 0 :
        return pd.DataFrame( data = { "Minimum" : [] , "Maximum" : [] ,
                                 "MinimumTime" : [] , "MaximumTime" : [] ,
                                 "upCrossTime" : [] , "Period": []  } )

    #Fill values
    periods = np.empty( ( len(upCrossID)-1 )  , dtype = type(se.index.dtype) )
    minimum , maximum , minimumTime , maximumTime = minMax( array , upCrossID )
    minimumTime = se.index[ minimumTime ]
    maximumTime = se.index[ maximumTime ]
    upCrossTime = se.index[ upCrossID[:-1]]
    periods = se.index[ upCrossID[1:]] - se.index[upCrossID[:-1]]
    return pd.DataFrame( data = { "Minimum" : minimum , "Maximum" : maximum ,
                                  "MinimumTime" : minimumTime , "MaximumTime" : maximumTime ,
                                  "upCrossTime" : upCrossTime , "Period": periods  } )



def getUpCrossDist(upCrossDf, variant = (0.,0.) ) :
    """Get Up-crossing distribution from upCrossMinMax result
    """
    from Snoopy.Statistics import probN
    N = upCrossDf.shape[0]
    p_ex = 1 - probN(N , variant = variant )
    df = pd.DataFrame(index=p_ex,columns=['Minimum','Maximum'])
    df.Minimum = upCrossDf.Minimum.sort_values(ascending=True).values
    df.Maximum = upCrossDf.Maximum.sort_values(ascending=False).values
    return df


def plotUpCross( upCrossDf , ax = None, cycleLimits = False ) :
    """
       Plot time trace together with extracted maxima
    """
    from matplotlib import pyplot as plt
    if ax is None : fig , ax = plt.subplots()
    if cycleLimits :
        for i in range(len(upCrossDf)) :
            ax.axvline( x = upCrossDf.upCrossTime[i] , label = None , alpha = 0.3)
            ax.axvline( x = upCrossDf.upCrossTime[i] + upCrossDf.Period[i] , label = None, alpha = 0.3)
    # else :
    #     ax.plot( upCrossDf.upCrossTime , [0. for i in range(len(upCrossDf))]  , "+" , label =  )
    #     ax.plot( upCrossDf.upCrossTime.iloc[-1] + upCrossDf.Period.iloc[-1] , 0.  , "+" , label = None)

    ax.plot( upCrossDf.MaximumTime , upCrossDf.Maximum , "o" , label = "Max", color ="b")

    if "MinimumTime" in upCrossDf.columns :
        ax.plot( upCrossDf.MinimumTime , upCrossDf.Minimum , "o" , label = "Min", color ="r")

    ax.legend(loc = 2)
    return ax

def plotUpCrossDist( upCrossDist , ax = None, label=None):
    """
       Plot upcrossing distribution
    """
    from matplotlib import pyplot as plt
    if ax is None : fig , ax = plt.subplots()
    prob = np.concatenate([upCrossDist.index,upCrossDist.index[::-1]])
    values = np.concatenate([upCrossDist.Minimum.values,upCrossDist.Maximum.values[::-1]])
    ax.plot(values,prob,'-+',label=label)
    ax.set_ylabel('Exeedence probability')
    ax.set_yscale('log')
    if label is not None: ax.legend()
    return ax

















