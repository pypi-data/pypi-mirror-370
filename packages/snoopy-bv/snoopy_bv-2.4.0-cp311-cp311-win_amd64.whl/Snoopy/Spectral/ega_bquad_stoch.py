import numpy as np
from scipy.optimize import root
from scipy.interpolate import LinearNDInterpolator
from Snoopy import logger

def ega_lin( blin, bquad, m2_roll, m0_ega ):
    """
    
    Parameters
    ----------
    blin : float
        Linear damping coefficient
    bquad : TYPE
        Quadratic damping coefficient
    m2_roll : fun
        roll m2, function of Beq and Ega_eq
    m0_ega : fun
        EGA m0, function of Beq and Ega_eq
    """
    def linearisation_equation( beq, ega_eq ) :
        eval_ = np.array( [ blin + bquad * (8/np.pi)**0.5 * m2_roll(beq,ega_eq)**0.5 - beq,
                           2 * m0_ega( beq, ega_eq )**0.5 - ega_eq
                         ])
        
        logger.debug ( eval_ )

        return eval_

    res = root( lambda x :  linearisation_equation(x[0] , x[1]) , x0 = [blin, 10.] )
    return res.x


class EgaLinearisation:
    
    def __init__(self, blin, bquad, roll_raos, ega_raos , ega_list):
        """Handle EGA + damping linearization.
        
        Parameters
        ----------
        blin : float
            Linear damping coefficient
        bquad : float
            Quadratic damping coefficient
        roll_raos : list
            List of roll RAO. Each element of the list contains roll rao for several linear damping. In RADIANS!
        ega_raos : TYPE
            List of EGA RAO. Each element of the list contains ega rao for several linear damping.
        ega_list : np.ndarray
            Ega value for each rao in the lists
        """
        self.blin = blin
        self.bquad = bquad
        
        self.roll_raos = roll_raos
        self.ega_raos = ega_raos
        self.ega_list = ega_list
        
        self.blin_list = roll_raos[0].getModeCoefficients()


    def linearize(self, ss):
        """Perform EGA + damping linearization on a given sea-state.
        
        Parameters
        ----------
        ss : SeaState
            Seastate on which to linearize

        Returns
        -------
        tuple
            b_eq, ega_eq, roll_m0 , roll_m2
        """
        ega_m0 = []
        roll_m2 = []
        roll_m0 = []
        for i, ega in enumerate(ega_list) :
            ega_m0.append(  sp.SpectralMoments( [ss] , rao_egas[i], num_threads = 6 ).getM0s()[0] )
            roll_mom = sp.SpectralMoments( [ss] , rao_rolls[i], num_threads = 6 )
            roll_m2.append(  roll_mom.getM2s()[0] )
            roll_m0.append(  roll_mom.getM0s()[0] )
            
        # ega_m0_df = pd.DataFrame(  data = np.array( ega_m0 ) , index = ega_list , columns = blin_list )
        # roll_m2_df = pd.DataFrame(  data = np.array( roll_m2 ) , index = ega_list , columns = blin_list )
        # points = roll_m2_df.stack().reset_index().values[:,:2]
        # values_r = roll_m2_df.stack().values[:]
        # values_e = ega_m0_df.stack().values[:] 
        # dplt.dfSurface( 2*ega_m0_df**0.5 , colorbar=True  ).set(title = "m0 EGA")
        # dplt.dfSurface( roll_m2_df, colorbar=True  ).set(title = "m2 roll")
        
        ega_m0 = np.array( ega_m0 ).flatten()
        roll_m2 = np.array( roll_m2 ).flatten()
        roll_m0 = np.array( roll_m0 ).flatten()
        points = np.array( np.meshgrid(  ega_list,  blin_list)).T.reshape(-1,2)
        
        m2_roll_i = LinearNDInterpolator( points, roll_m2 )
        m0_roll_i = LinearNDInterpolator( points, roll_m0 )
        m0_ega_i = LinearNDInterpolator( points,  ega_m0 )
            
        b_min = np.min(blin_list)
        b_max = np.max(blin_list)
        
        def m2_roll_fun( beq, ega ):
            return m2_roll_i( np.clip( ega, 2.0 , 22.5 ), np.clip( beq, b_min, b_max) )
        
        def m0_roll_fun( beq, ega ):
            return m0_roll_i( np.clip( ega, 2.0 , 22.5 ), np.clip( beq, b_min, b_max) )
        
        def m0_ega_fun( beq, ega ):
            return m0_ega_i(  np.clip( ega, 2.0 , 22.5 ), np.clip( beq, b_min, b_max) )
        
        beq, ega_eq = ega_lin( blin = self.blin, bquad = self.bquad , m2_roll = m2_roll_fun, m0_ega = m0_ega_fun )
        
        roll_m0, roll_m2 = m0_roll_fun(beq, ega_eq), m2_roll_fun(beq, ega_eq)
        
        logger.debug( f"Significant roll ampitude {np.rad2deg( 2*roll_m0**0.5 ):} degree" )
        
        return beq, ega_eq, roll_m0, roll_m2
                
        
if __name__ == "__main__" :
    from Snoopy import Spectral as sp

    logger.setLevel(10)

    ss = sp.SeaState.Jonswap( 10.0 , 12.0 , 1.5 , np.pi / 4 )

    ega_list = np.array( [ 2.,5.,10.,15.,22.5] )

    rao_egas = []
    rao_rolls = []
    for ega in ega_list :
        rao_egas.append(sp.Rao( f"test_tmp/data/EGA_{ega:.2f}/rao/EGA.rao" ))
        rao_rolls.append( sp.Rao( f"test_tmp/data/EGA_{ega:.2f}/rao/roll.rao" ).getSymmetrized()  * np.pi / 180. )

    blin_list = rao_rolls[0].getModeCoefficients()

    e = EgaLinearisation( blin = 2.0e7 , bquad = 2e8 , roll_raos = rao_rolls, ega_raos = rao_egas, ega_list = ega_list )

    logger.info("START")

    res = e.linearize( ss )
    print(res)   
    logger.info("STOP")
    
