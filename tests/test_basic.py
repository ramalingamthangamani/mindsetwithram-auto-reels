import os
import pandas as pd
import pytest
from utils.excel_manager import ExcelManager

# Ensure log directory exists so imports don't fail
os.makedirs("logs", exist_ok=True)

def test_excel_manager_creates_template(tmp_path):
    """Test that ExcelManager creates a template file if it doesn't exist."""
    test_file = tmp_path / "test_reels.xlsx"
    em = ExcelManager(file_path=str(test_file))
    
    assert os.path.exists(str(test_file))
    
    # Check headers
    df = pd.read_excel(str(test_file))
    expected_cols = ['FileName', 'Caption', 'Hashtags', 'Status', 'PostedDate']
    assert list(df.columns) == expected_cols

def test_excel_manager_get_pending_reel(tmp_path):
    """Test that ExcelManager correctly retrieves the next pending reel."""
    test_file = tmp_path / "test_reels.xlsx"
    
    # Create mock data
    df = pd.DataFrame({
        'FileName': ['file1', 'file2'],
        'Caption': ['cap1', 'cap2'],
        'Hashtags': ['#h1', '#h2'],
        'Status': ['Posted', 'Pending'],
        'PostedDate': ['2023-10-01', None]
    })
    df.to_excel(str(test_file), index=False)
    
    em = ExcelManager(file_path=str(test_file))
    reel = em.get_pending_reel()
    
    assert reel is not None
    assert reel['FileName'] == 'file2'
    assert reel['index'] == 1 # Second row

def test_excel_manager_mark_as_posted(tmp_path):
    """Test updating the status of a reel."""
    test_file = tmp_path / "test_reels.xlsx"
    
    # Create mock data
    df = pd.DataFrame({
        'FileName': ['file1'],
        'Caption': ['cap1'],
        'Hashtags': ['#h1'],
        'Status': ['Pending'],
        'PostedDate': [None]
    })
    df.to_excel(str(test_file), index=False)
    
    em = ExcelManager(file_path=str(test_file))
    em.mark_as_posted(0)
    
    updated_df = pd.read_excel(str(test_file))
    assert updated_df.at[0, 'Status'] == 'Posted'
    assert pd.notna(updated_df.at[0, 'PostedDate'])
