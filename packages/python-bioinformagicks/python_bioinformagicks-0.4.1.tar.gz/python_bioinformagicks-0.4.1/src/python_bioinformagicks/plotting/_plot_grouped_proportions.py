import anndata as ad
import scanpy as sc

import numpy as np

import matplotlib.pyplot as plt

from ..utilities._get_proportions import get_proportions

def plot_grouped_proportions(
    adata: ad.AnnData, 
    factor_to_plot: str,
    split_by: str,
    batch_key: str = "batch",
    stacked: bool = True
):
    
    """
    Generates (stacked) bar plots of item (cell) counts 
    and proportions, with each bar representing how many
    items are in each group of "factor_to_plot"
    across each group of "split_by". Item counts are
    reported on a per-batch basis with batch 
    assignments found in the "batch_key" column of 
    the adata.obs table.

    If adata.uns[split_by + "_colors"] exists, bars will
    be colored to match.
    
    Parameters
    ----------
    
    adata: ad.AnnData 
        The anndata object
    
    factor_to_plot: str
        The factor in adata.obs to generate 
        count/proportion plots for.
        Commonly `celltype`, `leiden`, `cluster`, etc.
    
    split_by: str
        The factor in adata.obs to compare/split
        by, such that groups of count/proportion
        bars are split across this factor. 
        Commonly `condition`, `treatment`, `age`, etc.
    
    batch_key: str (default: "batch")
        The column in adata.obs that indicates 
        the batch an item belongs to. This is used
        to normalize reported counts to item
        counts per batch. Important when some
        conditions are represented by multiple
        batches and others are not so that 
        comparisons between conditions are fairer.
    
    stacked: bool (default: True)
        If True, generate a stacked bar graph, 
        else stagger bars side-by-side. 
        
    Returns
    -------
    
    fig: matplotlib.Figure 
        Contains two axes, one with item counts per 
        batch and one with proportions. 
    
    """
    
    titles = ["# per " + split_by, "proportions"]
    
    obs = adata.obs

    groups = obs[split_by].cat.categories
    
    fig, axs = plt.subplots(
        1,2,
        figsize=(10,5),
        constrained_layout=True
    )
    
    for i in range(0, len(titles)):
        
        # calculate counts/proportions
        if ("#" in titles[i]):
            return_counts = True
            n_samples = obs.groupby(split_by)[batch_key].nunique()
            n_samples = np.asarray(n_samples)
        else:
            return_counts = False
        
        d = get_proportions(
            obs[obs[split_by].isin(groups)],
            outer_col = split_by, 
            inner_col = factor_to_plot,
            return_counts = return_counts
        )
        
        d = d[groups]
        
        if ("#" in titles[i]):
            d = d / n_samples
        
        # generate the bar graphs
        if ((factor_to_plot + "_colors") in adata.uns.keys()):
            d.T.plot.bar(
                stacked = stacked,
                color = adata.uns[factor_to_plot + "_colors"],
                ax = axs[i],
                linewidth = 1,
                edgecolor = "black"
            )
        else:
            d.T.plot.bar(
                stacked = stacked,
                ax = axs[i],
                linewidth = 1,
                edgecolor = "black"
            )

        if (i == (len(titles) - 1)):
            axs[i].legend(bbox_to_anchor=(1.1, 1.05), ncol=1)
        else:
            axs[i].get_legend().remove()
        
        axs[i].set_title(titles[i])
        axs[i].set_axisbelow(True)
        axs[i].yaxis.grid(color='lightgray', linestyle='-')

    return fig