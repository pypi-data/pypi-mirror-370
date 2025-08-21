import pickle
import itertools
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.special import comb
from scipy.spatial import ConvexHull
from matplotlib import pyplot as plt
from Snoopy import logger
from Snoopy.Statistics import POT_GPD, rolling_declustering, BM_GEV


class _DirectIformABC():
    """Abstract class for direct IFORM. Subclass are associated to a given univariate method.

    The univariate approach should be implemented in the ._create_univariate() method of the child class.

    Implementation of the approach described in  https://www.researchgate.net/publication/365459533_Model-free_environmental_contours_in_higher_dimensions

    More or less the equivalent of the following matlab code:  https://github.com/edmackay/Direct-IFORM
    """

    def __init__(self, df , npoints):
        """Abstract class, this will never be called directly.

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe containing n columns will result in coutour in n dimension
        npoints : int
            Discretisation for all dimensions
        """

        self._df = df.copy()
        self.npoints = npoints


        self.dim_names = self._df.columns.values
        self.ndim = len(self.dim_names)

        #--- Normalisation
        self.mean_dict = { k : np.mean( df.loc[ : , k  ] ) for k in self.dim_names  }
        self.std_dict = { k : np.std( df.loc[ : , k  ] ) for k in self.dim_names  }

        for d in self.dim_names :
            self._df[ d + "_a"  ] =  (df[ d  ] - self.mean_dict[ d] ) / self.std_dict[d]

        self.dim_names_a = [n+"_a" for n in self.dim_names]

        #--- Calculation of direction vectors
        self._direction_vector = direction_vector(self.ndim , self.npoints).rename( columns = { i:n for i, n in enumerate(self.dim_names_a) } )

        self._res_df = pd.DataFrame( index = self._direction_vector.index, dtype = float )

        #-- Initialisation of array containing results of fit for each direction
        self._fit_objects = None

        self._reset_cached_data()


    @property
    def direction_vector(self):
        return self._direction_vector

    def _reset_cached_data(self):
        #-- Cache for extracted nD contour (can be time consuming in ndim >= 5)
        self._contour = {}
        
        # voronoi diagram (for plot in 2D)
        self._vor = {}

    @property
    def n_angles(self):
        """Return the number of search direction"""
        return len(self._direction_vector)

    @property
    def results_df(self):
        return pd.concat( [self._direction_vector , self.fit_df, self._res_df  ], axis = 1 )

    @property
    def fit_df(self) :
        return pd.DataFrame( index=self._direction_vector.index )

    def _create_univariate(self , se):
        """Method to override in subclass.

        Should return an object that has the following method :
          - rp_to_x
          - plot_rp_fit
          - plot_rp_data
        """
        raise(NotImplementedError())


    def _clear_optional_data(self):
        """Method that remove optional data, such as storage of projected points. 
        
        This method is optional called within '.to_pickle()' to reduce file size. It depends on the ._fit() results and has thus to be implemented in child class.
        """
        pass
    

    def to_pickle(self , filename, clear_optional_data = True):
        """Store to pickle format.

        Parameters
        ----------
        filename : str
            File name
        """
        if clear_optional_data:
            self._clear_optional_data()
        with open(filename , "wb") as f :
            pickle.dump( self, f )

    @classmethod
    def from_pickle(cls , filename):
        """Load from pickle

        Parameters
        ----------
        filename : str
            File name

        Returns
        -------
        DirectIform
            The DirectIform object
        """
        with open(filename , "rb") as f :
            o = pickle.load( f )
        return o


    def _scale(self , points_df):
        """Scale the dataframe.
        
        Parameters
        ----------
        points_df : pd.DataFrame
            The dataframe in original dimension

        Returns
        -------
        pd.DataFrame
            Dataframe in scaled dimensions (columns with _a suffix).
        """
        return pd.DataFrame( index=points_df.index, data = { d + "_a" : (points_df[ d  ] - self.mean_dict[ d] ) / self.std_dict[d]  for d in self.dim_names } )

    def _scale_back(self , points_df ) :
        """Scale back the data.

        Parameters
        ----------
        points_df : pd.DataFrame
            The dataframe to scale back (columns with "_a" suffix).

        Returns
        -------
        pd.DataFrame
            Dataframe in original dimensions (columns without _a suffix).
        """
        return pd.DataFrame( index=points_df.index, data = { k : self.std_dict[k] * points_df[k+"_a"] + self.mean_dict[k]  for k in self.dim_names } )


    def fit_projections(self) :
        """Performs the univariate fits for all the direction vectors.

        Results is stored in "_fit_objects"
        """
        if self._fit_objects is None :
            _array = self._df.loc[ : , self.dim_names_a ].values
            _dir_vector = self._direction_vector.loc[:, self.dim_names_a].values
            self._fit_objects = np.empty( (self.n_angles) , dtype = object )
            for i, r in tqdm(list(enumerate(_dir_vector)), desc = "Fitting projections"):
                proj  = _array[:,:].dot( r )
                se =  pd.Series( index = self._df.index.values , data = proj)
                self._fit_objects[i] = self._create_univariate( se )
                

    def project_points( self, points, dir_id ):
        """Project point dataframe on given direction.

        Parameters
        ----------
        points : pd.DataFrame
            Points to project.
        dir_id : int
            Direction label.

        Returns
        -------
        np.array
            Point projection
        """
        _given_points = self._scale( points ).loc[ : , self.dim_names_a ].values
        return _given_points[:,:].dot( self._direction_vector.loc[dir_id,:].values )


    def point_to_rp( self, point_coordinates, method = "discrete",  opt_kwargs = {} ):
        """Look for the Return period of a given point. 

        Parameters
        ----------
        point_coordinates : pd.DataFrame
            Coordinates of the points, index are the different points, columns are the variable names
        method : str
            if method == "discrete" only existing search direction will be looked for.
            if method == "optimize_contraint" is used, optimization on the search direction is used, parametrized with cartesian coordiantes with unit norm as constraint.
            if method == "optimize_spherical" is used, optimization on the search direction is used, parametrized with spherical coordinates.

        Returns
        -------
        pd.DataFrame
            index is point, columns are "RP" and direction vectors.
        """
        
        npoints = len(point_coordinates)
        
        # Scale input coordinates
        _given_points = self._scale( point_coordinates ).loc[ : , self.dim_names_a ].values
        
        if "optimize" in method : 
            from scipy.optimize import minimize
            if "constraint" in method:
                _opt_kwargs = {"method" : "trust-constr" } # minimizer has to be able to deal with constraint.
            else : 
                _opt_kwargs = {"method" : "nelder-mead" }
                
            _opt_kwargs.update(opt_kwargs)

            # Create results dataframe, with RP, and search direction resulting in that RP.
            res_df = pd.DataFrame( index = point_coordinates.index , columns= ["RP"] + self.dim_names_a )

            _array = self._df.loc[ : , self.dim_names_a ].values
            
            # Run search on all discrete direction, will serve as initialization point
            _discrete = self.point_to_rp( point_coordinates, method ="discrete")

            # Function to maximize (RP for the given search direction)
            def proj_data(direction, ipoint):
                proj_data  = _array[:,:].dot( direction )
                proj_point  = _given_points[:,:].dot( direction )[ipoint]
                se =  pd.Series( index = self._df.index.values , data = proj_data)
                fit_obj = self._create_univariate( se )
                res = -fit_obj.x_to_rp( proj_point )
                logger.debug( f"RP = {-res:} - {np.sum(direction**2)**0.5:}")
                return res
            
            
            for point_id in tqdm( point_coordinates.index, desc = "Optimizing RP") :
                
                
                # x0 from discrete case
                x0 = self._direction_vector.loc[ _discrete.loc[point_id , "DIR_ID"], self.dim_names_a  ].values
                
                # function "proj_data" works with numpy and not pandas
                ipoint = point_coordinates.index.get_loc(point_id)

                if "constraint" in method : 
                    res_opt = minimize( lambda x: proj_data(x , ipoint), 
                                        x0 = x0,
                                        constraints = [ {"type":"eq" , "fun" : l2_norm_constraint , "jac" : l2_norm_jac }],
                                        **opt_kwargs
                                       )
                    res_df.loc[point_id, self.dim_names_a] = res_opt.x
                    
                    
                elif "spherical" in method : 
                    from Snoopy.Math.spherical_coordinates import x_to_t, t_to_x

                    # Convert starting point to spherical coordinates
                    t0 = x_to_t(x0)[1:]

                    def reparam( thetas , ipoint ):
                        direction = t_to_x( np.concatenate( [[1.0] , thetas] ) )
                        return proj_data(direction, ipoint)

                    res_opt = minimize( lambda x: reparam(x , ipoint), 
                                        x0 = t0,
                                        # TODO : add bounds ?
                                        **opt_kwargs)

                    res_df.loc[point_id, self.dim_names_a] = t_to_x( np.concatenate( [[1.0] , res_opt.x ] ) ) 
                else :
                    raise(Exception(f"Unknown method {method:}"))

                res_df.loc[point_id, "RP"] = -res_opt.fun
            return res_df
        
        elif method == "discrete":
            _dir_vector = self._direction_vector.loc[:, self.dim_names_a].values
            rp_tab = np.empty( (self.n_angles, npoints ), dtype = float)
            for iproj, r in tqdm(list(enumerate(_dir_vector)), desc = "Maximizing RP on discrete directions"):
                proj  = _given_points[:,:].dot( r )
                for ipoint in range(npoints):
                    rp_tab[ iproj, ipoint ] = self._fit_objects[iproj].x_to_rp( proj[ipoint] )
            return pd.DataFrame( index = point_coordinates.index, data = { "RP" : rp_tab.max(axis=0), "DIR_ID" : self._direction_vector.index[rp_tab.argmax(axis=0)] } )
        else: 
            raise(Exception(f"Unknown method {method:}"))
        

    def drop_directions(self, dir_id):
        """Drop the given search directions  (can be the one for which the fit failed)
        
        Parameters
        ----------
        rp_list : np.ndarray
            List of search direction ID to drop.
        """
        good_i = ~np.isin( self._direction_vector.index , dir_id )
        self._fit_objects = [ self._fit_objects[i] for i in range(self.n_angles) if good_i[i] ]
        self._direction_vector = self._direction_vector.loc[ good_i ]
        self._res_df = self._res_df.loc[good_i , :]
        
        # Data from which contour are extracted are modified, cached contours should be cleared
        self._reset_cached_data()


    def rp_projections(self, rp_list, ci_level = None ):
        """Calculate return values for on each projection, using existing fitted model.
        
        If value are already available, the calculation is skipped

        Parameters
        ----------
        rp_list : np.ndarray or float
            List of return period
        ci_level  : float or None
            If provided, the upper and lower bound of the CI are calculted and stored in the columns ("ci_low",rp, ci_level) and ("ci_high",rp, ci_level)
        """
        
        if not hasattr(rp_list, "__len__") :
            rp_list = np.array([rp_list])

        if np.all( [ rp in self._res_df.columns for rp in rp_list] ):
            logger.debug("Using existing projections at {rp:}")
            
        res = np.zeros( ( self.n_angles , len(rp_list) ) )
        for i in tqdm( np.arange(self.n_angles), desc = "Evaluate RP at each projection" ) :
            res[i,:] = self._fit_objects[i].rp_to_x( rp_list )

        for i , rp in enumerate(rp_list) :
            self._res_df[rp] = res[:,i]

        if ci_level is not None :
            res_low = np.zeros( ( self.n_angles , len(rp_list) ) )
            res_high = np.zeros( ( self.n_angles , len(rp_list) ) )
            for i in tqdm( np.arange(self.n_angles), desc = "Evaluate RP at each projection" ) :
                res_low[i,:], res_high[i,:] = self._fit_objects[i].rp_to_xci( rp_list, ci_level = ci_level )

            for i , rp in enumerate(rp_list) :
                self._res_df[("ci_low",rp,ci_level)] = res_low[:,i]
                self._res_df[("ci_high",rp,ci_level)] = res_high[:,i]



    def _extract_contour( self , rp ) :
        """Extract contour at RP, using Voronoi cells, in working space (normalised)

        Parameters
        ----------
        rp : float, or (float, str)
            Return period.

        Returns
        -------
        np.ndarray
            Points
        """
        if rp not in self._contour:
            from scipy.spatial import Voronoi
            reflection = 2 * self._direction_vector.values * self._res_df[rp].values[: , None]
            reflection = np.concatenate( [ np.array( [ np.zeros( (self.ndim) ),] ) , reflection])
            logger.debug(f"Calling Voronoi {reflection.shape:}")
            vor = Voronoi( reflection )
            if self.ndim == 2: # Save Voronoi object for further plot with plot_voronoi_2d
                self._vor[rp] = vor
            self._contour[rp] = vor.vertices[ vor.regions[ vor.point_region[0] ] ]
        else: 
            logger.debug(f"Using cache results for {rp:}")

        return self._contour[rp]

    def extract_contour( self , rp, ci_level = None, low_high = None ):
        """Extract contour (scaled back).

        Parameters
        ----------
        rp : Float
            Return period
        ci_level : float, optional
            If not None the confidence interval bound will be output (high or low) depending on "low_high" value. The default is None.
        low_high : str, optional
            'low' or 'high'. The default is None.

        Returns
        -------
        pd.DataFrame
            Points of the contour
        """

        if low_high is None:
            col = rp
        else :
            if ci_level is None : 
                raise(Exception("CI level should be given"))
            else: 
                col = ( f"ci_{low_high:}" ,rp, ci_level )

        if col not in self._res_df.columns :
            self.rp_projections( np.array([rp]), ci_level = ci_level )

        logger.debug(f"Extract {self.ndim:} contour at RP={rp:} {low_high:} {ci_level:} using Voronoi cells")
        return self._scale_back( pd.DataFrame(  data = self._extract_contour(rp=col) , columns = self.dim_names_a ) )
    
    
            
            

    @staticmethod
    def _variable_change(df, output_variables, transform_dict):
        """Add columns according to operation specified in transform_dict

        Parameters
        ----------
        df : pd.DataFrame
            The input/output dataframe (modified!)
        output_variables : list
            The list of desired columns to get.
        transform_dict : dict
            Dictionary of functions

        Returns
        -------
        df : pd.DataFrame
            The dataframe containing all the output variables
        """
        for v in output_variables :
            if v not in df.columns :
                df[v] = transform_dict[v] (df)
        return df


    def projected_contour( self , variables, rp, final_variables = None, return_triangulation = False, transform_dict = {}, ci_level = None, low_high = None ):
        """Return projection of the contour.

        Parameters
        ----------
        variables : list(str)
            Space in which the convex contour is calculated
        rp : float
            Return period
        final_variables : TYPE, optional
            Space in which the contour is output. The default is set to variables.
        return_triangulation : bool, optional
            If True, the triangulation is returned, necessary to display 3D surface. The default is False.
        transform_dict : dict, optional
            Dictionary of function to ease variable change. The default is {}.

        Returns
        -------
        pd.DataFrame
            The contour projection
        """

        if final_variables is None :
            final_variables = variables

        nd_contour = self.extract_contour(rp, ci_level=ci_level, low_high=low_high)
        
        self._variable_change( nd_contour, variables, transform_dict  )

        logger.debug(f"Projecting {self.ndim:}D contour on {len(variables):}D using Qhull")
        conv_hull = ConvexHull( nd_contour.loc[ : , variables ].values)

        # Construct dataframe containing only the contour points.
        contour_points = pd.DataFrame( columns = variables, data = conv_hull.points[conv_hull.vertices] )

        self._variable_change( contour_points, final_variables, transform_dict  )

        output_points = contour_points.loc[: , final_variables]

        if return_triangulation :
            # ConvexHull.simplices return position in the original point vector. The two following lines convert to position of contour points
            _conv = pd.Series( index = conv_hull.vertices, data = np.arange( len( conv_hull.vertices ) ) )
            simplices = _conv.loc[ conv_hull.simplices.flatten() ].values.reshape( conv_hull.simplices.shape )
            return output_points, simplices
        else :
            return output_points



    def sliced_contour(self, slice_dims , slice_values , rp, final_variables = None, transform_dict = {}, low_high = None, ci_level = None ) :
        """Cut the contour at a given level.

        Parameters
        ----------
        slice_dim : str
            The cut dimension.
        slice_value : float
            The value at which to cut
        rp : float
            Return period
        return_triangulation : bool, optional
            If True, the triangulation is returned. The default is False.

        Returns
        -------
        pd.DataFrame
            The intersection points. (and optionally the triangulation)
        """


        nd_contour = self.extract_contour( rp , low_high=low_high , ci_level = ci_level)

        _slice = nd_contour

        for slice_dim, slice_value in zip( slice_dims, slice_values ) :
            _slice = slice_convhull_df( _slice , slice_dim = slice_dim, slice_value=slice_value )


        if final_variables is not None :
            return self._variable_change( _slice, final_variables, transform_dict  ).loc[:,final_variables]
        else :
            return _slice



    #------------ Plotting functions
    def plot_slice_2d(self,  slice_dims , slice_values , rp , final_variables = None, ax = None, transform_dict = {}, color = "b", **kwargs):

        if len(slice_dims) != self.ndim-2 :
            raise(Exception("Not a 2D slice"))

        slice_cont = self.sliced_contour( slice_dims , slice_values , rp  )


        label = kwargs.pop( "label" , f"RP = {rp:} " +  " ".join( f"{d:} = {v:}" for d, v in zip(slice_dims, slice_values)) )

        ax = self.plot_2d_convex_hull(slice_cont, final_variables=final_variables, transform_dict=transform_dict, ax=ax, color = color, label=label,**kwargs)

        if final_variables is None :
            ax.set(xlabel = slice_cont.columns[0] , ylabel = slice_cont.columns[1] )
        else:
            ax.set(xlabel = final_variables[0] , ylabel = final_variables[1] )
        return ax



    def plot_angle_parameters(self , plane, values = None, ax=None, **kwargs) :

        if ax is None :
            fig, ax = plt.subplots()

        if values is None :
            values = self._res_df.columns
        id_ = np.isclose( (self.results_df.loc[ : , plane ]**2).sum(axis = 1) , 1 )
        res_df_sub = self.results_df.loc[id_].copy()

        res_df_sub["Angle"] =  np.rad2deg(np.mod( np.arctan2( res_df_sub[ plane[1] ] , res_df_sub[ plane[0] ] ) , 2*np.pi))
        res_df_sub.set_index("Angle").sort_index().loc[:, values ].plot(ax=ax, **kwargs)
        ax.set(ylabel = "Projected value", xlabel = f"Angle ( atan2( {plane[1]:} , {plane[0]:}) )" )
        return ax



    def plot_projection_2d( self , variables , rp ,final_variables = None, ax = None, transform_dict = {} , backend = "matplotlib", ci_level = None, low_high = None, **kwargs ) :
        """Plot the 2D projection of the contour.

        Parameters
        ----------
        variables : list(str)
            Space in which the convex contour is calculated
        rp : float
            Return period
        final_variables : TYPE, optional
            Space in which the contour is plotted. The default is set to variables.
        transform_dict : dict, optional
            Dictionary of function to ease variable change. The default is {}.
        backend : str, optional
            Library used to plot. The default is "matplotlib".
        **kwargs : any
            Argument passed to the plotting function.
            
        Returns
        -------
        ax : TYPE
            The figure
        """
        if final_variables is None :
            final_variables = variables
            
        cont = self.projected_contour(variables, rp, final_variables=final_variables, transform_dict = transform_dict, ci_level = ci_level, low_high = low_high)
    
        x, y = final_variables

        if backend == "matplotlib" :
            if ax is None :
                fig, ax = plt.subplots()
            ax.plot( cont.loc[:,x] , cont.loc[:,y] , **kwargs )
            ax.set(xlabel = cont.columns[0] , ylabel = cont.columns[1] )
            return ax
        elif backend == "plotly" :
            from plotly import express as px
            ax = px.line( data_frame = cont , x = x, y = y )
            return ax



    def plot_projection_3d(self, variables,  rp , ax = None, final_variables = None, transform_dict = {}, backend = "matplotlib", **kwargs):
        """Plot the 3D projection of the contour.

        Parameters
        ----------
        variables : list(str)
            Space in which the convex contour is calculated
        rp : float
            Return period
        final_variables : TYPE, optional
            Space in which the contour is plotted. The default is set to variables.
        transform_dict : dict, optional
            Dictionary of function to ease variable change. The default is {}.
        backend : str, optional
            Library used to plot. The default is "matplotlib".
        **kwargs : any
            Argument passed to the plotting function.
            
        Returns
        -------
        ax : TYPE
            The figure
        """
        cont, tri = self.projected_contour(variables, rp, final_variables=final_variables, transform_dict = transform_dict, return_triangulation = True)

        tri = orient_normals( cont.values, tri )

        if backend == "plotly" :
            import plotly.figure_factory as ff

            fig = ff.create_trisurf(x=cont.iloc[:,0], y=cont.iloc[:,1], z=cont.iloc[:,2],
                                 simplices = tri ,
                                 plot_edges = False, **kwargs)
            
            fig.layout.scene.xaxis.title, fig.layout.scene.yaxis.title, fig.layout.scene.zaxis.title = final_variables
            fig.show()
        else :
            if ax is None:
                fig = plt.figure()
                ax = fig.add_subplot(projection='3d')
            ax.plot_trisurf(  cont.iloc[:,0], cont.iloc[:,1], cont.iloc[:,2] , triangles = tri, **kwargs )
            ax.set(xlabel = final_variables[0] , ylabel = final_variables[1] , zlabel = final_variables[2])
        return ax


    def plot_data_2d( self, variables , transform_dict = {}, ax = None, backend = "matplotlib", **kwargs ):
        """Plot the 2D projection of the contour.

        Parameters
        ----------
        variables : list(str)
            Space in which the data are plotted.
        transform_dict : dict, optional
            Dictionary of function to ease variable change. The default is {}.
        backend : str, optional
            Library used to plot. The default is "matplotlib".
        **kwargs : any
            Argument passed to the plotting function.

        Returns
        -------
        ax : TYPE
            The figure
        """

        df = self._variable_change(self._df.copy(), variables, transform_dict)
        x, y = variables

        if len(variables) > 2 :
            color = variables[2]
        else:
            color = None

        if backend == "plotly" :
            import plotly.express as px
            fig = px.scatter( data_frame = df , x = x , y = y, color = color, **kwargs )
            if ax is not None :
                import plotly.graph_objects as go
                fig = go.Figure(data = fig.data + ax.data , layout = ax.layout)
            return fig
        else :
            import seaborn as sns
            if ax is None :
                fig, ax = plt.subplots()
            sns.scatterplot(data = df, x = x  , y = y  , hue = color , ax = ax, **kwargs)
            return ax


    def plot_univariate(self, i_direction, ax=None, fit_kwargs={}, data_kwargs={}):
        if ax is None :
            fig, ax = plt.subplots()

        self._fit_objects[i_direction].plot_rp_fit(ax=ax, **fit_kwargs)
        self._fit_objects[i_direction].plot_rp_data(ax=ax, **data_kwargs)

        t = [ f"{c:} = {self._direction_vector.loc[ i_direction, c ]:.2f}" for c in self._direction_vector.columns ]
        ax.set( title = ";".join(t) )
        return ax



    def plot_tangent(self, variables, rp, ax = None, scale = "original", transform_dict = {}, **kwargs ) :
        """Plot the tangents to the contour

        Parameters
        ----------
        variables : tuple
            Variable to plot, currently has to be in the variables in which the contour is calculated.
        rp : float, optional
            Return period to plot. The default is None.
        ax : plt.Axis, optional
            Where to plot the figure. The default is None.
        scale : str , optional
            sd

        Returns
        -------
        ax : matplotlib axe, optional
            The graph

        """
        from Snoopy import PyplotTools as dplt

        self.rp_projections( rp )

        if ax is None :
            fig, ax = plt.subplots()

        if variables[0] in self._df.columns and variables[1] in self._df.columns :
            var_change = False
            n = 2
        else : 
            n = 30
            raise(NotImplementedError)

        v1List = np.linspace(self._df[ variables[0]+ "_a"] .min(), self._df[ variables[0]+ "_a"] .max() , n)
        v2List = np.linspace(self._df[ variables[1]+ "_a"] .min(), self._df[ variables[1]+ "_a"] .max() , n)

        colorMap = dplt.getAngleColorMappable(cmap = "hsv")

        if scale != "original" :  # Plot scaled space
            f1 = f2 = lambda x:x  
            label_suf = "_a"
        else : # Plot original space
            f1 = lambda x : self.std_dict[ variables[0] ] * x + self.mean_dict[ variables[0] ]
            f2 = lambda x : self.std_dict[ variables[1] ] * x + self.mean_dict[ variables[1] ]
            label_suf = ""

        for d in self._direction_vector.index :
            ct = self._direction_vector.loc[d, variables[0] +"_a" ]
            st = self._direction_vector.loc[d, variables[1] +"_a"]

            x_v = self._res_df.loc[ d, rp ]

            if (ct != 0)  :
                v2t = v2List
                v1t = ((x_v - v2List * st) / ct)
            else :
                v2t = (x_v - v1List * ct) / st
                v1t = v1List
            angle = np.mod( np.arctan2( ct, st ), 2*np.pi)
            ax.plot( f1(v1t) ,f2(v2t), color = colorMap.to_rgba( angle ), **kwargs)
        ax.set(xlabel = variables[0]+label_suf, ylabel = variables[1]+label_suf, xlim = [ f1(np.min(v1List)), f1(np.max(v1List))] , ylim = [ f2(np.min(v2List)), f2(np.max(v2List))] )
        

    def plot_voronoi_2d(self, rp, *args, **kwargs):
        """Plots Voronoi diagram
        """
        from scipy.spatial import voronoi_plot_2d

        if self.ndim !=2 : 
            raise(Exception("plot_voronoi_2d only available for 2D contours"))

        if rp not in self._vor :
            self.extract_contour(rp=rp)

        return voronoi_plot_2d(self._vor[rp], *args, **kwargs)

    @staticmethod
    def plot_2d_convex_hull(points_df, final_variables = None, ax = None, transform_dict = {}, **kwargs):
        if ax is None :
            fig, ax = plt.subplots()
        chull = ConvexHull(points_df.values)

        if final_variables is not None:
            final_points = _DirectIformABC._variable_change( points_df,  final_variables, transform_dict = transform_dict ).loc[:,final_variables ].values
        else :
            final_points =  chull.points

        label = kwargs.pop("label" , None)
        for i, d in enumerate(chull.simplices) :
            ax.plot( final_points[d,0], final_points[d,1], label = label if i == 0 else None, **kwargs )
        return ax



def orient_normals( vertices, faces ) :
    """Orient the normals of a convex hull towards the exterior
    """
    faces = np.array(faces)
    tris = vertices[faces]

    # Calculate the normals
    n = np.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )
    centers = np.mean( tris - np.mean(vertices) , axis = 1 )
    id_ = np.diag( np.matmul( centers, np.transpose(n) )   ) > 0
    faces_oriented = np.array(faces)
    faces_oriented[ id_ , 2 ]  = faces[ id_ , 1 ]
    faces_oriented[ id_ , 1 ]  = faces[ id_ , 2 ]
    return faces_oriented



class DirectIform( _DirectIformABC ) :
    """Specialisation of DirectIform when univariate fits are performed using POT and GP fit
    """

    def __init__(self, df, npoints, duration, window_int = None, window = None, threshold_q = 0.9, pot_kwargs = {}):
        """Compute direct IFORM contour, using POT with GP as univariate fit.

        Parameters
        ----------
        df : pd.DataFrame
            The input data
        npoints : int
            Discretisation for all dimensions.
        duration : float
            Duration corresponding to the input data
        window_int : int, optional
            Minimum window used to decluster the data. The default is None.
        window : TYPE, optional
            Minimum window used to decluster the data, in df.index scale. The default is None.
        threshold_q : float, optional
            Quantile to use for the threshold. The default is 0.9.


        Example
        -------
        >>> diform_2d = DirectIform( df.loc[: , ["Hs**0.5" , "Tm" ] ], npoints = 11 , window_int= 48 , duration = len(df) / (24*365), threshold_q = 0.9  )
        >>> diform_2d.fit_projections( )
        >>> contour_df = diform_2d.extract_contour( rp = 25.0 )
        """

        _DirectIformABC.__init__(self , df = df , npoints = npoints )
        self.window_int = window_int
        self.window = window
        self.threshold_q = threshold_q
        self.duration = duration
        self._pot_kwargs = pot_kwargs


    def _create_univariate(self , se  ):
        """Univariate fit, return POT_GPD
        """
        declust = rolling_declustering(se , window_int = self.window_int , window = self.window)

        threshold = np.quantile(declust , self.threshold_q )

        pot = POT_GPD( declust , duration = self.duration, threshold = threshold, **self._pot_kwargs  )

        pot._fit()

        return pot
    
    
    def refit_projections(self, dir_ids, **kwargs):
        """Re-fit selected direction using alternate miminizer options.

        Parameters
        ----------
        dir_ids : np.ndarray
            Array of direction ids. 
        **kwargs : any
            Arguments passed to the _fit() method of the univariate class. (x0 and fit_kwargs for POT_GPD for instance).
        """

        dir_vector_pos = self._direction_vector.index.values[ dir_ids ]
        for i in tqdm(dir_vector_pos, desc = "Re-fitting projections"):
            self._fit_objects[i]._fit( **kwargs )
            
        self._reset_cached_data()


    def select_inf_nnlf(self):
        """Return projection for which likelyhood is zero.
        """
        return self.fit_df.loc[ ~np.isfinite( self.fit_df.NNLF ) ].index
        
        


    def _clear_optional_data(self):
        """Remove projected data to save memory
        """
        for f in self._fit_objects:
            f.clear_data()


    @property
    def fit_df(self) :
        return pd.DataFrame( index=self._direction_vector.index , data = { "THRESHOLD" : [ pot.threshold for pot in self._fit_objects],
                                                                           "SCALE" : [ pot.scale for pot in self._fit_objects],
                                                                           "SHAPE" : [ pot.shape for pot in self._fit_objects],
                                                                           "NNLF" : [ pot.nnlf for pot in self._fit_objects],
                                                                           "KS-PVALUE" : [ pot.ks for pot in self._fit_objects],
                                                                         } )





class DirectIformBM( _DirectIformABC ) :
    """Specialisation of DirectIform when univariate fits are performed using POT and GP fit
    """

    def __init__(self, df, npoints, block_size, bm_kwargs = {}):
        """Compute direct IFORM contour, using GEV on block maxima as univariate fit.

        Parameters
        ----------
        df : pd.DataFrame
            The input data
        npoints : int
            Discretisation for all dimensions.
        """

        _DirectIformABC.__init__(self , df = df , npoints = npoints )
        self.block_size = block_size
        self._bm_kwargs = bm_kwargs


    def _create_univariate(self , se ) :
        bm = BM_GEV.FromTimeSeries( se, block_size = self.block_size , **self._bm_kwargs )
        bm._fit()
        return bm


    def _clear_optional_data(self):
        """Remove projected data to save memory
        """
        pass


    @property
    def fit_df(self) :
        return pd.DataFrame( index=self._direction_vector.index , data = { "LOC" : [ bm.loc for bm in self._fit_objects],
                                                                           "SCALE" : [ bm.scale for bm in self._fit_objects],
                                                                           "SHAPE" : [ bm.shape for bm in self._fit_objects],
                                                                           "NNLF" : [ bm.nnlf for bm in self._fit_objects],
                                                                          } )



def direction_vector( ndim, npoints, mirror = "add_negative" ) :
    """Compute directtion vector to use for direct IFORM (or direct sampling) calculations
    """
    dims = list(range(ndim))
    df = pd.DataFrame( index = pd.MultiIndex.from_product( [ np.linspace(0,1, npoints) for n in range(ndim) ], names = dims ) , columns = ["sum"])
    df["sum"] = df.reset_index().loc[:, dims].sum(axis = 1).values
    res = df.loc[ np.isclose( df["sum"] , 1.0 ) , : ].reset_index().loc[ :,dims ]

    n_expected = comb(npoints+ndim-2,ndim-1, exact = True)

    if len( res ) != n_expected :
        raise(Exception( "Problem in finding the correct number of point on the sphere of radius = 1" ))

    # Add negative side if required
    if type(mirror) == str :
        mirror = [mirror for i in range(ndim)]

    for idim in range(ndim) :
        if mirror[idim] == "add_negative" :
            dup = res.loc[ res.loc[ : , idim ] > 0 ].copy()
            dup.loc[: , idim ] *=-1
            res = pd.concat( [res, dup ]  )
    res.reset_index(inplace = True, drop = True)

    # Normalize
    res = res.div( ((res**2).sum(axis = 1)**0.5), axis = 0 )

    return res

    """Alternate way using spherical coordinates
    from Snoopy.Math.spherical_coordinates import t_to_x
    df = pd.DataFrame( index = pd.MultiIndex.from_product( [ np.linspace(0 , np.pi, npoints) for n in range(ndim-2) ] + [np.linspace(0 , 2*np.pi, npoints*2)] ) , columns = ["r"])
    df["r"] = 1
    angles = df.reset_index().loc[:, ["r"] + [f"level_{i:}" for i in range(ndim-1) ]].values
    res = np.empty( ( len(df) , ndim  ) , dtype = float ) 
    for i_point in range(len(df)): 
        res[i_point , :] = t_to_x( angles[i_point] )
    return pd.DataFrame(data = res)
    """

def l2_norm_constraint(direction) : 
    c = np.sum( direction**2 )**0.5 - 1.
    logger.debug( f"Constraint = {c:}")
    return c

def l2_norm_jac( v ):
    return [ 2*v[i] / (2*np.sum(v**2)**0.5) for i in range(len(v)) ]


def slice_convhull( conv_hull, cut_dim, slice_value ):
    """Calculate intersection point of a convex hull

    Parameters
    ----------
    conv_hull : ConvexHull
        The hyper-surface to cut
    cut_dim : int
        The dimension in which the cut is performed
    slice_value : float
        Value at which to slice

    Returns
    -------
    intersection_point : np.ndarray
        The intersection point
    """

    # Find cutted simplices
    x_min = conv_hull.points[ conv_hull.simplices , cut_dim  ].min(axis = 1)
    x_max = conv_hull.points[ conv_hull.simplices , cut_dim  ].max(axis = 1)
    cutted_simplices = conv_hull.simplices[ np.where( (x_min < slice_value) &  (x_max >= slice_value) ) ]

    # Find edges of cutted simplices
    permutation = list(itertools.combinations( np.arange(conv_hull.ndim), 2))
    edges = np.concatenate(  [ cutted_simplices[: , permutation[i]] for i in range(len( permutation )) ] )

    # Find cutted edges of cutted simplices
    x_min_e = conv_hull.points[ edges, cut_dim ].min(axis = 1)
    x_max_e = conv_hull.points[ edges, cut_dim ].max(axis = 1)
    cutted_edges = edges[ np.where( (x_min_e < slice_value) &  (x_max_e >= slice_value) ) ]


    #Interpolate the intersection points
    alpha =  (conv_hull.points[ cutted_edges[:,1], cut_dim ] - slice_value) / np.diff( conv_hull.points[ cutted_edges, cut_dim ], axis = 1)[:,0]
    intersection_point = np.zeros( (len(cutted_edges) , conv_hull.ndim-1) )
    for idim in range(conv_hull.ndim-1):
        intersection_point[:, idim] = alpha * conv_hull.points[ cutted_edges[:,0], idim ]   + (1-alpha)*conv_hull.points[ cutted_edges[:,1], idim ]

    intersection_point = np.unique( intersection_point, axis = 0 )

    return intersection_point


def slice_convhull_df( points_df, slice_dim, slice_value ):
    """Same as slice_convhull, but with dataframe as input and output
    """
    conv_hull = ConvexHull( points_df )
    points = slice_convhull( conv_hull , cut_dim = points_df.columns.get_loc(slice_dim), slice_value=slice_value )
    contour_slice = pd.DataFrame( columns = points_df.columns.drop(slice_dim).values , data = points )
    return contour_slice
