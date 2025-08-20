import matplotlib


def vtkLookupTable_from_cmap(cmap , ncolors = 256):
    """Generate vtk LUT from matplotlib colormap name
    
    Parameters
    ----------
    cmap : str
        Color map name (e.g. 'cividis')
    ncolors : int
        Number of colors
        
    Returns
    -------
    vtk.vtkLookupTable
    
       The corresponding vtk look-up-table
    """    
    
    import vtk
    
    lut = vtk.vtkLookupTable()
    cmap_ = matplotlib.colormaps[cmap]
    lut.SetNumberOfColors(ncolors)
    for i in range(ncolors):
        lut.SetTableValue(i, *cmap_(i/ncolors))
    lut.Build()
    
    
    return lut