"""
scatter plot colored by density (kde)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize
from scipy.interpolate import interpn
from scipy.stats import linregress



def density_pairplot( data, diag_kws = {}, grid_kws = {}, **kwargs ):
    """Similar to sns.pairplot, but scatter plot are density colored

    Parameters
    ----------
    data : pd.Dataframe
        The data
    diag_kws : dict, optional
        Keywords passed to kdeplot. The default is {"fill" : True}..
    grid_kws : dict, optional
        Keywords passed to PairGrid. The default is {}.
    **kwargs : any
        Keywords argument passed to density_scatter

    Returns
    -------
    sns.PairGrid
        The plot
        
    Example
    -------
    >>> density_pairplot( data )
    """
    import seaborn as sns
    grid_kws.setdefault("diag_sharey", False)
    grid_kws.setdefault("aspect", 1)

    diag_kws.setdefault("fill", True)
    pairplot = sns.PairGrid( data, **grid_kws )
    col = data.columns
    nvar = len(col)
    axes = pairplot.axes
    for i in range(nvar):
        for j in range(i+1 , nvar):
            x = data.loc[ : , col[j ]].values
            y = data.loc[ : , col[i] ].values
            density_scatter( x = x,  y = y, ax=axes[i,j], **kwargs)
            density_scatter( x = y,  y = x, ax=axes[j,i], **kwargs)
            
    pairplot.map_diag( sns.distributions.kdeplot, **diag_kws )

    # Enforce aspect ratio to be 1.0
    pairplot.fig.set_figwidth( pairplot.fig.get_figheight() )
    return pairplot


def scatterPlot(df , x, y , ax = None, x_y = False , title = None, meanCov = None, **kwargs) :
    """
    Scatter plot, with additional option compared to pandas.plot(kind="scatter")
    """

    if ax is None :
        fig ,ax = plt.subplots()

    df.plot(ax=ax,x=x, y=y, kind = "scatter", **kwargs)

    _x = df.loc[:,x]
    _y = df.loc[:,y]

    displayMeanCov( x,y,meanCov,ax)

    if x_y is True :
        add_x_y(_x,_y,ax)

    return ax


def density_scatter( x , y, ax = None, sort = True, density_kwargs = {"bins" : 20}, scale = None, interpolation = "linear",
                    x_y = False, cbar = False, range = None, method = "auto", **kwargs ):
    """Scatter plot colored by density (2d histogram or kde).

    Parameters
    ----------
    x : np.ndarray
        X data
    y : np.ndarray
        Y data
    ax : matplotlib.axes, optional
        Where to plot the figure. The default is None.
    sort : TYPE, optional
        DESCRIPTION. The default is True.
    bins : TYPE, optional
        DESCRIPTION. The default is 20.
    scale : function, optional
        Color map scale. The default is None.
    interpolation : "linear" or "nearest" or "splinef2d", optional
        How to interpolate colors in the 2D histogram. The default is "linear".
    x_y : bool, optional
        If True x=y line is plotted. The default is False.
    cbar : bool, optional
        Color bar. The default is False.
    method : str, optional
        How to calculate the density, among ["kde", "hist", "auto"]. "kde" is too slow with high number of pointsn "auto" set "kde" when n < 100 and "hist" otherwise. Default to "auto".
    **kwargs : **
        optional arguments passed to plt.scatter()

    Returns
    -------
    ax : matplotlib.axes
        ax
    """

    if ax is None :
        fig , ax = plt.subplots()

    if method == "auto":
        if len(x) < 5000:
            method = "kde"
        else : # kde too slow for large number of points.
            method = "host"

    # Calculate the point density
    if "kde" in method :
        if "learn" in method:
            # With sklearn
            from sklearn.neighbors import KernelDensity
            xy = np.vstack([x,y]).T
            a = KernelDensity(**density_kwargs).fit(X = xy)
            z = a.score_samples( xy )
        else: 
            from scipy.stats import gaussian_kde
            xy = np.vstack([x,y])
            z = gaussian_kde( xy , **density_kwargs)(xy)
    else : 
        data , x_e, y_e = np.histogram2d( x, y, density = True, **density_kwargs)
        z = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T ,
                    method = interpolation, bounds_error = False)

        edges_id = np.isnan(z)
        z[ edges_id ] = interpn( ( 0.5*(x_e[1:] + x_e[:-1]) , 0.5*(y_e[1:]+y_e[:-1]) ) , data , np.vstack([x,y]).T[edges_id] ,
                                method = "nearest", bounds_error = False, fill_value = None)


    if scale is not None :
        z = scale(z)

    # Sort the points by density, so that the densest points are plotted last
    if sort :
        idx = z.argsort()
        x, y, z = x[idx], y[idx], z[idx]

    if x_y :
        add_x_y( x, y,  ax )

    ax.scatter( x, y, c=z, edgecolor = None, **kwargs )

    #Add color baz :
    if cbar :
        norm = Normalize(vmin = np.min(z), vmax = np.max(z))
        cbar = ax.get_figure().colorbar(cm.ScalarMappable(norm = norm), ax=ax)
        cbar.ax.set_ylabel('Density')

    if hasattr( x , "name" ) :
        ax.set_xlabel(x.name)
    if hasattr( y , "name" ) :
        ax.set_ylabel(y.name)

    return ax


def add_x_y( x,y, ax, **kwargs ) :
    minMax = [min(x.min(),y.min()),max(x.max(),y.max())]
    ax.plot(minMax , minMax , **kwargs)


def add_linregress( x, y, ax, text = True, engine = "scipy", intercept = True, lims = None, loc = 'best', **kwargs ):

    if lims is not None:
        minMax = np.array(lims)
    else:    
        minMax = np.array( [ min(x), max(x) ] )

    if engine == "scipy":
        lreg = linregress(x, y)
        label = f"y = {lreg.slope:.2f} x {lreg.intercept:+.2f} ; R2 = {lreg.rvalue**2:.2f} "
        ax.plot( minMax , lreg.slope * minMax  + lreg.intercept, label = label, **kwargs )
        ax.legend()
    elif engine == "statsmodels":
        import statsmodels.api as sm
        if intercept:
            xData = sm.add_constant(x)  # Adds a constant term to the predicton
            smLM = sm.OLS(y,xData).fit() # linear regression model fit
            label = f"y = {smLM.params[1]:.2f} x {smLM.params[0]:+.2f} ; R2 = {smLM.rsquared:.2f} "
            ax.plot( minMax , smLM.params[1] * minMax  + smLM.params[0], label = label, **kwargs )
        else:
            smLM = sm.OLS(y,x).fit() # linear regression model fit
            label = f"y = {smLM.params[0]:.2f} x ; R2 = {smLM.rsquared:.2f} "
            ax.plot( minMax , smLM.params[0] * minMax, label = label, **kwargs )

        ax.legend(loc = loc)

    return ax

def displayMeanCov(x,y, meanCov,ax):
    if meanCov is not None :
        if meanCov is True:
            mean = np.mean((y / x))
            cov = np.std((y / x)) / mean
            mean -= 1.
            ax.text( 0.8 , 0.2 ,  "mean : {:.1%}\nCOV : {:.1%}".format(mean , cov) , transform=ax.transAxes ) # verticalalignment='center'

        elif meanCov == "abs_mean_std" :
            mean = np.mean((y - x))
            std = np.std((y - x))
            ax.text( 0.8 , 0.2 ,  "mean : {:.2f}\nSTD : {:.2f}".format(mean , std) , transform=ax.transAxes ) # verticalalignment='center'


if "__main__" == __name__ :

    x = np.random.normal(size=10000)
    y = x * 3 + np.random.normal(size=10000)
    ax = density_scatter( x, y, bins = [30,30] )

    add_linregress(x,y,ax=ax)






