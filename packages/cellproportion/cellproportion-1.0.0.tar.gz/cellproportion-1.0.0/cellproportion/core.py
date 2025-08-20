import pandas as pd
import numpy as np
import anndata
from scipy.stats import mannwhitneyu
from .methods import calculate_v2, explain_v2
from .utils import load_metadata, load_colors, validate_groups, add_significance_categories, apply_default_colors

def cell_type_abundance(
    mc,
    annotation="annotation",
    sample_types="sample_types",
    sample_ID="sample_ID",
    sample_types_1="cSCC",
    sample_types_2="PL",
    colours_file=None,
    method="signed_r2",
    signed_r2_cutoff=None,
    explain=False
):
    """
    Compare cell type proportions between two groups.
    
    This function calculates cell type proportions for each sample and compares
    them between two experimental groups using various statistical methods.
    
    Parameters
    ----------
    mc : AnnData | pd.DataFrame
        Single-cell metadata or AnnData object containing cell annotations
        and sample information.
    annotation : str, default "annotation"
        Column name for cell type annotation.
    sample_types : str, default "sample_types"
        Column name for condition/group labels.
    sample_ID : str, default "sample_ID"
        Column name for sample/patient IDs.
    sample_types_1 : str, default "cSCC"
        Group 1 label for comparison.
    sample_types_2 : str, default "PL"
        Group 2 label for comparison.
    colours_file : str, optional
        Path to TSV file mapping annotation to colour hex codes.
        File should have 'annotation' and 'color' columns.
    method : str, default "signed_r2"
        Statistical method for comparison. One of:
        - 'signed_r2': Signed R² from regression
        - 'mean_diff': Difference in mean proportions
        - 'log2_fc': Log₂ fold-change
        - 'corr': Pearson correlation
    signed_r2_cutoff : float, optional
        Cutoff for signed_r2 magnitude. If provided, colors are applied
        based on both cutoff and p-value significance.
    explain : bool, default False
        If True, print method explanation before analysis.
    
    Returns
    -------
    pd.DataFrame
        Results table with columns:
        - V1: Cell type annotation
        - V2: Statistical metric value
        - V3: P-value from Mann-Whitney U test
        - sig_p: Significance category (p<0.01, p<0.05, etc.)
        - color: Color code for visualization (if colours_file provided or default)
    
    Raises
    ------
    TypeError
        If input is neither AnnData nor DataFrame.
    ValueError
        If unknown method is specified or groups not found in data.
    KeyError
        If required columns are missing from input data.
        
    Examples
    --------
    >>> import pandas as pd
    >>> from cellproportion import cell_type_abundance
    >>> 
    >>> # Using DataFrame input
    >>> results = cell_type_abundance(
    ...     metadata_df,
    ...     annotation="cell_type",
    ...     sample_types="condition", 
    ...     sample_ID="patient_id",
    ...     sample_types_1="tumor",
    ...     sample_types_2="normal",
    ...     method="signed_r2"
    ... )
    >>> print(results.head())
    """
    # Handle AnnData or DataFrame input
    if isinstance(mc, anndata.AnnData):
        mc = mc.obs.copy()
    elif isinstance(mc, pd.DataFrame):
        mc = mc.copy()
    else:
        raise TypeError("Input must be AnnData or DataFrame.")

    # Explain method if requested
    if explain:
        method_info = explain_v2().get(method.lower())
        if method_info:
            print(f"Method: {method}")
            for k, v in method_info.items():
                print(f"  {k}: {v}")
            print()
        else:
            raise ValueError(f"Unknown method: {method}")

    # Validate input data and convert to appropriate types
    mc = load_metadata(mc, annotation, sample_types, sample_ID)
    
    # Validate that specified groups exist
    validate_groups(mc, sample_types, sample_types_1, sample_types_2)

    # Calculate cell type fractions per sample
    cell_counts = mc.groupby([sample_ID, sample_types, annotation]).size().reset_index(name="n")
    total_counts = cell_counts.groupby([sample_ID, sample_types])["n"].transform("sum")
    cell_counts["fraction"] = cell_counts["n"] / total_counts

    # Get unique cell types
    cell_types = cell_counts[annotation].unique()
    
    # Initialize results
    results = []

    # Loop over each cell type
    for cell_type in cell_types:
        subset = cell_counts[cell_counts[annotation] == cell_type].copy()
        
        # Get fractions for each group
        group1_fractions = subset[subset[sample_types] == sample_types_1]["fraction"]
        group2_fractions = subset[subset[sample_types] == sample_types_2]["fraction"]
        
        # Skip if either group has no data
        if len(group1_fractions) == 0 or len(group2_fractions) == 0:
            print(f"Warning: No data for {cell_type} in one or both groups. Skipping.")
            continue
        
        # Calculate p-value using Mann-Whitney U test
        try:
            _, p_value = mannwhitneyu(group2_fractions, group1_fractions, alternative='two-sided')
        except ValueError as e:
            print(f"Warning: Could not calculate p-value for {cell_type}: {e}")
            p_value = np.nan

        # Calculate V2 metric
        try:
            v2_value = calculate_v2(
                subset,
                sample_types,
                method=method,
                group1=sample_types_1,
                group2=sample_types_2
            )
        except Exception as e:
            print(f"Warning: Could not calculate V2 for {cell_type}: {e}")
            v2_value = np.nan

        results.append({
            "V1": cell_type,
            "V2": v2_value,
            "V3": p_value
        })

    # Convert to DataFrame
    prep_table = pd.DataFrame(results)
    
    if prep_table.empty:
        print("Warning: No valid results generated.")
        return prep_table

    # Add significance categories
    prep_table = add_significance_categories(prep_table)

    # Handle colors
    if colours_file:
        try:
            col_df = load_colors(colours_file, prep_table["V1"].tolist())
            if col_df is not None:
                prep_table = prep_table.merge(col_df, on="V1", how="left")
            else:
                prep_table = apply_default_colors(prep_table, method, signed_r2_cutoff)
        except Exception as e:
            print(f"Warning: Could not load colors from file: {e}")
            prep_table = apply_default_colors(prep_table, method, signed_r2_cutoff)
    else:
        prep_table = apply_default_colors(prep_table, method, signed_r2_cutoff)

    return prep_table
