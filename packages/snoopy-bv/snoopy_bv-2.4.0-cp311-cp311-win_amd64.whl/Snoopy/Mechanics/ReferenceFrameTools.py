#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

from Snoopy import Geometry
from Snoopy.Mechanics import ReferenceFrame


def MovingFrameLocalPointToGlobal(frameTS, localPointPos=(0., 0., 0.)):
    """Returns the time series of a moving frame local point in global axis system
    
    Parameters
    ----------
    frameTS : numpy.ndarray
        Time series of the frame position and orientation
        shape: (n instants, 6)
        columns: x (m), y (m), z (m), roll (rad), pitch (rad), yaw (rad)
        Orientation convention is assumed to be Euler angles XYZ extrinsic
    localPointPos : tuple
        Local position of the point to output the time series in global
        reference frame
        shape: (3,)
        values: x (m), y (m), z (m)
        
    Returns
    -------
    numpy.ndarray
        Time series of the local point in global reference frame
        shape: (n instants, 3)
        columns: x (m), y (m), z (m)
    """
    ref = ReferenceFrame()
    localPoint = Geometry.Point(*localPointPos)
    pos = numpy.empty((frameTS.shape[0], 3), dtype=float)
    for i, values in enumerate(frameTS):
        x, y, z, roll, pitch, yaw = values
        ref.setTranslator(Geometry.Cartesian(x, y, z))
        ref.setRotator(Geometry.EulerAngles_XYZ_e(roll, pitch, yaw))
        pos[i, :] = ref.localToGlobal(localPoint).asNumpyArray()
    return pos


def MovingFrameAtLocalPoint(frameTS, localPointPos=(0., 0., 0.)):
    """Returns the time series of a moving frame expressed at other local point
    
    Parameters
    ----------
    frameTS : numpy.ndarray
        Time series of the frame position and orientation
        shape: (n instants, 6)
        columns: x (m), y (m), z (m), roll (rad), pitch (rad), yaw (rad)
        Orientation convention is assumed to be Euler angles XYZ extrinsic
    localPointPos : tuple
        Local position of the point to output the time series in global
        reference frame
        shape: (3,)
        values: x (m), y (m), z (m)
        
    Returns
    -------
    numpy.ndarray
        Time series of the local point in global reference frame
        shape: (n instants, 6)
        columns: x (m), y (m), z (m), roll (rad), pitch (rad), yaw (rad)
    """
    res = numpy.empty((frameTS.shape[0], 6), dtype=float)
    res[:, :3] = MovingFrameLocalPointToGlobal(frameTS, localPointPos)
    res[:, 3:] = frameTS[:, 3:] # Rigid body motion keeps orientations
    return res
