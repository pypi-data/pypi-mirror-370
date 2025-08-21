import anndata as ad
import numpy as np
import scipy

def calc_jasmine_score(
    adata: ad.AnnData, 
    genes: list[str],
    layer: str = None,
    recalculate_rank: bool = False,
    save_rank: bool = True
): 
    """
    Calculates the JASMINE gene set score,
    originally proposed in Noureen et al. 2022.

    Shows less (but non-zero) dependence on gene 
    detection rate than alternative methods for gene
    set scoring in scRNA-seq data.
    
    Parameters
    ----------

    adata: ad.AnnData
        The AnnData object

    genes: list of str
        The keys in adata.var.index to score

    layer: str (default: None)
        The key in adata.layers to pull the gene
        expression matrix from. If None, defaults
        to adata.X

    recalculate_rank: bool (default: False)
        If `ranks_nonzero` is in adata.layers.keys(), 
        then recalculate the gene ranks before 
        calculating JASMINE score. 

    save_rank: bool (default: True)
        Write the (sparse matrix) result of gene ranking
        to adata.layers["ranks_nonzero"] to remove the 
        need for recomputation.

    Returns
    -------
    
    jasmine_score: np.ndarray
        1D array of len(adata.obs.index) of gene set 
        scores, min-max normalized to [0,1]. 

    References
    ----------

    * https://doi.org/10.7554/eLife.71994
    
    * https://github.com/NNoureen/JASMINE

    Usage
    -----
    .. code-block::

        >>> genes_of_interest = ["Sftpc", "Lamp3", "Napsa"]
        >>> adata.obs["AT2 score"] = calc_jasmine_score(adata, genes_of_interest)
        >>> adata.obs.groupby("celltype")["AT2 score"].mean().idxmax()
        'AT2'

    """

    # get the normalized mean rank (NMR)
    NMR = _calc_mean_rank(
        adata, 
        genes,
        layer=layer,
        recalculate_rank=recalculate_rank,
        save_rank=save_rank
    )

    # get the likelihood ratio (LR)
    LR = _calc_likelihood_ratio(
        adata,
        genes,
        layer=layer
    )

    # calculate score
    jasmine_score = (NMR + LR) / 2
    jasmine_score = (jasmine_score - np.min(jasmine_score)) / np.ptp(jasmine_score)
    return jasmine_score


def _calc_mean_rank(
    adata, 
    genes, 
    layer=None,
    recalculate_rank=False,
    save_rank=True
):
    # get the gene expression matrix
    if (layer):
        X = adata.layers[layer]
    else:
        X = adata.X
    X = scipy.sparse.csr_matrix(X)
    
    # get indices of genes of interest
    gene_idx = [adata.var.index.get_loc(g) for g in genes]
        
    # rank the data
    if (("ranks_nonzero" in adata.layers.keys())
    and not (recalculate_rank)):
        ranks_nonzero = adata.layers["ranks_nonzero"]
    else:
        ranks_nonzero = scipy.sparse.csr_matrix(
            (scipy.stats.rankdata(X.data), X.indices, X.indptr),
            shape=X.shape
        )
        if (save_rank):
            adata.layers["ranks_nonzero"] = ranks_nonzero 

    # calculate the mean ranks for the gene set
    mean_ranks_nonzero = np.mean(
        ranks_nonzero[:, gene_idx],
        axis=1
    )

    # calculate the number of genes expressed per cell
    n_genes_in_cell = np.sum(
        X.astype(np.bool_),
        axis=1
    )
    
    # return the normalized mean-ranks
    return (mean_ranks_nonzero / n_genes_in_cell).data

def _calc_likelihood_ratio(
    adata,
    genes,
    layer=None
):
    # LR = a * (c + d) / (c * (a + b))
    # where:
    # a: number of signature genes detected
    # b: number of signature genes not detected
    # c: number of non-signature genes detected
    # d: number of non-signature genes not detected
    
    # get the gene expression matrix
    if (layer):
        X = adata.layers[layer]
    else:
        X = adata.X
    X = scipy.sparse.csr_matrix(X)
    
    # get indices of genes of interest
    gene_idx = [adata.var.index.get_loc(g) for g in genes]
    
    # calculate number of signature genes detected
    a = np.asarray(np.sum(
        X[:, gene_idx].astype(np.bool_),
        axis=1
    ))
    
    # calculate number of signature genes not detected
    b = (len(genes) - a)

    # calculate number of non-signature genes detected
    mask = np.ones(X.shape[1], dtype=np.bool_)
    mask[gene_idx] = False
    
    c = np.asarray(np.sum(
        X[:, mask].astype(np.bool_),
        axis=1
    ))
    
    # calculate number of non-signature genes not detected
    d = (X.shape[1] - c)

    # calculate the LR
    return (a * (c + d)) / (c * (a + b))