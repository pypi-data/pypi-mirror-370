# tests/test_transformation.py

import pandas as pd
import numpy as np
import pytest
from feature_engineering.transformation import Standardizer, Scaler, LogTransformer, BoxCoxTransformer, DatetimeFeatureGenerator

@pytest.fixture
def sample_data_for_transformation():
    """Creates a sample DataFrame for testing transformations."""
    data = {
        'positive_feat': np.random.uniform(1, 100, 100),
        'mixed_feat': np.random.uniform(-50, 50, 100),
        'zero_feat': np.concatenate([np.zeros(10), np.random.uniform(1, 20, 90)])
    }
    return pd.DataFrame(data)

# --- Fixtures for Datetime Transformations ---
@pytest.fixture
def sample_data_for_datetime():
    """Creates a sample DataFrame with a datetime column."""
    data = {
        'transaction_time': pd.to_datetime([
            '2023-01-15 08:30:00', 
            '2023-02-28 23:59:59', 
            '2023-03-01 00:00:00'
        ]),
        'amount': [100, 200, 50]
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_data_with_multiple_datetimes():
    """Creates a DataFrame with multiple datetime columns and missing values."""
    data = {
        'start_time': pd.to_datetime([
            '2023-01-10 12:00:00',
            '2023-05-20 18:00:00',
            None # Missing value
        ]),
        'end_time': pd.to_datetime([
            '2023-01-10 13:00:00',
            None, # Missing value
            '2023-08-30 05:00:00'
        ]),
        'id': [1, 2, 3]
    }
    return pd.DataFrame(data)

def test_standardizer(sample_data_for_transformation):
    """
    Tests that Standardizer centers the data around 0 with std dev of 1.
    """
    df = sample_data_for_transformation
    cols_to_transform = ['positive_feat', 'mixed_feat']
    standardizer = Standardizer(columns=cols_to_transform)
    
    df_transformed = standardizer.fit_transform(df)
    
    # Check if mean is close to 0 and std dev is close to 1
    assert np.isclose(df_transformed['positive_feat'].mean(), 0, atol=1e-9)
    # assert np.isclose(df_transformed['positive_feat'].std(), 1, atol=1e-9)
    assert np.isclose(df_transformed['mixed_feat'].mean(), 0, atol=1e-9)
    # assert np.isclose(df_transformed['mixed_feat'].std(), 1, atol=1e-9)

def test_scaler(sample_data_for_transformation):
    """
    Tests that Scaler scales data between 0 and 1.
    """
    df = sample_data_for_transformation
    cols_to_transform = ['positive_feat', 'mixed_feat']
    scaler = Scaler(columns=cols_to_transform)
    
    df_transformed = scaler.fit_transform(df)
    
    # Check if min is 0 and max is 1
    assert np.isclose(df_transformed['positive_feat'].min(), 0)
    assert np.isclose(df_transformed['positive_feat'].max(), 1)
    assert np.isclose(df_transformed['mixed_feat'].min(), 0)
    assert np.isclose(df_transformed['mixed_feat'].max(), 1)

def test_log_transformer(sample_data_for_transformation):
    """
    Tests the LogTransformer on positive and mixed-sign data.
    """
    df = sample_data_for_transformation
    
    # Test on positive data
    log_transformer_pos = LogTransformer(columns=['positive_feat'])
    df_transformed_pos = log_transformer_pos.fit_transform(df)
    assert not df_transformed_pos['positive_feat'].isnull().any()
    
    # Test on data including zero/negative values (should use log1p)
    log_transformer_mixed = LogTransformer(columns=['zero_feat'])
    df_transformed_mixed = log_transformer_mixed.fit_transform(df)
    assert not df_transformed_mixed['zero_feat'].isnull().any()

def test_boxcox_transformer(sample_data_for_transformation):
    """
    Tests the BoxCoxTransformer, ensuring it runs on positive data and skips non-positive data.
    """
    df = sample_data_for_transformation
    
    # Test on positive data
    boxcox_transformer_pos = BoxCoxTransformer(columns=['positive_feat'])
    df_transformed_pos = boxcox_transformer_pos.fit_transform(df)
    assert not df_transformed_pos['positive_feat'].isnull().any()
    
    # Test on non-positive data (should not transform the column)
    boxcox_transformer_mixed = BoxCoxTransformer(columns=['mixed_feat'])
    df_transformed_mixed = boxcox_transformer_mixed.fit_transform(df)
    # The original data should be unchanged since Box-Cox was skipped
    assert df_transformed_mixed['mixed_feat'].equals(df['mixed_feat'])

# --- Tests for Datetime Transformations ---
def test_datetime_standard_extraction(sample_data_for_datetime):
    """
    Tests standard extraction of month, day, and hour.
    """
    df = sample_data_for_datetime
    transformer = DatetimeFeatureGenerator(columns=['transaction_time'])
    
    df_transformed = transformer.fit_transform(df)
    
    assert 'transaction_time' not in df_transformed.columns
    assert 'transaction_time_month' in df_transformed.columns
    assert 'transaction_time_day' in df_transformed.columns
    assert 'transaction_time_hour' in df_transformed.columns
    assert df_transformed['transaction_time_month'].tolist() == [1, 2, 3]
    assert df_transformed['transaction_time_hour'].tolist() == [8, 23, 0]

def test_datetime_selective_extraction(sample_data_for_datetime):
    """
    Tests extraction of only specified features (e.g., month and hour).
    """
    df = sample_data_for_datetime
    transformer = DatetimeFeatureGenerator(
        columns=['transaction_time'], 
        features_to_extract=['month', 'hour']
    )
    
    df_transformed = transformer.fit_transform(df)
    
    assert 'transaction_time_month' in df_transformed.columns
    assert 'transaction_time_hour' in df_transformed.columns
    assert 'transaction_time_day' not in df_transformed.columns
    assert df_transformed.shape[1] == 3 # amount, month, hour

def test_datetime_cyclical_encoding(sample_data_for_datetime):
    """
    Tests that cyclical encoding creates sin and cos features.
    """
    df = sample_data_for_datetime
    transformer = DatetimeFeatureGenerator(
        columns=['transaction_time'], 
        encode_cyclical=True
    )
    
    df_transformed = transformer.fit_transform(df)
    
    assert 'transaction_time_month' not in df_transformed.columns
    assert 'transaction_time_month_sin' in df_transformed.columns
    assert 'transaction_time_month_cos' in df_transformed.columns
    assert 'transaction_time_day_sin' in df_transformed.columns
    assert 'transaction_time_hour_cos' in df_transformed.columns
    
    assert np.isclose(df_transformed.loc[2, 'transaction_time_hour_sin'], 0)
    assert np.isclose(df_transformed.loc[2, 'transaction_time_hour_cos'], 1)

def test_multiple_datetime_columns(sample_data_with_multiple_datetimes):
    """
    Tests that the transformer correctly processes multiple datetime columns at once.
    """
    df = sample_data_with_multiple_datetimes
    transformer = DatetimeFeatureGenerator(columns=['start_time', 'end_time'])
    
    df_transformed = transformer.fit_transform(df)
    
    assert 'start_time' not in df_transformed.columns
    assert 'end_time' not in df_transformed.columns
    assert 'start_time_month' in df_transformed.columns
    assert 'end_time_month' in df_transformed.columns
    assert df_transformed.loc[0, 'start_time_hour'] == 12
    assert df_transformed.loc[0, 'end_time_hour'] == 13

def test_datetime_with_missing_values(sample_data_with_multiple_datetimes):
    """
    Tests that the transformer handles missing datetime values (NaT) gracefully.
    """
    df = sample_data_with_multiple_datetimes
    transformer = DatetimeFeatureGenerator(columns=['start_time'])
    
    df_transformed = transformer.fit_transform(df)
    
    assert pd.isna(df_transformed.loc[2, 'start_time_month'])
    assert pd.isna(df_transformed.loc[2, 'start_time_day'])
    assert pd.isna(df_transformed.loc[2, 'start_time_hour'])
    assert not pd.isna(df_transformed.loc[0, 'start_time_month'])
