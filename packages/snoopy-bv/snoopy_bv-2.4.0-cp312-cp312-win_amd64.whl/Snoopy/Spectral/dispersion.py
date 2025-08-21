from Snoopy import logger
from _Spectral import w2k, k2w, w2we
import numpy as np
from numpy import tanh, sinh, pi, cos, sqrt

grav = 9.81


def k2Cp( k , depth = 0. ) :
    """Wave number to phase velocity

    Parameters
    ----------
    k : float or array
        Wave number
    depth : float, optional
        Water depth. The default is 0..

    Returns
    -------
    float or array
        Phase velocity Cp

    """
    if depth < 1e-4 :
        return ( (grav/k) )**0.5
    else :
        return ( (grav/k) * tanh(k*depth) )**0.5



def cp2k( cp, depth = 0.0 ):
    """Phase velocity to period


    Parameters
    ----------
    cp : float
        Phase velocity.
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    k : float
        Wave number

    """
    if depth < 1e-4:
        return grav / cp**2
    else :
        raise(NotImplementedError)


def w2Cp( w, depth ) :
    """Frequency to phase velocity

    Parameters
    ----------
    w : float or array
        Circular frequency
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Phase velocity Cp

    """
    k = w2k( w, depth  )
    return k2Cp( k, depth )


def cp2t( cp, depth = 0.0 ):
    """Phase velocity to period


    Parameters
    ----------
    cp : float
        Phase velocity.
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    t : float
        Wave period

    """
    return 2 * pi / k2w( cp2k(cp, depth) , depth )


def w2l(w, depth = 0.0) :
    """Convert frequency to wave length

    Parameters
    ----------
    w : float or array
        Circular frequency
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    flaot or array
        Wave length

    """
    return 2*pi / w2k(w, depth = depth)

def w2Cg( w , depth = 0. ):
    """Frequency to group velocity

    Parameters
    ----------
    w : float or np.ndarray
        Wave frequency (rad/s).
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Group velocity

    """

    if (depth < 1e-4 or depth > 1e4)  :
        return 0.5 * grav / w  # Deep water
    else :

        if not hasattr(w, "__iter__") :
            return w2Cg( np.array([w]) , depth )
        else :
            res = np.empty( w.shape, dtype = float )
            k = w2k( w , depth )
            res[ np.where(k * depth < 1e-4 ) ] = sqrt(grav*depth)
            res[ np.where(k * depth >= 1e-4 ) ] = (0.5 + ( k*depth / (sinh(2*k*depth)) )) * k2Cp(  k , depth  )
            return res


def l2t(l , depth = 0. ):
    """Wave length to period

    Parameters
    ----------
    l : float
        Wave lengfth
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Wave period
    """
    return 2*pi / k2w( 2*pi / l, depth = depth )


def l2w(l , depth = 0. ):
    """Wave length to period

    Parameters
    ----------
    l : float
        Wave lengfth
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Wave frequency (rad/s)
    """
    return k2w( 2*pi / l, depth = depth )


def t2l(t , depth = 0. ):
    """Period to wave length

    Parameters
    ----------
    t : float or array
        Wave period
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Wave length

    """
    return 2*pi / w2k( 2*pi / t , depth = depth )


def t2k(t , depth = 0. ):
    """Period to wave number

    Parameters
    ----------
    t : float or array
        Wave period
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Wave number

    """
    return w2k( 2*pi / t , depth = depth )



def T2Te( T , speed , heading, depth = 0. ):
    """Compute encounter wave period from wave period and speed

    Parameters
    ----------
    T : float
        DESCRIPTION.
    speed : float
        Speed (m/s).
    heading : float
        DESCRIPTION.
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Encounter period.

    """
    return 2 * pi / w2we( w = 2*pi / T, speed=speed, b=heading, depth=depth )


def Te2T( Te, **kwargs ):
    return 2 * pi  / we2w( we = 2*pi / Te, **kwargs )


def w2Cp( w , depth = 0.):
    """Frequency to phase velocity

    Parameters
    ----------
    w : float or array
        Wave frequency (rad/s)
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    Returns
    -------
    float
        Phase velocity

    """
    return w / w2k( w, depth = depth )



def we2w( we, b, speed, depth = 0., return_type = "auto", w_guess = None) :
    """Convert from encouter frequency to wave frequency.

    Return max of the solutions from the 2nd degree equation solution. To check and improve

    Parameters
    ----------
    we : float or np.ndarray
        Encounter frequency.
    b : float
        Heading, in radians
    speed : float
        Speed (m/s).
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).
        For now infinite water-depth only
    return_type : str, optional
        Among ["auto" , "tuple", "float"]. The default is "auto"

    Raises
    ------
    Exception
        Finite depth is not yet handled


    Returns
    -------
    float or tuple
        Wave frequency.
    """

    we = np.abs(we)

    if speed < 1e-6 :
        return we

    cb = cos( b )

    if np.isclose(cb, 0):
        return we

    if (depth < 1e-4 or depth > 1e4)  :
        if cb <= 0.0:
            # This already works in vectorized fashion (if return type is float).
            w_1, w_2 = np.sort( [(grav + sqrt(grav*(-4*cb*speed*we + grav)))/(2*cb*speed) , (grav - sqrt(grav*(-4*cb*speed*we + grav)))/(2*cb*speed) ] )
            return (w_2,) if return_type == "tuple" else w_2
        else:
            if hasattr( we ,  "__len__" ): 
                return np.array([ we2w(we_, b, speed, depth, return_type, w_guess) for we_ in we ])
            
            w_3 = max((grav + sqrt(grav*(+4*cb*speed*we + grav)))/(2*cb*speed) , (grav - sqrt(grav*(+4*cb*speed*we + grav)))/(2*cb*speed)  )
            we_max = grav / (4*speed*cb)

            if np.isclose( we_max, we ): # Two solutions
                sols = np.array( [ grav / (2*speed*cb)  , w_3] )
                if return_type == "float" :
                    if w_guess is None:
                        raise(ValueError("Several solution to we"))
                    else :
                        return sols[ np.abs( sols - w_guess).argmin() ]
                return sols
                    
            elif we < we_max: # Three solutions
                w_1, w_2 = np.sort( [(grav + sqrt(grav*(-4*cb*speed*we + grav)))/(2*cb*speed) , (grav - sqrt(grav*(-4*cb*speed*we + grav)))/(2*cb*speed) ] )
                sols  = np.array( [w_1, w_2, w_3] )
                if return_type == "float" :
                    if w_guess is None:
                        raise(ValueError("Several solutions to we, cannot return float."))
                    else :
                        return sols[ np.abs( sols - w_guess).argmin() ]
                return sols
            
            else:  # Only one solution
                return np.array((w_3,)) if return_type == "tuple" else w_3
    else :
        raise(Exception("w2we not yet implemented in finite waterdepth"))




def Te2T( te, b, speed, depth = 0., return_type = "auto") :
    """Compute encounter wave period from wave period and speed


    Parameters
    ----------
    te : float
        Enounter wave Period.
    speed : float
        Speed (m/s).
    b : float
        Relative heading.
    depth : float, optional
        Water depth. The default is 0.0 (infinite water-depth).

    return_type : str, optional
        Among ["auto" , "tuple", "float"]. The default is "auto"

    Returns
    -------
    float or tuple
        Wave period.
    """
    return 2*np.pi / we2w( 2*np.pi / te , b, speed, depth , return_type )
    