import numpy as np
import pandas as pd
from Snoopy.Math import df_interpolate, get_dx



def slidingDamping( df , T ,  a, n = None ):
    """Compute equivalent damping from forced motion.

    Parameters
    ----------
    df : pd.Dataframe
        Forced motion results. 
        should have "load" and "motion", with potentially a "velocity" columns, time is index.
        If "velocity" is not provided, the velocity is calculated by finite difference at intermediate times. 
    T : float
        Period
    a : float
        Forced oscillation amplitude, if None, taken as max on each cycle.
    n : int
        Number of interpolation point per period. If None, closest to data, over 60 is used. Default is None

    Returns
    -------
    beq : pd.Series
        Equivalent damping function of time (sliding)
    """

    time = df.index
    w = 2 * np.pi / T

    if n is None :
        dt = get_dx(df.index.values)
        n = int(T/dt)
        n = max(n , 60)

    newTime = np.arange(min(time) , max(time) , T/(n))
    df_new = df_interpolate(df, newIndex = newTime)

    if "velocity" in df.columns:
        dt = (newTime[1] - newTime[0])
        beq = pd.Series(index = newTime[:-n] , dtype = float)
        for i in range(len(newTime) - n):
            mt = df_new.load.values[i:i+n] * df_new.velocity.iloc[i:i+n] *dt
            if a is None :
                a_ = df_new.motion.iloc[i:i+n+1].abs().max()
            else :
                a_ = a
            beq.iloc[i] = -np.sum(mt) / (np.pi * a_**2 * w)
    else:
        dt2 = (newTime[1] - newTime[0])/2
        beq = pd.Series(index = newTime[:-n-1] + dt2, dtype = float)
        for i in range(len(newTime) - n - 1):
            mt = 0.5 * (df_new.load.values[i:i+n] + df_new.load.values[i+1:i+n+1]) * np.diff(df_new.motion.iloc[i:i+n+1])
            if a is None :
                a_ = df_new.motion.iloc[i:i+n+1].abs().max()
            else :
                a_ = a
            beq.iloc[i] = -np.sum(mt) / (np.pi * a_**2 * w)

    return beq



