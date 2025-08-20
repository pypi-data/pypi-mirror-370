"""
   Module to works on waterline
"""

from matplotlib import pyplot as plt
from Snoopy import Meshing as msh
from Snoopy import logger
import numpy as np



class SegmentCollection:
    """Handles segments defined as with two IDs.
    """

    def __init__(self, connectivity):
        """Handles segments defined as with two IDs.

        Parameters
        ----------
        connectivity : np.ndarray
            List of segments defined by two integers ()
        """
        self.connectivity = connectivity
        
    @property
    def n_segments(self):
        return len(self.connectivity)


    def is_closed( self ):
        # Segments on the waterline (not ordered)..
        wl = self.connectivity.flatten()

        # Counts of the indexes present in the waterline segments.
        # Each index should be counted twice if the waterline is closed.
        unique, counts = np.unique(wl, return_counts=True)

        # Number of indexes which are not counted twice.
        id_free = np.where(counts != 2)
        if len(id_free[0]) == 0:  # Waterline is closed.
            return True
        else:
            # logger.debug(self.nodes[unique[id_free]])
            return False


    def order(self):
        self.connectivity = np.concatenate( self.extract_continous_lines()  )
        return self.connectivity

    def extract_continous_lines(self, return_close_info = False):
        """Regroup waterline per continous lines (list of list of array of node indexes).

        Returns
        -------
        list
            List of continous lines (using nodes ID).
        """
        #-------- Find open segments
        # Find free point
        unique, counts = np.unique(self.connectivity.flatten(), return_counts=True)

        free_point = list( unique[ np.where( counts == 1 )[0] ] )

        continous_line_list = []
        close_info = []
        remaining_segs = list(range(len(self.connectivity)))
        
        #--------- Find 'open' continous line
        # Start from segment with a free edge:
        while len(free_point):
            p = free_point.pop(0)
            start_seg = np.where(self.connectivity[:,0] == p)[0]
            if len(start_seg) == 1 and start_seg in remaining_segs :
                continous_line = np.empty( self.connectivity.shape , dtype = self.connectivity.dtype)
                continous_line[0,:] = self.connectivity[start_seg[0], :]
                
                remaining_segs.remove(start_seg[0])
                for i in range(1, len(self.connectivity)+1):
                    # Search for the next segment which is connected to the last segment.
                    ic_ = np.where(self.connectivity[:, 0] == continous_line[i-1, 1])[0]
                    ic_ = [ ic for ic in ic_ if ic in remaining_segs ]
                    
                    ic2_ = np.where(self.connectivity[:, 1] == continous_line[i-1, 1])[0] 
                    ic2_ = [ ic for ic in ic2_ if ic in remaining_segs and continous_line[i-1,0] != self.connectivity[ic, 0]  ]
                    
                    if len(ic_) + len(ic2_) == 0: # reach end of the segment
                        n = i
                        break
                    elif len(ic_) == 1:
                        ic = ic_[0]
                        continous_line[i, :] = self.connectivity[ic, :]
                        remaining_segs.remove(ic)
                    elif len(ic2_) == 1:
                        ic = ic2_[0]
                        continous_line[i, :] = self.connectivity[ic, :][::-1]
                        remaining_segs.remove(ic)
                    else : 
                        raise(Exception())
                        
                continous_line = continous_line[:n,:]
                
                continous_line_list.append( continous_line )
                close_info.append(False)

            elif len(start_seg) > 1:
                raise(Exception())
                
        #--------- Find loops
        while len(remaining_segs) > 0 :
            start_seg = remaining_segs[0]

            continous_line = np.empty( self.connectivity.shape , dtype = self.connectivity.dtype)
            continous_line[0,:] = self.connectivity[start_seg, :]
            remaining_segs.remove(start_seg)

            for i in range(1, len(self.connectivity)+1):
                # Search for the next segment which is connected to the last segment.
                ic_ = np.where(self.connectivity[:, 0] == continous_line[i-1, 1])[0]
                ic_ = [ ic for ic in ic_ if ic in remaining_segs ]
                
                ic2_ = np.where(self.connectivity[:, 1] == continous_line[i-1, 1])[0] 
                ic2_ = [ ic for ic in ic2_ if ic in remaining_segs and continous_line[i-1,0] != self.connectivity[ic, 0]  ]
                
                if len(ic_) + len(ic2_) == 0 :
                    n = i
                    break
                elif len(ic_) == 1:
                    continous_line[i, :] = self.connectivity[ic_[0], :]
                    remaining_segs.remove(ic_[0])
                elif len(ic2_) == 1:
                    continous_line[i, :] = self.connectivity[ic2_[0], ::-1]
                    remaining_segs.remove(ic2_[0])
                else : 
                    raise(Exception())

            continous_line = continous_line[:n,:]
            continous_line_list.append( continous_line )
            close_info.append(True)

        if return_close_info :
            return continous_line_list, close_info
        else:
            return continous_line_list




class Waterline(SegmentCollection):

    def __init__(self, connectivity, nodes, sym = 0 ) :
        """Waterline class. contains the description of a mesh waterline

        Parameters
        ----------
        coords : np.ndarray
            Coordinates of the waterline segments

        segments : np.ndarray
            Connectivity between coordinates

        sym : integer, optional
            0 : Full wateline
            1 : half waterline (symmetric y>0)
            2 : portside waterline
            3 : starboard waterline
            The default is True.
            
        
        Note
        ----
        The segments are ordered and oriented upon construction.
        
        """

        # All nodes of the mesh.
        self.nodes = nodes

        self.sym = sym

        self.connectivity = connectivity
        

            
        self._lines = []  # List of connected lines
        self._closed = [] # List of integer to store which lines are open (0), close (1) or close when accounting for symmetry (2)
        self._areas = [] # List of areas
        
        if len(connectivity) == 0:
            logger.warning("Empty waterline")
            return

        # Removing nodes not on the waterline.
        self._pre_compute()

    def _pre_compute(self, remove_unused=True):
        """Split by continous lines, orient clockwise, and check if closed
        """
        
        if remove_unused:
            self.remove_unused_nodes(_skip_update = True)

        # Extract continous line, and check if they are closed.
        _lines, _closed = self.extract_continous_lines( return_close_info=True )

        # Compute area to orient the segments, and check if lines are closed when considering symmetry.
        eps = 1e-4
        for i,  (l, c) in enumerate(zip(_lines, _closed)):
            if c :
                self._closed.append( 1 )
                l_close = l
            elif self.sym and self.nodes[ l[0,0] , 1 ] < eps and self.nodes[ l[-1,1] , 1 ] < eps:
                self._closed.append( 2 )
                l_close = np.vstack(  [ l , [  l[-1,1], l[0,0] ] ] )
            else:
                self._closed.append( 0 )
                
            if self._closed[i] > 0 :
                area = np.sum( 0.5* (self.nodes[ l_close[:,1]  , 0] - self.nodes[ l_close[:,0]  , 0]) * (self.nodes[ l_close[:,1]  , 1] + self.nodes[ l_close[:,0]  , 1])) 
            else : 
                area = np.nan
                
            if area < 0 :
                logger.debug("Correct waterline orientation")
                self._lines.append( l[::-1, ::-1] )
            else: 
                self._lines.append( l )
                
            self._areas.append(np.abs(area))
            
        # Order the segments.
        self.connectivity = np.concatenate( self._lines )


    def is_closed(self):
        return np.array(self._closed).all()

    @property
    def area(self):
        """Compute the waterplane area.
        
        Return nan if the waterline is not close.
        """
        return np.sum(self._areas)

    def is_point_inside(self, pts):
        """Check wether a point inside a closed loop
        """
        inside = np.full(len(pts), False, dtype=bool)
        from matplotlib.path import Path
        for loop in self.polygons(include_sym=True):
            p = Path( self.nodes[ loop ] )
            current = p.contains_points(pts)
            inside = (current | inside)
        return inside

        
    def remove_unused_nodes(self, _skip_update = False):
        import pandas as pd
        used = np.isin( np.arange(len(self.nodes)) , self.connectivity.flatten() )
        w = np.where(used)[0]
        dic = pd.Series( index = w , data = np.arange(len(w)))
        self.nodes = self.nodes[used, :]
        self.connectivity = np.array( [ dic.loc[ self.connectivity[:,0] ].values,
                                        dic.loc[ self.connectivity[:,1] ].values]).T
        
        if not _skip_update:
            self._pre_compute() # Update lines and loop
        


    def splitted_coords(self, close_loop = True, to_3d = False):
        """Return waterline coordinates.
        """
        
        if to_3d : 
            nodes = self.nodes_3d
        else:
            nodes = self.nodes
        
        coords_list = []
        for con, c in zip( self._lines, self._closed) :
            if c == 1 and not close_loop :
                coords_list.append( nodes[ con[:, 0] ] )
            else: 
                coords_list.append( nodes[np.append(con[:, 0], con[-1, 1])] )

        return coords_list


    @classmethod
    def From_coords(cls, coords, close = False):
        """Build waterline from array of ordered (x,y)
        """
        pass


    def loops(self, include_sym = False):
        """Return list of closed loops, defined as list of segments.
        
        Example
        -------
        >>> wl.loops
        [array([[ 39,  53],
                [ 53,  68],
                ...
                [ 17,  28],
                [ 28,  39]], dtype=int32)]
        >>>
        """
        loops =  [ ]
        for l,c in zip(self._lines , self._closed) :
            if c == 1 :
                loops.append(l)
            elif include_sym and c == 2 :
                loops.append( np.vstack(  [ l , [  l[-1,1], l[0,0] ] ]  ))
        return loops



    def polygons(self, include_sym = False):
        """Return list of closed polygons

        Example
        ------
        >>> wl.polygons
        [array([ 39,  53,  ... ,  28], dtype=int32)]
        >>>
        """
        return [ l[:,0] for l in self.loops(include_sym = include_sym) ]


    @classmethod
    def Read_hstarH5( cls, filename ):
        """Waterline from hslec h5 output

        filename : str
            hslec h5 output

        Returns
        -------
        Waterline

        """
        import xarray
        ds = xarray.open_dataset( filename )

        proplin = ds.PROPWLIN.values
        ds.close()
        n = len(proplin)
        coords = np.empty( (2*n , 2), dtype = float )
        coords[:,:] = np.nan

        coords[::2,0] = proplin[ : , 12]
        coords[1::2,0] = proplin[ : , 15]
        coords[::2,1] = proplin[ : , 13]
        coords[1::2,1] = proplin[ : , 16]
        connectivity = np.arange(0 , 2*n , 1).reshape( n , 2 )
        return cls( coords, connectivity )


    def _computeNormals(self):
        """Compute waterline normals
        """
        logger.warning( "Waterline normals not yet implemented" )
        self._normals = None


    def plot(self , ax = None) :
        """Plot the waterline.

        Parameters
        ----------
        ax : plt.Axis, optional
            Where to plot. The default is None.

        Returns
        -------
        plt.Axis
            The plot
        """
        if ax is None :
            fig , ax = plt.subplots()

        # for seg in self.connectivity :
        #     ax.plot( self.coords[ seg , 0 ] , self.coords[ seg , 1 ] , "-o"  )

        for loop_c in self.splitted_coords():
            plt.plot( loop_c [:, 0], loop_c[:, 1], "-o")
            
        return ax
    
    def get_x_cuts(self, x):
        intersect = []
        for seg  in self.connectivity:
            x1, x2 = self.nodes[seg, 0]
            if x1 <= x <= x2  or  x2 <= x <= x1:
                y1, y2 = self.nodes[seg, 1]
                intersect.append( y1 + ( (x-x1) / (x2-x1) ) * (y2-y1)  )

        return intersect
    
    
    def getBounds(self):

        return [(np.min(self.nodes[:, 0]), np.max(self.nodes[:, 0])),
                (np.min(self.nodes[:, 1]), np.max(self.nodes[:, 1]))]

    def mergeCoincidentNodes(self, tol = 1e-5):
        """Merge coincident nodes
        """
        raise(NotImplementedError)


    def getHalfWaterline(self, side = +1) :
        """Cut waterline in two, if necessary additional point is added at y=0

        Parameters
        ----------
        side : float, optional
            +1 to get portside waterline (y>0)
            -1 to get starboard waterline (y<0).
            The default is +1.

        Returns
        -------
        Waterline

        """
        if self.sym != 0 :
            return self
        else:
            raise(NotImplementedError)

        
    @property
    def nodes_3d(self):
        """Add the z=0 coordinates
        """
        return np.c_[ self.nodes , np.zeros(  len(self.nodes) )]
    

    def get_vtk(self):
        import vtk
        vtkPoints = vtk.vtkPoints()
        vtkPoints.SetNumberOfPoints(len(self.nodes))
        # Nodes
        for nodeId, node in enumerate(self.nodes_3d):
            vtkPoints.InsertPoint(nodeId, node)
        aPolyData = vtk.vtkPolyData()
        aPolyData.SetPoints(vtkPoints)
        
        # Create a cell array to store the polygon in
        aCellArray = vtk.vtkCellArray()

        for l in self.polygons:
            # Define a polygonal hole with a clockwise polygon
            aPolygon = vtk.vtkPolygon()
            for p in l :
                aPolygon.GetPointIds().InsertNextId(p)
            aCellArray.InsertNextCell(aPolygon)
        aPolyData.SetPolys(aCellArray)
        return aPolyData







eps = 1e-3
def getHalfWaterline( waterLineCoords , side = +1 ) :
    """
    return the one sided waterline, sorted in increasing x
    """

    #In case the mesh is not symmetric, point should be added at z=0
    tmp_ = add_y0_points(waterLineCoords)

    half = waterLineCoords[ np.where( tmp_[:,1]*side > -eps) ]

    #Start from aft central point
    symPlaneId = np.where( np.abs( half[:,1] ) < eps )[0]
    startNode = symPlaneId[ np.argmin(  half[symPlaneId,0] ) ]

    if half[(startNode+1) % len(half) , 1] == 0 :
        startNode += 1

    half = np.roll( half, -startNode , axis = 0)

    if half[0,0] > half[-1,0] :
        return half[::-1]
    else :
        return half


def add_y0_points( waterLineCoords, y = 0.0 ) :

    if len(np.where( abs(waterLineCoords[:,1]) < eps )[0]) == 2 :
        return waterLineCoords


    print (len(np.where( abs(waterLineCoords[:,1]) < eps )[0]))
    raise(NotImplementedError)

    #Interpolate at y = 0
    #TODO
    #closed set of point
    closed = np.vstack( [ waterLineCoords , waterLineCoords[0,:] ] )
    diff = (closed[:,1]-y) * (closed[:,1]-y) > 0



def getHalfCircDomain( waterLineCoords, r , side = +1, n = None, x_center = 0.0, y_center = 0.0 , close = False) :
    """
    Add circle around half waterline
    """

    half = getHalfWaterline(waterLineCoords, side = side )

    if n is None :
        n = len(half)

    i = np.linspace( 0, np.pi, n  )
    circle = np.full( (n, half.shape[1]) , 0.0 )
    circle[:,0] = r * np.cos( i ) + x_center
    circle[:,1] = side * r * np.sin( i ) + y_center
    res = np.concatenate( [ half, circle ] )

    if close :
        res = np.vstack( [ res, res[0,:] ] )

    return res


# -----------------------------------------------------------------------------
def inside_wl(x, y, x1_wl, y1_wl, x2_wl, y2_wl):
    """Check if point is inside waterline
    Args:
        x (float): DESCRIPTION.
        y (float): DESCRIPTION.
        x1_wl (np.array): x coordinates of first point
        y1_wl (np.array): y coordinates of first point
        x2_wl (np.array): x coordinates of second point
        y2_wl (np.array): y coordinates of second point

    Returns:
        bool : True if inside, False if outside

    """
    xmin = min(np.min(x1_wl),np.min(x2_wl))
    xmax = max(np.max(x1_wl),np.max(x2_wl))
    ymin = min(np.min(y1_wl),np.min(y2_wl))
    ymax = max(np.max(y1_wl),np.max(y2_wl))

    expr = (xmin < x < xmax) and (ymin < y < ymax)

    tol = 1e-6

    if (not expr):
        return False
    cut  = 0
    cutp = 0
    ne  = np.size(x1_wl)
    for i in range(ne):
        yemin  = min(y1_wl[i],y2_wl[i])
        yemax  = max(y1_wl[i],y2_wl[i])
        expr   = (yemin <= y <= yemax)
        if(expr):
            # savoir si le pt est a gauche ou a droite du segment
            if( y1_wl[i] <= y2_wl[i] ):
                px0 = x1_wl[i]
                px1 = x2_wl[i]
                py0 = y1_wl[i]
                py1 = y2_wl[i]
            else:
                px0 = x2_wl[i]
                px1 = x1_wl[i]
                py0 = y2_wl[i]
                py1 = y1_wl[i]
            u    = np.array([ px0 - x , py0 - y, 0.])
            u1   = np.array([ px1 - x , py1 - y, 0.])
            d    = np.cross(u, u1)[2]
            if (d >= tol):
                if ( abs(y - py0) <= tol or abs(y - py0) <= tol ):
                    cutp = cutp + 1
                    cut  = cut  + 1
                else:
                    cut = cut + 1
    return ( (cut - cutp) % 2 == 1 )




def test_SegmentCollection():

    two_lines = np.array( [ (3,4), (200,3) , (8,9) , (9,10), (10,11), (100,200)  ] )
    two_loops = np.array( [ (3,100), (200,3) , (8,9) , (9,10), (10,8), (100,200)  ] )
    one_loop_one_line = np.array( [ (3,100), (200,3) , (8,9) , (9,10), (10,8), (100,300)  ] )


    l,r = SegmentCollection(one_loop_one_line).extract_continous_lines(True)
    assert( not r[0] and r[1] )

    l,r = SegmentCollection(two_loops).extract_continous_lines(True)
    assert( r[0] and r[1] )

    l,r = SegmentCollection(two_lines).extract_continous_lines(True)
    assert( not r[0] and not r[1] )


if __name__ == "__main__" :

    from matplotlib import pyplot as plt
    
    logger.setLevel(10)
    meshFile = f"{msh.TEST_DATA}/B31.hst"
    
    mesh = msh.Mesh(msh.HydroStarMesh(meshFile, keepSym = True).getUnderWaterHullMesh(0))
    
    print(mesh)
    
    logger.info("START")

    wl = mesh.extractWaterlineObj()
    wl.plot()
    
    
    # wl.is_point_inside( [ [0.0 , 0.0] , [1000. , 0.] ] )

    # wl.getBounds()

    # wl.plot()
    # logger.info("STOP")
