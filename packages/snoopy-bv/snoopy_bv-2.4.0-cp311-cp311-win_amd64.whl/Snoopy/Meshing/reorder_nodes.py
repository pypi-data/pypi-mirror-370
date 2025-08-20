import numpy as np
import pandas as pd


class ReorderNodes():

    def __init__(self, nodes_0, decimals = 2):
        """Re-order point of an identical grid for which the points IDs have been shuffled.
        
        Some tolerance can be allowed to find back points. 

        Parameters
        ----------
        nodes_0 : np.ndarray
            Reference grid (n,3) array
        tol : int
            Tolerance, as number of digit kept to "merge" node coordinates. 
            
        Example
        -------
        >>> r = ReorderVtkNodes( ref_grid, tol = 2 )
        >>> ids = r.get_ids( grid )
        >>> # ==> to get field at ref_grid, they needs to be looked at "ids" position in grid.
        """
        self.decimals = decimals
        self.node_0 = nodes_0
        hash2_0 = np.array([hash(tuple(r)) for r in np.round(self.node_0,decimals) ])
        
        # Rounding with a shift of 0.5 tolerance, so that, for instance 0.554 and 0.556 are considered the same with tol = 2
        # Is this silly ?
        hash0_0 = np.array([hash(tuple(r)) for r in np.round( np.round(self.node_0 - 0.5*10**(-decimals) ,decimals)+0.5*10**(-decimals) , decimals ) ])
        
        # hashm1_0 = np.array([hash(tuple(r)) for r in np.round(self.node_0,-1) ])
        self.se_0 = pd.DataFrame(  data = { "hash0_0" : hash0_0, "hash2_0" : hash2_0 , "index_0" : np.arange(len(self.node_0))} )
        
    def get_ids( self, nodes ):
        """Get the nodes ids that corresponds to grid_0

        Parameters
        ----------
        nodes : np.ndarray
            Grid (m,3) array.

        Returns
        -------
        new_index : np.ndarray
            Array of indices, length is the length of the original grid (n).
        """
        decimals = self.decimals
        node_ = nodes
        hash2_ = np.array([hash(tuple(r)) for r in np.round(node_,decimals) ])
        hash0_ = np.array([hash(tuple(r)) for r in np.round( np.round(node_ - 0.5*10**(-decimals) ,decimals)+0.5*10**(-decimals) , decimals ) ])

        val_ = pd.DataFrame(  data = {"hash0" : hash0_ , "hash2" : hash2_, "c_index" : np.arange(len(node_))})
        
        # Find node with same hash.
        tmp = self.se_0.merge(right = val_, left_on = "hash2_0", right_on = "hash2", how = "left"  )
        not_found = tmp.loc[ tmp["c_index"].isna() , "index_0"].values
        
        # For remaining nodes, same but with "shifted" rounding.
        if len(not_found)> 0 :
            tmp2 = self.se_0.loc[not_found].merge(right = val_, left_on = "hash0_0", right_on = "hash0", how = "left"  )
            tmp2 = tmp2.set_index("index_0")
            tmp2 = tmp2.loc[ ~tmp2.index.duplicated(keep='first') ]
            tmp.loc[ not_found ] = tmp2.loc[not_found]
        tmp.loc[ tmp["c_index"].isna() , "index_0"] = tmp.loc[ tmp["c_index"].isna(), :].index.astype(int)
        not_found2 = tmp.loc[ tmp["c_index"].isna() , "index_0"].values.astype(int)
 
        # Remaining item with double loop (a bit slow if a lot of nodes are to be found).
        if len( not_found2 ) > 100: 
            print("Warning : lot of point to be found with double loop, consider increasing tolerance" , len(not_found2))
    
        for i_missing in not_found2 :
            i_close = np.argmin(np.linalg.norm( self.node_0[i_missing] - node_, axis = 1))
            tmp.loc[i_missing] = i_close

        new_index = tmp["c_index"].astype(int).values
        max_dist =  np.max(np.linalg.norm( self.node_0 - node_[new_index] ))

        if max_dist > 10**(-decimals+1) : 
            print("Max distance much larger than tolerance" , max_dist)

        return new_index


if __name__ == "__main__" : 
    
    nodes_0 = np.array( [ [ x,x,x] for x in np.linspace(1,10,200) ] )
    ro = ReorderNodes( nodes_0 ,decimals=2 )
    order = np.arange(0,len(nodes_0),1)
    np.random.shuffle(order)
    nodes = np.array( nodes_0[order] )
    nodes += np.random.random() * 0.001
    t = ro.get_ids( nodes )
    assert( np.isclose( order[t]  , np.arange(0,len(nodes_0),1) ).all() )

    
    
    