import numpy as np
import pandas as pd
from Snoopy import logger
from matplotlib import pyplot as plt
from matplotlib.cm import ScalarMappable
import matplotlib

def standardLon(longitude):
    """Transform longitude (in degree) to standard range [-180.,180.]

    Parameters
    ----------
    longitude : float or array-like
        Longitude.

    Returns
    -------
    longitude : float or array-like
        Trnasformed longitude.

    """
    if hasattr(longitude,'__len__'):
        longitude = [l%360. for l in longitude]
        longitude = np.array([l - 360. if l>180. else l for l in longitude])
    else:
        longitude = longitude%360.
        if longitude>180.0: longitude -= 360.
    return longitude

def drawMap(ax=None, projection=None, central_longitude=0.0, lcolor='grey', scolor=None, background_img = False):
    """Draw the background maps.

    Parameters
    ----------
    ax : mpl.Axes, optional
        Where to plot. The default is None.
    projection : cartopy Projection, optional
        Projection. The default is cartopy.PlateCarree.
    central_longitude : float, optional
        Central longitude (to center the drawing). The default is 0.0.
    lcolor : str, optional
        Color for land. The default is 'grey'.
    scolor : str, optional
        Color for ocean. The default is None.

    Returns
    -------
    ax : TYPE
        DESCRIPTION.
    """
    from cartopy import crs as ccrs, feature
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

    if projection is None:
        projection = ccrs.PlateCarree(central_longitude=central_longitude)
        
    if ax is None: 
        fig, ax = plt.subplots( figsize = [12,6],  subplot_kw={'projection':projection })
        
    if background_img : 
        ax.stock_img()

    ax.coastlines()
    ax.add_feature(feature.LAND, facecolor=lcolor)

    if scolor is not None:
        ax.add_feature(feature.OCEAN, facecolor=scolor)

    try :
        ax.set_xticks( np.arange(-180, 210 , 30), crs=ccrs.PlateCarree())
        ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
    except :
        logger.debug("No ticks for non-rectangular coordinate system")
    ax.xaxis.set_major_formatter(LongitudeFormatter(zero_direction_label=True))
    ax.yaxis.set_major_formatter(LatitudeFormatter())

    return ax

def drawRoute(pathPoint, var=None, text_label = None,  ax=None,
              zoom = "full" , markersize = 5, cbar = False,  linestyle = "",
              cmap = "cividis", marker = "o", map_kwargs = {},
              **kwargs):
    """Draw route on earth map.

    Parameters
    ----------
    pathPoint : List, array of pd.DataFrame
        Path point to plotted.
        If dataFrame, should have "lat" and "lon" columns

    var : str, optional
        Columns to use to color path point. The default is None.
    label : TYPE, optional
        DESCRIPTION. The default is None.
    ax : matplotlib "axe", optional
        Where to plot. The default is None.
    central_longitude : float, optional
        central_longitude. The default is 0.0.
    zoom : str, optional
        DESCRIPTION. The default is "full".
    markersize : float, optional
        Marker size. The default is 5.
    lcolor : str, optional
        Color of land areas. The default is "grey".
    scolor : str, optional
        Color of sea/ocean areas. The default is None.
    cbar : bool, optional
        Add colorbar. The default is False.
    cmap : str, optional
        Color map (when variable are colored). The default is "cividis".
    marker : bool, optional
        use a ship shaped marker rotated to indicate ship heading. The default is "False".
        Only works when pathPoint is a pd.DataFrame that contains a "Dir" column.
        
    map_kwargs : dict, optional
        Argument passed to drawMap()
    **kwargs : Any
        Keyword arguments passed to .plot().

    Returns
    -------
    ax :
        The matplotlib Axis
    """
    from cartopy import crs as ccrs
    if linestyle :
        data_crs = ccrs.Geodetic()
    else :
        data_crs = ccrs.PlateCarree()
    
    if ax is None:
        ax = drawMap( **map_kwargs )

    if type(pathPoint) == list:  # List of [long, lat] tuple
        for iPoint in range(len(pathPoint)):
            lat, long = pathPoint[iPoint]
            ax.plot(long , lat,  "bo", markersize = markersize, transform = data_crs, **kwargs)

    elif type(pathPoint) == pd.DataFrame:
        pathPoint = pathPoint.copy()
        pathPoint.rename(columns=lambda x: x.lower() if x.lower() in ['lat','lon', 'dir'] else x, inplace=True)
        if var is not None:
            # Draw route colored by field value
            if marker == "ship_shape" :
                vmin = kwargs.pop("vmin", np.min(pathPoint.loc[:,var]))
                vmax = kwargs.pop("vmax", np.max(pathPoint.loc[:,var]))
                from Snoopy import PyplotTools as dplt
                c = dplt.getColorMappable( vmin, vmax, cmap = cmap )
                for _, row in pathPoint.iterrows():
                    angle_matplotlib = 360-row.loc['dir']+90
                    mrk, scale = create_ship_marker(angle_matplotlib)
                    ax.plot(row.lon, row.lat, marker = mrk, color=c.to_rgba(row.loc[var]), markersize=markersize*scale, markeredgecolor = 'k', transform = data_crs, **kwargs)
            else:
                c = ax.scatter(pathPoint["lon"], pathPoint["lat"],  s = markersize , c = pathPoint.loc[:,var], cmap=cmap, marker = marker, transform = data_crs, **kwargs)
                
            if cbar:
                cbar_ = ax.get_figure().colorbar( mappable = c, ax=ax , orientation='vertical',fraction=0.046, pad=0.04 )
                cbar_.set_label(var, rotation=90)

        else:
            if marker == "ship_shape" :
                for _, row in pathPoint.iterrows():
                    angle_matplotlib = 360-row.loc['dir']+90
                    mrk, scale = create_ship_marker(angle_matplotlib)
                    ax.plot(row.lon, row.lat, c = 'b', marker = mrk, markersize=markersize*scale, markeredgecolor = 'k', transform = data_crs, **kwargs)
            else:
                ax.plot(pathPoint["lon"], pathPoint["lat"], linestyle = linestyle, markersize = markersize, marker = marker, transform = data_crs, **kwargs)

        if text_label is not None :
            for _, row in pathPoint.iterrows():
                ax.text(row.lon - 3, row.lat - 3, row.loc[text_label],  horizontalalignment='right',  transform=data_crs, bbox=dict(boxstyle="square", fc="w"))

    else:  # Array
        ax.plot(pathPoint[:, 1], pathPoint[:, 0], linestyle = linestyle, markersize = markersize, transform = data_crs, **kwargs)

    set_map_zoom(ax, zoom, pathPoint)

    return ax

def animRoute(pathPoint, var=None, ax=None, central_longitude=0.0, zoom = "full" , markersize = 15, mcolor='b', lcolor='grey', scolor=None, every=1, verbose=0):
    """Animate route on earth map.

    Parameters
    ----------
    pathPoint : pd.DataFrame
        Path point to plotted.
        Mandatory columns : "lat", "lon" and "Dir".
        Optional columns : "time" and var.
    var : str, optional
        Columns to use to color path point. The default is None.
    ax : matplotlib "axe", optional
        Where to plot. The default is None.
    central_longitude : float, optional
        central_longitude. The default is 0.0.
    zoom : str, optional
        DESCRIPTION. The default is "full".
    markersize : float, optional
        Marker size. The default is 5.
    mcolor : str, optional
        Marker color. The default is 'b'.
    lcolor : str, optional
        Color of land areas. The default is "grey".
    scolor : str, optional
        Color of sea/ocean areas. The default is None.
    every : int, optional
        Integer defining animation output rate. The default is 1.
    verbose : int, optional
        Print progressbar is >0. The default is 0.

    Returns
    -------
    anim :
        The "animation". Animation can then be saved with the following command :
        anim.save(path, writer=writer)

    """
    import matplotlib.animation as animation

    pathPoint.rename(columns=lambda x: x.lower() if x.lower() in ['lat','lon', 'dir'] else x, inplace=True)

    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=20, metadata=dict(artist='Me'), bitrate=1800)

    ax = drawMap(central_longitude=central_longitude,lcolor=lcolor, scolor=scolor)

    set_map_zoom(ax, zoom, pathPoint)

    point = ax.plot(0, 0, color=mcolor, markersize=markersize)[0]
    if var is not None:
        cmap = matplotlib.colormaps['viridis']
        vmin = mt.floor(pathPoint.loc[:,var].min())
        vmax = mt.ceil(pathPoint.loc[:,var].max())
        # norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        line = ax.scatter(0, 0, color=mcolor, marker=',', s=10,cmap='viridis',vmin=vmin,vmax=vmax)
    else:
        # line = m.plot(0, 0, color='b', ls=':', lw=5)[0]
        line = ax.scatter(0, 0, color=mcolor, marker='.', s=5)

    if verbose>0:
        from tqdm import tqdm
        pbar = tqdm(np.arange(int(pathPoint.shape[0]/every)))

    def init():
        point.set_data([], [])
        return point, line

    def animate(i):
        if verbose>0: pbar.update()
        j = i*every
        lat = pathPoint.loc[j,'lat']
        lon = pathPoint.loc[j,'lon']
        point.set_data(lon, lat)

        angle_matplotlib = 360-pathPoint.loc[j,'dir']+90
        mrk, scale = create_ship_marker(angle_matplotlib)
        point.set_marker(mrk)

        # angle = 360.-pathPoint.loc[j,'dir']
        # point.set_marker((3, 0, angle))

        lat_s = pathPoint.loc[:j,'lat'][::every*2]
        lon_s = pathPoint.loc[:j,'lon'][::every*2]
        if var is not None:
            var_s = pathPoint.loc[:j,var][::every*2]
            line.set_offsets(np.array([lon_s,lat_s]).T)
            line.set_array(var_s.values)
        else:
            # line.set_data(lon_s,lat_s)
            line.set_offsets(np.array([lon_s,lat_s]).T)

        if "time" in pathPoint.columns: plt.title(pathPoint.time[j])
        else: plt.title(pathPoint.index[j])

        return point, line

    anim = animation.FuncAnimation(ax.get_figure(), animate, frames=int(pathPoint.shape[0]/every), init_func=init, repeat=True, blit=True)

    return anim, writer

def mapPlot(  dfMap , ax=None, isoLevel = None, vmin=None , vmax=None, levels = 200, cmap = "cividis", color_bar = False, map_kwargs = {}, **kwargs) :
    """
    Plot scalar field map. (same as mapPlot, but based on Cartopy)

    dfMap.index  => longitude
    dfMap.columns => latitude
    dfMap.data => scalar to plot
    """
    
    from cartopy import crs as ccrs
    data_crs = ccrs.PlateCarree(central_longitude=0.0)

    if ax is None:
        ax = drawMap(**map_kwargs)

    if vmin is None : 
        vmin = np.min( dfMap.values[  (~np.isnan(dfMap.values)) ] )
    if vmax is None : 
        vmax = np.max( dfMap.values[  (~np.isnan(dfMap.values)) ] )


    cf = ax.contourf(dfMap.index.values, dfMap.columns.values, np.transpose(dfMap.values), cmap = cmap, vmin=vmin, vmax=vmax, transform = data_crs, levels=levels, **kwargs )

    if color_bar :
        if vmin is not None and vmax is not None : extend = "both"
        elif vmin is None : extend = "max"
        else : extend = "min"
        cbar = plt.colorbar( ScalarMappable(norm=cf.norm, cmap=cf.cmap), extend = extend, cax = None, ax = ax)
        if isinstance(color_bar , str) :
            cbar.set_label( color_bar )

    return ax


def animate_geo_data( da, basename  = "picture", every = 1 , movie_kwargs = None, **kwargs ) :
    """Make videos/picture of geographic field.

    Parameters
    ----------
    da : xarray.DataArray
        Data
    basename : str, optional
        Ouptut file(s) basename. The default is "picture".
    every : int, optional
        Skip some data. The default is 1.
    movie_kwargs : None or dict, optional
        If None, pictures are generated, otherwise, the dict is passed to dplt.pictures_2_movie. The default is None.
    **kwargs : Any
        Arguments passed to dplt.mapPlot

    Returns
    -------
    None.

    Example
    -------
    >>> dplt.animate_geo_data( da, every = 3 , basename = "hs_world", vmin = 2.0, vmax = 9.0 , cmap = "cividis", movie_kwargs = {} )
    """

    from tqdm import tqdm
    from Snoopy import PyplotTools as dplt
    fList = []
    for itime, time in tqdm(list(enumerate(da.time.values[::every]))) :
        ax = mapPlot( da[itime,:,:].to_dataframe().loc[:,"hs"].unstack().transpose(), **kwargs )
        ax.set( title = time  )
        fig = ax.get_figure()
        fname =  f"{basename:}_{itime:03}.png"
        fList.append( fname )
        fig.savefig( fname  )
        plt.close(fig)

    if movie_kwargs is not None :
        movie_kwargs_ = { "fps" : 25 , "cleanPictures" : True }
        movie_kwargs_.update(movie_kwargs)
        dplt.pictures_2_movie(pictures = fList, output = basename,  ffmpeg_path = "ffmpeg", engine = "cv2", **movie_kwargs_ )




def drawGws( zoneList, ax=None, src='GWS', central_longitude=0.0, textLabel=True,
             edgecolor="black", facecolor = None,
             proj = None, fill = False, linestyle = "-", textSize = 8,
             map_kwargs = {},
            **kwargs ):
    """Draw Global Wave Statistics areas on map. Text and colors in each zone can be customized.

    Parameters
    ----------
    zoneList : str or list of str
        List of area names to plot. If "all", all areas are plot.
    ax : axis, optional
        axis. The default is None.
    src : str, optional
        Name of tab in Excel zones definition file. The default is 'GWS'.
    central_longitude : TYPE, optional
        Central longitude. The default is 0.0.
    textLabel : bool or list, optional
        Option to plot area names. If True, the zone name is used. Alternatively, a list of string can be given. The default is True.
    fill : bool, optional
        Option to fill zones. The default is True.
    edgecolor : str or list, optional
        Color of area contours. The default is None.
    facecolor : str or list, optional
        Color of filled area. The default is None.
    linestyle : str or list, optional
        linestyle for aera edges. The default is None.
    map_kwargs : dict, optional, default is {}.
        Argument passed to drawMap.
    """
    
    from Pluto.ScatterDiagram.coefsTable import gwsZone, gwsCentralPoints
    import matplotlib.patches as mpatches
    from cartopy import crs as ccrs
    data_crs = ccrs.PlateCarree(central_longitude=0.0)

    if type(zoneList) == str:
        if zoneList.lower() == 'all':
            zoneList = list(gwsZone[src].keys())
        else:
            zoneList = list( zoneList )

    if isinstance(edgecolor , str) or edgecolor is None :
        edgecolor = [edgecolor for z in zoneList]
    if isinstance(facecolor , str) or facecolor is None :
        facecolor = [facecolor for z in zoneList]
    if isinstance(linestyle , str) or linestyle is None :
        linestyle = [linestyle for z in zoneList]


    if ax is None:
        from Snoopy.PyplotTools import drawMap
        ax = drawMap( **map_kwargs  )

    for i, zone in enumerate(zoneList) :
        poly = mpatches.Polygon( [( v , u) for u,v in gwsZone[src][zone]], closed=True,
                                 edgecolor=edgecolor[i], fill=fill, lw=1, facecolor=facecolor[i], linestyle=linestyle[i],
                                 transform=data_crs, **kwargs )
        ax.add_patch(poly)
        if textLabel :
            if zone in gwsCentralPoints[src].keys() :
                lat , lon = gwsCentralPoints[src][zone]
            else :
                tab = np.array( gwsZone[src][zone] + [gwsZone[src][zone][0]] )
                lat, lon = tab[ :, 0 ].mean() ,tab[ :, 1 ].mean()
            if hasattr(textLabel , "__len__") : 
                text = textLabel[i]
            else : 
                text = zone
            ax.text( lon , lat , text, horizontalalignment='right', transform = data_crs, c = edgecolor[i], fontdict = {"size":textSize} )
    return ax

def create_ship_marker(rotation, shape = None):
    """Create a custom marker in the form of a ship that can be used with matplotlib.

    Adapted from here: https://stackoverflow.com/questions/23345565/is-it-possible-to-control-matplotlib-marker-orientation

    Parameters
    ----------
    rotation : float
        rotation angle in degrees.
        In matplotlib:
            0° is positive x, 90° is positive Y
            Counterclockwise is positive rotation
    rotation : array
        vertices of poligon to construct shape. The default is "None".
        If "None" a generic ship-shaped marker is created

    Returns
    -------
    marker : Path
        The marker to be used instead of conventional matplotlib markers.
    scale : float
        It seems that Path object are autoscaled by matplotlib plot/scatter functions.
        Multiply markersize with this value to get same size marker independent of rotation.
        for plt.plot: markersize = (markersize*scale)
        for plt.scatter: s = (markersize*scale)**2

    """
    from matplotlib.path import Path

    if shape is None:
        shape = np.array([
                        [-0.5, -0.5],  # origin at Aft SB in view from Top
                        [1.5, -0.5],  # Fore SB
                        [2.5, 0.], # Bow point
                        [1.5, 0.5],  # Fore PS
                        [-0.5, 0.5],  # Aft PS
                        [-0.5, -0.5]]  # back to Aft SB
                        )
    # rotate
    angle = rotation / 180 * np.pi
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    shape = np.matmul(shape, rot_mat)

    # scale
    x0 = np.amin(shape[:, 0])
    x1 = np.amax(shape[:, 0])
    y0 = np.amin(shape[:, 1])
    y1 = np.amax(shape[:, 1])
    scale = np.amax(np.abs([x0, x1, y0, y1]))

    marker = Path(shape)
    return marker, scale

def set_map_zoom(ax, zoom = "full", pathPoint = None):
    """Set zoom of an axis object.

    Parameters
    ----------
    ax : matplotlib axes
        Ax for which to set limits.
    zoom : str, optional
        Choose zoom type. Possible values are {'full', 'atlantic', 'extreme', 'moderate'}. The default is "full".
    pathPoint : pd.DataFrame, optional
        Pandas dataframe containing 'lat' & 'lon' columns needed to choose zoom scale. The default is None.

    Returns
    -------
    None.
    """
    from cartopy import crs as ccrs
    
    if zoom.lower() == "full" :
        ax.set_global()
        if isinstance(ax.projection, ccrs.PlateCarree):
            ax.set_xlim((-180., 180.))
            ax.set_ylim((-90.,  90.))
        return
        
    if not isinstance(ax.projection, ccrs.PlateCarree):
        return
    
    if zoom.lower() in ["atlantic"] :
        ax.set_xlim( [-85, 0] )
        ax.set_ylim( [-20, 60] )
    elif zoom.lower() in ["na", "northatlantic", "north-atlantic"] :
        ax.set_xlim( [-80, 5] )
        ax.set_ylim( [ 20, 70] )
    elif zoom.lower() == "extreme":
        dlon = pathPoint.lon.max()-pathPoint.lon.min()
        dlat = pathPoint.lat.max()-pathPoint.lat.min()
        ax.set_xlim((pathPoint.lon.min()-0.1*dlon, pathPoint.lon.max()+0.1*dlon))
        ax.set_ylim((pathPoint.lat.min()-0.1*dlat, pathPoint.lat.max()+0.1*dlat))
    else:
        raise(Exception(f"{zoom:} not reckognized"))
        
        
if __name__ == "__main__":
    
    from cartopy import crs as ccrs
    path = pd.DataFrame( {"lat" : np.linspace(1,50, 20) , "lon" : np.linspace(150,220, 20)} )
    drawRoute( path, map_kwargs= { "background_img" : True, "projection" : ccrs.PlateCarree()} , alpha = 0.5, linestyle = "-" )

