import numpy as np
from Snoopy import Meshing as msh

def convertPropHull(propHull, symType = msh.SymmetryTypes.NONE, read_coef = False, keep_symmetry = True):
    """Convert mesh from HydrpStar mesh storage to Snoopy object.

    Parameters
    ----------
    propHull : np.ndarray
        The mesh in HydroStar storage format
    symType : int, optional
        Symmetry, by default msh.SymmetryTypes.NONE

    Returns
    -------
    Mesh
        The mesh object
    """

    nPanel = len(propHull)
    nodes = np.stack( [ np.hstack( [propHull[:,12],  propHull[:,15],propHull[:,18], propHull[:,21]  ] ),
                        np.hstack( [propHull[:,13],  propHull[:,16],propHull[:,19], propHull[:,22]  ] ),
                        np.hstack( [propHull[:,14],  propHull[:,17],propHull[:,20], propHull[:,23]  ] ),
                      ]).T

    panels = np.arange( 0, nPanel*4,1 ).reshape( 4, nPanel ).T
    
    mesh = msh.Mesh( Vertices = nodes, Quads = panels, Tris = np.zeros((0,3), dtype = int),
                     keepSymmetry = keep_symmetry , symType = symType)
        
    if read_coef : 
        mesh.setPanelsData( propHull[:,11][:,np.newaxis], dataNames = ["POROSITY"], dataTypes = [0] , dataFreqs = [np.nan], dataHeads = [np.nan] )

    return mesh
    


def read_hslec_h5(filename, engine = "h5py", format = "hydrostarmesh", keep_symmetry = True):
    """Read hslec hdf output and convert to Snoopy.Mesh.

    Parameters
    ----------
    filename : str
        Filename
        
    format : str
        If format "hydrostarmesh", the mesh is returned as a ````HydroStarMesh```` object (concatenation of meshes), 
        If format "mesh", the mesh is returned as a ````Mesh````, where belong the panels is then given by "SECTION" data.
        
    Returns
    -------
    msh.HydroStarMesh or msh.Mesh
        The mesh
    """
    import h5py


    # Compatibility with HydroStar <= 8.2.
    cd = { "nb_body":"NBBODY",  "hull_symmetry":"HULL_SYMMETRY", "prophull":"PROPHULL",
           "nb_hull":"N_HULL", "proppont":"PROPPONT",  "nb_pont":"N_PONT", "propplate":"PROPPLATE",
           "nb_plate":"N_PLATE" }
        
    if engine != "h5py" : 
        logger.warning(f"engine={engine:} is ignored, hslec_h5 is now always read with h5py")
    
    with h5py.File(filename, "r") as da :
        version = da.attrs.get("version", None)
        if version is None : 
            k = cd
        else: 
            k = {d:d for d in cd.keys()}
        
        nbbody = da.attrs[k["nb_body"]][0]
        hull_symmetry = da.attrs[k["hull_symmetry"]][0]
        prophull = [ da[k["prophull"]] [ da[k["nb_hull"]][ibody,0] - 1 : da[k["nb_hull"]][ibody,1]] for ibody in range(nbbody) ]
        propont =  [ da[k["proppont"]] [ da[k["nb_pont"]][ibody,0] - 1 : da[k["nb_pont"]][ibody,1]] for ibody in range(nbbody) ]
        proplate = [ da[k["propplate"]][ da[k["nb_plate"]][ibody,0] - 1 : da[k["nb_plate"]][ibody,1]] for ibody in range(nbbody) ]


    symType = msh.SymmetryTypes.NONE
    if hull_symmetry == 1:
        symType = msh.SymmetryTypes.XZ_PLANE
    elif hull_symmetry == 2:
        symType = msh.SymmetryTypes.XZ_YZ_PLANES

    underWaterHullMeshes = [  convertPropHull(  prophull[ibody], keep_symmetry = keep_symmetry, symType = symType) for ibody in range(nbbody) ]

    aboveWaterHullMeshes = [  convertPropHull( propont[ibody], keep_symmetry = keep_symmetry, symType = symType) for ibody in range(nbbody) ]
    
    plateMeshes = [  convertPropHull( proplate[ibody] , symType = symType ) for ibody in range(nbbody) ]

    # TODO
    tankMeshes = []
    fsMeshes = []

    if format.lower() == "hydrostarmesh":
        return msh.HydroStarMesh( underWaterHullMeshes = underWaterHullMeshes,
                                aboveWaterHullMeshes = aboveWaterHullMeshes,
                                plateMeshes = plateMeshes,
                                fsMeshes = fsMeshes,
                                tankMeshes = tankMeshes,
                                )

    if format.lower() == "mesh":
        total_mesh = None
        for ibd in range(len(underWaterHullMeshes)) :
            for meshList, i_s in [ (underWaterHullMeshes,1) , (aboveWaterHullMeshes,11), (plateMeshes, 41) ,]:
                isection = i_s + ibd
                mesh = meshList[ibd]
                mesh.appendPanelsData( np.full( (mesh.getNPanels()) , isection) , dataName = "SECTION" )
                if total_mesh is None : 
                    total_mesh = mesh
                else :
                    total_mesh.append( mesh )
        return total_mesh
    else:
        raise(Exception(f"{format:} is not an available format"))
                


def read_hslec_waterline_h5(filename, engine = "h5py") :
    if engine == "h5py" :
        import h5py
        with h5py.File(filename, "r") as da :
            sym = da.attrs["hull_symmetry"][0]
            propwlin = da["propwlin"][:,:]
    else :
        import xarray
        with xarray.open_dataset(filename, engine = engine, phony_dims='access') as da :
            sym = da.attrs["hull_symmetry"]
            propwlin = da.PROPWLIN.values

    x1_ = propwlin[:,12]
    y1_ = propwlin[:,13]
    x2_ = propwlin[:,15]
    y2_ = propwlin[:,16]

    if sym == 1 :
        x1 = np.concatenate( [x1_, +x2_] )
        x2 = np.concatenate( [x2_, +x1_] )
        y1 = np.concatenate( [y1_, -y2_] )
        y2 = np.concatenate( [y2_, -y1_] )
    else :
        return x1_, y1_, x2_, y2_

    return x1, y1, x2, y2


if __name__ == "__main__" :
    from Snoopy import logger
    logger.setLevel(10)

    filename = rf"{msh.TEST_DATA:}/hslec_b31.h5"
    mesh = read_hslec_h5(filename , format = "mesh", keep_symmetry = False)
    mesh.vtkView()

