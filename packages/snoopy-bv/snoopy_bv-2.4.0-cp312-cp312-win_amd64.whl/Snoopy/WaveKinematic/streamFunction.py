import numpy as np
from matplotlib import pyplot as plt
from Snoopy import WaveKinematic as wk
import _WaveKinematic
from scipy.interpolate import InterpolatedUnivariateSpline
from Snoopy import logger



class StreamFunction(_WaveKinematic.StreamFunction):

    @staticmethod
    def plot_steepness_limit(ax = None, variant = "miche", label = "Steepness limit", **kwargs):
        if ax is None : 
            fig, ax = plt.subplots()
        kd = np.linspace(0.1 , 15.0,200)
        ax.plot(kd , steepness_limit(kd, variant = variant) , label = label, **kwargs)
        ax.set_xscale('log')
        ax.set(xlabel = "kd" , ylabel = r"$H/\lambda$")
        return ax

    def get_crest(self):
        return self.getElevation( t = 0.0 , x = 0.0 )
    
    def get_trough(self):
        return self.getElevation( t = self.getPeriod() / 2. , x = 0. )

    def __init__(self, H , T = None, wavelength=None, depth = -1, **kwargs):
        """Stream Function implementation. Based on the implementation of the Stream Function in FoamStar 2

        Parameters
        ----------
        depth : double
            depth of the fluid. Negative or zero values correspond to the infinite depth case.

        H : double
            wave height.

        T : double, optional
            wave period.
            Either T or wavelength must be provided depending on useLength. See useLength

        wavelength : double, optional
            wave length.
            Either T or wavelength must be provided depending on useLength. See useLength

        cEcS : double
            depending on useEulerCurrent value it is the mean value of Euler or Stokes currents

        useEulerCurrent : bool, True
            if useEulerCurrent is True, then cEcS corresponds to the mean value of Euler current. If it is False, then cEcS is that for Stokes.

        N : int, 30
            order of the wave

        maxIter : int, 1000
            number of maximum iteration to be used to resolve the problem. Note, that this value cannot be less than 10.

        tol : double
            tolerance value.

        damp : double, 0.3
            Relaxation  for numerical solver.
        """
        
        if wavelength is not None : 
            kwargs["useLength"] = True
            if T is not None:
                raise(Exception( "Period and length argument are mutually exclusive." ))
            T = 0.0
            if H/wavelength > steepness_limit( kd := 2*np.pi * depth / wavelength):
                # ax = self.plot_steepness_limit()
                # ax.plot( kd , H/wavelength , "o", label ="Current point")
                # ax.legend()
                raise(Exception("Above steepnesss limit" ))
        else : 
            wavelength = 0.0
            kwargs["useLength"] = False

        _WaveKinematic.StreamFunction.__init__(self , H = H , T = T , wavelength = wavelength , depth = depth, **kwargs)
        
        if not self.check():
            logger.warning("Warning, steepness seems to be above what Snoopy can handle.")


    def check(self, tol = 0.001):
        """Basic checks
        """
        T = self.getPeriod()
        L = self.getWaveLength()
        H = self.getWaveHeight()
        
        h_t = self.getElevation( t = 0. , x = 0. ) - self.getElevation( t = T/2. , x = 0. )
        h_l = self.getElevation( t = 0. , x = 0. ) - self.getElevation( t = 0.0 , x = L/2 )
        
        if not np.isclose(H , h_t) :
            return False

        if not np.isclose(H , h_l) :
            return False
        
        x = np.linspace( -0.5, 0.0, 200 )
        dx = (x[1]-x[0])*L
        eta = self.getElevation( x = x*L , t = 0)
        #Check negative steepness (0.001% as criteria)
        np.min( (np.diff(eta) / dx) )
        
        if ( (np.diff(eta) / dx) < -tol ).any(): 
            print ("Wiggles")
            return False
        
        return True

        
    def __str__(self):
        return f"H = {self.getWaveHeight():.2f}m T = {self.getPeriod():.2f}s L = {self.getWaveLength():.1f}m D = {self.getDepth():.1f}"

    def plot_x( self, ax=None , t = 0.0, **kwargs ):
        """Plot the wave        

        Parameters
        ----------
        ax : plt.Axis, optional
            Where to plot. The default is None.
        t : float, optional
            Time. The default is 0.0.
        **kwargs : any 
            Arguments passed to ax.plot()

        Returns
        -------
        ax : plt.Axis
            The plot
        """
        if ax is None :
            fig, ax = plt.subplots()
            
        length = self.getWaveLength()
        x = np.linspace( -0.5, +0.5, 200 )
        eta = self.getElevation( x = x*length , t = t)
        ax.plot( x,  eta  / self.getWaveHeight() , **kwargs)
        ax.set(title = self.__str__() , xlabel = r"$x / \lambda$", ylabel = r"$\eta / H$")
        return ax


    def getSteepness(self):
        return self.getWaveHeight() / self.getWaveLength()



def steepness_limit( kd, variant="Miche" ):
    """Steepness limit.

    If variant is "numerical", the limits of current numerical implementation is given.
    """
    
    if kd < 0. :
        kd = 6.
    if variant.lower() == "miche":
        return 0.88 * np.tanh( 0.89 * kd) / (2*np.pi)
    elif variant.lower() == "fenton" : 
        return 0.142 * np.tanh( kd )
    elif variant.lower() == "williams" : 
        loh = 2*np.pi / kd
        return (0.141063 * loh + 0.009572 * loh**2 + 0.00778 * loh**3) / ( 1 + 0.0788340 * loh + 0.0317567 * loh**2 + 0.0093407 * loh**3 ) / loh
    
    elif variant.lower() == "numerical" :
        # Numerically found
        kd_tested = np.arange(0.1, 2.0 , 0.05)
        st_tested = [0.004128107909593858, 0.010040370756606845, 0.019113993500315975, 0.025744381020102545, 0.03250350190093363, 0.03887867362795275, 0.045215537172688024, 0.051403723976451744, 0.05704513216247728, 0.06228471856166955, 0.06737834045969064, 0.07195005309739623, 0.07670334335023006, 0.08087939281319456, 0.08484425722886338, 0.08859904745425698, 0.08747393027201454, 0.08919518889281401, 0.09213255545762493, 0.09437460574786326, 0.09588537006403437, 0.09771953533822766, 0.1004807422726869, 0.10311525970015925, 0.10447476952164983, 0.10685134205240356, 0.10911823205749616, 0.11067656342098378, 0.11028378847785994, 0.11221734034947314, 0.11093440608209625, 0.11520027967184851, 0.11497159894314642, 0.11592737059773683, 0.11810516043546725, 0.117620030264821, 0.11836730018416414, 0.11773323057084556]
        return InterpolatedUnivariateSpline(kd_tested, st_tested, ext = "const")(kd)
    
    else : 
        raise(Exception())
        

"""Routines for period to wave length conversion (without actually solving the streamfunction)

Can go further in steepness than what can be numerically handed by the StreamFunction class
"""
def C0(kd) :
    return np.tanh(kd)**0.5

def C2(kd) : 
    s = 1/np.cosh(2*kd)
    return np.tanh(kd)**0.5 * (2+7*s**2)/(4*(1-s)**2)

def C4(kd) : 
    s = 1/np.cosh(2*kd)
    return np.tanh(kd)**0.5 * ( 4+32*s-113*s**2-400*s**3 -71*s**4 + 146 * s**2) / (32*(1-s)**2)

def fun(k,d,H,T) : 
    kd = k*d
    return (-2*np.pi / (T*(9.81*k)**0.5)) + C0(kd) + (0.5*k*H)**2 * C2(kd) + (0.5*k*H)**4 * C4(kd)

def t_to_l( t , h, d ):
    from scipy.optimize import root_scalar
    from Snoopy import Spectral as sp
    # Linear value
    l0 = sp.t2l(t, d)
    k0 = 2 * np.pi / l0 
    res = root_scalar(lambda k : fun(k,d,h,t)  , x0 = k0 )
    k = res.root
    return 2*np.pi / k

def l_to_t( l , h, d ):
    from scipy.optimize import root_scalar
    from Snoopy import Spectral as sp
    # Linear value
    t0 = sp.l2t(l, d)
    k = 2*np.pi / l
    res = root_scalar(lambda t : fun(k,d,h,t)  , x0 = t0 )
    return res.root


    