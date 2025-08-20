import pytest
import pandas as pd
import numpy as np
from cellproportion import cell_type_abundance, explain_v2
from cellproportion.spatial import spatial_cell_type_abundance

def create_test_data():
    """Create synthetic test data for testing."""
    np.random.seed(42)
    
    # Create synthetic metadata
    n_cells = 1000
    cell_types = ['T_cell', 'B_cell', 'NK_cell', 'Macrophage']
    conditions = ['tumor', 'normal']
    patients = ['P1', 'P2', 'P3', 'P4']
    regions = ['region_A', 'region_B', 'region_C']
    
    data = []
    for i in range(n_cells):
        data.append({
            'cell_type': np.random.choice(cell_types),
            'condition': np.random.choice(conditions),
            'patient_id': np.random.choice(patients),
            'tissue_region': np.random.choice(regions)
        })
    
    return pd.DataFrame(data)

def test_cell_type_abundance_basic():
    """Test basic functionality of cell_type_abundance."""
    df = create_test_data()
    
    results = cell_type_abundance(
        df,
        annotation="cell_type",
        sample_types="condition",
        sample_ID="patient_id",
        sample_types_1="tumor",
        sample_types_2="normal",
        method="signed_r2"
    )
    
    # Check that results are returned
    assert isinstance(results, pd.DataFrame)
    assert len(results) > 0
    
    # Check required columns exist
    required_cols = ['V1', 'V2', 'V3', 'sig_p', 'color']
    for col in required_cols:
        assert col in results.columns
    
    # Check that all cell types are represented
    assert set(results['V1'].unique()).issubset(set(df['cell_type'].unique()))

def test_spatial_analysis():
    """Test spatial cell type abundance analysis."""
    df = create_test_data()
    
    results = spatial_cell_type_abundance(
        df,
        region_col="tissue_region",
        annotation="cell_type",
        sample_types="condition",
        sample_ID="patient_id",
        sample_types_1="tumor",
        sample_types_2="normal",
        method="signed_r2"
    )
    
    # Check that results are returned
    assert isinstance(results, pd.DataFrame)
    assert len(results) > 0
    
    # Check required columns exist
    required_cols = ['region', 'V1', 'V2', 'V3', 'sig_p', 'color']
    for col in required_cols:
        assert col in results.columns
    
    # Check that regions are represented
    assert len(results['region'].unique()) > 0

def test_different_methods():
    """Test different statistical methods."""
    df = create_test_data()
    methods = ['signed_r2', 'mean_diff', 'log2_fc', 'corr']
    
    for method in methods:
        results = cell_type_abundance(
            df,
            annotation="cell_type",
            sample_types="condition",
            sample_ID="patient_id",
            sample_types_1="tumor",
            sample_types_2="normal",
            method=method
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) > 0
        assert 'V2' in results.columns

def test_explain_v2():
    """Test method explanation function."""
    explanations = explain_v2()
    
    assert isinstance(explanations, dict)
    assert 'signed_r2' in explanations
    assert 'mean_diff' in explanations
    assert 'log2_fc' in explanations
    assert 'corr' in explanations
    
    # Check that each method has required keys
    for method, info in explanations.items():
        assert 'definition' in info
        assert 'pros' in info
        assert 'cons' in info
        assert 'when_to_use' in info

def test_error_handling():
    """Test error handling for invalid inputs."""
    df = create_test_data()
    
    # Test invalid method
    with pytest.raises(ValueError):
        cell_type_abundance(
            df,
            annotation="cell_type",
            sample_types="condition",
            sample_ID="patient_id",
            sample_types_1="tumor",
            sample_types_2="normal",
            method="invalid_method"
        )
    
    # Test missing columns
    with pytest.raises(KeyError):
        cell_type_abundance(
            df,
            annotation="missing_column",
            sample_types="condition",
            sample_ID="patient_id",
            sample_types_1="tumor",
            sample_types_2="normal"
        )

if __name__ == "__main__":
    # Run basic tests
    test_cell_type_abundance_basic()
    test_spatial_analysis()
    test_different_methods()
    test_explain_v2()
    print("All tests passed!")
