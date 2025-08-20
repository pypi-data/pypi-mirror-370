#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Opera Geometry module
"""
import sys
import numpy
import _Geometry
from _Geometry import set_logger_level, add_logger_callback
from .sx3Manipulation import Kso3Manipulation
from .sx3Manipulation import Kse3Manipulation

Point = _Geometry.Point
Vector = _Geometry.Vector

# TranslatorTypeEnum and RotatorTypeEnum
TranslatorTypeEnum = _Geometry.TranslatorTypeEnum
RotatorTypeEnum = _Geometry.RotatorTypeEnum

_rotatorTypeEnumDict = {'basisvectors':RotatorTypeEnum.BASIS_VECTORS,
                        'quaternion':RotatorTypeEnum.QUATERNION,
                        'basisvectors':RotatorTypeEnum.BASIS_VECTORS,
                        'axisandangle':RotatorTypeEnum.AXIS_AND_ANGLE,
                        'rotationmatrix':RotatorTypeEnum.ROTATION_MATRIX,
                        'mrp':RotatorTypeEnum.MRP,
                        #FIXME to add in wrapping 'horizontalplane':RotatorTypeEnum.HORIZONTAL_PLANE,
                        'euleranglesxyx':RotatorTypeEnum.EULER_ANGLES_XYX_i,
                        'euleranglesxyz':RotatorTypeEnum.EULER_ANGLES_XYZ_i,
                        'euleranglesxzx':RotatorTypeEnum.EULER_ANGLES_XZX_i,
                        'euleranglesxzy':RotatorTypeEnum.EULER_ANGLES_XZY_i,
                        'euleranglesyxy':RotatorTypeEnum.EULER_ANGLES_YXY_i,
                        'euleranglesyxz':RotatorTypeEnum.EULER_ANGLES_YXZ_i,
                        'euleranglesyzx':RotatorTypeEnum.EULER_ANGLES_YZX_i,
                        'euleranglesyzy':RotatorTypeEnum.EULER_ANGLES_YZY_i,
                        'eulerangleszxy':RotatorTypeEnum.EULER_ANGLES_ZXY_i,
                        'eulerangleszxz':RotatorTypeEnum.EULER_ANGLES_ZXZ_i,
                        'eulerangleszyx':RotatorTypeEnum.EULER_ANGLES_ZYX_i,
                        'eulerangleszyz':RotatorTypeEnum.EULER_ANGLES_ZYZ_i
                        }

_translatorTypeEnumDict={
                         'cartesian':TranslatorTypeEnum.CARTESIAN,
                        }

def getRotatorType(key):
    k = key.lower().replace('_', '')
    if k in _rotatorTypeEnumDict:
        return _rotatorTypeEnumDict[k]
    raise Exception ('Unknown key %s'%key)

def getRotatorTypes():
    return _rotatorTypeEnumDict.keys()

def getTranslatorTypes():
    return _translatorTypeEnumDict.keys()
    
def getTranslatorType(key):
    k = key.lower().replace('_', '')
    if k in _translatorTypeEnumDict:
        return _translatorTypeEnumDict[k]
    raise Exception ('Unknown key %s'%key)
    
# Rotators
RotationMatrix = _Geometry.RotationMatrix
BasisVectors = _Geometry.BasisVectors
Quaternion = _Geometry.Quaternion
HorizontalPlane = _Geometry.HorizontalPlane
AxisAndAngle = _Geometry.AxisAndAngle
AxisConvention = _Geometry.AxisConvention
MRP = _Geometry.MRP
RotationVector = _Geometry.RotationVector
EulerAngles_XYX_i = _Geometry.EulerAngles_XYX_i
EulerAngles_XYZ_i = _Geometry.EulerAngles_XYZ_i
EulerAngles_XZX_i = _Geometry.EulerAngles_XZX_i
EulerAngles_XZY_i = _Geometry.EulerAngles_XZY_i
EulerAngles_YXY_i = _Geometry.EulerAngles_YXY_i
EulerAngles_YXZ_i = _Geometry.EulerAngles_YXZ_i
EulerAngles_YZX_i = _Geometry.EulerAngles_YZX_i
EulerAngles_YZY_i = _Geometry.EulerAngles_YZY_i
EulerAngles_ZXY_i = _Geometry.EulerAngles_ZXY_i
EulerAngles_ZXZ_i = _Geometry.EulerAngles_ZXZ_i
EulerAngles_ZYX_i = _Geometry.EulerAngles_ZYX_i
EulerAngles_ZYZ_i = _Geometry.EulerAngles_ZYZ_i

EulerAngles_XYX_e = _Geometry.EulerAngles_XYX_e
EulerAngles_XYZ_e = _Geometry.EulerAngles_XYZ_e
EulerAngles_XZX_e = _Geometry.EulerAngles_XZX_e
EulerAngles_XZY_e = _Geometry.EulerAngles_XZY_e
EulerAngles_YXY_e = _Geometry.EulerAngles_YXY_e
EulerAngles_YXZ_e = _Geometry.EulerAngles_YXZ_e
EulerAngles_YZX_e = _Geometry.EulerAngles_YZX_e
EulerAngles_YZY_e = _Geometry.EulerAngles_YZY_e
EulerAngles_ZXY_e = _Geometry.EulerAngles_ZXY_e
EulerAngles_ZXZ_e = _Geometry.EulerAngles_ZXZ_e
EulerAngles_ZYX_e = _Geometry.EulerAngles_ZYX_e
EulerAngles_ZYZ_e = _Geometry.EulerAngles_ZYZ_e

EulerAnglesConvention_XYX_i = _Geometry.EulerAnglesConvention_XYX_i
EulerAnglesConvention_XYZ_i = _Geometry.EulerAnglesConvention_XYZ_i
EulerAnglesConvention_XZX_i = _Geometry.EulerAnglesConvention_XZX_i
EulerAnglesConvention_XZY_i = _Geometry.EulerAnglesConvention_XZY_i
EulerAnglesConvention_YXY_i = _Geometry.EulerAnglesConvention_YXY_i
EulerAnglesConvention_YXZ_i = _Geometry.EulerAnglesConvention_YXZ_i
EulerAnglesConvention_YZX_i = _Geometry.EulerAnglesConvention_YZX_i
EulerAnglesConvention_YZY_i = _Geometry.EulerAnglesConvention_YZY_i
EulerAnglesConvention_ZXY_i = _Geometry.EulerAnglesConvention_ZXY_i
EulerAnglesConvention_ZXZ_i = _Geometry.EulerAnglesConvention_ZXZ_i
EulerAnglesConvention_ZYX_i = _Geometry.EulerAnglesConvention_ZYX_i
EulerAnglesConvention_ZYZ_i = _Geometry.EulerAnglesConvention_ZYZ_i

EulerAnglesConvention_XYX_e = _Geometry.EulerAnglesConvention_XYX_e
EulerAnglesConvention_XYZ_e = _Geometry.EulerAnglesConvention_XYZ_e
EulerAnglesConvention_XZX_e = _Geometry.EulerAnglesConvention_XZX_e
EulerAnglesConvention_XZY_e = _Geometry.EulerAnglesConvention_XZY_e
EulerAnglesConvention_YXY_e = _Geometry.EulerAnglesConvention_YXY_e
EulerAnglesConvention_YXZ_e = _Geometry.EulerAnglesConvention_YXZ_e
EulerAnglesConvention_YZX_e = _Geometry.EulerAnglesConvention_YZX_e
EulerAnglesConvention_YZY_e = _Geometry.EulerAnglesConvention_YZY_e
EulerAnglesConvention_ZXY_e = _Geometry.EulerAnglesConvention_ZXY_e
EulerAnglesConvention_ZXZ_e = _Geometry.EulerAnglesConvention_ZXZ_e
EulerAnglesConvention_ZYX_e = _Geometry.EulerAnglesConvention_ZYX_e
EulerAnglesConvention_ZYZ_e = _Geometry.EulerAnglesConvention_ZYZ_e

EulerAngleXYZeToEulerSmallAngleContinuity = _Geometry.EulerAngleXYZeToEulerSmallAngleContinuity
EulerAngleXYZiToEulerSmallAngleContinuity = _Geometry.EulerAngleXYZiToEulerSmallAngleContinuity
allRotationNames = ["RotationMatrix", "BasisVectors", "Quaternion", "AxisAndAngle", "MRP",
                    "RotationVector",
                    "EulerAngleXYXi", "EulerAngleXZXi", "EulerAngleYXYi", "EulerAngleYZYi",
                    "EulerAngleZXZi", "EulerAngleZYZi", "EulerAngleXYZi", "EulerAngleXZYi",
                    "EulerAngleYXZi", "EulerAngleYZXi", "EulerAngleZXYi", "EulerAngleZYXi",
                    "EulerAngleXYXe", "EulerAngleXZXe", "EulerAngleYXYe", "EulerAngleYZYe",
                    "EulerAngleZXZe", "EulerAngleZYZe", "EulerAngleXYZe", "EulerAngleXZYe",
                    "EulerAngleYXZe", "EulerAngleYZXe", "EulerAngleZXYe", "EulerAngleZYXe"]

def __registerRotationConverters(startRotName, allOtherNames):
    for name in [startRotName+"To"+name for name in allOtherNames]:
        if(not name.endswith(startRotName)):
            setattr(sys.modules[__name__], name, getattr(_Geometry, name))
for rotName in allRotationNames:
    __registerRotationConverters(rotName, allRotationNames)

# Translators
Cartesian = _Geometry.Cartesian
Spherical_Lat = _Geometry.Spherical_Lat
Spherical_CoLat = _Geometry.Spherical_CoLat

# Transform
Transform3D = _Geometry.Transform3D

def _AsTuple( self ):
    """Returns the coordinates as the (x, y, z) tuple.

    :return: a tuple of 3 coordinates.
    :rtype: tuple
    """
    return ( self.x, self.y, self.z )

def _AsNumpyArray( self ):
    """Returns the coordinates (x, y, z) as a length-3 numpy array.

    :return: a numpy array containing the 3 coordinates
    :rtype: :py:class:`numpy.ndarray`
    """
    import numpy
    t = _AsTuple( self )
    return numpy.array( t )

def ___repr__( self ):
    """
    The representation of the (x, y, z) data.
    """
    return self.__class__.__name__ + self.asTuple().__repr__()

def _CopyXYZ( class_, self, memo = None ):
    """
    Copies the XYZ instance. It may be a Point or a Vector.
    class_: The class that will be copied
    self: The instance that will be copied
    memo: It is there for deepcopy stuff, but useless in our case.
    """
    return class_( self )

for class_ in Point, Vector, Cartesian:
    class_.asTuple      = _AsTuple
    class_.asNumpyArray = _AsNumpyArray
    # Requested for ConfigObj
    class_.__repr__     = ___repr__

Point.__copy__     = lambda self: _CopyXYZ( Point, self )
Point.__deepcopy__ = lambda self, memo: _CopyXYZ( Point, self, memo )

Vector.__copy__     = lambda self: _CopyXYZ( Vector, self )
Vector.__deepcopy__ = lambda self, memo: _CopyXYZ( Vector, self, memo )

def __BasisVectorsRepr__(self):
    return ("{0:s}({1:s}, {2:s}, {3:s})").format(self.__class__.__name__, self.d1.__repr__(), self.d2.__repr__(), self.d3.__repr__())

BasisVectors.__repr__ = __BasisVectorsRepr__

#def _GetUnknows( self ):
#    """
#    Returns the unknowns as a tuple.
#    """
#    return self._getUnknowns()
#    #return tuple( [ i for i in self._getUnknowns() ] )
#
#def _SetUnknows( self, v ):
#    """
#    Sets the unknowns from the numpy array `v`.
#    """
#    # FIXME Nor type neither size checking yet...
#    # FIXME Do it when ABC has nUnknowns and nConstraints
#    #assert len(v) == 3
#    assert len(v.shape) == 1
#    self._setUnknowns(v)
#    #stdVec = _Geometry.RealVector()
#    #stdVec.reserve( len( v ) )
#    #for i in v:
#    #    stdVec.append( i )
#    #self._setUnknowns( stdVec )
#
#_Geometry._GeometryRotationABC.unknowns = property( _GetUnknows, _SetUnknows )

def _GetConstraints(self):
    return self._getConstraints()
_Geometry._GeometryRotationABC.constraints = property(_GetConstraints)

def _Directors( self ):
    """
    Returns a tuple containing the three directors.
    WARNING, the tuple index start is 0, while the first director is d1...
    """
    return (self.d1, self.d2, self.d3)

_Geometry._GeometryRotationABC.directors = _Directors

def Interp1dQuaternion(x, xs, data):
    r"""Interpolate a Quaternion with respect to one parameters.
    
    :param float x: first axis value to interpolate to.
    :param ndarray xs: first axis vector of size nx.
    :param ndarray data: a matrix containing the Quaternion to interpolate of size (nx, 4).
    :return: float: data value interpolated at x and y.
    """
    it0 = (numpy.abs(xs-x)).argmin()
    it1 = min(it0+1, len(xs)-1)
    if(it0 == it1):
        # special case if last element is found
        # get the last two elements
        it0 -= 1
    q0 = _Geometry.Quaternion(data[it0])
    q1 = _Geometry.Quaternion(data[it1])
    qInterp = q0.slerp((x-xs[it0])/(xs[it1]-xs[it0]), q1)
    return qInterp.unknowns

def Interp2dRotation(x, y, xs, ys, data, rotation1DInterpolator):
    r"""Interpolate a Rotation with respect to two parameters.
    
    :param float x: first axis value to interpolate to.
    :param float y: second axis value to interpolate to.
    :param ndarray xs: first axis vector of size nx.
    :param ndarray ys: a matrix containing the second axis of size ny.
    :param ndarray data: a matrix containing the rotation unknowns to interpolate of size (nx, ny, nRotUnk).
    :return: float: data value interpolated at x and y.
    """
    # First get the surrounding time instants
    it0 = (numpy.abs(xs-x)).argmin()
    it1 = min(it0+1, len(xs)-1)
    if it0 == it1:
        return rotation1DInterpolator(y, ys, data[it1])
    dataY0 = rotation1DInterpolator(y, ys, data[it0])
    dataY1 = rotation1DInterpolator(y, ys, data[it1])
    x0 = xs[it0]
    x1 = xs[it1]
    return rotation1DInterpolator(x, numpy.array([x0, x1]), numpy.array([dataY0, dataY1]))
