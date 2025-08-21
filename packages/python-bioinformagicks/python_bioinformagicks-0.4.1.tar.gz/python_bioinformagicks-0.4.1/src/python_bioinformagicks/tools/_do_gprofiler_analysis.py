import requests
import pandas as pd

def do_gprofiler_analysis(
    genes: list[str], 
    organism: str = "hsapiens",
    max_term_size: int = 10000,
    ordered: bool = False,
    sources: list[str] = ["GO:BP", "GO:MF", "REAC", "KEGG", "TF"],
    highlight: bool = True,
):
    """
    Given an ordered list of genes,
    performs an over-representation analysis (ORA) 
    using the gProfiler API.
    
    Parameters
    ----------
    
    genes: list of str
        List of genes to query, optionally sorted by user
        based on FDR or another significance metric.
    
    organism: str (default: "hsapiens")
        The organism ID to use for the query.
        See https://biit.cs.ut.ee/gprofiler/page/organism-list
        for a list of organism IDs supported
        by gProfiler. 
        Commonly one of: ["hsapiens", "mmusculus"]
    
    max_term_size: uint (default: 10000)
        Filter results table to only include those
        results with term sizes less than this 
        maximum. Set to None to disable.
    
    ordered: bool (default: False)
        If the list of genes is ordered by
        descending significance, set to True, 
        otherwise set to False. A slightly different 
        ORA is performed on ordered gene lists. 
    
    sources: list of str (default: ["GO\\:BP", "GO\\:MF", "REAC", "KEGG", "TF"])
        The list of source databases to consider for 
        gProfiler ORA. Some may only be available for
        certain organisms; see organism list page in
        the gProfiler documentation for more
        information.

    highlight: bool (default: False)
        If True, request that gProfiler add a 'highlighted'
        column to the resulting dataframe indicating if a 
        given term is a 'driver' term.
        See: https://biit.cs.ut.ee/gprofiler/page/docs#highlight_go    

    Returns
    -------
    ora_df: pandas.DataFrame
        The resulting gProfiler results dataframe.

    References
    ----------

    * https://biit.cs.ut.ee/gprofiler/gost
    * https://doi.org/10.1093/nar/gkad347

    Usage
    -----

    >>> diff_exp_genes = ["SFTPC", "LAMP3", "NAPSA", "SFTPB", "EPCAM", "COL1A1"]
    >>> ora_df = do_gprofiler_analysis(diff_exp_genes, ordered=False)
    >>> print(ora_df.head(1)[["source", "name", "p_value", "intersections"]])
        source                 name   p_value          intersections
    0   REAC  Surfactant metabolism  0.000033  [SFTPC, NAPSA, SFTPB]

    """

    # check if this is an ordered query; if it is, gProfiler
    # API cannot perform highlighting (interesting)
    if (ordered and highlight):
        highlight = False

    res = requests.post(
        url = "https://biit.cs.ut.ee/gprofiler/api/gost/profile/",
        json = {
            "organism": organism,
            "query": genes,
            "sources": sources,
            "highlight": highlight,
            "ordered": ordered,
            "no_evidences": True, 
            "no_iea": False,
        },
        headers = {
            "User-Agent": "FullPythonRequest"
        }
    )
    ora_df = pd.DataFrame.from_dict(res.json()['result'])

    if (max_term_size) & (max_term_size > 0):
        ora_df = ora_df[ora_df["term_size"] < max_term_size]
    
    return ora_df