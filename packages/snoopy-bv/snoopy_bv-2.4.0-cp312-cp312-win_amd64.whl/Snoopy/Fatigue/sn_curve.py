import pandas as pd
import numpy as np
from scipy.special import gammaincc, gamma
from scipy.integrate import quad, simpson
from scipy.optimize import root_scalar
from Snoopy import Fatigue as ft

class SnCurve(object):
    """SN curve data, and associated routine to calculate fatigue damage.

    Damage can be calculated from spectral values, from time-series, from discretized or analytical stress range distribution.

    S = SN.data[:,0] , m = SN.data[:,1], K = SN.data[:,2]

    Example
    -------
    >>> sn = SnCurve.BuildFromFAT(FAT=90.,slopes=[3.,5.]):
    >>> sn.damage_from_RSRTZ( rs = 100.0 , rtz = 10. , duration = 3600.)
    0.00011436041519549667
    """

    def __init__( self, data ) :
        """Build multi-slope SN-Curve

        Parameters
        ----------
        data : Array like
            SN-curve as [S, m, K] array

        Example
        -------
        >>> # A 2 slope SN-Curve
        >>> sn = SnCurve( [[0.0 ,  5, 4.330E15],     # For  0.00 < S < 53.4
        >>>                [53.4,  3, 1.520E12]]     # For  53.4 < S
        >>>             )
        >>>
        >>> # A single slope SN-Curve
        >>> # The first 0.0 (S) means that there is no "threshold", all cycles induce fatigue damage.
        >>> sn = SnCurve( [[0.0,  3, 1.520E12],] )
        """
        #Sort by increasing threshold
        self.df = pd.DataFrame( index = range(len(data)), data = data , columns = ["S", "m", "K"] )
        self.df = self.df.sort_values(by = "S").reset_index(drop=True)
        if not self.check() :
            #print (self)
            raise(Exception( "SN curve data not consistent"))


    def __str__(self):
        return self.df.__str__()

    @property
    def nbSlope(self):
        return len(self.df)


    @classmethod
    def BuildFromFile(cls, filename, sn_id = None) :
        """Build from StarSpec type syntax

        SN_CURVE  [sn_id]
        0.1    5       4.330E15
        53.4    3       1.520E12
        ENDSN_CURVE
        """

        with open(filename) as f :
            data = "\n".join([ l.strip() for l in f.readlines() if not (l.__contains__(".rao") or l.startswith("#")) ])
        f = data.split("SN_CURVE")
        for curves in f[1:-1] :
            curves_ = [ l for l in curves.splitlines() if not l.startswith("#") ]
            nSlope = len(curves_) - 2
            data = np.empty( ( nSlope ,3), dtype = float )
            if curves_[0].strip() :
                sn_id_ = curves_[0].split()[0]
            else :
                sn_id_ = None

            if sn_id == sn_id_:
                for islope in range(nSlope):
                    data[islope , :] = [float(s) for s in curves_[islope+1].split()]
                return cls(data)
        else :
            raise(Exception("SN_CURVE '{}' not found".format(sn_id)) )


    @classmethod
    def BuildFromFAT(cls,FAT=90.,slopes=[3.,5.]):
        """
        Build SN parameters from FAT value
        """
        if len(slopes) != 2:
            raise( Exception( 'ERROR: Number of slopes needs to be equal to 2.'))

        m1, m2 = slopes
        K1 = 2e6*FAT**m1
        SQ = K1**(1./m1)*10**(-7./m1)
        K2 = K1*SQ**(m2-m1)
        data = np.array([[SQ,m1,K1],[1e-4,m2,K2]])
        return cls(data)


    def _getIntersection_S(self, i=0 ) :
        """ Compute S at intersection between the slope "i" and "i+1"
        """
        s = np.exp((np.log(self.df.K[i+1] / self.df.K[i]) ) / ( self.df.m[i+1]-self.df.m[i]))
        return s

    def check(self):
        """Check SN curve consistency
        Return True if ok
        """
        for i in range(0, self.nbSlope-1  ):
            s = self._getIntersection_S( i )
            if ( abs(self.df.S[i+1]-s) > 0.05 * s):
                print("Unconsistent slope intersection")
                print(" Defined value :"+str(self.df.S[i+1]))
                print(" Computed value:"+str(s))
                return False
        return True


    def plot(self, ax=None, **kwargs):
        """Plot the SN-curve

        Parameters
        ----------
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        **kwargs : any
            Argument passed to plt.plot()

        Returns
        -------
        ax :
            The graph
        """
        from matplotlib import pyplot as plt
        sn = self.df
        if ax is None :
            fig, ax = plt.subplots()
        if self.nbSlope > 1:
            for i in range(self.nbSlope):
                s_min = max( sn.S[i] , (sn.K[i] / 1e10)**(1./sn.m[i]) ) # Avoid /0.0
                n_max = sn.K[i] / ( s_min ** sn.m[i] )
                if i == self.nbSlope-1 :
                    n_min = n_max / 100.
                    s_max = (sn.K[i] / n_min) ** (1/sn.m[i])
                else :
                    s_max = sn.S[i+1]
                    n_min = sn.K[i] / ( s_max ** sn.m[i] )
                ax.plot( [n_min, n_max], [s_max, s_min] , **kwargs)
        else:
            s_min = max( sn.S[0] , (sn.K[i] / 1e10)**(1./sn.m[i]) ) # Avoid /0.0
            n_max = sn.K[0] / ( s_min ** sn.m[0] )
            n_min = 1e2
            s_max = (sn.K[0] / n_min) ** (1/sn.m[0])
            ax.plot( [n_min, n_max], [s_max, s_min] , **kwargs )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("N")
        ax.set_ylabel("S")
        return ax



    def damage_from_RSRTZ (self, rs, rtz, duration) :
        """Return the damage from spectral moment (==> cycles are Rayleigh distributed)


        Parameters
        ----------
        rs : float
            Significant response (range)
        rtz : float
            UpCrossing period (in seconds)
        duration : float
            Sea-state duration.

        Returns
        -------
        float
            Damage on the given duration (in seconds)

        """

        sn = self.df
        dam = 0
        # using the upper incomplete gamma function
        #  sn.S[i]   is the lower bound of the i part of the SN curve
        #  sn.S[i+1] is the upper bound of the i part of the SN curve, provided that the curve is described starting from the lower part

        for i in range(self.nbSlope) :
            gratio1 = gammaincc( 1. + 0.5*sn.m[i], 2*sn.S[i]**2 / rs**2 )
            if i < self.nbSlope-1 :
                gratio2 = gammaincc( 1. + 0.5*sn.m[i], 2*sn.S[i+1]**2 / rs**2 )
            else:
                gratio2 = 0.  # the last part of the SN curve has no upper bound
            dam += (1. / sn.K[i]) * ( rs * 2.**0.5 / 2. )**sn.m[i]  * ( gratio1 - gratio2 ) * gamma( 1 + 0.5 * sn.m[i] )

        return dam * duration / rtz


    def fatigueLife_from_RSRTZ(self, rs, rtz, unit = "year" ) :
        """Return fatigue life on the sea-state (in year)

        Parameters
        ----------
        rs : float
            Significant response (range)
        rtz : float
            UpCrossing period (in seconds)
        unit : str
            Unit of the output fatigue life

        Returns
        -------
        float
            Fatigue life
        """
        if "year" in unit :
            return 1. / self.damage_from_RSRTZ( rs, rtz , 365.24*24*3600)
        elif "second" in unit :
            return 1. / self.damage_from_RSRTZ( rs, rtz , 1.)



    def damage_from_cycle( self , cycles ):
        dam = 0
        for i in range(self.nbSlope) :
            if i != self.nbSlope-1:
                upLim = self.df.S.iloc[i+1]
            else :
                upLim = np.inf
            c = cycles[ np.where( (self.df.S.iloc[i] < cycles) & (cycles <= upLim ) ) ]
            fat =  c**self.df.m.iloc[i] / self.df.K.iloc[i]
            dam += fat.sum()
        return dam

    def damage_from_ts( self , ts ) :
        """Return damage from time-series

        Parameters
        ----------
        ts : pd.Series or pd.DataFrame
            Stress time-series (index is time)

        Returns
        -------
        float
            Damage
        """

        cycles = ft.Rainflow( ts )()
        return self.damage_from_cycle( cycles )

    def fatigueLife_from_ts( self , ts ) :
        """Return fatigue life from time-series

        Parameters
        ----------
        ts : pd.Series
            Stress time-series (index is time)

        Returns
        -------
        float
            Fatigue life (same unit as ts.index)
        """

        duration = ts.index[-1] - ts.index[0]
        cycles = ft.Rainflow( ts )()
        return duration / self.damage_from_cycle( cycles )


    def damage_from_distribution(self, stress_range_pdf, nb_cycles):
        """Integrate numerically the SN curve with any analytical distribution.
        
        Parameters
        ----------
        stress_range_pdf : fun
            pdf of stress range
        nb_cycles : float
            Number of cycles

        Returns
        -------
        dam : float
            fatigue damage
        """
        
        dam = 0
        for iSlope in range(self.nbSlope) :
            s_min = self.df.S[iSlope]
            if iSlope == self.nbSlope-1 :
                s_max = np.inf
            else :
                s_max = self.df.S[iSlope+1]
            m = self.df.m[iSlope]
            k = self.df.K[iSlope]
            dam += quad( lambda x : stress_range_pdf(x) * x**m / k , s_min, s_max  )[0] * nb_cycles
        return dam
    
    def damage_from_distribution_corr(self, stress_range_pdf, nb_cycles, ReEQ, s_mean, s_res0, s_waveHS):
        """Integrate numerically the SN curve with any analytical distribution + a correction for mean stress effects
        
        Parameters
        ----------
        stress_range_pdf : fun
            pdf of stress range
        nb_cycles : float
            Number of cycles
        ReEQ : float
            Yielding stress (MPa)
        s_mean : float
            mean stress for the loading condition considered (MPa)
        s_res0 : float or str
            initial residual stress. if string value is set according to NI611 "plated_joint" or "cut_edge" depending on the element considered
        s_waveHS : float
            stress value at p=10^-4 (MPa)

        Returns
        -------
        dam : float
            fatigue damage
        """
        
        if isinstance(s_res0, str):
            if s_res0 == "plated_joint":  # from 611,  4.1.5 
                s_res0 = 0.1 * ReEQ
            elif s_res0 == "cut_edge":
                s_res0 = 0.0 # from NI611, (cut edge) 4.3.3
            else:  
                raise(Exception())

        s_cor = s_mean + s_res0   # corrected mean stress
        s_max = s_mean + s_waveHS

        if s_max + s_res0 > ReEQ :
            s_cor = s_mean + ReEQ - s_max
            
        # HERE THE CORRECTION FACTOR IS OBTAINED
        def x_to_xcorr(x):
            # Calculate the correction factor f_mean
            f_meanHS = 0.7 + 0.6*s_cor/x
            return np.clip(f_meanHS, 0.4, 1.0)*x

        def xcorr_to_x(x_corr):
            return root_scalar( lambda x : x_to_xcorr(x) - x_corr  , bracket = [x_corr/0.39 , x_corr/1.05] ).root

        dam = 0
        for iSlope in range(self.nbSlope) :
            s_min = self.df.S[iSlope]
            if s_min > 1e-3:
                s_min = xcorr_to_x(s_min)
                
            if iSlope == self.nbSlope-1 :
                s_max = np.inf
            else :
                s_max = self.df.S[iSlope+1]
                s_max = xcorr_to_x(s_max)
                
            m = self.df.m[iSlope]
            k = self.df.K[iSlope]

            dam += quad( lambda x : stress_range_pdf(x) * ( x_to_xcorr(x) )**m / k , s_min, s_max  )[0] * nb_cycles
            # x_range = np.linspace(s_min, s_max, 200)
            # dam += simpson( [stress_range_pdf(x) * x_corr(x)**m / k for x in x_range ], x_range ) * nb_cycles
        return dam



    def fatigueLife_from_distribution(self, stress_range_pdf, rtz ) :
        """Return fatigue life on the sea-state (in year).
        """
        return 1. / self.damage_from_distribution( stress_range_pdf, nb_cycles = 365.24*24*3600 / rtz )



    def damage_from_weibull(self, N, DSref, pR, ksi) :
        """Return the damage from Weibull distribution analytical integration

        Weibull distribution is parametrized with the stress range at a given probability level, and its shape factor

        Parameters
        ----------
        N : int or float
            Number of cycle
        DSref : float
            Stress range at probability pR
        pR : float
            Reference probability
        ksi : float
            Weibull shape factor

        Returns
        -------
        float
            fatigue damage
        """
        sn = self.df
        dam = 0

        lbda = DSref / (-np.log(pR))**(1./ksi) # Weibull scale parameter

        # using the upper incomplete gamma function
        #  sn.S[i]   is the lower bound of the i part of the SN curve
        #  sn.S[i+1] is the upper bound of the i part of the SN curve, provided that the curve is described starting from the lower part

        for i in range(self.nbSlope) :
            gratio1 = gammaincc( 1. + sn.m[i]/ksi, (sn.S[i] / lbda)**ksi )
            if i < self.nbSlope-1 :
                gratio2 = gammaincc( 1. + sn.m[i]/ksi, (sn.S[i+1] / lbda)**ksi )
            else:
                gratio2 = 0.  # the last part of the SN curve has no upper bound
            dam += (1. / sn.K[i]) * lbda**sn.m[i]  * ( gratio1 - gratio2 ) * gamma( 1. + sn.m[i]/ksi )

        return dam * N

    def damage_from_constantAmplitude(self, N, DS) :
        """ Return the damage for constant amplitude stress cycles
        """
        sn = self.df
        #  sn.S[i]   is the lower bound of the i part of the SN curve
        #  sn.S[i+1] is the upper bound of the i part of the SN curve, provided that the curve is described starting from the lower part

        if DS < sn.S[0] :
            # if DS is smaller than any value in sn.S[i] then we use the lowest part of the SN curve
            iSlope = 0
        else :
            for i in range(len(sn.S)-1) :
                if DS > sn.S[i] and DS < sn.S[i+1]:
                    iSlope = i
                elif DS > sn.S[i+1] : # this one is necessary to manage the last part
                    iSlope = i+1

        dam = DS**sn.m[iSlope] / sn.K[iSlope]

        return dam * N

    def damage_from_multiple_EDW(self, s_ranges, p_levels, Nt):
        """
        Compute the fatigue damage from a LT distribution obtained by several EDW
         using the method in NI611 R01 App 1 5.5.6 b) with the following modifications:
            - extended to any nb of slopes in the SN curve
            - the stress distribution is extrapolated beyond the last probability level.

        Parameters
        ----------
        s_ranges : array of real
            Stress ranges at different probability levels, in increasing order
        p_levels : array of real
            Probability levels, in decreasing order
        Nt : real
            Total number of cycles over the duration

        Returns
        -------
        The long term damage

        """
        nb_s_ranges = s_ranges.size
        if p_levels.size != nb_s_ranges:
            print('ERROR: unconsistent nb of stress range and probability_level data')

        sn = self.df
        damage = 0.

        for i_range in range(nb_s_ranges-1):
            if s_ranges[i_range] >= s_ranges[i_range+1]:
                print('ERROR: stress ranges are expected in increasing order')
            if p_levels[i_range] <= p_levels[i_range+1]:
                print('ERROR: probability levels are expected in decreasing order')

            lbda = - (s_ranges[i_range+1] - s_ranges[i_range]) / (np.log(p_levels[i_range+1]) - np.log(p_levels[i_range]))
            if lbda > 0.:
                kapa = np.log(p_levels[i_range]) + s_ranges[i_range] / lbda

                for i_slope in range(self.nbSlope):
                    # find the intersection of the two intervals
                    lower_bound = max(s_ranges[i_range], sn.S[i_slope])
                    gratio1 = gammaincc(1.+sn.m[i_slope], lower_bound / lbda)
                    #upper bound:
                    if i_slope < self.nbSlope-1:
                        if i_range < nb_s_ranges-2:
                            upper_bound = min(s_ranges[i_range+1], sn.S[i_slope+1])
                        else:
                            # extrapolate the last part of the distribution up to SN slope limit
                            upper_bound = sn.S[i_slope+1]
                        gratio2 = gammaincc(1.+sn.m[i_slope], upper_bound / lbda)
                    else:
                        #the last part of the SN curve has no upper bound
                        if i_range < nb_s_ranges-2:
                            upper_bound = s_ranges[i_range+1]
                            gratio2 = gammaincc(1.+sn.m[i_slope], upper_bound / lbda)
                        else:
                            # last part of distribution and of SN curve -> no upper limit
                            gratio2 = 0.

                    D = max(0., gratio1-gratio2) # i.e. check that lower_bound < upper_bound
                    D *= lbda**sn.m[i_slope] / sn.K[i_slope] * gamma(1.+sn.m[i_slope])
                    D *= Nt * np.exp(kapa)
                    damage += D

        return damage

#For compatibility purpose
SnCurve.spectralFatigueLife = SnCurve.fatigueLife_from_RSRTZ
SnCurve.distributionDamage  = SnCurve.damage_from_distribution
SnCurve.spectralDamage = SnCurve.damage_from_RSRTZ
SnCurve.WeibullDamage = SnCurve.damage_from_weibull
SnCurve.ConstantAmplitudeDamage = SnCurve.damage_from_constantAmplitude


def ThicknessEffectFactor(t,tRef=25.,n=0.25):
    """ Return the thickness effect factor to multiply the stress ranges or divide the FAT
    See applicable rules or NI611 to get values for tRef and n
    """
    tEff = max(tRef,t)
    return (tEff/tRef)**n

def YieldThicknessEffectFactor(ReH):
    """ Return the yield stress effect factor to multiply the stress ranges or divide the FAT
    See applicable rules or NI611
    """
    return 1200./(965.+ReH)


if __name__ == "__main__" :
    data = np.array( [ [0.001,  5, 4.330E15]], dtype = float )

    sn = SnCurve(data)
    sn.plot()
