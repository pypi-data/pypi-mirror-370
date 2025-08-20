import numpy as np
import pandas as pd

"""Routines to help with concatenation of time-series. Nothing rocket-science here...
"""

class ConcatTimeSeries(object) :
    def __init__(self, df_list, trim_0=0, trim_1=0 ) :
        """Concatenate time trace into a long one (index is offset).

        For instance, if you have two runs of 3hours, each starting at t=0,
        this would return the concatenated run, with index from 0 to 6 hours.

        Parameters
        ----------
        df_list : list
            List of dataframe
        trim_0 : float
            trim each times series (begining)
        trim_1 : float
            trim each times series (end)

        Example
        -------
        >>> time = np.arange(0, 10 , 0.1)
        >>> se0 = pd.DataFrame( index = time, data  = {"val" : np.cos(time * np.pi * 2 / 10) } )
        >>> se1 = pd.DataFrame( index = time, data  = {"val" : 2*np.cos(time * np.pi * 2 / 10) } )
        >>> ct = ConcatTimeSeries( [se0, se1], trim_0 = 0.0, trim_1 = 0.0)
        >>> se_concat = ct()

        """

        if trim_0 + trim_1 > 0. :
            self.df_list = [ df.loc[  df.index.values[0] + trim_0 : df.index.values[-1] - trim_1] for df in df_list ]
        else :
            self.df_list = df_list

        # Duration of each runs
        self._durations = np.array([ df.index[-1] - df.index[0] for df in self.df_list ])

        # Starting point of each runs
        self._t0 = np.array([ df.index[0] for df in self.df_list  ])

        # Time average step of each runs
        self._dx = self._durations / np.array( [len(df)-1 for df in self.df_list]  )

        # Offset applied to each time-series
        self._offset = (self._t0 - np.insert( np.cumsum( self._durations[:-1] + self._dx[:-1]  ), 0 , 0))

        # To handle both Series and DataFrame
        self._se = isinstance( self.df_list[0], pd.Series)

        self.new_index = np.concatenate( [ df.index.values - self._offset[i] for i, df in enumerate(self.df_list)] )
        self.new_data = np.concatenate( [df.values for df in self.df_list ])

    def __call__(self, original_index_as_columns = False, original_id_as_columns = False):
        """Return the concatenated time series

        Parameters
        ----------
        original_index_as_columns : bool, optional
            If True, the original index is output as additional columns. The default is False.

        Returns
        -------
        pd.DataFrame
            The concatenated time-series
        """

        return_se = self._se
        if original_index_as_columns or original_id_as_columns :
            return_se = False

        if return_se :
            return pd.Series( index = self.new_index, data = self.new_data)
        else :
            df = pd.DataFrame( index = self.new_index, data = self.new_data, columns = self.df_list[0].columns )

            if original_index_as_columns :
                df.loc[: ,"original_index" ] = self.original_index()

            if original_id_as_columns :
                df.loc[: ,"original_signal"] = np.concatenate(  [n*[i] for i, n in enumerate([len(d) for d in self.df_list])]  )

            return df


    def concatenate_synchronized_channels(self , df_list) :
        """Concatenate different time series that were sync with original time-series (but not necessarily same tmin/tmax/dt)

        Parameters
        ----------
        df_list : list
            List of dataframe

        Returns
        -------
        pd.DataFrame
            The concatenated time-series
        """
        new_index = np.concatenate( [ df.index.values - self._offset[i] for i, df in enumerate(df_list)] )
        new_data = np.concatenate( [df.values for df in df_list ])
        return pd.DataFrame( index = new_index , data = new_data )


    def original_index(self) :
        return np.concatenate( [ df.index.values for df in self.df_list ] )


if __name__ == "__main__":

    from matplotlib import pyplot as plt

    time = np.arange(0, 10 , 0.1)

    timeSub =  np.arange(2, 5 , 0.2)

    se0 = pd.DataFrame( index = time, data  = {"val" : np.cos(time * np.pi * 2 / 10) } )
    se1 = pd.DataFrame( index = time, data  = {"val" : np.cos(time * np.pi * 2 / 10) } )

    se0_sub = pd.DataFrame( index = timeSub, data  = {"val" : np.cos(timeSub * np.pi * 2 / 10) } )
    se1_sub = pd.DataFrame( index = timeSub, data  = {"val" : np.cos(timeSub * np.pi * 2 / 10) } )


    ct = ConcatTimeSeries( [se0, se1], trim_0 = 0.0, trim_1 = 0.0)

    se_concat = ct()
    fig, ax = plt.subplots()
    se_concat.plot(ax=ax)

    se_concat_sub = ct.concatenate_synchronized_channels( [se0_sub, se1_sub] )
    se_concat_sub.plot(ax=ax, linestyle = "" , marker = "+")


