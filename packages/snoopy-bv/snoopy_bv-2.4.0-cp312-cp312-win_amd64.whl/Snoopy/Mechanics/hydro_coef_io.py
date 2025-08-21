import numpy as np
import xarray as xr



def find_format_version(ds) :
    """Guess format version

    Parameters
    ----------
    ds : xarray.Dataset
        The dataset

    Returns
    -------
    str
        The format version
    """
    if "version" in ds.attrs.keys() :
        return str(ds.attrs["version"])
    else : 
        if "AddedMass" in ds.data_vars.keys() : 
            return "hydrostar_v8.2"



def hydro_coef_from_hstar_v82(inputXarray):
    old_names_to_new_names = {
            "AddedMass"        : "added_mass",
            "AddedMassInf"     : "added_mass_inf", 
            "Body"             : "body",
            "Body_i"           : "body_i",
            "Body_j"           : "body_j",
            "CoG"              : "cog",
            "Excitation_Re"    : "excitation_load_re",
            "Excitation_Im"    : "excitation_load_im",
            "Frequency"        : "frequency",
            "Heading"          : "heading",
            "HydroStatic"      : "hydrostatic",
            "HYDROSTATIC_HULL" : "hydrostatic_hull",
            "Incident_Im"      : "incident_load_im",
            "Incident_Re"      : "incident_load_re",
            "Mass"             : "mass_matrix",
            "Mode"             : "mode",
            "Mode_i"           : "mode_i",
            "Mode_j"           : "mode_j",
            "RefPoint"         : "ref_point",
            "RefWave"          : "ref_wave",
            "Motion_Im"        : "motion_im",
            "Motion_Re"        : "motion_re",
            "UserDamping"      : "user_damping_matrix",
            "WaveDamping"      : "wave_damping",
            "phony_dim_8"      : "xyz"}
    
    old_attrs_to_new_attrs = {
            "SPEED"             : "speed",
            "Speed"             : "speed",
            "Depth"             : "depth",
            "WATERDEPTH"        : "depth",
            "NBBODY"            : "nb_body",
            "NBMODE"            : "nb_mode",
            "InputFile"         : "input_file",
            "Executable"        : "executable",
            "ExecutableHash"    : "executable_hash",
            "InputFile"         : "input_file",
            "InputFileHash"     : "input_file_hash",
            "HydroStar commit"  : "solver_commit",
            "HydroStar version" : "solver_version"   }
    default_values = {"rho"     : 1025.,
                      "g"       : 9.806,
                      "software": "HydroStar",
                      "version" : 1.0  }

    # Eliminate key not in xarray
    for key in list(old_names_to_new_names.keys()):
        if (key not in inputXarray.keys()) and (key not in inputXarray.coords.keys()):
            if key not in ["phony_dim_8"] :# Hidden??
                old_names_to_new_names.pop(key)
                
    if "HYDROSTATIC_HULL" in inputXarray.keys():
        inputXarray["HYDROSTATIC_HULL"] = xr.DataArray(data = inputXarray["HYDROSTATIC_HULL"].values,
                                                        coords = {  "Body"  : inputXarray.Body ,
                                                                    "Mode_i": inputXarray.Mode_i ,
                                                                    "Mode_j": inputXarray.Mode_j ,})
        
    inputXarray = inputXarray.rename(old_names_to_new_names)

    inputXarray = inputXarray.assign_coords({"xyz"    :["x","y","z"]})
    ref_wave = inputXarray.ref_wave
    inputXarray["ref_wave"] = xr.DataArray(data = ref_wave.values, coords = {"xy"    :["x","y"]})
    
    inputXarray["cob"] = inputXarray.ref_point

    for key in list(inputXarray.attrs.keys()):
        if key in old_attrs_to_new_attrs:
            inputXarray.attrs[old_attrs_to_new_attrs[key]] = inputXarray.attrs.pop(key)

    # Add information missing from hydrostar:
    for item, val in default_values.items():
        if item not in inputXarray.attrs:
            inputXarray.attrs[item] = val
    
    inputXarray["base_flow_stiffness"] = xr.DataArray(data = np.zeros(( inputXarray.attrs["nb_body"] ,6,6), dtype = float),
                                                    coords = [ inputXarray["body"] , inputXarray["mode_i"] , inputXarray["mode_j"] ] )
    
    if "hydrostatic_hull" in inputXarray.data_vars : 
        inputXarray["hydrostatic_hull"] *= inputXarray.rho * inputXarray.g
    

    return inputXarray