import pandas as pd
import numpy as np

def load_metadata(input_data, annotation, sample_types, sample_ID):
    """
    Load metadata from AnnData object or DataFrame.

    Parameters
    ----------
    input_data : AnnData or pd.DataFrame
        The input data object.
    annotation : str
        Column name for cell annotation.
    sample_types : str
        Column name for condition/group labels.
    sample_ID : str
        Column name for sample/patient IDs.

    Returns
    -------
    pd.DataFrame
        Metadata DataFrame with specified columns as strings.
        
    Raises
    ------
    TypeError
        If input is neither AnnData nor DataFrame.
    KeyError
        If required columns are missing.
    """
    if hasattr(input_data, "obs"):  # AnnData
        mc = input_data.obs.copy()
    elif isinstance(input_data, pd.DataFrame):
        mc = input_data.copy()
    else:
        raise TypeError("Input must be an AnnData object or Pandas DataFrame.")

    # Check if required columns exist
    required_cols = [annotation, sample_types, sample_ID]
    missing_cols = [col for col in required_cols if col not in mc.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # Convert to string type
    for col in required_cols:
        mc[col] = mc[col].astype(str)

    return mc


def load_colors(colours_file, annotations):
    """
    Load colour mapping from file or return None.

    Parameters
    ----------
    colours_file : str or None
        Path to colour mapping file (TSV format).
    annotations : list
        List of annotation values to keep.

    Returns
    -------
    pd.DataFrame or None
        DataFrame with colour mappings, or None if no file provided.
        
    Raises
    ------
    FileNotFoundError
        If colours_file doesn't exist.
    ValueError
        If colours_file doesn't have required columns.
    """
    if colours_file:
        try:
            col_df = pd.read_table(colours_file)
            
            # Check required columns
            if "annotation" not in col_df.columns or "color" not in col_df.columns:
                raise ValueError("Colours file must contain 'annotation' and 'color' columns")
                
            col_df = col_df.rename(columns={"annotation": "V1"})
            col_df = col_df[col_df["V1"].isin(annotations)]
            return col_df
        except FileNotFoundError:
            raise FileNotFoundError(f"Colours file not found: {colours_file}")
    return None


def validate_groups(data, condition_col, group1, group2):
    """
    Validate that specified groups exist in the data.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data.
    condition_col : str
        Column name for conditions.
    group1 : str
        First group label.
    group2 : str
        Second group label.
        
    Raises
    ------
    ValueError
        If groups are not found in the data.
    """
    available_groups = set(data[condition_col].unique())
    missing_groups = []
    
    if group1 not in available_groups:
        missing_groups.append(group1)
    if group2 not in available_groups:
        missing_groups.append(group2)
        
    if missing_groups:
        raise ValueError(f"Groups {missing_groups} not found in {condition_col}. "
                        f"Available groups: {list(available_groups)}")


def add_significance_categories(df, p_col="V3"):
    """
    Add significance categories based on p-values.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with p-values.
    p_col : str, default "V3"
        Column name containing p-values.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'sig_p' column.
    """
    df = df.copy()
    df["sig_p"] = pd.cut(
        df[p_col],
        bins=[-float("inf"), 0.01, 0.05, 0.1, 0.5, float("inf")],
        labels=["p<0.01", "p<0.05", "p<0.1", "p<0.5", "p>0.5"],
        ordered=True
    )
    return df


def apply_default_colors(df, method="signed_r2", cutoff=None, p_col="V3", v2_col="V2"):
    """
    Apply default color scheme based on method and significance.
    
    Parameters
    ----------
    df : pd.DataFrame
        Results DataFrame.
    method : str, default "signed_r2"
        Analysis method used.
    cutoff : float, optional
        Cutoff value for signed_r2 method.
    p_col : str, default "V3"
        Column name for p-values.
    v2_col : str, default "V2"
        Column name for V2 values.
        
    Returns
    -------
    pd.DataFrame
        DataFrame with added 'color' column.
    """
    DEFAULT_COLORS = {
        "positive": "#E41A1C",  # red
        "negative": "#377EB8",  # blue
        "grey": "#BDBDBD"       # grey
    }
    
    df = df.copy()
    df["color"] = DEFAULT_COLORS["grey"]  # Default to grey
    
    if method.lower() == "signed_r2":
        if cutoff is not None:
            # Use both cutoff and p-value
            mask_significant = (np.abs(df[v2_col]) >= cutoff) & (df[p_col] < 0.05)
            df.loc[mask_significant & (df[v2_col] > 0), "color"] = DEFAULT_COLORS["positive"]
            df.loc[mask_significant & (df[v2_col] < 0), "color"] = DEFAULT_COLORS["negative"]
        else:
            # Use only p-value
            mask_significant = df[p_col] < 0.05
            df.loc[mask_significant & (df[v2_col] > 0), "color"] = DEFAULT_COLORS["positive"]
            df.loc[mask_significant & (df[v2_col] < 0), "color"] = DEFAULT_COLORS["negative"]
    else:
        # For other methods, color by significance and direction
        mask_significant = df[p_col] < 0.05
        df.loc[mask_significant & (df[v2_col] > 0), "color"] = DEFAULT_COLORS["positive"]
        df.loc[mask_significant & (df[v2_col] < 0), "color"] = DEFAULT_COLORS["negative"]
    
    return df


# Default color constants for external use
DEFAULT_COLORS = {
    "positive": "#E41A1C",  # red
    "negative": "#377EB8",  # blue
    "grey": "#BDBDBD"       # grey
}
