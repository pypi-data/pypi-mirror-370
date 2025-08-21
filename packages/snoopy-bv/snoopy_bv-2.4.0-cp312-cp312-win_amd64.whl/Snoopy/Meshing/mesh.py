import os
import logging
import numpy as np
import pandas as pd
from Snoopy import Geometry as geo
from Snoopy import logger
import _Meshing


class Mesh(_Meshing.Mesh):
    @property
    def nbpanels(self):
        return len(self.quads) + len(self.tris)

    @property
    def nbtris(self):
        return len(self.tris)

    @property
    def nbquads(self):
        return len(self.quads)

    @property
    def nbnodes(self):
        return len(self.nodes)


    @property
    def hasPanelData(self):
        return self.getPanelsData().shape[1] > 0

    def getDataRange(self) :
        if self.hasPanelData:
            return np.min(self.getPanelsData()), np.max(self.getPanelsData())
        else :
            return [np.nan , np.nan]


    def getMetaDataDF(self):
        
        return pd.DataFrame(data = 
                    {"frequency"    : self.getDataFreqs(),
                     "heading"      : self.getDataHeads(),
                     "data_name"    : self.getDataNames(),
                     "data_type"    : self.getDataTypes()})



    def appendPanelsData(self , data, dataName, dataType = 0, dataFreq= np.nan, dataHead = np.nan) :
        """Append panel data, inplace
        
        Parameters
        ----------
        data : np.ndarray
            The data to add  (n_panels)
        dataName : str 
            Name of the field
        dataType : TYPE, optional
            DESCRIPTION. The default is 0.
        dataFreq : TYPE, optional
            DESCRIPTION. The default is np.nan.
        dataHead : TYPE, optional
            DESCRIPTION. The default is np.nan.
        """
        
        if len(self.getDataNames()) == 0 :
            self.setPanelsData( panelsData = data[: , np.newaxis] ,
                                dataNames = [dataName],
                                dataTypes = [dataType],
                                dataFreqs = [dataFreq],
                                dataHeads = [dataHead],
                              )
        else : 
            self.setPanelsData( panelsData = np.append(  self.getPanelsData() , data[: , np.newaxis], axis = 1 ) ,
                                dataNames = self.getDataNames() + [dataName],
                                dataTypes = np.append( self.getDataTypes() , dataType),
                                dataFreqs = np.append( self.getDataFreqs() , dataFreq),
                                dataHeads = np.append( self.getDataHeads() , dataHead),
                               )


    def get_radiation_coef(self):
        return self.integrate_fields_xarray("PRESSURE_RAD",
                                            dimension   = ["heading" , "frequency","mode_j"])

    def get_excitation_force(self):
        all_data_names = self.getDataNames()

        # Normal is oriented towards the fluid, hence the the minus sign below. 
        if "PRESSURE_EXC" in  all_data_names:
            force =  -self.integrate_fields_xarray("PRESSURE_EXC", dimension   = ["heading" , "frequency"])
        elif ("PRESSURE_DIF" in all_data_names) and ("PRESSURE_INC" in all_data_names): 
            force = -self.integrate_fields_xarray("PRESSURE_DIF", dimension   = ["heading" , "frequency"]) 
            force -= self.integrate_fields_xarray("PRESSURE_INC", dimension   = ["heading" , "frequency"])
        else:
            raise ValueError("Can't find excitation force stored! Either 'PRESSURE_EXC' "+
                             "or both 'PRESSURE_DIF' and 'PRESSURE_INC' must be present!")
        return force

    def get_froude_krylov_force(self):
        return -self.integrate_fields_xarray("PRESSURE_INC",
                                            dimension   = ["heading" , "frequency"])

    def get_diffraction_force(self):
        return -self.integrate_fields_xarray("PRESSURE_DIF",
                                            dimension   = ["heading" , "frequency"])

    def createFreeSurface(self, a, b, dx, dy, x0=0., y0=0., x_min=None, x_max=None, y_min=None, y_max=None):
        """Create and add a free-surface mesh to the HydroStar Mesh, in place.

        Parameters
        ----------
        a, b : float
            Elliptical radii.
        dx : float
            DESCRIPTION.
        dy : float
            DESCRIPTION.
        x0 : float, optional
            x center. The default is 0..
        y0 : float, optional
            y center. The default is 0..
        method : str, optional
            Method, for now, only "triangulate". The default is "triangulate".
        
        Return
        ------
        Mesh
            The circular free-surface mesh.
        """
        from Snoopy.Meshing.vtk_fs_tools import create_fs_mesh
        waterline = self.extractWaterlineObj()
        fs_mesh = create_fs_mesh(waterline, dx=dx, dy=dy, x0=x0, y0=y0, a=a, b=b, x_min=x_min, x_max=x_max, y_min=y_min,
                                 y_max=y_max)
        
        # Orient downwards
        fs_mesh = self.FromPolydata(fs_mesh)
        fs_mesh.refreshGaussPoints()
        fs_mesh.orientPanels(-1)

        logger.debug(f"Surface mesh with {fs_mesh.getNPanels():} panels created.")
        return fs_mesh

    def integrate_hydrostatic(self):
        """Compute hydrostatic force, assumes free-surface at z=0.

        Returns
        -------
        np.ndarray
            the 6 dof forces.
        """
        z = np.minimum( self.getGaussPoints()[:,2] , 0. )
        return np.sum( z * self.getNormalsAtGaussPoints().T * self.getGaussWiWjdetJ() , axis = 1 )

    def integrate_fields_xarray(self,data_name,
                                dimension   = ["heading" , "frequency","mode_j"],
                                is_real     = False   ):
        """Integrate fields with generalized normal, and return integrated coefficient as xarray.DataArray.
        
        This can be used to get hydrodynamic coefficients (added-mass, wave-damping and excitation forces) from decomposed pressure. The metadata are used to reshape and determine the coordinates of the DataArray.
        
        Parameters
        ----------
        data_name : str
            keep only line which have data_name match this value 

        dimension : list, optional
            Reshape the integrated value in to the given dimension 
            Attention after integration, there will be another dimension added (corresponding to the 6 values of the generalized normals).

        is_real : boolean, optional
            Expect real data or complex data, by default we chose complex. 
            is_real == True: real data
            is_real == False: complex data
            
            If data are considered complex, it is assumed that real and imaginary part are identified by "self.dataTypes", even number being real part and odd number the imaginary part.

        Returns
        -------
        xa_output
            xarray.Dataset
            
        Example
        -------
        
        >>> mesh.getMetaDataDF()
              frequency  heading     data_name  data_type
        0           0.1      0.0  PRESSURE_DIF          1
        1           0.1     45.0  PRESSURE_DIF          1
                ...      ...           ...        ...
        1258        1.8    180.0  PRESSURE_RAD          8
        1259        1.8    180.0  PRESSURE_RAD         10
        
        >>> mesh.integrate_fields_xarray("PRESSURE_RAD", dimension = [ "heading", "frequency", "mode_i" ])
        >>> <xarray.DataArray (heading: 5, frequency: 18, mode_i: 6, mode_j: 6)>
        array([[[[ 1.13425997e+02+1.06272362e-01j,
                  -4.21884749e-15-8.80372164e-17j,
        ...
                   3.20142135e-09-3.85625754e-10j,
                   3.89495936e+07+1.06003669e+07j]]]])
        Coordinates:
          * frequency  (frequency) float64 0.1 0.2 0.3 0.4 0.5 ... 1.4 1.5 1.6 1.7 1.8
          * heading    (heading) float64 0.0 45.0 90.0 135.0 180.0
          * mode_i     (mode_i) int32 0 1 2 3 4 5
          * mode_j     (mode_j) int64 0 1 2 3 4 5
        """

        def _data_type_to_mode_j(xarrayIn):
            final = xarrayIn.assign_coords({"data_type": np.floor(xarrayIn.data_type/2).astype(int)})
            final = final.rename({"data_type":"mode_j"})
            return final

        metadata = self.getMetaDataDF()
        data = self.getPanelsData()
        
        data_filtered = pd.DataFrame.copy(metadata.loc[metadata.data_name == data_name,:])
        index_list = data_filtered.index
        nb_data = len(index_list)

        if (nb_data==0):
            raise ValueError(f"Found no data of type {data_name} stored!")
        if self.nbpanels == 0:
            # Return zero for empty mesh
            if is_real:
                integrated_values = np.zeros((6,nb_data),dtype = float)
            else:
                integrated_values = np.zeros((6,nb_data),dtype = complex)
        else:
            integrated_values = self.integrate_fields(index_list)
        data = pd.DataFrame(integrated_values,
                            index = pd.Index( range(0,6) , name = "mode_i" ), 
                            columns = data_filtered.set_index( ["frequency" , "heading", "data_type"] ).index )
        res = data.transpose().stack().to_xarray()
        data_is_real = (res.data_type.values%2).astype(bool)
        if is_real:
            final = _data_type_to_mode_j(res[:,:,data_is_real,:])
        else:
            data_is_imag = np.logical_not(data_is_real)
            real_part = _data_type_to_mode_j(res[:,:,data_is_real,:])
            
            imag_part = _data_type_to_mode_j(res[:,:,data_is_imag,:])
            final = real_part + 1j*imag_part
            
        for dim in ["heading" , "frequency","mode_j"]:
            if dim not in dimension: # This dimension ('dim') is not present in requested dimension
                # So the data should not depend on dimension 'dim'  => Raise if have more than 1 value
                if len(final[dim]) > 1:
                    raise RuntimeError( f"Requested dimension is independant of '{dim}', "+\
                                        f"but this object stored {len(final[dim])} values  of '{dim}'")
                # Drop the dimension 'dim'
                final = final.isel({dim:0},drop = True)
        # Cosmetic, if there are no "mode_j", rename "mode_i" => "mode"
        if "mode_j" not in dimension:
            final = final.rename({"mode_i":"mode"})
            dimension.append("mode")
        else:
            # Insert mode_i before mode_j
            dimension.insert(dimension.index("mode_j"),"mode_i")
        # Rearrange as requested!
        final = final.transpose(*dimension)
        return final


    def integrate_volume_py(self, direction = 2, nbGP = 1) :
        r"""Compute and return the mesh volume.
        

        Parameters
        ----------
        direction : int, optional
            integration direction (0=>x, 1=>y, 2=>z). The default is 2.
        nbGP : int, optional
            Number of gauss point. The default is 1.

        Returns
        -------
        float
            Volume

        Note
        ----
        If mesh is not explicitely closed by panels, the "cover" has to be at 0.0 in the integration direction.
        """
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        return np.sum(gp[:,direction] * normals[:,direction] * weight)
    
    
    def integrate_waterPlaneArea(self, nbGP = 1):
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        return -np.sum(normals[:,2] * weight)
    
    
    def integrate_stiffness_matrix(self , output_ref_point,
                                   ref_frame = "body-fixed",
                                   hull_stiffness = True, 
                                   buoyancy_stiffness = True, 
                                   rho_g = None):
        r"""Integrate hydrostatic stiffness matrix (pressure part).

        Parameters
        ----------
        output_ref_point : np.ndarray (3).
            Reference point.

        ref_frame : str
            "body-fixed" (translate and rotate with the ship), or "hydro" (only translate with the ship)
            
        hull_stiffness : True, optional
            If true (only relevant for ref_frame == 'hydro'), the hull_stiffness part is included.
            
        buoyancy_stiffness : True, optional
            If true (only relevant for ref_frame == 'hydro'), the buyancy_stiffness part is included.
            
        rho_g : float or None, optional
            Water density * multiplied with gravity, default to None
            
        Returns
        -------
        np.ndarray(6,6)
            Hydrostatic stiffness matrix (without gravity stiffness, which would need mass properties).

        Note
        ----
        When in hydrodynamic reference frame, the buoyancy stiffness cannot be transfered to another reference point (i.e. mcn.matrans3 must not be used).
        
        Formulas (hydrodynamic reference frame)
        ---------------------------------------
        
        Matrix expressed at a reference point R (x_r, y_r, z_r).
        
        .. list-table:: Hull stiffness (in hydrodynamic reference frame)
            :widths: 40 40 40 40 40 40
            :header-rows: 0
        
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - .. math:: \rho g \int\int n_3 dS
              - .. math:: \rho g \int\int (y-y_r) n_3 dS
              - .. math:: \rho g \int\int (x-x_r) n_3 dS
              - 0
            * - 0
              - 0
              - .. math:: \rho g \int\int (y-y_r) n_3 dS
              - .. math:: \rho g \int\int (y-y_r)^2  n_3 dS
              - .. math:: \rho g \int\int (x-x_r)*(y-y_r) n_3 dS
              - 0
            * - 0
              - 0
              - .. math:: \rho g \int\int (x-x_r) n_3 dS
              - .. math:: \rho g \int\int (x-x_r)*(y-y_r) n_3 dS
              - .. math:: \rho g \int\int (x-x_r)**2 n_3 dS
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
        
        
        
        .. list-table:: Buoyancy stiffness  (in hydrodynamic reference frame)
            :widths: 40 40 40 40 40 40
            :header-rows: 0
        
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - .. math:: \rho g V * (z_b-z_r)
              - 0
              - .. math:: -\rho g V * (x_b-x_r)
            * - 0
              - 0
              - 0
              - 0
              - .. math:: \rho g V * (z_b-z_r)
              - .. math:: -\rho g V * (y_b-y_r)
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
        
        
        
        .. list-table:: Gravity stiffness  (in hydrodynamic reference frame), for reference (implementation in Snoopy.Mechanics.MechanicalSolver.get_gravity_stiffness)
            :widths: 40 40 40 40 40 40
            :header-rows: 0
        
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0
            * - 0
              - 0
              - 0
              - .. math:: -mg(z_g-z_r)
              - 0
              - .. math:: mg(x_g-x_r)
            * - 0
              - 0
              - 0
              - 0
              - .. math:: -mg(z_g-z_r)
              - .. math:: mg(y_g-y_r)
            * - 0
              - 0
              - 0
              - 0
              - 0
              - 0

        Formulas (body-fixed reference frame)
        -------------------------------------
        ...
        """
        from Snoopy import Mechanics as mcn
        
        if self.nbpanels == 0:
            # Empty mesh, return zeros
            logger.debug("Mesh is empty, cannot integrate hydrostatic.")
            return np.zeros((6,6),dtype=float)
        
        normal_ref_point = self.getRefPoint()
                
        res = np.zeros( (6,6), dtype = float )

        normalsAtGaussPoints    = self.getNormalsAtGaussPoints()
        weight                  = self.getGaussWiWjdetJ()
        gaussPoints             = self.getGaussPoints()

        if ref_frame == "body-fixed" : 
            axoi =  ( gaussPoints[:,0]  - normal_ref_point[0] )
            ayoi =  ( gaussPoints[:,1]  - normal_ref_point[1] )
            for i in range(6):
                res[i,2] -= np.sum( weight *  normalsAtGaussPoints[:,i] )
                res[i,3] -= np.sum( ayoi*weight *  normalsAtGaussPoints[:,i] )
                res[i,4] = np.sum( axoi*weight *  normalsAtGaussPoints[:,i] )
                
            res = mcn.matrans3(res, origin = normal_ref_point, destination= output_ref_point)

        elif "hydro" in ref_frame :
            
            if hull_stiffness :
                axoi =  ( gaussPoints[:,0]  - output_ref_point[0] )
                ayoi =  ( gaussPoints[:,1]  - output_ref_point[1] )
                
                res[2,2] += -np.sum( weight * normalsAtGaussPoints[:,2] )
                res[2,3] += -np.sum( ayoi * weight * normalsAtGaussPoints[:,2] )
                res[2,4] += np.sum( axoi * weight * normalsAtGaussPoints[:,2] ) 
                res[3,3] += -np.sum( ayoi**2 * weight * normalsAtGaussPoints[:,2] )
                res[3,4] += np.sum( axoi * ayoi * weight * normalsAtGaussPoints[:,2] )
                res[4,4] += -np.sum( axoi**2 * weight * normalsAtGaussPoints[:,2] )
            
                # Alternate implementation with generalized normals
                # axoi =  ( gaussPoints[:,0]  - normal_ref_point[0] )
                # ayoi =  ( gaussPoints[:,1]  - normal_ref_point[1] )
                # for i in [2,3,4]:
                #     res[i,2] -= np.sum( weight *  normalsAtGaussPoints[:,i] )
                #     res[i,3] -= np.sum( ayoi*weight *  normalsAtGaussPoints[:,i] )
                #     res[i,4] = np.sum( axoi*weight *  normalsAtGaussPoints[:,i] )
                # return mcn.matrans3(res, origin = normal_ref_point, destination= output_ref_point)
        
            if buoyancy_stiffness :   # Warning : if this part is added, the matrix cannot be moved with matrans.
                volume = self.integrate_volume()
                cob = self.integrate_cob()
                cob_ref = cob - output_ref_point
                res[4,4] += cob_ref[2] * volume
                res[3,3] += cob_ref[2] * volume
                res[3,5] += -volume * cob_ref[0]
                res[4,5] += -volume * cob_ref[1]

            res[3,2] = res[2,3]
            res[4,2] = res[2,4]
            res[4,3] = res[3,4]

        else :
            raise(Exception("ref_frame {ref_frame:} not recognized"))
            
        if rho_g is not None : 
            res *= rho_g
            
        return res
                


    def integrate_cob_py(self, nbGP = 1):
        """Compute and return the center of buoyancy (Assuming closed hull, with free-surface at z=0)
        """
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)

        volume = self.integrate_volume(nbGP =nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        x = np.sum(gp[:,2] * normals[:,2] * gp[:,0] * weight)
        y = np.sum(gp[:,2] * normals[:,2] * gp[:,1] * weight)
        z = np.sum(0.5*(gp[:,0] * normals[:,0] + gp[:,1] * normals[:,1]) * gp[:,2] * weight)
        return np.array([x,y,z]) / volume
    
    def integrate_waterPlaneCenter(self, nbGP = 1):
        Sw = self.integrate_waterPlaneArea(nbGP = nbGP)
        Aw = np.zeros(3,dtype='float')
        
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        
        Aw[0:2] = -np.sum(gp[:,0:2] * (normals[:,2] * weight).reshape(-1,1), axis=0) / Sw
        
        return Aw
    

    def write(self, filename, *args, **kwargs):

        p = os.path.dirname(filename)
        if p and not os.path.exists( p ) :
            os.makedirs( p )

        if os.path.splitext(filename)[-1] in [".hst",".hs0"] :
            self.writeHydroStar(filename, *args, **kwargs)
        else :
            _Meshing.Mesh.write(self, filename, *args, **kwargs)


    def write_vtk_writer(self , filename , vtk_writer):
        """Write mesh with vtk library

        Parameters
        ----------
        filename : str
            Output filename
        vtk_writer : vtk.vtkWriter
            Vtk writer
        """
        w = vtk_writer()
        w.SetInputData( self.toVtkUnstructuredGrid() )
        w.SetFileName( filename )
        w.Update()
        w.Write()
        
        
    def write_vtu(self , filename) : 
        """Write mesh as vtk .vtu file

        Parameters
        ----------
        filename : str
            Output filename
        """
        import vtk
        self.write_vtk_writer( filename , vtk.vtkXMLUnstructuredGridWriter  )
        
    
    def write_vtk_hdf(self, filename, mode="w"):
        """Write to HDF vtk format

        Parameters
        ----------
        filename : str
            Filename.
        """

        from .vtkTools import write_vtkUnstructuredGrid_vtkhdf
        write_vtkUnstructuredGrid_vtkhdf(ugrid=self.toVtkUnstructuredGrid(),filename=filename,mode=mode)


    @staticmethod
    def _read_with_vtk( filename , reader, read_all_vector = False, read_all_scalar = False, **kwargs):
        r = reader()
        r.SetFileName(filename)
        if read_all_vector:
            r.ReadAllVectorsOn()
        if read_all_scalar:
            r.ReadAllScalarsOn()
        r.Update()
        return Mesh.FromPolydata( r.GetOutput(),**kwargs )
    

    @classmethod
    def ReadVtu(cls, filename, polygonHandling = "raise", BV_convention = False):
        """Read .vtu files

        Parameters
        ----------
        filename : str
            Filename

        Returns
        -------
        msh.Mesh
            Read mesh
        """
        import vtk
        return cls._read_with_vtk(  filename , 
                                    reader = vtk.vtkXMLUnstructuredGridReader, 
                                    polygonHandling  = polygonHandling,
                                    BV_convention = BV_convention)
    
    @classmethod
    def ReadVTK(cls,filename, polygonHandling = "raise", BV_convention = False ):
        from vtk import vtkUnstructuredGridReader 
        return cls._read_with_vtk(filename, vtkUnstructuredGridReader, 
                                polygonHandling = polygonHandling,
                                read_all_vector = True, read_all_scalar = True,
                                BV_convention = BV_convention)


    @classmethod
    def ReadSTL(cls , filename ):
        """Read stl file (binary or ascii).

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        Mesh
            The Snoopy Mesh object.
        """
        import vtk
        return cls._read_with_vtk(  filename , 
                                    reader = vtk.vtkSTLReader, 
                                    )


    @classmethod
    def ReadHdf(cls, filename, polygonHandling = "raise", BV_convention = True):
        """Read .hdf files

        Parameters
        ----------
        filename : str
            Filename

        Returns
        -------
        msh.Mesh
            Read mesh
        """
        import vtk
        
        if not os.path.exists(filename):
            raise(Exception(f"{filename:} does not exists"))

        obj = cls._read_with_vtk(  filename , reader = vtk.vtkHDFReader, 
                                    polygonHandling = polygonHandling,
                                    BV_convention    = BV_convention)
                                    
        # ATTENTION: ref_position is at CoB
        obj.setRefPoint(obj.integrate_cob())
        return obj
       


    def writeHydroStar(self, filename, panelType=1):
        """Write to HydroStar format.

        Parameters
        ----------
        filename : str
            The file name
        panelType : TYPE, optional
            PANEL_TYPE. The default is 1 (the panels have an "id").      
        """

        s_nodes = ""
        for i, n in enumerate(self.nodes) :
            s_nodes += "{:} {:.5e} {:.5e} {:.5e}\n" .format( i+1 , *n)

        def output_str(s_panels, ipanel, n_off):
            if panelType == 0: s_panels += ("{:5d}" *(len(n_off)-1) +"{:5d}").format(*n_off)
            else: s_panels += ("{:5d} " *len(n_off) +"{:5d}").format(ipanel, *n_off)
            if self.hasPanelsData():
                pd_ = self.getPanelsData()
                if len(n_off) == 3:
                    s_panels += " {:5d}".format(n_off[-1])
                s_panels += (" {:18.11f}"*pd_.shape[1]).format(*pd_[ipanel -1,:])
            s_panels += "\n"
            return s_panels
        s_panels = ""
        ipanel = 1
        for n in self.tris :
            n_off = n + 1
            #if panelType == 0: s_panels += "{} {} {}\n".format( *n_off )
            #else:  s_panels += "{} {} {} {}\n".format( ipanel, *n_off )
            s_panels = output_str(s_panels, ipanel, n_off)
            ipanel += 1
        for n in self.quads :
            n_off = n + 1
            #if panelType == 0: s_panels += "{} {} {} {}\n".format( *n_off )
            #else: s_panels += "{} {} {} {} {}\n".format( ipanel, *n_off )
            s_panels = output_str(s_panels, ipanel, n_off)
            ipanel += 1


        with open(filename, "w") as f :
            f.write( "NUMPANEL 1 1 {}\n".format(self.nbpanels))
            if hasattr(self, 'sym'):
                if self.sym == _Meshing.SymmetryTypes.XZ_PLANE:
                    f.write("SYMMETRY 1 1\n")
                elif self.sym == _Meshing.SymmetryTypes.NONE:
                    pass    # symmetry 0, no need to write
                else:
                    f.write(f"Given symmetry: {self.sym} is not taken into account yet.")
            f.write( "COORDINATES\n{:}ENDCOORDINATES\n".format(s_nodes) )
            if panelType == 0: f.write( "PANEL TYPE 0\n{:}ENDPANEL\n".format(s_panels))
            else: f.write( "PANEL TYPE 1\n{:}ENDPANEL\n".format(s_panels))
            f.write( "ENDFILE")


    def writeMsh( self, filename  ):
        """Write to msh (Moloh)."""

        s_nodes = ""
        for i, n in enumerate(self.nodes) :
            s_nodes += "{:} {:.5e} {:.5e} {:.5e}\n" .format( i+1 , *n)


        s_panels = ""
        ipanel = 1
        for n in self.quads :
            n_off = n + 1
            s_panels += "{} {} {} {} {} 1 0\n".format( ipanel, *n_off )
            ipanel += 1

        for n in self.tris :
            n_off = n + 1
            s_panels += "{} {} {} {} {} 1 0\n".format( ipanel, *n_off, n_off[-1] )
            ipanel += 1

        with open(filename, "w") as f :
            f.write( "NODES\n{:}ENDNODES\n".format(s_nodes) )
            f.write( "PANELS\n{:}ENDPANELS\n".format(s_panels))
            f.write( "GROUPS\n1 Hull\nENDGROUPS")

        return



    def getCb(self):
        """Compute block coefficient.
        """
        dims = [ a[1]-a[0] for a in self.getBounds() ]
        return self.integrate_volume() / np.prod( dims )


    def __str__(self) :
        """Print basic mesh information.
        """

        if self.nbnodes == 0 :
            return "Empty mesh"

        s = """
#------- Mesh object ------------------------#
Number of nodes  : {:}
Number of panels : {:}  ({:} QUAD and {:} TRIS)
Length      : {:.1f}
Beam        : {:.1f}
Draft/Depth : {:.1f}
Volume      : {:.1f}
Bounds : x=[{:8.2f},{:8.2f}]
         y=[{:8.2f},{:8.2f}]
         z=[{:8.2f},{:8.2f}]
#--------------------------------------------#"""
        return s.format( self.nbnodes, self.nbpanels, self.nbquads, self.nbtris,
                         self.getBounds()[0][1] - self.getBounds()[0][0],
                         self.getBounds()[1][1] - self.getBounds()[1][0],
                         self.getBounds()[2][1] - self.getBounds()[2][0],
                         self.integrate_volume(),
                         *[item for sublist in self.getBounds() for item in sublist] )


    def getBounds(self) :
        return [(np.min(self.nodes[:,0]), np.max(self.nodes[:,0])) ,
                (np.min(self.nodes[:,1]), np.max(self.nodes[:,1])) ,
                (np.min(self.nodes[:,2]), np.max(self.nodes[:,2])) ]



    def rotateAxis( self, axis=[0.,1.,0.], angle=0. ):
        """Rotate a mesh around axis given by vector (angle in radians).

        """
        if angle != 0.:
            v = geo.Vector(axis)
            v.normalise()
            rmat = np.transpose(geo.AxisAndAngle(v,angle).getMatrix())

            self.setVertices( np.matmul(self.getVertices(),rmat) )

    def rotateZYX( self, center=[0.,0.,0.], angle=[0.,0.,0.] ):
        """Rotate a mesh around center with Euler angles [roll, pitch, yaw] (angle in radians).

        """
        if any(angle) != 0.:
            rmat = geo.EulerAngles_XYZ_e(*angle).getMatrix()

            #Apply rotation around center : V' = [rmat]*[V-center] + center
            self.offset([-1.*i for i in center])
            self.setVertices( np.transpose(np.matmul(rmat,np.transpose(self.getVertices()))) )
            self.offset(center)

    def convertToVtk(mesh, offset=(0., 0., 0.), format = "vtkPolyData"):
        """Copy mesh to vtk polydata structure.
        
        Possible performance improvement : Set all at once using vtk.util.numpy_support ?
        """
        import vtk
        from vtk.util import numpy_support

        if format == "vtkPolyData":
            vtkdata = vtk.vtkPolyData()
            cells = vtk.vtkCellArray()
            vtkdata.SetPolys(cells)
        elif format == "vtkUnstructuredGrid":
            vtkdata = vtk.vtkUnstructuredGrid()
        else:
            raise NotImplementedError(f"Format {format} is not supported. Only vtkPolyData or vtkUnstructuredGrid for now!")

        # Fill up points 
        points = vtk.vtkPoints()
        for xyz in mesh.nodes:
            points.InsertNextPoint( xyz + offset)
        vtkdata.SetPoints(points)

        # Fill up cells
        for panel in mesh.tris :
            vtkdata.InsertNextCell( vtk.VTK_TRIANGLE, 3, panel  )
        for panel in mesh.quads :
            vtkdata.InsertNextCell( vtk.VTK_QUAD, 4, panel  )


        if mesh.hasPanelsData():
            from .hydro_names import get_full_dataname_metadata
            panelsData      = mesh.getPanelsData()
            panelsMetaData  = mesh.getMetaDataDF()
            all_full_name = get_full_dataname_metadata(panelsMetaData)
            

            for index,full_name in enumerate(all_full_name):
                scalar = numpy_support.numpy_to_vtk(panelsData[:,index])
                scalar.SetName(full_name)
                vtkdata.GetCellData().AddArray( scalar )
            
            for colname in panelsMetaData:
                col = panelsMetaData[colname]
                if "name" in colname:
                    array = vtk.vtkStringArray()
                    for item in col:
                        array.InsertNextValue(item)
                    array.SetName(colname)
                else:
                    array = numpy_support.numpy_to_vtk(col.to_numpy())
                    array.SetName(colname)
                vtkdata.GetFieldData().AddArray(array)

        return vtkdata

    def toVtkPolyData(self, offset=(0., 0., 0.)):
        return self.convertToVtk(offset,format = "vtkPolyData")

    def toVtkUnstructuredGrid(self,offset=(0., 0., 0.)):
        obj = self.convertToVtk(offset=offset,format = "vtkUnstructuredGrid")
        return obj


    def _vtk_lite(self, *args, **kwargs):
        from Snoopy.Meshing.vtkView import VtkLite
        return VtkLite.FromPolydata( self.toVtkPolyData(), *args,**kwargs )


    def to_interactive(self, **kwargs) :
        """Display mesh with vtk.
        """
        self._vtk_lite(**kwargs).to_interactive()

    def vtkView(self, *args, **kwargs):
        logger.warning("vtkView is deprecated, please use '.to_interactive'")
        self.to_interactive(*args, **kwargs)

    def to_picture(self, outputFile, **kwargs):
        self._vtk_lite(**kwargs).to_picture(output_file=outputFile)


    def to_notebook(self, **kwargs):
        return self._vtk_lite(**kwargs).to_notebook()


    @classmethod
    def FromPolydata(cls, polydata, polygonHandling = "raise", BV_convention = True):
        """Create Snoopy Mesh from vtk polydata."""
        import vtk
        from vtk.util import numpy_support
        points = polydata.GetPoints()

        etris = np.zeros( (0,3), dtype = int)
        equads = np.zeros( (0,4), dtype = int)

        if points is None :
            return cls( Vertices = np.zeros( (0,3), dtype = float ), Tris = etris, Quads = equads  )
        elif polydata.GetPoints().GetNumberOfPoints() == 0:
            return cls( Vertices = np.zeros( (0,3), dtype = float ), Tris = etris, Quads = equads  )

        all_cell_data = polydata.GetCellData()
        nb_data = all_cell_data.GetNumberOfArrays()

        nodes = numpy_support.vtk_to_numpy(  points.GetData() )

        # Get cell data
        idList = vtk.vtkIdList()
        quads = []
        tris = []
        notHandled = []
        # Stored index as numeric to filter later

        quadIds = []
        triIds  = [] 
        for ipanel in range(polydata.GetNumberOfCells()):
            polydata.GetCellPoints(ipanel, idList)

            nNodes = idList.GetNumberOfIds()

            nodesId = [idList.GetId(i) for i in range(nNodes)]

            if nNodes == 4:
                quads.append( nodesId )
                quadIds.append(ipanel)
            elif nNodes == 3:
                tris.append( nodesId )
                triIds.append(ipanel)
            elif polygonHandling == "raise":
                raise RuntimeError("Encounter polygons, the conversion to snoopy mesh object might have trouble")
            elif polygonHandling == "triangulate" :  # Polygon, to be triangulated
                if nb_data > 0:
                    logger.warning("Encounter polygons, the conversion to snoopy mesh object might have trouble, panelsData will be wrong")
                nodesId = np.array(nodesId)
                notHandled.append( ipanel )
                triangleIds = vtk.vtkIdList()
                polydata.GetCell(ipanel).Triangulate(triangleIds)
                for itri in range( triangleIds.GetNumberOfIds() // 3 ):
                    subId = [ triangleIds.GetId( itri*3 + 0 ), triangleIds.GetId( itri*3 + 1 ), triangleIds.GetId( itri*3 + 2 ) ]
                    tris.append( nodesId[subId] )

        if len(tris) == 0:
            tris = etris
        else :
            tris = np.array(tris, dtype = int)

        if len(quads) == 0:
            quads = equads
        else :
            quads = np.array(quads, dtype = int)

        #----- Handle cells data. First Tris, then Quads
        metadata = {}
        
        flatten_cell_data = []
        data_name_list = []
        for i in range(nb_data) : 
            extracted_array = all_cell_data.GetArray(i)
            array = numpy_support.vtk_to_numpy (extracted_array)
            
            if len(array.shape) == 1:
                flatten_cell_data.append(array)
                data_name_list.append(extracted_array.GetName())
            elif len(array.shape) == 2:
                for ii in range(array.shape[1]):
                    flatten_cell_data.append(array[:,ii])
                    data_name_list.append(extracted_array.GetName()+f"_{ii}")
                
            else:
                raise NotImplementedError("This routine is not yet ready to read multidimensioned array")


        nb_flatten_cell_data = len(flatten_cell_data)
        panel_data = np.zeros( ( len(tris) + len(quads), nb_flatten_cell_data ) )
        for iarray, array  in enumerate(flatten_cell_data):
            panel_data[: , iarray] = np.concatenate([array[triIds],array[quadIds]])
        

        if BV_convention:
            allFieldData = polydata.GetFieldData()
            nbFieldData = allFieldData.GetNumberOfArrays()
            for ifield in range(nbFieldData):
                field = allFieldData.GetAbstractArray(ifield)
                fieldname = field.GetName()
                if fieldname == "data_name":
                    data_name = []
                    for ii in range(field.GetNumberOfValues()):
                        data_name.append(field.GetValue(ii))
                    metadata["dataNames"] = data_name
                elif fieldname == "data_type":
                    metadata["dataTypes"] = numpy_support.vtk_to_numpy(field)
                elif fieldname == "frequency":
                    metadata["dataFreqs"] = numpy_support.vtk_to_numpy(field)
                elif fieldname == "heading":
                    metadata["dataHeads"] = numpy_support.vtk_to_numpy(field)
            obj = cls( Vertices = nodes, Tris = tris, Quads = quads, panelsData = panel_data  )
            if len(metadata.keys()) == 4:
                obj.setPanelsMetadata(**metadata)

        else:
            if nb_flatten_cell_data > 1:
                obj = cls( Vertices = nodes, Tris = tris, Quads = quads, panelsData = panel_data  )
                obj.setDataNames(data_name_list)
            else:
                obj = cls( Vertices = nodes, Tris = tris, Quads = quads )
        return obj


    def extractWaterLineSegments(self, eps=1e-4):
        """This method returns all the edges present on the plane z = 0 (not ordered).

        Parameters
        ----------
        eps : TYPE, optional
            Tolerance for considering an edge on the free-surface. The default is 1e-4.

        Returns
        -------
        np.ndarray
            List of nodes ID corresponding to overall mesh nodes
        """
        
        # Extraction of all edges: 4 for quadrangles and 3 for triangles in the whole mesh.
        # seg = [[index_first_node, index_second_node], ...].
        seg = self.getSegments()

        # Maximum of the absolute value of the z coordinate amongst the two boundaries of each segment.
        # zSeg = [max(|z(index_first_node), z(index_second_node)|), ...]
        zSeg = np.max(np.abs(self.nodes[:, 2][seg]), axis=1)

        # Segments where zSeg is null (waterline).
        seg_on_waterline = seg[np.where(zSeg < eps)[0]]

        _ , ind = np.unique( np.sort(seg_on_waterline, axis = 1) , axis = 0, return_index = True)
        
        return seg_on_waterline[ind]


    def checkTightWaterlines(self, waterline_segments):
        """Check that the waterline is water-tight.
        
        
        Parameters
        ----------
        waterline_segments : np.ndarray
            Waterline segments (nodes connectivity)

        Returns
        -------
        bool
            True if the waterline is closed. It also works in case of multiple waterlines.
        """
        from Snoopy.Meshing.waterline import SegmentCollection
        return SegmentCollection( waterline_segments ).is_closed()
        
   
    
    def extractWaterlineObj(self, eps=1e-4):
        """Extract waterline from hull mesh as a SINGLE waterline (DO NOT give the elementary waterline loops).
        
        Return
        ------
        np.ndarray
            array of segments defined by IDs (ordered).
        """
        # Segments on the waterline (not ordered).
        from Snoopy.Meshing.waterline import Waterline
        return Waterline( self.extractWaterLineSegments(eps), self.nodes[:,:2], self.sym == _Meshing.SymmetryTypes.XZ_PLANE )
    
    
    
    def getWaterlineBound(self):
        """Return waterline bounds.
        """
        self.extractWaterlineObj().getBounds()


    def plotWaterline(self, eps=1e-4, *args, **kwargs):
        """This method plots the waterline."""        
        self.extractWaterlineObj().plot(*args, **kwargs)



    def plot2D(self, proj="xy", *args, **kwargs):
        """Plot surface mesh with matplotlib

        Parameters
        ==========
        proj: str, Default "xy"
            List of axe to consider when plotting. 
            Default is xy, so z is ignored. 
            Possible values: "xy", "xz", "yz"
        """
        from Snoopy.PyplotTools import plotMesh
        return plotMesh( self.nodes, self.quads, self.tris, proj=proj, *args, **kwargs)


    def getCutMesh(self,*args,**kwargs):
        m = Mesh(super().getCutMesh(*args,**kwargs))
        if m.getNPanels()>0 : 
            m.setRefPoint(self.getRefPoint())
        return m
    


#Make C++ wrapped function return the python subclass. Warning : Make a copy
for method in ["getCutMesh"]:
    def makeFun(method):
        fun = getattr(_Meshing.Mesh, method)
        def newFun(*args,**kwargs) :
            return Mesh(fun(*args, **kwargs))
        newFun.__doc__ = fun.__doc__
        return newFun
    setattr(Mesh, method+"Copy", makeFun(method))




