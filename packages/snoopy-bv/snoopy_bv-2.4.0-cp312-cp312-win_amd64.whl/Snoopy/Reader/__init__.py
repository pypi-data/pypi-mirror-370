import os
class InputSyntaxError(Exception):
    pass

from .hydrostar_v import read_hydrostarV_database
from .hydrostar import PressureData
from .starspec import StarspecParser
from .bvFormat import bvReader, bvWriter, bvReader_csv
from .tecplot import tecplot_HOS
from .openFoam import openFoamReader, openFoamReadMotion
from .arianeReader import ariane8Reader, ariane702Reader
from .OperaH5Reader import OperaH5Reader
from .bvHdf5 import bvReader_h5, bvWriter_h5
from .simpleReader import simpleReader
from .json_tools import NumpyEncoder

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")


#Reader dictionary => possible to pass reader as string
dicoReader = {
              "bvReader" : bvReader ,
              "openFoamReader" : openFoamReader ,
              "ariane702Reader" : ariane702Reader ,
              "simpleReader" : simpleReader ,
              "ariane8Reader" : ariane8Reader ,
              "bvReader_h5" : bvReader_h5 ,
              "bvReader_csv" : bvReader_csv ,
              }

dicoWriter = {
             "bvWriter" : bvWriter ,
             "bvWriter_h5" : bvWriter_h5 ,
             }

def dfRead( filename , reader = "auto", **kwargs  ) :
    """
       Read and return as a dataFrame
    """
    import pandas as pd

    if reader == "auto" :
        """
        Choose reader based on extension
        """
        ext = os.path.splitext(filename)[-1]
        if ext in [".ts" , ".dat"] : reader = "bvReader"
        elif ext in [".h5", ".hdf"] : reader = "bvReader_h5"
        elif ext in [".csv"] : reader = "bvReader_csv"
        elif filename[-6:] == ".ts.gz" : reader = "bvReader"
        else : raise(Exception("Can not infer reader type for " + filename))

    if reader not in dicoReader.keys() :
        print ("Unknown reader, please choose within : {}".format(  list(dicoReader.keys() ) ))
        return

    res = dicoReader[reader] (filename , **kwargs )

    if type(res) == tuple :
        return pd.DataFrame( index = res[0]  , data = res[1] , columns = res[2] , dtype = float)
    else :
        return res


def dfWrite( filename, df, writer = "auto", **kwargs  ) :

    if writer == "auto" :
        """
        Choose reader based on extension
        """
        if os.path.splitext(filename)[-1] == ".ts" : writer = "bvWriter"
        elif os.path.splitext(filename)[-1] == ".h5" : writer = "bvWriter_h5"
        elif filename[-6:] == ".ts.gz" : writer = "bvWriter"
        else : raise(Exception("Can not infer reader type for " + filename))

    if writer not in dicoWriter.keys() :
        print ("Unknown writter, please choose within : {}".format(  list(dicoWriter.keys() ) ))
        return

    dicoWriter[writer] (filename, xAxis=df.index, data=df.values, labels=df.columns, **kwargs )
    
def getListSeparator():
    '''Retrieves the Windows list separator character from the registry'''
    import winreg as wr
    aReg = wr.ConnectRegistry(None, wr.HKEY_CURRENT_USER)
    aKey = wr.OpenKey(aReg, r"Control Panel\International")
    val = wr.QueryValueEx(aKey, "sList")[0]
    return val
