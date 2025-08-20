'''
Created on 24 avr. 2018

@author: cbrun
'''
import h5py
import pandas as pd


def getH5pyElementType(h5pyFile, element):
    # Default type
    elementType = None

    try:
        # Get type of the element
        elementType = h5pyFile[element].attrs['Type']
        if hasattr(elementType, 'decode'):
            elementType = elementType.decode('utf-8')

    except KeyError:
        # If the type has not defined type, try to put it under a generic group
        if type(h5pyFile[element]) == h5py._hl.group.Group:
            elementType = "Miscellaneous"

    return elementType


class OperaH5Reader:
    """Class to handle Opera output
    
    Example
    -------
    
    >>> r = OperaH5Reader(r"D:/OneDrive/Bureau Veritas/TLP FOWT - OperaResults/7-TLP+WT wave(11).h5")
    >>> df = r.getDataFrame()
    >>> print (r)
    Rigid bodies:
      - floater (1)
          *Acceleration   ('accX', 'accY', 'accZ', 'accwX', 'accwY', 'accwZ') 
          *Local Rotation Velocity   ('wX_local', 'wY_local', 'wZ_local', 'vX_local', 'vY_local', 'vZ_local') 
          *Position   ('X', 'Y', 'Z', 'AxisX', 'AxisY', 'AxisZ', 'Angle') 
          *Rotation   ('Roll', 'Pitch', 'Yaw') 
          *Total load   ('FX', 'FY', 'FZ', 'MX', 'MY', 'MZ') 
          *Velocity   ('vX', 'vY', 'vZ', 'wX', 'wY', 'wZ') 
    ...
    Rigid bodies load:
      - archimedeLoad
          *Application point   ('X', 'Y', 'Z') 
          *Load   ('FX', 'FY', 'FZ', 'MX', 'MY', 'MZ') 
      - buoyancyLoad
          *Application point   ('X', 'Y', 'Z') 
          *Load   ('FX', 'FY', 'FZ', 'MX', 'MY', 'MZ') 
    ...
    Rigid bodies analyses:
      - unifiedFormulation
          *Filter values   ('X', 'Y', 'Z', 'roll', 'pitch', 'yaw', 'vX', 'vY', 'vZ', 'wX', 'wY', 'wZ', 'accX', 'accY', 'accZ', 'accwX', 'accwY', 'accwZ') 
          
    >>> df = r.getDataFrame( type_='Rigid bodies', name="floater (1)", quantity="Position" )
    >>> print(df)
                   X         Y          Z     AxisX     AxisY     AxisZ     Angle
    Time                                                                         
    0.0     4.939000 -0.011000 -13.542000  1.000000  0.000000  0.000000  0.000000
    0.6     4.906912 -0.010865 -13.611827  0.009999  0.999950  0.000198  0.000176
             ...       ...        ...       ...       ...       ...       ...
    999.2  -0.403969 -0.008498 -13.623881 -0.340380  0.940204  0.012602  0.000429
    1000.0 -0.356190 -0.007178 -13.396658  0.000801 -0.999980  0.006303  0.000997
    >>> 
    """
    
    class _Object:
        def __init__(self, group):
            self._group = group
            self._keys = self._group.keys()

        def getScales(self):
            ret = []
            for key in self._keys:
                if 'DIMENSION_SCALE' in self.getAttrs(key, 'CLASS'):
                    ret.append((self.getAttrs(key, 'NAME')[0], self.get(key)[:,0]))
            return ret

        def get(self, key):
            if key in self._keys:
                # return self._group['data'][self._group[key][0]]
                return self._group[key]
            raise Exception("Unknown key: {}".format(key))

        def getKeys(self):
            return list(self._keys)

        def getAttrsNames(self, key):
            return self._group[key].attrs.keys()

        def getAttrs(self, key, attr=None):
            if attr is None:
                return self._group[key].attrs
            if attr in self._group[key].attrs.keys():
                attrs = self._group[key].attrs[attr]
                if hasattr(attrs, 'decode'):
                    attrs = attrs.decode('utf-8')
                return tuple(map(str.strip, attrs.split(',')))
            return ()

        def getHeaders(self, key):
            return self.getAttrs(key, 'Header')

        def getShape(self, key):
            return self.get(key).shape

    def __init__(self, fname):
        """Opera Reader.

        Parameters
        ----------
        fname : str
            Opera output file (.h5)
        """
        self._objects = dict()
        self._scales = dict()

        # Manage file given as input
        if isinstance(fname, h5py.File):
            # WARNING: If fname given as input is already a h5py File, its life cycle IS NOT managed by this class and
            #  must be done outside
            self.closeFileAtExit = False
            self._root = fname
        else:
            self.closeFileAtExit = True
            self._root = h5py.File(fname, 'r+')
        self._root.visit(self._extract)

    def _extract(self, key):
        type_ = getH5pyElementType(self._root, key)
        if type_ is None:
            return
        if type_ not in self._objects:
            self._objects[type_] = dict()
        obj = self._Object(self._root[key])
        self._objects[type_][key] = obj
        for scaleName, table in obj.getScales():
            self._scales[scaleName] = table

    def getRigidBodiesNames(self):
        return list(self._objects['Rigid bodies'].keys())

    def getRigidBody(self, name):
        return self._objects['Rigid bodies'][name]

    def getTypes(self):
        return list(self._objects.keys())

    def getNames(self, typeName):
        return list(self._objects[typeName].keys())

    def get(self, typeName, name):
        return self._objects[typeName][name]

    def close(self):
        if self.closeFileAtExit:
            self._root.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        ll = []
        for t in self.getTypes():
            ll.append(f"{t}:")
            for n in self.getNames(t):
                ll.append(f"  - {n}")
        return '\n'.join(ll)
    
    def __str__(self):
        """Print the object content.
        
        Compared to __repr__, it displays two levels more.
        """
        ll = []
        for t in self.getTypes():
            ll.append(f"{t}:")
            for n in self.getNames(t):
                ll.append(f"  - {n}")
                for comp in self._objects[t][n].getKeys() : 
                    ll.append( f"      *{comp:}   {self._objects[t][n].getHeaders(comp):} " )
        return '\n'.join(ll)

    def getSortedItems(self):
        """Return Tree items"""
        types = self.getTypes()
        types.sort()
        ret = []
        for t in types:
            objects = []
            for name in self.getNames(t):
                obj = self.get(t, name)
                quantities = []
                for quantity in obj.getKeys():
                    headers = []
                    for header in obj.getHeaders(quantity):
                        headers.append([header, []])  # No child !
                    if headers:
                        quantities.append([quantity, headers])
                if quantities:
                    objects.append([name, quantities])
            if objects:
                ret.append([t, objects])
        return ret

    def getDataFrame(self, type_='Rigid bodies', name="floater (1)", quantity="Position",
                     pointIndex=-1):
        """Return time series as dataframe.

        Parameters
        ----------
        type_ : str, optional
            Type key. The default is 'Rigid bodies'.
        name : str, optional
            Name key. The default is "floater (1)".
        quantity : TYPE, optional
            Quantity key. The default is "Position".

        Returns
        -------
        DataFrame
            The time series as dataframe
            
        Example
        -------
        >>> r = OperaH5Reader( r"output.h5"  )
        >>> df = r.getDataFrame( type_='Rigid bodies', name="floater (1)", quantity="Position" )
        >>> print(df)
                       X         Y          Z     AxisX     AxisY     AxisZ     Angle
        Time                                                                         
        0.0     4.939000 -0.011000 -13.542000  1.000000  0.000000  0.000000  0.000000
        0.6     4.906912 -0.010865 -13.611827  0.009999  0.999950  0.000198  0.000176
                 ...       ...        ...       ...       ...       ...       ...
        999.2  -0.403969 -0.008498 -13.623881 -0.340380  0.940204  0.012602  0.000429
        1000.0 -0.356190 -0.007178 -13.396658  0.000801 -0.999980  0.006303  0.000997
        >>> 
        """
        obj = self.get(type_, name)
        table = obj.get(quantity)
        if len(table.shape) == 3:
            table = table[:, pointIndex, :]

        scaleLabels = obj.getAttrs(quantity, attr='DIMENSION_LABELS')
        if len(scaleLabels) > 0:
            scaleLabel = scaleLabels[0]
        else:
            scaleLabel = 'TIME'  # default value
        if scaleLabel in self._scales:
            index = self._scales[scaleLabel]
        else:
            # Compatibility with older files
            key_time = f'{name:}/Time'
            if key_time in self.getNames("Time"):
                index = self.get("Time", key_time).get("Simulation Time")[:, 0]
            else:
                index = self.get("Time", "Time").get("Simulation Time")[:, 0]
        return pd.DataFrame(data=table,
                            index=pd.Index(index, name=scaleLabel),
                            columns=obj.getHeaders(quantity))

    def getDataShape(self, type_, name, quantity):
        return self.get(type_, name).get(quantity).shape
