import numpy as np

def write_matrix(mat, threshold = None):
    """Utility function to write matrix.

    Parameters
    ----------
    mat : ndarray
        matrix to be write to text

    Returns
    -------
    str
        write matrix to text
    """
    
    mat = np.array(mat)
    if threshold is not None :
        mat[np.where(np.abs(mat)<threshold) ] = 0.0
    nb_line,nb_collum = mat.shape
    out = ""
    for iline in range(nb_line):
        out += " ".join(["{:.6e}".format(mat[iline,icol]).rjust(14) 
                            for icol in range(nb_collum)]) +"\n"
    return out
    

import xarray as xa
def write_xarray(xa_input,output_filename):
    """Native netCDF doesn't support writing complex value.
    This function is a temporary(?) fix.

    Parameters
    ----------
    xa_input : xarray.DataArray or xarray.Dataset
        Input
    """
    if isinstance(xa_input, xa.DataArray):
        xa_dataset = xa.Dataset(data_vars=  {"xarray": xa_input})
    elif isinstance(xa_input, xa.Dataset):
        xa_dataset = xa_input
    else:
        raise TypeError(f"Input must be xarray.Dataset or xarray.DataArray. {type(xa_input)} received")
    xa_output = xa.Dataset()
    for key in xa_dataset.keys():
        
        xa_DataArray = xa_dataset[key]
        if np.iscomplexobj(xa_DataArray):
            xa_output[key+"_re"] = xa_DataArray.real
            xa_output[key+"_im"] = xa_DataArray.imag
        else:
            xa_output[key] = xa_DataArray


    xa_output.attrs = xa_dataset.attrs


    xa_output.to_netcdf(output_filename)
    