#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

class Kso3Manipulation(object):
    # class which define conversions of so(3) space (anti-symetric matrices)
    # so(3) = { S \in \mathcal{R}^{n \times n} : S^T = -S }
    def __init__(self):
        super(Kso3Manipulation, self).__init__()
        return
    
    def _R3Toso3(self, u1, u2, u3):
        U = numpy.zeros((3,3), dtype=float)
        U[1,0] = u3
        U[2,0] = -u2
        U[2,1] = u1
        
        U[0,1] = -u3
        U[0,2] = u2
        U[1,2] = -u1
        return U
    
    def _R3VectToso3(self, u):
        return self._R3Toso3(u[0], u[1], u[2])
    
    def _so3ToR3(self, U):
        u = numpy.zeros(3, dtype=float)
        u[0] = U[2,1]
        u[1] = U[0,2]
        u[2] = U[1,0] 
        return u
    
    
class Kse3Manipulation(object):
    # class which define conversions of se(3) space
    # the space se(3) = { (p, R) : p \in \mathcal{R}^3, R \in SO(3) } = R^3 \times SO(3)
    # where SO(3) = { R \in \mathcal{R}^{n \times n} : R \cdot R^T = I, det(R) = +1 }
    def __init__(self):
        super(Kse3Manipulation, self).__init__()
        return
    
    def _R6Tose3(self, v1, v2, v3, u1, u2, u3):
        ksi = numpy.zeros((4,4), dtype=float)
        U = self._R3Toso3(u1, u2, u3)
        ksi[:3,:3] = U
        ksi[3,0] = v1
        ksi[3,1] = v2
        ksi[3,2] = v3
        return ksi
    
    def _R6VectTose3(self, vu):
        return _R6Tose3(self, vu[0], vu[1], vu[2], vu[3], vu[4], vu[5])
    
    def _R6VectVectTose3(self, v, u):
        return _R6Tose3(self, v[0], v[1], vu[2], u[0], u[1], u[2])
   
    def _se3ToR6(self, ksi):
        u = self._so3ToR3(ksi[:3,:3])
        v = numpy.array(ksi[:3,3], dtype=float)
        vect = numpy.zeros(6, dtype=float)
        vect[:3] = v
        vect[3:] = u
        return vect