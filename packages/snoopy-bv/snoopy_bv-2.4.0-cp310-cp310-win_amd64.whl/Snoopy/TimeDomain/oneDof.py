import numpy as np
from scipy.integrate import odeint, solve_ivp
from scipy.interpolate import InterpolatedUnivariateSpline
from math import pi
import pandas as pd

class OneDof(object):
    """Class to solve simple 1 DOF mechanical equation

    M d2x/dt2 + Bl dx/dt + Bq (dx/dt)*|(dx/dt)| + K x = F

    """

    def __init__(self , m,  k , bl , bq, solver = "RK45" ):
        self.m = m
        self.bl = bl
        self.bq = bq
        self.k = k

        self.T0 = 2 * pi * ( self.m / self.k )**0.5
        self.solver = solver

    def __str__(self):
        """
           Print the system parameters
        """

        Bcr = 2*(self.m * self.k)**0.5

        str_ = """!--- Mechanical system parameter ---
Mass : {:.2f}
Stiffness : {:.2f}
Natural period : {:.2f}
Critical damping : {:.2f}
Linear damping : {:.2f} ( = {:.2f} Bcr)
!-----------------------------------!""".format(self.m , self.k, self.T0 , Bcr, self.bl, self.bl/Bcr )

        return str_

    def deriv(self, t , y, f_ex = lambda x, y: 0):
        return np.array( [ y[1] , (-self.bl*y[1] - self.bq * y[1] * abs(y[1])  - self.k*y[0] + f_ex(t,y) ) / self.m ]  )


    def decay(self , tMin , tMax , X0 , t_eval = None ):
        """Simulate a decay test (no excitation)


        Parameters
        ----------
        tMin : float
            Start time
        tMax : float
            End time
        X0 : (float, float)
            Initial position ( x, dx/dt )
        t_eval : np.ndarray, optional
            Fixed evaluation time, for ODE integration. The default is None.

        Returns
        -------
        pd.Series
            Motion as pandas Series
        """

        if type(t_eval) == int :
            t_eval = np.arange(tMin, tMax, self.T0 / t_eval  )

        out = solve_ivp( fun = self.deriv, t_span = [tMin, tMax], y0 = X0, t_eval = t_eval, method = self.solver)
        return pd.Series(  index = out.t , data = out.y[0,:]  )

    def forcedMotion(self , tMin, tMax, X0 , f_ex , t_eval) :
        """Simulate forced motion

        Parameters
        ----------
        tMin : float
            Start time
        tMax : float
            End time
        X0 : (float, float)
            Initial position ( x, dx/dt )
        f_ex : function
            Force function, takes position and velocity as input.
        t_eval : np.ndarray, optional
            Fixed evaluation time, for ODE integration. The default is None.

        Returns
        -------
        pd.Series
            Motion as pandas Series
        """
        if type(t_eval) == int :
            t_eval = np.arange(tMin, tMax, self.T0 / t_eval  )

        out = solve_ivp( fun = lambda t,y : self.deriv(t,y,f_ex), t_span = [tMin, tMax], y0 = X0, t_eval = t_eval, method = self.solver)
        return pd.Series(  index = out.t , data = out.y[0,:]  )


    def forcedMotion_se(self, se, X0, dt = None):
        """Simulate forced motion, with forces given as discrete time serie.

        X0 : (float, float)
            Initial position ( x, dx/dt )
        se : pd.Series
            Forces as pd.Series. Forces are interpolated to solve the ODE
        dt : float, optional
            Time step for ODE resolution. The default is None.

        Returns
        -------
        pd.Series
            Motion as pandas Series
        """
        interp = InterpolatedUnivariateSpline(se.index.values, se.values, ext = 1)
        tMin, tMax = se.index.min(), se.index.max()

        if dt is not None :
            t_eval = np.arange( tMin , tMax, dt)
        else :
            t_eval = None

        return self.forcedMotion( tMin = tMin, tMax = tMax , X0 = X0, f_ex= lambda t ,p : float(interp(t)), t_eval = t_eval )




if __name__ == "__main__" :

    m = 15
    bl = 1.5
    bq = 2.0
    k = 10

    # Generate a mcnSolve test
    oneDof = OneDof(m=m, bl=bl, bq=bq, k=k)
    print (oneDof)
    res = oneDof.decay(tMin=0.0, tMax=100.0, X0=np.array([10.0, 0.]) , t_eval = np.arange(0,100,0.1))
    res.plot()

    res2 = oneDof.forcedMotion(tMin=0.0, tMax=100.0, X0=np.array([10.0, 0.]) , t_eval = np.arange(0,100,0.1), f_ex = lambda x,y : x)
    res2.plot()


    se = pd.Series( index = np.linspace(0,100,20) , data = np.linspace(0,100,20)  )
    res3 = oneDof.forcedMotion_se( se, X0=np.array([10.0, 0.])  )
    res3.plot(marker = "+")
