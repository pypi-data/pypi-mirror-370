"""Convenience functions to compute long-term value with RAOs. The actual long-term formulas are in "LongTermSpectral" class, which is used by all the routines here defined.

Compare to class "LongTerm" and "LongTermSpectral", it handles the spectral moments calculation

LongTermRayleighABC ==> Abstract base class for all analysis with Rayleigh as short-term distribution. 

longTermSDABC ==> Specialization of LongTermRayleighABC when the sea-state are given as a scatter-diagram

LongTermRao ==> Cases where the input is linear RAOs and a list of sea-state

longTermSD ==> Cases where the input is linear RAOs and a scatter-diagram  (inherits longTermSDABC)

LongTermQuadDamping ==> Stochastic linearisation of roll damping, using a list of sea-state as input.

LongTermQuadDampingSD ==> Stochastic linearisation of roll damping, using a scatter-diagram as input
"""

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
from Snoopy import Statistics as st
from Snoopy import logger


class LongTermRayleighABC():
    """Abstract class that contains common function to calculate long-term response when short-term is Rayleigh distributed
    """

    def __init__(self, * , ssList, dss, nModes, engine = "python", sht_kwargs = {}) :
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        ssList : list
            list of seastate
        dss : float, optional
            Sea-state duration. The default is 10800.
        nModes : int
            Number of quantities to be computed. Generally automatically set in child class
        engine : str
            Which engine to use for the long-term calculation, among ["python" , "cpp" , "numba"]
        sht_kwargs : dict
            Keyword argument passed to the short-term calculator
        """
        
        self.ssList = ssList
        self._ssProb = np.array( [ ss.probability for ss in self.ssList ] )
        self._m0s_m2s = None
        self._spectralStats = None
        self._lt = None
        self._dss = dss
        self.nModes = nModes
        self.engine = engine
        self.sht_kwargs = sht_kwargs


    @property
    def dss(self):
        return self._dss


    @dss.setter
    def dss(self, dss):
        self._dss = dss
        if self._lt is not None:
            for i in range(self.nModes) :
                self._lt[i].dss = dss
        return self._dss


    def _compute_m0s_m2s(self):
        #TO BE IMPLEMENTED IN CHILD-CLASS, Return m0s and m2s
        raise(NotImplementedError)


    @property
    def m0s_m2s(self):
        """Return m0s and m2s.

        Returns
        -------
        tuple
            ( m0s, m2s )

        """
        if self._m0s_m2s is None:
            logger.info("Running short-term calculation")
            self._m0s_m2s = self._compute_m0s_m2s( )
            logger.info('Ok')

        return self._m0s_m2s


    @property
    def spectralStats(self):
        if self._spectralStats is None :
            self._spectralStats = sp.SpectralStats( *self.m0s_m2s )
        return self._spectralStats


    @m0s_m2s.setter
    def m0s_m2s(self, m0s_m2s):
        #TODO: check ?
        self._m0s_m2s = m0s_m2s


    @property
    def longTerm(self):
        if self._lt is None :
            m0s, m2s = self.m0s_m2s
            shtStats = sp.SpectralStats( m0 = m0s[:,:] , m2 = m2s[:,:] )
            self._lt = [st.LongTermSpectral( shtStats.Rs[:,i] , shtStats.Rtz[:,i], probabilityList = self._ssProb, dss = self.dss, engine = self.engine ) for i in range(self.nModes) ]
            
        return self._lt


    def _get_default_i_rao(self, i_rao) :
        if i_rao is None :
            if (self.nModes == 1) :
                return 0
            else :
                raise(ValueError("Index of RAO should be provided" ) )
        else :
            return i_rao

    def x_to_p(self, x, *args, **kwargs):
        """Return non-exceedance probability of x.

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        list
            Non-exceedance probability (on all 'mode' in the RAO)
        """
        return [lt.x_to_p(x, *args, **kwargs) for lt in self.longTerm ]


    def meanRtz(self):
        """Mean up-crossing period.

        Returns
        -------
        np.ndarray
            List of mean up-crossing period
        """
        return np.array([lt.meanRtz() for lt in self.longTerm ])
    

    def fatigue_damage(self, sn_curve, duration):
        """Return cumulative damage on the given duration.

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve
        duration : float
            Duration (years)

        Returns
        -------
        np.ndarray
            Cumulated fatigue damage.
        """
        return np.array([lt.fatigue_damage(sn_curve, duration) for lt in self.longTerm ])
    

    def fatigue_life(self, sn_curve):
        """Return fatigue life.

        Parameters
        ----------
        sn_curve : SnCurve 
            SN-Curve or list of SN-Curve

        Returns
        -------
        np.ndarray
            Fatigue life (years)
        """
        # check if list
        if hasattr(sn_curve, '__len__'):
            return_array=np.array([])
            for i,lt in enumerate(self.longTerm):
                res=lt.fatigue_life_num(sn_curve[i])
                return_array = np.append(return_array,res )
        
            return return_array
        else :
            return np.array([lt.fatigue_life_num(sn_curve) for lt in self.longTerm ])
    
    
    def fatigue_life_mean_corr(self, sn_curve, ReEQ, s_mean, element_type):
        """Return fatigue life.

        Parameters
        ----------
        sn_curve : SnCurve
            SN-Curve or list of SN-Curve
        ReEQ : float
            Yielding stress (MPa)
        s_mean : float
            mean stress for the loading condition considered (MPa)
            or list list of mean stresses for each RAO
        element_type : str
            "plated_joint" or "cut_edge" depending on the element considered
            
        Returns
        -------
        np.ndarray
            Fatigue life (years)
        """
        # check if not list 
        if isinstance(s_mean, float):   
            return np.array([lt.fatigue_life_mean_corr(sn_curve, ReEQ, s_mean, element_type) for lt in self.longTerm ])
        else:
            return_array=np.array([])
            for i,lt in enumerate(self.longTerm):
                res=lt.fatigue_life_mean_corr(sn_curve[i], ReEQ, s_mean[i], element_type)
                return_array = np.append(return_array,res )
        
            return return_array

    
    
    def x_to_pcycle(self, x, *args, **kwargs):
        return np.array([lt.x_to_pcycle(x, *args, **kwargs) for lt in self.longTerm ])
    

    def pcycle_to_x(self , p , *args, **kwargs) :
        """Value at given cycle exceedance probability.

        Parameters
        ----------
        pcycle : float
            Cycle exceedance probability

        Returns
        -------
        x : float
            Level with exceedance probability of pcycle
        """
        return np.array([lt.pcycle_to_x(p, *args, **kwargs) for lt in self.longTerm ])


    def rp_to_x(self,rp, num_threads = 1):
        """Compute return values corresponding to return period rp.

        Parameters
        ----------
        rp : float
            Return period, in year.

        Returns
        -------
        list(float)
            Return values
        """
        if num_threads > 1 : # Not recommended in general, the overhead is too large...
            logger.warning("num_threads > 1 is generally inefficient here.")
            from multiprocessing import Pool
            from functools import partial
            p = Pool(num_threads)
            res = p.map( partial( lt_calc , rp = rp ) , self.longTerm )
            p.close()  
            p.join()  
            return res
        else :
            return [lt.rp_to_x(rp) for lt in self.longTerm ]


    def p_to_x(self, p, *args, **kwargs):
        """Return the non-exceedance probability of x in duration (year).

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        list(float)
            cdf  (i.e.  P( x < X )  )
        """
        return [lt.p_to_x(p, *args, **kwargs) for lt in self.longTerm ]


    def longTermSingle(self, i_rao = None):
        """Return the underlying "LongTerm" class, for a single RAO."""

        i_rao = self._get_default_i_rao(i_rao)
        return self.longTerm[i_rao]




class LongTermSDABC( LongTermRayleighABC ):

    def __init__( self,  nModes, sd, nb_hstep, gamma, spreadingType = sp.SpreadingType.No, 
                 spreadingValue = 3., dss = 10800, engine = "python", sht_kwargs = {} ) :
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        rao : sp.Rao
            RAO, ready for spectral calculation (symmetrized). Can contain several 'mode'
        sd : DiscreteSD
            The scatter diagram
        nb_hstep : integer
            Number of heading step (36 would lead to a 10 degree step).
        gamma : float
            gamma value for Jonswap spectrum.
        spreadingType : sp.spreadingType
            Spreading type
        spreadingValue : float
            Spreading value
        dss : float, optional
            Sea-state duration. The default is 10800.

        Example
        -------
        >>> lt_sd = LongTermSD(rao, rec34_SD, 36 , 1.5, spreadingType = sp.SpreadingType.Cosn, spreadingValue=3.0)
        >>> extreme_25_years = lt_sd.rp_to_x(25.0)
        """

        self.sd = sd
        self.nb_hstep = nb_hstep
        ssList = self.sd.to_seastate_list(headingList=nb_hstep , gamma = gamma , spreadingType=spreadingType, spreadingValue = spreadingValue)
        self.ss_df = sp.SeaStatesDF.FromSeaStateList( ssList )

        LongTermRayleighABC.__init__(self, nModes = nModes, ssList = ssList, dss = dss, engine = engine, sht_kwargs = sht_kwargs )




    def contribution_df(self, x, i_rao = None, melt = False):
        """Return contribution as dataframe.

        Parameters
        ----------
        x : float or array
            Extreme value
        i_rao : int or None, optional
            Index of RAO of interest. The default is None.

        Returns
        -------
        pd.DataFrame
            Sea-state dataframe with contribution added as "Contribution_RAO_i" column

        """

        res = self.ss_df.copy()

        if hasattr(x, "__len__") :
            c_name = [ f"Contribution_RAO_{i:}" for i in range(len(x)) ]
            for i, x_ in enumerate(x):
                res.loc[:,c_name[i]] = self.longTerm[i].contribution(x_)

            if melt :
                return pd.melt( res, value_vars = c_name , var_name = "RAO", id_vars = self.ss_df.columns, value_name = "Contribution" )


        else :
            i_rao = self._get_default_i_rao(i_rao)
            res.loc[:,f"Contribution_RAO_{i_rao:}"] = self.longTerm[i_rao].contribution(x)
        return res
    


    def most_contributive_seastate_id(self, x):
        return [ lt.contribution(x[i]).argmax() for i, lt in enumerate(self.longTerm) ]
       
        

    def most_contributive_seastate(self, x):
        """Return most contributive sea-state.

        To be used as design sea-state or to generate Equivalent Design Wave

        Parameters
        ----------
        x : np.ndarray
            Long-term value for each of the RAOs "mode"

        Returns
        -------
        list(SeaState)
            List of design sea-state for each of the RAO "mode"
        """
        return [ self.ssList[ i ] for i in self.most_contributive_seastate_id(x) ]


    def design_seastate(self, x, method = "max"):
        """Return design sea-state. 
        
        Parameters
        ----------
        x : np.ndarray
            Long-term value for each of the RAOs "mode"
        method : str
            "max" return the sea-state with maximum contribution. 
            "int_head" first select most contributive heading (integrated over hs and tp), the select most contributive hs/tp on this direction.
            "int_head_tp" first select most contributive heading (integrated over hs and tp), the select most contributive tp on this direction (integrated over Hs).
            
        Returns
        -------
        list(SeaState)
            List of design sea-state for each of the RAO "mode"
        """
        if method == "max" : 
            return self.most_contributive_seastate(x)
        else :
            contrib = self.contribution_df( x )
            l = []
            for irao in range(self.rao.getNModes()):
                col_name = f"Contribution_RAO_{irao:}"
                head_int = contrib.groupby(["Heading_0"]).sum().loc[ : , col_name  ].idxmax()
                if method == "int_head_tp" :
                    tp_int = contrib.query("Heading_0 == @head_int").groupby(["tp_0"]).sum().loc[ : , col_name ].idxmax()
                    hs_int = contrib.query("Heading_0 == @head_int and tp_0==@tp_int").groupby(["hs_0"]).sum().loc[ : , col_name ].idxmax()
                    l.append( sp.SeaState.Jonswap( hs = hs_int , tp = tp_int, gamma = contrib.loc[:,"gamma_0"].iloc[0] , heading = np.deg2rad(head_int) ) )
                elif method == "int_head" :
                    id_ = contrib.query("Heading_0 == @head_int").loc[: , col_name].idxmax()
                    l.append( sp.SeaState.Jonswap( hs = contrib.loc[id_ , "hs_0"] , tp = contrib.loc[id_ , "tp_0"], gamma = contrib.loc[:,"gamma_0"].iloc[0] , heading = np.deg2rad(head_int) ) )
                else :
                    raise(Exception)
            return l


    def plot_contribution( self, x, how = "heading" , i_rao = None, ax = None, **kwargs):
        from Snoopy import PyplotTools as dplt
        if ax is None :
            fig, ax = plt.subplots()

        i_rao = self._get_default_i_rao(i_rao)

        contrib_df = self.contribution_df( x , i_rao = i_rao )

        if how == "heading" :
            contrib_df.groupby("Heading_0").sum().loc[ : , f"Contribution_RAO_{i_rao:}" ].plot(ax=ax, **kwargs)
        elif how == "hs_tp" :
            df = contrib_df.groupby( ["hs_0", "tp_0"] ).sum().loc[ : , f"Contribution_RAO_{i_rao:}" ].unstack()
            dplt.dfSurface(df, ax=ax, **kwargs)

        else:
            raise(ValueError( f"'how must be within ['heading' , 'hs_tp'']. Got : {how:}" ))



class LongTermRao(LongTermRayleighABC):
    """Calculate long-term response from RAOs.
    """

    def __init__( self, rao, ssList, dss, engine = "python", sht_kwargs = {"num_threads" : 1} ) :
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        rao : sp.Rao
            RAO, ready for spectral calculation (symmetrized). Can contain several 'mode'
        ssList : list
            list of seastate
        dss : float, optional
            Sea-state duration. The default is 10800.
        """
        
        self.rao = rao
        LongTermRayleighABC.__init__(self, dss = dss, ssList = ssList, nModes = self.rao.getNModes(), engine = engine, sht_kwargs = sht_kwargs)


    def _compute_m0s_m2s(self):
        smom = sp.SpectralMoments( self.ssList , self.rao, **self.sht_kwargs )
        m0 = smom.getM0s()
        m2 = smom.getM2s()
        return m0, m2



class LongTermSD( LongTermSDABC ):
    """Calculate long-term response from RAOs on a scatter diagram.
    """
    
    def __init__(self,  rao, *, sht_kwargs = {},  **kwargs ):
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        rao : sp.Rao
            RAO, ready for spectral calculation (symmetrized). Can contain several 'mode'
        sd : DiscreteSD
            The scatter diagram
        nb_hstep : integer
            Number of heading step (36 would lead to a 10 degree step).
        gamma : float
            gamma value for Jonswap spectrum.
        spreadingType : sp.spreadingType
            Spreading type
        spreadingValue : float
            Spreading value
        dss : float, optional
            Sea-state duration. The default is 10800.
            
        sht_kwargs : dict
            Argument passed to SeaStateDf.computeSpectral. For instance sht_kwargs = 

        Example
        -------
        >>> lt_sd = LongTermSD(rao, sd = rec34_SD, nb_hstep = 36 , gamma = 1.5, spreadingType = sp.SpreadingType.Cosn, spreadingValue=3.0,
                               sht_kwargs = { "num_threads" : 5 } )
        >>> extreme_25_years = lt_sd.rp_to_x(25.0)
        """
        self.rao = rao
        
        _sht_kwargs =  {"engine" : "SpectralMoments"}
        _sht_kwargs.update( sht_kwargs )
        LongTermSDABC.__init__(self,  nModes = rao.getNModes(), sht_kwargs = _sht_kwargs , **kwargs )


    def _compute_m0s_m2s(self) :
        return self.ss_df.computeSpectral(self.rao, linear_hs=True, progressBar=True,
                                          **self.sht_kwargs)




# For multiprocessing purpose.
def lt_calc(lt, rp) : 
    return lt.rp_to_x(rp)




class LongTermQuadDamping( LongTermRayleighABC ):

    def __init__( self, ssList, rao_sl, raos, bLin, bQuad, dss ):
        """Compute long-term value, using stochastic damping linearization on all sea-states.

        Parameters
        ----------
        ssList : list
            list of seastate
        rao_sl : rao
            Rao of the quantities with a quadratic damping. 
        rao : list
            List of RAOs. Each RAO is provided with several damping parameter, as rao_sl.
        bLin : float
            Linear damping
        bQuad : float
            Quadratic damping
        dss : float, optional
            Sea-state duration. The default is 10800.
        """

        self.rao_sl = rao_sl
        self.raos = raos
        
        self.bLin = bLin
        self.bQuad = bQuad
        
        self._beq = []

        LongTermRayleighABC.__init__( self, ssList = ssList, dss = dss, nModes = len(raos) )

    def _compute_m0s_m2s(self):
        smom = sp.SpectralMomentsSL( self.ssList , self.rao_sl, self.raos , self.bLin, self.bQuad, **self.sht_kwargs)
        m0 = smom.getM0s()
        m2 = smom.getM2s()
        self._beq = smom._beq 
        return m0, m2



class LongTermQuadDampingSD( LongTermQuadDamping, LongTermSDABC ) :

    def __init__( self, rao_sl, bLin, bQuad, raos, sd, nb_hstep, gamma, spreadingType = sp.SpreadingType.No, 
                  spreadingValue = 3., dss = 10800, sht_engine = "SpectralMoments", num_threads = 1, engine = "python", sht_kwargs = {} ):
        
        """Compute long-term value, using stochastic damping linearization on all sea-states.
        
        Parameters
        ----------
        rao_sl : rao
            Rao of the quantities with a quadratic damping. 
        rao : list
            List of RAOs. Each RAO is provided with several damping parameter, as rao_sl.
        bLin : float
            Linear damping
        bQuad : float
            Quadratic damping
        dss : float, optional
            Sea-state duration. The default is 10800.
        """

        self.rao_sl = rao_sl
        self.raos = raos

        self.bLin = bLin
        self.bQuad = bQuad
        
        LongTermSDABC.__init__(self, sd = sd, nb_hstep = nb_hstep, gamma = gamma, spreadingType = spreadingType, 
                               spreadingValue = spreadingValue, dss = dss, engine = "python", sht_kwargs = { "num_threads" : 1 }, 
                               nModes = len(raos) )
        
        


if __name__ ==  "__main__" :

    from Snoopy.Dataset import rec34_SD

    rao = sp.Rao( f"{sp.TEST_DATA:}/rao/roll_multi.rao").getSymmetrized() * np.pi / 180.
    
    bLin = 2e+08 
    bQuad = 2.0e10
    raos = [ rao ]
        
    lt_sd = LongTermQuadDampingSD( sd = rec34_SD, nb_hstep=36 , gamma = 1.5,  rao_sl = rao , raos = raos,  bLin = bLin , bQuad = bQuad )
    roll_ext = lt_sd.rp_to_x( 25. )[0]
    
    beq_dss = lt_sd._beq[lt_sd.most_contributive_seastate_id( [roll_ext] )[0]]
    print( roll_ext )
    
    rao_beq_dss = rao.getRaoAtModeCoefficients( [ beq_dss ] )
    lt_sd_eq = LongTermSD( sd = rec34_SD, nb_hstep=36 , gamma = 1.5,  rao = rao_beq_dss )
    roll_ext_bis = lt_sd_eq.rp_to_x( 25. )[0]
    print( roll_ext_bis )
    
    

