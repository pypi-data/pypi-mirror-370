import numpy as np
from matplotlib import pyplot as plt



def plotMesh( coords, quads, tris=None, ax=None, color = "darkblue" , proj="xy", **kwargs ):
    """Plot a surface mesh

    Parameters
    ==========
    proj: str
        List of axes to projecte the mesh: "xy", "xz" or "yz"
    """

    if proj == "xy":
        proj = [0, 1]
    elif proj =="xz":
        proj = [0, 2]
    elif proj == "yz":
        proj = [1, 2]
    else: 
        raise ValueError

    if ax is None :
        fig, ax = plt.subplots()

    q = np.c_[ (quads[:,:], quads[:,0]) ]
    ax.plot( coords[ q , proj[0] ].transpose(), coords[ q , proj[1] ].transpose() , "-" , color = color , **kwargs)

    if tris is not None :
        t = np.c_[ (tris[:,:], tris[:,0]) ]
        ax.plot( coords[ t , proj[0] ].transpose(), coords[ t , proj[1] ].transpose() , "-" , color = color , **kwargs)

    return ax


