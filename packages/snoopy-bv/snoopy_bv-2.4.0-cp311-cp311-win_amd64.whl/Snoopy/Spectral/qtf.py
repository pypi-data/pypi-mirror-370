import copy
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import _Spectral

deg2rad = np.pi / 180.


def checkArrayUniformness(array):
    nbarray = len(array)
    if nbarray > 1:
        dw = array[1] -array[0]
        for i in range(2, nbarray):
            dw_next = array[i] -array[i-1]
            if abs(dw -dw_next) > 1e-6:
                return (i, dw, dw_next)
    return (0, dw, dw)



class Qtf(_Spectral.Qtf) :
    """Full Quadratic Transfer Function data definition, called Qtf here.

    Qtf terms are obtained from a second order diffraction-radiation analysis.
    They correspond to the 2nd order loads applied to the vessel
    when subjected to the action of a bichromatic wave.
    
    The Qtf are then available for Nm modes, but also for
    a limited number Nb of incidences relative to the vessel heading,
    and couples of wave frequencies Nf x Ndf.

    Qtf is then a N_heading x N_frequency x N_difference_frequency x N_mode matrix defined in the rigid body reference frame.

    """

    def __init__(self, *args , **kwargs):
        """Construct the QTF object.
        
        The Qtf can be constructed from
            - Data given in amplitude/phase or complex.
            - File name
            
        Parameters
        ----------
        b : np.ndarray
            Headings (in radians)
        w : np.ndarray
            wave frequencies
        dw : np.ndarray
            Difference frequencies
        amplitudes : np.ndarray, optional*
            Qtf module value (n_heading * n_freq * n_diff * n_mode)
        phases : np.ndarray, optional*
            Qtf module value (n_heading * n_freq * n_diff * n_mode)
        reIm : np.ndarray, complex, optional*
            Qtf module value (n_heading * n_freq * n_diff * n_mode)
        modes : np.ndarray, optional 
            modes
        modeCoefficients : np.ndarray, optional 
            modes
        qtfStorageType : sp.QtfStorageType, optional
            How the qtf is stored, default to sp.QtfStorageType.W_DW
        refPoint : np.ndarray
            Reference point
        waveRefPoint : np.ndarray
            Phase reference point
        qtfMode : int, optional
            DIFF or SUM. The default is sp.QtfMode.DIFF.
        forwardSpeed : float, optional
            Forward speed. The default is 0.0.
        depth : float, optional
            waterdepth. The default is -1.0.
            
            
        Parameters
        ----------
        filename : str
            File to read
            
        Example
        -------
        >>> # From file
        >>> qtf = sp.Qtf("filename.qtf")
        >>>
        >>> # From variables
        >>> w = np.arange(0.2, 1.8, 0.05)
        >>> dw = np.arange(0., 0.205, 0.05)
        >>> b = np.linspace(0. , np.pi*2 , 13)
        >>> data = np.zeros( (len(b) , len(w) , len(dw) , 1) , dtype = complex )
        >>> qtf = sp.Qtf( b=b, w=w , dw=dw , reIm = data , refPoint = [0.,0.,0.] , waveRefPoint = [0.,0])
        """

        if len(args) == 1 and type(args[0]) == str :
            fn, ext = os.path.splitext(args[0])
            if ext.lower() == ".h5":
                super().__init__( Qtf.ReadHstarH5( args[0] ))
            else:
                super().__init__(  Qtf.ReadHstar( args[0]  ))
        elif "filename" in kwargs :
            fn, ext = os.path.splitext(kwargs["filename"])
            if ext.lower() == ".h5":
                super().__init__( Qtf.ReadHstarH5( **kwargs ) )
            else:
                super().__init__( Qtf.ReadHstar( **kwargs  ) )
        else :
            qtfStorageType = kwargs.pop( "qtfStorageType" , _Spectral.QtfStorageType.W_DW )
            try :
                if not len(list(filter(lambda arg : (isinstance(arg, _Spectral.QtfStorageType)
                                                     or isinstance(arg, _Spectral.Qtf)
                                                     or isinstance(arg, Qtf)), args))):
                    # qtfStorageType is not part of the args also args are neither of type _Spectral.Qtf nor Qtf
                    super().__init__( *args , qtfStorageType=qtfStorageType, **kwargs )
                else:
                    # qtfStorageType is a part of args or args are either of type _Spectral.Qtf or Qtf
                    super().__init__( *args , **kwargs )
            except TypeError as e: 
                print(args)
                print (e)
                raise(TypeError( """Wrong signature for Qtf constructor.
Available signatures : 

- b(nb_headings) w(nb_frequencies) dw(nb_diff) amplitudes(nb_heading, nb_frequencies, nb_diff, nb_modes) phases(nb_heading, nb_frequencies, nb_diff, nb_modes) refPoint(3) waveRefPoint(2) + optional kwds

- b(nb_headings) w(nb_frequencies) dw(nb_diff) reIm(nb_heading, nb_frequencies, nb_diff, nb_modes)  refPoint(3) waveRefPoint(2) + optional kwds
"""))

    def __str__(self) :
        s = "Frequency ({:}) , {:}\n".format( self.nbfreq , self.freq )
        s += "Difference frequencies ({:}) , {:}\n".format( self.nbdiff , self.diff )
        s += "Headings ({:}) , {:}\n".format( self.nbhead , self.head )
        return s

    @property
    def head(self):
        return self.getHeadings()

    @property
    def nbhead(self) :
        return self.getNHeadings()

    @property
    def freq(self):
        return self.getFrequencies()

    @property
    def nbfreq(self) :
        return self.getNFrequencies()

    @property
    def diff(self) :
        return self.getDeltaFrequencies()

    @property
    def nbdiff(self) :
        return self.getNDeltaFrequencies()

    @property
    def cvalues(self):
        return self.getComplexData()

    def __add__(self , rhs):
        tmp_ = _Spectral.Qtf.__add__( self, rhs  )
        return self.__class__(tmp_)

    def __sub__(self , rhs):
        tmp_ = _Spectral.Qtf.__sub__( self, rhs  )
        return self.__class__(tmp_)

    def __mul__(self , rhs):
        tmp_ = _Spectral.Qtf.__mul__( self, rhs  )
        return self.__class__(tmp_)

    __rmul__ = __mul__

    def __div__(self , rhs):
        tmp_ = _Spectral.Qtf.__div__( self, rhs  )
        return self.__class__(tmp_)


    def getConjugate(self):

        return self.__class__( b = self.head, w = self.freq , dw = self.diff, reIm = np.conjugate(self.cvalues),
                       qtfStorageType=_Spectral.QtfStorageType.W_DW,
                       forwardSpeed=0, refPoint=self.getReferencePoint(),
                       waveRefPoint=self.getWaveReferencePoint(), modes=[_Spectral.Modes.NONE,],
                       qtfMode = _Spectral.QtfMode.DIFF  )

    def getQtfAtMode(self, imode):
        """Return a single QTF corresponding to the i mode position

        Use full for routines working with single QTFs

        Parameters
        ----------
        imode : int
            Position of the mode in array

        Returns
        -------
        Qtf
            Qtf at imode position

        """
        if self.getSumMode() > 0:
            qtfMode = _Spectral.QtfMode.SUM
        else:
            qtfMode = _Spectral.QtfMode.DIFF
        return self.__class__(b=self.head, w=self.freq, dw=self.diff,
                              modeCoefficients=self.getModeCoefficients()[
                                                                      [imode]
                                                                         ],
                              modes=self.getModes()[[imode]],
                              reIm=self.cvalues[:, :, :, [imode]],
                              qtfStorageType=_Spectral.QtfStorageType.W_DW,
                              refPoint=self.getReferencePoint(),
                              waveRefPoint=self.getWaveReferencePoint(),
                              qtfMode=qtfMode,
                              forwardSpeed=self.getForwardSpeed(),
                              depth=self.getDepth())

    def getQtf0(self):
        """Return QTF0 from full QTF
        Returns
        -------
        Qtf0
            QtfO from FullQtf
        """
        return _Spectral.Qtf0(b=self.head, w=self.freq,
                              modeCoefficients=self.getModeCoefficients(),
                              modes=self.getModes(),
                              values=np.real(self.cvalues[:, :, 0, :]),
                              refPoint=self.getReferencePoint(),
                              waveRefPoint=self.getWaveReferencePoint(),
                              forwardSpeed=self.getForwardSpeed(),
                              depth=self.getDepth())

    @staticmethod
    def getMetaData(obj) :
        """ Get metadata from either RAO or generated pandas dataFrame
        """
        return {"speed" : obj.getForwardSpeed(),
                "refPoint" : obj.getReferencePoint(),
                "waveRefPoint" : obj.getWaveReferencePoint(),
                "components" : obj.getModes() }


    @classmethod
    def ReadHstar( cls , filename ) :
        """
        Read qtf data from HydroStar files (could be consolidated/optimized)
        """

        #Read header
        with open(filename, 'r') as fil :
            headerl = [line.strip() for line in fil.readlines() if line.strip()and line.strip().startswith('#')]
        header = [line.split() for line in headerl]

        speed = 0.0
        for iline, line in enumerate(header):
            #if line[0] == "#DIRECTION" : direction = dDirToMode[int(line[2])]  # Not use for now
            if line[0] == "#NBHEADING"  : nbhead = int(line[1])
            elif line[0] == "#HEADING"    : heading = np.deg2rad( np.array( list(map(float , line[1:])) , dtype = np.float64    ))
            elif line[0] == "#DIFF"       : diff = np.array( list(map(float , line[1:])) , dtype = np.float64    )
            # elif "Water density" in headerl[iline]  : rho = float( line[ 5 ] ) // not used so far
            elif "Waterdepth" in line  :
               if line[3][:3].lower() == "inf" : waterdepth = 0.
               else : waterdepth = float(line[ 3 ])
            elif line[0] == "#QTFMODE"  : qtfmode = line[1]
            elif "Ref.pt incident wave" in headerl[iline] :
               waveRefPoint = np.array( [float(line[6].strip("(")), float(line[7].strip(")"))], dtype=np.float64 )
            elif line[0] == "#COORD" :   refPoint = np.array( list(map(str, line[1:] )), dtype=np.float64)
            elif "Forward speed" in headerl[iline]:
                speed = float(headerl[iline].split()[4])    #"#  Forward speed : N m/s"

        nbdiff = len(diff)
        data = np.loadtxt(filename)
        nbfreq = int(len(data) / nbhead)
        freq = data[0:nbfreq  ,0]

        if qtfmode == "Diff" : mode = _Spectral.QtfMode.DIFF
        elif qtfmode == "Sum" : mode = _Spectral.QtfMode.SUM
        else : raise (Exception)


        #Values
        values = np.empty((nbhead, nbfreq, nbdiff, 1), dtype=complex)
        for ihead in range(nbhead):
            for ifreq in range(nbfreq):
                for idiff in range(nbdiff):
                    values[ihead, ifreq, idiff, 0] = complex(data[nbfreq*ihead+ifreq, 1+2*idiff],
                                                             data[nbfreq*ihead+ifreq, 2+2*idiff])


        return cls(b=heading, w=freq, dw=diff, reIm=values,
                   qtfStorageType=_Spectral.QtfStorageType.W_DW,
                   forwardSpeed=speed, refPoint=refPoint,
                   waveRefPoint=waveRefPoint, modes=[_Spectral.Modes.NONE,],
                   qtfMode=mode, depth = waterdepth)

    @classmethod
    def ReadHstarH5(cls, fileName, mode="r"):   # aka Opera's GetQTF(filename, mode="r") method
        """ read Qtf from hdf5 file format. Imported from Opera """
        # Added 5 additional attributes
        import xarray
        data = xarray.open_dataset(fileName)
        # Read the required data
        assert(len(data.mode) == 6)
        b = np.asanyarray(np.radians(data.heading))
        w = np.asanyarray(data.frequency_qtf)
        dw = np.asanyarray(data.diff_frequency)
        # FIXME information on ref pt, wave ref point and COG not in qtf file...
        try:
            # normally, ref_point and ref_wave are the values and not are attributes, but
            # previously they were treated as attributes. To keep the compatibility it was modified as the following:
            refPoint = np.asanyarray(data.attrs.get("ref_point", data.ref_point))
            if len(refPoint.shape) > 1:     # refPoint(1, 3), for example
                print(f"refPoint.shape has at least dimension {len(refPoint.shape):} > 1")
                if refPoint.shape[0] > 1:   # refPoint(2, 3), for example (multibody case)
                    for i in range(1, refPoint.shape[0]):
                        if abs(refPoint[i,0] -refPint[0,0]) +abs(refPoint[i, 1] -refPoint[0, 1]) +abs(refPoint[i, 2] -refPoint[0, 2]) > 1.e-10: 
                            raise Exception(f"Spectral.Qtf.ReadHstarH5 does not support the mutlibody case with different reference points. refPoint.shape = {refPoint.shape:}")
                else:                       # refPoint(1, 3) => refPoint(3)
                    refPoint = refPoint.reshape(3)
            #print(f"refPoint.shape = {refPoint.shape:}")
            waveRefPoint = np.asanyarray(data.attrs.get("ref_wave", data.ref_wave))     # normally it should be waveRefPoint(2)
            forwardSpeed = data.attrs["speed"]
            depth        = data.attrs["depth"]
        except:
            refPoint = np.zeros(3, dtype=float)
            waveRefPoint = np.zeros(2, dtype=float)
            forwardSpeed = 0.0
            depth   = -1.0
        # Create the complex array
        qtf_re = data.qtf_re.transpose("body", "heading", "frequency_qtf", "diff_frequency", "mode")
        qtf_im = data.qtf_im.transpose("body", "heading", "frequency_qtf", "diff_frequency", "mode")
        qtf = np.asanyarray(qtf_re[0, :, :, :, :] + 1.j * qtf_im[0, :, :, :, :])
        data.close()
        return cls(b, w, dw, qtf, _Spectral.QtfStorageType.W_DW, refPoint, waveRefPoint, forwardSpeed = forwardSpeed, depth = depth)

    def writeHstarH5(self, filename):
        import xarray
        qtf_re = np.expand_dims(np.real(self.getComplexData()), axis = 0)   # Adding additional dimmension "body"
        qtf_im = np.expand_dims(np.imag(self.getComplexData()), axis = 0)
        ds = xarray.Dataset(
                            data_vars = {
                                # qtf_re and qtf_im: The DIMENSION_LABELS are written in different order than the data axis because after
                                # the creation of the Dataset, qtf_im and qtf_re are "xarray.DataArray.transposed", i.e. the order of the axis is changed accroding
                                # to the correct "DIMENSION_LABELS" attribute.
                                        "qtf_re"            : (["body", "heading", "frequency_qtf", "diff_frequency", "mode"], qtf_re, {"DIMENSION_LABELS": ["body", "diff_frequency", "frequency_qtf", "heading", "mode"]}),
                                        "qtf_im"            : (["body", "heading", "frequency_qtf", "diff_frequency", "mode"], qtf_im, {"DIMENSION_LABELS": ["body", "diff_frequency", "frequency_qtf", "heading", "mode"]}),
                                        "body"              : np.array([1], dtype = np.int32),
                                        "diff_frequency"    : self.getDeltaFrequencies(),
                                        "frequency_qtf"     : self.getFrequencies(),
                                        "heading"           : np.rad2deg(self.getHeadings()),
                                        "mode"              : self.getModes(),
                                        },
                            coords    = {
                                        },
                            attrs     = {
                                        "ref_point" : self.getReferencePoint(),
                                        "Rho"       : np.array([1025.0]),
                                        "speed"     : np.array([self.getForwardSpeed()]),
                                        "depth"     : np.array([self.getDepth()]),
                                        "ref_wave"  : self.getWaveReferencePoint(),
                                        "g"         : np.array([9.81]),
                                        }
                            )
        ds["qtf_im"] = ds.qtf_im.transpose("body", "diff_frequency", "frequency_qtf", "heading", "mode")
        ds["qtf_re"] = ds.qtf_re.transpose("body", "diff_frequency", "frequency_qtf", "heading", "mode")
        encoding = {"qtf_im"            : {"_FillValue": None},
                    "qtf_re"            : {"_FillValue": None},
                    "body"              : {"_FillValue" : None},
                    "diff_frequency"    : {"_FillValue" : None},
                    "frequency_qtf"     : {"_FillValue" : None},
                    "heading"           : {"_FillValue" : None},
                    "mode"              : {"_FillValue" : None},
                   }
        #ds.to_netcdf(filename, engine = "h5netcdf", encoding = encoding, invalid_netcdf = True)
        ds.to_netcdf(filename, encoding = encoding)
        return ds

    def to_DataArray(self):
        """Convert to xarray labeled array
        

        Returns
        -------
        res : xarray.DataArray
            QTF data as xarray.DataArray

        """
        import xarray
        res = xarray.DataArray( self.cvalues, 
                                dims = ("heading" , "w1" , "dw", "mode"),
                                coords = { "heading" : self.head,
                                           "w1" : self.freq,
                                           "dw" : self.diff,
                                           "mode" : self.getModes() 
                                           },
                                )
        return res
        
    


    def to_DataFrame( self, heading, imode = 0, flat = False ) :
        """
        Convert to pandas dataFrame
        """
        da = self.to_DataArray()
        da = da.loc[ heading, : , :, da.mode[imode]]
        
        if not flat : 
            return da.to_dataframe(name = "qtf").loc[: , "qtf"].unstack()
        else : 
            df = da.to_dataframe(name = "qtf").loc[: , "qtf"].reset_index()
            df.loc[: , "w_mean"] = df.loc[: , "w1"] + 0.5 * df.loc[: , "dw"]
            df.loc[: , "w2"] = df.loc[: , "w1"] + df.loc[: , "dw"]
            return df
    
    
    
    

    @staticmethod
    def compare_metadata( qtf1 , qtf2 ) :
        """
        """
        if qtf1.getSumMode() != qtf2.getSumMode() : 
            return False
        if qtf1.getForwardSpeed() != qtf2.getForwardSpeed() : 
            return False
        if qtf1.getDepth() != qtf2.getDepth() : 
            return False
        if len(qtf1.getHeadings()) != len(qtf2.getHeadings()) : 
            return False
        if not np.isclose( qtf1.getHeadings() ,  qtf2.getHeadings()).all() : 
            return False
        if len(qtf1.getFrequencies()) != len(qtf2.getFrequencies()) : 
            return False
        if not np.isclose( qtf1.getFrequencies() ,  qtf2.getFrequencies()).all() : 
            return False
        if not np.isclose( qtf1.getReferencePoint() ,  qtf2.getReferencePoint()).all(): 
            return False
        if not np.isclose( qtf1.getWaveReferencePoint() ,  qtf2.getWaveReferencePoint()).all(): 
            return False
        
        return True
        
    @classmethod
    def MergeQtf_Diff(cls, qtf1, qtf2, checkUniformness = True):
        # simple checks
        # qtfMode

        if not Qtf.compare_metadata( qtf1 , qtf2 ) : 
            raise(Exception( "Cannot merge Qtf" ))
            
        diff1 = qtf1.getDeltaFrequencies()
        ndiff1 = len(diff1)

        diff2 = qtf2.getDeltaFrequencies()
        
        newdiff = np.array( list(diff1) + list(diff2) )

        tmp_values = np.empty((qtf1.nbhead, qtf1.nbfreq, len(newdiff), qtf1.getNModes()), dtype = complex)
        tmp_values[ :, :, :ndiff1 , : ] = qtf1.cvalues[:, :, : , :]
        tmp_values[ :, :, ndiff1: , : ] = qtf2.cvalues[:, :, : , :]
        
        #sort and remove duplicate
        sortedDiff, b = np.unique( newdiff , return_index = True)
        values = np.empty((qtf1.nbhead, qtf1.nbfreq, len(sortedDiff), qtf1.getNModes()), dtype = complex)
        values[:,:, : ,:] = tmp_values[:,:,b,:]

        
        qtfStT  = _Spectral.QtfStorageType.W_DW
        qtfMode = _Spectral.QtfMode.SUM if qtf1.getSumMode() > 0 else _Spectral.QtfMode.DIFF
        
        return cls(b=qtf1.getHeadings(),                      # b: numpy.ndarray[float64[m, 1]]
                   w=qtf1.getFrequencies(),                   # w: numpy.ndarray[float64[m, 1]]
                   dw=sortedDiff,                             # dw: numpy.ndarray[float64[m, 1]]
                   modes = qtf1.getModes(),                   # modes: numpy.ndarray[int32[m, 1]]
                   reIm=values,                               # reim: eigen::tensor<t, r, 0>
                   qtfStorageType= qtfStT,                    # qtfstoragetype: _spectral.qtfstoragetype
                   refPoint=qtf1.getReferencePoint(),         # refpoint: numpy.ndarray[float64[3, 1]]
                   waveRefPoint=qtf1.getWaveReferencePoint(), # waverefpoint: numpy.ndarray[float64[2, 1]]
                   qtfMode=qtfMode,                           # qtfmode: _spectral.qtfmode = qtfmode.diff
                   forwardSpeed = qtf1.getForwardSpeed(),     # forwardspeed: float = 0.0
                   depth = qtf1.getDepth())                   # depth: float = -1.0


    def write(self, filename):
        with open(filename, "w") as f:
            f.write("# Project : \n")                   # f.write("# Project : "+self.project +"\n")
            f.write("# User    : \n")                   # f.write("# User    : "+self.user +"\n")
            f.write("# File : \n")                      # f.write("# File : "+self.fileName +"\n")
            f.write("# Constants used in computations :\n")
            f.write("#     Reference length     : {:>10s} \n".format("1.0000"))     # f.write("#     Reference length     : {:>10s} \n".format(self.refLen))
            f.write("#     Water density (rho)  : {:>10s}\n".format("1025.0000"))   # f.write("#     Water density (rho)  : {:>10s}\n".format(self.rho))
            f.write("#     Gravity acceleration : {:>10s}\n".format("9.8100"))      # f.write("#     Gravity acceleration : {:>10s}\n".format(self.g))
            if self.getDepth() > 0.0:
                f.write("#     Waterdepth           : {:10.4f} \n".format(self.getDepth()))
            else:
                f.write("#     Waterdepth           :  Inf. \n")
            wrp = self.getWaveReferencePoint()
            f.write("#     Ref.pt incident wave : (   {:10.4f}{:10.4f})\n".format(wrp[0], wrp[1]))
            f.write("#            Forward speed : {:8.4f}  m/s   \n".format(self.getForwardSpeed()))
            f.write("#\n")
            f.write("#------------------------------------------------------------------------\n")
            f.write("#QTFTYPE \"{:s}\"\n".format("2RWE"))         #f.write("#QTFTYPE \"{:s}\"\n".format(self.qtfType))
            f.write("#CPLXTYPE {:s}\n".format("0"))       #f.write("#CPLXTYPE {:s}\n".format(self.cplxType))
            if self.getSumMode() > 0.:
                f.write("#QTFMODE {:s}\n".format("Sum"))
            else:
                f.write("#QTFMODE {:s}\n".format("Diff"))
            f.write("#DIRECTION  \"{:>12s}\n".format("0"))   # f.write("#DIRECTION  \"{:>12s}\n".format(self.direction))
            rp = self.getReferencePoint()
            f.write("#COORD   {:9.4f}{:9.4f}{:9.4f}\n".format(rp[0], rp[1], rp[2]))
            f.write("#NBHEADING{:4d}\n".format(self.getNHeadings()))
            f.write("#HEADING")
            for h in self.getHeadings():
                f.write("{:12.2f}".format(h *180./np.pi))
            f.write('\n')
            f.write("#DIFF")
            for d in self.getDeltaFrequencies():
                f.write("{:24.5f}".format(d))
            f.write("\n")
            f.write("#---w(r/s)-----------------------------------------------------\n")
            nbhead = self.getNHeadings()
            headings = self.getHeadings()
            nbfreq = self.getNFrequencies()
            freq   = self.getFrequencies()
            nbdiff = self.getNDeltaFrequencies()
            values = self.getComplexData()
            for ihead in range(nbhead):
                f.write("#Heading ={:8.2f}\n".format(headings[ihead] *180./np.pi))
                for ifreq in range(nbfreq):
                    f.write("{:13.4e}".format(freq[ifreq]))
                    for idiff in range(nbdiff):
                        f.write("{:13.4e}".format(np.real(values[ihead, ifreq, idiff, 0])))
                        f.write("{:13.4e}".format(np.imag(values[ihead, ifreq, idiff, 0])))
                    f.write("\n")
                f.write(" \n \n")





    def getHeadDataFrame( self , heading ) :
        """
        Return a dataframe w / diff corresponding to heading.
        """

        ihead = np.argmin( np.abs(self.head - heading) )
        # FIXME only one component in order to have a 2D array
        return pd.DataFrame( index = self.freq , data = self.getComplexData()[ihead, :, :, 0] ,  columns = self.diff , dtype = complex )



    def plot2D( self , headDeg, fun = np.abs, ax = None, rotation = "w1-w2"  ) :
        """Surface plot of the QTF

        Parameters
        ----------
        headDeg : float
            Heading to plot, in degree
        fun : function
            Part to plot, for instance, np.imag, np.real. The default is np.abs.
        ax : matplotlib axe    
            Where to plot the figure. The default is None.
        rotation : str, optional
            Among [ "w-dw", "w1-w2"] . The default is "w1-w2".

        Returns
        -------
        ax : matplotlib axe
            The matplotlib graph
          
        """
        
        if ax is None : 
            fig , ax = plt.subplots()
            df = self.to_DataFrame( np.deg2rad(headDeg), flat = True )
            if rotation == "w-dw" :
                ax.tricontourf(  df["w_mean"].values , df["dw"].values , fun(df["qtf"].values), 100 )
                ax.set_xlabel ( r"$\frac{\omega_1+\omega_2}{2}$" )
                ax.set_ylabel ( r"$d\omega$" )
            elif rotation == "w1-w2":
                df_sym = copy.deepcopy(df)
                df_sym.loc[:,"qtf"] = np.conj(df_sym["qtf"])
                df = df.rename( columns={"w1":"w2" , "w2":"w1" } )
                df = pd.concat( (df_sym, df) , ignore_index = True, sort = False)
                ax.tricontourf( df["w1"], df["w2"], fun(df["qtf"].values), 100  )
                ax.set_xlabel ( r"$\omega_1$" )
                ax.set_ylabel ( r"$\omega_2$" )
            else : 
                raise(Exception( f"Rotation {rotation:} not known" ))
        return ax
    
    
    def plot( self, headingDeg, how = "dw", ax = None, part = np.abs ,imode = 0, color_bar = True, **kwargs ):
        """Plot the QTF along the chosen axis
        
        Parameters
        ----------
        headingDeg : float
            Heading to plot, in degree
        how : str, optional
            Which x axis (w, or dw). The default is "dw".
        ax : ax or None, optional
            ax where to plot the graph. The default is None.
        part : TYPE, optional
            Complex part of the QTF (np.abs, np.imag... ). The default is np.abs.
        imode : int, optional
            Mode to plot. The default is 0.
        **kwargs : 
            Keywords arguments passed to ax.plot()

        Returns
        -------
        ax : ax
            ax with QTF plot

        """
        from Snoopy.PyplotTools import getColorMappable
        
        if ax is None :
            fig, ax = plt.subplots()
            
        df = part(self.getHeadDataFrame( heading = np.deg2rad(headingDeg) ))
        
        if how == "dw" :
            df = df.transpose()
            c = getColorMappable(vmin = 0.0 , vmax = np.max(df.columns))
            for w in df.columns:
                ax.plot( df.index.values , df[w].values, color = c.to_rgba(w), label = f"w = {w:}rad/s" if not color_bar else None , **kwargs )
            ax.set_xlabel( r"$d\omega$ (rad/s)" )
        elif how == "w":
            c = getColorMappable(vmin = 0.0 , vmax = np.max(df.columns))
            for dw in df.columns:
                ax.plot( df.index.values , df[dw].values, color = c.to_rgba(dw), label = f"dw = {dw:}rad/s" if not color_bar else None , **kwargs )
            ax.set(xlabel = "Frequency (rad/s)")
                
        if color_bar : 
            ax.get_figure().colorbar(c).set_label( r"$d\omega (rad/s)$" if how == "w" else r"$\omega (rad/s)$")
        else:
            ax.legend()
            
        
        return ax
    
