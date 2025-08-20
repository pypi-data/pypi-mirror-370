from scipy.interpolate import interp1d , InterpolatedUnivariateSpline  #InterpolatedUnivariateSpline is much much faster
import pandas as pd
import numpy as np



#To make the interpolator able to linearly interpolate
def extrap1d(interpolator , kind = "linear" ):
    xs = interpolator.x
    ys = interpolator.y
    if kind == "linear" :
       def pointwise(x):
           if x < xs[0]:     return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
           elif x > xs[-1]:  return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
           else:             return interpolator(x)
    elif kind == "constant" :
       def pointwise(x):
           if x < xs[0]:     return ys[0]
           elif x > xs[-1]:  return ys[-1]
           else:             return interpolator(x)
    else :
       print (kind , "extrapolator not supported")
       exit()
    def ufunclike(xs):
        return np.array(map(pointwise, np.array(xs)))
    return ufunclike


def df_interpolate( df , newIndex=None,  newColumns=None, xfunc = lambda x : x , yfunc = (lambda y : y , lambda y : y), interpolator = InterpolatedUnivariateSpline, axis = 0, **kwargs) :
    """Interpolate dataFrame with new index.
    
    Parameters
    ----------
    df : pd.DataFrames
        DataFrame to interpolate.
    newIndex : np.ndarray, optional
        New index, at which to interpolate. The default is None.
    newColumns : TYPE, optional
        New index, at which to interpolate. The default is None.
    xfunc : fun, optional
        Function to apply to x. The default is lambda x : x.
    yfunc : (fun, fun), optional
        Tuple of function and inverse function to apply to values before and after interpolation (for a log interpolation for instance). The default is (lambda y : y , lambda y : y).
    interpolator : class, optional
        interpolator class. The default is InterpolatedUnivariateSpline.
    **kwargs : Any
        kwargs passed to interpolator

    Returns
    -------
    df : pd.DataFrame
        The interpolated dataframe
    """
    ndf = df.copy()
    
    _is_se = False
    if type(df) == pd.Series:
        _is_se = True
        ndf = pd.DataFrame(ndf)
    
    if axis == 0 : 
        newData = {}
        for col in ndf.columns :
            f = interpolator( xfunc( ndf.index ) , yfunc[0]( ndf[col] )  , **kwargs )
            newData[col] =  yfunc[1]( f( xfunc(newIndex ) ) )
        ndf = pd.DataFrame(index = newIndex , data = newData)
    elif axis == 1 : 
        newData = {}
        for idx in ndf.index :
            f = interpolator( xfunc( ndf.columns ) , yfunc[0]( ndf.loc[idx,:] ) , **kwargs )
            newData[idx] =  yfunc[1]( f( xfunc(newColumns ) ) )
        ndf = pd.DataFrame(index = newColumns, data = newData).T
    else : 
        raise(Exception("Axis should be either 0 or 1"))
        
    if _is_se : 
        return pd.Series( ndf.iloc[:,0] )
    
    return ndf


def invInterpolate( df , newCol,  xfunc = (lambda y : y , lambda y : y) , yfunc =  lambda y : y , extrapolate = False , **kwargs) :
   """The col is now the index, with interpolated values of index as columns, xfunc apply to the original index
   WARNING : PROBLEM if the function is not monotonic !!
   """
   newData = {}
   for col in df.columns :
      f = interp1d( yfunc( df[col] ) , xfunc[0]( df.index )  , **kwargs )
      if extrapolate : f = extrap1d(f , extrapolate )
      newData[col] =   xfunc[1](f( yfunc(newCol) ))
   return pd.DataFrame(index = newCol , data = newData)




def Interp2dVariadicAxis(x, y, xs, ys, data):
    r"""Interpolate in variadic ys.
    
    ys is supposed varying non uniformly with respect to x.
    
    :param float x: first axis value to interpolate to.
    :param float y: second axis value to interpolate to.
    :param ndarray xs: first axis vector of size nx.
    :param list ys: list of list containing the second axis varying with respect to first axis (size of ny(x) ).
    :param list data: list of list containing the data to interpolate (size of (nx, ny(x)) ).
    :return: float: data value interpolated at x and y.
    """
    # First get the surrounding time instants
    it0 = (np.abs(xs-x)).argmin()
    it1 = min(it0+1, len(xs)-1)
    if it0 == it1:
        return interp1d(ys[it1], data[it1])(y)
    dataY0 = interp1d(ys[it0], data[it0])(y)
    dataY1 = interp1d(ys[it1], data[it1])(y)
    x0 = xs[it0]
    x1 = xs[it1]
    return interp1d([x0, x1], [dataY0, dataY1])(x)

