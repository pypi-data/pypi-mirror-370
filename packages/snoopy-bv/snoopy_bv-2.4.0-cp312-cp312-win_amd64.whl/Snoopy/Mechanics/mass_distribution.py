from math import isnan
import numpy as np
from Snoopy import logger
from .matrans import matrans3

MINWIDTH = 1.0
TOL = 1e-6


def _check_vector(vec3d):
    vec3d = np.asarray(vec3d)
    if not (len(vec3d.flat) == 3):
        raise TypeError(f"Must enter an vector with 3 components! {vec3d} received")
    return vec3d

def sort(x1: float,x2 : float):
    """Swap x1 and x2 if x1>x2

    Parameters
    ----------
    x1 : float
        first bound
    x2 : float
        second bound

    Returns
    -------
    tuple
        (x1,x2)

    Raises
    ------
    RuntimeError
        x1 = x2
    """
    if abs(x1 - x2)<1e-10:
        raise RuntimeError("Zero size element!")
    elif x1<x2:
        return x1,x2
    else:
        return x2,x1


#---------------------------------------------------------------------------#
#                       MATH OBJECTS                                        #
#---------------------------------------------------------------------------#

class LinearForm:
    """A mathematical object which represent a function y = coef*x + intercept 
    or y = a*x +b

    It compute barycenter if coef and intercept is given, or compute coef and 
    intercept if barycenter is given.
    It compute also the various moments
    """

    def __init__(self,x1,x2):
        """Initialized with bound [x1,x2]

        After, either barycenter or (coef,intercept) must be given
        Parameters
        ----------
        x1 : float
            Inferior bound
        x2 : float
            Superior bound
        """
        self.x1,self.x2 = x1,x2 = sort(x1,x2)
        self._integral      = None
        self._barycenter    = None

    @classmethod
    def solve_for_coef(cls,x1,x2,xg):
        """Given x1,x2, and barycenter, solve for the rest

        Parameters
        ----------
        x1 : float
            Inferior bound
        x2 : float
            Superior bound
        xg : float
            Barycenter

        Returns
        -------
        LinearForm
            completed LinearForm
        """
        obj = cls(x1,x2)
        obj.barycenter = xg
        return obj

    @property
    def barycenter(self) -> float:
        """Return barycenter
        """
        return self._barycenter

    @barycenter.setter
    def barycenter(self,xg):
        """Set barycenter, update/compute the coef/intercept

        Parameters
        ----------
        xg : float
            Barycenter
        """
        self._barycenter = xg
        x1 = self.x1
        x2 = self.x2
        if xg is None:
            xg = (x1+x2)/2
        num = 3*(x1 + x2 - 2*xg)
        denum = (2*(x1*x1+x1*x2+x2*x2)-3*(x1+x2)*xg)
        if abs(num)< TOL:
            self.coef = 0
            self.intercept = 1
            return self
        elif abs(denum)< TOL:
            self.coef = 1
            self.intercept = 0
        else:
            if denum <0:
                self.coef = num/denum
                self.intercept = -1
            else:
                self.coef = -num/denum
                self.intercept = 1
        self._integral  = (self.x2-self.x1)*(self.coef*(self.x1+self.x2)/2 + self.intercept)
        assert self._integral > 0, \
            f"Linear form yield non positive value ({self._integral})! {x1},{x2},{xg}"
        return self

    @classmethod
    def solve_for_barycenter(cls,x1,x2,coef,intercept):
        """Given bound x1,x2 and coef, intercept, solve for barycenter

        Parameters
        ----------
        x1 : float
            Inferior bound
        x2 : float
            Superior bound
        coef : float
            coeffient order 1 = a
        intercept : float
            coeffient order 0 = b
        Returns
        -------
        LinearForm
            completed LinearForm
        """
        obj = cls(x1,x2)
        obj.coef = coef
        obj.intercept = intercept
        if coef == 0:
            obj.barycenter = (x1+x2)/2
        else:
            obj.barycenter = obj.get_moment(1) /obj.get_moment(0) 
        return obj

    @property
    def integral(self) -> float:
        """Integral of y = a*x + b over interval [x1,x2]

        Proportional to the mass
        """
        if self._integral is None:
            self._integral  = (self.x2-self.x1)*(self.coef*(self.x1+self.x2)/2 + self.intercept)
            assert self._integral  > 0, f"Linear form yield non positive value! {self._integral}"
        return self._integral 

    @property
    def start(self) -> float:
        """Returns y1 = a*x1 +b
        """
        return self.coef*self.x1 + self.intercept

    @property
    def end(self) -> float:
        """Returns y2 = a*x2 +b
        """        
        return self.coef*self.x2 + self.intercept

    def integral_xn(self, order) -> float:
        """Compute integral of x^n over interval [x1,x2]
        """
        return (self.x2**(order+1)-self.x1**(order+1))/(order+1) 

    def get_moment(self, order) -> float:
        """Compute moment order n : (a*x + b)x^n over interval [x1,x2]
        """        
        if order < 0:
            raise RuntimeError("Order of moment can't be smaller than 0")
        if order == 0:
            return self.integral        
        val = self.coef*self.integral_xn(order+1)
        if self.intercept != 0:
            val += self.intercept*self.integral_xn(order)
        return val

    def get_normalized_quadratic_moment(self) -> float:
        """The form y = ax + b is undetermined if only barycenter xg is given
        But it is determined if normalized, meaning we divide everything by 
        the integral.
        """
        barycenter = self.barycenter
        val = self.get_moment(2) - 2*barycenter*self.get_moment(1) \
             +barycenter*barycenter*self.get_moment(0)

        return val/self.integral

    def get_normalized_moment(self) -> float:
        """The form y = ax + b is undetermined if only barycenter xg is given
        But it is determined if normalized, meaning we divide everything by 
        the integral.
        """        
        barycenter = self.barycenter
        val = self.get_moment(1) - barycenter*self.get_moment(0) 
        return val/self.integral
    


def calc_gyration(inertia_matrix_at_CoG):
    mass = inertia_matrix_at_CoG[0,0]
    gyration = np.zeros((6,),dtype=float)
    if mass > 1e-10:
        gyration[0] = np.sqrt(inertia_matrix_at_CoG[3,3]/mass)
        gyration[1] = np.sqrt(inertia_matrix_at_CoG[4,4]/mass)
        gyration[2] = np.sqrt(inertia_matrix_at_CoG[5,5]/mass)
        gyration[3] = np.sign(inertia_matrix_at_CoG[3,4])*np.sqrt(np.abs(inertia_matrix_at_CoG[3,4])/mass)
        gyration[4] = np.sign(inertia_matrix_at_CoG[3,5])*np.sqrt(np.abs(inertia_matrix_at_CoG[3,5])/mass)
        gyration[5] = np.sign(inertia_matrix_at_CoG[4,5])*np.sqrt(np.abs(inertia_matrix_at_CoG[4,4])/mass)
    return gyration
#---------------------------------------------------------------------------#
#                       MASS OBJECTS                                        #
#---------------------------------------------------------------------------#

class MassObject:
    """Base class for an object with mass
    """
    def __init__(self, CoG, inertia_matrix, ref_point = None):
        """To be overwritten in child class

        Parameters
        ----------
        CoG : ndarray 
            shape (3,) : Center of gravity
        inertia_matrix : ndarray
            shape (6,6) : inertia matrix at ref_point
        """
        self._CoG                           = _check_vector(CoG)
        if ref_point is None:
            self._ref_point                 = self._CoG 
            self._inertia_matrix_at_CoG     = np.asarray(inertia_matrix)
        else:
            self._ref_point                 = _check_vector(ref_point)
        self._inertia_matrix_at_ref_point   = np.asarray(inertia_matrix)
        

    def get_inertia_matrix_at(self,new_ref):
        new_ref = _check_vector(new_ref)
        return matrans3(self.inertia_matrix_at_CoG,self.CoG ,new_ref)


    @property
    def inertia_matrix(self):
        """Return inertia matrix at ref point

        Returns
        -------
        inertia_matrix : ndarray
            shape (6,6) : inertia matrix at ref_point
        """
        if not hasattr(self,"_inertia_matrix_at_ref_point"):
            self._inertia_matrix_at_ref_point = self.get_inertia_matrix_at(self.ref_point)
        return self._inertia_matrix_at_ref_point

    @property
    def inertia_matrix_at_CoG(self):
        """Return inertia matrix at CoG

        Returns
        -------
        inertia_matrix : ndarray
            shape (6,6) : inertia matrix at ref_point
        """
        if not hasattr(self,"_inertia_matrix_at_CoG"):
            if not hasattr(self,"_inertia_matrix_at_ref_point"):
                raise TypeError("Something wrong: neither inertia_matrix_at_CoG nor "\
                               +"_inertia_matrix_at_ref_point are defined! ")

            self._inertia_matrix_at_CoG = matrans3(self._inertia_matrix_at_ref_point,self.ref_point,self.CoG)
        return self._inertia_matrix_at_CoG

    @property
    def CoG(self):
        """Returns CoG
        """
        return self._CoG
    # Not defined CoG.setter here because we don't want CoG change after initialization!

    @property
    def ref_point(self):
        return getattr(self,"_ref_point",self.CoG)

    def set_ref_point(self,vec):
        """You can change ref_point

        Parameters
        ----------
        vec : _type_
            _description_
        """
        self._ref_point = _check_vector(vec)
        self._inertia_matrix_at_ref_point = self.get_inertia_matrix_at(vec)

    def __eq__(self, other_mass_object):
        """Compare 2 mass objects:
        2 mass object is considered equal if they have same CoG and same inertia matrix

        Parameters
        ----------
        other : MassObject
            Any object of type MassObject

        Returns
        -------
        bool
            Equal or not
        """
        if not isinstance(other_mass_object, MassObject):
            raise TypeError(f"Can't compare a mass object with object type {other_mass_object.__class__}")
        if not np.allclose(self.CoG,other_mass_object.CoG):
            return False
        if np.allclose(self.ref_point,other_mass_object.ref_point):
            return np.allclose(self.inertia_matrix,other_mass_object.inertia_matrix)
        else:
            other_inertia_matrix = other_mass_object.get_inertia_matrix_at(self.ref_point)
            return np.allclose(self.inertia_matrix,other_inertia_matrix)

    def __add__(self, other_mass_object):
        """Add 2 mass objects

        Parameters
        ----------
        other : MassObject
            another mass object

        Returns
        -------
        CollectMassElement
            adding 2 x MassElement will results as a CollectMassElement
            adding a CollectMassElement A with a MassElement B will results 
            as a new CollectMassElement C
            C containing all elements of A and B
        """
        if not isinstance(other_mass_object,MassObject):
            raise TypeError(f"Can't add a {self.__class__.__name__} object to " \
                    +"another object of type {otherMassObject.__class__.__name__}")
        if isinstance(other_mass_object,CollectMassElement):
            return CollectMassElement(self,*other_mass_object._mass_element_list)
        else:
            return CollectMassElement(self,other_mass_object)
        
    

#---------------------------------------------------------------------------#
def legacy_format(mass,x1,x2,xg,yr,zg,solve_now= True,**kwargs):
    """Build object with legacy format

    Parameters
    ----------
    mass : float
        mass
    x1 : float
        start bound x
    x2 : float
        end bound x
    xg : float
        coordinate of center gravity in x axis
    yr : float
        gyration radius in y
    zg : float
        coordinate of center gravity in y axis

    Returns
    -------
    MassElementPonctual or MassElementTriLin
        Built object
    """
    if abs(x1 - x2) < 1e-10:
        if not (x1 <= xg <= x2) :
            raise (ValueError("xg outside of x1,x2" ))
        I44 = I66 = yr**2*mass
        returnobj = MassElementPonctual(mass,xg,0,zg,I44,0,I66,**kwargs)
    else:
        global MINWIDTH
        y = abs(yr) *np.sqrt(3)
        returnobj = MassElementTriLin(mass,x1,x2,xg,-y,y,0,
                    zg-MINWIDTH/2,zg+MINWIDTH/2,zg,solve_now=solve_now,**kwargs)
        #returnobj = MassElementPlan(mass,x1,x2,xg,-y,y,0,zg-MINWIDTH/2,zg+MINWIDTH/2,zg,**kwargs)
    return returnobj


#---------------------------------------------------------------------------#
class MassElementABC(MassObject):
    """A single mass element, corresponding to a line in the .wld file
    """
    def __init__(self,*args,**kwargs):
        raise TypeError("Class {self.__class__} is not supposed to be instantialized")
        
    def cutX(self,X):
        """Cut item at X. Must be defined in child class
        """
        raise TypeError("Can't cut the base element")


    def solve(self):
        """Do the computation to finish object, skip if self.is_solved is True
        """
        if not self.is_solved:
            self._solve()
        self.is_solved = True

    def _solve(self):
        """Actually do the computation here, supposed to be overwritten in child class
        Do nothing if not overwritten
        """        

    @property
    def mass(self):
        if not hasattr(self,"_mass"):
            raise RuntimeError(f"Object {self} mas were not set!")
        return self._mass

    @mass.setter  
    def mass(self,val:float):
        """Set mass as val [kg]

        Parameters
        ----------
        val : float
            Mass in kg
        """
        self._mass = val
 

    def scale_mass(self,val:float):
        """Scale 
        """
        old_mass = self._inertia_matrix_at_CoG[0,0]
        assert  old_mass > 0, "Element with zero mass!"
        if val <= 0:
            raise ValueError("Set mass to zero or negative value!")
        self._inertia_matrix_at_CoG *= val/old_mass


    def translate(self,vec):
        """Translate entirely object in given direction and with given distance(inplace)


        Parameters
        ----------
        distance : ndarray(3,) or list()
            distance
        """
        dx, dy, dz = vec
        self._CoG += np.asarray(vec)
        self.x1 += dx
        self.x2 += dx

        self.y1 += dy
        self.y2 += dy

        self.z1 += dz
        self.z2 += dz
        # Object need to call resolve again to update value
        self.is_solved = False





    @property
    def xg(self) -> float:
        """Return xg
        """
        return self.CoG[0]
    @property
    def yg(self) -> float:
        """Return yg
        """        
        return self.CoG[1]
    @property
    def zg(self) -> float:
        """Return zg
        """          
        return self.CoG[2]
    


    @property
    def gyration(self):
        """Return gyration

        Returns
        -------
        ndarray(6,)
            gyration
        """
        return calc_gyration(self.inertia_matrix_at_CoG)
        

    


    @property
    def inertia_matrix_at_CoG(self):
        """Return inertia matrix at CoG

        Returns
        -------
        ndarray(6,6)
            inertia matrix at CoG
        """        
        if not hasattr(self,"_inertia_matrix_at_CoG"):
            self._inertia_matrix_at_CoG = self.get_inertia_matrix_at_CoG()
        return self._inertia_matrix_at_CoG    



    def get_inertia_matrix_at_CoG(self):
        """Compute inertia matrix at CoG

        Child class must overwrite this method 
        or set directly the value of 
        self._inertia_matrix_at_CoG
        """
        raise NotImplementedError(f"Methode get_inertia_matrix_at_CoG of class "+\
                f"{self.__class__} is not yet implemented")
    



#---------------------------------------------------------------------------#   
class MassElementPonctual(MassElementABC):
    def __init__(self,  mass    : float,
                        xg      : float,
                        yg      : float,
                        zg      : float,
                        I44     : float,
                        I55     : float,
                        I66     : float):
        """Initiator for MassElementPontual

        This class doesn't need to be solved, 
        so method _solve() will never be called.
        Even if it is explicically called, it 
        would do nothing since _solve() of MassElementABC
        does nothing and not overloaded in this class
        Parameters
        ----------
        mass : float
            Mass of object
        xg : float
            x position of ponctual mass
        yg : float
            y position of ponctual mass
        zg : float
            z position of ponctual mass
        I44 : float
            Terms 44 in inertia matrix
        I55 : float
            Terms 55 in inertia matrix
        I66 : float
            Terms 66 in inertia matrix
        """
        self.mass   = mass
        self.x1 = self.x2 = xg
        self.y1 = self.y2 = yg
        self.z1 = self.z2 = zg 
    
        mat = np.zeros((6,6),dtype=float)
        mat[0,0] = mat[1,1] = mat[2,2] = self.mass
        mat[3,3] = I44
        mat[4,4] = I55
        mat[5,5] = I66
        self._inertia_matrix_at_CoG = mat
        self._CoG = np.asarray([xg,yg,zg])
        self.is_solved = True


    def cutX(self, X: float):
        """Cut item at position X.

        Parameters
        ----------
        X : float
            where to cut

        Returns
        -------
        (avant_cut , after_cut)
            Return (None, self) or (self,None) if the cut did not
            actually cut the item
            Return 2 half if the cut does cut the item
        """        
        if self.xg > X:
            return None, self
        
        return self, None




#---------------------------------------------------------------------------#
class MassElementPlan(MassElementABC):
    """ Density function as a plan :   Rho(x,y,z) = ax * x +  ay * y + az * z + b

    Inherited in fortran implementation.
    All the methode here is a tradution of fortran code
    """


    def __init__(self,  mass    : float,
                        x1      : float,
                        x2      : float,
                        xg      : float,
                        y1      : float,
                        y2      : float,
                        yg      : float,
                        z1      : float,
                        z2      : float,
                        zg      : float,
                        solve_now = True):
        """Initiator for MassElementPlan

        Parameters
        ----------
        mass : float
            Mass of object
        x1 : float
            start point of object in x direction
        x2 : float
            end point of object in x direction
        xg : float
            position of gravity center in x direction
        y1 : float
            start point of object in y direction
        y2 : float
            end point of object in y direction
        yg : float
            position of gravity center in x direction
        z1 : float
            start point of object in z direction
        z2 : float
            end point of object in z direction
        zg : float
            position of gravity center in x direction
        """

        #Ajust min distance to avoid numerical error!
        self.x1,self.x2 = self.checkbound(x1,x2)
        self.y1,self.y2 = self.checkbound(y1,y2)
        self.z1,self.z2 = self.checkbound(z1, z2)
        self._CoG = np.asarray([xg,yg,zg])
        self.mass = mass
        self.is_solved = False
        if solve_now:
            self.solve()

    def checkbound(self,x1:float,x2:float):
        """Ajust boundary if x1 is too close to x2

        Inherited from Fortran implementation
        """
        global MINWIDTH
        if x1 > x2 :
            x1,x2 = x2,x1
        if x2 - x1 < MINWIDTH:
            print('Warning: bound ajustment')
            x1,x2 = x1 - 0.5*MINWIDTH, x2 + 0.5*MINWIDTH
        return x1,x2
        

    def _solve(self):
        """Knowing boundary and center of gravity, compute the coefficient of distribution
        """
        
        x1,x2 = self.x1,self.x2
        y1,y2 = self.y1,self.y2
        z1,z2 = self.z1,self.z2
        # Attention: infinite recursion loop if call self.CoG here because 
        # MassElementABC.get_CoG call MassElementABC.solve()
        # -> Use self._CoG instead!
        xg, yg, zg = self._CoG
        m = self.mass
        
        self.b = -(2*m*(3*x2**2*y2**2*z2*zg-6*x1*x2*y2**2*z2*zg+3*x1**2*y2**2*z2*zg  
            - 6*x2**2*y1*y2*z2*zg +12*x1*x2*y1*y2*z2*zg  -6*x1**2*y1*y2*z2*zg  +3*x2**2*y1**2*z2*zg 
            -6*x1*x2*y1**2*z2*zg  +3*x1**2*y1**2*z2*zg  +3*x2**2*y2**2*z1*zg  -6*x1*x2*y2**2*z1*zg 
            +3*x1**2*y2**2*z1*zg  -6*x2**2*y1*y2*z1*zg +12*x1*x2*y1*y2*z1*zg  -6*x1**2*y1*y2*z1*zg 
            +3*x2**2*y1**2*z1*zg  -6*x1*x2*y1**2*z1*zg  +3*x1**2*y1**2*z1*zg  +3*x2**2*y2*yg*z2**2 
            -6*x1*x2*y2*yg*z2**2  +3*x1**2*y2*yg*z2**2  +3*x2**2*y1*yg*z2**2  -6*x1*x2*y1*yg*z2**2 
            +3*x1**2*y1*yg*z2**2  +3*x2*xg*y2**2*z2**2  +3*x1*xg*y2**2*z2**2  -5*x2**2*y2**2*z2**2 
            +4*x1*x2*y2**2*z2**2  -5*x1**2*y2**2*z2**2  -6*x2*xg*y1*y2*z2**2  -6*x1*xg*y1*y2*z2**2 
            +4*x2**2*y1*y2*z2**2  +4*x1*x2*y1*y2*z2**2  +4*x1**2*y1*y2*z2**2  +3*x2*xg*y1**2*z2**2 
            +3*x1*xg*y1**2*z2**2  -5*x2**2*y1**2*z2**2  +4*x1*x2*y1**2*z2**2  -5*x1**2*y1**2*z2**2 
            -6*x2**2*y2*yg*z1*z2 +12*x1*x2*y2*yg*z1*z2  -6*x1**2*y2*yg*z1*z2  -6*x2**2*y1*yg*z1*z2 
            +12*x1*x2*y1*yg*z1*z2  -6*x1**2*y1*yg*z1*z2  -6*x2*xg*y2**2*z1*z2  -6*x1*xg*y2**2*z1*z2 
            +4*x2**2*y2**2*z1*z2  +4*x1*x2*y2**2*z1*z2  +4*x1**2*y2**2*z1*z2 +12*x2*xg*y1*y2*z1*z2 
            +12*x1*xg*y1*y2*z1*z2  +4*x2**2*y1*y2*z1*z2 -32*x1*x2*y1*y2*z1*z2  +4*x1**2*y1*y2*z1*z2 
            -6*x2*xg*y1**2*z1*z2  -6*x1*xg*y1**2*z1*z2  +4*x2**2*y1**2*z1*z2  +4*x1*x2*y1**2*z1*z2 
            +4*x1**2*y1**2*z1*z2  +3*x2**2*y2*yg*z1**2  -6*x1*x2*y2*yg*z1**2  +3*x1**2*y2*yg*z1**2 
            +3*x2**2*y1*yg*z1**2  -6*x1*x2*y1*yg*z1**2  +3*x1**2*y1*yg*z1**2  +3*x2*xg*y2**2*z1**2 
            +3*x1*xg*y2**2*z1**2  -5*x2**2*y2**2*z1**2  +4*x1*x2*y2**2*z1**2  -5*x1**2*y2**2*z1**2 
            -6*x2*xg*y1*y2*z1**2  -6*x1*xg*y1*y2*z1**2  +4*x2**2*y1*y2*z1**2  +4*x1*x2*y1*y2*z1**2 
            +4*x1**2*y1*y2*z1**2  +3*x2*xg*y1**2*z1**2  +3*x1*xg*y1**2*z1**2  -5*x2**2*y1**2*z1**2 
            +4*x1*x2*y1**2*z1**2  -5*x1**2*y1**2*z1**2) ) / ((x2-x1)**3*(y2-y1)**3*(z2-z1)**3)
        #print('B:',self.b)
        self.ax = m*(6*(2*xg-x2-x1))/((x2-x1)**3*(y2-y1)*(z2-z1))
        self.ay = m*(6*(2*yg-y2-y1))/((x2-x1)*(y2-y1)**3*(z2-z1))
        self.az = m*(6*(2*zg-z2-z1))/((x2-x1)*(y2-y1)*(z2-z1)**3)

        self.is_solved = True

    def _impose_coef(self,ax:float,ay:float,az:float,b:float):
        """Knowing boundary and the coefficient of distribution, compute CoG
        """
        self.ax = ax
        self.ay = ay
        self.az = az
        self.b  = b
        self._CoG = self.compute_CoG(ax,ay,az,b,self.x1,self.x2,self.y1,self.y2,self.z1,self.z2)
        self.is_solved = True
    
    def _copy_coef(self,other_mass_element_plan):
        """Copy coefficient from other to self

        Parameters
        ----------
        other : MassElementPlan
            another object MassElementPlan
        """
        assert isinstance(other_mass_element_plan,MassElementPlan)
        self.ax = other_mass_element_plan.ax
        self.ay = other_mass_element_plan.ay
        self.az = other_mass_element_plan.az
        self.b  = other_mass_element_plan.b
        self.is_solved = True     
    
    def cutX(self,X:float):
        """Cut item at X.

        Parameters
        ----------
        X : float
            where to cut

        Returns
        -------
        (avant_cut , after_cut)
            Return (None, self) or (self,None) if the cut did not
            actually cut the item
            Return 2 half if the cut does cut the item
        """
        if self.x1 >= X:
            return None, self
        if self.x2 <  X:
            return self,None
        
        ys1,ys2 = self.y1,self.y2
        zs1,zs2 = self.z1,self.z2
        amont = self.new_bound(self.x1,X,ys1,ys2,zs1,zs2)
        aval  = self.new_bound(X,self.x2,ys1,ys2,zs1,zs2)
        return amont,aval

    @staticmethod
    def compute_CoG(ax:float,ay:float,az:float,b:float,
                    xs1:float,xs2:float,ys1:float,ys2:float,
                    zs1:float,zs2:float):
        """Compute and returns CoG for a generic case, knowing bounds and coefficients
        """
        xgs = ( 3*az*xs2*zs2+3*az*xs1*zs2+3*az*xs2*zs1+3*az*xs1*zs1    
              + 3*ay*xs2*ys2+3*ay*xs1*ys2+3*ay*xs2*ys1+3*ay*xs1*ys1    
              + 4*ax*xs2**2+4*ax*xs1*xs2+6*b*xs2+4*ax*xs1**2+6*b*xs1     
              )/(6*(az*zs2+az*zs1+ay*ys2+ay*ys1+ax*xs2+ax*xs1+2*b) )
              
        ygs = ( 3*az*ys2*zs2+3*az*ys1*zs2+3*az*ys2*zs1+3*az*ys1*zs1     
              +4*ay*ys2**2+4*ay*ys1*ys2+3*ax*xs2*ys2+3*ax*xs1*ys2      
              +6*b*ys2+4*ay*ys1**2+3*ax*xs2*ys1+3*ax*xs1*ys1+6*b*ys1 
              )/ (6*(az*zs2+az*zs1+ay*ys2+ay*ys1+ax*xs2+ax*xs1+2*b) )
        zgs = ( 4*az*zs2**2+4*az*zs1*zs2+3*ay*ys2*zs2+3*ay*ys1*zs2             
              +3*ax*xs2*zs2+3*ax*xs1*zs2+6*b*zs2+4*az*zs1**2                   
              +3*ay*ys2*zs1+3*ay*ys1*zs1+3*ax*xs2*zs1+3*ax*xs1*zs1+6*b*zs1
              ) / (6*(az*zs2+az*zs1+ay*ys2+ay*ys1+ax*xs2+ax*xs1+2*b) )
        return np.asarray([xgs,ygs,zgs])

    def new_bound(self,xs1:float,xs2:float,ys1:float,
                  ys2:float,zs1:float,zs2:float):
        """Create a new element with same coefficients but different bound

        Returns
        -------
        MassElementPlan
            newly constructed element (same class as self)
        """
        ax,ay,az,b = self.az,self.ay,self.az,self.b
        xgs,ygs,zgs = self.compute_CoG(ax,ay,az,b,xs1,xs2,ys1,ys2,zs1,zs2)
        massSect = ((xs2-xs1)*(ys2-ys1)*(zs2-zs1)*\
                (az*zs2+az*zs1+ay*ys2+ay*ys1+ax*xs2+ax*xs1+2*b))/2
        return MassElementPlan(massSect,xs1,xs2,xgs,ys1,ys2,ygs,zs1,zs2,zgs)

    def _get_inertia_diagonal_term(self,ax:float,ay:float,az:float,b:float,
                        xs1:float,xs2:float,ys1:float,ys2:float,
                        zs1:float,zs2:float, yg:float, zg:float):   
        """Compute the element on the diagonal of the inertia matrix

        Returns
        -------
        float
            I44 or I55 or I66, depending on situtation
        """
        return ( (xs2-xs1)*(ys2-ys1)*(zs2-zs1)*(
        3*az*zs2**3+3*az*zs1*zs2**2 
        -8*az*zg*zs2**2   +2*ay*ys2*zs2**2  +2*ay*ys1*zs2**2  
        +2*ax*xs2*zs2**2  +2*ax*xs1*zs2**2  +4*b*zs2**2      
        +3*az*zs1**2*zs2  -8*az*zg*zs1*zs2  +2*ay*ys2*zs1*zs2 
        +2*ay*ys1*zs1*zs2 +2*ax*xs2*zs1*zs2 +2*ax*xs1*zs1*zs2 
        +4*b*zs1*zs2      +6*az*zg**2*zs2   -6*ay*ys2*zg*zs2  
        -6*ay*ys1*zg*zs2  -6*ax*xs2*zg*zs2  -6*ax*xs1*zg*zs2  
        -12*b*zg*zs2       +2*az*ys2**2*zs2  +2*az*ys1*ys2*zs2 
        -6*az*yg*ys2*zs2  +2*az*ys1**2*zs2  -6*az*yg*ys1*zs2  
        +6*az*yg**2*zs2   +3*az*zs1**3      -8*az*zg*zs1**2   
        +2*ay*ys2*zs1**2  +2*ay*ys1*zs1**2  +2*ax*xs2*zs1**2  
        +2*ax*xs1*zs1**2  +4*b*zs1**2       +6*az*zg**2*zs1   
        -6*ay*ys2*zg*zs1  -6*ay*ys1*zg*zs1  -6*ax*xs2*zg*zs1  
        -6*ax*xs1*zg*zs1 -12*b*zg*zs1       +2*az*ys2**2*zs1  
        +2*az*ys1*ys2*zs1 -6*az*yg*ys2*zs1  +2*az*ys1**2*zs1  
        -6*az*yg*ys1*zs1  +6*az*yg**2*zs1   +6*ay*ys2*zg**2   
        +6*ay*ys1*zg**2   +6*ax*xs2*zg**2   +6*ax*xs1*zg**2   
        +12*b*zg**2        +3*ay*ys2**3      +3*ay*ys1*ys2**2  
        -8*ay*yg*ys2**2   +2*ax*xs2*ys2**2  +2*ax*xs1*ys2**2  
        +4*b*ys2**2       +3*ay*ys1**2*ys2  -8*ay*yg*ys1*ys2  
        +2*ax*xs2*ys1*ys2 +2*ax*xs1*ys1*ys2 +4*b*ys1*ys2      
        +6*ay*yg**2*ys2   -6*ax*xs2*yg*ys2  -6*ax*xs1*yg*ys2  
        -12*b*yg*ys2       +3*ay*ys1**3      -8*ay*yg*ys1**2   
        +2*ax*xs2*ys1**2  +2*ax*xs1*ys1**2  +4*b*ys1**2       
        +6*ay*yg**2*ys1   -6*ax*xs2*yg*ys1  -6*ax*xs1*yg*ys1  
        -12*b*yg*ys1       +6*ax*xs2*yg**2   +6*ax*xs1*yg**2   
        +12*b*yg**2) ) /12

    def _get_inertia_cross_term(self,ax:float,ay:float,az:float,b:float,xs1:float,xs2:float,
                         ys1:float,ys2:float,zs1:float,zs2:float, xg:float, yg:float):
        """Compute the element outside of the diagonal of the inertia matrix

        Returns
        -------
        float
            I45 or I56 or I64, depending on situation
        """        
        return -( (xs2-xs1)*(ys2-ys1)*(zs2-zs1) 
       *(  3*az*xs2*ys2*zs2  +3*az*xs1*ys2*zs2  -6*az* xg*ys2*zs2 
          +3*az*xs2*ys1*zs2  +3*az*xs1*ys1*zs2  -6*az* xg*ys1*zs2 
          -6*az*xs2*yg *zs2  -6*az*xs1*yg *zs2 +12*az* xg*yg *zs2 
          +3*az*xs2*ys2*zs1  +3*az*xs1*ys2*zs1  -6*az* xg*ys2*zs1 
          +3*az*xs2*ys1*zs1  +3*az*xs1*ys1*zs1  -6*az* xg*ys1*zs1 
          -6*az*xs2*yg *zs1  -6*az*xs1*yg *zs1 +12*az* xg*yg *zs1 
          +4*ay*xs2*ys2**2   +4*ay*xs1*ys2**2   -8*ay* xg*ys2**2  
          +4*ay*xs2*ys1*ys2  +4*ay*xs1*ys1*ys2  -8*ay* xg*ys1*ys2 
          -6*ay*xs2*yg *ys2  -6*ay*xs1*yg *ys2 +12*ay* xg*yg *ys2 
          +4*ax*xs2**2 *ys2  +4*ax*xs1*xs2*ys2  -6*ax* xg*xs2*ys2 
          +6* b*xs2*ys2      +4*ax*xs1**2*ys2   -6*ax* xg*xs1*ys2 
          +6* b*xs1*ys2     -12* b* xg*ys2      +4*ay*xs2*ys1**2  
          +4*ay*xs1*ys1**2   -8*ay* xg*ys1**2   -6*ay*xs2*yg *ys1 
          -6*ay*xs1* yg*ys1 +12*ay* xg*yg *ys1  +4*ax*xs2**2 *ys1 
          +4*ax*xs1*xs2*ys1  -6*ax* xg*xs2*ys1  +6* b*xs2*ys1     
          +4*ax*xs1**2 *ys1  -6*ax* xg*xs1*ys1  +6* b*xs1*ys1     
         -12* b*xg*ys1       -8*ax* xs2**2*yg   -8*ax*xs1*xs2*yg  
         +12*ax*xg*xs2*yg   -12*b*xs2*yg        -8*ax*xs1**2 *yg  
         +12*ax*xg*xs1*yg   -12*b*xs1*yg       +24* b*xg*yg) ) / 24

    def get_inertia_matrix_at(self,ref_point):   
        """Compute inertia matrix at given point

        Parameters
        ----------
        ref_point : ndarray 
            shape (3,) : point where we want to compute inertia matrix 

        Returns
        -------
        inertia_matrix : ndarray
            shape (6,6) : inertia matrix at CoG 
        """
        mass = self.mass
        inertia = np.zeros((6,6),dtype=float)
        CoG = self.CoG
        ref_Point = np.asarray(ref_point)
        inertia[0,0] = inertia[1,1] = inertia[2,2] = mass

        inertia[4,0] = inertia[0,4] = mass*(CoG[2]-ref_point[2])
        inertia[5,1] = inertia[1,5] = mass*(CoG[0]-ref_point[0])
        inertia[3,2] = inertia[2,3] = mass*(CoG[1]-ref_point[1])

        inertia[5,0] = inertia[0,5] = -mass*(CoG[1]-ref_point[1])
        inertia[3,1] = inertia[1,3] = -mass*(CoG[2]-ref_point[2])
        inertia[4,2] = inertia[2,4] = -mass*(CoG[0]-ref_point[0])

        inertia[3,3] = self._get_inertia_diagonal_term( 
                      self.ax, self.ay, self.az, self.b, 
                      self.x1, self.x2,  
                      self.y1, self.y2,
                      self.z1, self.z2,
                      ref_point[1], ref_point[2])
        inertia[4,4] = self._get_inertia_diagonal_term( 
                      self.ay, self.az, self.ax, self.b, 
                      self.y1, self.y2,  
                      self.z1, self.z2,
                      self.x1, self.x2,
                      ref_point[2], ref_point[0])

        inertia[5,5] = self._get_inertia_diagonal_term( 
                      self.az, self.ax, self.ay, self.b, 
                      self.z1, self.z2,  
                      self.x1, self.x2,
                      self.y1, self.y2,
                      ref_point[0], ref_point[1])         

        inertia[3,4] = inertia[4,3] = self._get_inertia_cross_term( 
                      self.ax, self.ay, self.az, self.b, 
                      self.x1, self.x2,  
                      self.y1, self.y2,
                      self.z1, self.z2,
                      ref_point[0], ref_point[1])

        inertia[4,5] = inertia[5,4] = self._get_inertia_cross_term( 
                      self.ay, self.az, self.ax, self.b, 
                      self.y1, self.y2,  
                      self.z1, self.z2,
                      self.x1, self.x2,
                      ref_point[1], ref_point[2])

        inertia[5,3] = inertia[3,5] = self._get_inertia_cross_term( 
                      self.az, self.ax, self.ay, self.b, 
                      self.z1, self.z2,  
                      self.x1, self.x2,
                      self.y1, self.y2,
                      ref_point[2], ref_point[0])                                      
        return inertia
    def get_inertia_matrix_at_CoG(self):
        return self.get_inertia_matrix_at(self.CoG)
#---------------------------------------------------------------------------#


#---------------------------------------------------------------------------#
class MassElementTriLin(MassElementABC):
    """Describe MassElement with a mass distribution trilinear

    rho = (a1.x + b1)(a2.y + b2)(a3.z + b3)

    """
    linearName = ["linear_x","linear_y","linear_z"]
    def __init__(self,  mass    : float,
                        x1      : float,
                        x2      : float,
                        xg      : float,
                        y1      : float,
                        y2      : float,
                        yg      : float,
                        z1      : float,
                        z2      : float,
                        zg      : float,
                        solve_now = True):
        """Initiator for MassElementTriLin

        Parameters
        ----------
        mass : float
            Mass of object
        x1 : float
            start point of object in x direction
        x2 : float
            end point of object in x direction
        xg : float
            position of gravity center in x direction
        y1 : float
            start point of object in y direction
        y2 : float
            end point of object in y direction
        yg : float
            position of gravity center in x direction
        z1 : float
            start point of object in z direction
        z2 : float
            end point of object in z direction
        zg : float
            position of gravity center in x direction
        zfsurface: float
            offset in z direction
        solve_now : logical
            If solve_now: do the resolution
            Else: wait!

        """

        #Ajust min distance to avoid numerical error!
        self.x1,self.x2 = self.checkbound(x1,x2)
        self.y1,self.y2 = self.checkbound(y1,y2)
        self.z1,self.z2 = self.checkbound(z1,z2)
        self._CoG = np.asarray([xg,yg,zg])
        self.mass = mass
        
        self.linear_x       = None
        self.linear_y       = None
        self.linear_z       = None
        self.is_solved      = False
        self.can_be_solved  = True
        if solve_now:  
            self.solve()

    @classmethod
    def partial_init(cls):
        obj = cls.__new__(cls)
        obj.linear_x = None
        obj.linear_y = None
        obj.linear_z = None
        obj.is_solved = False   
        obj.can_be_solved = False

        return obj

    def checkbound(self,x1:float,x2:float):
        """Same as MassElementPlan.checkbound but ajustment 
        is not needed. We simply check order here        
        """
        return sort(x1,x2)


    def _solve(self):
        """Knowing all the bound and position of CoG, solve for the coefficients
        """
        # Attention: infinite recursion loop if call self.CoG here because 
        # MassElementABC.get_CoG call MassElementABC.solve()
        # -> Use self._CoG instead!
        if not self.can_be_solved:
            raise RuntimeError(f"CoG is not yet know at this point")
        xg, yg, zg = self._CoG
        self.linear_x = LinearForm.solve_for_coef(self.x1, self.x2 , xg)
        self.linear_y = LinearForm.solve_for_coef(self.y1, self.y2 , yg)
        self.linear_z = LinearForm.solve_for_coef(self.z1, self.z2 , zg)
        self.factor = self.mass/(\
            self.linear_x.integral*self.linear_y.integral*self.linear_z.integral)
        self.get_inertia_matrix_at_CoG()
        self.is_solved = True
    @property
    def CoG(self):
        """Update CoG form 3 linear form
        """
        self.solve()
        self._update_CoG()
        return self._CoG

    def _update_CoG(self):
        """Collect CoG from 3 linears forms
        """
        self._CoG = np.asarray([self.linear_x.barycenter,
                        self.linear_y.barycenter,
                        self.linear_z.barycenter])
    def get_inertia_matrix_at_CoG(self):
        """Compute the inertia mass matrix
        at CoG after solving for CoG or for coefficients

        Returns
        -------
        ndarray(6,6)
            inertia mass at CoG
        """
        val = np.zeros((6,6),dtype=float)
        val[0,0] = val[1,1] = val[2,2] = self.mass
        IQx = self.mass*self.linear_x.get_normalized_quadratic_moment()
        IQy = self.mass*self.linear_y.get_normalized_quadratic_moment()
        IQz = self.mass*self.linear_z.get_normalized_quadratic_moment()
        Ix = self.linear_x.get_normalized_moment()
        Iy = self.linear_y.get_normalized_moment()
        Iz = self.linear_z.get_normalized_moment()
        #print('Ix,Iy,Iz:',Ix,Iy,Iz)
        #print('IQx,IQy,IQz:',IQx,IQy,IQz)

        val[3,3] = IQy + IQz
        val[4,4] = IQx + IQz
        val[5,5] = IQx + IQy
        val[3,4] = val[4,3] = - self.mass *Ix*Iy
        val[4,5] = val[5,4] = - self.mass *Iy*Iz
        val[5,3] = val[3,5] = - self.mass *Iz*Ix
        self._inertia_matrix_at_CoG = val
        return val

    def _solve_with_intial_condition(self,startX:float):
        """ Solve with given initial condition 
        
        Given "startX" as an rho(x1)
        Compute the slope and intercept of X such as the total mass is 
        satisfied.
        Integration over mass distribution yield
        IntY*IntZ*(X2-X1)*(slope_x *(X1+X2)/2 +intercept) = mass
        So:
        slope_x * (X1+X2)/2 + intercept = mass/(IntY*IntZ*(X2-X1))   [1]
        Intial condition:
        slope_x * X1 + intercept = startX                            [2]
        Subtract [1] - [2] yield: 
        slope_x * (X2 - X1)/2 = mass/(IntY*IntZ*(X2-X1)) - startX
        So:
        slope_x = (mass/(IntY*IntZ*(X2-X1)) - startX)*2/(X2 - X1)
        intercept = startX - slope_x*X1
        """
        xg, yg, zg = self._CoG
        self.linear_y = LinearForm.solve_for_coef(self.y1, self.y2 , yg)
        self.linear_z = LinearForm.solve_for_coef(self.z1, self.z2 , zg)
        
        self.factor = 1
        x1 = self.x1
        x2 = self.x2
        total = self.mass/(self.linear_y.integral*self.linear_z.integral*(x2-x1))
        slope_x = (total - startX)*2/(x2-x1)
        intercept_x = startX - self.slope_x*x1
        self.linear_x = LinearForm.solve_for_barycenter(x1,x2,slope_x,intercept_x)
        self.can_be_solved  = True
        self.is_solved      = True

    @property
    def startX(self):
        """Distribution of mass at the begining of x"""
        return self.linear_x.start*self.factor

    @property
    def endX(self):
        """Distribution of mass at the end of x"""
        return self.linear_x.end*self.factor

    def cutX(self,X:float):
        """Cut item at X.

        Parameters
        ----------
        X : float
            where to cut

        Returns
        -------
        (avant_cut , after_cut)
            Return (None, self) or (self,None) if the cut did not
            actually cut the item
            Return 2 half if the cut does cut the item
        """        
        if self.x1 >= X:
            return None, self
        elif self.x2 <= X:
            return self,None
        else:
            item1 = self.new_bound(self.x1,X)
            item2 = self.new_bound(X,self.x2)
            return item1,item2
    
    def new_bound(self,x1:float,x2:float):
        """Create a new element with same coefficients but different bound

        Returns
        -------
        MassElementPlan
            newly constructed element (same class as self)
        """        
        obj = self.partial_init()
        obj.x1 = x1
        obj.x2 = x2
        obj.y1 = self.y1
        obj.y2 = self.y2
        obj.z1 = self.z1
        obj.z2 = self.z2
        obj.linear_x = LinearForm.solve_for_barycenter(obj.x1, obj.x2 , 
                            self.linear_x.coef,self.linear_x.intercept)
        obj.linear_y = self.linear_y
        obj.linear_z = self.linear_z
        obj.factor  = self.factor
        # Update new mass and mass matrix
        obj.mass = obj.factor*(\
            obj.linear_x.integral*obj.linear_y.integral*obj.linear_z.integral)

        # Now the new object "obj" is fully operational:
        obj.can_be_solved = True
        # This object is already have all the coefficient set, no need to solve
        # for coefficient, only need to update CoG
        obj._update_CoG
        obj.is_solved = True
        # Set ref_point if needed
        if hasattr(self,"_ref_point"):
            obj.ref_point = self._ref_point

        return obj





def read_hstar_mass_item( line ):
    """Create mass element from Hstar format (single line)
    """
    line_splitted = line.split()
    
    ID = line_splitted[0]
   
    description = line_splitted[1].lower()
    
    mass_data = [float(s) for s in line_splitted[2:]]
    
    if description == "point":
        return MassElementPonctual(*mass_data)
    elif description in ["plan","lin3d"]:
        return MassElementPlan(*mass_data)
    elif description == "trilin":
        return MassElementTriLin(*mass_data)
    elif description == "trilincont":
        return MassElementTriLinCont(*mass_data)
    else:
        return legacy_format( *[float(s) for s in line_splitted[-6:]] )
       

#---------------------------------------------------------------------------#
#                       COLLECTION OF MASS OBJECTS                          #
#---------------------------------------------------------------------------#
class CollectMassElement(MassObject):
    """Contain list of mass element, can be any derivation of MassElementABC
    """
    def __init__(self, *list_element):
        """Provide a list of element at initialisation

        list_element can be empty, so the collection is an empty list
        """
        self._mass_element_list = []        
        for item in list_element:
            self.add_element(item)
            
            
    @staticmethod
    def from_wld( filename, include_zfs = True ) :
        """Construct mass distribution from HydroStar file format.
        """
        import re

        with open(filename,"r") as f:
            buf = f.read()
            content = "\n".join( [ s.strip() for s in buf.splitlines() if not s.startswith("#")] )


        zfsurface = 0.0
        for matches in re.finditer(r"^ZFSURFACE(.*?)\n", content, re.DOTALL):
            zfsurface_str = matches.group().split()
            zfsurface = float(zfsurface_str[1])


        #-----------------------> Parse wld file : parse mass element and construct object
        collect_element = CollectMassElement()
        element_continue  = None
        for matches in re.finditer(r"^DISMASS(.*?)^ENDDISMASS", content, re.MULTILINE | re.DOTALL):
            lines = matches.group(0).splitlines()
            for line in lines[1:-1]:
                try : 
                    element = read_hstar_mass_item( line )
                except ValueError as e :
                    logger.error(f"Problem with mass item\n{line:}\n")
                    raise(e)
                if include_zfs :
                    element.translate([0,0,-zfsurface])

                if isinstance(element,MassElementTriLinCont):
                    if element_continue is None:
                        element_continue = element
                        collect_element.add_element(element_continue)
                    else:
                        element_continue += element
                else:
                    collect_element.add_element(element)
                    
        if len( collect_element._mass_element_list ) == 0:
            raise(Exception(f"Error file {filename:} does not contains any mass item..."))
                    
        if include_zfs :
            return collect_element
        else: 
            return collect_element, zfsurface

    def plot(self, ax=None, n = 200) :
        from matplotlib import pyplot as plt
        if ax is None : 
            fig, ax = plt.subplots()

        l = self.x2 - self.x1
        x_range = np.linspace(self.x1-0.05*l, self.x2+0.05*l , n)
        dx = x_range[1] - x_range[0]
        x_centers = 0.5*(x_range[:-1]+x_range[1:])
        m, z =  [], []
        for x in x_range[:-1] :
            cut_between = self.cut_seg(x, x+dx)
            if cut_between is not None : 
                m.append( cut_between.mass )
                z.append( cut_between.CoG[2] )
            else : 
                m.append( 0.0 )
                z.append( np.nan )
                
        ax.plot( x_centers, m / dx, label = r"$\rho$" )
        ax.legend()
        ax_z = ax.twinx()
        ax_z.plot( x_centers, z, color = "orange", label = "Zg" )
        ax_z.set(ylabel = "Zg (m)" )
        ax_z.legend()
        ax.set(ylim = [0. , None], xlabel = "x (m)", ylabel = r"$\rho$" )
        return ax



    def add_element(self, mass_element:MassElementABC):
        """Add new element (elem) in to _mass_element_list

        Do the type check of elem
        Do nothing if elem is None

        Parameters
        ----------
        mass_element : MassObject
            mass object to be aded
        """
        if mass_element is not None:
            assert isinstance(mass_element, MassElementABC)
            self._mass_element_list.append(mass_element)


    def __add__(self,other):
        """Add a collection with a element or another collection

        A new objet CollectMassElement will be created, containing 
        all elements of self and other (Newly created element will 
        contain 'other' if 'other' is an MassElement)

        Parameters
        ----------
        other : CollectMassElement or MassElement
            To be added with self

        Returns
        -------
        CollectMassElement
            Sum of self with other
        """
        if isinstance(other,CollectMassElement):
            return  CollectMassElement(*self._mass_element_list,
                                       *other._mass_element_list)
        elif isinstance(other,MassElementABC):
            return CollectMassElement(*self._mass_element_list,other)
        else:
            raise TypeError(f"Can't add a object {self.__class__.__name__} "\
                            +"to another object of type {other.__class__.__name__}")            

    def __iadd__(self,other):
        """Add a collection with a element or another collection.

        Same as __add__ but no new object is created.
        Element from 'other' (or 'other') will just simply be
        appended in list _mass_element_list of object 'self '

        Parameters
        ----------
        other : CollectMassElement or MassElement
            To be added with self

        Returns
        -------
        CollectMassElement
           self
        """        
        if isinstance(other,CollectMassElement):
            for item in other._mass_element_list:
                self.add_element(item)
        elif isinstance(other,MassElementABC):
            self.add_element(other)
        else:
            raise TypeError(f"Can't add a object {self.__class__.__name__} "\
                            +"to another object of type {other.__class__.__name__}")

    def cut_seg( self, x_min, x_max ):
        fore = self.cutX(x_max)[0]
        if fore is None :
            return None
        seg = fore.cutX(x_min)[1]
        if seg is None : 
            return None
        return seg

    def cutX(self,X : float):
        """Cut the collection at position X.

        Will perform the cut for all the element in _mass_element_list 
        and collect the corresponding results
        Parameters
        ----------
        X : float
            where to cut

        Returns
        -------
        (avant_cut , after_cut)
            Return (None, self) or (self,None) if the cut did not
            actually cut the item
            Return 2 half if the cut does cut the item
        """            
        if self.x1 >= X:
            return None, self
        elif self.x2 <= X:
            return self,None
        else:
            amont = self.__class__()
            aval = self.__class__()
            _mass_element_list = self._mass_element_list
            for ii in range(len(_mass_element_list)):
                item = _mass_element_list[ii]
                item1,item2 = item.cutX(X)
                amont.add_element(item1)
                aval.add_element(item2)
            return amont,aval

    @property
    def mass(self):
        """Return Mass

        Do the sum of mass over all element in _mass_element_list

        Returns
        -------
        float
            mass
        """
        val = 0
        for ii,item in  enumerate(self._mass_element_list):
            val += item.mass
        return val

    @property
    def CoG(self):
        """Returns the CoG

        Do the weighted sum of all CoG over all element in _mass_element_list

        Returns
        -------
        ndarray(3,)
            CoG
        """        
        val = np.zeros((3,),dtype=float)
        mass = 0
        if len(self._mass_element_list)==0:
            return val
        for item in  self._mass_element_list:
            mass += item.mass 
            val  += item.mass*item.CoG
        return val/mass

    def get_inertia_matrix_at(self,ref_point):
        """Compute inertia matrix at given point
        
        Parameters
        ----------
        ref_point : ndarray 
            shape (3,) : point where we want to compute inertia matrix 

        Returns
        -------
        inertia_matrix : ndarray
            shape (6,6) : inertia matrix at CoG 
        """
        ref_point = _check_vector(ref_point)
        inertia_matrix = np.zeros((6,6))
        for item in self._mass_element_list:
            elem_inertia_matrix = item.get_inertia_matrix_at(ref_point)
            inertia_matrix += elem_inertia_matrix 
        return inertia_matrix

    def get_inertia_matrix_at_CoG(self): 
        return self.get_inertia_matrix_at(self.CoG)



    @property
    def x1(self) -> float:
        """Return the inferior bound of the collection

        Used to detect if the cut is actually cut the collection or not
        """
        return np.min([item.x1 for item in self._mass_element_list])

    @property
    def x2(self) -> float:
        """Return thesuperior bound of the collection

        Used to detect if the cut is actually cut the collection or not
        """        
        return np.max([item.x2 for item in self._mass_element_list])
                

    @property
    def gyration(self):
        """Return gyration

        Returns
        -------
        ndarray(6,)
            gyration
        """
        
        return calc_gyration(self.get_inertia_matrix_at_CoG())
        
#---------------------------------------------------------------------------#
class MassElementTriLinCont(CollectMassElement,MassElementABC):
    """Special kind of element, containing a list of element

    The idea is to group a number of segments like mass distribution, and force 
    the continuity between the segment
    """

    def __init__(self,*args,**kwargs):
        """Initialisation

        Here the initialization is a little bit tricky.
        We would like to initialize as a mix between MassElement
        and CollectMassElement.
        We received some amount of data from args, we use it to 
        build an MassElementTriLin, then we add it to MassElementTriLinCont

        Later we will simply concatenate of _mass_element_list of all 
        the MassElementTriLinCont
        """
        self._mass_element_list = []
        self.lastX = None
        if len(args) == 0:
            return
        args = list(args)
        mass = args.pop(0)
        x1 = args.pop(0)
        x2 = args.pop(0)
        if len(args) == 6:
            item = MassElementTriLin(mass,x1,x2,None,*args,solve_now=False,**kwargs)
        elif len(args) == 7:
            item = MassElementTriLin(mass,x1,x2,*args,solve_now=False,**kwargs)
        else:
            raise RuntimeError(f"Invalid format for {self.__class__}, expect 8 or 9 inputs,"\
                             + f" but {len(args)} received")

        self.add_element(item)

        
    
    def find_first_id(self):
        """The continuity is not guaranted to be in correct order
        We need this function and function __next__ to find correctly 
        loop over all the sub-element, in continous order

        Returns
        -------
        int
            ID of element with x1 smallest, it must be the first element of 
            the list
        """
        min_x1 = self._mass_element_list[0].min_x1 
        first_id = 0
        for ii,item in enumerate(self._mass_element_list):
            if item.x1 < min_x1:
                min_x1 = item.x1
                first_id = ii
        return first_id

    def __iter__(self):
        """Initialize the loop
        """
        self.lastX = None
        return self
        
    def __next__(self):
        """Find the next element in the list

        Returns
        -------
        MassElementTriLin
            Next element in the list

        Raises
        ------
        StopIteration
            When run out of element
        """
        if self.lastX is None:
            return_elem = self._mass_element_list[self.find_first_id()]
            self.lastX = return_elem.x2
            return return_elem
        for item in self._mass_element_list:
            if abs(item.x1 - self.lastX)<1e-6:
                self.lastX = item.x2
                return item
        raise StopIteration               

    def _solve(self):
        """ Solve

        We have 2 cases for the first element:
        - If the first element is given an CoG in X: we solve it normally, 
          which mean we know all x1, x2, xg, y1, y2, yg, z1, z2, zg, we solve
          for coefficients.
        - If the first element is not given the CoG, we still give it a value 
          as None, so that the actual value in matrix would be nan
          We need to detect if xg is nan, in this case we force the mass 
          distribution of first element to ramp up, starting at 0
        From the second element, xg would be ignored!

        After solving the first element, we use last value of distribution as 
        initial condition to solve for the next distribution

        """
        previous_coef = 0
        for ii,elem in enumerate(self):
            if ii == 0:
                if isnan(elem._CoG[0]):
                    elem._solve_with_intial_condition(previous_coef)
                else:
                    elem._solve()
            elem._solve_with_intial_condition(previous_coef)
            previous_coef = elem.endX
        self.is_solved = True
