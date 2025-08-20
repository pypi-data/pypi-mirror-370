import os
import numpy as np
import xarray as xr
import pandas as pd
from Snoopy.Mechanics import matrans3, vectran3, dbmatrans
from Snoopy import Spectral as sp
from Snoopy import logger
from Snoopy.Reader.input_mcn_parser import parse_input_mcn
from Snoopy.Spectral.qtf import *
from Snoopy import Meshing as msh
from Snoopy.Meshing.mesh_io import read_hslec_h5


def _get_hydro_data():

    # This function reads the file hydro_data.csv which gathers all the metadata for each quantity of the *.h5 files.

    # Convension :
    # NAME : Name of the quantity.
    # TYPE : Type of the quantity in the xarray (variable, coordinate or attribut).
    # COMPLEX : 0 = real / 1 = complex.
    # TRANS : Method to use for changing the computation point (load_vector, motion_vector or matrix) with matrans.py.
    # MULTIBODY_INTERACTION : 0 = quantity without multibody interaction / 1 = with multibody interaction (useless ?).
    # FREQUENCY_HEADING : 0 = quantity which do not depend on the wave frequency and the heading / 1 = with dependency (ueseless ?).
    # BUILD_INFO : ? (useless ?)
    # MCN_COEF : 0 : not present in MCN_COEF / 1 : optional / 2 : mandatory.
    # RDF_COEF : 0 : not present in RDF_COEF / 1 : optional / 2 : mandatory.
    # MCN_INPUT : 0 : not present in MCN_INPUT / 1 : optional / 2 : mandatory.
    # QTF_COEF : 0 : not present in QTF_COEF / 1 : optional / 2 : mandatory.
    # DEFAULT_DIMS : Dimensions of the quantity (body_i, body_j, xyz, frequency, heading, mode_i, mode_j, etc.).
    # DESCRIPTION : Description of the quantity.

    content_df = pd.read_csv( f"{os.path.dirname(os.path.abspath(__file__)):}/hydro_data.csv" , index_col = 0  )
    content_df["TYPE"] = pd.Categorical(content_df["TYPE"], ["attribute", "coordinate", "variable"])
    return content_df.sort_values("TYPE")


@xr.register_dataset_accessor("hydro")
class HydroCoef():
    """Class to handle the hydrodynamic coefficients. 
    
    We store everything in xarray Dataset, with the following addition :
        - mandatory convention (not an convention anymore...)
        - Manipulation specific to the fact that we deal with hydrodynamic coefficient

    Note
    ----
    All quantities are expressed at the "ref_point". 
    """
    
    KIND = None
    

    
    # The dataframe that contains the "convention" of the different field names and shape
    content_df = _get_hydro_data()

    def __init__(self, data):
        self._data = data


    @staticmethod
    def coordinate_helpers( nb_body = 1):
        def_coords = { "mode_i" : np.arange(1,7) ,
                       "mode_j" : np.arange(1,7) ,
                       "mode" : np.arange(1,7) ,
                       "body" : np.arange(1,nb_body+1),
                       "body_i" : np.arange(1,nb_body+1),
                       "body_j" : np.arange(1,nb_body+1),
                       "xy":  ["x" , "y"] ,
                       "xyz": ["x" , "y", "z"] ,
                     }
        return def_coords

    def get_transposed(self):
        ds = self._data
        for var in ds.data_vars:
            if var in self.content_df.index.values:
                ds[var] = ds[var].transpose(  *TransDims(ds[var].dims).ordered_dims )
        return ds
    

    @property
    def nbbody(self):
        return self._data.attrs["nb_body"]
    
    
    @property
    def encounter_frequency(self):
        """Encounter frequency is a derived input that can be computed thank to dispersion relation.
        
        Return
        ------
        np.ndarray
           we[ nb_heading, nb_frequency] 
        """
        data = self._data
        if "frequency" in data and "heading" in data and "depth" in data.attrs:
            frequency = data.frequency
            heading   = data.heading
            depth     = data.attrs.get("depth",0.0)
            nb_head   = len(heading)
            nb_freq   = len(frequency)
            encounter_frequency = np.zeros((nb_head,nb_freq),dtype='float64')
            
            for i_freq,freq in enumerate(frequency):
                for i_head,head in enumerate(heading):
                    encounter_frequency[i_head,i_freq] = \
                            sp.w2we( freq , head*np.pi/180, self._data.attrs["speed"], depth =  depth)
            
            return xr.DataArray(data = encounter_frequency,
                                coords = [self._data.heading,self._data.frequency])
        else:
            raise RuntimeError(f"Object {self} doesn't have enough information to compute encounter frequency")

    

    @property
    def wave_length(self):
        data = self._data
        if "frequency" in data and "depth" in data:
            wl = sp.w2l(data["frequency"], depth = data["depth"]) 
            return xr.DataArray(data = wl, coords = [self._data.frequency])
        
        raise RuntimeError(f"Object {self} doesn't have enough information to compute wave length")


    def get_at_ref_point(self , ref_point) : 
        """Return the dataset expressed at another reference point.
        
        The original dataset is not modified
        
        Parameters
        ----------
        ref_point : np.ndarray(3)
            The new reference point.

        Returns
        -------
        Dataset
            The moved dataset
        """

        # Old and new reference points.
        n_bodies = self._data.nb_body
        old_ref_point = self._data.ref_point.values
        new_ref_point = np.asarray(ref_point)
        if new_ref_point.shape[0] == 3 and n_bodies == 1:
            new_ref_point = [new_ref_point]  # To match the former format of new_ref_point with a single body.

        if np.allclose(old_ref_point, new_ref_point):
            # The two reference points are identical.
            return self._data
        else:
            ds = self._data.copy(True)  # To be sure that original dataset is not modified.
            for i_bd in range(0, n_bodies):
                logger.debug(f"Changing ref_point of body {i_bd + 1} from {old_ref_point[i_bd]} to {new_ref_point[i_bd]}")

            # Amongst the variables which have a method for changing the point of reference (TRANS != Nan)
            for var in self.content_df.query( "TRANS in ['load_vector', 'motion_vector' , 'matrix' ]").index.values:

                # If a variable which has a method for changing the point of reference is present in the dataset.
                if var in ds.data_vars:

                    # Method for changing the point of reference (load_vector, motion_vector or matrix).
                    kind = self.content_df.loc[var, "TRANS"]
                    isMotion = "motion" in kind
                    logger.debug(f"            -> {var:} - isMotion: {isMotion:}")

                    # Object for handling the dimensions of the coordinates of the variable.
                    trans_dims = TransDims(self._data[var].dims)

                    # Stack all dimensions except mode / mode_i / mode_j.
                    # All dimensions other than mode / mode_i / mode_j are put together to obtain :
                    # - for a vector : [mode, list of other dimensions]
                    # - for a matrix : [mode_1, mode_2, list of other dimensions]
                    # The other dimensions may be : frequency, heading, body, etc.
                    if len(trans_dims.other_dims) > 0:  # trans_dims.other_dims = [] for the infinite-frequency added mass, etc.
                        da = ds[var].stack(all_but_mode=trans_dims.other_dims)
                    else:
                        da = ds[var]

                    # Change of point.
                    if kind == "matrix":
                        if trans_dims.last_dims == ["body_i", "body_j", "mode_i", "mode_j"]:
                            if len(trans_dims.other_dims) > 0:  # trans_dims.other_dims = [] for the infinite-frequency added mass, etc.
                                # Loop over all dimensions except body_i, body_j, mode_i and mode_j.
                                for i in range(da.shape[-1]):
                                    # Change of point for a matrix of size nBodies x nBodies x 6 x 6.
                                    da.values[:, :, :, :, i] = dbmatrans(da.values[:, :, :, :, i], origin=old_ref_point,
                                                                         destination=new_ref_point)
                            else:
                                # Change of point for a matrix of size nBodies x nBodies x 6 x 6.
                                da.values[:, :, :, :] = dbmatrans(da.values[:, :, :, :], origin=old_ref_point,
                                                                  destination=new_ref_point)
                        if trans_dims.last_dims == ["body", "mode_i", "mode_j"]:
                            # Loop over all bodies.
                            for i_bd in range(n_bodies):
                                if len(trans_dims.other_dims) > 0:  # trans_dims.other_dims = [] for the mass matrix, etc.
                                    # Loop over all dimensions except body, mode_i, mode_j.
                                    for i in range(da.shape[-1]):
                                        # Change of point for a matrix of size nBodies x 6 x 6.
                                        da.values[i_bd, :, :, i] = matrans3(da.values[i_bd, :, :, i],
                                                                            origin=old_ref_point[i_bd],
                                                                            destination=new_ref_point[i_bd])
                                else:
                                    # Change of point for a matrix of size nBodies x 6 x 6.
                                    da.values[i_bd, :, :] = matrans3(da.values[i_bd, :, :],
                                                                     origin=old_ref_point[i_bd],
                                                                     destination=new_ref_point[i_bd])
                    elif "vector" in kind:
                        # Loop over all bodies.
                        for i_bd in range(n_bodies):
                            if len(trans_dims.other_dims) > 0:  # In case trans_dims.other_dims = [].
                                # Loop over all dimensions except body and mode.
                                # trans_dims.last_dims = [body, mode].
                                for i in range(da.shape[-1]):
                                    # Change of point for a vector of size 6 x 1.
                                    if var == "qtf":  # WARNING: The order is not the same for QTF.
                                        da.values[:, i_bd, i] = vectran3(da.values[:, i_bd, i],
                                                                         origin=old_ref_point[i_bd],
                                                                         destination=new_ref_point[i_bd],
                                                                         isMotion=isMotion)
                                    else:
                                        da.values[i_bd, :, i] = vectran3(da.values[i_bd, :, i],
                                                                         origin=old_ref_point[i_bd],
                                                                         destination=new_ref_point[i_bd],
                                                                         isMotion=isMotion)
                            else:
                                # Change of point for a vector of size 6 x 1.
                                da.values[i_bd, :] = vectran3(da.values[i_bd, :], origin=old_ref_point[i_bd],
                                                              destination=new_ref_point[i_bd], isMotion=isMotion)

                    # Unstack the dimensions.
                    if len(trans_dims.other_dims) > 0:  # trans_dims.other_dims = [] for the infinite-frequency added mass, etc.
                        ds[var] = da.unstack().transpose(*trans_dims.original_dims)

                    else:
                        ds[var] = da

            # Update the reference point.
            ds["ref_point"].values = new_ref_point

            return ds


    def get_at_ref_wave(self, ref_wave):
        # TODO: implement phase shift when set to new wave reference point.
        raise NotImplementedError("Setting a new value for ref_wave is not yet implemented!")

        
    def check( self, kind = None ):
        """Check if necessary content is present, and warn for content which is not handled.

        Returns
        -------
        bool
            Return False if content is missing, True if everything is there
        """
        if kind is None:
            kind = self.KIND
        
        if kind is not None:
            m = self.missing_content(kind = kind)
            n_miss = np.sum( [len(v) for k , v in m.items()] )
            if n_miss > 0:
                logger.error( f"Missing content :\n{m:}" )
                return False

        nh = self.not_handled_content()
        if len(nh) > 0 : 
            logger.warning(f"Not handled content :\n{nh:}")
            
        return True
                
        
    def missing_content(self, kind ):
        """Check that the dataset contains the necessary information.
        
        Returns
        -------
        dict
            Missing attributes and variables
        """
        missing = {"attrs" : [] , "var" : []}
        for k in self.content_df.query( f"TYPE=='attr' and {kind:}==2" ).index.values:
            if k not in self._data.attrs.keys() :
                missing["attrs"].append( k )
                
        for k in self.content_df.query( f"TYPE=='variable' and {kind:}==2" ).index.values:
            if k not in self._data.data_vars.keys() : 
                missing["var"].append( k )
        return missing
    
    
    def not_handled_content(self):
        """Return list of dataarray which are not handled. 
        
        Data not handled will not be process by, for instance `get_at_ref_point()`

        Returns
        -------
        list
            Not handled variables
        """

        return [k for k in self._data.data_vars if k not in self.content_df.index]

    

    def convert_to_complex(self, drop = True):
        """Convert _re and _im to complex.
        """
        ds = self._data.copy()
        for a in self._data.data_vars.keys() :
            if a[-3:] == "_re" :
                logger.debug(f"Converting {a:} and _im to complex")
                ds[a[:-3]] = self._data[ a ] + 1j * self._data[ a.replace("_re" , "_im") ]
                if drop : 
                    ds = ds.drop_vars( [a, a.replace("_re" , "_im") ] )
        return ds

    def convert_to_real(self, drop = True):
        """Convert complex to _re and _im.
        """
        ds = self._data.copy()
        for a in ds.data_vars.keys() :
            #if a in self.content_df.query("COMPLEX == True").index.values:
            data_var = ds[a]
            if np.iscomplexobj(data_var):
                logger.debug(f"Converting {a:} and _im to real and imag")
                ds[a + "_re" ] = data_var.real
                ds[a + "_im" ] = data_var.imag
                if drop : 
                    ds = ds.drop_vars( [a] )
        return ds
    
    

    @classmethod
    def read(cls,filename, format_version = None, **kwargs):
        """Read standard format.

        Parameters
        ----------
        filename : str
            Path to hdf file
            
        **kwargs : any
            Keyword argument passed to xarray.open_dataset.  (including "engine")

        Returns
        -------
        xarray
            Output
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Can't find data file: {filename}")        

        with xr.open_dataset(filename, lock = False, **kwargs) as f:
            # .compute force the actual loading of the data and return it (not deferred). The filename is thus available even of ds is further modified.
            ds = f.compute(deep = True)

        if format_version == "auto":
            from Snoopy.Mechanics.hydro_coef_io import find_format_version, hydro_coef_from_hstar_v82
            format_version = find_format_version(ds)

        # Compatibility depending on version. 
        if format_version == "hydrostar_v8.2" : 
            ds = hydro_coef_from_hstar_v82( ds )

        ds = ds.hydro.convert_to_complex()
        ds = ds.hydro.get_transposed()
        assert ds.hydro.check(kind = cls.KIND)
        return ds


    def write(self,filename, **kwargs):
        output = self.convert_to_real()
        output.to_netcdf(filename, **kwargs)

    def convert_hydrostar_v8(self):
        from Snoopy.Mechanics.hydro_coef_io import hydro_coef_from_hstar_v82
        ds = hydro_coef_from_hstar_v82( self._data )
        ds = ds.hydro.convert_to_complex()
        ds = ds.hydro.get_transposed()
        return ds
    


    
    @classmethod
    def Build(cls, wave_length = None,**kwargs):
        """Construct the dataset with simple inputs (numpy).

        Parameters
        ----------
        nb_body : int
            number of body

        cog : numpy.array or list or xarray.DataArray
            Center of gravity, dimension : [nbBody,3]

        cob : numpy.array or list or xarray.DataArray
            Center of gravity, dimension : [nbBody,3]
    
        ref_point : numpy.array or list or xarray.DataArray
            Reference point, dimension : [nbBody,3]
            Optional, default value: cog
    
        ref_wave : numpy.array or list or xarray.DataArray
            Origin of wave phase in surface, dimension : [2,],
            Optional, default = [0,(ref_point[0],ref_point[1])]
    
        heading    : numpy.array or list or xarray.DataArray
            ship heading, in degree, dimension [nb_head,]
    
        frequency  : numpy.array or list or xarray.DataArray
            frequency of problem, dimension [nb_freq,]

        speed   : float
            advancing speed [m/s]
    
        depth : float
            depth [m].
            Optional, default = 0.
            Attention, Depth = 0. mean Depth = infitity
    
        hydrostatic : numpy.array or list or xarray.DataArray
            hydrostatic stiffness total, dimension ["body","mode_i","mode_j"]
            hydrostatic = hydrostatic_hull + hydrostatic_grav
    
        base_flow_stiffness : numpy.array or list or xarray.DataArray
            stiffness caused by steady flow, dimension ["body","mode_i","mode_j"]
            Optional, default: numpy.zeros((nb_body,nb_mode,nb_mode))
    
        excitation_load : numpy.array or list or xarray.DataArray
            excitation force, dimension
            ["body","mode","heading","frequency"]
    
        added_mass : numpy.array or list or xarray.DataArray
            added mass in radiation problem, dimension
            ["body_i","body_j","mode_i","mode_j","heading","frequency"]
    
        wave_damping : numpy.array or list or xarray.DataArray
            wave damping in radiation problem, dimension
            ["body_i","body_j","mode_i","mode_j","heading","frequency"]
    
        Returns
        -------
        xr.Dataset
            The data organised in a xarray.Dataset with the coordinates set.
        """
        if "nb_body" not in kwargs:
            raise ValueError("Number of body 'nb_body' must be present")
        for key, val in cls.coordinate_helpers(kwargs["nb_body"]).items():
            kwargs.setdefault(key,val)

        coords = {}
        attrs = {}
        da_list = {}
        content = HydroCoef.content_df
        for row_name, row in content.iterrows():

            data_type = row["TYPE"]
            data_value = kwargs.pop(row_name, None)

            if data_value is not None:
                if data_type == "coordinate":    
                    coords[row_name] = data_value
                elif data_type == "attribute":
                    attrs[row_name] = data_value
                elif data_type == "variable":
                    dims = row["DEFAULT_DIMS"].split()
                    coords_data = [(d, coords[d]) for d in dims]
                    da_list[row_name] = xr.DataArray(data=data_value ,
                                                     coords=coords_data)

        for var, data in kwargs.items() :
            logger.info(f"{var:} is not handled but stored as an attribute")
            attrs[var] = data

        output_xa = xr.Dataset( da_list, attrs = attrs )
        assert output_xa.hydro.check(kind = cls.KIND)

        return output_xa
    

    
    def export_rao_6_dof(self, kind = "motion"): 
        """Return list of RAO objects (list length = number of bodies).

        Parameters
        ----------
        kind : str, optional
            RAO to be read, "motion" or "excitation". The default is "motion".
        
        Returns
        -------
        raoList : list
            list of sp.Rao (one RAO with 6ddl for each body)
        """
        
        rao_list = []
        
        for ibody in range(self.nbbody) :
            data = self._data.isel(body = ibody)
            cvalues = data[kind].transpose("heading" , "frequency" , "mode").values

            rao_list.append( sp.Rao( b = np.deg2rad( data.heading.values) ,
                           w = self._data.frequency.values,
                           cvalue = cvalues,
                           modes = [1,2,3,4,5,6],
                           refPoint = data.ref_point.values,
                           waveRefPoint = data["ref_wave"].values,
                           depth = data.attrs["depth"],
                           forwardSpeed = data.attrs["speed"]
                      ))
            
        return rao_list 

        
        



class RdfCoef(HydroCoef):
    """Specialization of HydroCoef for what is specific to the geometry only.
    
    No mass data. Only hydrodynamic and hydrostatic.
    """
    
    KIND = "RDF_COEF"

        


class McnCoef(HydroCoef):
    """Specialization of HydroCoef that contains RdfCoef + motion solver results
    
    """
    
    KIND = "MCN_COEF"
    
    


@xr.register_dataset_accessor("mcn")
class McnInput(HydroCoef):
    """Specialization of HydroCoef that contains only mechanical properties.

    """
    
    KIND = "MCN_INPUT"
    
    @property
    def mass(self):
        return self._data.mass_matrix.sel( mode_i = 1 , mode_j = 1).values
    

    @classmethod
    def read_mcn(cls,inputFile):
        """Read an input mcn file and produce a xr.Dataset

        Parameters
        ----------
        inputFile : str
            Path to input.mcn
        Returns
        -------
        Dataset
            THe mechanical properties stored in xr.Dataset.
        """
        return cls.Build( **parse_input_mcn(inputFile) )



    @classmethod
    def read_json(cls, inputdata):
        """Extract informations that needed to create mcn_input from HydroStarV format. 
        
        Parameters
        ----------
            inputFile : str
                path to .json file
                
        Returns
        -------
        Dataset
            THe mechanical properties stored in xr.Dataset.
        """
        raise(NotImplementedError)


    @classmethod
    def Build(cls, **kwargs):
        gyration_radius = kwargs.pop("gyration_radius", None)

        mass = kwargs.pop("mass", None)
        mass_matrix = kwargs.get("mass_matrix", None)
        
        if mass_matrix is None:
            assert mass is not None, 'If mass_matrix is not present, mass must be given.'
            assert gyration_radius is not None,  'If mass_matrix is not present, mass must be given.'
            nb_body = len(mass)

            mass_matrix = np.zeros((nb_body, 6, 6), dtype='float64')
            
            for ibody in range(nb_body):
                gyration_radius = np.asarray(gyration_radius)
                mass_matrix[ibody, :3, :3] = mass[ibody] * np.eye(3)
                mass_matrix[ibody, 3:, 3:] = mass[ibody] * np.diag(gyration_radius[ibody, :3]**2)
                mass_matrix[ibody, 3, 4:] = (mass[ibody] * gyration_radius[ibody, 3:5]
                                             * np.abs(gyration_radius[ibody, 3:5]))
                mass_matrix[ibody, 4, 5] = (mass[ibody] * gyration_radius[ibody, 5]
                                            * np.abs(gyration_radius[ibody, 5]))
                # Symmetrization.
                mass_matrix[ibody, 4:, 3] = mass_matrix[ibody, 3, 4:]
                mass_matrix[ibody, 5, 4] = mass_matrix[ibody, 4, 5]
            kwargs["mass_matrix"] = mass_matrix
        else:
            if len(mass_matrix.shape) == 2:
                mass_matrix = mass_matrix[np.newaxis, :, :]
                nb_body = 1
            elif len(mass_matrix.shape) == 3:
                nb_body = mass_matrix.shape[0]
            else:
                raise ValueError(f"Invalid shape of mass matrix: {mass_matrix.shape}")
        if "ref_point" not in kwargs:
            kwargs["ref_point"] = kwargs["cog"]
            
        user_k = kwargs.get("user_stiffness_matrix", None)
        if user_k is None:
            kwargs["user_stiffness_matrix"] = np.zeros((nb_body, nb_body, 6, 6), dtype=float)
        ds = super().Build( **kwargs )
        return ds


class QTFCoef(HydroCoef):
    """Specialization of HydroCoef that contains QTF results."""

    KIND = "QTF_COEF"

class TransDims():
    """Handle dimension ordering to be compatible with matrans routines.
    """
    
    default_order = [ ["body_i", "body_j" , "heading", "frequency", "mode_i", "mode_j" ],  # Ex: added mass, damping.
                      ["body", "mode_i", "mode_j" ],  # Ex: hydrostatic matrix, mass matrix.
                      ["body", "heading", "frequency", "mode"],  # Ex: excitation loads, motions.
                      ["body_i", "body_j" , "mode_i", "mode_j" ],  # Ex: infinite-frequency added mass, user stiffness matrix.
                      ["body", "xyz" ], 
                      [ "xy" ],
                      ["body"],
                      ["heading", "frequency"],
                      ["body", "heading", "frequency_qtf", "diff_frequency", "mode"]  # Ex: QTF.
                     ]

    matrans_order = [["body", "mode"],
                     ["body", "mode_i", "mode_j"],
                     ["body_i", "body_j", "mode_i", "mode_j"],
                     ]
    
    @staticmethod
    def _order(dims, dims_order, check_all ):
        """This method orders the dimensions wrt dimsn_order."""

        # Copy of dims into a list.
        ordered_dims = [a for a in dims]

        for i, last in enumerate(dims_order):

            # If all variables of dims_order are present in the dimensions, the ordering process starts.
            if np.all([a in dims for a in last]):
                # All variables of dims_order are removed.
                for a in last:
                    ordered_dims.remove(a)

                # All variables of dims_order are added at the end.
                ordered_dims.extend(last)
                return  ordered_dims, last
        else:
            # If the variables of dims_orders are not present, return the dimensions unchanged.
            if check_all:
                raise(Exception(f"Do not know how to order {dims:}"))
            else:
                return ordered_dims, []

    def __init__(self, dimension):

        # Original dimensions of a variable.
        self.original_dims = dimension

        # Ordering the dimensions for matrans functions using matrans_order.
        self.matrans_dims, self.last_dims = self._order(dimension, self.matrans_order, check_all=False)

        # Dimensions which are not necessary for matrans functions.
        self.other_dims = self.matrans_dims[:-len(self.last_dims)]

    @property
    def ordered_dims(self):
        a, _ = self._order( self.original_dims, self.default_order, check_all = True )
        return a
