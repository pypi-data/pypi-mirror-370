#!/usr/bin/env python

import pytest


import python_bioinformagicks as bim


@pytest.fixture
def sample_adata():
    """
    Loads an ad.AnnData object from disk to use
    in tests. This is data from multiple publications
    that has been integrated and annotated before 
    subsetting to 5% of the cells and the top
    2000 highly variable genes.
    """

    import anndata as ad

    return ad.read_h5ad("./tests/data/test_adata.h5ad")


def test_in_ignore_list(
    sample_adata,
):
    """
    Testing bim.util.in_ignore_list

    A few ignorable genes were left in the test
    AnnData object; make sure they get detected.
    """

    import numpy as np

    mask = [bim.util.in_ignore_list(g) for g in sample_adata.var.index]
    
    ignored_genes = sample_adata[:, mask].var.index.tolist()

    assert (0 < np.sum(mask) < 200)
    assert ("mt-Rnr1" in ignored_genes)
    assert ("C330002G04Rik" in ignored_genes)
    assert ("Gm29538" in ignored_genes)
    assert ("Actb" not in ignored_genes)


def test_make_combined_categorical_column(
    sample_adata,
    col_a = "age",
    col_b = "celltype"
):
    """
    Testing bim.util.make_combined_categorical_column

    If we combine the age column with the celltype column,
    we expect age to be first in the order and celltype
    to be second. E12 and ASM are ages and celltypes
    in the sample_adata object. 
    """

    df = sample_adata.obs

    new_col = bim.util.make_combined_categorical_column(
        df,
        col_a,
        col_b
    )

    assert ("E12 ASM" in new_col.cat.categories)