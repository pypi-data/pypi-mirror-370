import numpy as np
from Snoopy import logger
from Snoopy import Meshing as msh


def create_fs_mesh(waterline, dx, dy, x0=None, y0=None, a=None, b=None, x_min=None, x_max=None, y_min=None, y_max=None):
    """Start from a rectangular grid, remove waterplane, optionally what is outside a given radius, and triangulate.

    Parameters
    ----------
    waterline : Waterline or None
        Structure waterline.
    dx : float
        x Step    
    dy : float
        y Step
    a and b : float
        Small and large radii of the elliptical mesh to create. If None, rectangular mesh is generated.
    x0 : float
        x center of circular mesh
    y0 : float
        y center of circular mesh
    x_min : float
        x start.
    x_max : float
        x stop.
    y_min : float
        y start.
    y_max : float
        y stop.
        
    Note
    ----
    The orientation of the panel might not be consistent at this stage.


    Returns
    -------
    vtkPolydata
        Triangular mesh for the free-surface. 
    """
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    if waterline and not waterline.is_closed():
        raise(Exception("Can only generate free-surface mesh when waterline is closed"))
    
    if (a is not None) and (b is not None):
        x_min = x0 - a
        x_max = x0 + a

        y_min = y0 - b
        y_max = y0 + b
        ic = 2

    if waterline and waterline.sym == 1:
        y_min = 0.0
        ic = 1

    # Create the point grid to be triangulated later
    xVect = np.arange(x_min, x_max, dx)
    yVect = np.arange(y_min, y_max, dy)
    X, Y = np.meshgrid(xVect, yVect)

    # Filter out point in waterplane
    logger.debug("Filter waterplane")
    xy = np.vstack([X.flatten(), Y.flatten()]).T

    if waterline:
        outside = ~waterline.is_point_inside(xy)
    else:
        outside = np.full((len(xy)), True, dtype=bool)
    
    if (a is not None) and (b is not None):
        from numpy.linalg import norm
        xy_ = np.array(xy)
        xy_[:, 0] -= x0
        xy_[:, 1] -= y0
        xy_[:, 0] /= a
        xy_[:, 1] /= b
        xy_filtered = xy[outside & (norm(xy_, axis=1) <= 1)]
        half_length = 0.5 * np.pi * (3 * (a + b) - np.sqrt((3 * a + b) * (a + 3 * b)))  # Ramanujan's first approximation.
        n_circ = int(ic * half_length / (np.minimum(dx, dy)))
        ellipse = np.zeros((n_circ, 2), dtype=float)
        angle = np.linspace(0, ic * np.pi, n_circ, endpoint=False)
        ellipse[:, 0] = a * np.cos(angle) + x0
        ellipse[:, 1] = b * np.sin(angle) + y0
        xy_filtered = np.concatenate([xy_filtered, ellipse])
    else: 
        xy_filtered = xy[outside]

    logger.debug("Triangulate")
    points = vtk.vtkPoints()
    verts = vtk.vtkCellArray()
    for x, y in xy_filtered:
        pt_id = points.InsertNextPoint([x, y, 0.])
        verts.InsertNextCell(1)
        verts.InsertCellPoint(pt_id)

    pointGrid = vtk.vtkPolyData()
    pointGrid.SetPoints(points)
    pointGrid.SetVerts(verts)

    # Create the polydata to triangulate
    append = vtk.vtkAppendPolyData()
    append.AddInputData(pointGrid)
    
    if waterline:
        _hullWaterlines = [createPolygon(pointArray) for pointArray in waterline.splitted_coords(to_3d=True, close_loop=False)]
        for hull in _hullWaterlines:
            append.AddInputData(hull)
    append.Update()
    
    # viewPolyData(append.GetOutput(), display_props={"edges" : 1})
    logger.debug("Number of polys {}, cells {}".format(
        append.GetOutput().GetNumberOfPolys(), append.GetOutput().GetNumberOfCells()))

    # Constrained 2D Delaunay triangulation: triangulate the point grid
    # and create holes in place of hulls
    delaunay = vtk.vtkDelaunay2D()

    delaunay.SetTolerance(1e-15)
    delaunay.SetInputConnection(append.GetOutputPort())
    delaunay.SetSourceConnection(append.GetOutputPort())
    delaunay.Update()

    del_data = delaunay.GetOutput()
    
    if waterline is None : 
        return del_data

    # Constrained Delaunay imposes segments, but do no ensure that the waterplane is cutted.
    cc = vtk.vtkCellCenters()
    cc.SetInputConnection(delaunay.GetOutputPort())
    cc.Update()
    
    logger.debug('Remove waterplane')
    points = vtk_to_numpy(cc.GetOutput().GetPoints().GetData())[:,:2]
    outside = ~waterline.is_point_inside(points)
    
    final = vtk.vtkPolyData()
    final.SetPoints(del_data.GetPoints())
    final_ca = vtk.vtkCellArray()
    final.SetPolys(final_ca)

    logger.debug('start insert')
    for i in range(del_data.GetNumberOfCells()) :
        if outside[i]:
            cell = del_data.GetCell(i)
            final_ca.InsertNextCell(cell)

    # TODO : check orientation consistency
    return final



def create_fs_mesh_circ( r, dx, dy, waterline, x0 = 0., y0 = 0.):

    import vtk
    if waterline.sym and False: 
        ymin = 0
        y0 = 0.
    else :
        ymin = -r-0.5*dx+y0
    
    rectGrid = create_fs_mesh(x_min=-r-0.5*dx+x0, x_max=+r+1.5*dx+x0, dx=dx,
                              y_min=ymin, y_max=+r+1.5*dy+y0, dy=dy,
                              waterline=waterline)
    # Create a disk
    polygonSource = vtk.vtkRegularPolygonSource()
    polygonSource.GeneratePolygonOff()
    polygonSource.SetNumberOfSides(100)
    polygonSource.SetRadius(r)
    polygonSource.SetCenter(x0, y0, 0.0)

    # Get the circle contour
    loops = vtk.vtkContourLoopExtraction()
    loops.SetInputConnection(polygonSource.GetOutputPort())

    # Cut the grid to get a disk with grid points
    cookieCutter = vtk.vtkCookieCutter()
    cookieCutter.SetInputData(rectGrid)
    cookieCutter.SetLoopsConnection(loops.GetOutputPort())

    # Cookie cutter is bugged and generates coincident points for every
    # vertex shared by at least tow polygons: remove them
    cleanPolyData = vtk.vtkCleanPolyData()
    cleanPolyData.PointMergingOn()
    cleanPolyData.SetInputConnection(cookieCutter.GetOutputPort())
    cleanPolyData.Update()

    return cleanPolyData.GetOutput()


def createPolygon( pointsArray ):
    """
    Create polydata with one polygon from ordered list of points
    """
    import vtk
    nTot = len(pointsArray)
    loops = vtk.vtkPolyData()
    
    loopPts = vtk.vtkPoints()
    loopPolys = vtk.vtkCellArray()
    loops.SetPoints(loopPts)
    loops.SetPolys(loopPolys)
    loopPts.SetNumberOfPoints(nTot)
    loopPolys.InsertNextCell(nTot)
    for i in range(nTot) :
        loopPts.SetPoint( i, pointsArray[i,:]  )
        loopPolys.InsertCellPoint(i)
    return loops



"""Obsolete code, not currently used.
"""
def extractWaterLine(hullPolydata):
    """Extract waterline from wetted hull
    
    Works using vtkFeatureEdges and vtkContourLoopExtraction
    
    return arrays of waterline nodes (xyz)
    """
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    #--- Retrieve waterline
    wl = vtk.vtkFeatureEdges()
    wl.SetInputData( hullPolydata )
    wl.BoundaryEdgesOn()
    wl.FeatureEdgesOff()
    wl.NonManifoldEdgesOff()
    wl.ManifoldEdgesOff()
    wl.Update()
    loops = vtk.vtkContourLoopExtraction()
    loops.SetInputConnection(wl.GetOutputPort())
    loops.Update()
    loops_p = loops.GetOutput()
    vtk_to_numpy(  loops_p.GetPoints().GetData() )
    idList = vtk.vtkIdList()
    loops_p.GetCellPoints(0, idList)
    nId = [idList.GetId(i) for i in range( idList.GetNumberOfIds() )]
    orderedCoord = vtk_to_numpy(  wl.GetOutput().GetPoints().GetData() ) [nId]

    return orderedCoord

def createHalfFreeSurfaceMesh_polydata( hullPolydata, R , dx, dy, x_center = 0., y_center = 0. , side = +1, orderedCoord = None) :
    """Create circulat free-surface mesh around a simple hull.

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center

    """
    import vtk
    from .waterline import getHalfCircDomain
    #--- Create background free-surface mesh
    rect = createRectangularGrid( x_min = x_center - 2*R,
                                  x_max = x_center + 2*R,
                                  dx = dx,
                                  y_min = y_center - 2*R,
                                  y_max = y_center + 2*R,
                                  dy = dy )

    if orderedCoord is None:
        orderedCoord = extractWaterLine( hullPolydata, side = side )

    res = getHalfCircDomain( orderedCoord, r=R , n=100,  side = side, x_center = x_center, y_center = y_center )

    cont = createPolygon(res)
    cookie = vtk.vtkCookieCutter()
    cookie.SetInputData(rect)
    cookie.SetLoopsData(cont)
    cookie.Update()

    return cookie.GetOutput()


def createFreeSurfaceMesh( *args, **kwargs ):
    """
    Create a full free surface mesh around the hull, using cookieCutter

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center
    """

    fs1 = createHalfFreeSurfaceMesh(*args, side = +1, **kwargs)
    fs2 = createHalfFreeSurfaceMesh(*args, side = -1, **kwargs)
    fs1.append(fs2)
    return fs1


def createHalfFreeSurfaceMesh( hullMesh, R , dx, dy, x_center = 0., y_center = 0., side = +1, orderedCoord = None ) :
    """ Create circulat free-surface mesh around a hull.

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center
    """
    polydata = createHalfFreeSurfaceMesh_polydata(hullMesh.toVtkPolyData(), R, dx, dy, x_center, y_center, side=side, orderedCoord = orderedCoord )
    return msh.Mesh.FromPolydata(polydata, polygonHandling = "triangulate")





def createRectangularGrid(x_min, x_max, dx, y_min, y_max, dy):
    """
    Create a rectangular grid polydata
    """
    import vtk
    x_dim = int((x_max - x_min) / dx)
    y_dim = int((y_max - y_min) / dy)

    planeSource = vtk.vtkPlaneSource()
    planeSource.SetOrigin(x_min, y_min, 0.0)
    planeSource.SetPoint1(x_max, y_min, 0.0)
    planeSource.SetPoint2(x_min, y_max, 0.0)
    planeSource.SetXResolution(x_dim)
    planeSource.SetYResolution(y_dim)
    planeSource.Update()
    return planeSource.GetOutput()



def creatDiskGrid( r, dx, dy, x_center = 0, y_center = 0 ) :
    import vtk
    rect = createRectangularGrid( -r, +r, dx, -r, +r, dy )
    n_circ = 100
    circle = np.zeros( (n_circ,3), dtype = float )
    angle = np.linspace(0 , 2*np.pi, n_circ, endpoint = False)
    circle[:,0] = r*np.cos( angle )
    circle[:,1] = r*np.sin( angle )
    cont = createPolygon(circle)

    cookie = vtk.vtkCookieCutter()
    cookie.SetInputData(rect)
    cookie.SetLoopsData(cont)
    cookie.Update()
    
    # Cookie cutter is bugged and generates coincident points for every
    # vertex shared by at least tow polygons: remove them
    cleanPolyData = vtk.vtkCleanPolyData()
    cleanPolyData.PointMergingOn()
    cleanPolyData.SetInputConnection(cookie.GetOutputPort())
    cleanPolyData.Update()

    return cleanPolyData.GetOutput()



    
    
