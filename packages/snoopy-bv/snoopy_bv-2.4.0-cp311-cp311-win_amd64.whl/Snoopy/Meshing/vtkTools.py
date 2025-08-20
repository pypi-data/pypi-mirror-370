import numpy as np
import h5py
import os

from Snoopy import logger


def get_vtk_reader( filename ):
    """return appropriate reader, based on extension, with filename already set.
    """
    import vtk
    
    ext = os.path.splitext(filename)[-1]
    
    if ext == ".vtk" : 
        reader = vtk.vtkDataSetReader()
    elif ext == ".vtu" : 
        reader = vtk.vtkXMLUnstructuredGridReader()
    elif ext == ".vtk" : 
        reader = vtk.vtkDataSetReader()
    elif ext in [".hdf" , ".h5"] :
        reader = vtk.vtkHDFReader()
    else: 
        raise("Extention not known {ext:}")
    reader.SetFileName(filename)
    return reader
    


def integrate_pressure( vtk_alg, field_name, ref_point ):
    """Integrate pressure with cells normals, using VTK.

    Parameters
    ----------
    vtk_alg : vtkAlgorithm 
        vtkAlgorithm generating a polydata.
    field_name : str
        Name of the pressure field.        
    ref_point : np.ndarray
        reference point for the torsor.
    

    Returns
    -------
    res : np.ndarray
        Forces torsor. (6 DOF)
        
    Example
    -------
    >>> reader =  vtk.vtkXMLUnstructuredGridReader()
    >>> reader.SetFileName("truc.vtk")
    >>> poly_a = vtk.vtkGeometryFilter()
    >>> poly_a.SetInputConnection(reader.GetOutputPort() )
    >>> inc_re_vtk = integrate_pressure( poly_a ,"pressure", ref_point = np.array([ 0., 0., 0.]) )
    array([ 0.00653133, -0.16187249, -0.29277204,  0.01027798, -0.01862387, -0.02936297])
    
    """
    import vtk
    from vtk.util import numpy_support
    
    # Compute normals
    n = vtk.vtkPolyDataNormals()
    n.SetInputConnection(vtk_alg.GetOutputPort())
    n.SetComputeCellNormals(True)

    # Add cell center
    cc = vtk.vtkAppendLocationAttributes()
    cc.SetInputConnection( n.GetOutputPort() )

    # Forces
    calc = vtk.vtkArrayCalculator()
    calc.SetInputConnection( cc.GetOutputPort() )
    calc.SetAttributeTypeToCellData()
    calc.AddVectorVariable( "Normals", "Normals")
        
    calc.AddScalarVariable("pressure" , field_name) # using field_name as variable name could cause issue in case of special character in field_name.
    calc.SetFunction( "pressure * Normals")
    calc.SetResultArrayName("Integration")
    
    vi = vtk.vtkIntegrateAttributes()
    vi.SetInputConnection( calc.GetOutputPort() )
    vi.Update()
    
    forces = numpy_support.vtk_to_numpy( vi.GetOutputDataObject(0).GetCellData().GetArray("Integration") )[0]
    
    # Moments
    calc.AddVectorVariable( "CellCenters" , "CellCenters")
    calc.SetFunction( f"pressure * cross(Normals, ( {ref_point[0]:} * iHat  + {ref_point[1]:} * jHat + {ref_point[2]:} * kHat) - CellCenters )")
    calc.SetResultArrayName("Integration")
    
    vi = vtk.vtkIntegrateAttributes()
    vi.SetInputConnection( calc.GetOutputPort() )
    vi.Update()

    moments = numpy_support.vtk_to_numpy(  vi.GetOutputDataObject(0).GetCellData().GetArray("Integration")  )[0]
    return np.concatenate( [forces , moments] )



#---------------------------------------------------------------------#
class ErrorObserver:
    def __init__(self, raise_exception = False):
        """To catch c++ vtk error in python and raise an exception.
        
        Example
        -------
        >>> import vtk
        >>> reader = vtk.vtkXMLUnstructuredGridReader()
        >>> reader.SetFileName( "fece" )
        >>> e = ErrorObserver()
        >>> reader.AddObserver( "ErrorEvent" , e)
        >>> reader.GetExecutive().AddObserver('ErrorEvent', e)
        >>> reader.Update()
        >>> print( e.error_catched )
        True
        >>> 
        
        Note
        ----
        The exception is not well capture within an try/except.
        """
        self.CallDataType = 'string0'
        self._error_catched = False
        self._raise_exception = raise_exception

    def __call__(self, obj, event, message):
        self._error_catched = True
        self._message = message
        if self._raise_exception : 
            raise(Exception(f"{event:}\n{message:}") )
        
    @property
    def error_catched(self):
        return self._error_catched

def write_vtkUnstructuredGrid_vtkhdf(ugrid, filename, mode="w"):
    """Write to HDF vtk format

    Parameters
    ----------
    ugrid : vtk.vtkUnstructuredGrid
        Input data in format vtk.vtkUnstructuredGrid 
    filename : str
        Filename.
    """
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    
    if not isinstance(ugrid, vtk.vtkUnstructuredGrid):
        raise TypeError(f"Expect in put as vtkUnstructuredGrid, {type(ugrid)} received!")

    logger.debug(f"Going to write vtkUnstructeredGrid to : {filename}")

    with  h5py.File( filename , mode=mode) as nf : 
        dset = nf.create_group( "VTKHDF" )
        
        dset.attrs.create("Type", np.bytes_("UnstructuredGrid"))
        dset.attrs["Version"] = [1, 0]

        cells = ugrid.GetCells()
        
        dset.create_dataset("NumberOfConnectivityIds", 
                            data  = np.asarray([cells.GetNumberOfConnectivityIds()]), 
                            dtype = np.int64,
                            compression="gzip", compression_opts = 9, shuffle = True)
        
        
        dset.create_dataset("NumberOfPoints", 
                            data  = np.asarray([ugrid.GetNumberOfPoints()]), 
                            dtype = np.int64,
                            compression="gzip", compression_opts = 9, shuffle = True)
        
        dset.create_dataset("NumberOfCells", 
                            data  = np.asarray([cells.GetNumberOfCells()]), 
                            dtype = np.int64, 
                            compression="gzip", compression_opts = 9, shuffle = True)
        
        points = vtk_to_numpy(ugrid.GetPoints().GetData())
        dset.create_dataset("Points", data  = points, chunks =  points.shape,
        compression="gzip", compression_opts = 9, shuffle = True)
        
        connectivity = vtk_to_numpy(cells.GetConnectivityArray())
        dset.create_dataset("Connectivity", data  = connectivity, chunks =  connectivity.shape, 
        compression="gzip", compression_opts = 9, shuffle = True)
        
        offsets = vtk_to_numpy(cells.GetOffsetsArray())
        dset.create_dataset("Offsets", data  =  offsets,chunks =   offsets.shape,
        compression="gzip", compression_opts = 9, shuffle = True)
        
        celltypes = vtk_to_numpy(ugrid.GetCellTypesArray())
        dset.create_dataset("Types",   data  = celltypes ,  chunks =   celltypes.shape,
        compression="gzip", compression_opts = 9, shuffle = True)
        
        all_attribute_types = ["PointData", "CellData", "FieldData"]
        
        for attribute_type_enum,attribute_type_name in enumerate(all_attribute_types):
            field_data = ugrid.GetAttributesAsFieldData(attribute_type_enum)
            nb_array =  field_data.GetNumberOfArrays() 
            if nb_array > 0:

                field_data_group = dset.create_group(attribute_type_name)
                # only for POINT and CELL attributes
                if attribute_type_enum < 2:
                    for i in range(nb_array):
                        array = field_data.GetArray(i)
                        if array:
                            anp = vtk_to_numpy(array)
                            field_data_group.create_dataset(array.GetName(), data = anp, chunks = anp.shape, 
                            compression="gzip", compression_opts = 9, shuffle = True)
                            
                    #for field_type in ["Scalars", "Vectors", "Normals", "Tensors", "TCoords"]:
                    #    array = getattr(field_data, "Get{}".format(field_type))()
                    #    print("Get:", field_type, array)
                    #    if array:
                    #        field_data_group.attrs.create(field_type, np.string_(array.GetName()))
            

            # FIELD attribute
            if attribute_type_enum == 2:
                for i in range(nb_array):
                    array = field_data.GetArray(i)
                    if not array:
                        array = field_data.GetAbstractArray(i)
                        if array.GetClassName() == "vtkStringArray":
                            dtype = h5py.special_dtype(vlen=bytes)
                            dset = field_data_group.create_dataset(
                                array.GetName(),
                                (array.GetNumberOfValues(),), dtype, 
                                compression="gzip", compression_opts = 9, shuffle = True)
                            
                            for index in range(array.GetNumberOfValues()):
                                dset[index] = array.GetValue(index)
                        else:
                            # don't know how to handle this yet. Just skip it.
                            print("Error: Don't know how to write "
                                  "an array of type {}".format(
                                      array.GetClassName()))
                    else:
                        anp = vtk_to_numpy(array)
                        dset = field_data_group.create_dataset(
                            array.GetName(), anp.shape, anp.dtype, chunks = anp.shape, 
                            compression="gzip", compression_opts = 9, shuffle = True)
                        dset[0:] = anp

