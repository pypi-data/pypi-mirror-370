# feature_engineering_suite/selection.py

import pandas as pd
import numpy as np
from sklearn.feature_selection import RFE, mutual_info_classif, mutual_info_regression
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureSelector(BaseEstimator, TransformerMixin):
    """
    Provides advanced methods for selecting the best features from a dataset.
    """
    def __init__(self, correlation_threshold=0.9, selection_method='correlation', estimator=None, n_features_to_select=None):
        """
        Initializes the FeatureSelector.

        Parameters
        ----------
        correlation_threshold : float, optional
            The threshold for dropping correlated features (default is 0.9).
        selection_method : str, optional
            The method to use for selection: 'correlation', 'rfe', 'model_importance'.
        estimator : scikit-learn estimator, optional
            The model to use for 'rfe' or 'model_importance' methods.
        n_features_to_select : int, optional
            The number of features to select for 'rfe' or 'model_importance'.
        """
        self.correlation_threshold = correlation_threshold
        self.selection_method = selection_method
        self.estimator = estimator
        self.n_features_to_select = n_features_to_select
        self.features_to_drop_ = []
        self.selected_features_ = []

    def fit(self, X, y=None):
        """
        Learns which features to select or drop based on the chosen method.
        """
        if self.selection_method == 'correlation':
            corr_matrix = X.corr().abs()
            upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            self.features_to_drop_ = [column for column in upper_tri.columns if any(upper_tri[column] > self.correlation_threshold)]
        
        elif self.selection_method == 'rfe':
            if self.estimator is None:
                raise ValueError("An 'estimator' must be provided for RFE.")
            rfe = RFE(self.estimator, n_features_to_select=self.n_features_to_select)
            rfe.fit(X, y)
            self.selected_features_ = X.columns[rfe.support_].tolist()

        elif self.selection_method == 'model_importance':
            if self.estimator is None:
                raise ValueError("An 'estimator' must be provided for model importance.")
            self.estimator.fit(X, y)
            importances = pd.Series(self.estimator.feature_importances_, index=X.columns)
            self.selected_features_ = importances.nlargest(self.n_features_to_select).index.tolist()
            
        else:
            raise ValueError("selection_method must be 'correlation', 'rfe', or 'model_importance'")
            
        return self

    def transform(self, X):
        """
        Applies the feature selection to the dataframe.
        """
        if self.selection_method == 'correlation':
            return X.drop(columns=self.features_to_drop_)
        else:
            return X[self.selected_features_]

    @staticmethod
    def get_mutual_info_importance(X, y, task='classification', discrete_features='auto'):
        """
        Calculates feature importance using mutual information.
        """
        if task == 'classification':
            importance = mutual_info_classif(X, y, discrete_features=discrete_features)
        elif task == 'regression':
            importance = mutual_info_regression(X, y, discrete_features=discrete_features)
        else:
            raise ValueError("task must be either 'classification' or 'regression'")
            
        feature_importance = pd.Series(importance, index=X.columns)
        return feature_importance.sort_values(ascending=False)
