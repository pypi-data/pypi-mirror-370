# feature_engineering_suite/__init__.py

from .selection import FeatureSelector
from .transformation import Transformer, Standardizer, Scaler, LogTransformer, BoxCoxTransformer
from .encoding import Encoder

__version__ = '0.1.0'