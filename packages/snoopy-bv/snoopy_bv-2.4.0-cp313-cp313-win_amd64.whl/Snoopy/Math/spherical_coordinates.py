import numpy as np


def x_to_t(x):
    """Convert from cartesian to spherical coordinates. Works in n dimension.
    
    Parameters
    ----------
    x : np.ndarray
        Cartesian coordinates (x1,x2,x3, ... , xn)
        
    Returns
    -------
    np.ndarray
        Spherical coordinates (r, theta_1, theta_2, ... , theta_n-1)
        
    Note
    ----
    A vectorized, much faster implementation is now implemented in cpp ( Snoopy.Math.x_to_t )
    
    """
    ndim = len(x)
    res = np.full((ndim), np.nan)
    r = np.linalg.norm( x )
    res[0] = r
    for i in range(1, ndim-1):
        res[i] =  np.arctan2(  np.linalg.norm( x[i:] ) , x[i-1] )
        
    res[ndim-1] =  np.arctan2( x[ndim-1]  , x[ndim-2] )
    return res



def t_to_x( t ):
    """Convert from spherical to cartesian coordinates. Works in n dimension.
    
    Parameters
    ----------
    t : np.ndarray
        Spherical coordinates (r, theta_1, theta_2, ... , theta_n-1)

    Returns
    -------
    np.ndarray
        Cartesian coordinates (x1,x2,x3, ... , xn)
        
    Note
    ----
    A vectorized, much faster implementation is now implemented in cpp ( Snoopy.Math.t_to_x )
    """
    ndim = len(t)
    res = np.full((ndim), np.nan, dtype = float)
    for i in range(0,ndim-1) :
        res[i] =  np.prod( np.sin( t[1:i+1] ) ) * np.cos( t[i+1] )
        
    res[ndim-1] =  np.prod( np.sin( t[1:ndim-1] ) ) * np.sin( t[ndim-1] )
    return res * t[0]


if __name__ == "__main__":
    from Snoopy import Math as sm
    
    x = np.array([ 0.2 ,0.6 , 0.4 , 0.6])
    xx = np.array( [ x for _ in np.arange(20)] )
    
    t =  x_to_t( x )
    t_cpp = sm.x_to_t( xx )

    assert( np.isclose( t , t_cpp[0,:] ).all() )
    x_back_cpp = sm.t_to_x( t_cpp )
    x_back = t_to_x(  t_cpp[0,:] )
    assert( np.isclose( x_back , x_back_cpp[0,:] ).all() )
    assert( np.isclose( x_back , x ).all() )
