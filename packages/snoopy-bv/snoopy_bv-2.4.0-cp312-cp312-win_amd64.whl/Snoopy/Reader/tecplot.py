"""
   Reader for tecplot files. Works at least with output from HOS-NWT.
"""

from Snoopy import logger
import pandas as pd
import numpy as np

def tecplot_HOS(file, i_col = 0, skip_last_block = False):
    """Read tecplot format.

    Might be made more general, currently works well at least with HOS-NWT output.

    Parameters
    ----------
    file : str
        Name of file to read
    i_col : int, optional
        Columns to read, by default 0
    skip_last_block : bool, optional
        If True, the last block is skipped, this can be useful read a results even if the calculation is still on-going, by default False.

    Returns
    -------
    pd.DataFrame
        File content given as a panda dataframe. index is time, columns are spatial coordinates
    """
    import re
    from io import StringIO

    with open(file, 'r') as a:
        data = a.read()

    blockList = [StringIO(str_) for str_ in data.split("\nZONE")]
    data_list = []
    time_list = []
    # NOTES:
    # VARIABLES="time" "p1"                 : in probes.dat (separated by whitespace)
    # VARIABLES="x","eta","etax","etat"     : in FreeSurface_CN_Stream.dat (separated by comma)
    if len( blockList ) > 2 :   # Several "ZONE" block
        # TITLE...
        # VARIABLES...
        # ZONE...
        # ...
        # ZONE...
        # ...
        logger.info("Reading surface time series")
        for ibloc in range(1, len(blockList) - int(skip_last_block) ) :
            # Parse zone information
            blocHeader = blockList[ibloc].readline()
            time = float( re.findall(r"[\S]+", blocHeader.replace(",", " ")  )[2] )
            time_list.append( time )
            if ibloc == 1 :
                a = pd.read_csv(  blockList[ibloc] , skiprows = 0, header = None , names = [ "x" , "y" , time ] , usecols = [0,1,2] , sep=r'\s+', engine = "c" , dtype = float)
                x = a.x.values
                y = a.y.values
                data_list.append( a.loc[:,time].values )
            else :
                data_list.append( pd.read_csv(  blockList[ibloc] , skiprows = 0, header = None , names = [ time ] , usecols = [i_col]  , sep=r'\s+', engine = "c", dtype = float ).values[:,0])


        if len(np.unique(y)) == 1 :  # 1D data
            col = pd.Index(x, name = "x")
        else: # 2D data  
            col = pd.MultiIndex.from_tuples( zip( x,y) )
        return pd.DataFrame( index = pd.Index(time_list, name = "time"), columns = col , data = np.stack( data_list, axis = 0 ))
    elif len( blockList ) == 2 :     # At least 1 "ZONE" block
        # Possible errors: tecplot file does not have TITLE and VARIABLES lines, instead it
        # has the empty lines just before ZONE line
        # Here we assume, that
        # TITLE=...
        # VARIABLES=...
        # ZONE T=...
        # ...
        # blockList[0] will contain:
        #   TITLE=...\nVARIABLES=...
        # blockList[1]:
        #   T=...\n...
        # Parse variables :
        title = blockList[0].readline()                     # TITLE=
        while title.startswith("#") :                       # remove headers befor the 
            title = blockList[0].readline()                 # TITLE keyword
        var = blockList[0].readline().split("=")[1].strip() # VARIABLES= ...
        # the following re.split splits by whitespace or comma the substring quated by " or '
        # 'aaa' 'bbb ccc', "ddd, eee", 'fff ggg, hhh'
        #   => ['aaa', 'bbb ccc', 'ddd, eee', 'fff ggg, hhh']
        # and then, we need to replace the first entrance of ' or " by empty symbol
        vars_ = [ c.replace("'", "").replace('"', '') for c in re.split(r"['\"]\s*[,]?\s*['\"]", var)]
        blocHeader = blockList[1].readline()                # ZONE T = "....", I = XXX[, J = YYY]
        return pd.read_csv(  blockList[1] , skiprows = 0, header = None , names = vars_, index_col = 0, sep=r'\s+', dtype = float )
    else :   # Only one block without "ZONE"
        # Possible errors, if tecplot file does not have TITLE and VARIABLES lines and starts directly by ZONE keyword
        # Here we assume, that
        # TITLE=...
        # VARIABLES=...
        # <data>
        # Parse variables :
        title = blockList[0].readline()
        while title.startswith("#") :
            title = blockList[0].readline()
        var = blockList[0].readline().split("=")[1].strip()
        # see comments to re.split in 'elif len (blockList ) == 2' block
        vars_ = [ c.replace("'", "").replace('"', '') for c in re.split(r"['\"]\s*[,]?\s*['\"]", var)]
        return pd.read_csv(  blockList[0] , skiprows = 0, header = None , names = vars_, index_col = 0, sep=r'\s+', dtype = float )



if __name__ == "__main__" :

    print ("Plot tecplot files")

    import argparse
    from Snoopy.PyplotTools import dfSlider
    parser = argparse.ArgumentParser(description='Visualize HOS 2D results', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument( '-nShaddow', help='For animation', type = int, default=0)
    parser.add_argument( "inputFile" )
    args = parser.parse_args()

    if args.inputFile[:-4] == ".wif" :
        from Spectral import Wif
        df = Wif( args.inputFile ).Wave2DC( tmin = 0.0 , tmax = 200. , dt = 0.4 , xmin = 0. , xmax = 400. , dx = 4. ,  speed = 0. )
    else :
        df = tecplot_HOS( args.inputFile )
    dfSlider( df )
