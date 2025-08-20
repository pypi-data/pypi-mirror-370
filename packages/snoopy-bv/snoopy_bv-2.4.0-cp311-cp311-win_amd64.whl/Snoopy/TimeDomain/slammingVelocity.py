import numpy as np
import pandas as pd
from Snoopy.TimeDomain import getDownCrossID


def getSlammingVelocity( rwe_ts, *, pos_z, vz_ts = None, method = "diff" ):
    """Exctract impact velocities

    Parameters
    ----------
    rwe_ts :
        Time series of position

    method : str, optional
        Method to extract impact velocity. The default is "diff". "map_up", "map_down and "interpolate" requires velocity input

    vz_ts : pd.Series
        Time series of vertical velocities. (for method in ["map_up", "map_down ,"interpolate"] )

    pos_z : float
        Position relative to mean free surface

    Returns
    -------
    pd.Series
        Series of impact velocities
    """

    if not np.isclose(rwe_ts.index.values ,  rwe_ts.index.values).all() :
        raise(Exception())

    margin = pos_z - rwe_ts

    id_ = getDownCrossID(margin.values , threshold = 0)

    if method == "map_up":
        return vz_ts.iloc[ id_ ]

    elif method == "map_down":
        return vz_ts.iloc[ id_ + 1]

    elif method == "interpolate":
        alpha = ( rwe_ts.values[ id_ + 1] - pos_z ) /  (rwe_ts.values[ id_ + 1] - rwe_ts.values[ id_ ])
        val = alpha * vz_ts.values[ id_ ] +  (1-alpha) * vz_ts.values[ id_ + 1]
        time =  alpha * rwe_ts.index.values[ id_ ] +  (1-alpha) * rwe_ts.index.values[ id_ + 1]
        return pd.Series( index = time , data = val )

    elif method == "diff" :
        val = ( rwe_ts.values[ id_ + 1] - rwe_ts.values[ id_ ] ) / ( rwe_ts.index.values[ id_ + 1] - rwe_ts.index.values[ id_ ] )
        time = ( rwe_ts.index.values[ id_ + 1] + rwe_ts.index.values[ id_ ] )*0.5
        return pd.Series( index = time , data = val )

    else :
        raise(Exception(f"Method {method:} not reckognised"))

