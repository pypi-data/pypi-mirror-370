import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import _Spectral

deg2rad = np.pi / 180.
rad2deg = 1.0/deg2rad


"""Class to handle transfer function

    For rapid prototyping, back and forth with pandas are used.
    Most of the routines could be transfer to the c++ base class.
"""
class MQtf(_Spectral.MQtf) :
    """
	Full Multidirectional Quadratic Transfer Function data definition, called MQtf here.          

    MQtf terms are obtained from a second order diffraction-radiation analysis.
    They correspond to the mean loads applied to the vessel 
    when subjected to the action of a bichromatic wave of unitary amplitude. 
    They are calculated for given vessel motion coordinates called here modes. 
    The MQtf are then available for Nm modes, but also for 
    a limited number Nb of incidences relative to the vessel heading,
    and couples of wave frequencies Nf x Ndf. 
    
    MQtf is then a Nb x Nf x Ndf x Nb matrix defined in the rigid body reference frame. 
    """
    #MQtf is then a Nb x Nf x Ndf x Nb x Nm matrix defined in the rigid body reference frame. 

    def __init__(self, *args , **kwargs) :
        if len(args) == 1 and type(args[0]) == str :
            super().__init__(  MQtf.ReadHstar( args[0]  ))
        elif "filename" in kwargs :
            super().__init__( MQtf.ReadHstar( **kwargs  ) )
        else :
            super().__init__( *args , **kwargs )


    def __str__(self) :
        s = "Frequency ({:}) , {:}\n".format( self.nbfreq , self.freq )
        s += "Headings ({:}) , {:}\n".format( self.nbdiff , self.diff )
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
        tmp_ = _Spectral.MQtf.__add__( self, rhs  )
        return self.__class__(tmp_)

    def __sub__(self , rhs):
        tmp_ = _Spectral.MQtf.__sub__( self, rhs  )
        return self.__class__(tmp_)

    def __mul__(self , rhs):
        tmp_ = _Spectral.MQtf.__mul__( self, rhs  )
        return self.__class__(tmp_)

    __rmul__ = __mul__

    def __div__(self , rhs):
        tmp_ = _Spectral.MQtf.__div__( self, rhs  )
        return self.__class__(tmp_)


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
        Read mqtf data from HydroStar files (could be consolidated/optimized)
        """

        #Read header
        with open(filename, 'r') as fil :
            headerl = [line.strip() for line in fil.readlines() if line.strip()and line.strip().startswith('#')]
        header = [line.split() for line in headerl]

        for iline, line in enumerate(header):
            #if line[0] == "#DIRECTION" : direction = dDirToMode[int(line[2])]  # Not use for now
            if line[0] == "#NBHEADING"  : nbhead = int(line[1])
            elif line[0] == "#HEADING"    : heading = np.deg2rad( np.array( list(map(float , line[1:])) , dtype = np.float64    ))
            elif line[0] == "#DIFF"       : diff = np.array( list(map(float , line[1:])) , dtype = np.float64    )
            elif "Water density" in headerl[iline]  : rho = float( line[ 5 ] )
            elif "Waterdepth" in line  :
               if line[3][:3].lower() == "inf" : waterdepth = 0.
               else : waterdepth = float(line[ 3 ])
            elif line[0] == "#QTFMODE"  : qtfmode = line[1]
            elif "Ref.pt incident wave" in headerl[iline] :
               waveRefPoint = np.array( [float(line[6].strip("(")), float(line[7].strip(")"))], dtype=np.float64 )
            elif line[0] == "#COORD" :   refPoint = np.array( list(map(str, line[1:] )), dtype=np.float64)

        speed = 0.0
        nbdiff = len(diff)
        data = np.loadtxt(filename)
        nbfreq = int(len(data) / nbhead / nbhead)
        freq = data[0:nbfreq  ,0]

        if qtfmode == "Diff" : mode = _Spectral.QtfMode.DIFF
        elif qtfmode == "Sum" : mode = _Spectral.QtfMode.SUM
        else : raise (Exception)


        #Values
        #values = np.empty((nbhead, nbfreq, nbdiff, nbhead, 1), dtype=complex)
        values = np.empty((nbhead, nbfreq, nbdiff, nbhead), dtype=complex)
        for ihead1 in range(nbhead):
            for ihead2 in range(nbhead):
                for ifreq in range(nbfreq):
                    for idiff in range(nbdiff):
                        #values[ihead1, ifreq, idiff, ihead2, 0] = complex(data[nbfreq*(nbhead*ihead1+ihead2)+ifreq, 1+2*idiff],
                        #                                                  data[nbfreq*(nbhead*ihead1+ihead2)+ifreq, 2+2*idiff])
                        values[ihead1, ifreq, idiff, ihead2] = complex(data[nbfreq*(nbhead*ihead1+ihead2)+ifreq, 1+2*idiff],
                                                                       data[nbfreq*(nbhead*ihead1+ihead2)+ifreq, 2+2*idiff])

        return cls(b=heading, w=freq, dw=diff, mqtf=values,
                   forwardSpeed=speed, refPoint=refPoint,
                   waveRefPoint=waveRefPoint,
                   qtfMode=mode)

    def writeHst( self, filename ):
        """
            write MQtf to the file
        """
        with open(filename, "w") as f:
            f.write("# Project :\n")
            f.write("# User    :\n")
            f.write("# File : "+filename +"\n")
            f.write("# Constants used in computations :\n")
            f.write("#     Reference length     :     1.0000\n")
            f.write("#     Water density (rho)  :  1025.0000\n")
            f.write("#     Gravity acceleration :     9.8100\n")
            f.write("#     Waterdepth           : 100.0000\n")
            s = str(self.getWaveReferencePoint()).replace("[", "").replace("]","")
            f.write("#     Ref.pt incident wave : (      "+s+")\n")
            f.write("#            Forward speed :   0.0000  m/s   \n#\n")
            f.write("#------------------------------------------------------------------------\n")
            f.write("#QTFTYPE \"2NDLOAD\"\n")
            f.write("#CPLXTYPE 0\n")
            f.write("#QTFMODE Diff\n")
            f.write("#DIRECTION  \"           1\n")
            s = str(self.getReferencePoint()).replace("[", "").replace("]","")
            f.write("#COORD     "+s+"\n")
            f.write("#NBHEADING   "+str(self.nbhead)+"\n")
            f.write("#HEADING      ") 
            for h in self.getHeadings():
                f.write(str(h*180/np.pi) +"  ")
            f.write("\n")
            f.write("#DIFF    ")
            for dw in self.getDeltaFrequencies():
                f.write(str(dw) +"  ")
            f.write("\n")
            f.write("#---w(r/s)-----------------------------------------------------\n")
            for ib1, b1 in enumerate(self.getHeadings()):
                f.write("##Heading1 = "+str(b1*180/np.pi)+"\n")
                for ib2, b2 in enumerate(self.getHeadings()):
                    f.write("#Heading2 = "+str(b2*180/np.pi)+"\n")
                    for iw, w in enumerate(self.getFrequencies()):
                        f.write("{:9.5e}".format(w))
                        for idw, dw in enumerate(self.getDeltaFrequencies()):
                            #v = self.cvalues[ib1, iw, idw, ib2, 0]
                            v = self.cvalues[ib1, iw, idw, ib2]
                            reV = v.real
                            imV = v.imag
                            f.write("  {: 9.5e}  {: 9.5e}".format(reV, imV))
                        f.write("\n")
                    f.write("\n\n")

    @classmethod
    def FromDataFrame( self , df , metaData ) :
        """
           Construct RAO from pandas dataFrame (shortcut to use pandas to work on Rao)
        """

        #TODO


    def toDataFrame(self , cplxType = "cvalues") :
        """
        Convert to pandas dataFrame
        """
        from pandas import DataFrame

        #Data
        df = DataFrame(index=self.freq, data = getattr(self , cplxType),
                       columns = self.head )

        #Metadata
        for key , val in Rao.getMetaData(self).items() :
            setattr( df , key ,  val)
        return df



    def getHeadDataFrame( self , heading, heading2 = None ) :
        """
        Return a dataframe w / diff corresponding to heading.
        """

        ihead = np.argmin( np.abs(self.head - heading) )
        if heading2 is None:
            ihead2 = ihead
        else:
            ihead2 = np.argmin( np.abs(self.head -heading2) )
        # FIXME only one component in order to have a 2D array
        #return pd.DataFrame( index = self.freq , data = self.getComplexData()[ihead, :, :, 0] ,  columns = self.diff , dtype = complex )
        return pd.DataFrame( index = self.freq , data = self.getComplexData()[ihead, :, :, ihead2] ,  columns = self.diff , dtype = complex )



    def plot_wiwj( self , ax = None, part = "module"  ) :
        """
          Plot the component amplitude against the frequency
        """
        #TODO
        fig , ax = plt.subplots()
        return ax

    def sprintData(self):
        """
        Just to print out on the screen for the check purpose
        """
        values = self.getComplexData()
        heading = self.getHeadings()
        freq = self.getFrequencies()
        nbhead = self.getNHeadings()
        nbfreq = self.getNFrequencies()
        nbdiff = self.getNDeltaFrequencies()

        s = ""
        for ihead1 in range(nbhead):
            s += "##Heading1 ={:7.2f}\n".format(heading[ihead1]*rad2deg)
            for ihead2 in range(nbhead):
                s += "#Heading2 ={:7.2f}\n".format(heading[ihead2]*rad2deg)
                for ifreq in range(nbfreq):
                    s += "{:13.4e}".format(freq[ifreq])
                    for idiff in range(nbdiff):
                        #s += "{:13.4e}{:13.4e}".format(values[ihead1, ifreq, idiff, ihead2, 0].real, values[ihead1,ifreq,idiff,ihead2,0].imag)
                        s += "{:13.4e}{:13.4e}".format(values[ihead1, ifreq, idiff, ihead2].real, values[ihead1,ifreq,idiff,ihead2].imag)
                    s += "\n"
                s += "\n\n"
        return s

    def printData(self):
        print(self.sprintData())

    def getMQtfIn2piRange(self):
        return MQtf(super().getMQtfIn2piRange())

    def getMQtfAtFrequencies(self, *args):
        return MQtf(super().getMQtfAtFrequencies(*args))

    def getMQtfAtHeadings(self, *args):
        return MQtf(super().getMQtfAtHeadings(*args))

    def plot_freq(self, dw, head1, head2, *args, **kwargs):
        """
        plots the values vs frequencies for a given dw, head1 and head2.
        if the 'ax' variable is given by **kwargs, then the given Axes 'ax' are used
        if the 'real' keyword is True (default) the real part is plotted
        if the 'imag' keyword is True (default) the imag part is plotted
        if none of the 'real' and 'imag' is provided, the absolut value is plotted
        """
        ax = kwargs.get('ax', None)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            del kwargs['ax']
        re = kwargs.get('real', None)
        im = kwargs.get('imag', None)
        abs_ = True
        if re is None:
            re = True
        else:
            del kwargs['real']
            abs_ = False
        if im is None:
            im = True
        else:
            del kwargs['imag']
            abs_ = False
        if dw < self.nbdiff and head1 < self.nbhead and head2 < self.nbhead:
            values = self.getComplexData()
            if abs_:
                #ax.plot(self.freq, np.abs(values[head1, :, dw, head2, 0]), *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Abs", **kwargs)
                ax.plot(self.freq, np.abs(values[head1, :, dw, head2]), *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Abs", **kwargs)
            else:
                if re:
                    #ax.plot(self.freq, values[head1, :, dw, head2, 0].real, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Real", **kwargs)
                    ax.plot(self.freq, values[head1, :, dw, head2].real, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Real", **kwargs)
                if im:
                    #ax.plot(self.freq, values[head1, :, dw, head2, 0].imag, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Imag", **kwargs)
                    ax.plot(self.freq, values[head1, :, dw, head2].imag, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Imag", **kwargs)

    def plot_head(self, freq, dw, head2, *args, **kwargs):
        """
        plots the values vs headings for a given freq, dw and head2.
        if the 'ax' variable is given by **kwargs, then the given Axes 'ax' are used
        if the 'real' keyword is True (default) the real part is plotted
        if the 'imag' keyword is True (default) the imag part is plotted
        if none of the 'real' and 'imag' is provided, the absolut value is plotted
        """
        ax = kwargs.get('ax', None)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            del kwargs['ax']
        re = kwargs.get('real', None)
        im = kwargs.get('imag', None)
        abs_ = True
        if re is None:
            re = True
        else:
            del kwargs['real']
            abs_ = False
        if im is None:
            im = True
        else:
            del kwargs['imag']
            abs_ = False
        if dw < self.nbdiff and freq < self.nbfreq and head2 < self.nbhead:
            values = self.getComplexData()
            if abs_:
                #ax.plot(self.head*rad2deg, np.abs(values[:, freq, dw, head2, 0]), *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Abs", **kwargs)
                ax.plot(self.head*rad2deg, np.abs(values[:, freq, dw, head2]), *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Abs", **kwargs)
            else:
                if re:
                    #ax.plot(self.head*rad2deg, values[:, freq, dw, head2, 0].real, *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Real", **kwargs)
                    ax.plot(self.head*rad2deg, values[:, freq, dw, head2].real, *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Real", **kwargs)
                if im:
                    #ax.plot(self.head*rad2deg, values[:, freq, dw, head2, 0].imag, *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Imag", **kwargs)
                    ax.plot(self.head*rad2deg, values[:, freq, dw, head2].imag, *args, label = "w = " +str(self.freq[freq]) +". H2 = " +str(self.head[head2]*rad2deg)+ ", dw = " +str(self.diff[dw]) +" Imag", **kwargs)

    def plot_diff(self, freq, head1, head2, *args, **kwargs):
        """
        plots the values vs difference frequency for a given freq, head1 and head2.
        if the 'ax' variable is given by **kwargs, then the given Axes 'ax' are used
        if the 'real' keyword is True (default) the real part is plotted
        if the 'imag' keyword is True (default) the imag part is plotted
        if none of the 'real' and 'imag' is provided, the absolut value is plotted
        """
        ax = kwargs.get('ax', None)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            del kwargs['ax']
        re = kwargs.get('real', None)
        im = kwargs.get('imag', None)
        abs_ = True
        if re is None:
            re = True
        else:
            del kwargs['real']
            abs_ = False
        if im is None:
            im = True
        else:
            del kwargs['imag']
            abs_ = False
        if freq < self.nbfreq and head1 < self.nbhead and head2 < self.nbhead:
            values = self.getComplexData()
            if abs_:
                #ax.plot(self.diff, np.abs(values[head1, freq, :, head2, 0]), *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Abs", **kwargs)
                ax.plot(self.diff, np.abs(values[head1, freq, :, head2]), *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Abs", **kwargs)
            else:
                if re:
                    #ax.plot(self.diff, values[head1, freq, :, head2, 0].real, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Real", **kwargs)
                    ax.plot(self.diff, values[head1, freq, :, head2].real, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Real", **kwargs)
                if im:
                    #ax.plot(self.diff, values[head1, freq, :, head2, 0].imag, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Imag", **kwargs)
                    ax.plot(self.diff, values[head1, freq, :, head2].imag, *args, label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)+ ", w = " +str(self.freq[freq]) +" Imag", **kwargs)
    
    def plot_wdw(self, head1, head2, *args, **kwargs):
        ax = kwargs.get('ax', None)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            del kwargs['ax']
        re = kwargs.get('real', None)
        im = kwargs.get('imag', None)
        label = kwargs.get('label', None)
        abs_ = True
        if re is None:
            re = False
        else:
            del kwargs['real']
            abs_ = False
        if im is None:
            im = False
        else:
            del kwargs['imag']
            abs_ = False
        if head1 < self.nbhead and head2 < self.nbhead:
            label_ = False
            if label is None:
                label = "H1 = " +str(self.head[head1]*rad2deg) +". H2 = " +str(self.head[head2]*rad2deg)
                kwargs['label'] = label
                label_ = True
            values = self.getComplexData()
            X, Y = np.meshgrid(self.diff, self.freq)
            if abs_:
                if label_:
                    kwargs['label'] += " Abs"
                #ax.plot_wireframe(X, Y, np.abs(values[head1, :, :, head2, 0]), *args, **kwargs)
                #ax.plot_surface(X, Y, np.abs(values[head1, :, :, head2, 0]), *args, cmap = "viridis", edgecolor="none")
                ax.plot_wireframe(X, Y, np.abs(values[head1, :, :, head2]), *args, **kwargs)
            else:
                if re:
                    kwargs_re = dict(kwargs)
                    if label_:
                        kwargs_re['label'] += " Real"
                    #ax.plot_wireframe(X, Y, values[head1, :, :, head2, 0].real, *args, **kwargs_re)
                    ax.plot_wireframe(X, Y, values[head1, :, :, head2].real, *args, **kwargs_re)
                if im:
                    kwargs_im = dict(kwargs)
                    if label_:
                        kwargs_im['label'] += " Imag"
                    #ax.plot_wireframe(X, Y, values[head1, :, :, head2, 0].imag, *args, **kwargs_im)
                    ax.plot_wireframe(X, Y, values[head1, :, :, head2].imag, *args, **kwargs_im)

    def plot_wh(self, dw, head2, *args, **kwargs):
        ax = kwargs.get('ax', None)
        if ax is None:
            fig, ax = plt.subplots()
        else:
            del kwargs['ax']
        re = kwargs.get('real', None)
        im = kwargs.get('imag', None)
        label = kwargs.get('label', None)
        abs_ = True
        if re is None:
            re = False
        else:
            del kwargs['real']
            abs_ = False
        if im is None:
            im = False
        else:
            del kwargs['imag']
            abs_ = False
        if dw < self.nbdiff and head2 < self.nbhead:
            label_ = False
            if label is None:
                label = "dw = " +str(self.diff[dw]) +". H2 = " +str(self.head[head2]*rad2deg)
                kwargs['label'] = label
                label_ = True
            values = self.getComplexData()
            X, Y = np.meshgrid(self.freq, self.head*rad2deg)
            if abs_:
                if label_:
                    kwargs['label'] += " Abs"
                #ax.plot_wireframe(X, Y, np.abs(values[:, :, dw, head2, 0]), *args, **kwargs)
                #ax.plot_surface(X, Y, np.abs(values[head1, :, :, head2, 0]), *args, cmap = "viridis", edgecolor="none")
                ax.plot_wireframe(X, Y, np.abs(values[:, :, dw, head2]), *args, **kwargs)
            else:
                if re:
                    kwargs_re = dict(kwargs)
                    if label_:
                        kwargs_re['label'] += " Real"
                    #ax.plot_wireframe(X, Y, values[:, :, dw, head2, 0].real, *args, **kwargs_re)
                    ax.plot_wireframe(X, Y, values[:, :, dw, head2].real, *args, **kwargs_re)
                if im:
                    kwargs_im = dict(kwargs)
                    if label_:
                        kwargs_im['label'] += " Imag"
                    #ax.plot_wireframe(X, Y, values[:, :, dw, head2, 0].imag, *args, **kwargs_im)
                    ax.plot_wireframe(X, Y, values[:, :, dw, head2].imag, *args, **kwargs_im)

if __name__ == "__main__" :

    qtf = MQtf("/home/iten/Work/calculations/hsomf/sym0m/rao/qtffx.qtf")
    qtf = qtf.getMQtfIn2piRange()
    f = np.linspace(0.2, 1.5, 30)
    qtf = qtf.getMQtfAtFrequencies(f)
    h = np.linspace(0.0, 2*np.pi, 10)
    qtf = qtf.getMQtfAtHeadings(h)
    qtf.printData()

