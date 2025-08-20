# -*- coding: utf-8 -*-

import numpy as np
from numba import jit

# ----------------------------------------------------------------------------

@jit(nopython=True)
def integrate_fz(k1:float,k2:float,h1:float,h2:float,d:float):
    kh1 = k1*h1
    kh2 = k2*h2
    khp = kh1 + kh2
    kd1 = k1*d
    kd2 = k2*d
    kdp = kd1 + kd2
    kdm = kd1 - kd2

    N   = (1.+np.exp(-2.*kh1))*(1.+np.exp(-2.*kh2))
    I1  = (1.- np.exp(-2*khp) - np.exp(-kdp) + np.exp(-2*khp+kdp))/(k1+k2)
    if abs(k1-k2) < 1e-6:
        I2 = d * ( np.exp(-2.*kh1) + np.exp(-2*kh2) )
    else:
        I2 = (np.exp(-2*kh2) - np.exp(-2.*kh1) - np.exp(-2*kh2-kdm) + np.exp(-2.*kh1+kdm)) / (k1-k2)
    return (I1 + I2)/N


@jit(nopython=True)
def qm(w1:float,w2:float,kh1:float,kh2:float,dbeta:float):
#def qm(w1,w2,kh1,kh2,dbeta):
    if w1<w2:
        return qm0(w1,w2,kh1,kh2,dbeta)
    else:
        return -qm0(w2,w1,kh2,kh1,dbeta)


@jit(nopython=True)
def qm0(w1:float,w2:float,kh1:float,kh2:float,dbeta:float):
#def qm0(w1,w2,kh1,kh2,dbeta):
    eps = 1E-6
    if w1 <eps:
        return 0.
    else:
        a = w1/w2
        cb = np.cos(dbeta)
        khm = np.sqrt(kh1**2 + kh2**2 - 2.*kh1*kh2*cb)
        t1 = np.tanh(kh1)
        t2 = np.tanh(kh2)
        t12 = t1*t2
        s1 = 2.*np.exp(-kh1) / ( 1.-np.exp(-2.*kh1) )
        s2 = 2.*np.exp(-kh2) / ( 1.-np.exp(-2.*kh2) )
        tm = np.tanh(khm)
        khm2 = khm/kh2

        q  = -0.5*(a**3*s1**2-s2**2) + a*(1-a)*( cb/t12 + 1. )
        q *= w2 / ( khm2*tm/t2 - (1.- a)**2 )

        return q

@jit(nopython=True)
def F1(w1:float,w2:float,k1:float,k2:float,grav:float):
    eps = 1E-6
    I1 = 0.
    I2 = 0.
    if w1>eps:
        I1 = (grav*k1)**2/w1
    if w2>eps:
        I2 = (grav*k2)**2/w2
    return -0.5*(w1**3 - w2**3 -  I1 + I2 )


@jit(nopython=True)
def F2(w1:float,w2:float,k1:float,k2:float,nu1:float,nu2:float,sb:float,h:float,h0:float,grav:float):

    eps  = 1E-6
    dw   = w1 - w2

    if w1 < eps:
        nuow1 = np.sqrt(grav*(1./h - 1./h0*sb**2))
        kow1  = np.sqrt(grav/h0)
    else:
        nuow1 = grav*nu1/w1
        kow1  = grav*k1/w1

    if w2 < eps:
        nuow2 = np.sqrt(grav*(1./h - 1./h0*sb**2))
        kow2  = np.sqrt(grav/h0)
    else:
        nuow2 = grav*nu2/w2
        kow2  = grav*k2/w2

    nu12 = nuow1*nuow2
    k12  = kow1*kow2
    w12  = w1*w2

    #return 1j * dw * (  nu12 + k12*sb**2 + w12 )
    return dw * (  nu12 + k12*sb**2 + w12 )

@jit(nopython=True)
def fz(z,k,h):
    return ( np.exp(k*z) + np.exp(-k*(z+2.*h)) ) / (1. + np.exp(-2*k*h))


def angle_measure0(x):
    if x>np.pi:
        return angle_measure0(x - 2.*np.pi)
    elif x<-np.pi:
        return angle_measure0(x + 2.*np.pi)
    else:
        return x

angle_measure = lambda x : np.vectorize(angle_measure0)(x)


# ----------------------------------------------------------------------------