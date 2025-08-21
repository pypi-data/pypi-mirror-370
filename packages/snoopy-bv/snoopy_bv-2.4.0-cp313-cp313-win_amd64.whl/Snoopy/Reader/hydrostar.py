"""
   Contain readers for HydroStar HDF5 files
"""
import os
import h5py
import numpy as np
import xarray as xr
from Snoopy.Mechanics import vectran3
from Snoopy import Spectral as sp
from Snoopy import logger



def read_hsmcn_h5(file_path, kind = "Motion"):
    """Read HSmcn HDF5 output file and return list of RAOs  (list length = number of bodies)

    Note
    ----
    This should now be replaced by "HydroCoef" : ````da.hydro.export_rao_6_dof(kind = "motion")````

    Parameters
    ----------
    file_path : str
        HDF file to read
    kind : str, optional
        RAO to be read, "Motion" or "Excitation". The default is "Motion".

    Returns
    -------
    raoList : list
        list of sp.Rao (one RAO with 6ddl for each body)
    """
    data = xr.open_dataset(file_path)

    raoList = []
    for ibody in range(data.attrs["NBBODY"]) :

        if kind in ["Excitation" , "Motion"] :
            rao_data = np.transpose(data[f"{kind:}_Re"].values[:,ibody,:,:] + 1j*data[f"{kind}_Im"].values[:,ibody,:,:], axes = [1, 0, 2])

        elif kind in [ "Radiation", "Radiation_wo_inf"] :
            motion_data = np.transpose(data["Motion_Re"].values[:,ibody,:,:] + 1j*data[f"Motion_Im"].values[:,ibody,:,:], axes = [1, 0, 2])
            amss = data["AddedMass"].transpose(  "Heading" , "Frequency" , "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ :,:,0,0,:,: ]

            if kind == "Radiation_wo_inf" :
                amssInf = data["AddedMassInf"].transpose(  "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ 0,0,:,: ]


            damp = data["WaveDamping"].transpose(  "Heading" , "Frequency" , "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ :,:,0,0,:,: ]
            rao_data = np.empty( motion_data.shape , dtype = "complex" )

            for ifreq in range(len( data["Frequency"] )) :
                w = data["Frequency"][ifreq]
                for ihead in range(len( data["Heading"] )) :
                    we = sp.w2we( w ,  data["Heading"][ihead] , speed = data.attrs["SPEED"] )

                    if kind == "Radiation" :
                        amss_ = amss[ ihead, ifreq, : , : ].values
                    else :
                        amss_ = amss[ ihead, ifreq, : , : ].values - amssInf.values

                    rad = -we**2 * amss_ + 1j * we * damp[ ihead, ifreq, : , : ].values
                    rao_data[ihead, ifreq] = -np.matmul(  rad , motion_data[ihead, ifreq, :]  )


        raoList.append( sp.Rao(
                  b = np.deg2rad( data.Heading.values) ,
                  w = data.Frequency.values,
                  cvalue = rao_data,
                  modes = [1,2,3,4,5,6],
                  refPoint = data.RefPoint.values[ibody],
                  waveRefPoint = data.RefWave.values,
                  depth = data.attrs["WATERDEPTH"],
                  forwardSpeed = data.attrs["SPEED"]
                  ) )

    data.close()
    return raoList



@xr.register_dataset_accessor("prs")
class PressureData():
    """Class to handle pressure output from HydroStar, using netcdf / xarray format.
    """

    def __init__(self, data):
        self._data = data
        
    
    def get_at_ref_point(self , ref_point):
        """Return a copy of the pressure dataset, with reference point of the radiated pressure changed.

        Parameters
        ----------
        ref_point : np.ndarray(3)
            The new reference point
            
        Returns
        -------
        xarray.DataSet
            Pressure dataset with the reference point change to the ref_point.
        """
        old_ref_point = self._data.ref_point[0,:].values
        new_ref_point = np.asarray(ref_point).reshape(3,)
        if np.allclose(old_ref_point,new_ref_point):
            return self._data
        else:
            ds = self._data.copy(True) # To be sure that original dataset is not modified. 
            logger.debug(f"Changing RefPoint from {old_ref_point} to {new_ref_point}")
            for var in  self._data.keys():
                if "rad" in var: 
                    logger.debug(f"            -> {var:} ")

                    if "inf" in var:
                        other_dims_than_modes = ['point_id']
                        original_dims = ('mode', 'point_id')
                    else:
                        other_dims_than_modes = ['frequency', 'heading', 'point_id']
                        original_dims = ('frequency', 'heading', 'mode', 'point_id')

                    # Stack all dimension 
                    da = ds[var].stack( all_but_mode = other_dims_than_modes )
                   
                    for i in range(da.shape[-1]) :
                        da.values[:,i] = vectran3(  da.values[:,i], origin = old_ref_point, 
                                                    destination = new_ref_point, isMotion = False)

                    # Unstack
                    ds[var] = da.unstack().transpose( *original_dims )

            ds["ref_point"].values[0,:] = ref_point
            return ds
    
    
    def get_at_wave_ref_point( self, wave_ref_point):
        """Return a copy of the pressure dataset, with wave reference point of the incident & diffracted pressures changed.

        Parameters
        ----------
        wave_ref_point : np.ndarray(2)
            The new wave reference point
            
        Returns
        -------
        xarray.DataSet
            Pressure dataset with the reference point change to the ref_point.
        """
        VectorToNewWaveRefPoint = wave_ref_point- self._data.ref_wave.values
        
        list_of_k = sp.dispersion.w2k( self._data.frequency.values , depth = self._data.attrs["depth"] ).reshape(len(self._data.frequency.values), 1)
        phase_shift = np.exp( +1j* list_of_k* 
                             (VectorToNewWaveRefPoint[0]*np.cos(np.deg2rad(self._data.heading.values))
                              + VectorToNewWaveRefPoint[1]*np.sin(np.deg2rad(self._data.heading.values)) ) )
        
        phase_shift = phase_shift.reshape(len(np.deg2rad(self._data.frequency.values)), len(np.deg2rad(self._data.heading.values)),1)
                
        ds = self._data.copy(True) # To be sure that original dataset is not modified. 
        logger.debug(f"Changing WaveRefPoint to {wave_ref_point}")
        for var in  self._data.keys():
            if "inc" in var or "dif" in var or var == "pressure" or var == "pressure_im" or var == "pressure_re": 
                logger.debug(f"            -> {var:} ")    
                ds[var] = self._data[var] * phase_shift
    
                
    
        ds["ref_wave"].values[:] = wave_ref_point

        return( ds )
    
    def export_to_rao( self, component = "total", motionRaos = None, angleUnit = "rad"):
        """Export presure as Rao objects.

        Parameters
        ----------
        component : str, optional
            among ["total", "inc", "dif", "inc+dif", "rad1", "rad2", ..., "rad6", "total_awe_from_given_motion", "total_rwe_from_given_motion", "total_rad_from_given_motion"]. The default is "total".
            !!!  "total" component content depends on the last execution of hsprs (could then varry from AWE to RWE...)
        motionRaos : list
            List of 6 dofs RAOs. Used to recomposed pressure from given motions. The length of the list is the number of bodies. Each "Rao" object contains the 6 DOF components.
        angleUnit : str, optional
           'deg' or 'rad'
            unit in use for rotations description in motionRaos
        Note
        ----
        The change reference point is handled (motionRaos and self can have different reference point on input)

        Returns
        -------
        Rao
            The transfer function object containing the pressure data.
        """

        ds = self._data
        component = component.lower() # Case insensitive
        if component == "total" :
            rao_data = ds.pressure
        elif component.startswith("rad"):
            mode_index = int(component[3:])
            rao_data = ds.pressure_rad.sel(mode = mode_index)
        elif component == "inc":
            rao_data = ds.pressure_inc
        elif component == "dif":
            rao_data = ds.pressure_dif
        elif component == "inc+dif":
            rao_data = ds.pressure_inc + ds.pressure_dif
        elif component in ["total_awe_from_given_motion",
                           "perturbed_awe_from_given_motion",
                           "total_rwe_from_given_motion",
                           "total_rad_from_given_motion",
                           "hydrostatic_variation"]:
            #TODO? : move reconstruction in a dedicated method that would return a dataArray. This function would then just take the correct field.
            if motionRaos is None:
                raise(Exception(f"Motion RAOs should be given to export the component {component}"))
            if len(motionRaos) >1:
                #TODO: handle multibody case
                logger.info("'total_from_given_motion' and 'perturbed_from_given_motion' cases are not implemented in multibody.")
                raise(NotImplementedError())
            if angleUnit not in ("deg", "rad"):
                raise( Exception("angleUnit should be either 'rad' or 'deg' !") )         
            if "deg" in angleUnit:
                motionRaos_ = [motionRaos[0].getRaoAtMode(i) for i in range(motionRaos[0].getNModes())]
                for i in range(3, 6):
                    motionRaos_[i] *= np.pi /180
                motionRaos = [ sp.Rao(motionRaos_)]

            # Motion RAO ref point should match the pressure data ref point
            if not np.isclose( ds.ref_point.values[0,:], motionRaos[0].getReferencePoint() ).all() :
                logger.debug("moving point of motion to match with pressure data")
                motionRaos_at_prs_ref = motionRaos[0].getMotionRaoAtPoint(coords=ds.ref_point.values[0,:],
                                                                          angleUnit='rad')
            else:
                motionRaos_at_prs_ref = motionRaos[0]
            
            if not np.isclose( ds.ref_wave.values, motionRaos_at_prs_ref.getWaveReferencePoint()).all() :
                motionRaos_at_prs_ref = motionRaos_at_prs_ref.getRaoAtWaveReferencePoint( ds.ref_wave.values )
            # Incident and diffraction pressures.
            inc_rao = self.export_to_rao(component="inc")
            inc_prs = inc_rao.cvalues
            dif_prs = self.export_to_rao(component="dif").cvalues
            if component == "total_rwe_from_given_motion"  or  component == "total_awe_from_given_motion":
                tot_prs = inc_prs + dif_prs
            elif component == "perturbed_awe_from_given_motion":  # perturbed_from_given_motion : only diffraction and radiation.
                tot_prs = dif_prs
            else : 
                tot_prs = 0
            #Adding radiation part
            if component != "hydrostatic_variation":
                # Radiation pressures.
                for mode_index in [1, 2, 3, 4, 5, 6]:
                    prs_rao = self.export_to_rao(component=f"rad{mode_index:}")
                    motions = motionRaos_at_prs_ref.cvalues[:, :, mode_index-1] 
                    # jw * motion * prad
                    tot_prs += prs_rao.cvalues * (prs_rao.getEncFrequencies()[:,:, None] * 1j)* motions[:, :, None]
            #Adding hydrostatic pressure variation 
            if component == "total_rwe_from_given_motion" or component =="hydrostatic_variation":
                #motion varrying hydrostatic pressure (z-pos. of point)
                points = ds.points.values - self._data.ref_point.values[0,:]
                heaveRao = motionRaos_at_prs_ref.cvalues[:, :, 2:3]
                rollRao = motionRaos_at_prs_ref.cvalues[:, :, 3:4]
                pitchRao = motionRaos_at_prs_ref.cvalues[:, :, 4:5]
                tot_prs = tot_prs - heaveRao -(rollRao*points[:, 1] - pitchRao*points[:, 0]) #pi/180 because Snoopy RAOS roll, pithc, yaw are in deg/m 
            
            rao = sp.Rao(w=inc_rao.freq,
                         b=inc_rao.head,
                         cvalue=tot_prs,
                         refPoint=inc_rao.getReferencePoint(),
                         waveRefPoint=inc_rao.getWaveReferencePoint(),
                         depth=inc_rao.waterdepth,
                         forwardSpeed=inc_rao.getForwardSpeed(),
                         meanValues=inc_rao.getMeanValues())
            return rao
        else:
            raise NotImplementedError(f"Unexpected component: {component}!")
        
        rao_data = rao_data.transpose( "heading", "frequency", "point_id" )
        return sp.Rao  (w               = ds.frequency.values,
                        b               = np.deg2rad(ds.heading.values),  # h5 output from HydroStar in degree
                        cvalue          = rao_data.values,
                        refPoint        = ds.ref_point.values[0,:],
                        waveRefPoint    = ds.ref_wave.values[:],
                        depth           = ds.attrs["depth"],
                        forwardSpeed    = ds.attrs["speed"], 
                        meanValues      = np.zeros((len(ds.point_id)))  )
    
    @classmethod
    def read(cls,filename, format_version = "auto"):
        """Read standard format.

        Parameters
        ----------
        filename : str
            Path to hdf file

        Returns
        -------
        xarray
            Output
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Can't find data file: {filename}")        
        
        try:
            with xr.open_dataset(filename, engine='h5netcdf', group="Pressure") as f:
                # .compute force the actual loading of the data and return it (not deferred). The filename is thus available even of ds is further modified.
                ds = f.compute()
                f.close()
        except OSError:
            with xr.open_dataset(filename, engine='h5netcdf') as f:
                # .compute force the actual loading of the data and return it (not deferred). The filename is thus available even of ds is further modified.
                ds = f.compute()
                f.close()

        if format_version == "auto":
            if "Version" in ds.attrs.keys() :
                format_version = "hydrostar_v8.2"
                
        
        # Compatibility depending on version. 
        if format_version == "hydrostar_v8.2" : 
            compat = {k:v for k, v in compat_HS82.items() if k in ds.keys() or k in ds.coords.keys()}
            # Rename coords and dataarray
            ds = ds.rename( compat )

            # Rename attributes
            for key in list(ds.attrs.keys()):
                if key in compat_HS82:
                    ds.attrs[compat_HS82[key]] = ds.attrs.pop(key)

        ds = ds.hydro.convert_to_complex()

        return ds



compat_HS82 = {
  "Frequency" : "frequency",
  "Heading" : "heading",
  "Mode" : "mode",
  "Pressure_Dif_Im"       	:	    "pressure_dif_im" 	,
  "Pressure_Dif_Re"       	:	    "pressure_dif_re" 	,
  "Pressure_Im"           	:	    "pressure_im"     	,
  "Pressure_Inc_Im"       	:	    "pressure_inc_im"       	,
  "Pressure_Inc_Re"       	:	    "pressure_inc_re"       	,
  "Pressure_Rad_Im"       	:	    "pressure_rad_im"       	,
  "Pressure_Rad_Inf_Im"   	:	    "pressure_rad_inf_im"   	,
  "Pressure_Rad_Inf_Re"   	:	    "pressure_rad_inf_re"   	,
  "Pressure_Rad_Re"       	:	    "pressure_rad_re"       	,
  "Pressure_Re"           	:	    "pressure_re"           	,
  "VelocityX_Dif_Im"      	:	    "velocity_x_dif_im"     	,
  "VelocityX_Dif_Re"      	:	    "velocity_x_dif_re"     	,
  "VelocityX_Im"          	:	    "velocity_x_im"         	,
  "VelocityX_Inc_Im"      	:	    "velocity_x_inc_im"     	,
  "VelocityX_Inc_Re"      	:	    "velocity_x_inc_re"     	,
  "VelocityX_Rad_Im"      	:	    "velocity_x_rad_im"     	,
  "VelocityX_Rad_Inf_Im"  	:	    "velocity_x_rad_inf_im" 	,
  "VelocityX_Rad_Inf_Re"  	:	    "velocity_x_rad_inf_re" 	,
  "VelocityX_Rad_Re"      	:	    "velocity_x_rad_re"     	,
  "VelocityX_Re"          	:	    "velocity_x_re"         	,
  "VelocityY_Dif_Im"      	:	    "velocity_y_dif_im"     	,
  "VelocityY_Dif_Re"      	:	    "velocity_y_dif_re"     	,
  "VelocityY_Im"          	:	    "velocity_y_im"         	,
  "VelocityY_Inc_Im"      	:	    "velocity_y_inc_im"     	,
  "VelocityY_Inc_Re"      	:	    "velocity_y_inc_re"     	,
  "VelocityY_Rad_Im"      	:	    "velocity_y_rad_im"     	,
  "VelocityY_Rad_Inf_Im"  	:	    "velocity_y_rad_inf_im" 	,
  "VelocityY_Rad_Inf_Re"  	:	    "velocity_y_rad_inf_re" 	,
  "VelocityY_Rad_Re"      	:	    "velocity_y_rad_re"     	,
  "VelocityY_Re"          	:	    "velocity_y_re"         	,
  "VelocityZ_Dif_Im"      	:	    "velocity_z_dif_im"     	,
  "VelocityZ_Dif_Re"      	:	    "velocity_z_dif_re"     	,
  "VelocityZ_Im"          	:	    "velocity_z_im"         	,
  "VelocityZ_Inc_Im"      	:	    "velocity_z_inc_im"     	,
  "VelocityZ_Inc_Re"      	:	    "velocity_z_inc_re"     	,
  "VelocityZ_Rad_Im"      	:	    "velocity_z_rad_im"     	,
  "VelocityZ_Rad_Inf_Im"  	:	    "velocity_z_rad_inf_im" 	,
  "VelocityZ_Rad_Inf_Re"  	:	    "velocity_z_rad_inf_re" 	,
  "VelocityZ_Rad_Re"      	:	    "velocity_z_rad_re"     	,
  "VelocityZ_Re"          	:	    "velocity_z_re"    ,
  "RefPoint"             	:	    "ref_point",
  "RefWavePoint"            :       "ref_wave",
  "ForwardSpeed"           : "speed",
  "SPEED"           : "speed",
  "WATERDEPTH" : "depth",
  "Version"    	 : "version",
  "InputFile" : "input_file",
  "InputFileHash" : "input_file_hash",
  "McnDBFile" : "mcn_db_file",
  "RdfDBFile" : "rdf_db_file",
  "McnDBFileHash" : "mcn_db_file_hash",
  "RdfDBFileHash" : "rdf_db_file_hash",
  "ExecutableHash" : "executable_hash"
  }



if __name__ == "__main__": 


    from Snoopy.Reader import TEST_DIR
    fname  = f"{TEST_DIR:}/p_b31.h5"
    ds = PressureData.read( fname )
    raos = ds.prs.export_to_rao()
