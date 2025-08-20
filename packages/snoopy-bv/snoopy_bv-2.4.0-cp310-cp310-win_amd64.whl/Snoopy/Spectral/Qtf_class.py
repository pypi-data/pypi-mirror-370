from __future__ import print_function
from __future__ import absolute_import
import numpy as np
from copy import deepcopy
from math import pi
from six.moves import map
from six.moves import range

class Qtf_py(object):
   __version__ = "QTF, python implementation"
   def __init__(self, filename = None):
      if filename : self.read(filename)
      self.mqtf = False
      self.nbhead2 = 1


   def read(self, filename, headerOnly = False):

      #Read header
      fil = open(filename, 'r')
      headerl = [line.strip() for line in fil.readlines() if line.strip()and line.strip().startswith('#')]
      fil.close()
      header = [line.split() for line in headerl]
      for iline, line in  enumerate(header):
         if line[0] == "#DIRECTION":
            self.direction = int(line[2])
         elif line[0] == "#NBHEADING":
            self.nbhead = int(line[1])
         elif line[0] == "#HEADING":
            self.heading = np.array(list(map(float, line[1:])), dtype=float)
         elif line[0] == "#DIFF":
            self.diff = np.array(list(map(float, line[1:])), dtype=float)
         elif "Water density" in headerl[iline]:
            self.rho = float(line[5])
         elif "Waterdepth" in line  :
            if line[3][:3].lower() == "inf":
               self.waterdepth = 0.
            else:
               self.waterdepth = float(line[3])
         elif "Gravity" in line:
            self.grav = float(line[4])
         elif "speed" in line:
            self.speed = float(line[4])
         elif line[0] == "#QTFMODE":
            self.qtfmode = line[1]
         elif "Ref.pt incident wave" in headerl[iline] :
            self.waveRefPoint = np.array([float(line[6].strip("(")), float(line[7].strip(")")), 0.0],
                                         dtype=np.float64)
         elif line[0] == "#COORD":
            self.refpoint = np.array(list(map(str, line[1:])), dtype=np.float64)
         elif line[0] == "#Heading2" and not self.mqtf:
            self.mqtf = True

      self.qtftype = "unknown"

      self.nbdiff = len(self.diff)
      data = np.loadtxt(filename)

      if self.mqtf:
          self.nbhead2 = self.nbhead
      self.nbfreq = int(len(data) / self.nbhead / self.nbhead2)
      self.freq = data[0:self.nbfreq  ,0]
      if (self.direction < 4):
         self.unit = r"$N/m^2$"
      if (self.direction > 3):
         self.unit = r"$N.m/m^2$"
      #self.unit="N/m^2"

      #Values
      if not headerOnly:
         self.values = np.zeros(  (self.nbfreq , self.nbdiff , self.nbhead , self.nbhead2) , dtype = complex )
         
         for ihead in range(self.nbhead):
             for ihead2 in range(self.nbhead2):
                f_offset = self.nbfreq *self.nbhead2 *ihead +self.nbfreq*ihead2
                for ifreq in range(self.nbfreq):
                   for idiff in range(self.nbdiff):
                      self.values[ifreq , idiff , ihead, ihead2] = complex(data[ f_offset + ifreq, 1+2*idiff],
                                                                           data[ f_offset + ifreq  , 2+2*idiff])

   def write(self, filename) :

      fil = open(filename , 'w')
      fil.write("# Project :\n")
      fil.write("# User    :\n")
      fil.write("# File : {}\n#\n".format(filename))
      fil.write("# Constants used in computations :\n")
      fil.write("#     Reference length     :     1.0000\n")
      fil.write("#     Water density (rho)  :  {}\n".format(self.rho))
      fil.write("#     Gravity acceleration :     {}\n".format(self.grav))
      if self.waterdepth > 1e-3 :    fil.write("#     Waterdepth           :  Inf.\n")
      else :                         fil.write("#     Waterdepth           :  {}\n".format(self.waterdepth))
      fil.write("#     Ref.pt incident wave : (    {} {})\n".format(self.waveRefPoint[0] , self.waveRefPoint[1]))
      fil.write("#            Forward speed :   " + str(self.speed) + " m/s\n")
      fil.write("#QTFTYPE    :  {}\n".format(self.qtftype) )
      fil.write("#UNIT       :  {}\n".format(self.unit) )
      fil.write('#DIRECTION "     {}\n'.format(self.direction) )
      fil.write("#NBHEADING " + str(self.nbhead) + "\n")
      fil.write("#HEADING " + " ".join(map(str, self.heading)) + "\n")
      fil.write("#DIFF " + " ".join(map(str, self.diff)) + "\n")
      fil.write("#---w(r/s)-----------------------------------------------------\n")
      
      if self.mqtf:
          for ihead, heading  in enumerate(self.heading) :
             fil.write("##Heading1 = {}\n".format(heading)  )
             for ihead2, heading2 in enumerate(self.heading) :
                 fil.write("#Heading2 = {}\n".format(heading2)  )
                 for ifreq, freq in enumerate(self.freq) :
                    fil.write( "{:.3f}  ".format(freq)  )
                    for idiff, diff in enumerate(self.diff) :
                       re = float(np.real(self.values[ifreq , idiff , ihead, ihead2]))
                       imag = float(np.imag(self.values[ifreq , idiff , ihead, ihead2]))
                       fil.write( "{: .6e} {: .6e} ".format( re , imag )  )
                    fil.write("\n")
                 fil.write("\n\n")
      else:
          for ihead, heading  in enumerate(self.heading) :
             fil.write("#Heading = {}\n".format(heading)  )
             for ifreq, freq in enumerate(self.freq) :
                fil.write( "{:.3f}  ".format(freq)  )
                for idiff, diff in enumerate(self.diff) :
                   re = float(np.real(self.values[ifreq , idiff , ihead, 0]))
                   imag = float(np.imag(self.values[ifreq , idiff , ihead, 0]))
                   fil.write( "{: .6e} {: .6e} ".format( re , imag )  )
                fil.write("\n")
             fil.write("\n\n")

      fil.close()
      return


   def __mul__(self, scal):
       qtf = deepcopy(self)
       qtf.values *= scal
       return qtf

   __rmul__ = __mul__

   def __div__(self, scal):
       qtf = deepcopy(self)
       qtf.values /= scal
       return qtf

   __rdiv__ = __div__

   def __add__(self, qtf2):
       qtf1 = deepcopy(self)
       qtf1.values += qtf2.values
       return qtf1

   def __sub__(self, qtf2):
       qtf1 = deepcopy(self)
       qtf1.values -= qtf2.values
       return qtf1
       
       
def move( vectQtf, newCoord , kind = "motion" , angle = "rad") :
   """
   return moved QTF to new location (x,y,z). original QTF is not modified
   """
   newQtf = deepcopy(vectQtf)
   oldCoord = vectQtf[0].refpoint
   x, y , z =  newCoord - oldCoord
   if angle == "rad" : toRad = 1
   elif angle == "deg" : toRad = pi/180.
   else : raise Exception
   Vi = np.array( [ [ 0. , -z , y ] , [ z , 0. , -x ] , [ -y , +x , 0. ] ] , dtype = float )
   newQtf[0:3] = newQtf[0:3] + np.dot( vectQtf[3:6] , Vi )
   return newQtf

if __name__ == "__main__" :

   #sum.write(r"D:\Etudes\Basic\rao\qtffx_2.qtf" )
   print ("Done")
