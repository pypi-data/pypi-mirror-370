import numpy as np
from matplotlib import pyplot as plt


def se_std( std, n):
    """Standard error of standard deviation

    Parameters
    ----------
    std : float
        Standard deviation estimate
    n : int
        Number of sample

    Returns
    -------
    float
        Standard error of standard deviation estimate
    """
    return std / (2*n-2)**0.5

def se_skewness(n):
    """Standard error of skewness

    Parameters
    ----------
    n : int
        Number of sample

    Returns
    -------
    float of skewness estimate
    """
    return (6*n*(n-1) / ((n-2)*(n+1)*(n+3)))**0.5

class StatErrors( object ):
    def __init__(self, array , arrayRef, estLabel="", refLabel = ""):
        self.array = array
        self.arrayRef = arrayRef
        self.relDif = array / arrayRef
        self.diff = array - arrayRef
        self.estLabel = estLabel
        self.refLabel = refLabel

    def getCOV(self):
        return self.relDif.std() / self.relDif.mean()

    def getStd(self):
        return self.relDif.std()

    def getMean(self):
        return self.relDif.mean() - 1.

    def getQuad(self):
        return np.mean( (self.relDif-1)**2 )**0.5

    def getNRMSE(self):
        return np.mean( self.diff**2 )**0.5 / self.arrayRef.mean()

    def plotDistribution( self, ax = None, hist = False, **kwargs ):
        """Plot error histogram
        """
        import seaborn as sns
        if ax is None :
            fig, ax = plt.subplots()
        ax = sns.distplot( self.relDif-1, kde = True, hist = hist, ax=ax,**kwargs )
        return ax

    def plotScatter( self, ax = None, x_y = True, text = [] , **kwargs ):

        text = [t.lower() for t in text]
        if ax is None :
            fig, ax = plt.subplots()
        ax.scatter( self.arrayRef, self.array, **kwargs )
        ax.set_xlabel(self.refLabel)
        ax.set_ylabel(self.refLabel)
        if x_y :
            min_, max_ = self.arrayRef.min() , self.arrayRef.max()
            ax.plot( [min_, max_], [min_, max_] )


        q_dict = { "cov" : self.getCOV ,
                   "mean" : self.getMean,

                    }
        textDisplay = ""
        for q, f in q_dict.items() :
            if q in text :
                textDisplay += f"{q:} = {f():.1%}\n"

        if textDisplay :
            ax.text( 0.7 , 0.2 ,  textDisplay , transform=ax.transAxes )

        return ax

    def __str__(self):
        s  = "MEAN : {:.1%}\n".format( self.getMean())
        s += "STD : {:.1%}\n".format( self.getStd())
        s += "COV : {:.1%}\n".format( self.getCOV())
        s += "NRMSE : {:.1%}\n".format( self.getNRMSE())
        s += "QUAD : {:.1%}\n".format( self.getQuad())
        return s

if __name__ == "__main__" :

    from scipy.stats import norm
    n = 1000
    ref = np.linspace( 1,2,n )
    est = ref + norm(0.1,0.1).rvs(n)

#    ref = np.array([1,2,4,5,6])
#    est = np.array([1.1,1.8,4.0,5.1,7])

    err = StatErrors(est, ref, "estimation", "referance")
    print (err)
    err.plotScatter(marker = "+", alpha = 0.5)
    ax = err.plotDistribution(label = "test")
    ax.legend()



