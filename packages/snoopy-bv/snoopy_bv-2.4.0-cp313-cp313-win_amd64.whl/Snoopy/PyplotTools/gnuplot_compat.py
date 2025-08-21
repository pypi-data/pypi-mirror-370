import pandas as pd


def read_csv_block( filepath_or_buffer, i_block, *, sep_block = "\n\n",  **kwargs ) :
    """Read csv file per block.

    This is principally meant to read file in the same fashion as gnuplot, which separate blocks by two blank lines.

    Parameters
    ----------
    filepath_or_buffer : str, path object or file-like object
        File to read.
    i_block : int or List(int) or "all"
        Position of block to be read. If integer, a DataFrame with block content is returned.
        If list of integer, a list of DataFrame is returned.
        If "all", list of dataframe containing all blocks content is returned
    sep_block : str, optional
        Block delimiter. The default is "\n\n".
    kwargs : Various
        Arguments passed to pd.read_csv

    Returns
    -------
    pd.DataFrame or List(pd.DataFrame)
        The data as pd.DataFrame
    """

    from io import StringIO

    with open(filepath_or_buffer, 'r') as a:
        data = a.read()

    blockList = [StringIO(str_) for str_ in data.split(sep_block)]

    if isinstance(i_block, str) :
        if i_block.lower() == "all" :
            return [pd.read_csv(blockList[i] , **kwargs) for i in range(len(blockList))]
        else :
            raise(Exception(f"Invalid argument for i_block: {i_block:}"))
    elif hasattr(i_block, "__iter__"):
        return [pd.read_csv(blockList[i] , **kwargs) for i in i_block]
    else:
        return pd.read_csv(blockList[i_block], **kwargs)
