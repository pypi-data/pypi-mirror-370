import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from natsort import natsorted

from ..utilities._truncate_colormap import truncate_colormap

def plot_gprofiler_results(
    ora_df: pd.DataFrame,
    title: str = "",
    cmap: bool = "Blues",
    n_terms: int = 15,
    sort_by: str = "fold_enrichment",
    min_FE: int = 0
):
    """
    Generates a barplot representing gProfiler
    ORA results, with: 
    `x = -log10(FDR)` 
    `y = term name`
    `color = term fold enrichment`
    
    Parameters
    ----------
    
    ora_df: pandas.DataFrame
        The results of a gProfiler ORA.
        
    title: str (default: "")
        The base title of the plot; may 
        be modified if iterating over
        gProfiler data sources
        
    cmap: str (default: "Blues")
        The matplotlib colormap to map to the 
        color parameter (fold-enrichment, FE)
    
    n_terms: uint (default: 15)
        The number of over-represented terms
        to keep for plotting, ranked by term
        fold enrichment (FE)
    
    sort_by: str (default: 'fold_enrichment')
        Sort the statistically significant terms by
        term fold enrichment (FE), i.e. 
        `(n_in_term/n_expected_in_term)`
        before cutting off to top n_terms. 
        If `FDR`, sort instead by statistical
        significance alone.
    
    min_FE: uint (default: 0)
        Ignore terms if their term fold enrichment
        is below this minimum value.
    
    Returns
    -------
    
    fig: matplotlib.Figure
        The resulting figures, one per source,
        aligned vertically.
    """

    # Determine how many subplots to make and create the axes
    n_sources = len(ora_df["source"].unique())

    fig, axs = plt.subplots(n_sources,1, figsize=(10,7*n_sources))
    axs = axs.ravel()


    for i,source in enumerate(natsorted(ora_df["source"].unique())):
        # filter to just this source
        d = ora_df[ora_df["source"]==source]
        if (len(d) < 2):
            continue

        # remove 'match class' terms, which are often duplicates of TF terms
        d = d[~d["name"].str.contains("match class")]

        # calculate term fold enrichment
        d["n_in_term"] = d["intersection_size"].tolist()
        d["n_expected_in_term"] = d["query_size"] * d["term_size"]
        d["n_expected_in_term"] /= d["effective_domain_size"]
        d["FE"] = d["n_in_term"] / (0.05 + d["n_expected_in_term"])

        # calculate -log10(p_adj)
        # gProfiler automatically converts to FDR/p_adj, then re-labels as pvals
        d["FDR"] = d["p_value"] 
        d["-log10(FDR)"] = -1 * np.log10(d["FDR"])

        # clean up term names for compactness
        max_len = 50
        if (source == "TF"):
            d["name"] = d["name"].apply(lambda x: _shorten_TF_term(x, max_len))
        elif ("GO:" in source):
            d["name"] = d["name"].apply(lambda x: _shorten_GO_term(x))
        
        # remove low term fold enrichment terms
        df = d[d["FE"] >= min_FE]

        # sort before cutting to top n_terms
        if (sort_by == "fold_enrichment"):
            df = df.sort_values("FE", ascending=False)
        elif (sort_by == "FDR"):
            df = df.sort_values("FDR", ascending=True)
        
        data = df.head(n_terms)
        data = data.sort_values("FDR", ascending=False)
        
        # generate a pleasant colormap to represent term fold enrichment
        color_facet = "FE"

        new_cmap = truncate_colormap(
            matplotlib.colormaps.get_cmap(cmap),
            minval=0.4,
            maxval=0.9
        )
        raw_vals = data[color_facet].to_numpy()
        vals = (raw_vals - np.min(raw_vals)) / (np.ptp(raw_vals))
        cvals = [new_cmap(v) for v in vals]

        # draw the bars
        axs[i].barh(
            data["name"], 
            data["-log10(FDR)"], 
            color=cvals,
            edgecolor="black", 
            linewidth=2
        )

        # format the graph
        axs[i].set_xlabel("-log10(FDR)")
        axs[i].set_ylabel(source)
        axs[i].set_title(title.replace("gProfiler_", "").replace("_", " "))
        axs[i].grid(False)

        # add the colorbar and map reasonable integer values to its ticklabels
        cbar = fig.colorbar(
            matplotlib.cm.ScalarMappable(cmap=new_cmap),
            ticks=[0,0.5,1],
            ax=axs[i],
        )
        cbar_tickmarks = [
            int(round(np.min(raw_vals),0)),
            int(round((np.min(raw_vals) + np.max(raw_vals))/2,0)),
            int(round(np.max(raw_vals),0))
        ]
        raw_val_range = np.ptp(raw_vals)
        if (raw_val_range < 3):
            cbar_tickmarks[0] = cbar_tickmarks[0] - 1
            cbar_tickmarks[2] = cbar_tickmarks[2] + 1
        
        cbar.ax.set_yticklabels(cbar_tickmarks)
        cbar.ax.set_ylabel("Term fold enrichment")

        # set the font sizes to something appropriate
        # TODO: is there a better way to parametrize this?
        for item in (
            [axs[i].title, axs[i].xaxis.label, axs[i].yaxis.label] 
            + axs[i].get_xticklabels()
            + axs[i].get_yticklabels()
            + [cbar.ax.title, axs[i].xaxis.label, axs[i].yaxis.label]
            + cbar.ax.get_xticklabels()
            + cbar.ax.get_yticklabels()
        ):
            item.set_fontsize(20) 

    return fig


def _shorten_GO_term(x):
    ret = x.replace("ositive", "os.")
    ret = ret.replace("egative", "eg.")
    ret = ret.replace("egulation", "eg.")
    return ret

def _shorten_TF_term(x, max_len):
    ret = x.split("Factor: ")[1]
    ret = ret.replace(";","")
    ret = ret.rjust(max_len)
    return ret