======================
python bioinformagicks
======================

A collection (read: `hodgepodge`) of tools for bioinformatics tasks.

Features
--------

Tools:

* TF-IDF marker gene testing ("quickMarkers"), as in SoupX_
* JASMINE gene set scoring, as in `Noureen et al.`_
* Over-representation analyses (ORAs) with gProfiler_
* Cell mask generation based on geometric sketching, as in Geosketch_
* Cell mask generation based on embedding (i.e. UMAP) coordinate bounds
* Z-standard scaling of gene expression on a per-group basis
* Basic single-cell variant calling for single point mutations

Plotting:

* Split embedding plot generation based on categorical observations
* Stacked barplot generation of cell proportions split by group and counts normalized per-batch
* Barplot generation for gProfiler_ ORA results, with optional term fold enrichment sorting

Utilities:

* Identification of genes often left ignored, like `AW146154`_ 
* Combination of categorical columns maintaining specified ordering 

.. _SoupX: https://github.com/constantAmateur/SoupX
.. _`Noureen et al.`: https://doi.org/10.7554/eLife.71994
.. _gProfiler: https://biit.cs.ut.ee/gprofiler/gost
.. _`AW146154`: https://www.ncbi.nlm.nih.gov/gene/101835
.. _Geosketch: https://doi.org/10.1016/j.cels.2019.05.003

Installation
------------

.. code-block:: console

    $ pip install python-bioinformagicks

Documentation 
-------------

https://python-bioinformagicks.readthedocs.io

Credits
-------

This package was created by Sylvia N. Michki.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

License
-------

Free software: GNU General Public License v3