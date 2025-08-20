# tests/test_encoding.py

import pandas as pd
import pytest
from feature_engineering.encoding import Encoder

@pytest.fixture
def sample_data_for_encoding():
    """Creates a sample DataFrame for testing encoding."""
    data = {
        'color': ['red', 'blue', 'green', 'red', 'blue'],
        'size': ['S', 'M', 'L', 'M', 'S'],
        'numeric': [10, 20, 30, 40, 50]
    }
    return pd.DataFrame(data)

def test_one_hot_encoding(sample_data_for_encoding):
    """
    Tests that one-hot encoding creates the correct new columns.
    """
    df = sample_data_for_encoding
    encoder = Encoder(method='onehot', columns=['color'])
    
    df_transformed = encoder.fit_transform(df)
    
    # Check that original column is dropped and new columns are added
    assert 'color' not in df_transformed.columns
    assert 'color_green' in df_transformed.columns
    assert 'color_red' in df_transformed.columns
    # 'color_blue' is dropped because of drop_first=True
    assert 'color_blue' not in df_transformed.columns
    assert df_transformed.shape[1] == 4 # size, numeric, color_green, color_red

def test_ordinal_encoding(sample_data_for_encoding):
    """
    Tests that ordinal encoding correctly maps categories to numbers.
    """
    df = sample_data_for_encoding
    size_mapping = {'S': 1, 'M': 2, 'L': 3}
    encoder = Encoder(method='ordinal', columns=['size'], mapping={'size': size_mapping})
    
    df_transformed = encoder.fit_transform(df)
    
    # Check that the mapping was applied correctly
    assert df_transformed['size'].tolist() == [1, 2, 3, 2, 1]
    assert df_transformed['size'].dtype == 'int64'

def test_ordinal_encoding_no_mapping_raises_error(sample_data_for_encoding):
    """
    Tests that an error is raised if ordinal encoding is attempted without a mapping.
    """
    df = sample_data_for_encoding
    encoder = Encoder(method='ordinal', columns=['size']) # No mapping provided
    
    with pytest.raises(ValueError):
        encoder.fit_transform(df)

def test_auto_column_selection(sample_data_for_encoding):
    """
    Tests that object columns are automatically selected if `columns=None`.
    """
    df = sample_data_for_encoding
    encoder = Encoder(method='onehot') # columns=None
    
    df_transformed = encoder.fit_transform(df)
    
    # Both 'color' and 'size' should be one-hot encoded
    assert 'color' not in df_transformed.columns
    assert 'size' not in df_transformed.columns
    assert 'color_red' in df_transformed.columns
    assert 'size_M' in df_transformed.columns
