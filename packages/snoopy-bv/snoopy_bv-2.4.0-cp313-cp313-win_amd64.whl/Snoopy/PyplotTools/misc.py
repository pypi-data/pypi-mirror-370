import itertools
import numpy as np
from Snoopy import logger

colorCycle = ('b', 'r', 'c' , 'm', 'y' , 'k', 'g')
def newColorIterator(ccycle=None,cmap=None,n=10,bounds=[0,1]):
    import matplotlib.pyplot as plt
    if ccycle is not None:
        if ccycle=='default': clrCycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        elif hasattr(ccycle,'__len__'): clrCycle = ccycle
        else: print('Not Implemented')

    elif cmap is not None:
        import matplotlib
        colorMap = matplotlib.colormaps[cmap]
        clrCycle = (colorMap(i) for i in np.linspace(bounds[0],bounds[1],n))
    else:
        clrCycle = colorCycle
    return itertools.cycle(clrCycle)


markerCycle = ('o', 'v', "s", '*' , 'D', "+" , "x")
def newMarkerIterator(mcycle=None):
    if mcycle is not None:
        if hasattr(mcycle,'__len__'): mkrCycle = mcycle
        else: print('Not Implemented')
    else:
        mkrCycle = markerCycle
    return itertools.cycle(mkrCycle)


linestyleCycle = ('-', '--', '-.', ':')
def newLinestyleIterator(lcycle=None):
    if lcycle is not None:
        if hasattr(lcycle,'__len__'): lstCycle = lcycle
        else: print('Not Implemented')
    else:
        lstCycle = linestyleCycle
    return itertools.cycle(lstCycle)


def getAngleColorMappable( unit = "rad", cmap = "twilight" ):
    if "rad" in unit.lower() :
        vmax = 2*np.pi
    else :
        vmax = 360.
    return getColorMappable( vmin = 0.0 , vmax = vmax , cmap = cmap )


def getColorMappable( vmin, vmax, cmap = "viridis" ):
    """Return ScalarMappable, using cmap as color map, between vmin and vmax.

    Parameters
    ----------
    vmin : float
        Lower bound
    vmax : float
        Upper bound
    cmap : str, optional
        Color map. The default is "viridis".
        
    Returns
    -------
    scalarMap : ScalarMappable
        The scalar mappable

    Example
    -------
    >>> vlist = np.arange( 10 )
    >>> smappable = getColorMappable(1, 10, cmap = "cividis")
    >>> fig, ax = plt.subplots()
    >>> for v in vlist : 
    >>>    ax.axvline( v , color = smappable.to_rgba( v ) )
    >>> # In case colorbar is desired (instead or on top of legend)
    >>> fig.colorbar( mappable = tp_color, ax=ax, label = "Tp")
    """
    import matplotlib.colors as colors
    import matplotlib.cm as cm
    cNorm  = colors.Normalize( vmin=vmin, vmax=vmax)
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cmap)
    return scalarMap


def pyplotLegend(fig=None,ax=None):
    if fig is not None :
        ax = fig.get_axes()[0]
    handles, labels =  ax.get_legend_handles_labels()
    uniqueLabels = sorted(list(set(labels )))
    uniqueHandles = [handles[labels.index(l)] for l in uniqueLabels ]
    return uniqueHandles, uniqueLabels


def uniqueLegend(ax, *args, **kwargs) :
    ax.legend( *pyplotLegend(ax=ax), *args, **kwargs )


def autoscale_xy(ax,axis='y',margin=0.1):
    """This function rescales the x-axis or y-axis based on the data that is visible on the other axis.
    ax -- a matplotlib axes object
    axis -- axis to rescale ('x' or 'y')
    margin -- the fraction of the total height of the y-data to pad the upper and lower ylims"""

    import numpy as np

    def get_boundaries(xd,yd,axis):
        if axis == 'x':
            bmin,bmax = ax.get_ylim()
            displayed = xd[((yd > bmin) & (yd < bmax))]
        elif axis == 'y':
            bmin,bmax = ax.get_xlim()
            displayed = yd[((xd > bmin) & (xd < bmax))]
        h = np.max(displayed) - np.min(displayed)
        cmin = np.min(displayed)-margin*h
        cmax = np.max(displayed)+margin*h
        return cmin,cmax

    cmin,cmax = np.inf, -np.inf

    #For lines
    for line in ax.get_lines():
        xd = line.get_xdata(orig=False)
        yd = line.get_ydata(orig=False)
        new_min, new_max = get_boundaries(xd,yd,axis=axis)
        if new_min < cmin: cmin = new_min
        if new_max > cmax: cmax = new_max

    #For other collection (scatter)
    for col in ax.collections:
        xd = col.get_offsets().data[:,0]
        yd = col.get_offsets().data[:,1]
        new_min, new_max = get_boundaries(xd,yd,axis=axis)
        if new_min < cmin: cmin = new_min
        if new_max > cmax: cmax = new_max

    if   axis=='x': ax.set_xlim(cmin,cmax)
    elif axis=='y': ax.set_ylim(cmin,cmax)


def rgb_to_hexa( r, g, b ) :
    return f"#{r:02x}{g:02x}{b:02x}"

def hexa_to_rgb( hexcode ) :
    return tuple(map(ord,hexcode[1:].decode('hex')))

def negativeColor( r,g,b ):
    if max( np.array([r,g,b]) > 1. ) :
       return 255-r , 255-g, 255-b
    else :
       return 1. - r , 1.-g, 1.-b


def align_yaxis(ax1, ax2):
    """Align zeros of the two axes, zooming them out by same ratio

    from https://stackoverflow.com/questions/10481990/matplotlib-axis-with-two-scales-shared-origin
    """
    axes = np.array([ax1, ax2])
    extrema = np.array([ax.get_ylim() for ax in axes])
    tops = extrema[:,1] / (extrema[:,1] - extrema[:,0])
    # Ensure that plots (intervals) are ordered bottom to top:
    if tops[0] > tops[1]:
        axes, extrema, tops = [a[::-1] for a in (axes, extrema, tops)]

    # How much would the plot overflow if we kept current zoom levels?
    tot_span = tops[1] + 1 - tops[0]

    extrema[0,1] = extrema[0,0] + tot_span * (extrema[0,1] - extrema[0,0])
    extrema[1,0] = extrema[1,1] + tot_span * (extrema[1,0] - extrema[1,1])
    [axes[i].set_ylim(*extrema[i]) for i in range(2)]



def set_tick_format(ax, format = ".2%" , axis = "x", minor_format = None ) :
    """Set tick format.

    Parameters
    ----------
    ax : plt.Axis
        Axis.
    format : str, optional
        Major formatter. The default is ".2%".
    axis : str, optional
        'x' or 'y'. The default is "x".
    minor_format : str, optional
        Minor formatter. The default is None.

    """
    import matplotlib.ticker as tick

    

    if axis == "x" :
        axis_ = ax.xaxis
    elif axis == "y" :
        axis_ = ax.yaxis
    else :
        raise(Exception())

    if format == "concise_date":
        import matplotlib.dates as mdates
        axis_.set_major_formatter(  mdates.ConciseDateFormatter(axis_.get_major_locator())) 
    elif hasattr(format, "__call__"):
        axis_.set_major_formatter(tick.FuncFormatter( format ))
    else:
        axis_.set_major_formatter(tick.FuncFormatter( lambda x, p : f"{x:{format:}}"))

    if minor_format is not None :
        def fun_minor( x , p ):
            return f"{x:{minor_format:}}"
        axis_.set_minor_formatter(tick.FuncFormatter(fun_minor))

def set_major_format(*args, **kwargs) :
    logger.warning("'set_major_format' is deprecated, please use 'set_tick_format'")




class PointProjection():
    def __init__(self, ax, x, y , x_label = None, y_label = None, projection_x = True, projection_y = True,
                 y_label_offset = 1.005,
                 x_label_offset = 1.005, **kwargs):
        """Annotate a point on a graph (by showing horizontal and vertical projection)

        Parameters
        ----------
        ax : plt.Axis
            Graph to annotate.
        x : float
            x coordinate.
        y : float
            y coordinate.
        x_label : str, optional
            Point x label. The default is None.
        y_label : str, optional
            Point y label. The default is None.
        **kwargs : any
            argument passed to ax.plot().

        Example
        -------
        >>> fig, ax = plt.subplots()
        >>> ax.plot( [6. , 8] , [60. , 80] )
        >>> p = PointProjection(ax , 7, 70, x_label = "$f_x$" , y_label = "$f_y$", color = "red")
        """

        kwargs_ = { "linestyle" : "--", "color" : "blue", "marker" : None }
        kwargs_.update(kwargs)

        self.ax = ax
        self.x = x
        self.y = y

        xmin = ax.get_xlim()[0]
        ymin = ax.get_ylim()[0]

        self.projection_x = projection_x
        self.projection_y = projection_y

        if self.projection_x :
            self.vline, = self.ax.plot([x,x],[ymin,y] , **kwargs_)

        if self.projection_y :
            self.hline, = self.ax.plot([xmin,x],[y,y] , **kwargs_)

        self.update()
        self.ax.set( ylim = [ymin , None], xlim = [xmin , None] )
        self.ax.get_figure().canvas.mpl_connect("draw_event", self.update)


        self.ax.annotate( y_label, xy=(+0.04, y*y_label_offset ), xycoords = ("axes fraction", "data"), color = kwargs_["color"])
        self.ax.annotate( x_label, xy=(x*x_label_offset, +0.04), xycoords = ("data" , "axes fraction"), color = kwargs_["color"])

    def update(self, event=None):
        xmin = self.ax.get_xlim()[0]
        ymin = self.ax.get_ylim()[0]

        if self.projection_x :
            self.vline.set_data( [self.x, self.x], [ymin,self.y] )

        if self.projection_y :
            self.hline.set_data( [xmin, self.x], [self.y,self.y] )


if __name__ == "__main__" :
    from matplotlib import pyplot as plt

    fig, ax = plt.subplots()
    ax.plot( [6. , 8] , [60. , 80] )
    p = PointProjection(ax , 7, 70, x_label = "$f_x$" , y_label = "$f_y$", color = "red")









