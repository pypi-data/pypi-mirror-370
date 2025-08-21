# -*- coding: utf-8 -*-

import os
import numpy as np
import xarray as xr
from Snoopy import logger
from .. import Spectral as sp
from . import g


def solve_for_motion(amplitude,heading,frequency,speed, 
                    encounter_frequency,
                    added_mass,mass_matrix, 
                    stiffness_matrix,
                    wave_damping, excitation,
                    zero_encfreq_range,
                    user_damping_matrix = None,
                    user_damping_matrix_rel = None, 
                    user_quadratic_damping  = None,
                    tol = 1e-3, itmax = 100):
    """Solve motions, single body, with input as simple numpy.

    all input are already at correct reference point.
    
    Return
    ------
    dict : 
        "motion" ( ihead, ifreq, imode )
    """
    
    if user_damping_matrix is None : 
        user_damping_matrix = np.zeros((6,6), dtype = float)
        
    
    linParam = 8./(3.*np.pi) * amplitude
    
    r1st = np.zeros( (len(heading), len(frequency), 6), dtype = 'complex' )
    
    nhead = len(heading)
    nfreq = len(frequency)

    user_damping_matrix_final = np.zeros((nhead, nfreq, 6,6), dtype = float)
    
    for i_head,headval in enumerate(heading):
        for i_freq,freqval in enumerate(frequency):
            
            f = encounter_frequency[i_head,i_freq]

            excitation_zeroencfreq_coef = CoefZeroFenc_freq_range( freqval, f, zero_encfreq_range )
            
            xtmp  = np.zeros(6,dtype = 'complex')
            error = 1.0
            it = 0
            
            M_Ma = added_mass[i_head, i_freq, : ,:] + mass_matrix 
            
            B_lin = user_damping_matrix.copy()

            if user_damping_matrix_rel is not None:
                bcr = 2.0 * np.sqrt( np.abs( M_Ma * stiffness_matrix ) )  # To check
                B_lin += 0.01 * user_damping_matrix_rel * bcr

            while ( error > tol and it <= itmax ) :
                it +=1

                Bq_eq = np.zeros((6,6))
                if user_quadratic_damping is not None:
                    for k in range(6):
                        Bq_eq[k,:] =  linParam * f * user_quadratic_damping[k,:] * np.abs( xtmp[k] )

                lhs = (- f**2 * M_Ma + 1j * f * ( wave_damping[i_head, i_freq, :, :] + Bq_eq + B_lin ) + stiffness_matrix )

                rhs = excitation[i_head, i_freq,:] *excitation_zeroencfreq_coef
                if excitation_zeroencfreq_coef<1:
                    logger.debug(f"Excitation before treatment: { excitation[i_head, i_freq,:]}")
                    
                    logger.debug(f"Excitation after treatment: {rhs}")

                r1st[i_head, i_freq, :] = np.linalg.solve(lhs ,rhs )
                if user_quadratic_damping is not None and error > tol:
                    error   =  np.abs(r1st[i_head, i_freq, :] - xtmp).max()
                    xtmp[:] = 0.9 * r1st[i_head, i_freq, :] + 0.1*xtmp[:]
                else:
                    break
                
            user_damping_matrix_final[i_head, i_freq, :, :] = Bq_eq + B_lin
                                        

    res_dict = {"motion": r1st, "user_damping_matrix_final" : user_damping_matrix_final}
    
    return res_dict

    
def get_gravity_stiffness(mass, cog, ref_point, ref_frame ):
    """Compute gravity stiffness.
    
    Parameters
    ----------
    cog : np.ndarray(3)
        Center of gravity
    ref_point : np.ndarray(3)
        Reference point
    mass : float
        Mass
    ref_frame : str
        Reference frame, among ["body-fixed", "hydro"].

    Returns
    -------
    np.ndarray
        return the 6*6 gravity stiffness matrix
    """

    gravity_stiffness  = np.zeros((6,6),dtype = float)
    
    GQ = ref_point - cog
    #logger.debug(f"GQ:{GQ}")
    if ref_frame == "body-fixed" :
        gravity_stiffness[0,4] = -1.0
        gravity_stiffness[1,3] = +1.0
        gravity_stiffness[3,3] = +GQ[2]
        gravity_stiffness[4,4] = +GQ[2]

        gravity_stiffness[5,3] = -GQ[0]
        gravity_stiffness[5,4] = -GQ[1]  # Signed opposed to the one in HydroStar++. 
    elif ref_frame == "hydro": 
        gravity_stiffness[3,3] = +GQ[2]
        gravity_stiffness[4,4] = +GQ[2]

        gravity_stiffness[3,5] = -GQ[0]
        gravity_stiffness[4,5] = -GQ[1]
    else : 
        raise(Exception())

    return gravity_stiffness * mass * 9.81
    


class MechanicalSolver:

    def __init__(self, mcn_input_obj, rdf_coef_obj):
        """Initialize object MechanicalSolver from mcn_input_obj and rdf_coef_obj
        
        Parameters
        ----------
        mcn_input_obj : McnInput
            Contain input formation for mechanical solver
            
        rdf_coef_obj : RdfCoef
            Contain hydrodynamic coefficients
        """
        
        self.mcn_input_obj = mcn_input_obj
        self.rdf_coef_obj  = rdf_coef_obj
        self._mcn_coef = None


    def solve(self, ref_points = None, ref_frame = "hydro" ):
        """Solves the mechanical equation.

        Parameters
        ----------
        ref_points : np.ndarray, optional
            Where the motion equation is written. The default is CoG
            .
        ref_frame : str, optional
            Reference frame in which the motion equation is solved. The default is "hydro".

        Returns
        -------
        McnCoef
            The motion equation results
        """
    
        logger.info('> Solve motion equation')

        speed   = self.rdf_coef_obj.speed
        head    = self.rdf_coef_obj.heading.data
        wrps    = self.rdf_coef_obj.frequency.data
        we      = self.rdf_coef_obj.hydro.encounter_frequency.data
        nb_body = self.rdf_coef_obj.nb_body
        
        if nb_body >1:
            raise NotImplementedError("This MechanicalSolver can't handle multibody calculation yet")

        # By default, write equation at CoG
        if ref_points is None : 
            ref_points = self.mcn_input_obj.cog.values

        ref_point = ref_points[0,:]

        # Set ref_point of rdf_coef_obj AND mcn_input_obj 
        mcn_input_obj = self.mcn_input_obj.hydro.get_at_ref_point( ref_points[0,:] )
        rdf_coef_obj = self.rdf_coef_obj.hydro.get_at_ref_point( ref_points[0,:] )
        
        amplitude = mcn_input_obj.attrs.get( "amplitude" , 1.0)

        # zero_encfreq_range took prority over zero_encfreq_option
        zero_encfreq_range = mcn_input_obj.attrs.get("wzeroencfrq") # zero_encfreq_range is required!

        # Attention, hardcoding nb_body = 1
        rdf_coef_obj_sel  = rdf_coef_obj.sel(body=1,body_i=1,body_j=1)
        mcn_input_obj_sel = mcn_input_obj.sel(body=1,body_i=1,body_j=1)

        cog_point = mcn_input_obj_sel.cog.values
        mass      = mcn_input_obj_sel.mcn.mass

        # Mass_matrix = mass_object.inertia_matrix
        mass_matrix = mcn_input_obj_sel.mass_matrix.data
        
        gravity_stiffness = np.zeros((6,6), dtype='float64')
        if ref_frame == "hydro" : 

            hydrostatic_hull    = rdf_coef_obj_sel.hydrostatic_hull.data 

            # Term not in hydrostatic_hull from hydrostar... 
            volume = mass
            buoyancy_stiffness = np.zeros((6,6), dtype='float64')
            buoyancy_stiffness[3,3] = (rdf_coef_obj.cob[0,2] - ref_point[2] ) * volume * g
            buoyancy_stiffness[4,4] = (rdf_coef_obj.cob[0,2] - ref_point[2] ) * volume * g

            # Add gravity stiffness
            gravity_stiffness[3,3] = ref_point[2] - cog_point[2] 
            gravity_stiffness[4,4] = ref_point[2] - cog_point[2]
            gravity_stiffness = gravity_stiffness * mass * g
            
            # Body is assumed in equilibrium at rest, so that buoyancy_stiffness and gravity_stiffness compensate each other for terms [3,5] and [4,5].

            # Total hydrostatic stiffness
            hydrostatic = hydrostatic_hull + gravity_stiffness + buoyancy_stiffness

        elif ref_frame == "body-fixed" :
            hydrostatic_hull_bf = rdf_coef_obj_sel.hydrostatic_hull_bf.data[:,:]
            gravity_stiffness = get_gravity_stiffness( mass, cog_point , ref_point , ref_frame  )
            hydrostatic = hydrostatic_hull_bf + gravity_stiffness
        else : 
            raise ValueError(f"Unavailable ref_frame {ref_frame}. Please choose between body-fixed or hydro.")

        # Stiffness from base flow
        if "base_flow_stiffness" in rdf_coef_obj_sel.data_vars : 
            K = hydrostatic + rdf_coef_obj_sel.base_flow_stiffness.values
        else: 
            K = hydrostatic

        excitation     = rdf_coef_obj_sel.excitation_load.values
        added_mass     = rdf_coef_obj_sel.added_mass.values
        wave_damping   = rdf_coef_obj_sel.wave_damping.values
        
        if hasattr(mcn_input_obj_sel,'user_stiffness_matrix'):
            K += mcn_input_obj_sel.user_stiffness_matrix.data

        # Quadratic damping
        user_quadratic_damping  = _unset_zeros_matrix(getattr(mcn_input_obj_sel,'user_quadratic_damping',None))

        user_damping_matrix_rel = _unset_zeros_matrix(getattr(mcn_input_obj_sel,'user_damping_matrix_rel',None))
        
        user_damping_matrix =  _unset_zeros_matrix(getattr(mcn_input_obj_sel,'user_damping_matrix',None))


        motion_solution = solve_for_motion(amplitude,head,wrps,speed, 
                    we,  added_mass,mass_matrix, K,
                    wave_damping, excitation,
                    zero_encfreq_range,
                    user_damping_matrix = user_damping_matrix,
                    user_damping_matrix_rel = user_damping_matrix_rel, 
                    user_quadratic_damping  = user_quadratic_damping,
                    tol = 1e-3, itmax = 100)

        motion = xr.DataArray( data = motion_solution["motion"][np.newaxis,:,:,:] ,
                               coords = [rdf_coef_obj.body, rdf_coef_obj.heading, rdf_coef_obj.frequency, rdf_coef_obj.mode] )
        
        user_damping_matrix =  xr.DataArray( data = motion_solution["user_damping_matrix_final"][np.newaxis,np.newaxis,:,:,:] ,
                               coords = [rdf_coef_obj.body_i, rdf_coef_obj.body_j, rdf_coef_obj.heading, rdf_coef_obj.frequency, rdf_coef_obj.mode_i, rdf_coef_obj.mode_j] )

        stiffness_matrix =  xr.DataArray( K[np.newaxis] , coords = (rdf_coef_obj["body"], rdf_coef_obj["mode_i"] , rdf_coef_obj["mode_j"]) )
        
        user_stiffness_matrix =  xr.DataArray( mcn_input_obj_sel.user_stiffness_matrix.data[np.newaxis] , coords = (rdf_coef_obj["body"], rdf_coef_obj["mode_i"] , rdf_coef_obj["mode_j"]) )


        # Construct the "mcn_coef" object

        # Return the data from rdf_coef_obj to the original ref_point
        # We add the motion and hydrostatic in object rdf_coef_obj so that they 
        # can be moved together with other data
        self._mcn_coef = rdf_coef_obj
        self._mcn_coef["motion"] = motion
        self._mcn_coef["hydrostatic"] = stiffness_matrix
        self._mcn_coef["cog"]   = mcn_input_obj.cog
        self._mcn_coef["mass_matrix"] = mcn_input_obj.mass_matrix
        self._mcn_coef["user_stiffness_matrix"] = user_stiffness_matrix
        self._mcn_coef["user_damping_matrix"] = user_damping_matrix
        self._mcn_coef.attrs["wzeroencfrq"] = zero_encfreq_range

        return self._mcn_coef

        
    @property
    def mcn_coef(self):
        if self._mcn_coef is None: 
            self.solve()

        return self._mcn_coef
    

    def get_linear_system(self) : 
        return self._linear_system


    def getWetModes(self):
        """
        Computes body wet frequencies and modes

        Returns
        -------
        None.
        """
        
        # TO CHECK
        raise(NotImplementedError)

        wr   = np.zeros( (len(self.head), len(self.wrps), 6))
        vect = np.zeros( (len(self.head), len(self.wrps), 6, 6))

        K = self.stiffness_matrix
        # solve eigenvalue problem for all frequencies and heading
        for i_head in range(len(self.head)):

            for i_freq in range(len(self.wrps)):

                M = self.added_mass[i_head, i_freq, : ,:] + self.massMatrix

                #Minv = np.linalg.inv(M)
                #matA = np.matmul( Minv , K + 0.01 * (EPS**2) * np.diag(M) )
                #w2, v = np.linalg.eig( matA )

                w2, v = eigh (a = K + 0.01 * (EPS**2) * np.diag(M) , b = M )


                wr[i_head, i_freq, :] = np.sqrt( np.abs(w2) )
                vect[ i_head , i_freq , : , :] = v.real


        wetFreq  = np.zeros(6)
        wetModes = np.zeros((6,6))

        # sort unique encounter frequencies
        x  = self.we[:,:].reshape(-1)
        xu, idu = np.unique( x , return_index = True )
        ids = np.argsort( xu )
        xs  = xu[ids]

        # compute wet frequencies and and wet modes
        for imod in range(6):

            # get eigenvalues
            yu   = wr[:,:,imod].reshape(-1)[idu]
            ys   = yu[ids]

            funcFreq = lambda w : interpolate.interp1d(xs, ys, bounds_error = False , fill_value = (ys[0], ys[-1] ) )(w) - w

            wetFreq[imod] = optimize.fsolve(func=funcFreq, x0 = xs[0])

            # get eigenvectors
            v  = vect[ : , : , : , imod].reshape(-1, vect.shape[-2]).T
            vu = v[:,idu]
            vs = vu[:,ids]

            funcVect = interpolate.interp1d( xs , vs , bounds_error = False , fill_value = (vs[:,0], vs[:,-1] ) )

            wetModes[:,imod] = funcVect( wetFreq[imod] )
            wetModes[:,imod] = wetModes[:,imod] / np.linalg.norm( wetModes[:,imod]  )


        # sort
        idmod    = np.argsort( wetFreq )
        wetFreq  = wetFreq[idmod]
        wetModes = wetModes[:,idmod]

        logger.debug('\n')
        logger.debug('----------------------------------------------------')
        logger.debug('WET FREQUENCIES AND MODES')
        logger.debug('----------------------------------------------------')
        for imod in range(6):
            logger.debug(f' > Wet mode : {imod+1}')
            logger.debug(f'Frequency : {wetFreq[imod]:.3f} (rad/s)')
            logger.debug('Decomposition:')
            logger.debug(f"{ np.array2string(wetModes[:,imod], formatter={'float_kind':'{0:.3f}'.format}) }")
            logger.debug('----------------------------------------------------')

        return wetFreq, wetModes


    def writeRaos(self, rao_path):
        """Write motions and hydrdoynamic forces RAOs.
        
        (after solving the mechanical equation).

        Parameters
        ----------
        path : string
            Raos output path

        Returns
        -------
        None.
        """
        def write_rao(cvalue):
            rao =  sp.Rao(b = np.deg2rad(self.head) ,
                          w = self.wrps,
                          cvalue = cvalue,
                          refPoint = self.cog_point,
                          waveRefPoint = np.array([0.,0.]), # to check in hydrostar-v
                          depth = self.depth,
                          forwardSpeed = self.speed,
                          modes = np.array([irao]),
                          rho = self.rho,
                          grav = self.grav )

            rao.write( rao_path + f'/{fname}' + '.rao' )

        if not os.path.exists(rao_path):
            os.mkdir(rao_path)

        data = {'fext': self.excitation,
                'motion': self.r1st,
                'cm': self.added_mass,
                'ca':self.wave_damping}

        for name, value in data.items():
            for imod in range(6):
                offset = 0
                if name in ['fext','motion']: # motion or excitation forces
                    cvalue = value[:,:,imod:imod+1]
                    if (name == 'motion' and imod > 2): # convert rotations to degree
                        cvalue = cvalue * np.rad2deg(1.)
                    if name == 'fext':
                        offset = 6
                    irao = imod + 1 + offset
                    fname = sp.modesIntToMode(irao).name.lower()
                    cvalue = -1j * np.conj(cvalue)
                    write_rao(cvalue)
                else: # hydrodynamic coefficients
                    for jmod in range(6):
                        cvalue = value[:,:,imod:imod+1,jmod]
                        irao = 0
                        fname = f'{name}_{imod+1}{jmod+1}'
                        write_rao(cvalue)



def _unset_zeros_matrix(matrix):
    """Return None if input matrix is zeros
    
    Return the input as is otherwise.

    Parameters
    ----------
    matrix : arraylike or None
        Input matrix

    Returns
    -------
    _type_
        _description_
    """
    
    if matrix is not None:
        if np.all(np.abs(matrix)<1e-15):
            return None
    return matrix


def CoefZeroFenc_freq_range( freq, fenc, zero_freq_range ):
    """Function to set the excitation to zero near the zero-encounter frequency.
    """
    if zero_freq_range == 0:
        return 1.0
    fenc4 = (fenc/zero_freq_range)**4
    CoefZeroFenc = 1.0
    if freq > zero_freq_range and np.abs(fenc) < zero_freq_range:
        CoefZeroFenc = 1.0- np.exp(-fenc4*14)

    return CoefZeroFenc