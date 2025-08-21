"""
Utils to handle list of sea-states
"""

import numpy as np
import pandas as pd
from Snoopy import Spectral as sp
from Snoopy import logger

class SeaStatesDF( pd.DataFrame ):
    """Class to handle list of sea-state, when spectrum types are identical on all sea-state.
    Derives from pd.DataFrame.

    Implement convenience methods to group/round sea-state parameter to optimize spectral or long-term calculation

    Example
    -------

    >>> ss_df = SeaStatesDF( data = { "Spectrum_0" : ["Jonswap", "Jonswap" , "Jonswap"] ,
                                      "hs_0" : [1.0 , 1.2, 1.1] ,
                                      "tp_0" : [10.0 , 11.2, 10.3],
                                      "gamma_0" : [1.0 , 1.0 , 1.1],
                                      "Heading_0" : [np.pi , np.pi , np.pi],
                                      "SpreadingType_0" : ["Cosn" , "Cosn" , "No"],
                                      "SpreadingValue_0" : [2.0 , 2.0 , 0.0],
                                      "PROB" : [1.0 , 1.0 , 1.0] }   )

    >>> ss_df.to_ssList()

    [<Snoopy.Spectral.seastate.SeaState at 0x270bf2d2630>,
     <Snoopy.Spectral.seastate.SeaState at 0x270bf2d2720>,
     <Snoopy.Spectral.seastate.SeaState at 0x270bd4286d0>]



    """

    @property
    def _specCode(self) :
        return type(  self.loc[:, self._getSpectrumCols()[0]] [0]  )


    @property
    def _constructor(self):
        return SeaStatesDF




    @classmethod
    def FromStarSpec(self , filename):
        """Construct from StarSpec input file

        Parameters
        ----------
        filename : str
            Starspec input file
        """

        raise(NotImplementedError)


    @classmethod
    def FromSeaStateList(cls, ssList) :
        """If seastate are homogeneous, return dataframe of parameter

        Parameters
        ----------
        ssList : list
            List of sea-states

        Returns
        -------
        df : pd.DataFrame
            DataFrame describing sea-state parameters

        """

        nSpec =  [ss.getSpectrumCount() for ss in ssList]
        nSpec = list(set(nSpec))
        if len(nSpec) == 1:
            nSpec = nSpec[0]
        else:
            raise(Exception( "All sea-state should have the same number of modes" ))

        #Fill dataframe with sea-state parameters
        df = cls( index = range(len(ssList)) )

        df.loc[:, "PROB"] =  [ ss.probability for ss in ssList ]


        for ispec in range(nSpec):
            specType =  [ss.getSpectrum(ispec).name for ss in ssList]
            specType = list(set(specType))
            if len(specType) == 1 :
                df.loc[:, f"Spectrum_{ispec:}"] = specType[0]
                for icoef, coef in enumerate(ssList[0].getSpectrum(ispec).getCoefs_name()) :
                    df.loc[:, f"{coef:}_{ispec:}"] =  [ ss.getSpectrum(ispec).getCoefs()[icoef] for ss in ssList]
                df.loc[:, f"Heading_{ispec:}"] =  [ np.rad2deg(ss.getSpectrum(ispec).heading) for ss in ssList]
                df.loc[:, f"SpreadingType_{ispec:}"] =  [ ss.getSpectrum(ispec).getSpreadingType().name for ss in ssList]
                df.loc[:, f"SpreadingValue_{ispec:}"] =  [ ss.getSpectrum(ispec).getSpreadingValue() for ss in ssList]
            else:
                raise(Exception( "Multi-spectrum type not yet implemented in ssList_to_dataframe" ))
        return df


    def get_extended_dimensions(self, name, value, prob ):
        """Add dimension to seastate_df.

        For instance, add the draft information, and modify the probability accordingly.

        Parameters
        ----------
        name : str
            Name
        value : np.ndarray
            Value
        prob : np.ndarray
            Probability assoicated to each value

        Returns
        -------
        SeaStateDf
            The "extruded" sea-state dataframe.
        """

        prob /= np.sum(prob)
        l = []
        for v,p in zip(  value, prob ): # TODO, from Python 3.10  zip( ... , strict = True)
            new = self.copy(deep = True)
            new.PROB *= p
            new.loc[ : , name ] = v
            l.append(new)

        return SeaStatesDF( pd.concat( l ) )



    def has_same_spectra(self):
        """Return true if all sea-state have same parametric shape.
        
        Return False if some spectra are Jonswap and some others Wallop... 
        """
        ispecCols = self._getSpectrumICols()
        return np.all( np.unique( self.values[:,i])==1  for i in ispecCols)
    

            

    def to_ssList( self, convert_period = False ) :
        """Convert to list of Snoopy SeaState.
        
        Parameters
        ----------

        Returns
        -------
        ssList : list
            List of Snoopy seastate.
        """
        if convert_period: 
            self._convert_period() 
        
        if not self.has_same_spectra():
            raise(Exception("SeaStateDF sea-state should all have same shape familily"))
            
        ispecCols = self._getSpectrumICols()

        specClasses = [ getattr( sp, self.values[0,i]  ) for i in ispecCols ]
        
        iargs = [ { coef : self.columns.get_loc( rf"{coef:}_{imode:}") for coef in specClass.getCoefs_name() } for imode, specClass in enumerate( specClasses ) ]
        ihead = [  self.columns.get_loc( f"Heading_{imode:}" ) for imode in range(len(specClasses))  ]
        ispreading_type = [  self.columns.get_loc( f"SpreadingType_{imode:}" ) for imode in range(len(specClasses))  ]
        ispreading_value = [  self.columns.get_loc( f"SpreadingValue_{imode:}" ) for imode in range(len(specClasses))  ]
        iprob = self.columns.get_loc( "PROB" )
               
        val = self.values
        
        ssList = []
        for iss in range(len(self)):
            specList = []
            for imode, ispecCol in enumerate( ispecCols ):
                args =  { k : val[ iss, i ] for k,i in iargs[imode].items() }
                spec = specClasses[imode]( **args , heading = np.deg2rad( val[iss, ihead[imode]]) ,
                                                    spreading_type = sp.SpreadingType.__members__[val[iss, ispreading_type[imode]] ]    ,
                                                    spreading_value = val[iss, ispreading_value[imode]]  ,
                                         )
                specList.append(spec)
            ss = sp.SeaState( specList, probability = val[ iss, iprob ] )
            ssList.append( ss )
        return ssList
    
    def _convert_period( self ) :
        """
        Preprocess dataframe in order to convert to required period by the spetrum constructor. 
        This allows for example to provide tz instead of tp for Jonswap

        Raises
        ------
        NotImplementedError
            If period or psectrum type not recognized.

        Returns
        -------
        None.

        """
        
        for imode, specCol in enumerate( self._getSpectrumCols() ) :
            spec_ = self.iloc[0,:].loc[ specCol ]
            if spec_ == 'Jonswap':
                # identify columns of imode that are not amongst the arguments of the spectrum constructor
                colsNotInCoefs = [c for c in self._getColumns() if c not in self._getCoefsColumns() and rf"_{imode:}" in c]
                
                if not colsNotInCoefs: continue # if empty list then no conversion needed
                
                period = colsNotInCoefs[0].split('_')[0]
                
                if period == 't0m1':
                    func = sp.Jonswap.t0m12tp
                elif period == 'tm2':
                    func = sp.Jonswap.tm2tp               
                elif period == 'tz':
                    func = sp.Jonswap.tz2tp  
                else: 
                    raise NotImplementedError(f"converting {period} to tp is not implemented yet for {spec_}") 
                            
                self[rf"{period:}_{imode:}"] = [func(self.loc[idx, rf"{period:}_{imode:}"], self.loc[idx, rf"gamma_{imode:}"]) for idx in self.index] # apply function to convert to tp
                self.rename(columns = {rf"{period:}_{imode:}":rf"tp_{imode:}"}, inplace = True) # rename col to tp_imode
            
            else:
                pass
                # raise NotImplementedError(f'period conversion not implemented yet for spectrum type: {spec_}')
                
    def getCompacted(self, rounding_dict = {}) :
        """Remove duplicated sea-state (assign higher probability accordingly).
        
        Parameters
        ----------
        rounding_dict : TYPE, optional
            DESCRIPTION. The default is {}.

        Returns
        -------
        SeaStatesDF
            Sea-states DataFrame, without duplicates .

        """
        from Snoopy.Statistics import compact_probability_df

        df_ = self.copy(deep = True)
        df_._convertNamesToInt()
        df_ = df_.astype( {c:int for c in df_.columns if df_.dtypes[c] == object} )

        dfUnique = compact_probability_df(df_, "PROB")
        dfUnique._convertIntToNames()

        return dfUnique

    def _convertNamesToInt(self):
        """Convert str to int, so that sea-states can be sorted
        """
        if not self._specCode == int :
            for i, specCol in enumerate( self._getSpectrumCols()) :
                self.loc[ :, specCol] = self.loc[ :, specCol].apply( lambda x : sp.SpectrumType[x].value )
                self.loc[ :, f"SpreadingType_{i:}"] = self.loc[ :, f"SpreadingType_{i:}"].apply( lambda x :  getattr( sp.SpreadingType, x).__int__() )                
            

    def _convertIntToNames(self):
        if not self._specCode == str :
            for i, specCol in enumerate(self._getSpectrumCols()) :
                self.loc[ :, specCol] = self.loc[ :, specCol].apply( lambda x : sp.SpectrumType(x).name )
                self.loc[ :, f"SpreadingType_{i:}"] = self.loc[ :, f"SpreadingType_{i:}"].apply( lambda x :  sp.SpreadingType(x).name )



    def _getSpectrumCols(self) :
        return [ i for i in self.columns if "Spectrum" in i]
    
    def _getSpectrumICols(self) :
        return [ i for i in range(len(self.columns)) if "Spectrum" in self.columns[i]]


    @property
    def nSpec(self):
        return len( self._getSpectrumCols() )

    def _getCoefsColumns(self) :
        l = []
        for imode, specCol in enumerate( self._getSpectrumCols() ) :
            spec_ = self.iloc[0,:].loc[ specCol ]
            if isinstance(spec_ , str) :
                specClass = getattr( sp, spec_ )
            else :
                specClass = getattr( sp, sp.SpectrumType(spec_).name )
            l.extend ( [  rf"{coef:}_{imode:}" for coef in specClass.getCoefs_name() ] +  [ f"Heading_{imode:}", f"SpreadingType_{imode:}", f"SpreadingValue_{imode:}"] )

        return l
    
    def _getColumns(self) :
        l = []
        for imode, specCol in enumerate( self._getSpectrumCols() ) :
            jmode = specCol.split('_')[1]
            l.extend ( [  c for c in self.columns if ('_'+jmode in c) and (c != specCol) ] )
        return l



    def computeSpectral( self, rao, linear_hs = False, progressBar = True, engine = "SpectralMoments", num_threads = 1, dw = 0.005, w_min=-1, w_max = -1 ):
        """Calculate m0 and m2 for all sea-states, using the fact that m0 and m2 are linear with Hs

        Parameters
        ----------
        rao : sp.Rao
            Transfert functions
        linear_hs : bool, optional
            Ff True, compute for unit hs, and scale back. The default is False.
        progressBar : bool, optional
            If True a progress bar is displayed. The default is True.
        engine : str, optional
                Among ['SpectralMoments', 'ResponseSpectrum']. The default is 'SpectralMoments'.

        Returns
        -------
        m0 : array[nSeaState, nModes]
            Moments of order 0
        m2 : array[nSeaState, nModes]
            Moments of order 2

        """

        #Progress bar does not work in some environment (like pytest)
        if progressBar :
            from tqdm import tqdm
        else :
            tqdm = lambda x, desc : x

        m0 = np.empty( (len(self) , rao.getNModes()) , dtype = float )
        m2 = np.empty( (len(self) , rao.getNModes()) , dtype = float )
        if linear_hs :
            dfUnit = self.getUnitHsDf().reindex()
            m0u, m2u = dfUnit.computeSpectral(rao , linear_hs = False, progressBar = progressBar, engine = engine, dw=dw, w_min = w_min, w_max = w_max, num_threads=num_threads)
            dfUnit_ = dfUnit.reset_index().loc[: , : ].set_index(self._pList() )
            dfAll = self.set_index( self._pList() )
            pos = dfUnit_.loc[  dfAll.index , "index" ].values
            m0[: , :] = m0u[ pos, : ] * self.hs_0.values[: , np.newaxis]**2
            m2[: , :] = m2u[ pos, : ] * self.hs_0.values[: , np.newaxis]**2
            return m0 , m2
        else :
            ssList = self.to_ssList()

            if engine == "ResponseSpectrum":
                for iss, ss in enumerate(tqdm(ssList, desc = "Spectral calculation")) :
                    rSpec = sp.ResponseSpectrum( ss, rao)
                    m0[iss, : ] = rSpec.getM0s()
                    m2[iss, : ] = rSpec.getM2s()
            elif engine == "SpectralMoments" :
                smom = sp.SpectralMoments( ssList, rao, num_threads  = num_threads, dw=dw, w_min = w_min, w_max = w_max )
                m0[:,:] = smom.getM0s()
                m2[:,:] = smom.getM2s()
            else :
                raise(ValueError("Engine should be among ['SpectralMoments', 'ResponseSpectrum']"))

            return m0 , m2


    def getUnitHsDf(self) :
        """Return Sea-state DataFrame with Hs = 1

        Returns
        -------
        SeaStateDf
            Unit Hs seastate dataframe

        """
        dfUnit = self.groupby( [a for a in self._getCoefsColumns() if "hs" not in a] ).Spectrum_0.unique().copy()
        dfUnit.loc[:] = dfUnit.reset_index().loc[ :, "Spectrum_0"][0][0]
        dfUnit = dfUnit.reset_index()
        dfUnit.loc[: , "hs_0"] = 1.0
        dfUnit.loc[: , "PROB"] = np.nan
        return SeaStatesDF( dfUnit )

    def _pList(self):
        return [a for a in self._getCoefsColumns() if "hs" not in a]



if __name__ == "__main__" :

    ssList = [
                sp.SeaState( [ sp.Jonswap(1, 10.001, 1 , np.pi), sp.Jonswap(5, 10, 1 , np.pi/4)] , probability = 0.25),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(2.515, 10, 1)] , probability = 0.5),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(5, 10, 1)] , probability = 0.25),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(5, 10, 1)] , probability = 0.25),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(2.515, 10, 1)] , probability = 0.5),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(8.515, 10, 1)] , probability = 1.0),
                sp.SeaState( [ sp.Jonswap(1, 10, 1), sp.Jonswap(5, 10, 1)] , probability = 0.25),
             ]

    logger.info("Run START")
    df = SeaStatesDF.FromSeaStateList(ssList)
    logger.info("FromSeaStateList STOPSTART")

    ssListNew = df.to_ssList()

    logger.info("To ssList STOPSTART")
    
    dfNew = SeaStatesDF.FromSeaStateList(ssListNew)
    dfCompacted = dfNew.getCompacted(  rounding_dict = {"tp_0" : 2} )
    logger.info("get compacted STOPSTART")
    

    print (dfCompacted)

    ss = sp.SeaState.FromHspecString(  "JONSWAP  HS 1  TP 10  GAMMA 1.0 HEADING 180.  JONSWAP HS 1 TP 10 GAMMA 2.0 HEADING 0.")

    print (ss)
    logger.info("FromHspecString STOPSTART")

    df1 = SeaStatesDF.FromSeaStateList(ssList)
    dfUnit = df1.getUnitHsDf()

    rao = sp.Rao( [ sp.Rao( f"{sp.TEST_DATA:}/rao/heave.rao" ) for i in range(100) ] )

    rao_i = rao.getRaoForSpectral()
    r1 = df1.computeSpectral( rao_i , engine = "ResponseSpectrum" , progressBar = False)
    r2 = df1.computeSpectral( rao , engine = "SpectralMoments" )
