import pandas as pd
import _Spectral
from deprecated import deprecated

"""
Handle RAO names and enum

This looks too messy to be the correct way to handle things. Ideas are welcomed...
"""


modesNameToModeDict = _Spectral.Modes.__members__


# Note : the Froude scale dimension is the dimension of the quantity. Dimension of the Rao is "n-1".
# "SYM", "TYPE", "COMPONENT", "HSTAR_UNIT" , "FROUDE_SCALE".
modeNameToSymDict  = {
    'NONE':   (0,  "UNKNOWN", 0, "N/A" , None) ,
    'SURGE':  (+1, "MOTION", 1 , "m/m" , 1) ,
    'SWAY':   (-1, "MOTION", 2 , "m/m", 1) ,
    'HEAVE':  (+1, "MOTION", 3 , "m/m", 1) ,
    'ROLL':   (-1, "MOTION", 4 , "deg/m", 0) ,
    'PITCH':  (+1, "MOTION", 5 , "deg/m", 0 ) ,
    'YAW':    (-1, "MOTION", 6 , "deg/m", 0) ,
    'FX':     (+1, "LOAD", 1 , "N/m", 3) ,
    'FY':     (-1, "LOAD", 2 , "N/m", 3) ,
    'FZ':     (+1, "LOAD", 3 , "N/m", 3) ,
    'MX':     (-1, "LOAD", 4 , "N.m/m", 4) ,
    'MY':     (+1, "LOAD", 5 , "N.m/m", 4) ,
    'MZ':     (-1, "LOAD", 6 , "N.m/m", 4) ,
    'WAVE':   ( 0, "WAVE" , 0 , "m/m", 1) ,
    'RWE':    ( 0, "PRESSURE" , 0 , "m/m", 1) ,
    'SECTFX': (+1, "INTERNALLOAD", 1 , "N/m", 3) ,
    'SECTFY': (-1, "INTERNALLOAD", 2 , "N/m", 3) ,
    'SECTFZ': (+1, "INTERNALLOAD", 3 , "N/m", 3) ,
    'SECTMX': (-1, "INTERNALLOAD", 4 , "N.m/m", 4) ,
    'SECTMY': (+1, "INTERNALLOAD", 5 , "N.m/m", 4) ,
    'SECTMZ': (-1, "INTERNALLOAD", 6 , "N.m/m", 4) ,
    'WATERVELOCITY_X': (0, "WATERVELOCITY", 1, "m/s/m", 0.5),
    'WATERVELOCITY_Y': (0, "WATERVELOCITY", 2, "m/s/m", 0.5),
    'WATERVELOCITY_Z': (0, "WATERVELOCITY", 3, "m/s/m", 0.5),
    'PRESSURE' : (0,  "PRESSURE" , 1, "m/m", 1),
    'VSURGE':  (+1, "VELOCITY", 1 , "m/s/m", 0.5) ,
    'VSWAY':   (-1, "VELOCITY", 2 , "m/s/m", 0.5) ,
    'VHEAVE':  (+1, "VELOCITY", 3 , "m/s/m", 0.5) ,
    'VROLL':   (-1, "VELOCITY", 4 , "deg/s/m", -0.5) ,
    'VPITCH':  (+1, "VELOCITY", 5 , "deg/s/m", -0.5 ) ,
    'VYAW':    (-1, "VELOCITY", 6 , "deg/s/m", -0.5) ,
    'ASURGE':  (+1, "ACCELERATION", 1 , "m/s²/m" , 0) ,
    'ASWAY':   (-1, "ACCELERATION", 2 , "m/s²/m", 0) ,
    'AHEAVE':  (+1, "ACCELERATION", 3 , "m/s²/m", 0) ,
    'AROLL':   (-1, "ACCELERATION", 4 , "deg/s²/m", -1) ,
    'APITCH':  (+1, "ACCELERATION", 5 , "deg/s²/m", -1 ) ,
    'AYAW':    (-1, "ACCELERATION", 6 , "deg/s²/m", -1 ) ,
    'ROLLCENTER': (0, "ROLLCENTER", 66, "m", None),
    'PITCHCENTER': (0, "PITCHCENTER", 66, "m", None),
    'AXIAL_LINESTRESS':   (0,  "axial-stress", 0, "MPa/m" , None) ,
    'PT1_LINESTRESS':   (0,  "pt1-combined-stress", 0, "MPa/m" , None) ,
    'PT2_LINESTRESS':   (0,  "pt2-combined-stress", 0, "MPa/m" , None) ,
    'PT3_LINESTRESS':   (0,  "pt3-combined-stress", 0, "MPa/m" , None) ,
    'PT4_LINESTRESS':   (0,  "pt4-combined-stress", 0, "MPa/m" , None) ,
    'BOTTOM_X_STRESS':   (0,  "bottom-x-normal-stress", 0, "MPa/m" , None) ,
    'BOTTOM_Y_STRESS':   (0,  "bottom-y-normal-stress", 0, "MPa/m" , None) ,
    'BOTTOM_XY_STRESS':   (0,  "bottom-xy-shear-stress", 0, "MPa/m" , None) ,
    'TOP_X_STRESS':   (0,  "top-x-normal-stress", 0, "MPa/m" , None) ,
    'TOP_Y_STRESS':   (0,  "top-y-normal-stress", 0, "MPa/m" , None) ,
    'TOP_XY_STRESS':   (0,  "top-xy-shear-stress", 0, "MPa/m" , None) ,
    'BOTTOM_ENVELOPE_STRESS':   (0,  "bottom-envelope-stress", 0, "MPa/m" , None) ,
    'TOP_ENVELOPE_STRESS':   (0,  "top-envelope-stress", 0, "MPa/m" , None) ,
}


# Add all components for added-mass and damping
for imode in range(1,7):
    for jmode in range(1,7):
        mode_str = f"{imode}{jmode}"
        mode_int = int(mode_str)
        if imode < 4:
            if jmode < 4:
                unitCA = r"$kg/s$"
                unitCM = r"$kg$"
            else:
                unitCA = r"$kg.m/s/rad$"
                unitCM = r"$kg.m/rad$"
        else:
            if jmode < 4:
                unitCA = r"$kg.m/s$"
                unitCM = r"$kg.m$"
            else:
                unitCA = r"$kg.m^2/s/rad$"
                unitCM = r"$kg.m^2/rad$"
        modeNameToSymDict["CM_"+mode_str] = (0,"ADDED-MASS" ,mode_int,unitCM,0)
        modeNameToSymDict["CA_"+mode_str] = (0,"WAVE-DAMPING",mode_int,unitCA,0)


# TYPE and COMPONENT corresponds to the "RAOTYPE" and "COMPONENT" from HydroStar and Homer output files.
modesDf = pd.DataFrame(  data = modeNameToSymDict , index = pd.Index(["SYM", "TYPE", "COMPONENT", "HSTAR_UNIT" , "FROUDE_SCALE"]) ).transpose()
modesDf.index.name = "NAME"

modesDf.loc[ : , "MODE"] = [ _Spectral.Modes.__members__[k] for k in modesDf.index ]
modesDf.loc[ : , "INT_CODE"] = [ _Spectral.Modes.__int__( a ) for a in modesDf.MODE ]


def modesIntToMode( int_ ) :
    if int_ in modesIntToNameDict.keys() :
        return _Spectral.Modes(int_)
    else :
        _Spectral.Modes.NONE


"""For conversion to HydroStar RAO files
"""
def modesNameToType( name ) :
    """Convert SNOOPY ID to HydroStar/Homer 'RAOTYPE'

    Parameters
    ----------
    name : str
        Name

    Returns
    -------
    str
        "RAOTYPE"  (HydroStar/Homer convention)

    Example
    -------
    >>> modesNameToType("HEAVE")
    'MOTION'
    """
    return modesDf.loc[name, "TYPE"]


def modesNameToComponent( name ) :
    """Convert SNOOPY ID to HydroStar/Homer 'RAOTYPE'

    Parameters
    ----------
    name : str
        Name

    Returns
    -------
    int
        "COMPONENT"  (HydroStar/Homer convention)

    Example
    -------
    >>> modesNameToType("HEAVE")
    3
    """
    return modesDf.loc[name, "COMPONENT"]



modesIntToTypeComponentDict =  modesDf.set_index("INT_CODE").loc[ : , ["TYPE", "COMPONENT"] ].transpose().to_dict("list")
modesTypeComponentToIntDict = { tuple(v) : k for k, v in modesIntToTypeComponentDict.items() }

def modesIntsToNames( modesInts ):
    """Convert modes integer code to name (strings)
    """
    # return [ modesIntToNameDict[i] for i in modesInts ]
    return modesDf.reset_index().set_index("INT_CODE").loc[ modesInts , "NAME" ].values





"""
Following lines are for compatibility with older code, might be removed
"""
modesIntToNameDict = { i : _Spectral.Modes(i).__str__().split(".") [1] for i in range( len(modesNameToModeDict)   ) }

@deprecated
def modeFromModesTypeComponent(raotype,component):
    """Build RAO mode from raotype and component

    Parameters
    ----------
    rao_type : str
        rao type
    component : int
        component
    Returns
    -------
    _Spectral.Modes
        _description_
    """
    return _Spectral.Modes( modesTypeComponentToIntDict.get( ( raotype, component ) , 0 ) )

@deprecated
def modeToModesTypeComponent(mode):
    """Get raotype and component from RAO mode

    Parameters
    ----------
    mode : _Spectral.Modes
        RAO mode

    Returns
    -------
    (rao_type,component)
    """
    return modesIntToTypeComponentDict[mode.value]