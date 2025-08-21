"""

   Additional plotting tools for pandas DataFrame

"""

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.legend import Legend
from Snoopy import logger
import numpy as np
import pandas as pd



def centerToEdge(array):
    dx = array[1:] - array[:-1]
    if (abs(dx / dx[0] - 1) < 0.01).all():
        return np.append(array - 0.5*dx[0], array[-1] + 0.5*dx[0])
    else:
        raise(ValueError("Can not find edge from center if bins are not considered evenly spaced"))

class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def compareSurfaceAndMarginals(  df1, df2, surfaceArgs, cumulative = True, name1 = None, name2 = None, kwargs_l1= {}, kwargs_l2 = {}):

    fig, axList = plt.subplots( nrows = 2, ncols = 2 )

    dfSurface(df1, ax = axList[1,0], **surfaceArgs)
    axList[1,0].set_xlabel( axList[1,0].get_xlabel() +  "\n" + name1  )
    dfSurface(df2, ax = axList[0,1], **surfaceArgs)
    axList[0,1].set_xlabel( axList[0,1].get_xlabel() +  "\n" + name2  )


    for df, name, kwargs in [ (df1, name1, kwargs_l1), (df2, name2, kwargs_l2)]:
        if not cumulative :
            axList[1,1].barh( df.index, df.sum(axis=1), alpha = 0.5 , label = name)
            axList[0,0].bar( df.columns, df.sum(axis=0), alpha = 0.5, label = name )
        else:
            hsCum = np.add.accumulate( df.sum(axis=1)[::-1] )[::-1]  # 1-np.add.accumulate( df.sum(axis=1) )
            axList[1,1].plot(hsCum,  hsCum.index, label = name, **kwargs )
            axList[1,1].set_xscale("log")
            tzCum = np.add.accumulate( df.sum(axis=0)[::-1] )[::-1]  # 1-np.add.accumulate( df.sum(axis=0) )
            axList[0,0].plot(tzCum.index, tzCum, "o", label = name, **kwargs )
            axList[0,0].set_yscale("log")

    axList[0,0].legend()
    ymin = min( df1.index.min() , df2.index.min())
    ymax = max( df1.index.max() , df2.index.max())

    axList[1,1].set_ylim([ymin, ymax])
    axList[1,0].set_ylim([ymin, ymax])

    xmin = min( df1.columns.min() , df2.columns.min())
    xmax = max( df1.columns.max() , df2.columns.max())

    axList[0,0].set_xlim([xmin, xmax])
    axList[0,1].set_xlim([xmin, xmax])

    axList[0,0].set_ylabel( "Exceedance rate " + df.columns.name )
    axList[1,1].set_xlabel( "Exceedance rate " + df.index.name )
    plt.tight_layout()
    return fig

def dfSurfaceAndMarginals( df, surfaceArgs, cumulative = True ):
    fig, axList = plt.subplots( nrows = 2, ncols = 2 )

    dfSurface(df, ax = axList[1,0], **surfaceArgs)
    if not cumulative :
        axList[1,1].barh( df.index, df.sum(axis=1), alpha = 0.5 )
        axList[0,0].bar( df.columns, df.sum(axis=0), alpha = 0.5 )
    else:
        hsCum = 1-np.add.accumulate( df.sum(axis=1) )
        axList[1,1].plot(hsCum,  hsCum.index, "o" )
        axList[1,1].set_xscale("log")
        tzCum = 1-np.add.accumulate( df.sum(axis=0) )
        axList[0,0].plot(tzCum.index, tzCum, "o" )
        axList[0,0].set_yscale("log")

    axList[1,1].set_ylim([df.index.min(), df.index.max()])
    axList[1,0].set_ylim([df.index.min(), df.index.max()])

    axList[0,0].set_ylabel( "Exceedance rate " + df.columns.name )
    axList[1,1].set_ylabel( "Exceedance rate " + df.index.name )

    axList[0,0].set_xlim([df.columns.min(), df.columns.max()])
    axList[0,1].set_xlim([df.columns.min(), df.columns.max()])

    axList[0,1].axis("off")
    plt.tight_layout()
    return fig


def dfSurface(df, ax=None, nbColors=200, interpolate=True, polar=False, polarConvention="seakeeping",
              colorbar=False, cmap='viridis', scale=None, vmin=None, vmax=None, midpoint=None,
              clip=False, nbTicks=11, image_path = None, hatch = None,**kwargs):
    """Surface plot from pandas.DataFrame.

    Parameters
    ----------
    df: pandas.DataFrame or xarray.DataArray

        Dataframe formmated as follow:
        * columns : x or theta values
        * index : y or r values
        * data = data

        DataArray of dimension 2 formmated as follow:
        * data = data
        * dims : x and y values

    ax: matplotlib.axes._subplots.AxesSubplot
        Specify existing axis to plot

    nbColors: int, default 200
        Number of colorscale levels

    interpolate: bool, default True
        * if True, data are considered as node value and interpolated in between
        * if False, data are considered as center cell value  => similar to sns.heatmap

    colorbar: bool, default False
        Specify is colobar should be plotted

    scale: function, default None
        Function to scale dataframe values

    vmin: float, default None
        Lower contour boundary

    vmax: float, default None
        Upper contour boundary

    clip: bool, default False
        Clip dataframe values with vmin and vmax (othervise, value outside [vmin, vmax] appear blank).
        
    hatch : tuple(2)
        hatches the area between the two iso-line prescribed
        
    image_path : str or None
        Path to image to add in background

    **kwargs:
        Arguments applied to matplotlib.axes.Axes.contourf
    """

    import xarray as xa
    if type(df)==xa.DataArray: raise NotImplementedError

    yaxis = df.columns.astype(float)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=polar)
        if polar:
            if polarConvention == "seakeeping":
                ax.set_theta_zero_location("S")
                ax.set_theta_direction(1)
            elif polarConvention == "geo":
                ax.set_theta_zero_location("N")
                ax.set_theta_direction(1)


    if (vmin is not None) and (vmax is not None):
        lvls = np.linspace(vmin,vmax,nbColors)
    else:
        lvls = nbColors

    if clip and ((vmin is not None) or (vmax is not None)):
        df = df.clip(vmin,vmax)

    if midpoint is not None:
        n0 = vmin if vmin is not None else df.min().min()
        n1 = vmax if vmax is not None else df.max().max()
        norm = MidpointNormalize(vmin=n0,vmax=n1,vcenter=midpoint)
    else:
        norm = None

    if scale is not None:
        val = scale(df.values)
    else :
        val = df.values

    if interpolate:
        cax = ax.contourf(yaxis, df.index, val, cmap=cmap, levels=lvls, norm=norm, **kwargs)
    else:
        try:
            cax = ax.pcolormesh(centerToEdge(yaxis), centerToEdge(df.index), val, cmap=cmap, vmin=vmin, vmax=vmax, **kwargs)
        except ValueError as e:
            raise(Exception(f"{e.args[0]:}\nIndex is not evenly spaced, try with interpolate = True"))

    # Add x and y label if contains in the dataFrame
    if not polar:
        if df.columns.name is not None:
            ax.set_xlabel(df.columns.name)
        if df.index.name is not None:
            ax.set_ylabel(df.index.name)
        
    if hatch is not None:
        ax.contourf(yaxis, df.index, val,  color = "black", levels=hatch, hatches=["/"] )
        ax.contour(yaxis, df.index, val,  levels=hatch, colors = "black")

    # Add colorbar, make sure to specify tick locations to match desired ticklabels
    if colorbar:
        cbar = ax.get_figure().colorbar(cax)
        if isinstance(colorbar, str) :
            cbar.set_label(colorbar)
        if (vmin is not None) or (vmax is not None):
            t0 = vmin if vmin is not None else cbar.get_ticks()[0]
            t1 = vmax if vmax is not None else cbar.get_ticks()[-1]
            tks = np.linspace(t0,t1,nbTicks)
            # print(tks)
            cbar.set_ticks(tks)
            cbar.set_ticklabels([f'{tk:.2f}' for tk in tks])
            
    # add image to the center
    if image_path is not None:
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        img = plt.imread(image_path)
        imagebox = OffsetImage(img, zoom=0.2)
        ab = AnnotationBbox(imagebox, (0, 0), frameon=False)
        ax.add_artist(ab)

    return ax



def dfIsoContour(df, ax=None, polar=False, polarConvention="seakeeping", inline=True,
                 clabels=None, legend = False, ccolor = None, **kwargs):
    """Iso contour plot from pandas.DataFrame

    Parameters
    ----------
    df: pandas.DataFrame
        Dataframe formmated as follow:

        * index : y or theta values
        * columns : x or theta values
        * data = data

    ax: matplotlib.axes._subplots.AxesSubplot
        Specify existing axis to plot
    polar : bool, optional
        Plot in polar coordinates. The default is False.
    polarConvention : str, optional
        Convention for polar plots. The default is "seakeeping".
    inline : bool, optional
        Put level description on the line. The default is True.
    clabels: list, optional
        Custom contour labels
    legend : bool, optional
        Put iso level in legend. The default is False.
    ccolor : None or list, optional
        override iso-line colors. The default is None.

    """
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, polar=polar)
        if polar:
            if polarConvention == "seakeeping":
                ax.set_theta_zero_location("S")
                ax.set_theta_direction(1)
            elif polarConvention == "geo":
                ax.set_theta_zero_location("N")
                ax.set_theta_direction(1)

    cax = ax.contour(df.columns.astype(float), df.index, df.values, **kwargs)

    if inline:
        if clabels is not None:
            fmt = {}
            for l, s in zip(cax.levels, clabels):
                fmt[l] = s
            ax.clabel(cax, cax.levels, inline=True, fmt=fmt, fontsize=10)
        else:
            ax.clabel(cax, inline=1, fontsize=10,  fmt=r"%1.1f")

    #Legend
    if legend  :
        for i, l in enumerate(clabels) :
            cax.collections[i].set_label(l)
        ax.legend()

    if ccolor is not None :
        for i, cc in enumerate(ccolor) :
            cax.collections[i].set_color( cc )

    # Add x and y label if contained in the dataFrame
    if df.columns.name is not None:
        ax.set_xlabel(df.columns.name)
    if df.index.name is not None:
        ax.set_ylabel(df.index.name)
    return ax


def dfSlider(dfList, labels=None, ax=None, display=True, **kwargs):
    """ Interactive 2D plots, with slider to select the frame to display

    Column is used as x axis
    Index is used as frame/time (which is selected with the slider)

    :param dfList: List of DataFrame to animate
    :param labels: labels default = 1,2,3...
    :param ax: Use existing ax if provided
    :param display: display the results (wait for next show() otherwise)

    :return:  ax

    """

    print("Preparing interactive plot")
    from matplotlib.widgets import Slider
    import numpy as np

    # Make compatible with single dataFrame input
    if type(dfList) is not list:
        dfList = [dfList]
    if labels is None:
        labels = [i for i in range(len(dfList))]

    if ax is None:
        fig, ax = plt.subplots()

    plt.subplots_adjust(bottom=0.20)
    ax.grid(True)

    a0 = 0
    global currentValue
    currentValue = dfList[0].index[a0]

    lList = []
    for idf, df in enumerate(dfList):
        l, = ax.plot(df.columns.astype(float).values, df.iloc[a0, :], lw=2, label=labels[idf], **kwargs)
        lList.append(l)

    ax.legend(loc=2)

    df = dfList[0]
    ax.set_title(df.index[0])

    tmin = min([min(df.columns.astype(float).values) for df in dfList])
    tmax = max([max(df.columns.astype(float).values) for df in dfList])
    ymin = min([df.min().min() for df in dfList])
    ymax = max([df.max().max() for df in dfList])

    #plt.axis( [tmin, tmax, ymin , ymax ] )
    ax.set_xlim([tmin, tmax])
    ax.set_ylim([ymin, ymax])

    axTime = plt.axes([0.15, 0.10, 0.75, 0.03], facecolor='lightgoldenrodyellow')
    sTime = Slider(axTime, 'Time', df.index[0], df.index[-1], valinit=a0)

    def update(val):
        global currentValue
        t = []
        for i, df in enumerate(dfList):
            itime = np.argmin(np.abs(df.index.values - sTime.val))
            lList[i].set_ydata(df.iloc[itime, :])
            t.append("{:.1f}".format(df.index[itime]))
            currentValue = val
        ax.set_title(" ".join(t))
        ax.get_figure().canvas.draw_idle()

    update(currentValue)

    def scroll(event):
        global currentValue
        s = 0
        if event.button == 'down' and currentValue < tmax:
            s = +1
        elif event.button == 'up' and currentValue > tmin:
            s = -1
        dt = dfList[0].index[1]-dfList[0].index[0]
        sTime.set_val(currentValue + s*dt)

    ax.get_figure().canvas.mpl_connect('scroll_event', scroll)
    sTime.on_changed(update)

    if display:
        plt.show()

    # Return ax, so that it can be futher customized ( label... )
    return ax


def dfSlider2D(df, labels=None, ax=None, display=True, **kwargs):
    """Interactive 2D plots, with slider to select the frame to display.

    Parameters
    ----------
    df : pd.Dataframe
        Dataframe, with time as index, and x,y as column (multi-index).
    ax : plt.Axis, optional
        Use existing ax if provided. The default is None.
    display : bool, optional
        call plt.show(). The default is True.

    Returns
    -------
    ax : plt.Axis
        The plot.
    """
    
    logger.info("Preparing interactive plot")
    from matplotlib.widgets import Slider
    import numpy as np

    if ax is None:
        fig, ax = plt.subplots()

    plt.subplots_adjust(bottom=0.20)
    ax.grid(True)

    a0 = 0
    global currentValue, cf
    currentValue = df.index[a0]

    df0 = df.iloc[a0].unstack()
    x = df0.index.values
    y = df0.columns.values

    cf = ax.contourf(y, x , df0.values, **kwargs  )

    ax.set_title(df.index[0])

    tmin = min(df.index.astype(float).values)
    tmax = max(df.index.astype(float).values)

    axTime = plt.axes([0.15, 0.10, 0.75, 0.03], facecolor='lightgoldenrodyellow')
    sTime = Slider(axTime, 'Time', df.index[0], df.index[-1], valinit=a0)

    def update(val):
        global currentValue, cf
        
        itime = np.argmin(np.abs(df.index.values - sTime.val))
        
        for coll in cf.collections:
            coll.remove()
        cf = ax.contourf(y, x, df.iloc[itime].unstack().values,  **kwargs)

        currentValue = val
        ax.set_title( f"{val:}" )
        ax.get_figure().canvas.draw_idle()

    update(currentValue)

    def scroll(event):
        global currentValue
        s = 0
        if event.button == 'down' and currentValue < tmax:
            s = +1
        elif event.button == 'up' and currentValue > tmin:
            s = -1
        dt = df.index[1]-df.index[0]
        sTime.set_val(currentValue + s*dt)

    ax.get_figure().canvas.mpl_connect('scroll_event', scroll)
    sTime.on_changed(update)

    if display:
        plt.show()

    # Return ax, so that it can be futher customized ( label... )
    return ax

def dfAnimate(df, movieName=None, nShaddow=0, fps=25, xlim=None, ylim=None, xlabel=None, ylabel=None, codec="h264", extra_args = None, ax = None, time_label = "s", **kwargs):
    """Animate a dataFrame where time is the index, and columns are the "spatial" position

    Parameters
    ----------
    df : DataFrame
        Dataframe to animate, columns as x axis, and index as time.
    movieName : str or None, optional
        Filename for output file, if None, interactive animation is displayed. Default to None
    nShaddow : int, optional
        Number of "shaddow" steps, by default 0
    fps : int, optional
        _description_, by default 25
    xlim/ylim : tuple, optional
        bounds, by default None
    xlabel / ylabel : str, optional
        Labels, by default None
    codec : str, optional
        Codec, by default "h264"
    extra_args : _type_, optional
        extra_args passed to FFMpegWriter, by default None
    ax : plt.Axis or None, optional
        Where to plot, by default None
    time_label : str or fun, optional
        Time unit or function to format title with time, by default "s"
    """

    from matplotlib import animation

    if isinstance(time_label, str):
        time_label_fun = f"t = {{:.1f}} {time_label:}".format
    else:
        time_label_fun = time_label

    if movieName is not None :
        logger.info("Making animation file : " + movieName)

    global pause
    pause = False

    def onClick(event):
        global pause
        pause ^= True

    nShaddow = max(1, nShaddow)

    if ax is None :
        fig, ax = plt.subplots()
    else :
        fig = ax.get_figure()
        
    fig.canvas.mpl_connect('button_press_event', onClick)
    ls = []
    for i in range(nShaddow):
        if i == 0:
            color = "black"
        else:
            color = "blue"
        ltemp,  = ax.plot([], [], lw=1, alpha=1-i*1./nShaddow, color=color, **kwargs)
        ls.append(ltemp)

    xVal = df.columns.astype(float)

    ax.grid(True)

    if xlim:
        ax.set_xlim(xlim)
    else:
        ax.set_xlim(min(xVal), max(xVal))

    if ylim:
        ax.set_ylim(ylim)
    else:
        ax.set_ylim(df.min().min(), df.max().max())

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    def run(itime):
        ax.set_title( time_label_fun( df.index[itime])  )
        for s in range(nShaddow):
            if not pause:
                if itime > s:
                    ls[s].set_data(xVal, df.iloc[(itime - s), :])
        return ls

    ani = animation.FuncAnimation(fig, run, range(len(df)), blit=True, interval=30, repeat=False)

    ax.legend()

    if movieName is None:
        plt.show()
    else:
        mywriter = animation.FFMpegWriter(fps=fps, codec=codec, extra_args = extra_args)
        ani.save(movieName + '.mkv', writer=mywriter)


def testSlider():
    from Snoopy.TimeDomain import TEST_DIR
    df = pd.read_csv(f"{TEST_DIR:}/eta_surf.csv", index_col = 0)
    dfSlider( df )


def testSurfacePlot():
    df = pd.DataFrame(index=np.linspace(0, 0.5, 100), columns=np.linspace(0, 2*np.pi, 50), dtype="float")
    df.loc[:, :] = 1
    for i in range(len(df.columns)):
        df.iloc[:, i] = np.sin(df.columns[i]) * df.index.values
    ax = dfSurface(df, polar=True,  interpolate=True, polarConvention="geo", colorbar=True, vmin = 0.2, vmax = 0.3)
    ax = dfIsoContour(df, levels=[0.0, 0.5], ax=ax)
    plt.show()

    
def lineplot_data(data, x, y, exclude= None, hue = None, mark =None, style = None, cmap = "viridis", markers = None,
                   styles = None, legend = True, legend_loc = {"hue" : "upper left", "mark" : "upper center", "style" : "upper right"},
                   title = None, log = "", **kwargs ):
    """Mix between seaborn "scatterplot" & seaborn "lineplot" :
    Return the x / y scatterplot of data hueed according to value of hue
    Lines are drawn for each serie of y = f(..., param1, param2, (...,) paramHue )

    data : pd.DataFrame describing the evaluation of a fonction Y = f(X, param1, param2, ..., paramHue)
        on a product of tuple of coordinates
        typically, a very simple example of data cold be :
            x   param1  paramhue y
        0   0     0        0       0
        1   1     0        0       1
        2   0     0        1       1
        3   1     0        1       2
        4   0     1        0       1
        5   1     1        0       2
        6   0     1        1       2
        7   1     1        1       1
        
        For each param1 value (here 2), the function will draw y = f(x, paramhue) lines,
        and the line will be hueed according to paramhue value
        
    x : column label (often str)
      label of column used to build x axis
      
    y : column label (often str)
      label of column used to build y axis
      
    exclude : (opt) list
        list of column of the dataframe that are not supposed to be considered as parameters (f.e other outputs)
      
    hue : (opt) column label (often str)
      label of column used to define color. If None (default),
      all lines will be drawn with plt default colors 
      or with the same defined color if keyword c is used (see **kwargs)
      
    mark : (opt) column label (often str)
      label of column used to choose marker. 
      If None (default), all lines will be drawn witout mark 
      or with the same marker if keyword "mk" is used (see **kwargs) 
      
    style : (opt) column label (often str)
     label of column used to choose linestyle. 
     If None (default), all lines will be drawn solid
     or with the linstyle if keyword "ls" is used (see **kwargs) 

    cmap : (opt) str or cmap object, optional.
        color map in use for hue, default to "viridis".
        
    markers : (opt) List of markers
        markers in use for mark. Default : large set of markers from plt
        
    styles : (opt) List of linestyle
        linestyles in use for style. Default : set of linestyle from plt  

    legend : (opt) bool or str
        if True, legend is shown (shorten but still can be long !)
        if legend = "brief", min legend is displayed
        
    title : (opt) str
        title of the fig
        
    log : (opt) str
        str describing which axis as to be logged.
        Can be "x", "y", "xy" / "all" / "both"
        
    Return :
        axis with drawn lines as asked.
    """

    if isinstance( cmap, str ) : 
        cmap = matplotlib.colormaps[cmap]

    if isinstance(data.index, pd.MultiIndex):
        data  =  data.to_frame()
    for col_name in [x, y, hue, mark]:
        if (col_name!=None) and (col_name in data.columns) == False:
            raise(Exception(f"{col_name} not in data column"))
     
    if exclude != None:
        for elt in exclude:
            if (elt in data.columns) == False:
                raise(Exception(f"Can't exclude {elt} from columns"))
        data = data.drop(exclude, axis = 1)
        
    if mark !=None:
        if markers == None: 
            markers = ["o","x", "+", "v","^","<",">","1","2","3","4","8","s","p","P","*","h","H","+","x","X","D","d","|","_",0,1,2,3,4,5,6,7,8,9,10,11]
        if len(data[mark].unique()) > len(markers):
            raise(Exception("Not enough markers for all values in marker"))
    
    if style !=None:
        if styles == None: 
            styles =  ['-', '--', '-.', ':']
        if len(data[style].unique()) > len(styles):
            raise(Exception("Not enough linestyles for all values in styles"))
  

    data_tmp = data.sort_values(x) #on trie par x pour que les points soient reliés par x croissants
    
    if hue !=None: 
        list_hue_index =  data[hue].drop_duplicates() #on identifie tous les valeurs que prend la colonne hue
    if mark!=None:
        list_markers_index = data[mark].drop_duplicates() #on identifie tous les valeurs que prend la colonne mark
    if style != None:
        list_style_index = data[style].drop_duplicates()


    
    l_special_coords = []
    for elt in [x, y, hue, mark, style]:
        if elt != None:
            l_special_coords.append(elt)
    
    l_others_col = data.columns.drop(l_special_coords) #on construit la liste des clés des autres colonnes
    NbCond = len(l_others_col) #le nombre de colonne restante correspond à la valeur cible du test que l'on effectuera lors de la découpe du dataframe
    
    
    if NbCond == 0: #si il n'y a pas d'autres colonnes que x, y, hue et marker, il faut parcourir le data une unique fois sans besoin de le découper 
        tmp = data_tmp
        
    else :
        data_coords_to_eval = data[l_others_col].drop_duplicates() #on construit l'ensemble des tuples des valeurs des colonnes hors x, y, hue et marker
        
        i = data_coords_to_eval.index[0]
        coords = data_coords_to_eval.loc[i]
        idx_sel = data_tmp.index[ (((data_tmp[l_others_col] ==  coords).values.sum(axis = 1)) == NbCond) ] 
        tmp = data_tmp.loc[idx_sel]

    l_lines_style = []
    l_label_style = []
    l_lines_marker = []
    l_label_marker = []
    l_lines_hue = []
    l_label_hue = []
    
    fig, ax = plt.subplots()

    #For legend : first set of shared params
    if hue !=None:
        if mark !=None:
            if style !=None:
                for hue_index in np.sort(list_hue_index):
                    tmp_ = tmp.loc[ tmp[hue] == hue_index]
                    i_marker =0
                    for marker_index in np.sort(list_markers_index):
                        tmp__ = tmp_.loc[ tmp_[mark] == marker_index]
                        i_style = 0
                        for style_index in np.sort(list_style_index):
                            tmp___ = tmp__.loc[ tmp_[style] == style_index]
                            ax.plot( tmp___[x], tmp___[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                    marker = markers[i_marker],  linestyle= styles[i_style],
                                    label = str(hue) + " : " + str(hue_index) + ",\n " + str(mark) + " : " +str(marker_index)+ ",\n " + str(style) + " : " +str(style_index), **kwargs)
                            i_style+=1
                            
                            if (hue_index == np.sort(list_hue_index)[0]) and (i_marker == 0):
                                l_lines_style.append(ax.lines[-1])
                                l_label_style.append(str(style) + " : " +str(style_index))
                                
                        if (hue_index == np.sort(list_hue_index)[0]):
                            l_lines_marker.append(ax.lines[-1])
                            l_label_marker.append(str(mark) + " : " +str(marker_index))
                        i_marker+=1
                    l_lines_hue.append(ax.lines[-1])
                    l_label_hue.append(str(hue) + " : " +str(hue_index))
                        
            else: #hue, mark but not style
                for hue_index in np.sort(list_hue_index):
                    tmp_ = tmp.loc[ tmp[hue] == hue_index]
                    i_marker =0
                    for marker_index in np.sort(list_markers_index):
                        tmp__ = tmp_.loc[ tmp_[mark] == marker_index]
                        ax.plot( tmp__[x], tmp__[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                marker =markers[i_marker],
                                label = str(hue) + " : " + str(hue_index) + ",\n " + str(mark) + " : " +str(marker_index), **kwargs)  
                                                
                        if (hue_index == np.sort(list_hue_index)[0]):
                            l_lines_marker.append(ax.lines[-1])
                            l_label_marker.append(str(mark) + " : " +str(marker_index))
                        i_marker+=1
                    l_lines_hue.append(ax.lines[-1])
                    l_label_hue.append(str(hue) + " : " +str(hue_index))
                    
        else: #hue, not mark
            if style !=None:
                for hue_index in np.sort(list_hue_index):
                    tmp_ = tmp.loc[ tmp[hue] == hue_index]
                    i_style = 0
                    for style_index in np.sort(list_style_index):
                        tmp__ = tmp_.loc[ tmp_[style] == style_index]
                        ax.plot( tmp__[x], tmp__[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                linestyle= styles[i_style],
                                label = str(hue) + " : " + str(hue_index) + ",\n " + str(style) + " : " +str(style_index), **kwargs)
                        
                        if (hue_index == np.sort(list_hue_index)[0]) :
                            l_lines_style.append(ax.lines[-1])
                            l_label_style.append(str(style) + " : " +str(style_index))                                
                        i_style+=1
                    l_lines_hue.append(ax.lines[-1])
                    l_label_hue.append(str(hue) + " : " +str(hue_index))
                        
            else: #hue, not mark, not style
                for hue_index in np.sort(list_hue_index):
                    tmp_ = tmp.loc[ tmp[hue] == hue_index]
                    ax.plot( tmp_[x], tmp_[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                label = str(hue) + " : " + str(hue_index) + ",\n ", **kwargs)
                    l_lines_hue.append(ax.lines[-1])
                    l_label_hue.append(str(hue) + " : " +str(hue_index))
    else : #not hue
        if mark !=None:
            if style !=None:
                i_marker =0
                for marker_index in np.sort(list_markers_index):
                    tmp_ = tmp.loc[ tmp[mark] == marker_index]
                    i_style = 0
                    for style_index in np.sort(list_style_index):
                        tmp__ = tmp_.loc[ tmp_[style] == style_index]
                        ax.plot( tmp__[x], tmp__[y], 
                                marker =markers[i_marker],  linestyle= styles[i_style],
                                label = str(mark) + " : " +str(marker_index)+ ",\n " + str(style) + " : " +str(style_index), **kwargs)
                        if (i_marker == 0):
                            l_lines_style.append(ax.lines[-1])
                            l_label_style.append(str(style) + " : " +str(style_index))
                        i_style+=1

                    l_lines_marker.append(ax.lines[-1])
                    l_label_marker.append(str(mark) + " : " +str(marker_index)) 
                    i_marker+=1
                    
            else: #not hue, mark, not style
                i_marker =0
                for marker_index in np.sort(list_markers_index):
                    tmp_ = tmp.loc[ tmp[mark] == marker_index]
                    ax.plot( tmp_[x], tmp_[y], 
                            marker =markers[i_marker],
                            label = str(mark) + " : " +str(marker_index), **kwargs)
                    l_lines_marker.append(ax.lines[-1])
                    l_label_marker.append(str(mark) + " : " +str(marker_index)) 
                    i_marker+=1
        else: #not hue not mark
            if style !=None:
                tmp_ = tmp.loc[ tmp[hue] == hue_index]
                i_style = 0
                for style_index in np.sort(list_style_index):
                    tmp__ = tmp_.loc[ tmp_[style] == style_index]
                    ax.plot( tmp__[x], tmp__[y], 
                            linestyle= styles[i_style],
                            label = str(style) + " : " +str(style_index), **kwargs)
                    l_lines_style.append(ax.lines[-1])
                    l_label_style.append(str(style) + " : " +str(style_index))
                    i_style+=1
            else:
                tmp_ = tmp
                ax.plot( tmp_[x], tmp_[y], **kwargs)
    if legend == True:
        ax.legend()
    
    if legend == "brief":
        if hue !=None:
            leg = Legend( ax, l_lines_hue, l_label_hue, frameon = False, framealpha = 0.3, loc = legend_loc["hue"])
            ax.add_artist(leg)
        if mark !=None:
            leg = Legend( ax, l_lines_marker, l_label_marker, frameon = False, framealpha = 0.3, loc = legend_loc["mark"])
            ax.add_artist(leg)
        if style !=None:
            leg = Legend( ax, l_lines_style, l_label_style, frameon = False, framealpha = 0.3, loc = legend_loc["style"])
            ax.add_artist(leg)
                    
    if NbCond > 0: #si il y a d'autres colonnes, on trouve les combi. de tuples de paramètres "autres", et on itère dessus
        for i in data_coords_to_eval.index[1:]:
            coords = data_coords_to_eval.loc[i]
            NbCond = len(l_others_col)
            idx_sel = data_tmp.index[ (((data_tmp[l_others_col] ==  coords).values.sum(axis = 1)) == NbCond) ] 
            tmp = data_tmp.loc[idx_sel]  
        
                    
            #For legend : first set of shared params
            if hue !=None:
                if mark !=None:
                    if style !=None:
                        for hue_index in np.sort(list_hue_index):
                            tmp_ = tmp.loc[ tmp[hue] == hue_index]
                            i_marker =0
                            for marker_index in np.sort(list_markers_index):
                                tmp__ = tmp_.loc[ tmp_[mark] == marker_index]
                                i_style = 0
                                for style_index in np.sort(list_style_index):
                                    tmp___ = tmp__.loc[ tmp_[style] == style_index]
                                    ax.plot( tmp___[x], tmp___[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                            marker =markers[i_marker],  linestyle= styles[i_style],
                                            label = str(hue) + " : " + str(hue_index) + ",\n " + str(mark) + " : " +str(marker_index)+ ",\n " + str(style) + " : " +str(style_index), **kwargs)
                                    i_style+=1
                                i_marker+=1
                    else:
                        for hue_index in np.sort(list_hue_index):
                            tmp_ = tmp.loc[ tmp[hue] == hue_index]
                            i_marker =0
                            for marker_index in np.sort(list_markers_index):
                                tmp__ = tmp_.loc[ tmp_[mark] == marker_index]
                                ax.plot( tmp__[x], tmp__[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                        marker =markers[i_marker],
                                        label = str(hue) + " : " + str(hue_index) + ",\n " + str(mark) + " : " +str(marker_index), **kwargs)
                                i_marker+=1
                else:
                    if style !=None:
                        for hue_index in np.sort(list_hue_index):
                            tmp_ = tmp.loc[ tmp[hue] == hue_index]
                            i_style = 0
                            for style_index in np.sort(list_style_index):
                                tmp__ = tmp_.loc[ tmp_[style] == style_index]
                                ax.plot( tmp__[x], tmp__[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                        linestyle= styles[i_style],
                                        label = str(hue) + " : " + str(hue_index) + ",\n " + str(style) + " : " +str(style_index), **kwargs)
                                i_style+=1
                    else:
                        for hue_index in np.sort(list_hue_index):
                            tmp_ = tmp.loc[ tmp[hue] == hue_index]
                            ax.plot( tmp_[x], tmp_[y], color = cmap(  np.abs(hue_index) /  np.abs((list_hue_index)).max()    ) ,
                                        label = str(hue) + " : " + str(hue_index) + ",\n ", **kwargs)
            else :
                if mark !=None:
                    if style !=None:
                        i_marker =0
                        for marker_index in np.sort(list_markers_index):
                            tmp_ = tmp.loc[ tmp[mark] == marker_index]
                            i_style = 0
                            for style_index in np.sort(list_style_index):
                                tmp__ = tmp_.loc[ tmp_[style] == style_index]
                                ax.plot( tmp__[x], tmp__[y], 
                                        marker =markers[i_marker],  linestyle= styles[i_style],
                                        label = str(mark) + " : " +str(marker_index)+ ",\n " + str(style) + " : " +str(style_index), **kwargs)
                                i_style+=1
                            i_marker+=1
                    else:
                        i_marker =0
                        for marker_index in np.sort(list_markers_index):
                            tmp_ = tmp.loc[ tmp[mark] == marker_index]
                            ax.plot( tmp_[x], tmp_[y], 
                                    marker =markers[i_marker],
                                    label = str(mark) + " : " +str(marker_index), **kwargs)
                            i_marker+=1
                else:
                    if style !=None:
                        tmp_ = tmp.loc[ tmp[hue] == hue_index]
                        i_style = 0
                        for style_index in np.sort(list_style_index):
                            tmp__ = tmp_.loc[ tmp_[style] == style_index]
                            ax.plot( tmp__[x], tmp__[y], 
                                    linestyle= styles[i_style],
                                    label = str(style) + " : " +str(style_index), **kwargs)
                            i_style+=1
                    else:
                        tmp_ = tmp
                        ax.plot( tmp_[x], tmp_[y], **kwargs)
    if title != None:
        fig.suptitle(title)
    
    if "x" in log :
        ax.set_xscale("log")
    if "y" in log :
        ax.set_yscale("log")
    if (log == "both") or (log == "all") :
        ax.set_xscale("log")
        ax.set_yscale("log")
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return(ax)
    

if __name__ == "__main__":

    print("Test")
    testSurfacePlot()
    testSlider()
