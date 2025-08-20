# tests/test_selection.py

import pandas as pd
import numpy as np
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from feature_engineering.selection import FeatureSelector

@pytest.fixture
def sample_data_for_selection():
    """Creates a sample DataFrame for testing selection features."""
    data = {
        'feat1': np.random.rand(100),
        'feat2': np.random.rand(100) * 10,
        'feat3': np.random.rand(100),
        'feat4_useless': np.random.rand(100) * 0.1,
        'target_class': np.random.randint(0, 2, 100),
        'target_reg': np.random.rand(100) * 50
    }
    df = pd.DataFrame(data)
    # Create a highly correlated feature
    df['feat1_correlated'] = df['feat1'] * 2 + np.random.normal(0, 0.05, 100)
    # Make feat2 more important for the target
    df['target_class'] = (df['feat2'] > 5).astype(int)
    return df

def test_correlation_selection(sample_data_for_selection):
    """
    Tests that highly correlated features are correctly identified and dropped.
    """
    df = sample_data_for_selection
    X = df[['feat1', 'feat2', 'feat1_correlated']]
    
    selector = FeatureSelector(selection_method='correlation', correlation_threshold=0.9)
    
    # Test fit method
    selector.fit(X)
    assert 'feat1_correlated' in selector.features_to_drop_
    
    # Test transform method
    X_transformed = selector.transform(X)
    assert 'feat1_correlated' not in X_transformed.columns
    assert 'feat1' in X_transformed.columns
    assert X_transformed.shape[1] == 2

def test_rfe_selection(sample_data_for_selection):
    """
    Tests Recursive Feature Elimination (RFE) selection.
    """
    df = sample_data_for_selection
    X = df[['feat1', 'feat2', 'feat3', 'feat4_useless']]
    y = df['target_class']
    
    estimator = LogisticRegression()
    selector = FeatureSelector(
        selection_method='rfe', 
        estimator=estimator, 
        n_features_to_select=2
    )
    
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    
    assert len(selector.selected_features_) == 2
    assert X_transformed.shape[1] == 2
    # 'feat2' should be selected as it's most important
    assert 'feat2' in selector.selected_features_

def test_model_importance_selection(sample_data_for_selection):
    """
    Tests selection based on model feature importance.
    """
    df = sample_data_for_selection
    X = df[['feat1', 'feat2', 'feat3', 'feat4_useless']]
    y = df['target_class']
    
    estimator = RandomForestClassifier(n_estimators=10, random_state=42)
    selector = FeatureSelector(
        selection_method='model_importance',
        estimator=estimator,
        n_features_to_select=1
    )
    
    selector.fit(X, y)
    X_transformed = selector.transform(X)
    
    assert len(selector.selected_features_) == 1
    assert X_transformed.shape[1] == 1
    # 'feat2' should have the highest importance
    assert 'feat2' in selector.selected_features_

def test_estimator_not_provided_raises_error(sample_data_for_selection):
    """
    Tests that an error is raised if an estimator is required but not provided.
    """
    df = sample_data_for_selection
    X = df[['feat1', 'feat2']]
    
    # Test with RFE
    with pytest.raises(ValueError, match="An 'estimator' must be provided for RFE."):
        selector_rfe = FeatureSelector(selection_method='rfe')
        selector_rfe.fit(X, df['target_class'])
        
    # Test with model_importance
    with pytest.raises(ValueError, match="An 'estimator' must be provided for model importance."):
        selector_model = FeatureSelector(selection_method='model_importance')
        selector_model.fit(X, df['target_class'])

def test_get_mutual_info_importance(sample_data_for_selection):
    """
    Tests the static method for mutual information importance.
    """
    df = sample_data_for_selection
    X = df[['feat1', 'feat2', 'feat3']]
    y_class = df['target_class']
    y_reg = df['target_reg']

    # Test classification
    importance_class = FeatureSelector.get_mutual_info_importance(X, y_class, task='classification')
    assert isinstance(importance_class, pd.Series)
    assert not importance_class.isnull().any()
    assert importance_class.index[0] == 'feat2' # feat2 should be most important

    # Test regression
    importance_reg = FeatureSelector.get_mutual_info_importance(X, y_reg, task='regression')
    assert isinstance(importance_reg, pd.Series)
    assert not importance_reg.isnull().any()
