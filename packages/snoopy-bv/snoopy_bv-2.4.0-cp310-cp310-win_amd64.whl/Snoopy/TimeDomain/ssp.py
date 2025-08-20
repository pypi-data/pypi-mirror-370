import numpy as np

from Snoopy.Math import df_interpolate
from Snoopy.TimeDomain.TimeSignals import fftDf
from scipy.integrate import trapezoid

def SSP(df, df_ref, dt=None, t_start=None, t_stop=None, removeAverage=False):
    r"""Estimate the Surface Similarity Parameter, to estimate the error between two time signals.
    
    SSP ranges from 0.0 (identical signal) to 1.0 (out of phase, or very different).
    
    .. math::
            SSP = \frac{ (\int | F_{\eta, pred}(f) - F_{\eta, ref}(f)|^2 df)^{1/2} }{(\int | F_{\eta, pred}(f)|^2 df)^{1/2}+(\int | F_{\eta, ref}(f)|^2 df)^{1/2}}
    
    
    See
    Kim, I-C., et al. "Real-time phase-resolved ocean wave prediction in directional wave fields: Enhanced algorithm and experimental validation." Ocean Engineering 276 (2023): 114212.
    
    https://www.sciencedirect.com/science/article/pii/S0029801823005966

    The calculation is done between t_start and t_stop if given (if not, on the largest interval where both signals are defined)
    Series must have time as index.

    Parameters
    ==========
    df: pd.Series
        the experimental time signal
        corresponds to :math:`F_{\eta, pred}`
    df_ref: pd.Series
        the reference time signals
        corresponds to :math:`F_{\eta, ref}`
    dt: float
        time step
    removeAverage: bool
        to remove or not the average. 
        The ISSP from ECN uses this.
    
    Returns
    =======
    float
        the value of the SSP or ISSP.
    """
    if dt is None:
        # extract dt based on the largest dt in the signals
        dt = max(max(np.diff(df.index.to_numpy())), max(np.diff(df_ref.index.to_numpy())))
    if t_start is None: 
        t_start = max(df.index[0], df_ref.index[0])
    if t_stop is None:
        t_stop = min(df.index[-1], df_ref.index[-1])

    new_index = np.arange(t_start, t_stop, dt)

    df = df_interpolate(df, newIndex = new_index)
    df_ref = df_interpolate(df_ref, newIndex = new_index)
    
    F_df = fftDf(df)
    F_df_ref = fftDf(df_ref)

    if removeAverage: 
        mean_F = F_df_ref.mean()
    else: 
        mean_F = 0
    num = trapezoid((F_df-F_df_ref).abs()**2, x=F_df.index)**0.5
    denum = (trapezoid((F_df-mean_F).abs()**2, x=F_df.index)**0.5
            +trapezoid((F_df_ref-mean_F).abs()**2, x=F_df.index)**0.5)

    return num/denum
