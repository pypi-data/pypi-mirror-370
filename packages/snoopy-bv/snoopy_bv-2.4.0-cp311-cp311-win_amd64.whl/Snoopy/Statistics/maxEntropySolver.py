import numpy as np
from scipy.integrate import simpson
from scipy.optimize import root
from copy import deepcopy
from Snoopy import logger

class MaxEntropySolver(object) :

    def __init__(self , mu , x = np.linspace( -0.2 , 0.2 , 1000 ) ) :
        """Find exponential distribution that matches the specified moment.

        The exponential distribution can be shown to be the one maximising the entropy.

        Parameters
        ----------
        mu : array like
            Moments
        x : array like, optional
            Integration point. The default is np.linspace( -0.2 , 0.2 , 1000 ).

        """

        #Target moment
        self.mu = mu

        #Integration step for x
        self.x = x
        self.n = len(self.mu)
        self._jac = np.empty( (self.n,self.n) )
        self._moms = np.empty( (self.n) )
        self._lSol = None
        self._pdfSol = None


    def gn( self, l = None  ) :
        """Compute moments
        """
        from .f_maxEntropy import pdf_v as expPdf_v
        if l is None :
            l = self._lSol
        n = len(l)
        pVect = expPdf_v( self.x , l  )
        for i in range( n ) :
            tmp_ = pVect * self.x**(2*i)
            self._moms[i] = simpson(tmp_ , x=self.x)
        return self._moms


    def gnk( self, l = None ) :
        """Compute moments derivative
        """
        from .f_maxEntropy import pdf_v as expPdf_v
        if l is None :
            l = self._lSol
            pVect = self._pdfSol
        else :
            pVect = expPdf_v( self.x , l)

        for in_ in range(self.n) :
            for ik_ in range(self.n) :
                tmp_ = pVect * self.x**(2*in_ + 2*ik_)
                self._jac[in_,ik_] = -simpson( tmp_ , x=self.x )
        return self._jac


    def solve( self , l0 , method = "hybr", itmax = 500, eps = 1e-8) :
        """
        Parameters
        ----------
        l0 : array-like
            Starting coefficients
        method : str, optional
            Solver used, among ["Newton", "hybr", "lm", "broyden1", "broyden2", "anderson"]. The default is "hybr".
        itmax : int, optional
            Maximum number of iteration. The default is 500.
        eps : float, optional
            Tolerance. The default is 1e-8.

        Returns
        -------
        array-like
            Coefficient of exponential distribution matching the moment
        """
        from .f_maxEntropy import pdf as expPdf

        logger.debug( f"MaxEntrop in {self.mu:} {max(self.x):} {l0:}" )

        # Newton non-linear solver
        if method == "Newton" :
            l = deepcopy(l0)
            entr = -l.dot( self.gn(l0) )
            for i in range(itmax) :
                moms = self.gn(l)
                entr_0 = entr
                jacs = self.gnk(l)
                v = self.mu - moms
                delta = np.linalg.solve(jacs , v)
                l += delta

                #Compute entropy at iteration i
                entr = -l.dot( moms )

                #Stopping criteria
                if( abs( (entr - entr_0) / entr) < eps ) and i > 2:
                    break
            else :
                print ("Error, MaxEntropySolver, Maximum of iterations reach")
                raise(Exception)
            self.n_it = i   # Number of iteration

        elif method in ["hybr", "lm", "broyden1", "broyden2", "anderson", "linearmixing", "diagbroyden", "excitingmixing", "krylov", "df-sane"]:
            #Scale
            diag = np.ones(  (len(l0)) , dtype = float )
            for i in range(2, len(l0)) :
                diag[i] = self.mu[1]**i
            l = root( lambda x : self.gn(x) - self.mu , x0=l0 , jac  = self.gnk , method = method, options = {"diag" : diag} ).x
        else :
            raise(Exception(f"Wrong input for method in solve {method:}"))


        #Check relative error < 1 %, for each item (if target is > 1e-50)
        c = np.where( np.abs(self.mu) > 1e-30 )
        if (np.abs( self.mu[ c ] / self.gn(l)[c] - 1.0 ) > 0.05).any() :
            print( self.mu[ c ] )
            print( self.gn(l)[c] )
            print ("Warning : bad solution")

        self._lSol = l
        self._pdfSol = np.array( [ expPdf(x_ , l) for x_ in self.x ] )

        return self._lSol

    def getDistribution(self , cdfInterpolated = False ) :

        from .f_maxEntropy import MaxEntropyDistribution
        if self._lSol is None :
            self.solve()
        d = MaxEntropyDistribution( self._lSol )
        if cdfInterpolated is True :
            d.cdf = lambda x : self.cdf_interp(x)
        return d

    def cdf_interp( self , x , l = None ) :
        """
        cdf function (use precomputed database and interpolate)
        """
        if l is None :
            pdf = self._pdfSol
        else :
            pdf = np.array( [ expPdf(x_ , l) for x_ in self.x ] )

        #Integrate and interpolate
        i = np.searchsorted(self.x , x)
        if i == 0 :
            return 0
        s1 =  simpson( pdf[:i] , x=self.x[:i] )
        s2 =  simpson( pdf[:i+1] , x=self.x[:i+1] )
        return 0.5*(s1+s2)

