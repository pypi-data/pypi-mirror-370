import pandas as pd

def make_combined_categorical_column(
    df: pd.DataFrame, 
    col_a: str, 
    col_b: str, 
    category_order: list[str] =None
):
    """
    Given a dataframe `df` and two column labels,
    generates a new categorical series as a combination
    of the two columns. 
    
    Roughly a wrapper around the following code:
    `(df[col_a].astype(str) + " " + df[col_b].astype(str)).astype("category")`
    
    Parameters
    ---------

    df: pandas.DataFrame
        The input dataframe
    
    col_a, col_b: str
        Names of columns in `df` to combine. Must 
        be `str` or `categorical` type columns.
    
    category_order: list of str (default: None)
        The order of categories in the new combined
        column. New column categories are always
        separated by spaces, i.e.:
        `col_a_val + " " + col_b_val`
        New category order must include only
        all possible category new values.
        
        When `None`, ordered with first column order 
        as parent, second column order as child, i.e. 
        `["a0 b0", "a0 b1", ..., "a1 b0", ...]`
    
    Returns
    -------
    
    new_col: pd.Series
        The new categorical series
    

    Usage
    -----

    Here, :code:`df["age"]` and :code:`df["phase"]` are categorical
    columns that have had their categories manually ordered by the
    user. We first demonstrate a simple approach to combining the 
    columns that will default to alphabetical category ordering. We then 
    compare to the result of this function, which maintains the original
    category ordering. 

    .. code-block::

        >>> df["age"].cat.categories.tolist()
        ['E12', 'E15', 'E17', 'E19', 'P3', ...]
        >>> df["phase"].cat.categories.tolist()
        ['G1', 'S', 'G2M']
        >>> df["age_phase_unordered"] = df["age"].astype(str) + " " + df["phase"].astype(str)
        >>> df["age_phase_unordered"] = df["age_phase_unordered"].astype("category")
        >>> df["age_phase_unordered"].cat.categories.tolist()
        ['E12 G1', 'E12 G2M', 'E12 S', 'E15 G1', 'E15 G2M', ...]
        >>> df["age_phase_ordered"] = make_combined_categorical_column(df, "age", "phase") 
        >>> df["age_phase_ordered"].cat.categories.tolist()
        ['E12 G1', 'E12 S', 'E12 G2M', 'E15 G1', 'E15 S', ...]

    """
        
    new_col = df[col_a].astype(str) + " " + df[col_b].astype(str)
    new_col = new_col.astype("category")
    
    try:
        if (category_order):
            new_col = new_col.cat.reorder_categories(category_order)
        else:
            possible_categories = new_col.cat.categories
            category_order = []
            for x in df[col_a].cat.categories:
                for y in df[col_b].cat.categories:
                    cat = x + " " + y
                    if (cat in possible_categories):
                        category_order.append(x + " " + y)
            new_col = new_col.cat.reorder_categories(category_order)
    except Exception as e:
        print("Failed to re-order new categories: " + str(e))
    
    return new_col