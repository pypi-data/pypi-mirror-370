from Snoopy.Statistics.dist import FrozenDistABC, DistGen


class PowernGen(DistGen):
    def __init__(self, distModel, n):
        self.distModel = distModel
        self.n = n

    def cdf(self, x, *args, **kwargs):
        return self.distModel(*args, **kwargs).cdf(x) ** self.n

    def pdf(self, x, *args, **kwargs) :
        return self.n * self.distModel.cdf(x, *args, **kwargs) ** (self.n-1) * self.distModel.pdf(x, *args, **kwargs)

    def ppf(self, p, *args, **kwargs) :
        return self.distModel.ppf( p**(1./self.n), *args, **kwargs )



class Powern( FrozenDistABC ):
    def __init__( self, dist, n ):
        self.dist = dist
        self.n = n

    def cdf(self, x):
        return self.dist.cdf(x)**self.n

    def pdf(self, x) :
        return self.n * self.dist.cdf(x) ** (self.n-1) * self.dist.pdf(x)

    def ppf(self, p) :
        return self.dist.ppf( p**(1./self.n) )


if __name__ == "__main__" :

    from scipy.stats import weibull_min
    from matplotlib import pyplot as plt
    import numpy as np
    n = 2922
    shape, loc , scale = 1.484,  0.66 , 3.041
    trueDist = weibull_min(shape, loc, scale)

    fig, ax = plt.subplots()
    hsList = np.arange(5, 25 , 0.02)
    ax.plot(hsList, Powern(trueDist, n ).pdf(hsList))
    ax.plot(hsList, Powern(trueDist, n*10 ).pdf(hsList))
    ax.plot(hsList, Powern(trueDist, n*100 ).pdf(hsList))