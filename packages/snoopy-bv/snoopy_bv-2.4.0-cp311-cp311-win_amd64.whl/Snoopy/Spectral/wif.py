import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy import TimeDomain as td
from Snoopy import WaveKinematic as wk
from Snoopy import Spectral as sp
from Snoopy.Math import get_dx, is_multiple
from Snoopy import logger
import _Spectral



class Wif(_Spectral.Wif):
    """Discretized spectrum, with phase. Describes a wave elevation time-series.

    Example
    -------
    >>> ss = sp.SeaState.Jonswap( hs = 1.0, tp = 10.0, gamma = 1.5 , heading = np.pi )
    >>> wif = sp.Wif( ss )
    >>> wif.to_dataframe()
         Frequency      Amplitude     Phase   Heading             Complex
    0     0.107116   0.000000e+00  5.832948  3.141593  0.900344-0.435179j
    1     0.118874   0.000000e+00  3.215705  3.141593 -0.997255-0.074045j
    ..         ...            ...       ...       ...                 ...
    198   1.978462   7.512711e-03  5.737647  3.141593  0.862361-0.518879j
    199   1.994234   5.591527e-03  4.286457  3.141593 -0.407578-0.910654j
    """

    def __str__ (self):
        """Print the wif object.

        Returns
        -------
        s : str
            Description of the wif object content.
        """
        s = "Wif object {:}\nNumber of component {:} (from {:.2f} to {:.2f})\n".format(self.__repr__(), self.nbwave, self.freq.min(), self.freq.max())
        s += "Hs = {:.3f}\n".format(self.hs)
        s += "Tz = {:.3f}\n".format(self.tz)


        if len(self.getIndependentHeadings()) < 3  :
            s += "Heading = {:}\n".format( np.rad2deg(self.getIndependentHeadings()) )
        else :
            s += "Heading = spreaded\n"

        s += "Depth = {:}\n".format(self.depth)
        return s


    def __hash__( self ):
        """Return wif hash.

        Returns
        -------
        int
            hash
        """
        #Probably not the fastest way...
        return hash( (tuple(self.freq), tuple(self.amp) , tuple(self.phi), tuple(self.head), self.depth) )

    def __add__(self , rhs):
        tmp_ = _Spectral.Wif.__add__( self, rhs  )
        return self.__class__(tmp_)

    def __imul__(self, rhs):
        _Spectral.Wif.__imul__( self, rhs  )
        return self

    def __eq__(self, other):
        if other is None:
            return False
        for attr in ('freq', 'amp', 'head', 'phi'):
            if (getattr(self, attr) != getattr(other, attr)).any():
                return False
        return True


    @classmethod
    def FromFreqEdges(cls, seastate, w_edges, seed = 0 ):
        """Discretize the sea-state based on frequency edges.

        Can be useful for constant dk (HOS-OCEAN) case.

        Parameters
        ----------
        w_bins : np.ndarray
            Frequency edges (wif.nbwave = len(w_bins) -1)


        #TODO : implement for multi-directional seastate, next to other cpp constructor

        Returns
        -------
        Wif
            Wif object
        """
        if not seastate.isUnidirectional():
            raise(Exception( "FromFreqBins only available for unidirectional sea states"))
        w = 0.5*(w_edges[:-1] + w_edges[1:])
        nbwave = len(w)
        dw = np.diff(w_edges)
        a = (2*seastate.compute( w )*dw)**0.5
        b = np.full( (nbwave) , seastate.getSpectrum(0).heading, dtype = float )
        rng = np.random.default_rng(seed if seed != 0 else None)
        phi = 2*np.pi  * rng.random(nbwave)
        return cls(  w=w,  a=a, b=b , phi = phi, depth = -1.0 )



    def removeNaN(self) :
        """Return Wif object without NaN components.

        Returns
        -------
        sp.Wif
            Wif object without NaN components.
        """
        ids = np.where(  ( ~np.isnan(self.freq)) &
                         ( ~np.isnan(self.amp)) &
                         ( ~np.isnan(self.head)) &
                         ( ~np.isnan(self.phi))
                      )

        return self.__class__( w = self.freq[ids] , a = self.amp[ids], phi = self.phi[ids], b = self.head[ids], depth = self.depth )


    def to_dataframe(self):
        """Return wif data as pandas.DataFrame.

        Returns
        -------
        pd.DataFrame
            Wif data as dataFrame

        """
        return pd.DataFrame( data = { "Frequency" : self.freq,
                                      "Amplitude" : self.amp,
                                      "Phase" : self.phi,
                                      "Heading" : self.head,
                                      "Complex" : self.amp*np.exp( 1j * self.phi )
                                     })


    def write( self, filename ) :
        """Write the wif file.

        Parameters
        ----------
        filename : str
            Output file

        Returns
        -------
            None.
        """
        with open(filename, "w") as f :
            # Write header
            f.write( f"# TYPE = 2 (Wave time series in local vessel reference) | DEPTH = {self.depth:.4g}\n")
            f.write( "# Pulsation (rad/s) | Amplitude (m) | Phase (rad) | Wave Heading (deg)\n")
            # Write data
            for i in range(self.nbwave):
                f.write( "{:.5f} {:.4e} {:+.4e} {:3.1f}\n".format( self.freq[i],self.amp[i],self.phi[i],np.rad2deg(self.head[i])  ) )


    def get_dw(self, dw = None, eps = 1e-3, allow_hole = False) :
        """Check if all wif frequency are evenly spaced.

        If allow_hole is true, a common denominator is looked for.

        Parameters
        ----------
        dw : float, optional
            Check if dw is the frequency step. The default is None.

        Returns
        -------
        dw : float or None
            Frequency step, or None if frequencies are not evenly distributed

        """
        if self.nbwave == 1 :
            return self.freq[0]

        even_dw = get_dx( np.unique( np.sort(self.freq)), dw, eps = eps )
        if even_dw :
            return even_dw

        elif allow_hole :
            if dw is not None:
                if is_multiple(self.freq, dw, tol = eps) :
                    return dw
            else :
                dw_l  = np.diff(self.freq)  # Non-exaustive possibilities.
                for dw in np.unique(dw_l) :
                    if is_multiple(self.freq, dw, tol = eps) :
                        return dw

        return None



    def get_trepeat(self, speed=0.0) :
        """Compute and return repetition period.

        Parameters
        ----------
        speed : float, optional
            Speed of the reference frame.. The default is 0.0.

        Returns
        -------
        float
            Repetition period.
        """
        if self.nbwave == 1 :
            return abs(2*np.pi / self.getEncounterFrequencies( speed ) [0])
        else :
            if speed > 0.0 :
                dw = get_dx( np.unique(np.sort(self.getEncounterFrequencies(speed))))
            else :
                dw = self.get_dw()

            if dw is not None :
                return 2*np.pi / dw
            else :
                return np.inf


    def get_wp(self):
        """Get peak circular frequency.

        Only available if frequency are uniformly discretized

        Returns
        -------
        float or None
            Spectrum peak frequency, if any can be deduced.
        """
        if self.get_dw(allow_hole = True) is None  :
            return None
        else :
            return self.freq[ np.argmax(self.amp) ]



    def write_hos(self, filename, unidir = True):
        """Write wif to HOS format.

        Parameters
        ----------
        filename : str
            File name
        unidir : bool, optional
            If unidir is True, all the angles are set to 0 in the HOS input file. Set unidir to False to set the angle values to the heading of the
            wif. By default True.
        """
        s = ""
        if self.nbwave > 1:
            dw = self.get_dw( eps = 1e-3 , allow_hole=True )
            if dw is None:
                raise(Exception("Error : All frequencies should be a multiple of df"))
        else:
            dw = self.freq[0]

        for iwif in range(self.nbwave) :
            iharmo = int(np.round( self.freq[iwif] / dw ))

            if(unidir):
                angle = 0.0
            else:
                angle = self.head[iwif] * 180 / np.pi

            s += "{harmo:} , {f:.6e}  , {amp:.4e}  , {angle:.3f}  , {phase:.3f}  ,\n".format( harmo = iharmo , f = iharmo*dw / (2*np.pi) ,
                                                                                amp = self.amp[iwif],
                                                                                angle = angle,
                                                                                phase = np.mod( self.phi[iwif] , 2*np.pi) )
        with open( filename, 'w' ) as f :
            f.write(s)

    
    
    @classmethod
    def Read_hos(cls , filename, depth = -1, rnum = None , clock = None) :
        """Read from HOS format.

        Parameters
        ----------
        filename : str
            HOS .dat filename
        depth : TYPE, optional
            DESCRIPTION. The default is -1.

        Returns
        -------
        sp.Wif
            Wif object
        """
        data = pd.read_csv( filename , sep = ",", header = None )

        freq_read = data.iloc[:,1] * 2*np.pi

        if rnum is None :
            freq = freq_read
        else :
            freq = data.iloc[:,0] * clock / (2**rnum / (2*np.pi))
            if not np.isclose( freq ,  freq_read ,rtol = 1e-3).all() :
                logger.error( f"{freq/freq_read:}" )
                raise(Exception())


        return cls( a =  data.iloc[:,2] ,
                    w = freq ,
                    phi = data.iloc[:,4] ,
                    b = data.iloc[:,3]*np.pi/180,
                    depth = depth)




    def plot(self , ax=None, marker = "+", linestyle = "", label = "Wave components", **kwargs  ) :
        """Plot the component amplitude against the frequency, if bin width is available, the spectral density is plotted as well.

        Parameters
        ----------
        ax : ax or None, optional
            Where tp plot the graph, if None, a new ax is created and returned. The default is None.
        marker : str, optional
            The default is "+".
        linestyle : str, optional
            The default is "".
        **kwargs :
            Arguments passed to ax.plot

        Returns
        -------
        ax : TYPE
            DESCRIPTION.

        """
        if ax is None :
            _ , ax = plt.subplots()

        ax.plot( self.freq , self.amp , marker = marker , linestyle = linestyle, label = label, **kwargs )
        ax.set_ylim( bottom=0. , )
        ax.set_xlabel( r"$\omega$ $(rad/s)$" )
        ax.set_ylabel( "Components amplitude" )
        if self.isWidth :
            label_spectrum = kwargs.pop( "label_spectrum", "Wave spectrum" )
            ax1 = ax.twinx()
            d_ = self.getDensity()
            ax1.set_ylim( bottom=0. , top = max(d_)*1.05 )
            ax1.plot( self.freq , d_ , "o-" , markersize = 2, color = "red", label = label_spectrum )
            ax1.set_ylabel( "Spectral density" )
            ax1.legend(loc = "upper left")
        ax.legend(loc = "upper right")
        return ax

    def plotTime(self, tmin = -100.0 , tmax = +100.0 , dt = 0.5, ax = None):

        if ax is None :
            fig, ax = plt.subplots()

        time = np.arange(tmin, tmax , dt)
        se = td.ReconstructionWifLocal( self ).evalSe(time)
        se.plot(ax=ax)
        return ax



    @classmethod
    def Jonswap(cls, *args, wifArgs = {"nbSeed" : 200, "seed":0} , **kwargs ):
        """Convenience routine to quickly discretize a Jonswap spectrum.

        Parameters
        ----------
        *args :
            Argument passed to sp.Jonswap

        **kwargs :
            Keyword Argument passed to sp.Jonswap

        wifArgs : dict, optional
            Argument passed to sp.Wif( ). The default is {"nbSeed" : 200, "seed":0}.

        Returns
        -------
        Wif
            Discretize Jonswap spectrum

        """
        ss = _Spectral.Jonswap( *args, **kwargs )
        return cls( ss, **wifArgs)

    @classmethod
    def Airy(cls , a , period = None, w = None , heading = 0.0, phi = 0.0, depth = 0.0):
        """Define a regular wave.

        Parameters
        ----------
        a : float
            Wave amplitude
        period : float, optional
            Wave period. The default is None.
        w : float, optional
            Wave angular frequency. The default is None.
        heading : float, optional
            Wave heading. The default is 0.0.
        phi : float, optional
            Wave phase. The default is 0.0.
        depth : float, optional
            water depth. The default is 0.0.

        Returns
        -------
        Wif
            Wif with a single component
        """
        if w is None :
            w = 2 * np.pi / period
        elif period is not None :
            raise(Exception("Either period or w should be specified, not both"))

        return cls( a = [a] , w = [w] , phi = [phi] , b = [heading], depth = depth)





    @classmethod
    def Read(cls , filename) :
        """
        Read wif file (BV format). Not necessary anymore as wrtten in C++
        """
        data = np.loadtxt( filename , comments="#" )
        return cls( w = data[:,0] , a = data[:,1] , phi = data[:,2] , b = np.deg2rad(data[:,3])  )

    @property
    def hs(self):
        return 4.004*self.m0**0.5

    @property
    def m0(self):
        """Spectral zero order moment ( m0 = stdv**2)
        """
        return np.sum( self.amp[np.where(self.freq > 0.)]**2 / 2 )


    @property
    def m2(self) :
        return np.sum( self.amp ** 2 * self.freq**2 / 2 )

    @property
    def tz(self) :
        return 2*np.pi*(self.m0/self.m2)**0.5

    @property
    def nbwave(self) :
        return len(self.getPhases())


    @classmethod
    def FromTS(cls, se, b , method = "FFT", **kwargs):
        """Generate wif from time series.

        Parameters
        ----------
        se : pd.Series
            Wave elevation time trace.
        b : float, optional
            Heading.
        method : str, optional
            How to generate wif. The default is "FFT".
        **kwargs : Any
            Argument passed to underlying algorythm  (freq, model, x0)

        Returns
        -------
        sp.Wif
            Wif object
        """
        if type(method) is str:
            if method == "FFT" :
                return Wif.FromTS_FFT( se=se, b=b, **kwargs )
            elif method == "FFT2" :
                return Wif.FromTS_FFT2( se=se, b=b, **kwargs )
            elif method == "LSQ" :
                return Wif.FromTS_LSQ( se=se, b=b, **kwargs )
            elif method == "LLSQ" :
                return Wif.FromTS_LLSQ( se=se, b=b, **kwargs )
            else:
                raise(Exception("{:} not known".format( method )))

        try:
            return method( se=se, b=b, **kwargs )
        except Exception as e:
            raise(Exception("Error computing WIF from TS: {:}".format(e)))


    @classmethod
    def FromFS(cls, se, b, t = 0.0, depth = -1):
        """Estimate Wif from wave elevation snapshot.

        Parameters
        ----------
        se : pd.Series
            Wave elevation snapshot, index is position, in (m).
        b : float
            Wave heading (radians)
        t : float, optional
            Time corresponding to the snapshot. The default is 0.0.
        depth : float, optional
            Water-depth. Default to infinite water-depth

        Returns
        -------
        sp.Wif
            Wif object
        """
        space_fft = td.fftDf( se )

        k = 2*np.pi * space_fft.index.values

        w = _Spectral.k2w(k, depth = depth)

        # Time shift in case the snapshot does not start at x=0
        if b == np.pi :
            phi = np.angle( space_fft.values ) - k * se.index[0]
        elif b == 0. :
            phi = -np.angle( space_fft.values ) + k * se.index[0]
        else :
            raise(Exception("FromTS is only available for waves in x direction yet."))

        wif = cls( w = w , a = np.abs(space_fft.values) ,
                           phi = phi,
                           b = np.full( len(w), b) , depth = depth)

        # Correct phase to match position and given time.
        # wif.offset(dx = se.index[0])
        wif.offset(dt = t)
        return wif


    def get2ndOrderElevation(self, time, full2nd = True):
        """Calculate 2nd order wave elevation time trace at a fixed location.

        Convenience function, the actual work is performed in wk.SecondOrderKinematic.getElevation()

        Parameters
        ----------
        time : np.ndarray
            Time
        full2nd : bool, optional
            If True 2nd order potential is accounted for, otherwise, only the quadratic part. The default is True.

        Returns
        -------
        np.ndarray
            2nd order time-domain reconstruction.
        """

        if full2nd :
            kinModel = wk.SecondOrderKinematic
        else :
            kinModel = wk.SecondOrderKinematic21

        return kinModel( self ).getElevation( time , 0, 0 ) - wk.FirstOrderKinematic( self ).getElevation( time , 0, 0 )



    @classmethod
    def FromTS_FFT2(cls, se, b = 0.0, depth = -1., wmin = 0.01, wmax = 1.5, itmax = 15, tol = 0.01, full2nd = False):
        """Create a wif from time serie, through FFT
        with iterative process to remove 2nd component


        Parameters
        ----------
        se : Pandas.Series
            Wave time trace
        b : float, optional
            Wave heading (rad). The default is 0.0.
        wmax : float, optional
            DESCRIPTION. The default is 1.5.
        itmax : int, optional
            Maximum number of iteration. The default is 15.
        tol : float, optional
            Tolerance for convergence criteria. The default is 0.01.
        full2nd : bool, optional
            If True 2nd order potential is accounted for, otherwise, only the quadratic part. The default is True.

        Returns
        -------
        Wif
            Wif object corresponding to the input time series.
        """

        wif = cls.FromTS( se=se , b=b , depth = depth)
        wif = wif.getFiltered(wmin = wmin , wmax = wmax)
        for i in range(itmax):
            se1 = se - wif.get2ndOrderElevation( se.index.values , full2nd )
            wif_new = cls.FromTS( se = se1 , b=b , depth = depth )
            diff = abs( wif_new.hs - wif.hs )
            wif = wif_new.getFiltered( wmin = wmin , wmax = wmax )
            if diff < tol :
                break
        else :
            logger.error( f"Convergence not reached after itmax={itmax:} iterations" )

        logger.debug(f"FromTS_FFT2 : number of iteration = {i+1:}" )
        return wif



    @classmethod
    def FromTS_FFT(cls, se, b = 0.0, depth = -1., windows = None, wmin = None, wmax = None, speed = 0.0, wp = 0.5):
        """Create a wif from time serie, through FFT.

        Parameters
        ----------
        se : Pandas.Series
            Wave time-trace, index is time, in seconds.
        b : float, optional
            Wave heading (rad). The default is 0.0.
        speed : float
            Forward speed, in case the wave-elevation is given in a moving frame.
        wp : float
            Indicative peak period of the spectrum. Used in case of following sea to choose between the different solution.

        Returns
        -------
        Wif
            Wif object corresponding to the input time series.
        """
        from Snoopy.TimeDomain import fftDf

        # FFT
        df = fftDf(se, index='rad', windows = windows)

        we, amp, phi = df.index.values, df.abs().values,  df.apply(np.angle).values

        # Time shift in case the serie does not start at t=0
        phi_ = phi - we * se.index[0]

        if speed == 0.0:
            w = we
        elif np.cos(b) <= 0. :  # Only one solution
            w = sp.we2w(we, b = b, speed = speed, depth = depth)
        else : # Possibly several solutions
            # Select the one closest to indicative wp.
            logger.warning( "Retrieving wave component from moving probe is ambiguous in following seas!!!" )
            w = np.empty(len(we), dtype = float)
            for i, we_ in enumerate(we) :
                w_s = np.array( sp.we2w(we_, b = b, speed = speed, depth = depth, return_type="tuple") )
                w[i] = w_s[ np.abs( w_s - wp).argmin() ]

        wif = cls(w = w, a=amp , phi = phi_, b = b*np.ones((len(we))), depth = depth)

        if (wmin is None) and (wmax is None):
            return wif
        if wmin is None:
            wmin = 0.
        if wmax is None:
            wmax = 1000.
        return wif.getFiltered(wmin=wmin, wmax=wmax)


    @classmethod
    def FromTS_LSQ(cls, se, freq, x0 = None, b = 0.0, model = wk.FirstOrderKinematic, depth = -1., solver_kwargs = {}) :
        """Create a wif from time serie, through least-square (non-linear).

        Parameters
        ----------
        se : Pandas.Series
            Wave time trace
        freq : np.array
            Frequency table.
        x0 : np.array, optional
            Initial guess. The default is None.
        b : float, optional
            Wave Heading. The default is 0.0.
        model : wk.KinematicModel, optional
            Wave kinematic model. The default is wk.FirstOrderKinematic.
        solver_kwargs : dict, optional
            Keyword arguments passed to scipy.optimize.minimize. The default is {}.

        Returns
        -------
        Wif
            Wif object corresponding to the input time series.

        """
        from Snoopy import Spectral as sp
        from scipy.optimize import least_squares

        dx =  get_dx(se.index.values, raise_exception=True)

        if not isinstance(freq , (np.ndarray,)) :
            if freq in ["fft",   "FFT" ] :
                freq = np.fft.rfftfreq(se.index.size, d=dx) * 2 * np.pi
                if x0 is None :
                    x0 = sp.Wif.FromTS_FFT(se, b=b).getCosSin()

            elif freq in ["fft1",   "FFT1" ] :
                freq = np.fft.rfftfreq(se.index.size, d=dx) * 2 * np.pi
                freq = freq[1:]
                if x0 is None :
                    wif_ = sp.Wif.FromTS_FFT(se, b=b)
                    wif_.removeZeroFrequency()
                    x0 = wif_.getCosSin()

        if x0 is None :
            x0 = sp.Wif.FromTS_LLSQ( se=se , freq=freq, b=b ).getCosSin()

        def err( cos_sin, freq ):
            #Error function to minimize
            wif_ = sp.Wif( freq, cos_sin, 180.0, depth = depth )
            kin_ = model(wif = wif_)
            eta_ = kin_.getElevation( se.index.values, 0,0 )
            return se.values - eta_

        assert( 2*len(freq) == len(x0) )
        print ("Solving non-linear LSQ")
        resOpt = least_squares( lambda x : err( x, freq ), x0 = x0, **solver_kwargs )

        if not resOpt.success :
            print ("Non-linear least squared failed" )

        wif = cls( w = freq, cos_sin = resOpt.x, b = b )

        #Warn if overfit
        hs_loc = ( 4 * se.std() )
        if not 0.9 * hs_loc < wif.hs < 1.2 * hs_loc :
            print ("WARNING, Wif.FromTS : original hs = {}, fitted hs = {}".format(wif.hs , hs_loc ))

        return wif


    def getFiltered(self , wmin = 0.0001, wmax = 1000.):
        """Return filtered Wif.

        Parameters
        ----------
        wmin : float, optional
            Minimum circular frequency. The default is 0.0001.
        wmax : float, optional
            Maximum circular frequency. The default is 1000..

        Returns
        -------
        wif : sp.Wif
            Filtered wif file
        """
        i = np.where( (self.freq < wmax) & (self.freq > wmin )   )

        return Wif( w = self.freq[i], a = self.amp[i], phi = self.phi[i] , b = self.head[i], depth = self.depth )


    @classmethod
    def FromTS_LLSQ(cls, se, freq, b = 0.0, depth = -1):
        r"""Create a wif from time serie, through linear least-square.

        Compute  A(:) and B(:) so that  [Sum( Ai*cos(wi *t) + Bi*sin(wi*t) )  -  signal(t)  ]**2  is minimized  (LSQ)

        Method -->  Find the zeros of the derivate with regards to Ai and Bi ==> Linear system 2n*2n to solve

        Notes
        -----
        The match between original and reconstructed wave elevation increase with n.
        However a too high value of n make the energy of the underlying spectrum too high,
            --> The signal blows up outside the fitted time range,
            --> The reconstruction of 1st and 2nd order response via RAO/QTF is very sensitive to numerical error (interpolation...) and not usable in practice.

        Parameters
        ----------
        se : Pandas.Series
            Wave time trace
        freq : np.array
            Frequency table.
        b : float, optional
            Wave Heading. The default is 0.0.

        Returns
        -------
        Wif
            Wif object corresponding to the input time series.

        """
        from scipy.linalg import lu_factor, lu_solve

        time = se.index.values


        freq = np.sort(freq)

        #Handle w = 0
        mean = None
        if 0. in freq :
            freq = freq[1:]
            mean = np.mean(se.values)
            se -= mean

        n = len(freq)

        matB = np.zeros( (2*n), dtype = float )
        matA = np.zeros( (2*n, 2*n), dtype = float )

        for i in range(n):
            matB[i]   = np.sum( se.values[:] * np.cos( freq[i] * time[:] ))
            matB[i+n] = np.sum( se.values[:] * np.sin( freq[i] * time[:] ))

        for j in range(n):
            costmp1 = np.cos(freq[j] * time[:])
            sintmp1 = np.sin(freq[j] * time[:])
            for i in range( n ):
                matA[i,j]     = np.sum(np.cos(freq[i]*time[:]) *  costmp1)
                matA[i,j+n]   = np.sum(matA[i,j+n]    +  np.cos(freq[i]*time[:]) *  sintmp1)
                matA[i+n,j]   = np.sum(matA[i+n,j]    +  np.sin(freq[i]*time[:]) *  costmp1)
                matA[i+n,j+n] = np.sum(matA[i+n,j+n]  +  np.sin(freq[i]*time[:]) *  sintmp1)

        logger.info(f"Solving linear LSQ {matA.shape:}")
        res = lu_solve( lu_factor(matA), matB )  # res = np.linalg.solve( matA , matB )

        #Convert to amp/phase
        amp  = (res[:n]**2 + res[n:]**2)**0.5
        phi  = np.arctan2(  -res[n:] , res[:n]  )

        head = np.full( (n), b, dtype = float )

        if mean is not None:
            amp = np.append( mean, amp )
            phi = np.append( 0., phi )
            freq = np.append( 0., freq )
            head = np.append( b, head )

        #Return wif file
        wif = cls( w = freq, a = amp, phi = phi , b = head, depth = depth )

        #Warn if overfit
        hs_loc = ( 4 * se.std() )
        if not 0.9 * hs_loc < wif.hs < 1.2 * hs_loc :
            logger.info("WARNING, Wif.FromTS : original hs = {}, fitted hs = {}".format(wif.hs , hs_loc ))

        return wif

    def getCosSin(self):
        cos_sin = np.empty( self.nbwave*2 )
        cos_sin[:self.nbwave] = self.amp * np.cos( self.phi )
        cos_sin[self.nbwave:] = self.amp * np.sin( self.phi )
        return cos_sin


    def optimize(self, energyRatio):
        """Remove smallest component, so that remaining energy > original energy * energyRatio.

        Parameters
        ----------
        energyRatio : float
            Amount of energy to keep (1.0, conserve 100% of the energy).

        Returns
        -------
        Wif
            Wif with "optimized" frequencies.
        """
        if self.nbwave == 1 :
            return Wif(self)

        totalEnergy = np.sum(self.amp[:]**2)
        E = totalEnergy
        amp_sort_index = np.argsort(self.amp)

        #Identify index where energyRatio is reached in sorted amplitude list
        i = 0
        while ( E/totalEnergy > energyRatio):
            sort_i = amp_sort_index[i]
            E = E-self.amp[sort_i]**2
            i = i + 1

        #Cut the lists at this index
        optim_amp = self.amp[amp_sort_index[i:]]
        optim_freq = self.freq[amp_sort_index[i:]]
        optim_phi = self.phi[amp_sort_index[i:]]
        optim_beta = self.head[amp_sort_index[i:]]

        #Sort frequencies
        sort_index = np.argsort(optim_freq)
        optim_amp = optim_amp[sort_index]
        optim_freq = optim_freq[sort_index]
        optim_phi = optim_phi[sort_index]
        optim_beta = optim_beta[sort_index]

        #Return wif file
        return Wif( w = optim_freq, a = optim_amp, phi = optim_phi , b = optim_beta, depth = self.depth )

    def getTimeReversed( self ) :
        return Wif( w = self.freq, a = self.amp, phi = -self.phi , b = self.head, depth = self.depth )


    def offset_py(self, dt=0., dx=0., dy = 0.) :
        """Offset the wif, in place (change phases).

        Parameters
        ----------
        dt : float, optional
            Shift in time. The default is 0..
        dx : float, optional
            Shift in x direction. The default is 0..
        dy : float, optional
            Shift in y direction. The default is 0..

        Returns
        -------
        None.

        """

        k = self.getWaveNumbers()
        w = self.getFrequencies()
        dphi = - w * dt + k * ( dx * self.getCosHeadings() + dy * self.getSinHeadings())
        self.setPhases(self.phi + dphi)



    def beta(self, s=None, spectrum=None):
        """Return probability index, given a spectral density
        Only relevant to design wave (if "beta" has been minimized)
        """
        dw = self.freq[1] - self.freq[0]
        if s is None :
            s = ( spectrum.compute( self.freq ) * dw)**0.5
        return ( np.sum( (self.amp[:] / s[:])**2 ) )**0.5

    def convertStarSpecToSnoopy(self):
        """Convert heading convention from StarSpec/Ariane/Homer format to Snoopy/Opera format
            (cf. Spectral/plotHeadingConvention.py to check orientation)
        """
        self.setHeadings( np.pi - self.getHeadings() )