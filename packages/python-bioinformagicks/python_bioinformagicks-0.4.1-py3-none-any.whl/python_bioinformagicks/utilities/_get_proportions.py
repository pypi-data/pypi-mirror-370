import pandas as pd
import numpy as np

def get_proportions(
    df: pd.DataFrame, 
    outer_col: str, 
    inner_col: str,
    return_counts: bool = False
):
    """
    Calculates how many items from each
    `outer_col` are also in `inner_col` as
    a fraction of the total items in `outer_col`.
    
    Parameters
    ----------
    df: pd.DataFrame
        The dataframe containing at least the columns
        `outer_col` and `inner_col`.
    
    outer_col: str
        The column name of the outermost column;
        often `batch`, `sample`, or `genotype`.
    
    inner_col: str
        The column name of the innermost column;
        often `celltype`, `leiden`.
        
    return_counts: bool (default: False)
        If `True`, return the number of cells,
        otherwise return the fraction.

    """
    
    if (outer_col in df.columns):
        if (inner_col in df.columns):
            groups = df.value_counts([outer_col, inner_col]).astype(float)
            count_data = groups.unstack(level=outer_col)
            count_data = count_data.fillna(0)
            if (return_counts):
                ret = count_data
            else:
                ret = count_data / count_data.apply(np.sum, axis=0)
            return ret
    
    print("[ERROR]: missing outer_col/innner_col")
    return None
