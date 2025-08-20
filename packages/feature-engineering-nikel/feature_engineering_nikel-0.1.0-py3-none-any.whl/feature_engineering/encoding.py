# feature_engineering_suite/encoding.py

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class Encoder(BaseEstimator, TransformerMixin):
    """
    A flexible encoder for categorical variables.
    """
    def __init__(self, method='onehot', columns=None, mapping=None):
        self.method = method
        self.columns = columns
        self.mapping = mapping
        self.columns_to_encode_ = []

    def fit(self, X, y=None):
        """
        Identifies the columns to encode.
        """
        if self.columns:
            self.columns_to_encode_ = self.columns
        else:
            self.columns_to_encode_ = list(X.select_dtypes(include=['object', 'category']).columns)
        
        if self.method == 'ordinal' and not self.mapping:
            raise ValueError("A 'mapping' dictionary must be provided for ordinal encoding.")
            
        return self

    def transform(self, X):
        """
        Applies the specified encoding method.
        """
        X_copy = X.copy()
        
        if self.method == 'onehot':
            X_copy = pd.get_dummies(X_copy, columns=self.columns_to_encode_, dummy_na=False, drop_first=True)
        
        elif self.method == 'ordinal':
            for col in self.columns_to_encode_:
                if col in self.mapping:
                    X_copy[col] = X_copy[col].map(self.mapping[col])
                else:
                    print(f"Warning: No mapping provided for column '{col}'. It will be skipped.")
        else:
            raise ValueError("method must be either 'onehot' or 'ordinal'")
            
        return X_copy