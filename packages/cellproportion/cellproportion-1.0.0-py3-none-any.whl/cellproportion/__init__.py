"""
CellProportion: A Python package for cell type proportion analysis in single-cell and spatial transcriptomics data.

This package provides tools for comparing cell type proportions between experimental groups,
supporting both single-cell RNA-seq and spatial transcriptomics data analysis.

Main Functions
--------------
cell_type_abundance : Compare cell type proportions between two groups
spatial_cell_type_abundance : Compare proportions within spatial regions
explain_v2 : Get explanations of available statistical methods

Statistical Methods
------------------
- signed_r2: Signed R² from regression (direction + fit strength)
- mean_diff: Difference in mean proportions between groups
- log2_fc: Log₂ fold-change of mean proportions
- corr: Pearson correlation with group labels

Examples
--------
Basic usage for single-cell analysis:

>>> from cellproportion import cell_type_abundance
>>> results = cell_type_abundance(
...     adata,
...     annotation="cell_type",
...     sample_types="condition",
...     sample_ID="patient_id",
...     sample_types_1="tumor",
...     sample_types_2="normal",
...     method="signed_r2"
... )

Spatial analysis:

>>> from cellproportion.spatial import spatial_cell_type_abundance
>>> spatial_results = spatial_cell_type_abundance(
...     adata,
...     region_col="tissue_region",
...     annotation="cell_type",
...     sample_types="condition",
...     sample_ID="patient_id",
...     sample_types_1="tumor",
...     sample_types_2="normal"
... )

Method explanations:

>>> from cellproportion.methods import explain_v2
>>> print(explain_v2())
"""

from ._version import __version__
from .core import cell_type_abundance
from .spatial import spatial_cell_type_abundance
from .methods import calculate_v2, explain_v2
from .utils import DEFAULT_COLORS, load_metadata, load_colors

__all__ = [
    "__version__",
    "cell_type_abundance", 
    "spatial_cell_type_abundance",
    "calculate_v2",
    "explain_v2",
    "DEFAULT_COLORS",
    "load_metadata",
    "load_colors"
]

# Package metadata
__author__ = "Ankit Patel"
__email__ = "ankit.patel@qmul.ac.uk"
__description__ = "Cell type proportion analysis for single-cell and spatial transcriptomics data"
__url__ = "https://github.com/ankitpatel/cellproportion"
