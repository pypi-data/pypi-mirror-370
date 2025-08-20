import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy.Math import edges_from_center, get_dx
from Snoopy import Spectral as sp
from Snoopy import logger

"""
   Function related to discrete scatter diagram.

   Storage type is a pandas.DataFrame, with Hs as index and Tp/Tz as columns. The type of wave period is indicated by the index name

"""


class DiscreteSD( pd.DataFrame ) :

    @classmethod
    def FromTimeSeries(cls, hs, T, hsEdges = np.arange(0,21,0.5), tEdges =  np.arange(1,21,0.5) , T_name = None, dropnull = False ) :
        """Construct scatter-diagram from time series.

        No extrapolation is done, this is simply a 2D histogram

        Parameters
        ----------
        hs : np.ndarray
            Hs time-serie
        T : np.ndarray
            Period Hs time-serie
        hsEdges : np.ndarray, optional
            Edges for Hs. The default is np.arange(0,21,0.5).
        tEdges : np.ndarray, optional
            Edges for period. The default is np.arange(1,21,0.5).
        T_name : str, optional
            Name of the period, among ["tz" , "t0m1" , "tp"]. The default is None.
        dropnull : bool, optional
            Only keep time series datapoints where both hs and T are non-zero. The default is False.
            
        Returns
        -------
        DiscreteSD
            The scatter-diagram

        """
        if dropnull:
            hs_ = hs[(hs != 0.) & (T != 0.)] 
            T_ = T[(hs != 0.) & (T != 0.)] 
        else:
            hs_ = np.copy(hs)
            T_ = np.copy(T)
            
        data_, hsEdges_, tzEdges_ = np.histogram2d( hs_, T_ , bins = [ hsEdges , tEdges ] )
        sdDiscrete = pd.DataFrame( data = data_, index = 0.5*(hsEdges_[:-1] + hsEdges_[1:]), columns = 0.5*(tzEdges_[:-1] + tzEdges_[1:])  )
        sdDiscrete.index.name = "hs"
        sdDiscrete.columns.name = T_name
        return cls(sdDiscrete)

    def __init__(self, *args, **kwargs) :
        """init as standard pandas DataFrame, just ensure that index and columns are float.
        """
        pd.DataFrame.__init__(self, *args, **kwargs)
        if self.columns.dtype == np.dtype("O") :
            self.columns = self.columns.astype(float)
        if self.index.dtype == np.dtype("O") :
            self.index = self.index.astype(float)

    @property
    def _constructor(self):
        return DiscreteSD

    @property
    def dv1( self ):
        return self.index[1] - self.index[0]

    @property
    def n( self ):
        return self.sum().sum()

    @property
    def nv2( self ):
        return len(self.columns)

    @property
    def nv1( self ):
        return len(self.index)

    @property
    def v2name(self):
        return self.columns.name


    @property
    def dv2( self ):
        return self.columns[1] - self.columns[0]

    def makeProbabilityDensity(self):
        """Scale probability so that values are probability density. (integral == 1)
        """
        self /= self.sum().sum() * self.dv1 * self.dv2


    def plotSD(self, ax = None, linewidths= 1.0, density = False, **kwargs) :
        """Plot the scatter diagram

        Parameters
        ----------
        ax : plt.Axes, optional
            Where to plot. The default is None.
        linewidths : float, optional
            Spacing between cells. The default is 1.0.
        **kwargs : any
            Argument passed to seaborn.heatmap

        Returns
        -------
        ax : plt.Axes
            The plot

        Example
        -------
        To get plot with number in each cell :

        >>> sd.plotSD( annot=True, ax=ax, fmt = ".2f", annot_kws = {"fontdict":{"size":8}}, cbar=False), norm=colors.LogNorm(vmin=1e-10, vmax=sd.max().max()), clip = True) )
        """

        import seaborn as sns

        if ax is None :
            fig, ax = plt.subplots()

        sd = self.sort_index(ascending = False, axis = 0)

        sns.heatmap( sd,
                     linewidths = linewidths,
                     ax=ax,
                     **kwargs
                     )
        return ax



    def iso_probability(self , p):
        return self.iso_value(  p * self.sum().sum()  * self.dv1*self.dv2 )


    def iso_value(self , v):
        """Return ISO probability contour.

        Parameters
        ----------
        v : float
            Value

        Returns
        -------
        hs : np.ndarray
            Hs
        tx : np.ndarray
            Period
        """
        from contourpy import contour_generator
        qc = contour_generator( z = self.values , y = self.index.values, x = self.columns.values  )
        vertices = qc.create_contour( v )
        if len(vertices) == 0 :
            hs,tp =  [] , []
        else:
            hs = np.concatenate( [ np.append( c[:,1]  , np.nan) for c in vertices ] )
            tx = np.concatenate( [ np.append( c[:,0] , np.nan) for c in vertices ] )
        return hs , tx


    def iform_iso(self , p) :
        """Return contour based on RP-C205

        Note that this has very little interest over standard iform, which should be prefered.

        1- Find Hs with exceedance probability p
        2- Find probability density for this Hs
        3- Get iso density contour

        Parameters
        ----------
        p : float
            Probability

        Returns
        -------
        Tuple of array
            The contour
        """
        from Pluto.statistics.ecdf import Empirical
        empHs = Empirical.FromBinCounts( *self.get_v1_edges_count() )
        hs = empHs.isf( p )
        logger.debug(f"IFORM_ISO, Hs = {hs:}")
        hs_r = self.index[ self.index.get_loc( float(hs) , method = "nearest" ) ]

        # Get V2 at hs location
        t = self.get_v2_conditional_pdf( hs_r ).idxmax()
        p_density = self.loc[ hs_r, t ]
        return self.iso_value( p_density )


    def toStarSpec(self, gamma = None):
        """Convert to starspec

        Parameters
        ----------
        gamma : float, optional
            gamma value. Used to convert period to something handled by StarSpec. The default is None.

        Returns
        -------
        str
            The scatter-diagram, in StarSpec format

        """
        t_def = self.columns.name.lower()
        return toStarSpec(self , period = t_def, gamma = gamma )


    def get_v1_pdf(self) :
        hs_hist = self.sum(axis = 1)
        return hs_hist / (hs_hist.sum()*self.dv1)

    def get_v1_cdf(self):
        edges = self.get_v1_edges()
        return pd.Series( np.insert( np.cumsum( self.sum(axis = 1 )) , 0 , 0. ) / self.n , index = edges )

    def get_v1_sf(self):
        hs_pdf = self.get_v1_pdf()
        return pd.Series(  1. - np.cumsum( hs_pdf.values )*self.dv1, index = self.index.values + self.dv1*0.5 )


    def sample(self , n = 1) :
        a = (self.stack()*n).astype(int)
        n_tot = a.sum() * n
        s = np.zeros( (n_tot, 2), dtype = float )
        i = 0
        for ht, n in a.iteritems() :
            s[i:i+n, 0] = ht[0]
            s[i:i+n, 1] = ht[1]
            i += n
        return s

    def get_v1_edges(self):
        return edges_from_center(self.index.values)

    def get_v2_edges(self):
        return edges_from_center(self.columns.values)

    def get_v1_edges_count(self):
        return edges_from_center(self.index.values) , self.sum(axis = 1.).values


    def getCountScatterDiagram(self, n = None ):
        if n is None :
            n = self.sum().sum()  # Just make the scatter diagram as integer
        sd_count = self * n / self.n
        sd_count = sd_count.round(0).astype(int)
        return sd_count


    def getAggregated(self , new_edges , axis = 0, eps = 0.001 ):
        """Aggregate scatter-diagram by larger bins.

        Parameters
        ----------
        new_edges : np.ndarray
            New bin edges.
        axis : int, optional
            Axis. The default is 0.
        eps : float, optional
            Tolerance. The default is 0.001.

        Returns
        -------
        DiscreteSd
            Aggregated scatter-diagram.
        """


        if isinstance( new_edges , int) :
            old_edges = edges_from_center(self.axes[axis])
            new_edges = old_edges[::new_edges]
            if new_edges[-1] < old_edges[-1] :
                new_edges = np.append( new_edges, 2*new_edges[-1]-new_edges[-2] )

        newCenter = (new_edges[:-1] + new_edges[1:])*0.5
        dtype = self.dtypes.values[0]
        if axis == 0 :
            newSd = self.__class__( index = pd.Index(newCenter , name = self.index.name) , columns = self.columns  )
            for i, c in enumerate(newCenter) :
                newSd.loc[c , : ] = self.loc[ new_edges[i]+eps : new_edges[i+1]-eps , :  ].sum()
                newSd.loc[c , : ] += self.loc[ new_edges[i+1]-eps : new_edges[i+1]+eps , :  ].sum() * 0.5
                newSd.loc[c , : ] += self.loc[ new_edges[i]-eps : new_edges[i]+eps , :  ].sum() * 0.5
        elif axis == 1 :
            newSd = self.__class__( index = self.index, columns = pd.Index(newCenter , name = self.columns.name ))
            for i, c in enumerate(newCenter) :
                newSd.loc[: , c ] = self.loc[ : , new_edges[i] + eps : new_edges[i+1] - eps  ].sum(axis = 1)
                newSd.loc[: , c ] += self.loc[ : , new_edges[i]-eps:new_edges[i] + eps  ].sum(axis = 1) * 0.5
                newSd.loc[: , c ] += self.loc[ : , new_edges[i+1]-eps:new_edges[i+1] + eps  ].sum(axis = 1) * 0.5

        #Check that total count is there
        if not ( np.isclose(  self.n , newSd.n) ) :
            print (self.n , newSd.n)
            raise(Exception("Problem in aggregating the scatter diagram"))

        return self.__class__(newSd).astype(dtype)

    def makeEven( self, dv1 = None , dv2 = None ):
        """Make the bin size constant.
        """
        #TODO : use "getAggregated" ?

        if dv1 is None :
            dv1 = np.min(np.diff( self.index.values ))

        newIndex = np.arange( self.index.values[0] , self.index.values[-1] , dv1 )
        for i in newIndex :
            if i not in self.index :
                if np.min(np.abs(self.index - i)) > 1e-5 :
                    self.loc[i , :] = np.zeros( (self.nv2), dtype = float )

        self.sort_index(inplace = True)

        if dv2 is None :
            dv2 = np.min(np.diff( self.columns.values ))
        newIndex = np.arange( self.columns.values[0] , self.columns.values[-1] , dv2 )
        for i in newIndex :
            if i not in self.columns :
                if np.min(np.abs(self.columns - i)) > 1e-5 :
                    self.loc[: , i] = np.zeros( (self.nv1), dtype = float )
        self.sort_index(axis = 1, inplace = True)


    def isEvenlySpaced(self, tol) :
        if get_dx(self.index.values, tol ) is None:
            return False
        if get_dx(self.columns.values, tol ) is None:
            return False
        return True

    def get_v2_conditional_pdf(self , v1, method = None):
        ihs = self.index.get_loc( v1, method = method )
        return (self.iloc[ihs,:] / (self.iloc[ihs,:].sum() * self.dv2) )


    def get_v2_conditional_sf(self, v1):
        t_pdf = self.get_v2_conditional_pdf(v1)
        return pd.Series(  1. - np.cumsum( t_pdf.values )*self.dv2, index = self.columns.values + self.dv2 * 0.5 )

    def getWithoutZeros(self):
        sdNew = self.loc[ self.sum(axis = 1) > 0 , :].copy(deep=True)
        sdNew = sdNew.loc[ :, sdNew.sum(axis = 0) > 0 ]
        return sdNew


    def to_seastate_list(self, headingList, gamma , spreadingType , spreadingValue ):
        """Create list of Jonswap sea-state from scatter-diagram

        Parameters
        ----------
        headingList : array like or int
            List of headings  and associated probability list. If integer "n", iso-probability is assumed, with n steps over 2*pi.
        gamma : float
            Gamma value.
        spreadingType : sp.SpreadingType
            Spreading function
        spreadingValue : float
            Spreading value

        Raises
        ------
        ValueError
            If period is not 'tp', 'tz' or 't0m1'.

        Returns
        -------
        ssList : list( sp.SeaState )
            List of sea-state
        """

        if isinstance(headingList , int) :
            headingList = np.linspace( 0 , np.pi*2 , headingList, endpoint = False )
            probList = np.full( (len(headingList)) , 1. / len(headingList) )
        elif len( np.array( headingList ).shape ) == 1 :
            probList = np.full( (len(headingList)) , 1. / len(headingList) )
        elif len( np.array( headingList ).shape ) == 2 :
            probList = headingList[:,1]
            headingList = headingList[:,0]
        else :
            raise(Exception())

        ssList = []
        for hs, row in self.iterrows():
            for t, prob in row.items():
                if self.columns.name.lower() == 'tp':
                    tp = t
                elif self.columns.name.lower() == 'tz':
                    tp = sp.Jonswap.tz2tp(t,gamma)
                elif self.columns.name.lower() == 't0m1':
                    tp = sp.Jonswap.t0m12tp(t,gamma)
                else:
                    raise ValueError("Scatter diagram columns name should be either 'Tp', 'Tz' or 'T0m1', not {self.columns.name:}")

                for head, prob_head in zip(headingList, probList):
                    spec = sp.Jonswap(hs=hs, tp=tp, gamma = gamma,  heading = head, spreading_type = spreadingType , spreading_value = spreadingValue )
                    ss = sp.SeaState( spec , probability = prob * prob_head )
                    ssList.append(ss)
        return ssList

    def getTruncated(self , hsMax ):
        """Remove data above hsMax, and report the probablility to Hs = 0. (the ship stay in the port !)

        Parameters
        ----------
        hsMax : float
            Maximum allowed Hs

        Returns
        -------
        DiscreteSD, float
            Truncated scatter diagram, fraction of time below hsMax
        """
        return truncate(self, hsMax)


"""
Functional API kept for compatibility purpose
"""

def toStarSpec(data, period=None, gamma = None):

    # Return a string compatible with StarSpec format
    nHs, nTz = data.shape

    if period is None :
        period = data.columns.name
        logger.info(f"Period for scatter diagram set to {period:}")

    if period.lower() == "tz":
        tList = data.columns.values
        str_ = "SCATTER NB_HS  {}  NB_TZ   {}\n".format(nHs, nTz)
    elif period.lower() == "tp":
        tList = data.columns.values
        str_ = "SCATTER NB_HS  {}  NB_TP   {}\n".format(nHs, nTz)
    elif period.lower() == "t0m1":
        tList = sp.Jonswap.t0m12tp( data.columns.values , gamma = gamma )
        if gamma is None :
            raise(Exception("toStarSpec : gamma required to convert from T0m1" ))
        str_ = "SCATTER NB_HS  {}  NB_TP   {}\n".format(nHs, nTz)
    else :
        raise(Exception(f"Do not know how to convert {period:} to Tp"))

    for t in tList :
        str_ += "{:.3f}  ".format(t)

    str_ += "\n"
    pFormat = "{:.3e} " * (nTz - 1) + "{:.3e}\n"
    for i in data.index:
        str_ += "{:.3f} ".format(i) + pFormat.format(*data.loc[i, :])
    str_ += "ENDSCATTER\n"
    return str_


def getMarginalHs( table ):
    nHs = table.shape[0]
    sf, densityHs = np.zeros((nHs), dtype = "float64"), np.zeros((nHs), dtype = "float64")
    for iHs in range( nHs  ) :
        densityHs[iHs] = table.iloc[iHs , :].sum()
        sf[iHs] = 1. - np.sum( densityHs[0:iHs] )

    d_hs = table.index.values[1] - table.index.values[0]

    return table.index.values - d_hs/2. , sf


def truncate(table, hsMax):
    """Remove data above hsMax, and report the probablility to Hs = 0. (the ship stay in the port !)
    """
    below = table.loc[:hsMax, :].copy()
    ratio = below.sum().sum() / table.sum().sum()
    below.loc[0.] = below.sum(axis=0) * (1 - ratio) / ratio
    below.sort_index(inplace=True)
    return below, ratio



def removeZeros( sd ):
    sdNew = sd.loc[ sd.sum(axis = 1) > 0 , :]
    sdNew = sdNew.loc[ :, sdNew.sum(axis = 0) > 0 ]
    return sdNew






if __name__ == "__main__":

    import numpy as np
    import pandas as pd
    logger.setLevel(10)

    from Snoopy.Dataset import rec34_SD

    rec34_SD.plotSD(cmap = "cividis")


