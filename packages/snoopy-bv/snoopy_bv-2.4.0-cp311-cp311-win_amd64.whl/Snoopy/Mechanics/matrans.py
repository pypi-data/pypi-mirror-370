"""
   Equivament of HydroStar matrans.f90  (translate matrix from one point to another)

   Ref : "Dynamic coupling of seakeeping and sloshing" (S.Malenica, M.zalar, X.B.Chen)

"""
import numpy as np


def matrans2(a,vect) :
    """
    Parameters
    ----------
    a : np.ndarray (6,6)
        Matrix to move
    vect : np.ndarray (3)
        Moving vector : vect = origin - destination

    Returns
    -------
    np.ndarray (6,6)
        moved matrix
    """
    #Move matrices by vector vect = origin-destination
    v = np.zeros((3,3), dtype = float)
    v[0,1] = -vect[2]
    v[0,2] = +vect[1]
    v[1,0] = +vect[2]
    v[1,2] = -vect[0]
    v[2,0] = -vect[1]
    v[2,1] = +vect[0]
    return matrans(a,v)


def matrans3(a, origin, destination) :
    """Move load matrix from origin to destination

    Parameters
        ----------
        a : array(6,6)
            Matrix to move
        origin : array(3)
            Original reference point of matrix a
        destination : array(3)
            Target reference point of matrix a
    """
    return matrans2(a , origin - destination)



def matrans(a, v):
    """This function moves the diagonal blocks of a matrix using the matrix matV."""

    b12 = np.matmul(v, a[0:3, 0:3])
    b22 = np.matmul(b12, v)
    b12 = np.matmul(v, a[0:3, 3:6])
    b21 = np.matmul(a[3:6, 0:3], v)

    b22 = b12 - b21 - b22

    b12 =  np.matmul(a[0:3, 0:3], v)
    b21 =  np.matmul(v, a[0:3, 0:3])

    res = np.zeros( (6,6), dtype=float)
    res[:, :] = a[:, :]
    res[0:3, 3:6] = res[0:3, 3:6] - b12[0:3, 0:3]
    res[3:6, 0:3] = res[3:6, 0:3] + b21[0:3, 0:3]
    res[3:6, 3:6] = res[3:6, 3:6] + b22[0:3, 0:3]

    return res


def b2matrans(a, v, i_bd, j_bd):
    """This function moves the off-diagonal blocks of a matrix using the matrix matV."""

    b12 = np.matmul(v[:, :, i_bd], a[i_bd, j_bd, 0:3, 0:3])
    b22 = np.matmul(b12, v[:, :, j_bd])
    b12 = np.matmul(v[:, :, i_bd], a[i_bd, j_bd, 0:3, 3:6])
    b21 = np.matmul(a[i_bd, j_bd, 3:6, 0:3], v[:, :, j_bd])

    b22 = b12 - b21 - b22

    b12 = np.matmul(a[i_bd, j_bd, 0:3, 0:3], v[:, :, j_bd])
    b21 = np.matmul(v[:, :, i_bd], a[i_bd, j_bd, 0:3, 0:3])

    n_bodies = a.shape[0]
    res = np.zeros((n_bodies, n_bodies, 6, 6), dtype=float)
    res[:, :, :, :] = a[:, :, :, :]

    res[i_bd, j_bd, 0:3, 3:6] = res[i_bd, j_bd, 0:3, 3:6] - b12[0:3, 0:3]
    res[i_bd, j_bd, 3:6, 0:3] = res[i_bd, j_bd, 3:6, 0:3] + b21[0:3, 0:3]
    res[i_bd, j_bd, 3:6, 3:6] = res[i_bd, j_bd, 3:6, 3:6] + b22[0:3, 0:3]

    return res


def dbmatrans(a, origin, destination):
    """This function moves a matrix from origin to destination."""

    n_bodies = a.shape[0]

    # matV matrix.
    matV = np.zeros((3, 3, n_bodies), dtype=float)
    for i_bd in range(0, n_bodies):
        dx = -(origin[i_bd][0] - destination[i_bd][0])
        dy = -(origin[i_bd][1] - destination[i_bd][1])
        dz = -(origin[i_bd][2] - destination[i_bd][2])
        matV[0, 1, i_bd] = dz
        matV[0, 2, i_bd] = -dy
        matV[1, 0, i_bd] = -dz
        matV[1, 2, i_bd] = dx
        matV[2, 0, i_bd] = dy
        matV[2, 1, i_bd] = -dx

    # Diagonal blocks.
    res = np.zeros((n_bodies, n_bodies, 6, 6))
    res[:, :, :, :] = a[:, :, :, :]
    for i_bd in range(0, n_bodies):
        res[i_bd, i_bd, :, :, ] = matrans(a[i_bd, i_bd, :, :], matV[:, :, i_bd])

    # Off-diagonal blocks.
    for i_bd in range(0, n_bodies - 1):
        for j_bd in range(1, n_bodies):
            res = b2matrans(a=res, v=matV, i_bd=i_bd, j_bd=j_bd)
            res = b2matrans(a=res, v=matV, i_bd=j_bd, j_bd=i_bd)

    return res

def matrans_freq_head( mat4 , origin, destination) :
    moved = np.zeros(mat4.shape, dtype=mat4.dtype)
    for ihead in range(mat4.shape[0]):
        for ifreq in range(mat4.shape[1]):
            moved[ihead, ifreq , :,:] =  matrans3( mat4[ihead, ifreq , :,:], origin, destination )
    return moved






def vectran(a, vect, isMotion = False):
    """
    Move modal amplitudes by a vect v 
    ONLY APPLY FOR LOAD 
    Parameters
    ----------
    a : array(6)
        modal amplitudes vector to move
    vect : array(3)
           vector
        
    Returns
    -------
    res : array(6)
        moved modal amplitudes vector

    """
    res = np.zeros(a.shape, dtype=a.dtype)
    if isMotion:  # Motions: rotation stay the same but positions change.
        res[3:] = a[3:]
        res[:3] = a[:3] + np.cross(vect, a[3:])
    else:  # Loads: forces stay the same but moments change.
        res[:3] = a[:3]
        res[3:] = a[3:] + np.cross(vect, a[:3])

    return res


def vectran3(a, origin, destination, isMotion=False):
    """
    Move modal amplitudes by a vect v 
    ONLY APPLY FOR LOAD 
    Parameters
    ----------
    a : array(6)
        modal amplitudes vector to move
    origin : array(3)
        Original reference point of a
    destination : array(3)
        Target reference point of a
        
    Returns
    -------
    res : array(6)
        moved modal amplitudes vector

    """
    
    return vectran(a, origin - destination, isMotion=isMotion)


def vectran_freq_head( a4 , origin, destination, isMotion = False) :
    moved = np.zeros(a4.shape, dtype=a4.dtype)
    for ihead in range(a4.shape[0]):
        for ifreq in range(a4.shape[1]):
            moved[ihead, ifreq , :] =  vectran3(a4[ihead, ifreq , :], origin, destination, isMotion = isMotion)
    return moved


def compare_with_Pluto():
    a = np.diag( [1.,1,1, 10, 20, 30] )
    v = np.array(  [10, 20, 30] , dtype = float)

    m_py = matrans2( a, v )

    from Pluto.massDistribution.py_matrans_m import matrans2 as matrans2_for
    m_for = matrans2_for( a, v )

    diff = np.abs(m_py - m_for).max()
    assert (diff == 0)


if __name__ == "__main__" :
    # compare_with_Pluto()
    
    m = np.zeros((6,6), dtype = "float")
    
    m[3,3] = 100
    m[3,1] = 10
    m[1,3] = 10
    
    v= np.array( [ 0, 0, 1] )
    
    print (m)
    print ( matrans2( m , v ) )

