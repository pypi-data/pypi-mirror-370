from io import StringIO
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import warnings
import re
from Snoopy import Spectral as sp
from Snoopy import logger
from Snoopy import Math as smath
import _Spectral


def readMetaData(str_) :
    """Parse RAO header (HydroStar format) to get RAO metadata
    """
    def _simpleConvert(line):
        raw = l.split(":")[1].strip()
        if raw == "None":
            return None
        else:
            return float(raw)
    meta = {}
    for l in str_ :
        ls = l.strip().split()
        if "Forward speed" in l : meta["forwardSpeed"] = float(  ls[4] )
        elif "RAOTYPE" in l : type_ =  l.strip().split() [2]
        elif "COMPONENT" in l : component =  int( ls[2] )
        elif "MEANVALUE" in l : meta["meanValues"] =  [float( ls[3] )]
        elif "Reference point" in l : meta["refPoint"] =  [float( i ) for i in l.strip()[:-1].split()[-3:] ]
        elif "incident wave" in l : meta["waveRefPoint"] =  [float( i ) for i in l.strip()[:-1].split()[-2:] ]
        elif "Waterdepth" in l :
            if ls[3] == "Inf.": meta["depth"] = 0.
            else: meta["depth"] = float( ls[3] )
        #elif "UNIT" in l : meta["unit"] = ls[2]
        elif "Water density" in l:
            meta["rho"] = _simpleConvert(l)
        elif "Gravity acceleration" in l:
            meta["grav"]  = _simpleConvert(l)
        elif "#---m" in l:
            meta["is_wrt_rads"] = False  # RAO with the section x-coordinate (internal loads along sections).

    meta["modes"] = [ sp.Modes( sp.modesTypeComponentToIntDict.get( ( type_, component ) , 0 ) ) ]

    return meta


"""Class to handle transfer function
    For rapid prototyping, back and forth with pandas are used.
    Most of the routines could be transfer to the c++ base class.
"""
class Rao(_Spectral.Rao) :
    """Response Amplitude Operator data definition, called Rao here.

    Rao terms are obtained from a first order diffraction-radiation analysis.
    They correspond to the mean loads applied to the vessel
    when subjected to an Airy wave.
    They are calculated for given vessel motion coordinates called here modes.
    The Rao are then available for Nm modes, but also for
    a limited number Nb of incidences relative to the vessel heading,
    and of wave frequencies Nf.

    Rao is then a Nb x Nf x Nm matrix.

    """

    def __init__(self,*args,**kwargs):
        """Construct the RAO object.

        The based class is in c++, and several constructor are available (see below example). Most of the time, the Rao object is build from a datafile (HydroStar format)

        Parameters
        ----------
        filename : str
            Name of the HydroStar rao output
            
        Parameters
        ----------
        b : np.ndarray
            Headings (in radians)
        w : np.ndarray
            wave frequencies
        module : np.ndarray, optional*
            Qtf module value (n_heading * n_freq * n_mode)
        phase : np.ndarray, optional*
            Qtf module value (n_heading * n_freq * n_mode)
        cvalue : np.ndarray, complex, optional*
            Qtf module value (n_heading * n_freq * n_mode)
        modes : np.ndarray, optional 
            modes
        modeCoefficients : np.ndarray, optional 
            modes
        refPoint : np.ndarray
            Reference point
        waveRefPoint : np.ndarray
            Phase reference point
        forwardSpeed : float, optional
            Forward speed. The default is 0.0.
        depth : float, optional
            waterdepth. The default is -1.0.

        Example
        -------
        >>> # From file
        >>> rao1 = sp.Rao( filename = "heave.rao" )
        >>> # Copy constructor
        >>> rao2 = sp.Rao( rao  )
        >>> # From variable
        >>> rao3 = sp.Rao( w =[0.1, 0.2], b = [np.pi] , module = np.ones( (1,2,1) ) ,phase = np.zeros( (1,2,1) ),  refPoint = [0.,0.,0.], waveRefPoint = [0., 0.])
        """
        
        if len(args) == 1 and type(args[0]) == str :
            kwargs =  parse_rao_file( args[0])
            args = []
        elif "filename" in kwargs :
            kwargs = parse_rao_file( **kwargs)
        rho = kwargs.pop("rho", None)
        grav = kwargs.pop("grav", None)
        is_wrt_rads = kwargs.pop("is_wrt_rads", True)  # True if keyword not present.

        try:
            if len(args) > 0 and rho is None and grav is None :
                if isinstance( args[0] , sp.Rao):
                    rho, grav = args[0].rho, args[0].grav
                elif (isinstance( args[0] , list) or isinstance( args[0] , tuple)) and ( len(args) < 2) and len(kwargs) == 0 :
                    if isinstance( args[0][0], sp.Rao ):
                        rho, grav = args[0][0].rho, args[0][0].grav
            super().__init__(*args,**kwargs)
        except TypeError:
            # Analyse signature for clearer error message:
            check_input_signature(kwargs)

        self.rho = rho
        self.grav = grav
        self._is_wrt_rads = is_wrt_rads  # True if internal loads along sections.

    def __str__(self) :

        dw = "(step = {:.1f})".format( self.getdw() ) if self.getdw() > 0 else ""
        db = "(step = {:.1f})".format( np.rad2deg( self.getdb())) if self.getdb() > 0 else ""

        s = "#------ RAO object ----------#\n"
        with np.printoptions(precision=1, suppress=True) :
            s +=  "Frequency : {:} from {:.3g} to {:.3g} {:}\n".format( self.nbfreq , self.freq.min() , self.freq.max(), dw)
            s +=  "Headings  : {:} from {:} to {:} {:}\n".format( self.nbhead , np.rad2deg(self.head).min() , np.rad2deg(self.head).max(), db)
            s +=  "Speed     : {:} m/s\n".format( self.getForwardSpeed() )
        s +=  "Max value : {:}\n".format( np.max(self.module) )


        if len(np.unique( self.modesNames )) == 1 :
            s += f"RAO type : {self.modesNames[0]:} ({self.getUnits()[0]:})\n"
        else :
            s += f"RAO type : {self.modesNames:}\n"

        c = self.getModeCoefficients()
        if len(np.unique( c )) > 1 :
            s += f"Coefficients :  from  {np.min(c):} to {np.max(c):}\n"

        return s

    def isRao(self):
        """Check if data are actually transfer function.

        Rao object is sometimes used as a dirty shortcut to save/load added-mass and wave damping coefficients.

        Returns
        -------
        bool
            True if RAOs is actually a transfer function.
        """
        return  np.all( [not t in ["WAVE-DAMPING" , "ADDED-MASS"] for t in self.getType() ] )

    def isWRTrads(self) -> bool:
        """Check if data are with respect to wave frequencies or meters (internal loads along sections).

        Returns
        -------
        bool
            True if RAOs are with respect to wave frequencies.
        """
        return  self._is_wrt_rads


    def getType(self):
        """Return RAO type."""
        return sp.modesDf.set_index( "INT_CODE").loc[self.getModes(),"TYPE"]

    def isClose( self, rao , rtol = 1e-5 ):
        """Compare current RAO values to an other one

        Parameters
        ----------
        rao : Rao
            RAO to be compared with

        Returns
        -------
        close : bool
            True if RAOs are close

        """

        if not rao.module.shape == self.module.shape  :
            return False

        close = np.isclose( self.cvalues , rao.cvalues, rtol = rtol).all()

        return close


    def getUnits(self) :
        return sp.modesDf.loc[self.modesNames , "HSTAR_UNIT"].values


    @property
    def unit(self):
        uniqueUnits = list(set( self.getUnits() ))
        if len( uniqueUnits ) == 1 :
            return uniqueUnits[0]
        else :
            return "N/A"

    @property
    def waterdepth(self):
        return self.getDepth()


    @property
    def head(self):
        return self.getHeadings()

    @property
    def coef(self):
        return self.getModeCoefficients()

    @property
    def headDeg(self):
        return np.rad2deg( self.getHeadings() )

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
    def cvalues(self):
        return self.getComplexData()

    @property
    def module(self) :
        return self.getModules()

    @property
    def phasis(self) :
        return self.getPhases()

    @property
    def real(self) :
        return self.getReal()

    @property
    def imag(self) :
        return self.getImag()

    @property
    def modesNames(self):
        return sp.modesDf.reset_index().set_index("INT_CODE").loc[  self.getModes() , "NAME" ].values


    def to_RaoArray(self):

        return np.array( [ self.getRaoAtMode(imode) for imode in range( self.getNModes() ) ] )

    def is6DOF(self):
        """Check if RAOs corresponds to 6 DOF motions.

        Returns
        -------
        check : Boolean
            Return True if 6 DOF
        """
        check = (self.getModes() == np.array([1,2,3,4,5,6])).all()
        return check

    def is6Load(self):
        """Check if RAOs corresponds to 6 DOF loads (or internal loads).

        Returns
        -------
        check : Boolean
            Return True if 6 DOF loads
        """
        check = (self.getModes() == np.array([7,8,9,10,11,12])).all() or (self.getModes() == np.array([15,16,17,18,19,20])).all()
        return check


    def getDerivate( self , n = 1 , update_mode = False) :
        """Derive a RAO object

        Parameters
        ----------
        n : int, optional
            order of derivation, by default 1

        derivate_on_mode : bool, optional
            change the mode object accordingly, by default False
            if derivate_on_mode == True:
                mode object of motion will become velocity with n = 1 or acceleration with n = 2
                mode object of velocity will become acceleration with = 2
                other will be set to unknown

        Returns
        -------
        sp.Rao
            The differentiated RAO
        """

        tmp_ = _Spectral.Rao.getDerivate( self, n )
        out = self.__class__(tmp_,rho=self.rho,grav=self.grav)
        # Modes object also need to be changed here
        if update_mode:
            out.modes = derivateMode(out.modes,n)
            return out
        else:
            return out

    def getRaoAtFrequencies(self, *args, **kwargs) :
        """Get new RAO with values interpolated at given frequencies

        Parameters
        ----------
        values : np.ndarray
            Frequencies (rad/s)

        Returns
        -------
        sp.Rao
            The interpolated RAO
        """
        return self.__class__(  _Spectral.Rao.getRaoAtFrequencies(self, *args, **kwargs) ,rho=self.rho,grav=self.grav )

    def getRaoAtHeadings_withoutInterpolation(self, headings) :
        if not isinstance(headings,list):
            heading = [headings]
        existing_headings = self.getHeadings()
        found_heading = []
        all_idx = []
        for heading in headings:
            idx = np.where(existing_headings == heading)
            if (len(idx) == 0):
                logger.warning( f"Can't extract heading = {heading} without doing interpolation/extrapolation." )
            else:
                all_idx.append(idx[0][0])
                found_heading.append(heading)
        new_cvalue = self.cvalues[all_idx,:,:]

        return self.clone(b = found_heading,cvalues = new_cvalue)


    def getRaoAtHeadings(self, *args, **kwargs) :
        """Get new RAO with values interpolated at given headings

        Parameters
        ----------
        values : np.ndarray
            Headings (rad)

        Returns
        -------
        sp.Rao
            The interpolated RAO
        """
        return self.__class__(  _Spectral.Rao.getRaoAtHeadings(self, *args, **kwargs) ,rho=self.rho,grav=self.grav )


    def getRaoAtModeCoefficients(self, *args, **kwargs) :
        """Get new RAO with values interpolated at given "mode coefficients"

        Parameters
        ----------
        values : np.ndarray
            Coefficients (linearisation parameter)

        Returns
        -------
        sp.Rao
            The interpolated RAO
        """
        return self.__class__(  _Spectral.Rao.getRaoAtModeCoefficients(self, *args, **kwargs),rho=self.rho,grav=self.grav  )


    def getRaoIn2piRange(self, *args, **kwargs) :
        """Get new RAO with heading sorted and in [0, 2*pi]

        Returns
        -------
        sp.Rao
            Sorted RAO
        """
        return self.__class__(  _Spectral.Rao.getRaoIn2piRange(self, *args, **kwargs) ,rho=self.rho,grav=self.grav )



    def clone(self,**kwargs):
        """Create new rao obj that are similar to self but with desired modifications
        All the different we want to made to self will be pass as arguments via kwargs
        Returns
        -------
        Rao
            New object of class Rao that are similar to self
        """
        metadata = Rao.getMetaData(self)
        metadata.update(kwargs)
        modes = metadata.pop("modes")
        meanValues = metadata.pop("meanValues")
        modesCoefficients = metadata.pop("modesCoefficients")
        b = metadata.pop("b",self.head)
        w = metadata.pop("w",self.freq)
        if "cvalues" in metadata.keys():
            phase = metadata.pop("phase",self.phasis)
            module = metadata.pop("module",self.module)
            cvalues = metadata.pop("cvalues")

            return self.__class__(  b=b, w=w,
                                    cvalue = cvalues,
                                    modes=modes,
                                    meanValues = meanValues,
                                    modesCoefficients = modesCoefficients,
                                    **metadata )
        else :
            phase = metadata.pop("phase",self.phasis)
            module = metadata.pop("module",self.module)
            return self.__class__(  b=b, w=w, module=module,
                                    phase=phase, modes = modes,
                                    meanValues = meanValues,
                                    modesCoefficients = modesCoefficients,
                                    **metadata )

    # Handling modes
    @property
    def modes(self):
        return [_Spectral.Modes(modeID) for modeID in self.getModes() ]

    @modes.setter
    def modes(self,val):
        if isinstance(val,list):
            modes = self._convertToRaoMode(val)
        else:
            modes = [self._convertToRaoMode(val)]
        self.setModes(modes)

    @classmethod
    def _convertToRaoMode(cls,val):
        if isinstance(val,int):
            return _Spectral.Modes(val)
        elif isinstance(val,_Spectral.Modes):
            return val
        elif isinstance(val,tuple):
            if not len(val) == 2:
                raise SyntaxError(f"Fail to convert tuple {val} to Rao Mode object")
            return sp.getModes(*val)
        elif isinstance(val,list):
            return [cls._convertToRaoMode(item) for item in val]



    def __add__(self , rhs):
        tmp_ = _Spectral.Rao.__add__( self, rhs  )
        return self.__class__(tmp_,rho=self.rho,grav=self.grav)

    def __iadd__(self, rhs):
        _Spectral.Rao.__iadd__(self, rhs)
        return self

    def __sub__(self , rhs):
        tmp_ = _Spectral.Rao.__sub__( self, rhs  )
        return self.__class__(tmp_,rho=self.rho,grav=self.grav)

    def __isub__(self, rhs):
        _Spectral.Rao.__isub__(self, rhs)
        return self

    def __mul__(self , rhs):
        tmp_ = _Spectral.Rao.__mul__( self, rhs  )
        return self.__class__(tmp_,rho=self.rho,grav=self.grav)

    __rmul__ = __mul__

    def __imul__(self , rhs):
        _Spectral.Rao.__imul__( self, rhs  )
        return self

    def __truediv__(self , rhs):
        tmp_ = _Spectral.Rao.__truediv__( self, rhs  )
        return self.__class__(tmp_,rho=self.rho,grav=self.grav)

    def __itruediv__(self , rhs):
        _Spectral.Rao.__itruediv__( self, rhs  )
        return self

    def getClosestHeadingIndex(self, heading) :
        return np.argmin(  ( self.head-heading ) % (2*np.pi ) )


    def getRaoAtMode(self, imode) :
        """Return a single RAO corresponding to the i mode position.

        Useful for routines working with single RAOs

        Parameters
        ----------
        imode : int
            Position of the mode in array

        Returns
        -------
        Rao
            Rao at imode position

        """
        metadata = Rao.getMetaData(self)
        mode = metadata.pop("modes")
        meanValues = metadata.pop("meanValues")
        modesCoefficients = metadata.pop("modesCoefficients")

        return self.__class__(  b=self.head, w=self.freq, module=self.module[:,:,[imode]],
                                phase=self.phasis[:,:,[imode]], modes = [ mode[imode] ],
                                meanValues = [meanValues[imode]],
                                modesCoefficients = [modesCoefficients[imode]],
                                **metadata )


    @staticmethod
    def getMetaData(obj):
        """Get metadata from either RAO or generated pandas dataFrame.
        """
        def _get(val):
            return sp.modesDict[val]
        return { "forwardSpeed" : obj.getForwardSpeed(),
                 "refPoint" : obj.getReferencePoint(),
                 "waveRefPoint" : obj.getWaveReferencePoint(),
                 "modes" : obj.getModes(),
                 "modesCoefficients" : obj.getModeCoefficients(),
                 "meanValues" : obj.getMeanValues(),
                 "depth" : obj.getDepth(),
                 "rho"        : obj.rho,
                 "grav"       : obj.grav }


    @classmethod
    def ReadHstar( cls, filename, blockIndex = None, Beq = None ) :
        return cls(**parse_rao_file( filename, blockIndex = blockIndex, Beq = Beq))
        

    def hstarHeader( self, filename = "None", imode = 0 ) :
        """Write metadata to HydroStar format.
        """

        template = """# Project :
# User    : Written by Snoopy library
# File : {filename:}
#
# Constants used in computations :
#     Reference length     :     1.0000
#     Water density (rho)  :     {rho}
#     Gravity acceleration :     {grav}
#     Waterdepth           :  {waterdepth:}
#     Ref.pt incident wave : (     {waveX:.4f}   {waveY:.4f})
#            Forward speed :   {speed:.4f}  m/s
#
# Reference point of body 1: (   {refX:.4f}   {refY:.4f}  {refZ:.4f})
# MEANVALUE :   {mean:.5e}
#   AMP/PHASE
#------------------------------------------------------------------------
#RAOTYPE    :  {raoType:}
#COMPONENT  :  {component:}
#UNIT       :  {unit:}
#NBHEADING  {nbHeading:}
#HEADING  {headingList:}
#---w(r/s)-----------------------------------------------------
"""
        rho = getattr(self,"rho",None)
        grav = getattr(self,"grav",None)
        type_, component = sp.modesIntToTypeComponentDict.get( self.getModes()[imode], 0 )

        refPoint = self.getReferencePoint()
        waveRefPoint = self.getWaveReferencePoint()
        header = template.format(
                                 filename = filename,
                                 waterdepth = "Inf." if self.waterdepth < 0 else self.waterdepth,
                                 waveX = waveRefPoint[0],
                                 waveY = waveRefPoint[1] ,
                                 speed = self.getForwardSpeed(),
                                 refX = refPoint[0],refY = refPoint[1],refZ = refPoint[2],
                                 component = component,
                                 nbHeading = self.nbhead,
                                 headingList = "  ".join(["{:11.2f}".format(h) for h in np.rad2deg(self.head)]) ,
                                 mean = self.getMeanValues()[imode],
                                 raoType = type_,
                                 unit = self.unit,
                                 rho = rho,
                                 grav = grav
                                )

        return header




    def get_opposite_side(self):
        """Return starboard transfer function from portside transfer function

        Returns
        -------
        sp.Rao
        """

        if self.getNModes() != 1:
            raise(Exception( "get_opposite_side is only for single RAOs"))

        df = self.toDataFrame( cplxType = "cvalues" )
        df.columns = (2*np.pi - df.columns)
        df.sort_index( axis = 1 , inplace = True)

        metaData = sp.Rao.getMetaData(self)
        metaData["refPoint"] = np.array( [metaData["refPoint"] [0] , -metaData["refPoint"][1] , metaData["refPoint"][2] ]  )

        return sp.Rao.FromDataFrame( df , metaData  = metaData )



    def _dataString(self, imode=0, is_real_number = False):
        """Returns data as string (use to write files).

        For complex numbers (actual RAOs) the string is composed of 2 blocks: left is module, right is phase (deg). 
        If "is_real_number" is True, only one block is used, and value can be negative (this is a short-cut to handle added-mass and wave-damping for visualization in HstarIce).

        Parameters
        ----------
        imode : int
            mode to write
        is_real_number : bool
            Data is real (used for added-mass or wave-damping). Default to False.

        Returns
        -------
        str
            The string to write.
        """

        if not is_real_number : 
            m = self.toDataFrame(cplxType = "module", imode=imode)
            p = np.rad2deg(self.toDataFrame(cplxType = "phasis", imode=imode))
            df = pd.concat( [m,p] , axis = 1, join = "inner" )
        else: 
            df = self.toDataFrame(cplxType = "real", imode=imode)

        return df.to_csv(sep = ' ' , header = None, float_format = '%.6e', lineterminator='\n' )


    def write(self , filename, imode = None, is_real_number = False) :
        """Write RAO in HydroStar format.

        Parameters
        ----------
        filename : str
            File where to write the RAO.
        imode : int or None
            Mode to output. Output all None
        is_real_number : bool
            Data is real (used for added-mass or wave-damping). Default to False.

        Returns
        -------
        None.
        """
        if imode is not None :
            nBlock = 1
        else :
            nBlock = self.getNModes()
            if nBlock == 1 :
                imode = 0

        if nBlock == 1 :
            with open(filename , "w", encoding = "utf-8") as f :
                f.write(self.hstarHeader( filename= filename,imode = imode ))
                f.write(self._dataString( imode = imode, is_real_number = is_real_number ))
                f.write("#------------------------------------------------------------\n#ENDFILE {}".format(filename))
            return
        else:
            with open(filename , "w", encoding = "utf-8") as f :
                f.write(self.hstarHeader(filename))
                for i, linearDamping in enumerate(self.getModeCoefficients()) :
                    f.write("#LINPARVALUE {}\n".format(linearDamping))
                    f.write( self._dataString(imode=i, is_real_number=is_real_number) )
                    if i == nBlock-1 :
                        f.write("#-------------------------\n#ENDFILE")
                    else :
                        f.write("\n\n")


    @classmethod
    def FromDataFrame( self , df , metaData ) :
        """Construct RAO from pandas dataFrame (shortcut to use pandas to work on Rao).

        Parameters
        ----------
        df : pd.DataFrame
            The rao data
        metaData : dict
            The metadata required to construct the RAO ('forwardSpeed','refPoint','waveRefPoint'...)

        Returns
        -------
        Rao
            The RAO object
        """
        head = df.columns
        nbhead = len(head)
        freq = df.index
        nbfreq = len(freq)
        module = np.empty((nbhead, nbfreq, 1), dtype=float)
        phasis = np.empty((nbhead, nbfreq, 1), dtype=float)
        module[:, :, 0] = np.abs(df.values).transpose()
        phasis[:, :, 0] = np.angle(df.values).transpose()
        return Rao(b=df.columns, w=df.index, module=module, phase=phasis, **metaData)

    def plot(self , ax = None, part = "module", imode = 0, headingsDeg=None,
                    legend_kwargs = {"loc": 1 , "fontsize" : 8} , xAxis = "freq",
                    label_prefix = "", marker = "o", ls = "-",
                    **kwds  ) :
        """Plot the component amplitude against the frequency.

        Parameters
        ----------
        ax : axis, optional
            Plot RAO in exiusting axis. If not provided, a new figure is created. The default is None.
        part : str, optional
            Component of the RAO to be plotted ("module" or "phasis"). The default is "module".
        imode : TYPE, optional
            DESCRIPTION. The default is 0.
        headingsDeg : list of floats, optional
            List of headings to be plotted (in degrees). If not provided, all headings are plotted. The default is None.
        legend_kwargs : dict, optional
            Keyword argument passed to ax.legend()
        label_prefix : str, optional
            Prefix for curve label (before heading value). Default to ""
        marker : str, optional
            Marker style. Default to "o"
        ls : str, optional
            Line style. Default to "-"

        + keywords arguments passed to ax.plot()

        """
        if ax is None :
            fig , ax = plt.subplots()


        if xAxis.lower() == "freq" :
            xAxis_ = self.freq
            ax.set_xlabel( r"$\omega$ $(rad/s)$" )
        elif xAxis.lower() == "period" :
            xAxis_ = 2 * np.pi / self.freq
            ax.set_xlabel( r"Period $(s)$" )
        else :
            raise(Exception("Choose xAxis among ['freq', 'period']"))

        if headingsDeg is not None:
            iAndHead = []
            for b in headingsDeg :
                is_,  = np.where( np.isclose( self.headDeg , b ) )
                if len(is_) >= 1  :
                    iAndHead.append( (is_[0] , b) )
                else :
                    logger.warning( f"{b:.1f} not available in RAO" )
        else:
            iAndHead = enumerate( self.headDeg )

        for ib, b in iAndHead:
            ax.plot( xAxis_ , getattr(self, part)[ib, :, imode].transpose() , marker=marker, ls=ls, label = f"{label_prefix:}{b:.0f}°" , **kwds  )

        name = self.modesNames[imode]
        if name  != "NONE" :
            ax.set_ylabel( f"{name:} ({self.getUnits()[imode]:})" )

        ax.legend( **legend_kwargs )
        return ax


    def plotH(self, w = None, ax = None, part = "module", **kwds ) :
        """Plot the component amplitude against the heading.

        Parameters
        ----------
        w : None of float, optional
            The frequency to plot. The default is None.
        ax : axis, optional
             Plot RAO in exiusting axis. If not provided, a new figure is created. The default is None.
        part : str, optional
            Component of the RAO to be plotted ("module" or "phasis"). The default is "module".
        **kwds : any
            Argument passed to plt.plot.

        Returns
        -------
        ax : plt.Axis
            The graph.
        """
        if ax is None:
            fig, ax = plt.subplots()
        if w is None:
            for iw, w in enumerate(self.freq):
                ax.plot( self.headDeg, getattr(self, part)[:, iw, 0].transpose() , "o-", label = "{:.5f}".format(w), **kwds )
        else:
            iw = np.abs(self.freq - w).argmin()
            ax.plot( self.headDeg, getattr(self, part)[:, iw, 0].transpose() , "o-", label = "{:.5f}".format(w), **kwds )

        ax.set_xlabel( r"$\beta$ $(degrees)$" )
        ax.set_ylim( bottom = 0. , )
        ax.legend(loc = 1)
        return ax

    def _getDefaultMode(self , imode = None):
        if imode is None :
            if self.getNModes() == 1 :
                return 0
            else :
                raise(Exception("imode should be specified"))
        return imode


    def plot2D(self, imode = None , ax=None, **kwargs):
        from Snoopy.PyplotTools import dfSurface

        imode = self._getDefaultMode(imode = imode)

        if ax is None:
            fig, ax = plt.subplots()

        dfSurface( self.toDataFrame(cplxType = "module", imode=imode).transpose() , ax=ax, **kwargs )
        ax.yaxis.set_major_formatter(FuncFormatter( lambda x,p : f"{np.rad2deg(x):.1f}" ))
        ax.xaxis.set_major_formatter(FuncFormatter( lambda x,p : f"{x:.2f}" ))
        return ax




    def toDataFrame(self, cplxType = "cvalues", imode = None ) :
        """Convert to pandas dataFrame

        Parameters
        ----------
        cplxType : str, optional
            Among ["cvalues", "module", "phasis" , "real" , "imag"]
        imode : int, optional
            Mode. The default is None.

        Returns
        -------
        df : pd.DataFrame
            Dataframe
        """

        imode = self._getDefaultMode(imode)

        # Data
        df = pd.DataFrame( index = pd.Index( self.freq, name = "frequency") ,
                        columns = pd.Index( self.head , name = "heading") ,
                        data = getattr(self , cplxType)[:, :, imode].transpose(),
                        )

        #Metadata
        metadata = Rao.getMetaData(self)
        meanValues = [metadata.pop( "meanValues" )[imode] ]

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            for key , val in metadata.items() :
                setattr( df , key ,  val)
            setattr( df , "meanValues" ,  meanValues)
        return df


    def toDataArray(self) :
        """Convert to xarray.dataArray.

        Returns
        -------
        data : xarray.DataArray
            Array with all rao data and metadata as attrs.

        """
        import xarray as xa
        data = xa.DataArray( self.getComplexData() ,
                             coords = [ self.getHeadings() , self.getFrequencies() , self.getModeCoefficients()] ,
                             dims =  ['Headings' , "Frequencies" , "Coefficients" ]
                           )

        for k, v in self.getMetaData(self).items():
            data.attrs[k] = v
        return data


    @classmethod
    def FromDataArray(self, data):
        return Rao( b=data.Headings, w=data.Frequencies, cvalue = data.values, **data.attrs )


    def _checkOneMode(self, msg = "Function not available for several RAOs in one object"):
        if not self.getNModes() == 1 :
            raise(Exception( msg ))


    def getScaled( self , length_ratio , n = None ) :
        """Return scaled transfer function.

        Parameters
        ----------
        length_ratio : str
            Ratio of length
        n : float, optional
            Froude scale, if not provided, retrived from RAO type. The default is None.

        Returns
        -------
        Rao
            The scaled Rao
        """
        ns = sp.modesDf.set_index("INT_CODE").loc[ self.getModes() , "FROUDE_SCALE" ].values
        sRao = []
        for imode in range(self.getNModes() ) :
            if n is not None:
                n_ = n
            else :
                if ns[imode] is not None :
                    n_ = ns[imode]
                else :
                    raise(Exception("Unknown froude scale, n should be provided"))

            sRao.append(   self.getRaoAtMode(imode) * length_ratio**(n_ - 1 )  )

        rao = sp.Rao(sRao)
        rao.setFrequencies( rao.freq / length_ratio**0.5 )

        return rao
    
    def getAdim( self , length , n = None ) :
        """Return scaled transfer function.
    
        Parameters
        ----------
        length_ratio : str
            Ratio of length
        n : float, optional
            Froude scale, if not provided, retrived from RAO type. The default is None.
    
        Returns
        -------
        Rao
            The scaled Rao
        """
        rao = self.getScaled( length_ratio = 1 / length , n = n )
        rao.setFrequencies( rao.freq / 9.81**0.5 )
    
        return rao    


    def getSorted( self, duplicatesBounds = True ) :
        """Return Rao sorted in direction (return new instance).

        Parameters
        ----------
        duplicatesBounds : bool, optional
            Duplicate 0-360. The default is True.

        Returns
        -------
        Rao
            Rao sorted in direction
        """
        if not self.getNModes() == 1 :
            return self.getSorted_Multi(duplicatesBounds=duplicatesBounds)

        df = self.toDataFrame()
        df.columns  = np.mod( df.columns , 2*np.pi)
        df.sort_index( inplace = True, axis = 1)
        #Drop duplicated heading
        df = df.loc[ :, ~df.columns.duplicated(keep='first') ]
        df.sort_index( inplace = True, axis = 0)

        if duplicatesBounds:
            insLast = 0
            eps = 1e-12
            if df.columns.min() > eps :
                df.insert( 0 , df.columns[-1]-2*np.pi ,  df.iloc[ :,-1 ]  )
                insLast = 1

            if df.columns.max() < 2*np.pi - eps :
                df.insert( len(df.columns) , df.columns[insLast] + 2*np.pi ,  df.iloc[ :,insLast ] )

        return Rao.FromDataFrame( df , Rao.getMetaData(self)  )


    def getSorted_Multi( self, duplicatesBounds = True ) :
        """Return Rao sorted in direction (return new instance).

        Parameters
        ----------
        duplicatesBounds : bool, optional
            Duplicate 0-360. The default is True.

        Returns
        -------
        Rao
            Rao sorted in direction
        """
        import xarray as xa

        df = self.toDataArray()

        if len( np.unique(df.Coefficients) ) > 0:
            df = df.sortby( "Coefficients")

        df["Headings"] = np.mod( df["Headings"].values , 2*np.pi)

        #Drop duplicated heading
        _, index = np.unique( df.Headings, return_index=True)

        df = df[ index , :  , :]

        if duplicatesBounds:
            eps = 1e-12
            if df.Headings.min() > eps :
                toAdd = df[ [-1] , : , :].copy()
                toAdd["Headings"] -= toAdd.Headings.values[:] + 2*np.pi
                df = xa.concat( [toAdd , df] , dim = "Headings" )

            if df.Headings.max() < 2*np.pi - eps :
                toAdd = df[ [0] , : , :].copy()
                toAdd["Headings"] = toAdd.Headings.values[:] + 2*np.pi
                df = xa.concat( [ df , toAdd] , dim = "Headings")
        return Rao.FromDataArray( df  )


    def getRaoAtWaveReferencePoint( self, waveRefPoint ):
        """Return the RAO expressed at an other waveReferencePoint
    
        Parameters
        ----------
        WaveRefPoint : np.array of shape (2)
            New reference point to consider, (x, y) coords
            
        Returns
        -------
        Rao
            The Rao at new waveReferencePoint
        """
        VectorToNewWaveRefPoint = self.getWaveReferencePoint() - waveRefPoint
        
        list_of_k = sp.dispersion.w2k( self.freq , depth = self.getDepth() ).reshape(self.nbfreq, 1)
        phase_shift = np.exp( -1j* list_of_k* 
                             (VectorToNewWaveRefPoint[0]*np.cos(self.head)
                              + VectorToNewWaveRefPoint[1]*np.sin(self.head)).reshape(1, self.nbhead ) )
                
        metaData = Rao.getMetaData(self)
        metaData["waveRefPoint"] = waveRefPoint
        
        raos = []
        for imode in range(self.getNModes() ) :
            df_rao = self.toDataFrame(imode = imode)
            df_rao_ = df_rao * phase_shift         
            raos.append( Rao.FromDataFrame( df_rao_, metaData ).getRaoAtMode(0) )
        
        rao_shifted = Rao( raos )
       
        return rao_shifted
        

    def getFreqInterpolate( self, wmin , wmax , dw = 0.05 , cmplxMethod = "mod", usePythonInterp=False, **kwargs) :
        """Interpolate RAO frequency (rao is assumed sorted), return new instance.

        Parameters
        ----------
        wmin : float
            Frequency lower bound
        wmax : float
            Frequency upper bound
        dw : float, optional
            Frequency step. The default is 0.05.
        cmplxMethod : str, optional
            Way to interpolate complex. The default is "mod".
        usePythonInterp : bool, optional
            Use Scipy interpolation. The default is False (Snoopy interpolation is used).
        **kwargs :
            keywords argument to scipy.interpolate.InterpolatedUnivariateSpline

        Returns
        -------
        Rao
            Interpolated Rao

        """
        w_ = np.arange( wmin , wmax , dw )
        if usePythonInterp:
            from Snoopy.Math import InterpolatedComplexSpline
            self._checkOneMode()
            data = np.empty((self.nbhead, len(w_), 1), dtype=complex)
            for ihead , head in enumerate(self.head) :
                vals = self.cvalues[ihead, :, 0].transpose()
                f = InterpolatedComplexSpline(self.freq , vals, cmplxMethod = cmplxMethod, **kwargs )
                data[ihead, :, 0] = f(w_).transpose()

            return Rao(w=w_, b=self.head, cvalue=data , **Rao.getMetaData(self) )
        return Rao(self.getRaoAtFrequencies(w_))


    def isReadyForInterpolation_py(self) :
        """
        #Return True, is the rao is ready for interpolation (sorted, data on 0-360, with duplicated headings to close the circle)

        Now available in the cpp
        """
        logger.warning("Deprecated, use .isReadyForInterpolation()" )

        close360 = min( self.head) <= 0.0 and max(self.head) >= 2*np.pi
        return close360 and self.is360()


    def getHeadInterpolate( self , db = None , head= None, cmplxMethod = "mod" , **kwargs ):
        """Interpolate headings
        Care should be taken for the 0-360 junction.
        To make this simple, for now RAO should first be sorted on 0-360, with duplicated first and last headings!

        Only works for getNModes() == 1

        Parameters
        ----------
        db : float, optional
            Heading step. The default is None.
        head : np.ndarray, optional
            Heading list. The default is None.
        cmplxMethod : str, optional
            Way to interpolate complex. The default is "mod".
        **kwargs : TYPE
            keywords argument to scipy.interpolate.InterpolatedUnivariateSpline.

        Returns
        -------
        Rao
            Interpolated RAO.

        """

        logger.warning("getHeadInterpolate is deprecated, use getRaoAtHeading instead.")

        if self.getNModes() > 1 :
            raise(Exception( "python heading interpolation only available if nModes == 1" ))

        from Snoopy.Math import InterpolatedComplexSpline

        if not self.isReadyForInterpolation() :
            raise(Exception("RAO not ready for interpolation"))

        if db is None and head is not None :
            b_ = head
        elif db is not None:
            b_ = np.arange( 0 , 2*np.pi , db )
        else :
            raise(Exception("Either db or head should be provided"))

        data = np.empty((len(b_), self.nbfreq, 1), dtype=complex)
        for ifreq , freq in enumerate(self.freq) :
            f = InterpolatedComplexSpline(self.head , self.cvalues[:, ifreq, 0],  cmplxMethod = cmplxMethod, **kwargs )
            data[:, ifreq , 0] = f(b_)
        return Rao(w=self.freq, b=b_, cvalue=data, **Rao.getMetaData(self) )


    def is360_py(self , minSpacing = np.pi / 2. ):
        """Check if data areavailable on 0 / 360
        Rough, just check that heading are available in the 4 quarters

        Routine available now directly in cpp
        """
        logger.warning("rao.is360_py is deprecated, use rao.is360 instead")
        headTmp = np.sort(self.head)
        a1 =  np.mod(headTmp-np.radians(45.)  , 2*np.pi ).min() < minSpacing
        a2 =  np.mod(headTmp-np.radians(135.) , 2*np.pi ).min() < minSpacing
        a3 =  np.mod(headTmp-np.radians(225.) , 2*np.pi ).min() < minSpacing
        a4 =  np.mod(headTmp-np.radians(315.) , 2*np.pi ).min() < minSpacing
        return a1 and a2 and a3 and a4


    def getSymmetryType(self):
        """Check how the RAO can be symmetrised (with regard to wave heading)

        Returns
        -------
        np.ndarray (integer)
            Symmetry type (+1 = symmetric , -1 = anti-symmetric , 0 = No known symmetry)

        """

        if abs( self.getReferencePoint()[1] ) > 1e-3 :
            return [0] * self.getNModes()
        else :
            return sp.modesDf.set_index("INT_CODE").loc[ self.getModes() , "SYM" ].values


    def getSymmetrized(self, force_sym=0) :
        """
        Return symmetrized rao
        """

        if self.is360() :
            logger.debug( "RAO already available on 0-360 degree" )
            return self.__class__(self)

        if abs(self.getReferencePoint()[1]) > 1e-3 :
            raise(Exception("RAO can not be symmetrized (y position = {:})".format(self.getReferencePoint()[1])))

        raoList = []
        for imodes in range( self.getNModes() ) :
            if force_sym == 0:
                sym = self.getSymmetryType()[imodes]
            else:
                sym = force_sym
            if sym == 0 :
                raise(Exception(f"Unknwown symmetry type, RAO can not be symmetrized ({self.getType():})"))
            else :
                df = self.toDataFrame(imode = imodes)
                for col in df.columns :
                    if col != 0. and col != 2*np.pi and col != np.pi :
                        df.loc[:, 2*np.pi - col ] = sym * df.loc[:, col ]
                df = df.sort_index(axis = 1)
                metadata = Rao.getMetaData(self)
                metadata["meanValues"] = [metadata["meanValues"][imodes] ]
                metadata["modes"] = [self.getModes()[imodes]]
                metadata["modesCoefficients"] = [self.getModeCoefficients()[imodes]]
                raoList.append(  Rao.FromDataFrame(df, metadata  ) )


        return sp.Rao( raoList )


    def getInterpolated(self, wmin = 0.05 , wmax = 2.0 , ext = 3 , dw = 0.05 , db = 5. ,
                        k = 1 , cmplxMethod = "mod", usePythonInterp=False, **kwargs) :
        """Return an interpolated, symmetrized, evenly spaced transfer function

        cmplxMethod :
           MOD_PHASE : Interpolate module and phase
           RE_IM     : Interpolate real and imaginary
           MOD_REIM  : Interpolate module and get phase from RE_IM interpolation
        """
        logger.warning( "getInterpolated is deprecated, use getRaoForSpectral instead" )

        return self.getSymmetrized().getSorted(duplicatesBounds = True).getHeadInterpolate( db = db, cmplxMethod = cmplxMethod) \
               .getFreqInterpolate( wmin = wmin , wmax = wmax, dw = dw , k =  k ,  cmplxMethod = cmplxMethod , ext = ext, usePythonInterp=usePythonInterp)



    def getRaoForSpectral(self, wmin = 0.1 , wmax = 2.0 ,  dw = 0.005 , db_deg = 5. , interpStrategy = "RE_IM_AMP", extrapType = "BOUNDARY"   ) :
        """Prepare RAO for spectral calculation

        - symmetrize
        - interpolate in both heading and frequency
        - remove duplicate heading if any

        Parameters
        ----------
        wmin : float, optional
            Minimum frequency. The default is 0.1.
        wmax : float, optional
            Minimum frequency. The default is 2.0.
        dw : float, optional
            Frequency step. The default is 0.005.
        db_deg : float, optional
            Heading step (degree). The default is 5.
        extrapType : str, optional
            How to extrapolate (BOUNDARY, EXTRAPOLATE, ZERO, EXCEPTION). The default is "RE_IM_AMP".
        interpStrategy : str, optional
            How to interpolate complex number (BOUNDARY, EXTRAPOLATE, ZERO, EXCEPTION). The default is "RE_IM_AMP".

        Returns
        -------
        Rao
            RAO, ready for spectral calculation.

        """

        if isinstance(extrapType , str) :
            extrapType = getattr( smath.Interpolators.ExtrapolationType , extrapType.upper())

        if isinstance(interpStrategy , str) :
            interpStrategy = getattr( sp.ComplexInterpolationStrategies , interpStrategy.upper() )

        return self.getSymmetrized()\
                   .getSorted(duplicatesBounds = True)\
                   .getRaoAtHeadings( np.deg2rad(np.arange( 0, 360.,  db_deg)), interpStrategy = interpStrategy) \
                   .getRaoAtFrequencies( np.arange( wmin , wmax, dw ) ,  interpStrategy = interpStrategy , extrapType = extrapType )



    def interpValues( self , freq, head, ext = "zeros", **kwargs ) :
        """
        Interpolate values at frequency and heading

        """
        from Snoopy.Math import InterpolatedComplexSpline
        nbwave = len(head)

        #Put heading on 0-360
        head_ = np.mod(head , 2*np.pi)

        #Prepare RAO for heading interpolation
        rao_  = self.getSymmetrized().getSorted(duplicatesBounds = True)

        #Interpolate at wif heading
        newhead = np.array( list(set(head_ )) )
        rao_ = rao_.getHeadInterpolate( head = newhead )

        f = {}
        for head in newhead :
            ihead = np.where( rao_.head == head  )[0][0]
            f[head] = InterpolatedComplexSpline(  self.freq , rao_.cvalues[ihead, :, 0].transpose(), ext=ext, **kwargs )

        cvalue = np.empty( (nbwave), dtype = complex)
        #Interpolate frequency
        for i in range(nbwave) :
            cvalue[ i  ] = f[ head_[i] ](freq[i])
        return cvalue


    def _getSingleHeading(self, heading) :
        """Return RAO with all values copied from heading
        For prototyping only
        """
        mod = np.empty(self.module.shape, dtype = float)
        phi = np.empty(self.phasis.shape, dtype = float)
        ihead = np.where(  self.head == heading)[0][0]
        mod[:,:,:] = self.module[ihead,:,:]
        phi[:,:,:] = self.phasis[ihead,:,:]

        return self.__class__(  b=self.head, w=self.freq, module=mod, phase=phi, **Rao.getMetaData(self) )

    def getExtrudedRao(self, nb_heading) :
        """
        """

        s = self.module.shape
        mod = np.empty( (nb_heading, s[1], s[2]) , dtype = float)
        phi = np.empty( (nb_heading, s[1], s[2]), dtype = float)
        mod[:,:,:] = self.module[0,:,:]
        phi[:,:,:] = self.phasis[0,:,:]
        return self.__class__(  b=np.linspace( 0 , 2*np.pi , nb_heading ), w=self.freq, module=mod, phase=phi, **Rao.getMetaData(self) )

    @classmethod
    def GetIncidentWave( cls, x, y, head, freq, **metadata ) :
        """
        Parameters
        ----------
        x : float
            Longitudinal position, with respec to wave reference point
        y : TYPE
            Transferse position, with respec to wave reference point
        head : TYPE
            DESCRIPTION.
        freq : TYPE
            DESCRIPTION.
        **metadata : TYPE
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.
        """
        cvalue = np.empty( (len(head), len(freq), 1) , dtype = complex)
        k = sp.w2k(freq)
        for i, h in enumerate(head) :
            cvalue[i, : , 0] = np.exp( -1j * k * ( x * np.cos(h) + y * np.sin( h ) ))
        return cls(  b=head, w=freq, cvalue=cvalue, **metadata )


    def getdw_py(self):
        """
        Copy of rao_getdw subroutine from rao_general.f90. Now in spp
        """
        logger.warning("Deprecated, use .getdw()" )
        dw = (self.freq[-1] - self.freq[0] ) / (self.nbfreq - 1)
        for ifreq in range(self.nbfreq - 1):
            if abs( (self.freq[ifreq+1] - self.freq[ifreq]) / dw - 1 ) > 0.03:
                return -1.
        return dw

    def isEvenFreq(self):
        """
        Copy of rao_isEvenFreq subroutine from rao_general.f90
        """
        return self.getdw() > -0.5


    def getMotionRaoAtPoint( self, coords, angleUnit ) :
        """Express motions at a different point

        Parameters
        ----------
        coords : np.ndarray (3)
            Coordinates where to move the motions
        angleUnit : str
            "deg" or "rad"

        Returns
        -------
        sp.Rao
            Moved motions
        """
        #Check that motionRao is indeed 6 DOF motions
        if not self.is6DOF():
            raise(Exception("motionRAOs should be motions"))

        return self.getRaoAtPoint( coords, raoType= "motion", angleUnit = angleUnit )


    def getRaoAtPoint(self, coords, raoType, angleUnit=None) :
        """Express RAOs (load or motion) at a different point

        Parameters
        ----------
        coords : np.ndarray (3)
            Coordinates where to move the motions
        raoType : str
            "load" or "motion"
        angleUnit : str
            "deg" or "rad"
        Returns
        -------
        sp.Rao
            Moved Raos
        """
        move_vect = np.array( coords ) - self.getReferencePoint()

        rao_array = self.to_RaoArray()

        if raoType == "motion":
            if angleUnit.lower() == "deg" :
                angleConvert = np.pi / 180
            elif angleUnit.lower() == "rad" :
                angleConvert = 1.0
            else :
                raise(Exception("angleUnit must be 'deg' ot 'rad'"))
            rao_array[0:3] = rao_array[0:3] + np.cross( rao_array[3:6] * angleConvert  , move_vect )

        elif raoType == "load" :
            rao_array[3:6] = rao_array[3:6] + np.cross( rao_array[0:3]  , move_vect )

        movedRao = sp.Rao( rao_array )
        movedRao.setReferencePoint( coords )

        return movedRao
    
    def getAccAtPoint(self, component, target_point, angleUnit, gravity = True ):
        """Compute acceleration at any point, from 6dof motion.

        Parameters
        ----------
        component : int
            from 0 (surge) to 6 (yaw)
        target_point : tuple(3)
            Coordinates
        angleUnit : str
            "rad" or "deg
        gravity : bool, optional
            whether g*theta is used, by default True

        Returns
        -------
        Rao
            Transfer function of acceleration, single component
        """

        rao_p = self.getRaoAtPoint( target_point, raoType="motion", angleUnit = angleUnit ).getRaoAtMode(component)
        rao_d = rao_p.getDerivate(n=2, update_mode = True)

        if gravity and component <= 2:
            g = 9.81
            if angleUnit.lower() == "deg" :
                angleConvert = np.pi / 180
            elif angleUnit.lower() == "rad" :
                angleConvert = 1.0
            if component == 1: #ACCY
                rao_d = rao_d  + g * angleConvert * self.getRaoAtMode(3)
            elif component == 0: #ACCX
                rao_d = rao_d  - g * angleConvert * self.getRaoAtMode(4)

        return rao_d



    def getLoadRaoAtPoint(self, coords):
        """Express loads at a different point

        Parameters
        ----------
        coords : np.ndarray (3)
            Coordinates where to move the motions

        Returns
        -------
        sp.Rao
            Moved loads
        """
        if not self.is6Load():
            raise(Exception("loadRAOs should be loads"))
        return self.getRaoAtPoint(coords = coords, raoType = "load")


    def mergeWith(self, rao2):
        """
        Merge two RAOs that have the same headings but not the same frequencies
        Returns a new Rao

        The hstarHeader() are first compared to check consistency
        """
        if not self.hstarHeader() == rao2.hstarHeader():
            raise(Exception("Cannot merge the two raos, they are not consistent!"))
        df = pd.concat([self.toDataFrame(), rao2.toDataFrame()]).sort_index()
        metaData = Rao.getMetaData(self)
        return Rao.FromDataFrame(df, metaData)


    def getRaoWeFiltered(self , we_max) :
        """Put zero for when encounter frequency exceed the specified values

        In pradtice when the mesh resolution leads to spurious results at high frequency

        Parameters
        ----------
        we_max : float
            Cut-off frequency

        Returns
        -------
        Rao
            Rao where all values with we > we_max set to zero

        """
        arr = self.toDataArray()
        i0 = np.where( self.getEncFrequencies() > we_max )
        for imode in range(len(arr.modesCoefficients)) :
            arr[:,:,imode][i0] = 0.0
        return self.__class__.FromDataArray( arr )



def derivateMode(mode, n = 1):
    """Transformation of mode respect to the derivation
    I know it's dirty...
    Derivation of motion   --> velocity
    Derivation of velocity --> acceleration
    Anything other thing   --> unknown

    Parameters
    ----------
    mode : Spectral.Modes
        Object mode
    n : int, optional
        Degree of derivation, by default 1

    Returns
    -------
    Spectral.Modes
        Derivate modes
    """

    if isinstance(mode,list):
        return [derivateMode(item,n=n) for item in mode]

    raotype,component = sp.modesIntToTypeComponentDict[mode.value]

    outMode = sp.Modes.NONE
    if raotype == "MOTION":
        if n == 1:
            #outMode = sp.modeFromModesTypeComponent("VELOCITY",component)
            outMode = sp.Modes( sp.modesTypeComponentToIntDict.get( ( "VELOCITY", component ) , 0 ) )
        elif n == 2:
            #outMode = sp.modeFromModesTypeComponent("ACCELERATION",component)
            outMode = sp.Modes( sp.modesTypeComponentToIntDict.get( ( "ACCELERATION", component ) , 0 ) )
    elif raotype == "VELOCITY":
        if n == 1:
            #outMode = sp.modeFromModesTypeComponent("ACCELERATION",component)
            outMode = sp.Modes( sp.modesTypeComponentToIntDict.get( ( "ACCELERATION", component ) , 0 ) )

    # More transformation to be hardcoded go here:
    else :
        logger.debug( "label not known for RAO derivative" )

    return outMode

def getUnitRao( wmin = 0.2 , wmax = 1.8 , dw = 0.05, speed = 0.0 , heading = np.arange(0,2*np.pi,15)):
    freq = np.arange(wmin, wmax+dw, dw)
    phi = np.zeros((len(heading), len(freq), 1), dtype=float)
    mod = np.zeros((len(heading), len(freq), 1), dtype=float)
    mod[:,:, 0] = 1.
    return Rao(w=freq, b=heading, module=mod, phase=phi, forwardSpeed=speed,
               refPoint=[0.,0.,0.], waveRefPoint=[0.,0.], modes=[_Spectral.Modes.SURGE,])



def parse_rao_file(filename, blockIndex = None, Beq = None ) :
    """Read rao data from HydroStar files (could be optimized).

    In the classical case, the RAO has just one block.

    However, it may happen that several blocks exist when several dampings have been used. This is useful for stochastic linearization.
    If there are several blocks, there are two options:
    - By default, all the blocks of the RAO will be read.
    - if blockIndex is given, only this block will be read.
    - if Beq is given, only the block with the closest equivalent damping to Beq will be read
        -> an improvement could consist in interpolating between the different equivalent dampings

    If return_object is True (by default), use normal routine, and return object
    If return_object is False, return information needed to build object
    Parameters
    ----------
    filename : str
        File to read
    blockIndex : int or None, optional
        block to read. The default is None.
    Beq : float, optional
        Beq to read (take closest available). The default is None.
    return_object : bool, optional
        build and return object or not
    Returns
    -------
    sp.Rao
        The transfer funnction object

    """
    logger.debug(f"Reading RAO file {filename:}")
    # Default is UTF-8, consistently on Windows (including from Korea) / Linux. However, older HydroStar output might present "²" encoded in cp1252.
    try :
        with open(filename , "r", encoding = "utf-8") as f :
            f_str = f.read()
    # Following is needed for acceleration RAOs generated by HydroStar prior to v8.3
    except UnicodeDecodeError :
        with open(filename , "r", encoding = "cp1252") as f :
            f_str = f.read()

    #Read header
    header = [ l.strip() for l in f_str.splitlines() if l.startswith("#") and l.strip() ]

    #Parse heading
    for l in header :
        if "#HEADING" in l :
            head = np.deg2rad( np.array( l.split()[1:] , dtype = float ) )
            break

    linparvalue = []
    #read LINPARVALUE
    for l in header :
        if "#LINPARVALUE" in l or "DAMPING" in l and "WAVE" not in l :
            linparvalue.append( float( l.split()[1] ) )
        elif "COS/SIN" in l:
            raise(Exception("COS/SIN rao not supported, please use Amplitude / Phase format"))

    #Parse RAO header :
    metaData = readMetaData( header)
    nbhead = int(re.search( r'.*#.*NBHEADING\s*(\d+)\s*\n', "\n".join(header)).group(1))

    dataStr = "\n".join( [l for l in f_str.splitlines() if not l.startswith("#") ] )
    dataStrList = dataStr.split("\n\n")
    nBlock = len(dataStrList)

    blockToRead = 0

    if isinstance( blockIndex, int) is True:
        blockToRead = blockIndex
        nBlock = 1

    if isinstance( Beq, float) is True:
        blockToRead = (np.abs(np.asarray(linparvalue)-Beq)).argmin()  # returns index of closest value of linparvalue to Beq
        nBlock = 1

    data = np.loadtxt( StringIO(dataStrList[0]), dtype = float , comments = "#" )
    module = np.empty((nbhead, data.shape[0], nBlock), dtype=float)
    phasis = np.empty((nbhead, data.shape[0], nBlock), dtype=float)

    if (nBlock == 1):
        data = np.loadtxt( StringIO(dataStrList[blockToRead]), dtype = float , comments = "#" )
        module[:, :, 0] = data[:,1:nbhead+1].transpose()
        if len( data[0,:] ) == 2*nbhead+1  :
            phasis[:, :, 0] = np.deg2rad(data[:,nbhead+1:2*nbhead+1].transpose())
        else :
            logger.warning(f"Phases not available in RAO {filename:}, Phasis set to zero.")
            phasis[:, :, 0] = 0.0
    else:
        for ib in range(nBlock):
            data = np.loadtxt( StringIO(dataStrList[ib]), dtype = float , comments = "#" )
            module[:, :, ib] = data[:,1:nbhead+1].transpose()
            phasis[:, :, ib] = np.deg2rad(data[:,nbhead+1:2*nbhead+1].transpose())


    kwargs = {  "b"     : head,
                "w"     : data[:,0],
                "module": module, 
                "phase" : phasis}
    if not (nBlock == 1):
        meanValues = metaData.pop( "meanValues" , [0]) * nBlock
        modes = metaData.pop( "modes" , [0]) * nBlock
        kwargs["modesCoefficients"] = linparvalue
        kwargs["meanValues"]        = meanValues
        kwargs["modes"]             = modes
    kwargs.update(metaData)
    return kwargs




def check_input_signature(kwargs):
    """Check if input of Rao is compatible with C++ init.
    
    Objective is to get a message easier to read than the one provided by c++. It always raises an exception.
    
        
    
    Parameters
    ----------
    kwargs : dict
        input that are supposed to passed to C++ initiator

    Raises
    ------
    TypeError
        Invalid keywords
    """
    input1 = ["b", "w", "modesCoefficients", "modes", "module", "phase", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input2 = ["b", "w", "modesCoefficients", "modes", "cvalue", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input3 = ["b", "w", "module", "phase", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input4 = ["b", "w", "modes", "module", "phase", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input5 = ["b", "w", "cvalue", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input6 = ["b", "w", "modes", "cvalue", "refPoint", "waveRefPoint", "forwardSpeed", "depth", "meanValues"]
    input7 = ["rao", "checkReferencePoint"]
    input8 = ["rao"]
    
    keys = kwargs.keys()
    if "rao" in kwargs:
        _must_match_input(keys,[input7,input8])
    elif ("modesCoefficients" in keys):
        _must_match_input(keys,[input1,input2])
    elif "modes" in keys:
        _must_match_input(keys,[input4,input6])
    else:
        _must_match_input(keys,[input3,input5])

def _must_match_input(keys,possibility_list):
    """Check in set of input keys match the admissible format.
    
    Parameters
    ----------
    keys : list
        list of input keys
    possibility_list: list
        list of admissible input keys

    Raises
    ------
    TypeError
        When something wrong in signature
    """
    all_expected_keys = []
    all_admissible_input = []
    str_all_admissible_input = ""
    for possibility in possibility_list:
        all_expected_keys += possibility
        all_admissible_input.append(set(possibility))
        str_all_admissible_input += "\t"+ ", ".join(possibility) + "\n"
        
    #Check if there are unexpected keys:
    for key in keys:
        if key not in all_expected_keys:
            raise TypeError(f"__init__() of RAO got an unexpected keyword argument '{key}'")
    
    set_keys = set(keys)
    
    for admissible_input in all_admissible_input:
        if set_keys == admissible_input:
            raise TypeError("Keyword argument names are correct, but type seems wrong") 
        elif len(set_keys.difference(admissible_input)) == 0:
            missing_keys = admissible_input.difference(set_keys)


    raise TypeError(f"""__init__() is called with invalid set of keywords : {keys}    
Reminder: input must match one of the following possibility:
{str_all_admissible_input}May be you miss the following key: {missing_keys}""")


if __name__ == "__main__" :

    # Frequency-domain transfer function results.
    rao = Rao(f"{sp.TEST_DATA:}/rao/roll.rao")

    # Frequency-domain results which are not a transfer function.
    rao = Rao(f"{sp.TEST_DATA:}/rao/ca_33.rao")

    # Results with respect to section x-coordinate.
    rao = Rao(f"{sp.TEST_DATA:}/rao/my_f5.rao")
