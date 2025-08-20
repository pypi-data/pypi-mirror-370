import os
import numpy as np
import pandas as pd


def openFoamReader(filename, *args, **kwargs):
    """Automatic reader for OpenFoam and foamStar postProcesses files.
    
    For common file names, detect the appropriate reader for the file based on its name. 
    Forces, moments, and body motion are implemented. 

    Returns
    -------
    data: pd.DataFrame
        a data frame which index is the time.
        Column names are either automatically determined by the header
        (foamStar postProcesses) or hard coded by the reader (OpenFoam postProcesses)
    """
    dicoReader = {
        "motions.dat": openFoamReadMotion,
        "sixDofDomainBody.dat": openFoamReadMotion,
        "surfaceElevation.dat": openFoamReadMotion,
        "fx.dat": openFoamReadLoads,
        "fy.dat": openFoamReadLoads,
        "fz.dat": openFoamReadLoads,
        "mx.dat": openFoamReadLoads,
        "my.dat": openFoamReadLoads,
        "mz.dat": openFoamReadLoads,
        "PTS_localMotion_pos.dat": openFoamReadMotion,
        "PTS_localMotion_vel.dat": openFoamReadMotion,
        "PTS_localMotion_acc.dat": openFoamReadMotion,
        "forces.dat": openFoamReadForce,
        "fFluid.dat": openFoamReadLoads,
        "mFluid.dat": openFoamReadLoads,
        "fCstr.dat": openFoamReadLoads,
        "mCstr.dat": openFoamReadLoads,
        "acc.dat": openFoamReadLoads,
        "alpha.water": openFoamReadProbes,  # OF probes (not freeSurface probes!)
        "p": openFoamReadProbes,
        "p_rgh": openFoamReadProbes,
        "U": openFoamReadProbes,
        "positions": openFoamReadProbesPositions, # specific to foamStar
    }
    fname = os.path.basename(filename)
    return dicoReader.get(fname, openFoamReadMotion)(filename, *args, **kwargs)
    # .get(fname, openFoamReadMotion) means that the method openFoamReadMotion is used by default (if filename is not in dicoReader)


def foamStarReadHeader(filename: str, maxLines: int = 5, add_units: bool = False, points=False, formating="pos"):
    """Read the header of an output file which has been constructed with foamStar style.
    
    If the header is foamStar style, then it should have:
    - info about the system in the first few lines
    - names of the columns
    - units

    For example:
    ```
    # motion info (body)
    # time surge sway heave roll pitch yaw surge_vel sway_vel heav_vel omega_x omega_y omega_z surge_acc sway_acc heave_acc roll_acc pitch_acc yaw_acc
    # [s] [m] [m] [m] [deg] [deg] [deg] [m/s] [m/s] [m/s] [rad/s] [rad/s] [rad/s] [m/s2] [m/s2] [m/s2] [rad/s2] [rad/s2] [rad/s2]
    ```
    The last two lines are used to construct the column names, while other are discarded.

    If points=True:
    3 lines exists with the x, y, and z positions.
    So the header is:
        - info about the system or type of measurement
        - names for the columns (points names, typically "s12")
        - (maybe units of the measurement)
        - 3 lines with x, y and z positions
    The user can choose what to use as names, throug the variable format:
        - names only ("s12") [choice pos]
        - one position only (value of x, y or z) choice x, y or z
        - names + position ("s12 (x, y, z)") choice posVal

    For example:
    ```
    # Internal load (my.dat)
    # t s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 s14 s15 s16 s17 s18 s19 s20 s21 s22 s23
    # x -1.971900e+02 -1.711900e+02 -1.551900e+02 -1.391900e+02 -1.231900e+02 -1.071900e+02 -9.119000e+01 -7.519000e+01 -5.919000e+01 -4.319000e+01 -2.719000e+01 -1.119000e+01 4.810000e+00 2.081000e+01 3.681000e+01 5.281000e+01 6.881000e+01 8.481000e+01 1.008100e+02 1.168100e+02 1.328100e+02 1.488100e+02 1.688100e+02
    # y 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00 0.000000e+00
    # z -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00 -6.800000e+00
    ```

    Parameters
    ----------
    filename: str
        filename, including path.
    add_units: bool, default: False
        if True, then the units are added to the column names: "surge [m]"
    maxLines: int
        maximal number of lines in the header (should not be modified, except if exotic header)
    points: bool, default: False
        if True and if format is specified, the reader will read the x, y and z value
    format: str, default: "pos"
        possible values: "pos"|"x"|"y"|"z"|"posVal"

    Returns
    -------
    names: List[str]
        names to be used as column names for a reader.
    """
    with open(filename, "r") as fil:
        header = [
            l.strip().split()
            for l in [fil.readline() for line in range(maxLines + 1)]
            if l.startswith("#")
        ]
    line_name = [line_number for line_number, line in enumerate(header) if line[1]=="time" or line[1]=="t"]# line which starts by the word "time"
    names = header[line_name[0]][2:]
    if add_units: #units are always specified immediatly after names
        units = header[line_name[0]+1][2:]
        if "[" not in units[0]:
            raise ValueError(f"Units not correct in header. Should be formatingted as [s]. Please verify. \n The line used to specify units was {units}.")
        names = [name + " " + unit for (name, unit) in zip(names, units)]
    if points:
        if formating in ["x", "y", "z"]:
            line_name = [line_number for line_number, line in enumerate(header) if line[1]==formating]# line which starts by the word "time"
            names = header[line_name[0]][2:]
            names = [float(name) for name in names]
        elif formating == "posVal":
            line_name = [line_number for line_number, line in enumerate(header) if line[1]=="x"]
            if len(line_name) == 1: 
                x = header[line_name[0]][2:]
            else:
                x = ["" for value in names]
            line_name = [line_number for line_number, line in enumerate(header) if line[1]=="y"]
            if len(line_name) == 1: 
                y = header[line_name[0]][2:]
            else: y = ["" for value in names]
            line_name = [line_number for line_number, line in enumerate(header) if line[1]=="z"]
            if len(line_name) == 1: 
                z = header[line_name[0]][2:]
            else: z = ["" for value in names]
            names = [f"{pos} ({float(xv):.2e}, {float(yv):.2e}, {float(zv):.2e})" for pos, xv, yv, zv in zip(names, x, y, z)]
    return names

def openFoamReadForce(filename, headerStyle=None, *args, **kwargs):
    """Reader for foamStar and OpenFoam forces postProcesses.
    
    foamStar implements a fluidForces postProcess which writes a forces.dat 
    file, which structure is simpler than the OpenFoam forces.dat file. 
    To differenciate between both, we can read the first few lines: 
    
    - ` # forces ` is an OpenFoam file
    - ` # fluidForces (body)` is a foamStar file 

    Parameters
    ----------
    filename: str
    headerStyle: None or "foamStar"
        if "foamStar", the reader is automaticallly assuming a foamStar-style format
        (no parenthesis in the output file)
    """
    with open(filename, "r") as stream:
        first_line = stream.readline().split()
    if (headerStyle=="foamStar") or ("fluidForces" in first_line): 
        return openFoamReadForce_foamStarStyle(filename, *args, **kwargs)
    else: 
        return openFoamReadForce_OpenFoamStyle(filename, *args, **kwargs)
    #TODO: add this function


def openFoamReadForce_foamStarStyle(filename: str, add_units: bool=False):
    """Read openFoam "forces" file that uses the foamStar style (with parenthesis).

    Parameters
    ----------
    filename: str
    add_units: bool, default: False
        if True, then the units are added to the column names: "fx [N]"
    """
    names = foamStarReadHeader(filename, add_units=add_units)
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        sep = r'\s+',   #delim_whitespace=True, depricated
        dtype=float,
        index_col=0,
        names=names,
    )
    return df

def openFoamReadForce_OpenFoamStyle(filename, field="total"):
    """Read openFoam "forces" file that uses the OpenFoam style (with parenthesis).

    Parameters
    ----------
    filename: str
    field: str, default: "total"
        define if you want the "total" of the forces and moments or only the "pressure" component.
    """
    with open(filename, "r") as fil:
        data = [
            l.strip().strip().replace("(", " ").replace(")", " ").split()
            for l in fil.readlines()
            if not l.startswith("#")
        ]
    xAxis = np.array([float(l[0]) for l in data])
    nx = len(xAxis)
    ns = len(data[0]) - 1
    parsedArray = np.zeros((nx, ns))
    if field == "total" or field == "pressure":
        dataArray = np.zeros((nx, 6))
        labels = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]

    for i, l in enumerate(data):
        parsedArray[i, :] = [float(k) for k in l[1:]]

    if ns == 12:
        if field == "total":
            for i in range(3):
                dataArray[:, i] = parsedArray[:, 0 + i] + parsedArray[:, 3 + i]
                dataArray[:, i + 3] = parsedArray[:, 6 + i] + parsedArray[:, 9 + i]
        else:
            dataArray = parsedArray
            labels = [
                "Fx-Pressure",
                "Fy-Pressure",
                "Fz-Pressure",
                "Fx-Viscous",
                "Fy-Viscous",
                "Fz-Viscous",
                "Mx-Pressure",
                "My-Pressure",
                "Mz-Pressure",
                "Mx-Viscous",
                "My-Viscous",
                "Mz-Viscous",
            ]
    elif ns == 18:
        if field == "total":
            for i in range(3):
                dataArray[:, i] = (
                    parsedArray[:, 0 + i]
                    + parsedArray[:, 3 + i]
                    + parsedArray[:, 6 + i]
                )
                dataArray[:, i + 3] = (
                    parsedArray[:, 9 + i]
                    + parsedArray[:, 12 + i]
                    + parsedArray[:, 15 + i]
                )
        elif field == "pressure":
            for i in range(3):
                dataArray[:, i] = parsedArray[:, 0 + i]
                dataArray[:, i + 3] = parsedArray[:, 9 + i]

        else:
            dataArray = parsedArray
            labels = [
                "Fx-Pressure",
                "Fy-Pressure",
                "Fz-Pressure",
                "Fx-Viscous",
                "Fy-Viscous",
                "Fz-Viscous",
                "Fx-Porous",
                "Fy-Porous",
                "Fz-Porous",
                "Mx-Pressure",
                "My-Pressure",
                "Mz-Pressure",
                "Mx-Viscous",
                "My-Viscous",
                "Mz-Viscous",
                "Mx-Porous",
                "My-Porous",
                "Mz-Porous",
            ]
    else:
        dataArray = parsedArray
        if field != "total":
            labels = ["Unknown{}".format(j) for j in range(ns)]
    return pd.DataFrame(index=xAxis, data=dataArray, columns=labels)


def openFoamReadHeaderProbe(filename, maxLines: int=200, position=False):
    """ Read header of probes in openfoam format

    Parameters
    ----------
    filename : str
    maxLines : int, optional
        Number of lines max to read, by default 200
    position : bool, optional
        if True, will add the positions to the names, by default False

    Returns
    -------
    List[str]
        names to be used by the reader
    """
    with open(filename, "r") as fil:
        header = [
            l.strip()
            for l in [fil.readline() for line in range(maxLines + 1)]
            if l.startswith("#")
        ]
    if position:
        names = [ f"p{line.split(' ')[2]} : {line.split('(')[1].split(')')[0]}" for line in header if "# Probe" in line]
    else: 
        names = [ f"p{line.split(' ')[2]}" for line in header if "# Probe" in line]
    return names


def openFoamProbesDataFrame(filename, maxLines: int=200):
    """ Return a list of probes positions

    Parameters
    ----------
    filename : str
    maxLines : int, optional
        Number of lines max to read, by default 200

    Returns
    -------
    pandas.DataFrame
    """
    with open(filename, "r") as fil:
        header = [
            l.strip()
            for l in [fil.readline() for line in range(maxLines + 1)]
            if l.startswith("#")
        ]
    names = [ f"p{line.split(' ')[2]}" for line in header if "# Probe" in line]
    positions = [ f"{line.split('(')[1].split(')')[0]}" for line in header if "# Probe" in line]
    positions = [pos.split(" ") for pos in positions]
    res = pd.DataFrame(data={"names":names, "positions":positions})
    return res


def openFoamReadProbes(filename: str,
                       maxProbeNumber: int = 200,
                       formating=None):
    """ Read an OF probe file (not a freeSurface probe!)

    Parameters
    ----------
    filename : str
    maxProbeNumber : int, optional
        each probe will be a line in the header
        This value should be larger than the number of probes expected.
        by default 200
    formating : str, optional
        if "pos", will add the position of the probe to the probe name.
        if None, the names will be p0, p1, etc.
        by default None
    """
    if formating == "pos":
        position = True
    else:
        position = False
    names = openFoamReadHeaderProbe(filename, position=position, maxLines=maxProbeNumber)
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        sep = '\\s+',   #delim_whitespace=True, deprecated
        dtype=float,
        index_col=0,
        names=names,
    )
    return df


def openFoamReadProbesPositions(filename: str,
                       maxProbeNumber: int = 200):
    """ Read an OF probe file (not a freeSurface probe!)

    Parameters
    ----------
    filename : str
    maxProbeNumber : int, optional
        each probe will be a line in the header
        This value should be larger than the number of probes expected.
        by default 200
    """
    names = openFoamReadHeaderProbe(filename, position=False, maxLines=maxProbeNumber)
    names = [f"{item}_{suffix}" for item in names for suffix in ["x", "y", "z"]]
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        sep = '\\s+',   #delim_whitespace=True, deprecated
        dtype=float,
        index_col=0,
        names=names,
    )
    return df


def openFoamReadMotion(
    filename: str,
    headerStyle: str = "foamStar",
    add_units: bool = False,
    headerMaxLines: int = 5,
    namesLine: int = 1,
    points=False,
    formating="pos"
):
    """Read motion or loads from foamStar.

    Parameters
    ----------
    filename: str
        filename, including path.
    headerStyle: str, default: "foamStar"
        indicate style of the header.
        If not foamStar, then the line number where to extract the column name should be given (default is second line)
    add_units: bool, default: False
        if True, then the units are added to the column names: "surge [m]"
    headerMaxLines: int, default: 5
        maximal number of lines in the header (should not be modified, except if exotic header)
    namesLines: int, default: 1
        line number of the line with the names (if header is not foamStar)
    points: bool, default: False
        if True, then use the format value for getting the values of points
    formating: str, default: "pos"
        specification for the format of the column names
        possible values: 
            - "pos": use only the names of the points (typically: "s12")
            - "x", "y", or "z": use the float value of x, y, or z
            - "posVal": use the complete names + positions with the format "name (x, y, z)"
    """
    if headerStyle == "foamStar":
        names = foamStarReadHeader(filename, add_units=add_units, maxLines=headerMaxLines, formating=formating, points=points)
    else:
        with open(filename, "r") as fil:
            header = [
                l.strip().split()
                for l in [fil.readline() for line in range(headerMaxLines + 1)]
                if l.startswith("#")
            ]
            names = header[namesLine][2:]
    df = pd.read_csv(
        filename,
        comment="#",
        header=None,
        sep = '\\s+',   #delim_whitespace=True, depricated
        dtype=float,
        index_col=0,
        names=names,
    )
    return df


def openFoamReadLoads(
    filename: str,
    headerStyle: str = "foamStar",
    add_units: bool = False,
    headerMaxLines: int = 5,
    formating: str = "pos"
):
    return openFoamReadMotion(filename=filename, headerStyle=headerStyle, add_units=add_units, 
                              headerMaxLines=headerMaxLines, formating=formating, points=True)



def openFoamReadDisp(filename):
    """Read displacement signal from foamStar.

    Parameters
    ----------
    filename : str 
        The tabulated displacement file
    Returns
    -------
    DataFrame
        The displacement as dataframe

    Format sample:
    --------------
    (  
    (0.0 ( (0.0 0.0 0.0) ( 0.0 0.0 0.0) ) )  
    (0.1 ( (0.0 0.0 1.0) ( 0.0 0.0 0.0) ) )  
    (0.2 ( (0.0 0.0 2.0) ( 0.0 0.0 0.0) ) )  
    (0.3 ( (0.0 0.0 3.0) ( 0.0 0.0 0.0) ) ) 
    )
    """    
    with open(filename, "r") as fil:
        data = [
            l.strip().strip().replace("(", " ").replace(")", " ").split()
            for l in fil.readlines()
            if not l.startswith("#")
        ]
    data = np.array(list(filter(None, data))).astype(float)
    labels = ["Dx", "Dy", "Dz", "Rx", "Ry", "Rz"]

    xAxis = data[:, 0]
    dataArray = data[:, 1:]

    return pd.DataFrame(index=xAxis, data=dataArray, columns=labels)


def openFoamWriteDisp(df, filename):
    """Write displacement signal for foamStar
    """
    with open(filename, "w") as f:
        f.write("(\n")
        for index, row in df.iterrows():
            f.write(
                "({:21.15e}  (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) )\n".format(
                    index, *row
                )
            )
        f.write(")")
    

def openFoamWriteForce(df, filename):
    """Write force in foamStar format
    """

    ns = df.shape[1]

    if not (ns in [6, 12, 18]):
        raise ValueError("ERROR: forces datafame should contain 6, 12 or 18 components!")

    with open(filename, "w") as f:
        f.write("# Forces\n")
        f.write(
            "# CofR                : ({:21.15e} {:21.15e} {:21.15e})\n".format(0, 0, 0)
        )
        if ns == 6:
            f.write("# Time                forces(pressure) moment(pressure)\n")
        elif ns == 12:
            f.write(
                "# Time                forces(pressure viscous) moment(pressure viscous)\n"
            )
        elif ns == 18:
            f.write(
                "# Time                forces(pressure viscous porous) moment(pressure viscous porous)\n"
            )

        for index, row in df.iterrows():
            if ns == 6:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
            elif ns == 12:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
            elif ns == 18:
                f.write(
                    "{:21.15e}\t(({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e})) (({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}) ({:21.15e} {:21.15e} {:21.15e}))\n".format(
                        index, *row
                    )
                )
