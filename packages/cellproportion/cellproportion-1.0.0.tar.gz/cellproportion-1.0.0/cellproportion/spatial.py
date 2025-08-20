import pandas as pd
import numpy as np
import anndata
from scipy.stats import mannwhitneyu
from .methods import calculate_v2, explain_v2
from .utils import load_metadata, load_colors, validate_groups, add_significance_categories, apply_default_colors

def spatial_cell_type_abundance(
    mc,
    region_col="region",
    annotation="annotation",
    sample_types="sample_types",
    sample_ID="sample_ID",
    sample_types_1="cSCC",
    sample_types_2="PL",
    method="signed_r2",
    signed_r2_cutoff=None,
    colours_file=None,
    explain=False
):
    """
    Compare cell type proportions between two groups within each spatial region.
    
    This function performs cell type proportion analysis separately for each
    spatial region, allowing for region-specific comparisons between groups.
    
    Parameters
    ----------
    mc : AnnData | pd.DataFrame
        Single-cell metadata or AnnData object containing cell annotations,
        sample information, and spatial region data.
    region_col : str, default "region"
        Column name for spatial region annotation.
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
    method : str, default "signed_r2"
        Statistical method for comparison. One of:
        - 'signed_r2': Signed R² from regression
        - 'mean_diff': Difference in mean proportions
        - 'log2_fc': Log₂ fold-change
        - 'corr': Pearson correlation
    signed_r2_cutoff : float, optional
        Cutoff for signed_r2 magnitude. If provided, colors are applied
        based on both cutoff and p-value significance.
    colours_file : str, optional
        Path to TSV file mapping annotation to colour hex codes.
        File should have 'annotation' and 'color' columns.
    explain : bool, default False
        If True, print method explanation before analysis.
    
    Returns
    -------
    pd.DataFrame
        Results table with columns:
        - region: Spatial region name
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
    >>> from cellproportion.spatial import spatial_cell_type_abundance
    >>> 
    >>> # Using DataFrame input with spatial regions
    >>> results = spatial_cell_type_abundance(
    ...     spatial_metadata_df,
    ...     region_col="tissue_region",
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
    required_cols = [annotation, sample_types, sample_ID, region_col]
    missing_cols = [col for col in required_cols if col not in mc.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")
    
    for col in required_cols:
        mc[col] = mc[col].astype(str)
    
    # Validate that specified groups exist
    validate_groups(mc, sample_types, sample_types_1, sample_types_2)

    # Get unique regions
    regions = mc[region_col].unique()
    print(f"Analyzing {len(regions)} spatial regions: {list(regions)}")

    results = []

    # Loop through each spatial region
    for region in regions:
        region_data = mc[mc[region_col] == region].copy()
        
        if region_data.empty:
            print(f"Warning: No data found for region '{region}'. Skipping.")
            continue
        
        # Calculate cell type fractions for this region
        cell_counts = region_data.groupby([sample_ID, sample_types, annotation]).size().reset_index(name="n")
        total_counts = cell_counts.groupby([sample_ID, sample_types])["n"].transform("sum")
        cell_counts["fraction"] = cell_counts["n"] / total_counts

        # Get unique cell types in this region
        cell_types = cell_counts[annotation].unique()

        # Analyze each cell type in this region
        for cell_type in cell_types:
            subset = cell_counts[cell_counts[annotation] == cell_type].copy()
            
            # Get fractions for each group
            group1_fractions = subset[subset[sample_types] == sample_types_1]["fraction"]
            group2_fractions = subset[subset[sample_types] == sample_types_2]["fraction"]
            
            # Skip if either group has no data
            if len(group1_fractions) == 0 or len(group2_fractions) == 0:
                print(f"Warning: No data for {cell_type} in region {region} for one or both groups. Skipping.")
                continue
            
            # Calculate p-value using Mann-Whitney U test
            try:
                _, p_value = mannwhitneyu(group2_fractions, group1_fractions, alternative='two-sided')
            except ValueError as e:
                print(f"Warning: Could not calculate p-value for {cell_type} in {region}: {e}")
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
                print(f"Warning: Could not calculate V2 for {cell_type} in {region}: {e}")
                v2_value = np.nan

            results.append({
                "region": region,
                "V1": cell_type,
                "V2": v2_value,
                "V3": p_value
            })

    # Convert to DataFrame
    prep_table = pd.DataFrame(results)
    
    if prep_table.empty:
        print("Warning: No valid results generated.")
        return prep_table

    print(f"Generated {len(prep_table)} region-celltype combinations")

    # Add significance categories
    prep_table = add_significance_categories(prep_table)

    # Handle colors
    if colours_file:
        try:
            col_df = load_colors(colours_file, prep_table["V1"].unique().tolist())
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
