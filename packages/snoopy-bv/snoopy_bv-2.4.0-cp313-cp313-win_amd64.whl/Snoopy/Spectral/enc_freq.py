import numpy as np
from Snoopy import Spectral as sp
from matplotlib import pyplot as plt
from Snoopy.Math import FunContourGenerator


class ContourWeSpeed( FunContourGenerator ):
    def __init__(self, speed , w_range = np.arange(0.2 , 1.8, 0.01), side = 2 ):
        """ x is frequency, y is heading
        """
        x = w_range
        y = np.linspace( 0. , side*np.pi , side*200 )
        self.speed = speed
        FunContourGenerator.__init__(self , lambda w , b : np.abs(sp.w2we( w, b, speed = speed )), x , y )

    def plot( self, values = None, **kwargs ) :
        if values is None :
            values = np.arange( 0.1 , sp.w2we( np.max(self.x) , b = np.pi, speed =self.speed) , 0.1 )
        ax = FunContourGenerator.plot(self, values = values, **kwargs)
        ax.set(xlabel = "Frequency (rad/s)" , ylabel = "Heading (rad)" )
        return ax

class ContourWeW( FunContourGenerator ):
    def __init__(self, w , speed_range, side = 2):
        x = speed_range
        y = np.linspace( 0. , side*np.pi , side*200 )
        FunContourGenerator.__init__(self , lambda speed, b : np.abs(sp.w2we( w, b, speed = speed )), x , y )

    def plot( self, values = None, **kwargs ) :
        ax = FunContourGenerator.plot(self, values = values, **kwargs)
        ax.set(xlabel = "Speed (m/s)" , ylabel = "Heading (rad)" )
        return ax


class ContourWeW_t( FunContourGenerator ):
    def __init__(self, w , speed_range, to_ms = 1.0, side = 2):
        x = np.linspace( 0. , side * np.pi , side * 200 )
        y = speed_range
        FunContourGenerator.__init__(self , lambda b, speed : np.abs(sp.w2we( w, b, speed = speed*to_ms )), x , y )

    def plot( self, values = None, **kwargs ) :
        ax = FunContourGenerator.plot(self, values = values, **kwargs)
        ax.set(xlabel = "Speed (m/s)" , ylabel = "Heading (rad)" )
        return ax





if __name__ == "__main__" :


    ContourWeSpeed( speed = 5.0 ).plot( )

    ContourWeW( speed_range = np.arange(0. , 10. , 0.01), w = 0.8 ).plot( values = [0.5],  )



