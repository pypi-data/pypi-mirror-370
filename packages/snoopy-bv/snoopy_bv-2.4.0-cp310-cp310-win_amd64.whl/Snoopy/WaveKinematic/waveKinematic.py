import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import _WaveKinematic

availableWaveKinematic = [
                         'FirstOrderKinematic',
                         'SecondOrderKinematic',
                         'SecondOrderKinematic21',
                         'Wheeler1st',
                         'Wheeler2nd',
                         'DeltaStretching',
                         ]


class WaveKinematicABC( object) :

    def getElevation_SE( self , time , x, y , speed = 0.0 ) :
        """Return wave elevation at a fixed position, as pandas Series.


        Parameters
        ----------
        time : float or array-like
            Time
        x : float or array-like
            x coordinates of the point.
        y : float or array-like
            y coordinates of the point.
        speed : float, optional
            Speed. The default is 0.0.

        Returns
        -------
        pd.Series
            Wave elevation
        """

        res = self.getElevation(  time , x, y , speed = speed )
        se = pd.Series( index = pd.Index(time , name = "Time") , data = res )
        se.name = "eta (m)"
        return se

    def getPressure_SE( self , time , x, y , z ) :
        """Return wave dynamic pressure at a fixed position, as pandas Series.


        Parameters
        ----------
        time : float or array-like
            Time
        x : float or array-like
            x coordinates of the point.
        y : float or array-like
            y coordinates of the point.
        z : float or array-like
            z coordinates of the point.

        Returns
        -------
        pd.Series
            Wave pressure (in m).
        """

        res = self.getPressure( time , x, y, z )
        se = pd.Series( index = pd.Index(time , name = "Time") , data = res )
        se.name = "Pressure"
        return se


    def getElevation_DF( self , time , xVect , y , speed = 0.0 ) :
        """Return wave elevation along X axis as pandas dataframe (time, x0, x1 ... xn).
        """
        res = self.getElevation2D(  time , xVect, np.full( time.shape, y) , speed = speed )
        return pd.DataFrame( index = time , data = res, columns = xVect )


    def getVelocity_DF( self , time , x, y , z, speed = 0.0, index = "time" ) :
        """Return wave velocity at a fixed position, as pandas DataFrame (time, vx, vy, vz).

        Parameters
        ----------
        time : array
            Time
        x : float
            x coordinates of the point.
        y : float
            y coordinates of the point.
        z : float
            z coordinates of the point.
        speed : float, optional
            Speed. The default is 0.0.

        Returns
        -------
        pd.DataFrame
            Wave kinematic

        Example
        -------
        vel = kin.getVelocity_DF( time = np.arange(0., 10800 , 0.5) , [0.0 , 0.0] )

        """

        if isinstance(time , np.ndarray) :
            index = "time"
        elif isinstance(z , np.ndarray) :
            index = "z"
        else :
            raise(Exception("Only one argument should be an array"))

        # TODO Vectorize in c++ for much faster computation ?
        if index == "time" :
            res = np.empty( (len(time) , 3 ))
            for i, t in enumerate(time) :
                res[i] = self.getVelocity(  t , x + speed * t , y , z )
            return pd.DataFrame( index = pd.Index(time, name = index) , data = res ,columns = ["vx" , "vy" , "vz"] )

        elif index == "z" :
            res = np.empty( (len(z) , 3 ))
            for i, z_ in enumerate(z) :
                res[i] = self.getVelocity(  time , x + speed * time , y , z_ )
            return pd.DataFrame( index = pd.Index(z, name = index) , data = res ,columns = ["vx" , "vy" , "vz"] )


    def __call__(self , time , x , y) :
        return self.getElevation( time, x , y  )

    def getModes(self):
        return [0]


    def plot( self, time, x_range, z_range, ax = None, x_range_eta = None, x_scale = 1.0 ):
        """Plot wave kinematic with vector (+ free-surface elevation)

        Parameters
        ----------
        time : float
            Time to plot
        x_range : np.ndarray
            X range
        z_range : np.ndarray
            z range
        ax : Axis, optional
            Where to plot. The default is None.
        x_range_eta : np.ndarray, optional
            x_range for the elevation (generally finer than for velocity vectors). The default is None.
        x_scale : float, optional
            Scale for x-axis. The default is 1.0.

        Returns
        -------
        ax : Axis
            The plot.
        """

        if ax is None :
            fig, ax = plt.subplots()

        if x_range_eta is None :
            x_range_eta = x_range

        # Variable are cached, so that only data has to be updated upon animation (use in .__update_plot).
        self.__x_range_eta = x_range_eta
        self.__x_scale = x_scale
        self.__X, self.__Z = np.meshgrid( x_range, z_range )
        self.__u = np.full( self.__X.shape , np.nan)
        self.__v = np.full( self.__X.shape , np.nan)

        for ix in range(len(x_range)) :
            for iz in range(len(z_range)) :
                if self.__Z[iz, ix] < self.getElevation( time, self.__X[iz,ix] , 0.0 ) :
                    self.__u[iz,ix], _ , self.__v[iz,ix] = self.getVelocity( time = time , x = self.__X[iz,ix] , y = 0.0 , z = self.__Z[iz, ix] )

        eta = self.getElevation( time, x_range_eta , 0.0 )

        self.__line,  = ax.plot(x_range_eta / x_scale, eta)
        self.__quiver = ax.quiver( self.__X / x_scale, self.__Z, self.__u, self.__v, (self.__u**2 + self.__v**2)**0.5, cmap = "cividis")
        ax.set(title = "Wave kinematic", xlabel = r"x (m)", ylabel = "z (m)")
        return ax

    def __update_plot(self, time):
        """Update plot ( .plot() has to be called first)
        """

        # Update quiver
        self.__u[:,:] = np.nan
        self.__v[:,:] = np.nan
        for ix in range( self.__X.shape[1]  ) :
            for iz in range(self.__X.shape[0]) :
                if self.__Z[iz, ix] < self.getElevation( time, self.__X[iz,ix] , 0.0 ) :
                    self.__u[iz,ix], _ , self.__v[iz,ix] = self.getVelocity( time = time , x = self.__X[iz,ix] , y = 0.0 , z = self.__Z[iz, ix] )
        self.__quiver.set_UVC( self.__u, self.__v, (self.__u**2 + self.__v**2)**0.5)

        # Update wave elevation
        eta = self.getElevation( time, self.__x_range_eta , 0.0 )
        self.__line.set_data( self.__x_range_eta / self.__x_scale, eta )



    def animate(self , time_range , x_range, z_range, ax = None, x_range_eta = None, x_scale = 1.0, set_args = {}) :
        """Animates wave kinematic with vector (+ free-surface elevation)

        Parameters
        ----------
        time_range : np.ndarray
            Time range
        x_range : np.ndarray
            X range
        z_range : np.ndarray
            z range
        ax : Axis, optional
            Where to plot. The default is None.
        x_range_eta : np.ndarray, optional
            x_range for the elevation (generally finer than for velocity vectors). The default is None.
        x_scale : float, optional
            Scale for x-axis. The default is 1.0.

        Returns
        -------
        FuncAnimation
            The animation.
        """
        from matplotlib.animation import FuncAnimation
        ax = self.plot(0., x_range = x_range, z_range = z_range, x_scale = x_scale, x_range_eta = x_range_eta, ax=ax)
        return FuncAnimation( ax.get_figure(), func = self.__update_plot, frames = time_range)



class SecondOrderKinematic(_WaveKinematic.SecondOrderKinematic, WaveKinematicABC) :
    pass

class SecondOrderKinematic21(_WaveKinematic.SecondOrderKinematic21, WaveKinematicABC) :
    pass

class FirstOrderKinematic(_WaveKinematic.FirstOrderKinematic, WaveKinematicABC) :
    pass

class Wheeler1st(_WaveKinematic.Wheeler1st, WaveKinematicABC) :
    pass

class Wheeler2nd(_WaveKinematic.Wheeler2nd, WaveKinematicABC) :
    pass

class DeltaStretching(_WaveKinematic.DeltaStretching, WaveKinematicABC) :
    pass



if __name__ == "__main__":
    from Snoopy import Spectral as sp
    from Snoopy import WaveKinematic as wk

    hs, tp = 5.0 , 10.0
    ss = sp.SeaState(sp.Jonswap(hs = hs , tp = tp, gamma=1.0 , heading = 0.0))

    new_wave = wk.DeltaStretching( sp.edw.NewWave(target = 8.0 , ss = ss, waveModel = wk.FirstOrderKinematic).wif , 0.3 , 20.)


    new_wave_anim = new_wave.animate( time_range = np.arange(-4*tp, 4*tp , tp/10),
                                      x_range = np.arange( -3 * sp.t2l(tp), 3 * sp.t2l(tp), sp.t2l(tp) / 10),
                                      x_range_eta = np.arange( -3 * sp.t2l(tp), 3 * sp.t2l(tp), sp.t2l(tp) / 50),
                                      z_range = np.arange(-8, 10.0, 1.0), set_args = {"ylim" : (-10 , +8)}
                                    )
