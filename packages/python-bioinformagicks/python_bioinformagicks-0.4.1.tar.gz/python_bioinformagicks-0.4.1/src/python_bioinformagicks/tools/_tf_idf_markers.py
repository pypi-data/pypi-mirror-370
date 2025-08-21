"""
Code for identifying marker genes based on
term-frequency, inverse-document frequency
testing (TF-IDF).
"""

import scanpy as sc
import anndata as ad

import pandas as pd
import numpy as np

from scipy.stats import (
    hypergeom,
    rankdata
)

def tf_idf_markers(
    adata: ad.AnnData, 
    groupby: str, 
    n_genes: int = 10, 
    n_genes_to_plot: int = 10, 
    redo_threshold: bool = False,
    dendrogram: bool = False, 
    save_markers: bool = False, 
    return_fig: bool = False,
    var_key_to_ignore: str = None,
    **kwargs
):
    """
    Performs term-frequency, inverse-document frequency 
    calculation in order to rank marker genes across
    groups in groupby. This is an alternative to mean expression
    based DEG testing that prioritizes uniqueness of genes 
    over fold-change in expression across groups. 

    TODO: make compatible with :code:`scanpy.tl.rank_genes_groups`
    
    Parameters
    ---------
    adata: ad.AnnData
        The anndata object for this experiment
    
    groupby: str
        The column in adata.obs that we will split the 
        data on for the TF-IDF test. 
        
    n_genes: int > 0 (default: 10)
        The number of top genes per group to return 
        in the marker gene dictionary
    
    n_genes_to_plot: int in range (0, n_genes] (default: 10)
        The number of genes per group to plot in the 
        resulting dotplot. Set to 0 to disable plot generation.
    
    redo_threshold: bool (default: False)
        If :code:`adata.layers["binary"]` exists, redo the 
        calculation of the binary matrix. Possibly useful 
        when performing TF-IDF ranking on a subset of adata.
        
    save_markers: bool (default: False)
        If True, store the marker gene matrix in the adata
        object as :code:`adata.uns["TF_IDF_" + groupby]`
            
    return_fig: bool (default: False)
        If True, output of this function changes to a tuple
        of dict, dpl (dotplot object from scanpy) instead
        of just dict. Otherwise, dotplot is generated and
        shown but not returned from this function.
    
    var_key_to_ignore: str (default: None)
        The name of a boolean column in adata.var which
        indicates genes that should be ignored during marker
        gene testing (often mitochondrial genes, pseudogenes,
        ribosomal genes, etc.). If `None`, no gene masking
        is performed.
        
    kwargs:
        Arguments passed to :code:`sc.pl.dotplot` 
        (if `n_genes_to_plot>0`)

    Returns
    -------
    marker_dict: dict
        The marker gene dictionary. 
        Keys are :code:`adata.obs[groupby].unique()`
    
    dpl: sc.pl.DotPlot (optional)
        If :code:`plot is True` and :code:`return_fig is True`, 
        scanpy DotPlot object is also returned for 
        further processing/saving.
    
    References
    ----------

    * https://github.com/constantAmateur/SoupX
    * https://doi.org/10.1093/gigascience/giaa151
    * https://constantamateur.github.io/2020-04-10-scDE
    """

    # binarize the gene expression data
    if ((redo_threshold) 
    or ("binary" not in adata.layers.keys())):
        threshold = np.percentile(adata.X.data, 5)
        X = adata.X.copy()
        X.data = np.where(adata.X.data > threshold, 1, 0)
        adata.layers["binary"] = X.copy().astype(np.bool_)
        del X
    
    # get gene (var) mask
    if (var_key_to_ignore in adata.var.columns):
        gene_mask = ~adata.var[var_key_to_ignore].astype(np.bool_)
    else:
        gene_mask = np.array([True for x in adata.var.index])
    
    # calculate the TF matrix
    clusters = adata.obs[groupby].astype("category").cat.categories
    X_clust  = []
    for c in clusters:
        cell_mask = adata.obs[groupby] == c
        expression = np.squeeze(
            np.asarray(
                np.sum(adata[cell_mask, gene_mask].layers["binary"], axis=0)
            )
        )
        X_clust.append(expression)
    cluster_max = np.max(X_clust, axis=1)
    TF = np.asarray(X_clust).T / cluster_max
    TF = TF.T
    
    # calculate the IDF vector
    n_cells = len(adata.obs.index)
    n_cells_expressing_gene = adata[:, gene_mask].layers["binary"].getnnz(axis=0)
    IDF = (np.log2((n_cells + 1) / (n_cells_expressing_gene + 1)))
    
    # calculate the TF-IDF matrix (marker gene scores)
    TF_IDF = TF * IDF
    TF_IDF = pd.DataFrame(
        data=TF_IDF, 
        index=clusters, 
        columns=adata[:, gene_mask].var.index.tolist()
    ).T
    if (save_markers):
        adata.uns["TF_IDF_" + groupby] = TF_IDF
    
    """
    Do hypergeometric test to assign p-values to this
    distribution of gene-cluster frequencies.
    M is the total number of objects, 
    n is total number of Type I objects. 
    N is the number of items selected/draws
    k is the observed number of Type I objects selected/drawn

    Suppose we have a collection of 20 genes, of which 7 are DEGs. 
    Then if we want to know the probability of finding a given number 
    of DEGs if we choose at random 12 of the 20 genes, we can 
    initialize a frozen distribution and plot the probability mass function:
    [M, n, N] = [20, 7, 12]
    """

    k = TF
    M = n_cells
    n = n_cells_expressing_gene
    N = cluster_max
    pvals = {}
    adjusted_pvals  = {}
    for i, c in enumerate(clusters):
        pvals[c] = hypergeom.pmf(k[i], M, n, N[i])
        adjusted_pvals[c]  = _bh_correct(pvals[c])
    adjusted_pvals = pd.DataFrame.from_dict(
        adjusted_pvals, 
        orient="index", 
        columns=adata[:, gene_mask].var.index.tolist()
    ).T
    
    # get the top N genes for each cluster
    target_fdr = 0.05
    top_genes = {}
    top_adjusted_pvals  = {}
    for i, c in enumerate(clusters):
        mask = adjusted_pvals[c] <= target_fdr
        df = TF_IDF[mask].sort_values(c, ascending=False).head(n_genes)
        genes = df.index.tolist()
        genes_idx = [adata[:, gene_mask].var.index.get_loc(g) for g in genes]
        top_genes[c] = genes
        top_adjusted_pvals[c]  = adjusted_pvals[c][genes_idx]
    
    if (n_genes_to_plot > 0):
        if (0 < n_genes_to_plot < n_genes):
            plot_me = {}
            for k in clusters:
                plot_me[k] = top_genes[k][0:n_genes_to_plot]
        else:
            plot_me = top_genes

        dpl = sc.pl.dotplot(
            adata, 
            plot_me, 
            groupby=groupby, 
            dendrogram=dendrogram,
            return_fig=True,
            **kwargs
        )
        dpl.add_totals(color="lightgray").style(cmap="Reds")
        
        if (return_fig):
            return top_genes, dpl
        else:
            dpl.show()
    
    return top_genes


def _bh_correct(
    pvals: np.array
):
    """
    Perform Benjamini-Hochberg p-value adjustment
    for multiple comparisons.

    Parameters
    ----------

    pvals: np.array (in range [0,1])
        The uncorrected p-values

    Returns
    -------

    adjusted_pvals: np.array (in range [0,1])
        The BH adjusted p-values
    """

    ranked_pvals = rankdata(pvals)
    adjusted_pvals = pvals * len(pvals) / ranked_pvals
    adjusted_pvals[adjusted_pvals > 1] = 1
    return adjusted_pvals