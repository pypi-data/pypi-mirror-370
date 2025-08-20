import numpy as np
import pandas as pd
from statsmodels.formula.api import ols
from scipy.stats import pearsonr

def explain_v2():
    """
    Returns a dictionary explaining each V2 method, its pros, and cons.
    
    Returns
    -------
    dict
        Dictionary with method explanations including definition, pros, cons, and when to use.
    """
    return {
        "signed_r2": {
            "definition": "Signed R² from regression — measures both direction and fit.",
            "pros": "Captures both direction and fit strength; interpretable.",
            "cons": "Assumes linearity; sensitive to outliers.",
            "when_to_use": "When relationship between group and proportion is expected to be roughly linear."
        },
        "mean_diff": {
            "definition": "Difference in average proportions between groups.",
            "pros": "Simple to interpret; no assumptions about shape of relationship.",
            "cons": "Ignores variance; scale-dependent.",
            "when_to_use": "When you want a straightforward absolute difference."
        },
        "log2_fc": {
            "definition": "Log₂ fold-change of mean proportions between groups.",
            "pros": "Intuitive ratio-based interpretation.",
            "cons": "Sensitive to low means; ignores variance.",
            "when_to_use": "When group differences are multiplicative."
        },
        "corr": {
            "definition": "Pearson correlation between fraction and condition labels.",
            "pros": "Simple, scale-invariant.",
            "cons": "Ignores magnitude differences; only captures linear association.",
            "when_to_use": "When you care about association direction/strength, not effect size."
        }
    }

def calculate_v2(data, condition_col, method="signed_r2", group1=None, group2=None):
    """
    Calculate V2 metric for given data and method.
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing fraction and condition columns.
    condition_col : str
        Column name for condition/group labels.
    method : str, default "signed_r2"
        One of 'signed_r2', 'mean_diff', 'log2_fc', 'corr'.
    group1 : str, optional
        Group 1 label (required for mean_diff and log2_fc).
    group2 : str, optional
        Group 2 label (required for mean_diff and log2_fc).
    
    Returns
    -------
    float
        Calculated V2 metric value.
    
    Raises
    ------
    ValueError
        If unknown method is specified or required groups are missing.
    """
    method = method.lower()

    if method == "signed_r2":
        # Use OLS regression to get signed R²
        model = ols(f"fraction ~ C({condition_col})", data=data).fit()
        slope = model.params.iloc[1] if len(model.params) > 1 else 0
        r2 = model.rsquared
        return ((-slope) / abs(slope)) * r2 if slope != 0 else 0

    elif method == "mean_diff":
        if group1 is None or group2 is None:
            raise ValueError("group1 and group2 must be specified for mean_diff method")
        mean_g1 = data.loc[data[condition_col] == group1, "fraction"].mean()
        mean_g2 = data.loc[data[condition_col] == group2, "fraction"].mean()
        return mean_g1 - mean_g2

    elif method == "log2_fc":
        if group1 is None or group2 is None:
            raise ValueError("group1 and group2 must be specified for log2_fc method")
        mean_g1 = data.loc[data[condition_col] == group1, "fraction"].mean()
        mean_g2 = data.loc[data[condition_col] == group2, "fraction"].mean()
        if mean_g2 == 0:
            return np.inf if mean_g1 > 0 else np.nan
        return np.log2(mean_g1 / mean_g2)

    elif method == "corr":
        # Convert categorical to numeric codes for correlation
        labels = pd.Categorical(data[condition_col]).codes
        corr_val, _ = pearsonr(data["fraction"], labels)
        return corr_val

    else:
        raise ValueError(f"Unknown V2 method: {method}. Available methods: signed_r2, mean_diff, log2_fc, corr")
