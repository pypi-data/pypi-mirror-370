import pandas as pd

from natsort import natsorted

def get_grouped_categories(
    df: pd.DataFrame,
    groupby: str,
    column_to_reorder: str,
    sort: bool = False
):
    """
    Given a dataframe, subset by the `groupby`
    column, identify unique values in the grouped
    `column_to_reorder`, and return a flat list of unique
    categories, ordered first by parent group then by initial
    category ordering (or natsorted ordering).
    
    Useful for resetting categories of the `column_to_reorder`.

    Parameters
    ----------
    df: pd.Dataframe
        The dataframe. Must contain categorical
        columns `groupby` and `column_to_map`
    
    groupby: str 
        The column name in `df` to group/subset by.
        Must be a categorical column.
    
    column_to_reorder: str
        The column name in `df` to reorder.
        Must be a categorical column.
    
    sort: bool (default: False)
        If :code:`True`, natsort the categories
        in each group before insertion into final list.
        If :code:`False`, leave the original category ordering.

    Returns
    -------
    new_category_order: list of str
        The reordered categories.

    Usage
    -----

    Here we will reorder categories in :code:`df["celltype"]` by first
    grouping by :code:`df["compartment"]`. In this case, since the Endothelial
    compartment is the first category in :code:`df["compartment"]`, the 
    celltypes belonging to that compartment will be ordered before those
    of the next compartment (Epithelial), and so on.

    >>> df["celltype"].cat.categories.tolist()
    ['ASM', 'AT1', 'AT1 | AT2', 'AT2', 'Alveolar Macrophage', ...]
    >>> df["compartment"].cat.categories.tolist()
    ['Endothelial', 'Epithelial', 'Immune', 'Mesenchymal']
    >>> new_order = get_grouped_categories(df, "compartment", "celltype", sort=True)
    >>> df["celltype"] = df["celltype"].cat.reorder_categories(new_order)
    >>> df["celltype"].cat.categories.tolist()
    ['Artery', 'Lymph', 'Proliferating gCap', 'Vein', 'aCap', 'gCap', 'AT1', ...]
    """

    categories = {}
    for i,group in enumerate(df[groupby].cat.categories):
        # subset the data
        a = df[df[groupby] == group]
        
        # remove categories not found in group
        cleaned_groupby_col = a[column_to_reorder].cat.remove_unused_categories()

        # optional sort
        if (sort):
            categories[group] = natsorted(cleaned_groupby_col.cat.categories)
        else:
            categories[group] = cleaned_groupby_col.cat.categories.tolist()

    # make the flat list
    new_category_order = []
    for v in categories.values():
        for x in v:
            new_category_order.append(x)
    return new_category_order