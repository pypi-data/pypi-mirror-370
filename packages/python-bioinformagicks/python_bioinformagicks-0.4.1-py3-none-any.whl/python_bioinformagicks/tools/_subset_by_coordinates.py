import anndata as ad
import numpy as np

def subset_by_coordinates(
    adata: ad.AnnData,
    x_bounds: list = [],
    y_bounds: list = [],
    use_rep: str = "X_umap"
):
    """
    Given a bounding box in 2D space,
    return a cell mask containing only
    cells inside of that box.
    
    Useful for subsetting data using a 
    UMAP/other projection based on location
    rather than categorical/quantitative 
    conditions (i.e. "I want cells from that
    bottom-right corner cluster only.")
    
    TODO: generalize to other/arbitrary 
    bounding shapes
    
    Parameters
    ----------
    adata: ad.AnnData
        The parent anndata object to subset
    
    x_bounds: list/tuple (default: [])
        The minimum and maximum bounds of the 
        bounding box along the x-axis, i.e.
        `[x_min, x_max]`. Expressed as a 
        fraction of the axis' actual
        minimum and maximum span, i.e. in the
        range `[0,1]`.
    
    y_bounds: list/tuple (default: [])
        As for x_bounds, but along the y-axis
    
    use_rep: str (default: "X_umap")
        The projection to subset on. Only the 
        first 2 dimensions of this projection
        are used during subsetting.
    
    Returns
    -------
    mask: np.ndarray 
        The boolean mask on length adata.n_obs
        where cells within the bounding area 
        are given value True, else False.
    """
    
    if not (x_bounds or y_bounds):
        print("At least one of x_bounds, y_bounds must "
            + "be specified to subset.")
        return None
    
    # get the projection coordinates
    X = adata.obsm[use_rep]
    
    # rescale to relative (min/max) coordinates
    for i in [0,1]:
        X[:,i] = (X[:,i] - np.min(X[:,i])) / np.ptp(X[:,i])
    
    # keep all cells to start
    mask = np.ones_like(X[:,0], dtype=np.bool_)
    
    # filter based on bounds
    if (x_bounds):
        mask = mask & (X[:,0] >= x_bounds[0]) & (X[:,0] <= x_bounds[1])
    if (y_bounds):
        mask = mask & (X[:,1] >= y_bounds[0]) & (X[:,1] <= y_bounds[1])
    
    # let the user know approximately how many cells made it through filters
    print(
        str(round(np.sum(mask) * 100 / len(mask), 3)) + 
        "% of cells in bounding area"
    )
    return(mask)