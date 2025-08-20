
import numpy as np
import xarray as xa
from tqdm import tqdm
from Snoopy import logger
from Snoopy.Mechanics import g, matrans3, vectran3
from ..Spectral import w2we
from .mechanicalsolver import MechanicalSolver , get_gravity_stiffness, CoefZeroFenc_freq_range
from .hydro_coef import RdfCoef
from Snoopy.Tools.print_format import write_xarray

#------------> Compute hydrocoef from Snoopy mesh object
def get_baseFlowStiffness_unscaled_from_SnoopyMesh(pressure_mesh,ref_point = None):        
    try:
        value = pressure_mesh.integrate_fields_xarray("baseFlowStiffness_integrant",
                                        dimension   = ["mode_j"],
                                        is_real     = True).transpose().values
    except ValueError:
        # NO base flow stiffness -> Return zero
        return np.zeros((6,6), dtype= float)
    if ref_point is not None:
        return matrans3(value,origin = pressure_mesh.getRefPoint(), destination = ref_point)
    else:
        return value

def get_baseFlowStiffness_scaled_from_SnoopyMesh(pressure_mesh, rho , speed, ref_point = None):
    return get_baseFlowStiffness_unscaled_from_SnoopyMesh(pressure_mesh, ref_point = ref_point) * rho *(speed**2)


def get_rdfcoef_from_mesh( pressure_mesh, speed, rho, depth = 0., output_ref_point = None ):
    returnDict = {}
    g = 9.81
    returnDict["rho"]   = rho 
    returnDict["depth"] = depth
    
    CoB = pressure_mesh.integrate_cob()
    if output_ref_point is None:
        output_ref_point = CoB

    logger.info(f"Reference point : {output_ref_point}")
    if not np.allclose(CoB,output_ref_point):
        logger.warning(f"Reference point of rdf_coef is not at CoB ({CoB})!!!")


        
    panelsMetaData = pressure_mesh.getMetaDataDF()
    panelsMetaData_rad = panelsMetaData.loc[panelsMetaData.data_name == "PRESSURE_RAD"]
    panelsMetaData_radXA = panelsMetaData_rad.set_index(["data_name","heading","frequency",'data_type']).to_xarray()


    all_heading = panelsMetaData_radXA.heading.values
    all_freq    = panelsMetaData_radXA.frequency.values
    nb_heading = len(all_heading)
    nb_frequency = len(all_freq)
        
    
    if "baseFlowStiffness_integrant" in panelsMetaData.data_name.values:
        returnDict["base_flow_stiffness"] = \
            get_baseFlowStiffness_scaled_from_SnoopyMesh(pressure_mesh, rho, speed)[np.newaxis, ...]
        
        
    
    hydrostatic_hull = pressure_mesh.integrate_stiffness_matrix(ref_frame = "hydro", output_ref_point = output_ref_point, buoyancy_stiffness = False)
    returnDict["hydrostatic_hull"] = (hydrostatic_hull* rho*g)[np.newaxis, ...]


    encounter_frequency = np.zeros((nb_heading,nb_frequency),dtype = float)
    for ihead,head in enumerate(all_heading):
        for ifreq,freq in enumerate(all_freq):
            encounter_frequency[ihead, ifreq] = w2we( w = freq, speed=speed, b=head*np.pi / 180., depth=depth )


    info = {"rho" : rho,  "encounter_frequency": encounter_frequency, "output_ref_point": output_ref_point}

    # Attention: for now all the pressure stored in panelsData is outputted at CoB, so before integration, 
    # we need to set refPoint of mesh to CoB
    pressure_mesh.setRefPoint(CoB)
    excitation      = get_from_pressure_integration(pressure_mesh, "excitation", **info).values[np.newaxis, ...]
    added_mass      = get_from_pressure_integration(pressure_mesh, "added_mass", **info).values[np.newaxis,np.newaxis, ...]
    wave_damping    = get_from_pressure_integration(pressure_mesh, "wave_damping", **info).values[np.newaxis,np.newaxis, ...]
    fkload          = get_from_pressure_integration(pressure_mesh, "incident_load", **info).values[np.newaxis, ...]
    diffraction     = get_from_pressure_integration(pressure_mesh, "diffraction", **info).values[np.newaxis, ...]

    returnDict.update({ "excitation_load"     : excitation,
                        "incident_load"       : fkload,
                        "diffraction_load"    : diffraction,
                        "added_mass"          : added_mass,
                        "wave_damping"        : wave_damping,
                        "speed"               : speed,
                        "frequency"           : all_freq,
                        "heading"             : all_heading,  
                        "ref_point"           : output_ref_point.reshape(1,3),
                        "cob"                 : CoB.reshape(1,3),
                        "ref_wave"            : CoB[:2],  # This assumes that REF_WAVE in the mesh data is CoB
                        "nb_body" : 1})
    
    # Hydrostatic pressure stiffness, in body fixed reference frame
    hstat_hull_bf = g * rho * pressure_mesh.integrate_stiffness_matrix( ref_frame = "body-fixed", output_ref_point=output_ref_point )[np.newaxis , :, :]
    res = RdfCoef.Build(**returnDict, hydrostatic_hull_bf = hstat_hull_bf)
    
    assert( res.hydro.check() )

    return res

    

def get_from_pressure_integration(pressure_mesh, quantity_name,encounter_frequency, rho, output_ref_point = None ):
    """Compute various hydrodynamic coefficients from stored panelsData in pressure_mesh 
    objects

    Parameters
    ----------
    pressure_mesh : Snoopy.Meshing.Mesh 
        Hydro mesh with panelsData containing pressure 
    quantity_name : str
        selection of quality of interest: 
        "added_mass","wave_damping", "excitation",
        "excitation_re" or "excitation_im"
    encounter_frequency : np.ndarray
        encounter frequency: table of nb_heading x nb_frequency
    rho : float
        water density
    output_ref_point : np.ndarray or None
        Following the decomposed pressure reference, the default reference point is the CoB. This can be changed using output_ref_point

    Returns
    -------
    np.ndarray
        final output, table of size: 
         - nb_heading x nb_frequency x 6 x 6 for added_mass and wave_damping
         - nb_heading x nb_frequency x 6     for excitationXXX
         
    """
    
    g = 9.81
    if quantity_name in ["added_mass","wave_damping"]:
        rad_coef = pressure_mesh.get_radiation_coef()
        if quantity_name == "added_mass":
            for ihead, head in enumerate(rad_coef.heading):
                for ifreq, freq in enumerate(rad_coef.frequency):
                    rad_coef[ihead,ifreq,:,:]  /=  encounter_frequency[ihead, ifreq]
            res =  rho * g * rad_coef.imag
        elif quantity_name == "wave_damping":
            res = rho * g * rad_coef.real
        
        if output_ref_point is not None:
            for ihead, head in enumerate(rad_coef.heading):
                for ifreq, freq in enumerate(rad_coef.frequency):
                    res.values[ihead,ifreq,:,:] = matrans3( res.values[ihead,ifreq,:,:] , origin = pressure_mesh.getRefPoint() , destination = output_ref_point )
                    

    # Excitation, froude_krylov, diffraction
    elif quantity_name[:10] in ["excitation","incident_l","diffractio"]:
        if quantity_name.startswith("excitation"):
            coef = pressure_mesh.get_excitation_force()
        elif quantity_name.startswith("incident_l"):
            coef = pressure_mesh.get_froude_krylov_force()
        elif quantity_name.startswith("diffraction"):
            coef = pressure_mesh.get_diffraction_force()
        else:
            raise ValueError(f"Confusing name: {quantity_name}")
        res =  coef*rho*g
        if output_ref_point is not None:
            for ihead, head in enumerate(coef.heading):
                for ifreq, freq in enumerate(coef.frequency):
                    res.values[ihead,ifreq,:,] = vectran3( res.values[ihead,ifreq,:] , origin = pressure_mesh.getRefPoint() , destination = output_ref_point )

        if quantity_name.endswith("re"):
            res = res.real
        elif quantity_name.endswith("im"):
            res = res.imag
    else: 
        raise NotImplementedError(f"Can't extract {quantity_name} from Snoopy mesh object!")
    return res

    

class InternalLoad():

    def __init__(self, pressure_mesh, allsections, mcn_coef, speed, rho ):
        """Class that handles internal loalds calculation.

        For now the motion equation it includes the resolution of the motion equation.s

        Parameters
        ----------
        pressure_mesh : Mesh
            The mesh, with decomposed pressure data.
        allsections : AllSection.
            The sectional inertia
        speed : float
            The ship speed.
        rho : float
            Water density.
        user_damping : None or xarray.DataArray.
            User damping (imode, jmode, ifreq, ihead)
        user_stiffness : None or xarray.DataArray
            User stiffness (imode, jmode).
            
        Note
        ---- 
        The user damping can depends on frequency/heading. this is typically the case when quadratic damping is linearized in regular waves.
        """

        self.allsections = allsections

        # In the future this can be changed in case allsections define section in Y direction.        
        cut_normal  =  np.array([1.,0.,0.])
        
        # Radiated pressure in mesh are always for unit motion expressed at CoB.
        cob = pressure_mesh.integrate_cob()
        pressure_mesh.setRefPoint(cob)
        
        
        # Integrate ship hydrodynamic coefficent, this will be output at CoB
        rdf_coef = get_rdfcoef_from_mesh( pressure_mesh = pressure_mesh,  rho = rho, speed = speed, output_ref_point = cob)
        
        mcn_input = allsections.get_mcn_input()


        mcn_input_obj = mcn_input.isel( body=0,body_i=0,body_j=0 )

        global_cog_point = mcn_input_obj.cog.values
        
        # Move global properties to CoG
        rdf_coef = rdf_coef.hydro.get_at_ref_point(global_cog_point)
        
        # Attention, hardcoding nb_body = 1
        rdf_coef_sel  = rdf_coef.isel(body=0,body_i=0,body_j=0)
        
        # Compute motion: since compute motion is cheap, it will be always recompute here, 
        # even if it was already computed in hsmcn or hvmcn
        
        if mcn_coef is None : 
            self._mechanical_solver = MechanicalSolver( rdf_coef_obj = rdf_coef , mcn_input_obj = mcn_input )  # Remove from self after debugging is finished ?
            mcn_coef = self._mechanical_solver.solve(ref_frame = "body-fixed")
        else : 
            # Check consistency between mass in mcn_coef and AllSections
            # TODO
            pass
        
        zero_encfreq_range = mcn_coef.attrs["wzeroencfrq"] 
        logger.debug(f"zero_encfreq_range = {zero_encfreq_range}")
        

        self._motion = mcn_coef.motion
        # linear_system = self._mechanical_solver._linear_system
        
        
        # Get list of section
        sectionlist = allsections.sectionlist
        nsection = len(sectionlist)

        # Extract needed information from hydrodatabase:
        all_encounter_frequency = rdf_coef_sel.hydro.encounter_frequency
        all_heading             = rdf_coef_sel.heading
        all_frequency           = rdf_coef_sel.frequency
        nfreq = len(all_frequency)
        nhead = len(all_heading)

        # Check ship equibrium
        mass = float(mcn_input_obj.mcn.mass)
        volume = pressure_mesh.integrate_volume()
        
        # The volume is computed numerically--> There might be a miss match with mass
        # The correction factor here is to compensate this small integral value
        correction_factor = volume* rho /mass
        unbalance = abs(correction_factor-1.0)        
        if (unbalance > 1e-2):
            raise ValueError(f"Mass input = {mass:} is heavily unbalanced with "+
                             f"mass of displaced volume computed numerically {volume*rho:}")

        
        info = {"encounter_frequency"   : all_encounter_frequency.values, 
                "rho"                   : rho,
                "output_ref_point"      : global_cog_point  }

        # Allocate the internal forces
        total_force = np.zeros((nsection,nhead,nfreq,6), dtype=complex)

        
        for isection,section in tqdm(list(enumerate(sectionlist)), desc = "Computing internal loads"):

            cutted_mesh = pressure_mesh.getCutMesh( section.section_point, cut_normal)
            

            hydrostatic_hull_bf = rho * g * cutted_mesh.integrate_stiffness_matrix(ref_frame = "body-fixed", 
                                                                                   output_ref_point = global_cog_point)
            

            baseflow_stiffness = get_baseFlowStiffness_scaled_from_SnoopyMesh(cutted_mesh,rho, speed,
                                                                              ref_point=global_cog_point)
            
            # Integrate partial hydrodynamic coefficient.
            added_mass      = get_from_pressure_integration(cutted_mesh, "added_mass",  **info)
            wave_damping    = get_from_pressure_integration(cutted_mesh, "wave_damping",  **info)
            excitation      = get_from_pressure_integration(cutted_mesh, "excitation", **info)


            section_mass = section.inertia_matrix[0,0]
        
            gravity_stiffness = get_gravity_stiffness(  mass = section_mass, cog = section.CoG, 
                                                        ref_point = global_cog_point, 
                                                        ref_frame = "body-fixed" )

            stiffness_matrix_total = baseflow_stiffness + hydrostatic_hull_bf + gravity_stiffness
            
            selection = {"drop": True}
            for ifreq, freq in enumerate(all_frequency):
                selection["frequency"] = ifreq
                for ihead, head in enumerate(all_heading):
                    
                    
                    user_damping = mcn_coef.user_damping_matrix.sel(body_i=1, body_j=1, heading = head , frequency = freq ).values
                    
                    selection["heading"] = ihead
                    
                    we = all_encounter_frequency.sel(heading = head, 
                                                     frequency = freq).values

                    excitation_zeroencfreq_coef = CoefZeroFenc_freq_range( freq, we, zero_encfreq_range )

                    motion_sel = (-1 * self._motion).isel(body = 0, **selection).values
                    velocity        = 1j * we * motion_sel
                    acceleration    =  - we * we * motion_sel

                    # Stiffness like forces:
                    stiffness_force = np.matmul(stiffness_matrix_total  , motion_sel)
                    
                    # Damping like forces
                    damp_force = np.matmul(wave_damping.isel(**selection).values + user_damping * section.VIS44PC, velocity)
        
                    # Mass like force
                    amss_force = np.matmul(added_mass.isel(**selection).values, acceleration)
                    inertia_force = np.matmul(section.inertia_matrix, acceleration)
                    
                    # Excitation like force
                    excitation_force = excitation.isel(**selection).values * excitation_zeroencfreq_coef

                    lhs = amss_force + inertia_force + damp_force + stiffness_force 

                    # Total internal loads, moved section reference point
                    total_force[isection,ihead, ifreq,:] = vectran3( lhs + excitation_force , 
                                                                           origin = global_cog_point, 
                                                                           destination = section.section_point )

        self.internal_loads = total_force

        self._rdf_coef = rdf_coef


    def get_internal_loads_ds(self) :
        """Return internal loads as xarray.Dataset
        """
        IDs = []
        section_points = []
        for s in self.allsections.sectionlist:
            IDs.append(s.ID)
            section_points.append(s.section_point)
        section_points = np.array(section_points)
        #IDs = np.array(IDs)
        rdf_coef = self._rdf_coef
        heading = rdf_coef.heading 
        frequency = rdf_coef.frequency
        mode = rdf_coef.mode
        attrs = rdf_coef.attrs
        ref_wave = rdf_coef.ref_wave.values
        attrs["ref_wave_X"] = ref_wave[0]
        attrs["ref_wave_Y"] = ref_wave[1]

        return xa.Dataset(
            data_vars = {"internal_loads": (["ID","heading","frequency","mode"],self.internal_loads[...]),
                         "section_points": (["ID","xyz"], section_points) },
            coords    = {"ID"       : ("ID"        , IDs),
                         "xyz"      : ("xyz",  ["x","y","z"]),
                         "heading"  : heading,  
                         "frequency": frequency,
                         "mode"     : mode },
            attrs     = attrs) 


        

    def get_motion_da(self) :
        """Return motion as xarray.DataArray
        """
        return self._motion

    
    def write(self,filename):
        """Write internal into HDF format
        """
        logger.info(f"Save internal load data to : {filename}")
        write_xarray(self.get_internal_loads_ds(),filename)        

