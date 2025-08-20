# feature_engineering_suite/transformation.py

import pandas as pd
import numpy as np
from scipy.stats import boxcox
from sklearn.preprocessing import StandardScaler, MinMaxScaler, PolynomialFeatures
from sklearn.base import BaseEstimator, TransformerMixin
from itertools import combinations

class Transformer(BaseEstimator, TransformerMixin):
    """Base class for numerical transformations."""
    def __init__(self, columns=None):
        self.columns = columns if columns is None or isinstance(columns, list) else [columns]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        raise NotImplementedError

class Standardizer(Transformer):
    """Applies StandardScaler to specified columns."""
    def fit(self, X, y=None):
        self.scaler = StandardScaler()
        self.scaler.fit(X[self.columns])
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        X_copy[self.columns] = self.scaler.transform(X_copy[self.columns])
        return X_copy

class Scaler(Transformer):
    """Applies MinMaxScaler to specified columns."""
    def fit(self, X, y=None):
        self.scaler = MinMaxScaler()
        self.scaler.fit(X[self.columns])
        return self
        
    def transform(self, X):
        X_copy = X.copy()
        X_copy[self.columns] = self.scaler.transform(X_copy[self.columns])
        return X_copy

class LogTransformer(Transformer):
    """Applies a log transformation to specified columns."""
    def transform(self, X):
        X_copy = X.copy()
        for col in self.columns:
            if (X_copy[col] <= 0).any():
                X_copy[col] = np.log1p(X_copy[col] - X_copy[col].min())
            else:
                X_copy[col] = np.log(X_copy[col])
        return X_copy

class BoxCoxTransformer(Transformer):
    """Applies a Box-Cox transformation to specified columns."""
    def fit(self, X, y=None):
        self.stats_ = {}
        for col in self.columns:
            if (X[col] <= 0).any():
                print(f"Warning: Column '{col}' contains non-positive values. Box-Cox not applied.")
                self.stats_[col] = None
            else:
                _, lmbda = boxcox(X[col])
                self.stats_[col] = lmbda
        return self

    def transform(self, X):
        X_copy = X.copy()
        for col in self.columns:
            lmbda = self.stats_.get(col)
            if lmbda is not None:
                X_copy[col] = boxcox(X_copy[col], lmbda=lmbda)
        return X_copy

class PolynomialFeatureGenerator(Transformer):
    """Generates polynomial and interaction features."""
    def __init__(self, columns, degree=2, interaction_only=False, include_bias=False):
        super().__init__(columns)
        self.degree = degree
        self.interaction_only = interaction_only
        self.include_bias = include_bias
        self.poly = PolynomialFeatures(degree=self.degree, interaction_only=self.interaction_only, include_bias=self.include_bias)

    def fit(self, X, y=None):
        self.poly.fit(X[self.columns])
        return self
    
    def transform(self, X):
        X_copy = X.copy()
        poly_features = self.poly.transform(X_copy[self.columns])
        poly_df = pd.DataFrame(poly_features, index=X_copy.index, columns=self.poly.get_feature_names_out(self.columns))
        
        # Drop original columns and concatenate new polynomial features
        X_copy = X_copy.drop(columns=self.columns)
        X_copy = pd.concat([X_copy, poly_df], axis=1)
        return X_copy

class InteractionFeatureGenerator(Transformer):
    """Creates interaction features for specified column pairs."""
    def __init__(self, interaction_pairs):
        """
        Parameters
        ----------
        interaction_pairs : list of tuples
            A list where each tuple contains two column names to interact.
            e.g., [('feat1', 'feat2'), ('feat1', 'feat3')]
        """
        if not all(isinstance(p, tuple) and len(p) == 2 for p in interaction_pairs):
            raise ValueError("interaction_pairs must be a list of tuples with two elements each.")
        self.interaction_pairs = interaction_pairs

    def transform(self, X):
        X_copy = X.copy()
        for col1, col2 in self.interaction_pairs:
            new_col_name = f"{col1}_x_{col2}"
            X_copy[new_col_name] = X_copy[col1] * X_copy[col2]
        return X_copy

class DatetimeFeatureGenerator(Transformer):
    """
    Extracts specified features from datetime columns, with an option to encode them cyclically.
    """
    def __init__(self, columns, features_to_extract=['month', 'day', 'hour'], encode_cyclical=False):
        """
        Parameters
        ----------
        columns : list
            List of datetime column names to transform.
        features_to_extract : list, optional
            List of time units to extract. Can include 'month', 'day', 'hour'. 
            Default is ['month', 'day', 'hour'].
        encode_cyclical : bool, optional
            Whether to encode the extracted features cyclically (sin/cos). Default is False.
        """
        super().__init__(columns)
        self.features_to_extract = features_to_extract
        self.encode_cyclical = encode_cyclical

    def transform(self, X):
        """
        Applies the datetime feature extraction.
        """
        X_copy = X.copy()
        for col in self.columns:
            # Ensure the column is in datetime format
            dt_col = pd.to_datetime(X_copy[col])
            
            if 'month' in self.features_to_extract:
                if self.encode_cyclical:
                    X_copy[f'{col}_month_sin'] = np.sin(2 * np.pi * dt_col.dt.month / 12)
                    X_copy[f'{col}_month_cos'] = np.cos(2 * np.pi * dt_col.dt.month / 12)
                else:
                    X_copy[f'{col}_month'] = dt_col.dt.month

            if 'day' in self.features_to_extract:
                if self.encode_cyclical:
                    days_in_month = dt_col.dt.days_in_month
                    X_copy[f'{col}_day_sin'] = np.sin(2 * np.pi * dt_col.dt.day / days_in_month)
                    X_copy[f'{col}_day_cos'] = np.cos(2 * np.pi * dt_col.dt.day / days_in_month)
                else:
                    X_copy[f'{col}_day'] = dt_col.dt.day

            if 'hour' in self.features_to_extract:
                if self.encode_cyclical:
                    X_copy[f'{col}_hour_sin'] = np.sin(2 * np.pi * dt_col.dt.hour / 24)
                    X_copy[f'{col}_hour_cos'] = np.cos(2 * np.pi * dt_col.dt.hour / 24)
                else:
                    X_copy[f'{col}_hour'] = dt_col.dt.hour
            
            # Drop the original datetime column
            X_copy = X_copy.drop(columns=[col])
            
        return X_copy
