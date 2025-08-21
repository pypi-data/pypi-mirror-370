import scanpy as sc
import anndata as ad

import numpy as np
import scipy

def scale_by_group(
    adata: ad.AnnData,
    groupby: str = "celltype",
    layer: str = None,
    copy: bool = True,
    zero_center: bool = False,
):
    """
    Performs z-standard scaling, similar to
    :code:`sc.pp.scale`, but for each category
    in :code:`adata.obs[groupby]` independently. 
    
    For instance, if :code:`groupby == "celltype"`,
    the resulting data matrix of z-scaled 
    expression values would highlight changes
    from the mean of all cells within each
    celltype (but changes between celltypes 
    would be largely meaningless). 
    
    Parameters
    ----------
    adata: ad.AnnData 
    
    groupby: str (default: "celltype")
        The categorical column in `adata.obs`
        containing groups to subset and standard
        scale within.
    
    layer: str (default: `None`)
        The layer key in `adata.layers` whose 
        values should be scaled (i.e. the starting
        matrix). If `None`, use :code:`adata.X`.
    
    zero_center: bool (default: `False`)
        As in :code:`sc.pp.scale`; when `True`, subtract
        the mean gene expression within each group.
        When `False`, the sparse structure of the gene
        expression data remains.
    
    copy: bool (default: `True`)
        If `True`, return a copy of the resulting
        scaled data matrix. If `False`, modify 
        input `adata` by placing resulting matrix
        in :code:`adata.layers[scaled_by_ + str(groupby)]`.
    
    Returns
    -------
    If :code:`copy is True`, return the scaled matrix.
    
    If :code:`copy is False`, scaled matrix is placed
    in :code:`adata.layers["scaled_by_" + str(groupby)]`,
    which modifies :code:`adata` in-place. 

    If :code:`zero_center is False`, resulting scaled
    matrix is of type :code:`scipy.sparse.csr_matrix`, else
    result is of type :code:`np.ndarray` (dense). 
    """
    
    ret = np.zeros(adata.X.shape)
    
    for group in adata.obs[groupby].astype("category").cat.categories:
        
        # get obs indices of parent adata object
        obs_mask = adata.obs[groupby] == group
        parent_obs_indices = np.nonzero(obs_mask)[0]
    
        # calculated scaled matrix of child object
        # TODO: this assumes X_group_scaled is sparse,
        # need to consider if dense
        X_group_scaled = scipy.sparse.csr_matrix(
            sc.pp.scale(
                adata[obs_mask], 
                zero_center = zero_center,
                layer = layer,
                copy = True
            ).X, 
        ) 
        
        # calculate parent indices
        sparse_indices = np.asarray(X_group_scaled.nonzero())
        sparse_indices[0] = [parent_obs_indices[x] for x in sparse_indices[0]]
        ravelled_sprase_indices = np.ravel_multi_index(
            sparse_indices, 
            adata.X.shape
        )

        # put the calculcated data into the parent matrix
        np.put(
            ret,
            ravelled_sprase_indices,
            X_group_scaled.data,
        )
    
    # save memory by converting to sparse matrix
    # if the result was not zero-centered
    if (zero_center is False):
        ret = scipy.sparse.csr_matrix(ret)
    
    if (copy):
        return ret
    else:
        adata.layers["scaled_by_" + str(groupby)] = ret
        return None