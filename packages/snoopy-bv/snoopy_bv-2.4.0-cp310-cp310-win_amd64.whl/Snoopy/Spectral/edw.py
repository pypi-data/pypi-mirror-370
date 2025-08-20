from copy import deepcopy
import numpy as np

from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
from Snoopy import TimeDomain as td
from Snoopy import Math as smt
from Snoopy import logger


class EdwABC(object):

    def __init__(self, target , ss, *, method = "MHLGA", wmin = None, wmax = None, dw = None, depth = -1, speed = 0.0):
        self.target = target
        self.ss = ss

        #--------For FORM calculation
        self._wib = None
        self._wmin = wmin
        self._wmax = wmax
        self._dw = dw
        self._depth = depth
        self._method = method
        self.speed = speed

        self.x0 = None


    def plot_eta1(self, ax = None, tmin=-100, tmax = +100, dt = 0.2, **kwargs):
        """Plot the wave elevation.
        """
        if ax is None :
            fig, ax = plt.subplots()
        time = np.arange(tmin, tmax , dt)
        td.ReconstructionWifLocal( self.wif, speed = self.speed ).evalSe(time).plot( ax=ax, **kwargs )
        ax.set(xlabel = "time (s)", ylabel = r"$\eta$ (m)")
        return ax

    def get_eta1_space_time(self, tmin=-100, tmax=100, dt=0.2, xmin=-500, xmax=+500, dx =10) :
        time = np.arange(tmin, tmax , dt)
        space = np.arange(xmin, xmax , dx)
        rec = td.ReconstructionWifLocal( self.wif, speed = self.speed )
        return rec.getElevation_DF(time,space)

    def _form(self):
        """ Use form approach to calculate the design waves
        """
        from scipy import optimize

        logger.debug("Computing EDW with FORM")

        #Fill wif with wave spectrum
        wib = sp.Wib.SetSeaState(self.ss, wmin = self._wmin, wmax = self._wmax , nbSeed = self._nbSeed, depth = self._depth)

        # ------- Function to minimize
        def betaToMin(x, grad=None) :
            x = np.array(x)
            return np.sum( x[:wib.nbwave]**2 + x[wib.nbwave:]**2 )

        def betaToMinJac(x) :
            return 2*np.array(x)

        def resp(x) :
            wib.ab = x
            resp = self._getResponseAt0( wib.getWif() ) - self.target
            logger.debug(f"target diff {resp:}")
            return resp

        # Do not start from 0.0
        x0 = np.zeros( (2*wib.nbwave) )
        if self.x0 is None :
            x0[:] = 0.01
        else :
            x0[:] = self.x0[:]

        #------- Run minimization
        if self._method == "MHLGA" :
            from Snoopy.Math import MHLGA
            self._opt = MHLGA( x0, resp, beta_tol = 1e-4, func_tol=1e-4, itmax=100 , dx = 0.01)
        else :
            constraintsList =  { "type" : "eq" , "fun" : resp  }
            self._opt = optimize.minimize(betaToMin, x0 = x0 , args=(), jac = betaToMinJac, constraints = constraintsList,
                                  method="SLSQP" , options={"maxiter" : 1000 , "ftol" : 1e-4 , "disp":True} )   # Powell  COBYLA
        #Store results in wib
        wib.ab = np.array(self._opt.x)

        self._wib = wib
        self.wif = wib.getWif()


    def plotResponse(self , ax = None, tmin=-100, tmax = +100, dt = 0.2, **kwargs):
        """Plot the response on which the design wave is conditioned.
        """
        if ax is None :
            fig, ax = plt.subplots()
        time = np.arange(tmin, tmax , dt)
        ax.plot( time , self._getReconstructor(self.wif) (time), **kwargs)
        ax.set(xlabel = "Time (s)")
        return ax

    #To implement in subclass
    def _getReconstructor(self , wif):
        raise(NotImplementedError)

    def _getResponseAt0(self, wif ) :
        return self._getReconstructor(wif)( 0.0 )

    def _analytical_calculation(self ):
        raise(NotImplementedError)



class Edw_Rao(EdwABC):

    def __init__(self , target, ss, rao,  method = "analytical") :
        """Compute RCW based on linear RAO.

        Parameters
        ----------
        target : float
            Target to achieve at t=0.0
        ss : SeaState
            The sea-state
        rao : Rao
            The transfer function
        method : str, optional
            "analytical" or "numerical". The default is "analytical".
        """
        self.rao = rao
        EdwABC.__init__(self, target, ss, method = method)
        self._wmin = np.min( self.rao.freq )
        self._wmax = np.max( self.rao.freq )
        self._dw = self.rao.freq[1] - self.rao.freq[0]
        self._nbSeed = len(self.rao.freq)

        self.speed = self.rao.getForwardSpeed()

        if method == "analytical":
            self._analytical_calculation()
        else :
            self._form()

    def _analytical_calculation(self):
        self.wif = rcwCalc(  self.target , self.rao , self.ss )

    def _getReconstructor(self, wif ) :
        return lambda x : td.ReconstructionRaoLocal( wif , self.rao )(x)[:, 0]

    def _getResponseAt0(self, wif ) :
        return td.ReconstructionRaoLocal( wif , self.rao )(0)[0]


class Drcw_Rao(Edw_Rao):

    def _analytical_calculation(self):
        self.wif = drcwCalc(  self.target , self.rao , self.ss )
    
    



class Edw_Qtf(EdwABC):

    def __init__(self, target, ss , qtf):
        self.qtf = qtf
        EdwABC.__init__(self , target, ss)
        self._wmin = np.min( self.qtf.freq )
        self._wmax = np.max( self.qtf.freq )
        self._dw = self.qtf.freq[1] - self.qtf.freq[0]
        self._nbSeed = len(self.qtf.freq)
        self._form()

    def _getReconstructor(self, wif) :
        return td.ReconstructionQtfLocal( wif , self.qtf )

    def _getResponseAt0(self, wif ) :
        return td.ReconstructionQtfLocal( wif , self.qtf )(0)[0]


class Edw_Rao_qtf(EdwABC):
    def __init__(self, target, ss , rao , qtf, method = "MHLGA"):
        self.rao = rao
        self.qtf = qtf
        EdwABC.__init__(self , target, ss)
        self._wmin = np.min( self.rao.freq )
        self._wmax = np.max( self.rao.freq )
        self._dw = self.rao.freq[1] - self.rao.freq[0]
        self._nbSeed = len(self.rao.freq)
        self._form()

    def _getReconstructor(self, wif ) :
        return lambda x : td.ReconstructionRaoLocal( wif , self.rao )(x)[:, 0] + td.ReconstructionQtfLocal( wif , self.qtf )(x)[:, 0]

    def _getResponseAt0(self, wif ) :
        return td.ReconstructionRaoLocal( wif , self.rao )(0)[0] + td.ReconstructionQtfLocal( wif , self.qtf )(0)[0]


class NewWave( EdwABC ):
    def __init__(self , target , ss , *,  waveModel, speed = 0.0, method = "MHLGA", wmin=0.2, wmax = 1.8, dw = 0.05):
        EdwABC.__init__(self , target, ss , method = method, wmin = wmin, wmax = wmax, speed = speed)
        self.waveModel = waveModel
        self._nbSeed = 1 + int( (wmax - wmin) / dw )
        self._form()

    def _getReconstructor(self, wif ) :
        kin = self.waveModel( wif )
        return lambda time : kin.getElevation(  time , 0. , 0.  )




class SlammingWave( EdwABC ):
    def __init__(self , target , ss , rao, height, *, method = "MHLGA"):
        EdwABC.__init__(self , target, ss, method = method)
        self.rao = rao
        self.rao_v = self.rao.getDerivate(n = 1)
        self.height = height
        self._wmin = np.min( self.rao.freq )
        self._wmax = np.max( self.rao.freq )
        self._dw = self.rao.freq[1] - self.rao.freq[0]
        self._nbSeed = len(self.rao.freq)

        start_ = Edw_Rao( target, ss , self.rao_v , method = method )
        self.x0 = start_._wib.ab

        self._form()


    def _getResponseAt0(self, wif) :
        time = np.arange( -10. , 10., 0.05 )
        recMvt = td.ReconstructionRaoLocal( wif , self.rao ).evalSe( time )
        impact = td.getSlammingVelocity( recMvt, pos_z = self.height)

        if len(impact) == 0 :
            logger.debug("no impact")
            # return self.target + 100 * abs(self.height-recVz.iloc[i0])
        else:
            #penalty = recVz.iloc[i_impact].idxmax()
            logger.debug(f"imp = {impact.max():}")
            # print (tmp)
            return impact.max() # + 100*np.abs(penalty)
        return td.ReconstructionRaoLocal( wif , self.rao )(0)[0]

    def _getReconstructor(self, wif ) :
        return lambda x : td.ReconstructionRaoLocal( wif , self.rao_v )(x)[:, 0]


class Reg_EDW_Rao( EdwABC ):


    def __init__( self , target , rao , freq = None, head = None, freq_range = [0.2, 1.2] ) :

        self.target = target
        self.speed = rao.getForwardSpeed()

        self.rao = rao
        df = self.rao.toDataFrame(  )
        df_mod = np.abs(df)

        if head is None :
            self.head = df_mod.loc[freq_range[0]:freq_range[1], :].max(axis = 0).idxmax()
        else :
            self.head = head

        if freq is None :
            self.freq = df_mod.loc[ freq_range[0]:freq_range[1], self.head].idxmax()
        else :
            self.freq = freq

        v_ = df_mod.loc[self.freq , self.head ]
        p_ = np.angle( df.loc[self.freq , self.head ] )

        self.wif = sp.Wif( a = [ target / np.abs(v_)], w = [self.freq] , b = [self.head]  , phi = [-p_] )

    def _getReconstructor(self, wif ) :
        return lambda x : td.ReconstructionRaoLocal( wif , self.rao )(x)[:, 0]



def rcwCalc(  targetVal , rao , seaState, dw = None ) :
    """Compute RCW and return wif. Only 1 mode, without spreading for now.
    """

    if seaState.getSpectrumCount() > 1 :
        print ("Design waves not implemented for multi-modal sea-state")
        raise(NotImplementedError)
        
    if not seaState.isUnidirectional() :
        raise(Exception("For unidirectional RCW, the input seastate should be unidirectional"))
        
    heading = seaState.getSpectrum(0).heading

    if dw is not None :
        rao_ = rao.getRaoAtFrequencies( np.arange( smt.round_nearest( np.min(rao.freq), dw) ,
                                         smt.round_nearest( np.max(rao.freq), dw) + dw ,
                                         dw ))
    else :
        dw = smt.get_dx(rao.freq)
        rao_ = rao
        if dw is None :
            raise(Exception("EDW calculation requires a constant dw step, please provide dw"))

    rSpec = sp.ResponseSpectrum( seaState , rao_.getSorted(duplicatesBounds = False)  )
    m0  = rSpec.getM0()  # TODO remove spreading if any
    sw = seaState.compute(rao_.freq)

    ihead = np.argmin( abs(rao.head[:] - heading ) )
    
    if np.rad2deg(abs(rao.head[ihead] - heading )) > 5.0 : 
        logger.warning("Warning EDW is calculated using a heading far from what is available in the RAO. (> 5 degrees)")

    amp = rao_.module[ihead, :,0] * sw[:] * dw * targetVal
    phi = -rao_.phasis[ihead, :, 0]
    amp /= m0

    return sp.Wif( w = rao_.freq , a = amp , phi = phi , b = np.full( (len(rao_.freq)), heading )  )



def drcwCalc(  targetVal , rao , seaState, dw = None ):
    """Compute DRCW and return wif. Only 1 mode, without spreading for now.
    """
    if dw is not None :
        rao_ = rao.getRaoAtFrequencies( np.arange( smt.round_nearest( np.min(rao.freq), dw) ,
                                         smt.round_nearest( np.max(rao.freq), dw) + dw ,
                                         dw ))
    else :
        dw = smt.get_dx(rao.freq)
        rao_ = rao
        if dw is None :
            raise(Exception("EDW calculation requires a constant dw step, please provide dw"))

    rao_ = rao_.getSorted(duplicatesBounds = False) 
    
    db = smt.get_dx(rao_.head)
    if db is None:
        raise(Exception("EDW calculation requires a constant db step"))

    rSpec = sp.ResponseSpectrum( seaState , rao_ )
    m0  = rSpec.getM0()

    amp, phi, head, freq = np.empty( (0), dtype = float ), np.empty( (0), dtype = float ) , np.empty( (0), dtype = float ), np.empty( (0), dtype = float )
    for ihead in range(rao_.getNHeadings()) :
        sw = seaState.compute(rao_.freq, rao_.head[ihead])
        amp = np.concatenate( [ amp,  rao_.module[ihead, :,0] * sw ] )
        phi = np.concatenate( [ phi, -rao_.phasis[ihead, :, 0] ] )
        head = np.concatenate( [ head, np.full( (rao_.getNFrequencies()), rao_.head[ihead] ) ]  )
        freq = np.concatenate( [ freq, rao_.freq  ] )
    amp *= dw * db * targetVal / m0
    wif = sp.Wif( w = freq, a = amp , phi = phi , b = head  )
    wif = wif.optimize(1.0)
    return wif



def newWave( targetVal, seaState , wmin=0.2, wmax=1.8, dw=0.05 ):
    """Return wif corresponding to the new wave
    """

    if seaState.getSpectrumCount() > 1 :
        print ("Design waves not implemented for multi-modal sea-state")
        raise(NotImplementedError)

    spec = seaState.getSpectrum(0)

    freq = np.arange( wmin, wmax, dw )
    sw = seaState.compute( freq )

    n = len(freq)
    heading = np.full( (n), spec.heading )
    phi = np.zeros( (n) )

    amp = sw[:] * dw
    amp *= targetVal / np.sum(amp)

    return sp.Wif( w = freq , a = amp , phi = phi , b = heading  )



"""
Kept for compatibility purpose, replaced by NewWave
"""


def constrainedWave( constraints , seaState , waveModel, depth = 0.0,  **kwargs ) :
    """return wif of the most probable (miminmize beta) wave that sastisfies some constraints eta(t_i) = v_i
    **kwargs contains arguments passed to SetSeaState (wmin , wmax, nbSeed)
    """

    from scipy import optimize

    #Fill wif with wave spectrum
    wib = sp.Wib.SetSeaState(seaState, depth = depth , **kwargs)

    # ------- Function to minimize
    def betaToMin(x, grad=None) :
        x = np.array(x)
        a = np.sum( x[:wib.nbwave]**2 + x[wib.nbwave:]**2 )
        return a

    def betaToMinJac(x) :
        return 2*np.array(x)

    # ------- Constraints
    if not hasattr( constraints , "__len__")  :
        constraints = [ (0.0 , constraints) ]

    def resp(x, target , time) :
        wib.ab = x
        kin = waveModel( wib.getWif() )
        a = kin.getElevation(  time , 0. , 0.  ) - target  # Much slower.
        return a

    # constraintsList =  [   { "type" : "eq" , "fun" : lambda x : resp(x , v , t) }   for  t, v in constraints ]  # Does not work

    diff = np.empty((len(constraints)))

    def multiConstraint( x ) :
        #return resp(x, 0 , constraints[0][0]) - constraints[0][1]
        for i, (t,v) in enumerate(constraints) :
            diff[i] = resp( x, 0 , t ) - v
        return np.linalg.norm( diff )

    constraintsList =  { "type" : "eq" , "fun" : multiConstraint  }

    # ------- Run minimization
    # Do not start from 0.0
    x0 = np.zeros( (2*wib.nbwave) )
    x0[:] = 0.01

    a = optimize.minimize(betaToMin, x0 = x0 , args=(), jac = betaToMinJac, constraints = constraintsList,
                          method="SLSQP" , options={"maxiter" : 1000 , "ftol" : 1e-4 , "disp":True} )   # Powell  COBYLA

    #Store results in wib
    wib.ab = np.array(a.x)

    return wib
