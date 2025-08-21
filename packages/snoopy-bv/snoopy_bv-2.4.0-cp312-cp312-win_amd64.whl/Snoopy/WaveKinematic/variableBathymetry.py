# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from Snoopy import Spectral as sp
from Snoopy import logger
import scipy.interpolate


class VariableBathymetry(object):


    def __init__(self, wrps, wdiff, heading,
                 x0=None, xmax=None, depthFunc=None,
                 x = None, depth = None,
                 nstep = 100, refWave=[0.,0.]):
        '''
        Creates VariableBathymetry object

        Parameters
        ----------
        wrps : np.ndarray
            frequency vector.
        wdiff : np.ndarray
            difference frequency vector.
        heading : np.ndarray
            heading vector in degree.
        x0 : float, optional
            x-coordinate for the bathymetry variation start.
        xmax : float, optional
            x-coordinate for the bathymetry variation end.
        depthFunc : function, optional
            function describing the bathymetry variation with x (h = f(x)).
        x : np.ndarray, optional
            x locations for variable bathymetry, should be defined if x0,
            xmax and depthFunc are None
        depth : np.ndarray, optional
            corresponding depths at x locations for variable bathymetry,
            should be defined if x0, xmax and depthFunc are None
        nstep : integer, optional
            number of steps for discretization. The default is 100.
        refWave : array, optional
            incident wave reference point. The default is [0.,0.].

        Returns
        -------
        None.

        '''

        # inputs

        self.nstep = nstep

        self.refWave = np.array(refWave)
        self.wrps = wrps
        self.wdiff = wdiff
        self.hdeg = np.array(heading)

        if depthFunc is None:
            x0 = x[0]
            xmax = x[-1]
            depthFunc = scipy.interpolate.interp1d(x,depth)

        self.x0   = x0
        self.xmax = xmax
        self.depthFunc = lambda x : depthFunc( np.clip(x,x0,xmax) )



        # constants
        self._deg2rad = np.pi/180.
        self._grav = 9.81

        # variables for 1st order computation
        self._npt  = nstep + 1
        self._x    = np.linspace(x0,xmax,self._npt)
        self._dx   = self._x[1] - self._x[0]

        self._depth = self.depthFunc(self._x)

        self._kL   = sp.w2k(self.wrps,self._depth[0])
        self._kR   = sp.w2k(self.wrps,self._depth[-1])
        self._cgL  = sp.w2Cg(self.wrps,self._depth[0])

        self._nw = len(self.wrps)

        self._head = self.hdeg * self._deg2rad
        self._nbhead   = len(self._head)
        self._sb = np.sin(self._head)
        self._cb = np.cos(self._head)

# ----------------------------------------------------------------------------

    def get_mesh_points(self):
        '''
        Get mesh x-coordiantes

        Returns
        -------
        np.ndarray
            mesh x-coordiantes.

        '''
        return self._x

# ----------------------------------------------------------------------------

    def get_depth(self, x = None ):
        '''
        Get local depth corresponding to mesh x-coordiantes

        Parameters
        ----------
        x : np.ndarray, optional
            x-coordiantes if None the mesh x-coordiantes are taken. The default is None.

        Returns
        -------
        np.ndarray
            local depth corresponding to x

        '''

        if x is None:
            return self._depth
        else:
            return self.depthFunc(x)


# ----------------------------------------------------------------------------

    def plot_bathymetry(self,ax=None,x=None,*args,**kwargs):
        '''
        Plots the varying bathymetry along x axis

        Parameters
        ----------
        ax : matplotlib axes object, optional
            axis of the current figure if None a new axis is created. The default is None
        x : np.ndarray, optional
            x-coordiantes if None the mesh x-coordiantes are taken. The default is None.
        *args :
            Options to pass to matplotlib plotting method.
        **kwargs :
            Options to pass to matplotlib plotting method.

        Returns
        -------
        ax : matplotlib axes object
            axis of the figure.

        '''

        if ax is None:
            fig,ax = plt.subplots()
        if x is None:
            x = self._x
        ax.plot(x,-self.depthFunc(x),*args,**kwargs)
        ax.set(title='bathymetry',
               xlabel='x [m]',
               ylabel='-h(x)')
        ax.grid(True)
        return ax

# ----------------------------------------------------------------------------

    def solve_first_order_problem(self):
        '''
        Solves first order potential for variable bathyemtry

        Returns
        -------
        None.

        '''

        logger.info('SOLVE FIRST-ORDER PROBLEM')
        logger.info('---------------------------------------------------')
        logger.info('> Compute first order wave kinematics for the first wave (w1)')
        kinematics  = self.first_order_kinematics(x = self._x)
        self._k     = kinematics['wave_number']
        self._nu    = kinematics['x-wave_number']
        self._cg    = kinematics['group_velocity']
        self._amp   = kinematics['amplitude']

        # integrated value of nu
        self._nusum         = np.zeros(self._nu.shape)
        #self._nusum[:,:,1:] = np.cumsum(self._nu[:,:,:-1], axis = 2 )*self._dx
        # forward
        self._nusum[:,:,1:] = np.cumsum(self._nu[:,:,1:], axis = 2 )*self._dx

        # variables for 2nd order computation
        self._ndw = len(self.wdiff)
        self._w1  = self.wrps
        self._w2  = self.wrps.reshape(-1,1) + self.wdiff.reshape(1,-1)
        #self._w2  = self.wrps.reshape(-1,1) - self.wdiff.reshape(1,-1)

        self._k2   = np.empty((self._nw,self._ndw,self._npt))
        self._nu2  = np.empty((self._nw,self._ndw,self._nbhead,self._npt))
        self._cg2  = np.empty((self._nw,self._ndw,self._npt))
        self._amp2 = np.empty((self._nw,self._ndw,self._nbhead,self._npt))

        km  = np.empty((self._nw,self._ndw))
        self._kmx = np.empty((self._nw,self._ndw,self._nbhead))
        self._kmy = np.empty((self._nw,self._ndw,self._nbhead))

        logger.info('> Compute first order wave kinematics for the second wave (w2)')
        for iw in range(self._ndw):
            kinematics =  self.first_order_kinematics(x = self._x, wrps = self._w2[:,iw])
            self._k2[:,iw,:]      = kinematics['wave_number']
            self._nu2[:,iw,:,:]   = kinematics['x-wave_number']
            self._cg2[:,iw,:]     = kinematics['group_velocity']
            self._amp2[:,iw,:,:]  = kinematics['amplitude']
            #km[:,iw]        = self._kL - self._k2[:,iw,0]
            km[:,iw]        = -self._kL + self._k2[:,iw,0]
        self._kmx = (km.T * self._cb.reshape(1,1,-1).T).T
        self._kmy = (km.T * self._sb.reshape(1,1,-1).T).T

        self._km = km

        self._nu2sum           = np.zeros(self._nu2.shape)
        #self._nu2sum[:,:,:,1:] = np.cumsum(self._nu2[:,:,:,:-1], axis = 3 )*self._dx
        #forward
        self._nu2sum[:,:,:,1:] = np.cumsum(self._nu2[:,:,:,1:], axis = 3 )*self._dx

        kinematics  = self.first_order_kinematics(x = self._x, wrps = self.wdiff )
        self._kd    = kinematics["wave_number"]

        self._mu    = (self._kd.reshape(1,self._ndw,1,-1)**2 - self._kmy[:,:,:,np.newaxis]**2).astype('complex')**0.5

        logger.info('---------------------------------------------------\n')

# ----------------------------------------------------------------------------

    def first_order_kinematics(self , x , wrps= None):
        '''
        Computes first order wave kineamatics (amplitude, wave-number,...)
        for a varying bathymertry at differnt x locations

        Parameters
        ----------
        x : np.ndarray
            x coordinates.
        wrps : np.ndarray, optional
            frequency vector, if None it is defined as wrps used to create the
            object. The default is None.

        Returns
        -------
        kinematics : dict
            dictionnary where stored kinematics properties. The results include
            - depth : depth at x
            - wave_number : wave number supposing constant depth at x
            - x-wave_number : wave number along x direction
            - group_velocity : group velocity at x
            - amplitude : wave amplitude at x
        '''

        npt   = len(x)

        if wrps is None:
            w = self.wrps
        else:
            w = wrps

        nw  = len(w)

        k     = np.empty((nw,npt))
        nu    = np.empty((nw,self._nbhead,npt))
        cg    = np.empty((nw,npt))
        amp   = np.empty((nw,self._nbhead,npt))

        depth = self.depthFunc(x)

        k0  = sp.w2k(w,self._depth[0])
        cg0 = sp.w2Cg(w,self._depth[0])

        ratio = np.empty((nw))

        for ipt in range(len(x)):
            k[:,ipt]      = sp.w2k(w,depth[ipt])
            cg[:,ipt]     = sp.w2Cg(w,depth[ipt])
            nu[:,:,ipt]   = np.sqrt( k[:,ipt].reshape(-1,1)**2 - k0.reshape(-1,1)**2 * self._sb.reshape(1,-1)**2 )
            # deal with zero freq
            for iw in range(nw):
                if k[iw,ipt]*depth[ipt] < 1e-4:
                    ratio[iw] = (depth[ipt] / self._depth[0])
                else:
                    ratio[iw] = np.tanh(k[iw,ipt]*depth[ipt]) / np.tanh(k0[iw]*self._depth[0])
            konu = np.sqrt(1.- ratio.reshape(-1,1)**2 * self._sb.reshape(1,-1)**2)

            amp[:,:,ipt]  = np.sqrt( cg0/cg[:,ipt]).reshape(-1,1) * \
                            np.sqrt( self._cb.reshape(1,-1)/konu )
            '''
            amp[:,:,ipt]  = np.sqrt( cg0/cg[:,ipt] * k[:,ipt] ).reshape(-1,1) * \
                            np.sqrt( self._cb.reshape(1,-1)/nu[:,:,ipt] )
            '''

        kinematics = {}
        kinematics['depth'] = depth
        kinematics['wave_number'] = k
        kinematics['x-wave_number'] = nu
        kinematics['group_velocity'] = cg
        kinematics['amplitude'] = amp

        return kinematics

# ----------------------------------------------------------------------------

    def second_order_particular(self):
        """
        Solves second order potential for variable bathyemtry (particular part)

        Returns
        -------
        A : np.ndarray
            slope.
        B : np.ndarray
            intercept.

        """
        from Snoopy.WaveKinematic.bathymetry_utils import F1, F2

        psi_1 = np.empty((self._nw,self._nbhead,self._npt))

        psi_2 = np.empty((self._nw,self._ndw,self._nbhead,self._npt))

        tmp   = self._cb*(self.x0-self.refWave[0])

        psi_1 = self._nusum + self._kL.reshape(-1,1,1) * tmp.reshape(1,self._nbhead,1)

        F     = np.empty((self._nw,self._ndw,self._nbhead,self._npt),dtype=complex)

        for idw in range(self._ndw):
            psi_2[:,idw,:,:] = self._nu2sum[:,idw,:,:] + self._k2[:,idw,0].reshape(-1,1,1) * tmp.reshape(1,self._nbhead,1)


        for iw in range(self._nw):
            for idw in range(self._ndw):
                for ipt in range(self._npt):
                    F[iw,idw,:,ipt] =  F1(w2 = self.wrps[iw],
                                          w1 = self._w2[iw,idw],
                                          k2 = self._k[iw,ipt],
                                          k1 = self._k2[iw,idw,ipt],
                                          grav  = self._grav)

                    for ib in range(self._nbhead):
                        F[iw,idw,ib,ipt] = F[iw,idw,ib,ipt] + \
                                           F2(w2 = self.wrps[iw],
                                              w1 = self._w2[iw,idw],
                                              k2 = self._kL[iw],
                                              k1 = self._k2[iw,idw,0],
                                              nu2 = self._nu[iw,ib,ipt],
                                              nu1 = self._nu2[iw,idw,ib,ipt],
                                              sb  = self._sb[ib],
                                              h   = self._depth[ipt],
                                              h0  = self._depth[0],
                                              grav = self._grav)

        A = np.empty((self._nw,self._ndw,self._nbhead,self.nstep),dtype=complex)
        B = np.empty((self._nw,self._ndw,self._nbhead,self.nstep),dtype=complex)

        logger.info('> Compute integration constants for particular part')
        for iw in range(self._nw):
            for idw in range(self._ndw):
                logger.debug(f'w = {self.wrps[iw]:2.3} [rad/s]\t-\tdw = {self.wdiff[idw]:2.3} [rad/s]')
                for ipt in range(self.nstep):
                    for ib in range(self._nbhead):
                        phase1 = np.exp( 1j*(-psi_1[iw,ib,ipt] + psi_2[iw,idw,ib,ipt]) )
                        a12    = 1j * self._amp[iw,ib,ipt] * self._amp2[iw,idw,ib,ipt]
                        B[iw,idw,ib,ipt] =  a12 * F[iw,idw,ib,ipt] * phase1
                        phase1 = np.exp( 1j*(-psi_1[iw,ib,ipt+1] + psi_2[iw,idw,ib,ipt+1]) )
                        a12    = 1j * self._amp[iw,ib,ipt+1] * self._amp2[iw,idw,ib,ipt+1]
                        A[iw,idw,ib,ipt] =  ( a12 * F[iw,idw,ib,ipt+1] * phase1 - B[iw,idw,ib,ipt] ) / self._dx

                        denom = (self._grav*self._kmy[iw,idw,ib]*np.tanh(self._kmy[iw,idw,ib]*self._depth[ipt+1]) - self.wdiff[idw]**2 )
                        A[iw,idw,ib,ipt] = A[iw,idw,ib,ipt] / denom
                        B[iw,idw,ib,ipt] = B[iw,idw,ib,ipt] / denom
        logger.info('Done')
        return A, B

# ----------------------------------------------------------------------------

    def second_order_homogenous(self,a,b):
        '''
        Solves second order potential for variable bathyemtry (homogenous part)

        Parameters
        ----------
        a : np.ndarray
            slope.
        b : np.ndarray
            intercept.

        Returns
        -------
        C : np.ndarray
            integration constant for exp(1j*mu*dx) term.
        D : np.ndarray
            integration constant for exp(-1j*mu*dx) term.
        '''

        from Snoopy.WaveKinematic.bathymetry_utils import integrate_fz, qm

        C = np.empty((self._nw,self._ndw,self._nbhead,self.nstep),dtype=complex)
        D = np.empty((self._nw,self._ndw,self._nbhead,self.nstep),dtype=complex)

        logger.info('> Compute integration constants for homogeneous part')
        for iw in range(self._nw):
            for idw in range(self._ndw):
                logger.debug(f'w = {self.wrps[iw]:2.3} [rad/s]\t-\tdw = {self.wdiff[idw]:2.3} [rad/s]')
                for ib in range(self._nbhead):
                    h1 = self._depth[0]
                    h2 = self._depth[1]
                    phase = np.exp(1j*self._km[iw,idw]*(self.x0-self.refWave[0]))
                    #phase = np.exp(1j*self._kmx[iw,idw,ib]*(self.x0-self.refWave[0]))
                    # potential continuity
                    I_hh = integrate_fz(k1 = self._kd[idw,1], k2 = self._kd[idw,1],
                                        h1 = h2,  h2 = h2 ,
                                        d  = h2)
                    I_hm = integrate_fz(k1 = self._kd[idw,1], k2 = self._km[iw,idw],
                                        h1 = h2,  h2 = h1,
                                        d = h2)
                    I_hp = integrate_fz(k1 = self._kd[idw,1], k2 = self._kmy[iw,idw,ib],
                                        h1 = h2,  h2 = h2,
                                        d = h2)
                    q0 = qm(w2= self.wrps[iw], w1= self._w2[iw,idw],
                            kh2=self._k[iw,0]*h1,kh1=self._k2[iw,idw,0]*h1,dbeta=0.)

                    rhs_p = (-1j*q0*I_hm*phase - b[iw,idw,ib,0]*I_hp)/I_hh

                    # velocity continuity
                    I_hh = integrate_fz(k1 = self._kd[idw,0], k2 = self._kd[idw,1],
                                        h1 = h1,  h2 = h2 ,
                                        d  = h2)
                    I_hm = integrate_fz(k1 = self._kd[idw,0], k2 = self._km[iw,idw],
                                        h1 = h1,  h2 = h1,
                                        d = h1)
                    I_hp = integrate_fz(k1 = self._kd[idw,0], k2 = self._kmy[iw,idw,ib],
                                        h1 = h1,  h2 = h2,
                                        d = h2)

                    rhs_m = (q0*I_hm*self._km[iw,idw]*phase - a[iw,idw,ib,0]*I_hp)/(1j*I_hh*self._mu[iw,idw,ib,1])
                    #rhs_m = (q0*I_hm*self._kmx[iw,idw,ib]*phase - a[iw,idw,ib,0]*I_hp)/(1j*I_hh*self._mu[iw,idw,ib,1])

                    C[iw,idw,ib,0] = 0.5*(rhs_p+rhs_m)
                    D[iw,idw,ib,0] = 0.5*(rhs_p-rhs_m)

                    for ipt in range(1,self.nstep):
                        h1 = self._depth[ipt]
                        h2 = self._depth[ipt+1]
                        phase = 1j*self._mu[iw,idw,ib,ipt]*self._dx
                        # potential continuity
                        I_hh1 = integrate_fz(k1 = self._kd[idw,ipt+1], k2 = self._kd[idw,ipt+1],
                                             h1 = h2,  h2 = h2 ,
                                             d  = h2)
                        I_hp1 = integrate_fz(k1 = self._kd[idw,ipt+1], k2 = self._kmy[iw,idw,ib],
                                             h1 = h2,  h2 = h2 ,
                                             d  = h2)
                        I_hh  = integrate_fz(k1 = self._kd[idw,ipt+1], k2 = self._kd[idw,ipt],
                                             h1 = h2,  h2 = h1 ,
                                             d  = h2)
                        I_hp  = integrate_fz(k1 = self._kd[idw,ipt+1], k2 = self._kmy[iw,idw,ib],
                                             h1 = h2,  h2 = h1 ,
                                             d  = h2)
                        rhs_p  = ( a[iw,idw,ib,ipt-1]*self._dx + b[iw,idw,ib,ipt-1] )*I_hp
                        rhs_p += ( C[iw,idw,ib,ipt-1]*np.exp(+phase) + D[iw,idw,ib,ipt-1]*np.exp(-phase) ) * I_hh
                        rhs_p -= b[iw,idw,ib,ipt] * I_hp1
                        rhs_p  = rhs_p / I_hh1
                        # velocity continuity
                        I_hh1 = integrate_fz(k1 = self._kd[idw,ipt], k2 = self._kd[idw,ipt+1],
                                             h1 = h1,  h2 = h2 ,
                                             d  = h2)
                        I_hp1 = integrate_fz(k1 = self._kd[idw,ipt], k2 = self._kmy[iw,idw,ib],
                                             h1 = h1,  h2 = h2 ,
                                             d  = h2)
                        I_hh  = integrate_fz(k1 = self._kd[idw,ipt], k2 = self._kd[idw,ipt],
                                             h1 = h1,  h2 = h1 ,
                                             d  = h1)
                        I_hp  = integrate_fz(k1 = self._kd[idw,ipt], k2 = self._kmy[iw,idw,ib],
                                             h1 = h1,  h2 = h1 ,
                                             d  = h1)
                        rhs_m  =  (a[iw,idw,ib,ipt-1] * I_hp - a[iw,idw,ib,ipt] * I_hp1)
                        rhs_m +=  1j*self._mu[iw,idw,ib,ipt] * ( C[iw,idw,ib,ipt-1]*np.exp(+phase) - D[iw,idw,ib,ipt-1]*np.exp(-phase) ) * I_hh
                        rhs_m  = rhs_m / (1j*self._mu[iw,idw,ib,ipt+1]*I_hh1)
                        C[iw,idw,ib,ipt] = 0.5*(rhs_p + rhs_m)
                        D[iw,idw,ib,ipt] = 0.5*(rhs_p - rhs_m)
        logger.info('Done')
        return C,D

# ----------------------------------------------------------------------------


    def solve_second_order_problem(self):
        '''
        Solves second order potential for variable bathyemtry

        Returns
        -------
        None.

        '''
        logger.info('SOLVE SECOND-ORDER PROBLEM')
        logger.info('---------------------------------------------------')
        # local part
        self.a, self.b = self.second_order_particular()

        # homogenous part
        self.c, self.d = self.second_order_homogenous(self.a, self.b)
        logger.info('---------------------------------------------------\n')

    def get_second_order_potential_mesh(self,cp=1.0,ch=1.0):
        '''
        Computes second order potential for mesh points

        cp : float, optional
            particular part coefficient. Default is 1.0
        ch : float, optional
            homogenous part coefficient. Default is 1.0

        Returns
        -------
        p : np.ndarray
            second order potential, shape=(nw,ndw,nbhead,npt).

        '''

        p = np.empty((self._nw,self._ndw,self._nbhead,self._npt),dtype=complex)

        for iw in range(self._nw):
            for idw in range(self._ndw):
                for ipt in range(self._npt-1):
                    p[iw,idw,:,ipt] = cp*self.b[iw,idw,:,ipt]
                # last point
                p[iw,idw,:,-1] = cp*(self.a[iw,idw,:,-1]*self._dx + self.b[iw,idw,:,-1])

        for iw in range(self._nw):
            for idw in range(self._ndw):
                for ipt in range(self._npt-1):
                    p[iw,idw,:,ipt] = p[iw,idw,:,ipt] + ch*(self.c[iw,idw,:,ipt] + self.d[iw,idw,:,ipt])
                # last point
                p[iw,idw,:,-1] = p[iw,idw,:,-1] + ch*(self.c[iw,idw,:,-1]*np.exp(1j*self._mu[iw,idw,:,-1]*self._dx) + \
                                 self.d[iw,idw,:,-1]*np.exp(-1j*self._mu[iw,idw,:,-1]*self._dx))
        return p

# ----------------------------------------------------------------------------

    def get_second_order_potential_flat_mesh(self):
        '''
        Computes second order potential for mesh points


        Returns
        -------
        p : np.ndarray
            second order potential, shape=(nw,ndw,nbhead,npt).

        '''
        from Snoopy.WaveKinematic.bathymetry_utils import qm
        p = np.empty((self._nw,self._ndw,self._nbhead,self._npt),dtype=complex)
        h1 = self._depth[0]
        for iw in range(self._nw):
            for idw in range(self._ndw):
                for ipt in range(self._npt):
                    xdiff = self._x[ipt] - self.refWave[0]
                    ydiff = 0.00 - self.refWave[1]
                    q0 = qm(w2 = self.wrps[iw]   , w1= self._w2[iw,idw],
                            kh2= self._k[iw,0]*h1, kh1=self._k2[iw,idw,0]*h1, dbeta=0.)
                    p[iw,idw,:,ipt]  = -1j*q0*np.exp(1j*self._kmx[iw,idw,:]*xdiff + 1j*self._kmy[iw,idw,:]*ydiff)
        return p


# ----------------------------------------------------------------------------

    def get_second_order_potential_flat(self, points):
        '''
        Computes second order potential for mesh points

        Returns
        -------
        p : np.ndarray
            second order potential, shape=(nw,ndw,nbhead,npt).

        '''

        from Snoopy.WaveKinematic.bathymetry_utils import qm, fz

        npt = points.shape[0]
        x,y,z  = points.T

        p = np.empty((self._nw,self._ndw,self._nbhead, npt),dtype=complex)
        h1 = self._depth[0]
        for iw in range(self._nw):
            for idw in range(self._ndw):
                for ipt in range(npt):
                    xdiff = x[ipt] - self.refWave[0]
                    ydiff = y[ipt] - self.refWave[1]
                    f0 = fz(z[ipt],self._km[iw,idw],h1)
                    q0 = qm(w2 = self.wrps[iw]   , w1= self._w2[iw,idw],
                            kh2= self._k[iw,0]*h1, kh1=self._k2[iw,idw,0]*h1, dbeta=0.)
                    p[iw,idw,:,ipt]  = -1j*q0*f0*np.exp(1j*self._kmx[iw,idw,:]*xdiff + 1j*self._kmy[iw,idw,:]*ydiff)
        return p

# ----------------------------------------------------------------------------

    def get_second_order_potential(self,points,cp=1.0,ch=1.0):
        '''
        Computes second order potential for given points

        Parameters
        ----------
        points : np.ndarray
            points, shape=(npt,3) with npt number of points.
        cp: float, optional
        particular part coefficient. Default is 1.0
        ch: float, optional
        homogenous part coefficient. Default is 1.0


        Returns
        -------
        p : TYPE
            second order potential, shape=(nw,ndw,nbhead,npt).

        '''
        from Snoopy.WaveKinematic.bathymetry_utils import fz

        npt = points.shape[0]
        x,y,z  = points.T


        p = np.empty((self._nw,self._ndw,self._nbhead,npt),dtype=complex)

        for ipt in range(npt):

            ix0 = np.where( x[ipt] >= self._x[:-1],True,False)
            ix1 = np.where( x[ipt] <= self._x[1:],True,False)
            ix  = np.where(ix0*ix1)[0][0]

            xdiff = x[ipt]-self._x[ix]
            ydiff = y[ipt]-self.refWave[1]

            for iw in range(self._nw):
                for idw in range(self._ndw):
                    # particular part
                    fp  =  np.array( [ fz(z=z[ipt],k=k,h=self._depth[ix+1]) for k in self._kmy[iw,idw,:] ])
                    pp  = (self.a[iw,idw,:,ix]*xdiff + self.b[iw,idw,:,ix])*fp
                    # homogeneous part
                    fh  =  fz(z=z[ipt],k=self._kd[idw,ix+1],h=self._depth[ix+1])
                    phase = self._mu[iw,idw,:,ix+1]*xdiff
                    ph  = (self.c[iw,idw,:,ix]*np.exp(1j*phase) + self.d[iw,idw,:,ix]*np.exp(-1j*phase))*fh
                    # total
                    phase = self._kmy[iw,idw,:]*ydiff
                    p[iw,idw,:,ipt] = (cp*pp + ch*ph)*np.exp(1j*phase)
        return p

    def get_correction_factor(self, points=None, phase_degree = True):

        from Snoopy.WaveKinematic.bathymetry_utils import angle_measure

        if points is None:
            x = self.get_mesh_points()
            points = np.zeros(shape=(len(x),3))
            points[:,0] = x

        npt = points.shape[0]
        x,y,z  = points.T

        p_tot = self.get_second_order_potential(points)
        p_particular = self.get_second_order_potential(points,cp=1,ch=0)

        R = np.ones(shape=p_tot.shape,dtype=float)
        alpha = np.empty(shape=p_tot.shape,dtype=float)

        xdiff = self.x0 - self.refWave[0]
        for ipt in range(npt):
            ix0 = np.where( x[ipt] >= self._x[:-1],True,False)
            ix1 = np.where( x[ipt] <= self._x[1:],True,False)
            ix  = np.where(ix0*ix1)[0][0]

            ydiff = y[ipt] - self.refWave[1]

            for iw in range(self._nw):
                psi_1 = self._nusum[iw,:,ix] + self._nu[iw,:,ix+1]*(x[ipt]-self._x[ix]) \
                      + self._kL[iw]*(xdiff*self._cb + ydiff*self._sb)
                for idw in range(self._ndw):
                    kx  = self._nu[iw,:,ix+1] - self._nu2[iw,idw,:,ix+1]
                    km  = np.sqrt(kx**2+self._kmy[iw,idw,:]**2)
                    denom1 = (self._grav*self._kmy[iw,idw,:]*np.tanh(self._kmy[iw,idw,:]*self._depth[ix+1]) - self.wdiff[idw]**2 )
                    denom2 = (self._grav*km*np.tanh(km*self._depth[ix+1]) - self.wdiff[idw]**2 )
                    phase_p = np.angle(p_tot[iw,idw,:,ipt])
                    p_particular[iw,idw,:,ipt] = p_particular[iw,idw,:,ipt] * (denom1/denom2)
                    psi_2 = self._nu2sum[iw,idw,:,ix] + self._nu2[iw,idw,:,ix+1]*(x[ipt]-self._x[ix]) \
                          + self._k2[iw,idw,0]*(xdiff*self._cb + ydiff*self._sb)
                    alpha[iw,idw,:,ipt] = angle_measure( phase_p - (-psi_1 + psi_2) )
                    alpha[iw,idw,:,ipt] = angle_measure(alpha[iw,idw,:,ipt] - 0.5*np.pi)



        p_particular_greater_zero_index = np.where(np.abs(p_particular) > 1.0e-6)
        R[p_particular_greater_zero_index] = np.abs( p_tot[p_particular_greater_zero_index] / p_particular[p_particular_greater_zero_index] )
        if phase_degree : alpha = alpha / self._deg2rad

        return R, alpha

# ----------------------------------------------------------------------------

def check_second_order_flat(tol, x0 = 1., depth = 3., w_min = 0.5, w_max = 15, wdif = 0.1, refWave = [0., 0.], plot = False):
    r"""
    This function calculates the second order potential using Snoopy.WaveKinematic Wave Kinematic for a constant depth
    and using Snoopy.WaveKinematic.VariableBathymetry with a constant depth distribution and returns whether two methods
    produce the 'same' results with given tolerance
        tol     : tolerance. all values by both methods should provide the error less than the tolerance. |\phi_inc_VB_flat/\phi_inc_flat -1| < tol.
                  consider tol * 100% is the tolerance in percents
        x0      : starting point for x coordinate of the bottom distribution. For the test x = [x0, x0+2]
        depth   : is the depth of the channel. For the test d = [depth, depth]
        w_min   : minimum frequency in rad/s
        w_max   : maximum frequency in rad/s
        wdif    : frequencies distribution step. w_n+1 = w_n +wdif
        refWave : wave's reference point
        plot    : if True, the real + imaginary and module are plotted
    """
    from Snoopy import WaveKinematic as wk
    from Snoopy import Spectral as sp
    logger.info(f"Second Order check for a flat bottom of depth {depth:}m.")
    logger.info(f"    bathymetry starting point x0 = {x0:}")
    logger.info(f"    w_min = {w_min:}")
    logger.info(f"    w_max = {w_max:}")
    logger.info(f"    dw    = {wdif:}")
    logger.info(f"    wave's heading is 0°")
    logger.info(f"    wave's reference point : ({refWave[0]:}, {refWave[1]:})")
    logger.info(f"Continuity of the velocity potential is checked at ({x0:}, 0.0, 0.0)")

    # Point at which we calculate the Incident Velocity Potential
    pts = np.array([[x0, 0.0, 0.0], ])
    # Incident wave Reference Point
    refWave = np.array( refWave )

    # Heading of the Incident Wave
    headings = np.array([ 0.0 ])

    # Water depth and depth distribution
    x = np.array([ x0, x0+2. ])             # x_0, x_max
    d = np.array([ depth, depth])

    # frequency range
    wrps = np.arange(w_min, w_max +wdif, wdif)
    # frequencies differencies
    wdif = np.array( [wdif ] )

    bathy = VariableBathymetry(
        x = x,
        depth   = d,
        wrps    = wrps,
        wdiff   = wdif,
        heading = headings,
        nstep   = 1,
        refWave = refWave
    )

    bathy.solve_first_order_problem()

    bathy.solve_second_order_problem()

    # -------------- Incident Velocity Potential using Snoopy.WaveKinematic.VariableBathymetry using the constant distribution of the bottom
    pp = bathy.get_second_order_potential(pts, cp = 1., ch = 1.)

#    # -------------- Incident Velocity Potential using Snoopy.WaveKinematic.VariableBathymetry for a constant depth ( h = h(x_0) )
#    pp_flat = bathy.get_second_order_potential_flat(pts)

    # -------------- Incident Velocity Potential using Snoopy.WaveKinematic
    wrps_wk = np.arange(w_min, w_max +wdif[0]*2, wdif[0])
    # 1. Creating Snoopy.Spectral.Wif
    amp = np.ones( (len(wrps_wk)) )                     # amplitudes of waves are 1.0
    phi = np.zeros( (len(wrps_wk)) )                    # initial waves phases are 0.0
    wif_heads = np.zeros( (len(wrps_wk)) )              # All waves
    wif_heads[:] = headings[0]                          # have the same direction 0.0°
    wif = sp.Wif(wrps_wk, amp, phi, wif_heads, depth)   # creating wif object
    # 2. Snoopy.WaveKinematic.SecondOrderKinematic based on the wif object
    wk2 = wk.SecondOrderKinematic(wif)
    Qi  = wk2.getQi(-1)                                 # getting Q/(g k^- tanh (k^- h) - (w_1 -w_2)^2      = Qi[ ifreq, idiff ]
    #Wi  = wk2.getWi(-1)
    #Ki  = wk2.getKi(-1)
    Kix = wk2.getKix(-1)                                # getting k^-_x = k_1 \cos \beta_1 -k_2 \cos\beta_2
    Kiy = wk2.getKiy(-1)                                # getting k^-_y = k_1 \sin \beta_1 -k_2 \sin\beta_2
    pp_exact = np.zeros( (len(wrps_wk)), dtype = complex)  # Allocating space
    # 3. Calculation the Velocity Potential
    for iw in range(len(wrps_wk)):
        # we need to conjugate, because Snoopy Wave Kinematic module calculates the lower triangular (w_1 < w_2, which can be seen from printing Wi)
        pp_exact[iw] = np.conj(1j *Qi[iw, 1] *np.exp(1j*(Kix[iw, 1]*(pts[0][0] -refWave[0]) +Kiy[iw, 1] *(pts[0][1] -refWave[1]))))

    if plot:
        k = wif.getWaveNumbers()
        kh = k *depth

        fig, ax = plt.subplots(2, 1)
        ax[0].plot(kh[:-1], pp[:,0,0,0].real, label = "VB.get_second_order_potential. Real")
        ax[0].plot(kh[:-1], pp_exact[:-1].real, label = "Flat bottom, using Snoopy.WaveKinematic. Real")
#        ax[0].plot(kh[:-1], pp_flat[:,0,0,0].real, label = "VB.get_second_order_potential_flat. Real")

        ax[1].plot(kh[:-1], pp[:,0,0,0].imag, label = "VB.get_second_order_potential. Imag")
        ax[1].plot(kh[:-1], pp_exact.imag[:-1], label = "Flat bottom, using Snoopy.WaveKinematic. Imag")
#        ax[1].plot(kh[:-1], pp_flat[:,0,0,0].imag, label = "VB.get_second_order_potential_flat. Imag")
        ax[0].legend()
        ax[0].grid()
        ax[0].set_xlabel("kh")
        ax[0].set_ylabel("$\\Re e\\phi^{(2)}$")
        ax[1].legend()
        ax[1].grid()
        ax[1].set_xlabel("kh")
        ax[1].set_ylabel("$\\Im m\\phi^{(2)}$")
        fig.set_size_inches(12.8, 9.6)
        plt.show()

        fig, ax = plt.subplots()
        ax.plot(kh[:-1], np.abs(pp[:, 0, 0, 0]), label = "sqrt VB.get_second_order_potential. Abs")
        ax.plot(kh[:-1], np.abs(pp_exact[:-1]), label = "Flat bottom, using Snoopy.WaveKinematic. Abs")
#        ax.plot(kh[:-1], np.abs(pp_flat[:,0,0,0]), label = "Flat bottom, VB.WaveKinematic. Abs")
        ax.legend()
        ax.grid()
        ax.set_xlabel("kh")
        ax.set_ylabel("$|\\phi^{(2)}|$")
        fig.set_size_inches(12.8, 9.6)
        plt.show()

    res_VB_abs = np.abs(pp[:,0,0,0])
    res_in_abs = np.abs(pp_exact[:-1])
#    if not np.allclose(res_VB_abs, res_in_abs, rtol = 1.2e-2):
#        for iv, v in enumerate(np.isclose(res_VB_abs, res_in_abs)):
#            if not v:
#                print(res_VB_abs[iv], res_in_abs[iv], np.abs(res_VB_abs[iv]/res_in_abs[iv]-1.))
    return np.allclose(res_VB_abs, res_in_abs, rtol = tol)

# ----------------------------------------------------------------------------

if "__main__" == __name__:

    plt.close("all")

    # input example ----------------------------------------------------------

    x0 = 0.0
    xmax = 100.0
    h0 = 30

    slope = 20./100.
    depthFunc = lambda x : -slope*(x-x0) + h0

    wmin = 0.1
    wmax = 2.00
    wstep = 0.1
    wrps = np.arange(wmin,wmax+wstep,wstep)

    wdiff  = np.array([0.05,0.1,0.2])
    heading = [0.0,30.0]

    # ------------------------------------------------------------------------


