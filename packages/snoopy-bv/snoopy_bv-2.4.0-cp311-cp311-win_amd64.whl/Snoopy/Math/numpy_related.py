import numpy as np

def round_nearest(x, a):
    """Round number with a given precision.

    Parameters
    ----------
    x : float (or numpy array)
        Array to round
    a : float, optional
        Precision

    Example
    -------
    >>> round_nearest(0.014 , 0.01)
    0.01
    >>> round_nearest( 4.3333 , 0.05)
    4.35
    """
    return np.round(np.round(x / a) * a, -int( np.floor(np.log10(a))))


def round_sig(x, sig = 4):
    """Round float, keeping a given number of significant digit

    Parameters
    ----------
    x : float or int
        Float to round
    sig : int, optional
        Number of significant figure. The default is 4.
        
    Returns
    -------
    float or int (same type as x)
        The rounded float
        
    Example
    -------
    >>> round_sig( 21235, 2)
    21000
    >>> round_sig( 2.2156, 3)
    2.22 
    """
    return np.round(x, sig - np.floor(np.log10(abs(x))).astype(int)-1)



def round_sum(data, decimals):
    """Return round-up array, keeping sum intact.

    Parameters
    ----------
    data : Array like
        Array to round
    decimals : int
        Number of decimals

    Returns
    -------
    rounded_data : Array like
        The rounded array.

    Example
    -------
    >>> round_up_sum(  [0.33, 0.34, 0.33]  , 1 )    
    array([0.3, 0.4, 0.3])
    
    >>> round_up_sum([0.66, 0.66, 0.67, 0.67, 0.67, 0.67] , 1  )
    array([0.6, 0.6, 0.7, 0.7, 0.7, 0.7])
    """
    shape_ = data.shape
    data = data.reshape(-1)

    rounded_data = np.round(data, decimals)
    o_sum = round(np.sum(data))
    if not np.isclose(o_sum, round(o_sum, decimals)):
        raise (Exception(f"Original sum should be round (here, sum is {o_sum:})."))

    n_adjust = round((o_sum - np.sum(rounded_data)) / 10**(-decimals))
    sort_index = np.argsort(rounded_data - data)

    if n_adjust >= 0:
        rounded_data[sort_index[:n_adjust]] += 10**(-decimals)
    else:
        rounded_data[sort_index[n_adjust:]] -= 10**(-decimals)

    rounded_data = rounded_data.reshape(shape_)
    assert (np.isclose(np.sum(data), np.sum(rounded_data)))
    return rounded_data



def is_multiple( array , dx , tol = 1e-10):
    """Check if all element in array are multiple of dx.

    Due to floating point arithmetic, this can generally be only approximate.

    Parameters
    ----------
    array : array like
        Array to check
    dx : float
        Multiple to check for
    tol : float, optional
        Tolerance. The default is 1e-10

    Returns
    -------
    dx : Bool
        True if dx is a multiple of all element in array.
    """
    r = np.mod(array , dx)
    return (np.isclose( r, 0 ) | np.isclose(r , dx, atol = tol)).all()




def get_dx( array, dx=None, eps = 1e-3, raise_exception=False ):
    """Check if array is evenly spaced.

    Parameters
    ----------
    array : TYPE
        DESCRIPTION.
    dx : float, optional
            Check if dx is the step. The default is None.
    eps : float, optional
            Tolerance. The default is 0.001

    Returns
    -------
    dx : float or None
        Step, if any, None otherwise
    """
    n = len(array)
    if n <= 1 :
        return None

    if dx is None :
        dx = ( np.max( array ) - np.min(array)) / (n-1)

    # Check that all frequency are multiple of df
    check = (np.diff(array) - dx) < eps

    if check.all() :
        return dx
    else :
        if raise_exception : 
            raise(Exception( "Array must be evenly spaced to retrieve 'dx'" ))
        return None

def edges_from_center(array):
    """Return edges from bin centers.
    
    Check that data are evenly spaced

    Parameters
    ----------
    array : array
        Centers

    Returns
    -------
    array
        edges
    """
    dx = get_dx( array )

    if dx is None :
        raise(Exception( f"{array:} is not evenly spaced" ))

    return np.append( [array[0]-0.5*dx] , [  array + 0.5*dx]  )



if __name__ == "__main__" :

    #Quick test :
    array = np.array([ 0.5 , 1.5 , 2.5, 3.5 ])
    print (edges_from_center( array ))

    round_sig( x = 21235, sig=2)
