
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
import numpy as np




def newXaxis( ax, fun = None, tick_in_original_scale = None, inv_fun = None, tick_in_new_scale = None, format = None) :
    """Return a second axis, function of the first
    """

    ax2 = ax.twiny()
    ax2.set_xlim( ax.get_xlim() )
    ax2.grid(False)

    if tick_in_original_scale is not None :
        ax2.set_xticks(tick_in_original_scale)
        ax2.set_xticklabels( fun( np.array(tick_in_original_scale)) )

    elif tick_in_new_scale is not None :
        ax2.set_xticks( inv_fun(tick_in_new_scale) )
        ax2.set_xticklabels( tick_in_new_scale )



    elif inv_fun is None :
        #Automatic new xticks
        tick_in_original_scale = ticker.MaxNLocator(nbins=8, steps=[1,2,5]).tick_values(*ax.get_xlim())
        ax2.set_xticks(tick_in_original_scale)
        ax2.set_xticklabels( fun(tick_in_original_scale) )

    else :
        right_ax_limits = sorted([ fun(lim) for lim in ax.get_xlim()])

        tick_in_new_scale = ticker.MaxNLocator(nbins=8, steps=[1,2,5]).tick_values(*right_ax_limits)[3:]

        print (tick_in_new_scale)
        print (inv_fun(tick_in_new_scale))
        tick_in_new_scale = np.array([0.25, 1.0 , 2.0])

        ax2.set_xticks( inv_fun(tick_in_new_scale))
        ax2.set_xticklabels( tick_in_new_scale )

    if format is not None :
        ax2.xaxis.set_major_formatter(ticker.FormatStrFormatter(format))
        pass



    return ax2



if __name__ == "__main__" :



    x = np.array([ 0.707, 1. ,2 ,3 ])

    def f(x) :
        return 1/x**2

    def inv(x) :
        return 1/x**0.5

    fig, ax = plt.subplots()
    ax.plot( x , x , "o" )
    ax2 = newXaxis(ax , fun = f , tick_in_original_scale = [0.5, 1.,  1.5, 2.,  2.5, 3.,  3.5], format = "%.2f" )
