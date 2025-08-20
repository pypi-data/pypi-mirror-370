from scipy.optimize import fsolve
from Snoopy import Meshing as msh
from Snoopy import Geometry as geo
import numpy as np
from Snoopy import logger
from Snoopy.Tools import clean_comment_lines

class MeshBalance( object ):
    def __init__(self, mesh , mass , CoG , rho = 1025, rCenter = [0.,0.,0.], x0 = None, forceSymmetry = None) :
        """Create instance to balance a mesh.

        Parameters
        ----------
        mesh : msh.Mesh
            Mesh to balance
        mass : float
            Mass
        CoG : [x,y,z]
            Center of gravity, with regard to the current position of the mesh
        rho : float, optional
            Fluid volumic mass. The default is 1025.
        rCenter : np.array, optional
            Reference point for rotation. The default is [0.,0.,0.].
        x0 : [z,rx,rz], optional
            Starting point for the solver. The default is None.
        heel0 : bool, optional
            If True, the heel is fixed to 0. (avoid numerical epsilon that breaks the symmetry)
        """

        self.mesh = mesh
        self.fullMesh = msh.Mesh( self.mesh )
        self.fullMesh.toSymmetry( msh.SymmetryTypes.NONE )

        self.mass = mass
        self.CoG = np.array(CoG)
        self.rho = rho
        self._balancedPosition = None

        if forceSymmetry is None :
            if abs(CoG[1]) < 1e-5 and mesh.sym == msh.SymmetryTypes.XZ_PLANE :
                logger.debug("Symmetry enforced")
                self.forceSymmetry = True
            else :
                self.forceSymmetry = False
        else :
            self.forceSymmetry = forceSymmetry

        if x0 is None  :
            if self.forceSymmetry :
                self._x0 = [-np.mean( self.mesh.getBounds()[2] ) , 0.0  ]
            else :
                self._x0 = [-np.mean( self.mesh.getBounds()[2] ) , 0.0 , 0.0 ]
        else :
            self._x0 = x0

        self._rCenter = np.array( rCenter )


    @classmethod
    def FromHydroStarMesh(cls , hs_mesh , *args, **kwargs):
        """Create MeshBalance class from HydroStar Mesh object
        """
        mesh = hs_mesh.getUnderWaterHullMesh(0)
        mesh.append( hs_mesh.getAboveWaterHullMesh(0))
        return cls( msh.Mesh(mesh), *args, **kwargs )

    @property
    def balancedPosition(self):
        """Equilibrium position (dz , drx, dry)
        """
        if self._balancedPosition is None :
            logger.info("Solving equilibrium START")
            self._solve_equilibrium()
            logger.info("Solving equilibrium done STOP")
        return self._balancedPosition


    def _solve_equilibrium(self) :
        """Perform the actual calculation. Fill _balancePosition
        """
        logger.debug("Computing equilibrium position")
        res = fsolve( self.unbalance , x0 = self._x0 , full_output=True )
        self._balancedPosition, self._fsolve, success , _ = res
        if self.forceSymmetry :
            self._balancedPosition = [self._balancedPosition[0] , 0.0 , self._balancedPosition[1]]

    def isStable(self):
        """Compute GM to check if the equilibrium is stable.
        """

        return


    def get_point_in_new_system( self , point, new_system ) :
        """

        Parameters
        ----------
        point : array(3)
            Point in original mesh reference

        new_system : array(3)
            Offset and rotation defining the new system

        Returns
        -------
        newPoint : array(3)
            Point in the new mesh reference

        """
        z , rx, ry, = new_system
        rmat = geo.EulerAngles_XYZ_e( rx,ry, 0).getMatrix()

        #Apply rotation around center : V' = [rmat]*[V-center] + center
        newPoint = np.transpose(np.matmul(rmat,np.transpose( point - self._rCenter )))
        newPoint += self._rCenter
        newPoint[2] += z
        return newPoint


    def unbalance( self, coefs ) :
        """
        Compute unbalance between mass and volume
        """

        if self.forceSymmetry :
            z , ry = coefs
            rx = 0.0
        else :
            z , rx, ry = coefs


        #--- Rotate the mesh
        tmpMesh = msh.Mesh( self.fullMesh )
        tmpMesh.rotateZYX(  center = self._rCenter, angle = [ rx , ry , 0.] )
        tmpMesh.offset(  [0.0 , 0.0 , z]   )

        cuttedMesh = msh.Mesh( tmpMesh.getCutMesh(  geo.Point( 0,0,0 ) , geo.Vector(0,0,1 ) ))

        if cuttedMesh.getNPanels() == 0:
            return np.array( [ - 1.0 , 0.0 , 0.0 ])

        vol = cuttedMesh.integrate_volume()
        cob = cuttedMesh.integrate_cob()[:-1]

        #--- Rotate the mass
        new_cog = self.get_point_in_new_system( self.CoG, [z , rx, ry])

        if self.forceSymmetry :
            err = np.array( [ vol * self.rho / self.mass - 1.0 ,
                               (new_cog[0] - cob[0]) ,
                            ] )
        else :
            err = np.array( [ vol * self.rho / self.mass - 1.0 ,
                               (new_cog[0] - cob[0]) ,
                               (new_cog[1] - cob[1]) ] )

        logger.debug( f"Unbalance = {err:}")
        return err

    def get_cog_in_balanced_system(self):
        return self.get_point_in_new_system(self.CoG , self.balancedPosition )


    def get_balanced_HydroStarMesh(self) :
        z , rx, ry = self.balancedPosition

        if self.forceSymmetry : 
            tmpMesh = msh.Mesh( self.mesh )
        else :
            tmpMesh = msh.Mesh( self.fullMesh )
            
        tmpMesh.rotateZYX(  center = self._rCenter, angle = [ rx , ry , 0.] )
        tmpMesh.offset(  [0.0 , 0.0 , z]   )

        wetted =  tmpMesh.getCutMesh(  geo.Point( 0,0,0 ) , geo.Vector(0,0,1 ))
        dry =  tmpMesh.getCutMesh(  geo.Point( 0,0,0 ) , geo.Vector(0,0,-1 ))

        return msh.HydroStarMesh(  underWaterHullMeshes = [wetted] ,
                                   aboveWaterHullMeshes = [dry] ,
                                   plateMeshes= [ msh.Mesh() ],
                                   fsMeshes = [],
                                   tankMeshes = []
                                   )


def hsbln( inputFile ):
    """Replace old Fortran executable. Uses same input file, but uses Snoopy.Meshing under the hood.

    Input File Parameters (based on hsbln/bln_input.f90, method blnInput%read(inputFile)):
      - INPUT_MESH         i_filename           Mesh file to equilibrate (aka blnInput%fullMeshFile)
      - OUTPUT_MESH        o_filename           Output file name (aka blnInput%equilibratedMeshFile)
      - COGPOINT_BODY      bd COGx COGy COGz    Center of the gravity position (aka blnInput%CoG(3))
      - INITIAL_POSITION   bd Tx Ty Tz Rx Ry Rz Initial position (aka blnInput%initialPosition(6))
      - MASS_BODY          bd mass              Mass of the ship (aka blnInput%mass)
      - POINT_TO_MOVE      pt_ind ptx pty ptz   Points to move (aka blnInput%points(:,:))
      - RHO                rho                  Water density (aka blnInput%rho)
      - TOLERANCE          tol                  Tolerance for the equilibrium (aka blnInput%tol)
      - DISMA              [TYPE 1]             Mass distribution. Only type 1 is supported
                                                if mass distribution is given, the cog and mass are
                                                calculated automatically:
                                                mass = sum(dism(1, :))
                                                cog(1) = sum(dism(1, idism) *dism(4,idism))/mass
                                                cog(2) = 0.
                                                cog(3) = sum(dism(1, idism) *dism(6, idism))/mass
            no_dism(idism) [anything anything ...] dism(1,idism) dism(2,idism) dism(3,idism) dism(4,idism) dism(5,idism) dism(6,idism)
        ENDDISM

    Default values:
        Tx Ty Tz Rx Ry Rz = 0 0 0 0 0 0
        rho = 1025
        tol = 1.e-6
    """

    # Default values:
    inputMesh = ""
    outputMesh = ""
    cog = {1: [0, 0, 0]}
    initialPosition = {1:[0, 0, 0, 0, 0, 0]}
    mass = {1:0}
    animation = False
    relaxation = [0.1, 0.5]
    rho = 1025.0
    tol = 1.e-6
    points = []
    dismass = []

    dismassParsing = False

    with open(inputFile, "r") as f:
        lns = f.readlines()

    clean_comment_lines(lns)

    for l in lns:
        l = l.strip()
        if l == "": continue
        if l[:1] == "#" or l[:1] == "!": continue
        ws = l.split()
        if ws[0][:4].upper() == "ENDF": break
        if dismassParsing:
            if ws[0][:7].upper() == "ENDDISM": dismassParsing = False; continue
            if len(ws) > 7:
                dismass.append([int(ws[0]), np.array(list(map(float, ws[-6:])))])
        else:
            if ws[0].upper() == "INPUT_MESH" and len(ws) > 1:
                inputMesh = ws[1]
            elif ws[0].upper() == "OUTPUT_MESH" and len(ws) > 1:
                outputMesh = ws[1]
            elif ws[0].upper() == "COGPOINT_BODY" and len(ws) >4:
                cog[int(ws[1])] = np.array(list(map(float, ws[2:])))
            elif ws[0].upper() == "INITIAL_POSITION" and len(ws) > 7:
                initialPosition[int(ws[1])] = np.array(list(map(float, ws[2:])))
            elif ws[0].upper() == "MASS_BODY" and len(ws) > 2:
                mass[int(ws[1])] = float(ws[2])
            elif ws[0].upper() == "POINT_TO_MOVE" and len(ws) > 4:
                points.append([int(ws[1]), np.array(list(map(float, ws[2:])))])
            elif ws[0].upper() == "RHO" and len(ws) > 1:
                rho = float(ws[1])
            elif ws[0].upper() == "TOLERANCE" and len(ws) > 1:
                tol = float(ws[1])
            elif ws[0][:5].upper() == "DISMA":
                if len(ws) > 2 and int(ws[2]) != 1:
                    raise Exception("Obsolete type of mass distribution {:s}. Only type 1 is supported".format(ws[2]))
                dismassParsing = True

    if len(dismass) > 0:
        mass = {1:0.0}
        cog = {1:np.zeros(3)}
        for ds in dismass:
            mass[1]  += ds[1][0]
            cog[1][0] += ds[1][0] *ds[1][3]
            cog[1][2] += ds[1][0] *ds[1][5]
        cog[1] /= mass[1]

    if False:
        print("input_mesh            = ", inputMesh)
        print("output_mesh           = ", outputMesh)
        for bd in sorted(cog.keys()):
            print("COG[{:02d}]               = ".format(bd), cog[bd])
            print("initial position [{:02d}] = ".format(bd), initialPosition[bd])
            print("mass body[{:02d}]         = ".format(bd), mass[bd])
        print("NB points to move     = ", len(points))
        if len(points) > 0:
            for i in range(len(points)):
                print("    #{:02d}           = ".format(i+1), points[i])
        print("rho                   = ", rho)
        print("tolerance             = ", tol)
        if len(dismass) > 0:
            print("Mass distribution is given")
            for i in range(len(dismass)):
                print("    #{:02d}           = ".format(i+1), dismass[i])


    ship = msh.HydroStarMesh(inputMesh, keepSym = True)
    balance = MeshBalance.FromHydroStarMesh( hs_mesh= ship,
                                             mass = mass[1],
                                             CoG  = cog[1],
                                             rho  = rho
                                           )
    balanced = balance.get_balanced_HydroStarMesh()
    balanced.write(outputMesh)

    print( f"CoG Position in new mesh reference : \n{balance.get_cog_in_balanced_system():}")
    logger.debug(f"vol *rho /mass = {balanced.getUnderWaterHullMesh(0).integrate_volume() * 1025./mass[1]:}")

    if len(points) > 0:
        with open(outputMesh+".pts", "w") as f:
            for p in points:
                newpoint = balance.get_point_in_new_system(p[1], balance.balancedPosition)
                # write to the file:  pt_id  x  y  z
                f.write("{:8d}  {:18.11f}  {:18.11f}  {:18.11f}\n".format(p[0], newpoint[0], newpoint[1], newpoint[2]))
    return


   

if __name__ == "__main__" :
    import sys
    hsbln( sys.argv[0] )
















