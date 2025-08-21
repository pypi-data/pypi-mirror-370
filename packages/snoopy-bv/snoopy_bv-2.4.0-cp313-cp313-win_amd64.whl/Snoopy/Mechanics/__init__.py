#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Opera Mechanical module
"""
import numpy
import os
import _Mechanics
from _Mechanics import set_logger_level, add_logger_callback
from Snoopy import Geometry
from .matrans import matrans3, matrans_freq_head, vectran_freq_head, vectran3, dbmatrans
import xarray as xa

g = 9.81

from .hydro_coef import RdfCoef, McnInput, HydroCoef, McnCoef, QTFCoef
from .internal_load import InternalLoad, get_from_pressure_integration
from .mechanicalsolver import MechanicalSolver, get_gravity_stiffness


    
# Redirection
Torsor = _Mechanics._Torsor
#KinematicTorsor = _Mechanics._KinematicTorsor
#StaticTorsor = _Mechanics._StaticTorsor



_typeToKeyTranslation = {Geometry.TranslatorTypeEnum.CARTESIAN:'Cartesian',
                         Geometry.TranslatorTypeEnum.SPHERICAL_LAT:'Spherical_Lat',
                         Geometry.TranslatorTypeEnum.SPHERICAL_COLAT:'Spherical_CoLat'}

_typeToKeyRotation = {Geometry.RotatorTypeEnum.QUATERNION:'Quaternion',
                      Geometry.RotatorTypeEnum.AXIS_AND_ANGLE:'AxisAndAngle',
                      Geometry.RotatorTypeEnum.BASIS_VECTORS:'BasisVectors',
                      Geometry.RotatorTypeEnum.ROTATION_MATRIX:'RotationMatrix',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XYX_i:'EulerAngles_XYX_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XYZ_i:'EulerAngles_XYZ_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XZX_i:'EulerAngles_XZX_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XZY_i:'EulerAngles_XZY_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YXY_i:'EulerAngles_YXY_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YXZ_i:'EulerAngles_YXZ_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YZX_i:'EulerAngles_YZX_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YZY_i:'EulerAngles_YZY_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZXY_i:'EulerAngles_ZXY_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZXZ_i:'EulerAngles_ZXZ_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZYX_i:'EulerAngles_ZYX_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZYZ_i:'EulerAngles_ZYZ_i',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XYX_e:'EulerAngles_XYX_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XYZ_e:'EulerAngles_XYZ_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XZX_e:'EulerAngles_XZX_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_XZY_e:'EulerAngles_XZY_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YXY_e:'EulerAngles_YXY_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YXZ_e:'EulerAngles_YXZ_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YZX_e:'EulerAngles_YZX_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_YZY_e:'EulerAngles_YZY_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZXY_e:'EulerAngles_ZXY_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZXZ_e:'EulerAngles_ZXZ_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZYX_e:'EulerAngles_ZYX_e',
                      Geometry.RotatorTypeEnum.EULER_ANGLES_ZYZ_e:'EulerAngles_ZYZ_e',
                      Geometry.RotatorTypeEnum.MRP:'MRP'}

class KinematicTorsor(_Mechanics._KinematicTorsor):
    """
    """

class StaticTorsor(_Mechanics._StaticTorsor):
    """
    """

class ReferenceFrame(_Mechanics._ReferenceFrame):
    def getTranslator(self, inGlobal=True):
        """Returns the translator inner representation.

        :param bool inGlobal: if True, returns the inner translation
            representation in the global reference frame,
            otherwise returns the inner translation representation in the
            parent reference frame (which defaults to the global reference
            frame if the parent is not set).

        :return: the reference frame inner translation representation in
            :ref:`translation object<GeometryTranslation>`.
        """
        return getattr(self, "getTranslatorIn{0:s}".format(inGlobal and "Global" or "Parent"))()

    def getRotator(self, inGlobal=True):
        """Returns the rotation inner representation.

        :param bool inGlobal: if True, returns the inner rotation
            representation in the global reference frame,
            otherwise returns the inner rotation representation in the
            parent reference frame (which defaults to the global reference
            frame if the parent is not set).

        :return: the reference frame inner rotation representation in
            :ref:`rotation object<GeometryRotation>`.
        """
        return getattr(self, "getRotatorIn{0:s}".format(inGlobal and "Global" or "Parent"))()


def GetGlobalPointPositions(positionTable, point):
    n, _ = positionTable.shape
    res = numpy.empty((n, 7))
    res[:, 3:] = positionTable[:, 3:]
    rf = ReferenceFrame()
    for i in range(n):
        rf.setTranslator(Geometry.Cartesian(positionTable[i, :3]))
        rf.setRotator(Geometry.AxisAndAngle(positionTable[i, 3:]))
        res[i, :3] = rf.localToGlobal(point).asTuple()
    return res

from .ReferenceFrameTools import MovingFrameLocalPointToGlobal

#Clean imports ?
__all__ = ["ReferenceFrame" , "Torsor" , "KinematicTorsor"  , "StaticTorsor",
           "matrans3", "matrans_freq_head", "GetGlobalPointPosition",
           "MovingFrameLocalPointToGlobal"]


TEST_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tests", "test_data")
