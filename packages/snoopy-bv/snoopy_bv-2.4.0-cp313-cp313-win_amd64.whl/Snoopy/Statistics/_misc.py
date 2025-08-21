import numpy as np

def compact_probability_df( df, probabilty_column, rounding_dict  = {} ):
    """Sum the probability of identical event and remove duplicates.
    
    Using pandas this now a simple .groupby().sum()... 
    
    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION.
    rounding_dict : dict, optional
        Dictionary to round data columns. The default is {}.

    Returns
    -------
    pd.DataFrame
        Compacted probability dataframe
        
    Example
    -------
    >>> df = pd.DataFrame(index = [1,2,3,4,5] , data = {"val" : [1,1,1,2,2],"val2" : [3.,1.,1.,2.,2.1], "PROB" : 5*[1/5] }  )
    >>> df
        val  val2  PROB
     1    1   3.0   0.2
     2    1   1.0   0.2
     3    1   1.0   0.2
     4    2   2.0   0.2
     5    2   2.1   0.2
     >>> st.compact_probability_df(df, probabilty_column, rounding_dict = {"val2":0})
        val  val2  PROB
     4    2   2.0   0.4
     1    1   3.0   0.2
     2    1   1.0   0.4
    """
    
    df_ = df.copy()
    for k , v in rounding_dict.items() :
        df_.loc[:, k] = np.round( df_.loc[:, k] , v )
    col = [i for i in df_.columns if i != probabilty_column]
    
    return df_.groupby( col ).sum().reset_index()
