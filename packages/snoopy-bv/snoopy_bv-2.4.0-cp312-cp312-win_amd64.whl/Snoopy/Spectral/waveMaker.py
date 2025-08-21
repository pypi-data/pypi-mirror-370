import numpy as np
from numpy import sinh, cosh, exp
from Snoopy.TimeDomain import fftDf
from Snoopy import Spectral as sp
from matplotlib import pyplot as plt



def adim_transfer_function_hinged( kh , d ) :
    """Hinge wave maker transfer function (non-dimensional)

    Translated from HOS-NWT fortran code.

    Parameters
    ----------
    k : float or array-like
        wave-number * depth
    d : float
        relative height of hinge (d=0 ==> bottom mounted. d=0.5=> hinged at half the water depth)

    Returns
    -------
    complex
        transfer function amplitude / paddle_motion

    """

    if isinstance(kh, float) :
        return adim_transfer_function_hinged(np.array([kh]) , d)[0]

    resu = np.zeros( kh.shape , dtype = complex )

    def small_k_small_kd(k,d) :
        resu = - 1j * k * (1.0 - d) * (2.0 * k +   sinh(2.0 * k)) / (4.0 * sinh(k))
        resu = resu / (k * (1.0 - d) * sinh(k) + cosh(k * d) - cosh(k))
        return resu

    def big_k_small_kd(k,d):
        return - 1j * k * (1.0 - d) / (2.0 * k * (1.0 - d) -2.0 + 4.0 * cosh(k * d)*exp(-k))

    def both_large_1(k,d) :
        return - 1j * k * (1.0 - d) / (2.0 * k * (1.0 - d) - 2.0)

    def both_large_2(k,d) :
        return - 1j * k * (1.0 - d) / (2.0 * k * (1.0 - d) - 2.0 + 2.0 * exp(k*(d-1.0)))

    case_0 = (kh < 1e-10)
    resu[ case_0 ] = 0.0

    case_1 = (kh < 50) &  (kh * d < 50) & ~case_0
    resu[ case_1 ] = 1. / small_k_small_kd( kh[case_1] , d )

    case_2 = (kh >= 50) & (kh*d < 50) & ~case_0
    resu[ case_2 ] = 1. / big_k_small_kd( kh[case_2] , d )

    case_3 = (kh >= 50) & (kh*d >= 50) & (kh * (1.0 - d ) > 20) & ~case_0
    resu[ case_3 ] = 1. / both_large_1( kh[case_3] , d )

    case_4 = (kh >= 50) & (kh*d >= 50) & (kh * (1.0 - d ) <= 20) & ~case_0
    resu[ case_4 ] = 1. / both_large_2( kh[case_4] , d )

    assert((case_0.astype(int) + case_1.astype(int) + case_2.astype(int) + case_3.astype(int) + case_4.astype(int) == 1).all())

    return resu


def adim_transfer_function_piston( kh ) :
    """Piston wave maker transfer function (non-dimensional), module

    Parameters
    ----------
    kh : float or array-like
        wave-number * depth

    Returns
    -------
    float
        transfer function amplitude / paddle_motion
    """

    return 4 * sinh( kh )**2 / (2*kh + sinh(2*kh))


def adim_transfer_function_flap( kh ) :
    """Flap wave maker transfer function (non-dimensional), module.

    Should corresponds to adim_transfer_function_hinged with d = 0.0

    Parameters
    ----------
    kh : float or array-like
        wave-number * depth

    Returns
    -------
    float
        transfer function amplitude / paddle_motion
    """
    return 4 * ( sinh( kh ) / kh) * (  kh * sinh(kh) - cosh(kh) + 1)   / ( sinh(2*kh) + 2 * kh)


class WaveMaker(object):

    def __init__(self , h, d):
        """Wave maker class

        For now, only handle transfer function for hinged paddle

        Parameters
        ----------
        h : float
            Water depth
        d : float
            Height of the hinge (from bottom)
        """
        self.d = d
        self.h = h


    def transfer_function( self , w ) :
        d = self.d
        h = self.h
        k = sp.w2k(w , h)
        return adim_transfer_function_hinged(  k * h , d / h)


    def to_wif(self , se_stroke) :
        """Output wif file of linear wave elevation at wave-maker position
        """

        fft_stroke = fftDf( se_stroke, index = "rad" )

        fft_wave = fft_stroke * self.transfer_function( fft_stroke.index.values )

        wif_ = sp.Wif( w = fft_wave.index.values , a = np.abs(fft_wave.values) , phi = np.angle( fft_wave.values ) , b = np.full( fft_wave.shape, np.pi ))

        wif_.removeZeroFrequency()

        return wif_



    def wave_FFT(self , paddle_se) :
        """Return wave FFT

        Perform FFT on paddle motion, and apply RAO

        Parameters
        ----------
        paddle_se : pd.Series
            Wave motion time-series

        Returns
        -------
        pd.Series
            FFT of wave elevation
        """

        eps = 1e-8
        fft_ = fftDf(paddle_se).loc[eps:]
        wave_fft_ = fft_ * self.transfer_function( w = fft_.index.values * 2*np.pi )
        return wave_fft_


    def plot(self , ax = None, w = np.linspace( 0.2, 4.0 , 50 ) , adim = False) :
        if ax is None :
            fig , ax = plt.subplots()

        if adim :
            ax.plot(  sp.w2k(w , self.h) * self.h , np.abs(self.transfer_function(w))  )
            ax.set( xlabel = "kh"  , ylabel = "Transfer function (H / S)")
        else :
            ax.plot(  w , np.abs(self.transfer_function(w))  )
            ax.set( xlabel = "Frequency (rad/s)"  , ylabel = "Transfer function (H / S)")

        return ax



if __name__ == "__main__" :

    h = 5.
    d = 0.

    wmk = WaveMaker( h, d )

    wmk.plot()
    wmk.plot(adim = True)
