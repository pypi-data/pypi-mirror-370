# -*- coding: utf-8 -*-

import os
import numpy as np
import json
from glob import glob
import xarray as xa
from Snoopy import logger

def dataset_to_rao( ds , quantity = "excitation") :
    """Convert dataset of hydrodynamic coefficients to sp.Rao objects

    Parameters
    ----------
    ds : xarray.Dataset
        Hydrodynamic coefficients

    Returns
    -------
    excitationRaos : sp.Rao
        DESCRIPTION.

    """
    from Snoopy import Spectral as sp

    if quantity == "excitation"  :
        # Excitation
        excitationRaos = sp.Rao( b = np.deg2rad(ds["head"].values) , w = ds.freq, cvalue = ds["excitation"].values ,
                             modes = [ sp.Modes.FX , sp.Modes.FY, sp.Modes.FZ, sp.Modes.MX , sp.Modes.MY , sp.Modes.MZ ],
                             refPoint = [0.0 , 0.0, 0.0],
                             waveRefPoint = [ 0.0 , 0.0  ] ,
                             forwardSpeed = ds.attrs["speed"][0],
                             # waterDepth = ds.attrs["waterDepth"]
                           )

        return excitationRaos

    else :
        raise(NotImplementedError)


def json_to_rao( db_path, output_path ):
    """Convert from .json to .rao format (for StarViewer compatibility)

    For now, only excitation

    Parameters
    ----------
    db_path : str
        HydroStar-V database path
    output_path : str
        Output folder for .rao files

    Returns
    -------
    None.

    """
    from Snoopy import Spectral as sp

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    ds = read_appUnsteadyFlow_json( db_path )

    excitationRao = dataset_to_rao(ds , quantity="excitation")

    for name , rao in [ (name ,  excitationRao.getRaoAtMode( imode )) for  imode, name in enumerate( sp.modesIntsToNames( excitationRao.getModes() ))  ] :
        rao.write( os.path.join( output_path ,  f"Excitation_{name:}.rao"))

    return


def read_hydrostarV_database(inputdata):
    if isinstance(inputdata,dict):
        folderPath = inputdata.get("folderPath","./")
        data = inputdata
    elif isinstance(inputdata,str):
        folderPath = os.path.dirname(os.path.abspath(inputdata))
        data = read_json(inputdata)
    globalParameters        = data["globalParameters"]["libGlobal"]
    outputDir               = globalParameters["outputDirName"]
    baseFlowDB_filename     = data["appBaseFlow"]["baseFlowDB"]["fileName"]
    meshDB_filename         = data["appBaseFlow"]["meshDB"]["fileName"]
    baseFlow_db_path        = os.path.join(folderPath,outputDir,"DataBase")
    unsteadyFlow_db_path    = os.path.join(folderPath,outputDir,"UnsteadyFlow_DB")
    kwargs = {}
    kwargs.update(read_appMeshBaseFlow_json(baseFlow_db_path,
                                            baseFlowDB_filename= baseFlowDB_filename,
                                            meshDB_filename    = meshDB_filename))

    kwargs["rho"] = rho = globalParameters["waterDensity"]
    kwargs["g"] = g     = globalParameters["gravity"]

    kwargs["software"]  = "HydroStar-V"
    hflowDBs = read_appUnsteadyFlow_json(unsteadyFlow_db_path)

    outputList = []
    for hflowDB in hflowDBs:
        hflowDB.update(kwargs)
        # Scaling is needed here!
        # In the future this scaling might be moved
        # inside hydrostar-v fortran code
        speed = hflowDB["speed"]
        hflowDB["added_mass"]    *= rho
        hflowDB["wave_damping"]  *= rho
        hflowDB["excitation"]    *= rho*g
        ## Attention! HydroStarV output forces in hydrostar convention!
        ## Convert back to standard convention here!
        hflowDB["excitation"]    = np.conj(hflowDB["excitation"]*1j)
        hflowDB["hydrostatic_hull"]    *= rho*g
        hflowDB["base_flow_stiffness"] *= rho * speed**2
        # More scaling to be tested?

        outputList.append(hflowDB)
    return outputList
def read_appUnsteadyFlow_json(db_path,selectForce=1):
    """ Read appUnsteadyFlow json output files and return a
        dictionary of hydrodynamic forces


    Parameters
    ----------
    db_path : str
        appUnsteadyFlow database path
    selectForce: int
        1 : chose to output extForce1 and radForces1
        2 : chose to output extForce2 and radForces2
    Returns
    -------
    unsteadyFlowOutput : xarray
        array of hydrodynamic forces
    """

    files = glob(db_path + '/Forces_SPEED_*_HEAD_*_FREQ_*.json')

    #print( f"Reading HydroStar-V results : {len(files):} cases found." )

    if len(files) == 0 :
        raise(Exception(f"No data found in {db_path:}"))

    waveFreq = []
    encFreq = []
    forwardSpeed = []
    waveHeading = []

    extForceCollect   = []
    addedMassCollect  = []
    waveDampingCollect= []
    waveLength = []

    # read json files
    for file in files:
        data = read_json(file)

        uFlowParams = data.get("unsteadyFlowParams",{})

        forwardSpeed.append(uFlowParams.get("forwardSpeed"))
        waveHeading.append(uFlowParams.get("waveHeadingDeg"))
        waveFreq.append(uFlowParams.get("waveFreqRad"))
        encFreqVal  = uFlowParams.get("encFreqRad")
        encFreq.append(encFreqVal)
        waveLength.append(uFlowParams.get("waveLength"))


        if selectForce == 1:
            extForceCollect.append(read_vector(data,"extForces1"))
            radForces = read_vector(data,"radForces1")

        elif selectForce == 2:
            extForceCollect.append(read_vector(data,"extForces2"))
            radForces = read_vector(data,"radForces2")

        addedMassCollect.append(radForces.real)
        
        waveDampingCollect.append(radForces.imag *encFreqVal)


    speed   = np.unique(np.array(forwardSpeed,dtype='float64'))
    head    = np.unique(np.array(waveHeading,dtype='float64'))
    wrps    = np.unique(np.array(waveFreq,dtype='float64'))

    # sort
    speed.sort()
    head.sort()
    wrps.sort()

    nspeed = len(speed)
    nw     = len(wrps)
    nhead  = len(head)

    excitation  = np.empty((1,nhead,nw,6),dtype='complex64')
    added_mass   = np.empty((1,1,nhead,nw,6,6),dtype='float64')
    wave_damping = np.empty((1,1,nhead,nw,6,6),dtype='float64')

    we   = np.empty((nhead,nw),dtype='float64')
    wl   = np.empty((nhead,nw),dtype='float64')

    # gather all
    unsteadyFlowOutputCollect = []
    returnDicts = []
    for i_speed in range(nspeed):
        for i_head in range(nhead):
            for i_freq in range(nw):
                indx = np.where( (speed[i_speed] == forwardSpeed) \
                               & (head[i_head]   == waveHeading)
                               & (wrps[i_freq]   == waveFreq) )[0][0]
                we[i_head,i_freq] = encFreq[indx]
                wl[i_head,i_freq] = waveLength[indx]
                excitation[0,i_head,i_freq,:] = extForceCollect[indx]
                added_mass[0,0,i_head,i_freq,:,:] = addedMassCollect[indx]
                wave_damping[0,0,i_head,i_freq,:,:] = waveDampingCollect[indx]
        returnDicts.append({ "excitation"       : excitation,
                             "added_mass"       : added_mass,
                             "wave_damping"     : wave_damping,
                             "speed"            : speed[i_speed],
                             "frequency"        : wrps,
                             "heading"          : head,
                             "wave_length"      : wl,
                             "encounter_frequency" : we})
    return returnDicts



def read_appMeshBaseFlow_json(  db_path,
                                baseFlowDB_filename= "baseFlowDB.json",
                                meshDB_filename    = "meshDB.json"):

    """
    Read appPrepMesh and appBaseFlow json output files and return cob position and
    hydroStatic stiffness matrices


    Parameters
    ----------
    db_path : str
        appBaseFlow database path

    Returns
    -------
    meshBaseFlowOutput :xarray
        array of hydrodynamic forces
    """

    # open baseFlowDB
    data = read_json(os.path.join(db_path , baseFlowDB_filename))

    kHyd = read_vector(data.get("baseFlowConst",{}), "HydroStaticStiffness")
    kBf  = read_vector(data.get("baseFlowConst",{}), "BaseFlowStiffness")

    # open meshDB to get hull mesh ID and cob
    data = read_json(os.path.join(db_path , meshDB_filename))


    nMeshPair = data.get("nMeshPair")

    assert ( nMeshPair == kHyd.shape[2] )

    id_hull = []
    RefPointList = []
    for i in range(nMeshPair):
        surfaceType = data.get("meshPair_"+str(i+1),{}).get("surfaceType")
        if surfaceType == "hull" :
            id_hull.append(i)
            RefPointList.append(read_vector( db = data.get("meshPair_"+str(i+1),{}).get("cMesh", {}),
                                     vector_name = "refPosition" ))

    RefPoint = np.array(RefPointList)
    CoBPoint = np.array(RefPointList)

    RefWave  = np.array(CoBPoint[0,:2])
    return {
        "cob_point"  : CoBPoint,
        "ref_point"  : RefPoint,
        "ref_wave"   : RefWave,
        "base_flow_stiffness" : np.transpose(kBf[:,:,id_hull],axes=(2,0,1)),
        "hydrostatic_hull"    : np.transpose(kHyd[:,:,id_hull],axes=(2,0,1))}



def read_json(inputJSON):
    """ simple wrap to simplify reading json """
    with open(inputJSON,"r") as fid:
        data = json.load(fid)
    return data

def read_vector(db, vector_name):
    """Read vector with vector_name in a database
    Can also read complex vector

    Parameters
    ----------
    db : dict
        dictionnary that contain the vector
    vector_name : str
        name of vector

    Returns
    -------
    output : numpy ndarray
        vector output
    """
    vector_dict = db.get(vector_name,{})
    shape_  = vector_dict.get("dimVec")
    if "data" in vector_dict.keys(): # real vector
        vector_ = vector_dict.get("data")
        return np.reshape(vector_, shape_, order = 'F')
    elif ("dataRe" in vector_dict.keys()) and ("dataIm" in vector_dict.keys()):
        # complex vector
        vector_realPart = np.reshape(vector_dict.get("dataRe"), shape_, order = 'F')
        vector_imagPart = np.reshape(vector_dict.get("dataIm"), shape_, order = 'F')
        return vector_realPart+ 1j*vector_imagPart


if __name__ == "__main__":

    pass
