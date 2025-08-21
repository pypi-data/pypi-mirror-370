from Snoopy import Meshing as msh
import numpy as np
from Snoopy import logger

def getQuadsConnectivity( nx, ny ) :
    quads = np.empty( ((nx-1)*(ny-1),4), dtype = int )
    rangex = np.arange(nx-1, dtype = int)
    rangey = np.arange(ny-1, dtype = int)
    for iy in rangey:
        ipanel = rangex + iy * (nx-1)
        quads[ ipanel ,0] = rangex + nx * iy
        quads[ ipanel ,1] = 1 + rangex + nx * iy
        quads[ ipanel ,2] = 1 + rangex + nx * (iy + 1)
        quads[ ipanel ,3] = rangex + nx * (iy + 1)
    return quads


def createRectangularGrid( x_range, y_range, x_min=None, x_max=None, dx=None, y_min=None, y_max=None, dy=None, z=0 ):
    """Return rectangular grid mesh.
    """
    
    if x_min is not None: 
        logger.warning("DeprecationWarning : createRectangularGrid : please use x_range, instead of x_min/x_max")
    
    if x_range is None : 
        x_range = np.arange(x_min, x_max, dx)
        y_range =  np.arange(y_min, y_max, dy)
        
    X, Y = np.meshgrid( x_range, y_range )
    nodes = np.stack( [X.flatten(), Y.flatten(), np.full(len(Y.flatten()),z )] ).T
    quads = getQuadsConnectivity( len(x_range), len(y_range) )

    return msh.Mesh( Vertices = nodes, Quads = quads, Tris = np.zeros((0,3), dtype = float)  )
