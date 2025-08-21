import re

def in_ignore_list(g: str):
    """
    Given a gene symbol `g`, return `True` 
    if this gene is any of the following:
        
    * A mitochondrial gene
    * A ribosomal gene
    * A hemoglobin gene
    * A lncRNA gene
    * An antisense gene
    * A microRNA
    * An uncharacterized/predicted gene
    
    These genes are often uninformative or not a focus
    of study in transcriptomic analyses, and their inclusion
    in differential expression testing results can be
    distracting to readers. 

    This function identifies such nuiscance genes based on
    gene symbol alone and as such may miss or include
    genes erronously.

    Parameters
    ----------
    g: str
        The gene symbol to test
    
    Returns
    -------
    True if g is in any of those categories, else False.
    
    Usage
    -----
    .. code-block::

        >>> in_ignore_list("Gm12941")
        True
        >>> in_ignore_list("Actb")
        False
        >>> adata.var["ignore"] = [in_ignore_list(g) for g in adata.var.index]
        
    """
    
    to_ignore = [
        "MT-", "mt-", "RPL", "Rpl", "RPS", "Rps",
        "HBA", "Hba", "HBB", "Hbb", "LINC", "Lnc",
        "RP11", "Rp11", "-AS", "LOC", "n-R5", "-mir",
        "snopsi", "AC0", "XXbac", "Trn", "-DT"
        "-ps", "-ps1", "-ps2", 
        "ROSA", "Gt(ROSA)26Sor"
    ]
    
    regex_patterns_to_ignore = [
        "^Gm[0-9]{3,}", "[0-9]Rik",
        "^AU[0-9]{3,}", "^C[0-9]{1,}orf[0-9]{1,}", 
        "^RP[0-9]{1,}-[0-9]{1,}", "^Rp[0-9]{1,}-[0-9]{1,}",
        "^CT[A-Z]-[0-9]{1,}", "^A[A-Z][0-9]{2,}"
    ]
    
    # first search for brute-forcable substrings
    for x in to_ignore:
        if (x in g):
            return True
        
    # then, check for complex (regex-needed) substrings
    for pattern in regex_patterns_to_ignore:
        if (re.search(pattern, g)):
            return True
    
    # no matches found
    return False