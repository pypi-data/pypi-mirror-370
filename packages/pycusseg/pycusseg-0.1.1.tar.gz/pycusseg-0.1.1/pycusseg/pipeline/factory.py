from sklearn.impute import SimpleImputer
from sklearn.preprocessing import (StandardScaler, 
                                   MinMaxScaler, 
                                   RobustScaler,
                                   MaxAbsScaler,
                                   OneHotEncoder,
                                   OrdinalEncoder,
                                   QuantileTransformer,
                                   PowerTransformer,
                                   FunctionTransformer, 

                                   )
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

class GroupbyAggregator(BaseEstimator, TransformerMixin):
    def __init__(self, groupby_key, aggs):
        self.groupby_key = groupby_key
        self.aggs = aggs
        self.agg_result_ = None

    def fit(self, X, y=None):
        agg_dict = {}
        for spec in self.aggs:
            col = spec['column']
            ops = spec['ops']
            agg_dict[col] = ops

        df_agg = X.groupby(self.groupby_key).agg(agg_dict)
        df_agg.columns = [f"{col}_{op}" for col, op in df_agg.columns]
        df_agg.reset_index(inplace=True)
        self.agg_result_ = df_agg
        return self

    def transform(self, X):
        return X.merge(self.agg_result_, on=self.groupby_key, how='left')

class ExtractDatePartsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, parts):
        self.parts = parts

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = pd.to_datetime(X.squeeze(), errors='coerce')
        out = pd.DataFrame()
        if 'year' in self.parts:
            out['year'] = X.dt.year
        if 'month' in self.parts:
            out['month'] = X.dt.month
        if 'weekday' in self.parts:
            out['weekday'] = X.dt.weekday
        return out
class TransformerFactory:
    """Factory class để tạo các transformer khác nhau"""
    
    @staticmethod
    def run(transformer_dict: dict) -> tuple:
        transformer_type = transformer_dict.get('type', None)
        if transformer_type == 'quantile':
            return ('quantile', QuantileTransformer(output_distribution='normal', random_state=42))
        if transformer_type == 'log':
            return ('log', FunctionTransformer(np.log))
        if transformer_type == 'log1p':
            return ('log1p', FunctionTransformer(np.log1p))
        if transformer_type == 'powertransformer':
            method = transformer_dict.get('method', 'box-cox')
            return ('powertransformer', PowerTransformer(method=method, standardize=True))
        else:
            raise ValueError(f"Không hỗ trợ loại transformer: {transformer_type}")
class ScalerFactory:
    """Factory class để tạo các scaler khác nhau"""
    
    @staticmethod
    def run(scaler_dict: dict) -> tuple:
        scaler_type = scaler_dict.get('type', None)
        if scaler_type == 'standard':
            return ('scaler', StandardScaler())
        elif scaler_type == 'minmax':
            return ('scaler', MinMaxScaler())
        elif scaler_type == 'robust':
            return ('scaler', RobustScaler())
        elif scaler_type == 'maxabs':
            return ('scaler', MaxAbsScaler())
        else:
            raise ValueError(f"Không hỗ trợ loại scaler: {scaler_type}")

class EncoderFactory:
    """Factory class để tạo các encoder khác nhau"""
    
    @staticmethod
    def run(encoder_dict: dict) -> tuple:
        encoder_type = encoder_dict.get('type', None)
        if encoder_type == 'onehot':
            return ('encoder', OneHotEncoder(sparse_output=False, handle_unknown='ignore'))
        elif encoder_type == 'ordinal':
            categories = encoder_dict.get('categories', 'auto')
            cats = [categories] if categories != 'auto' else 'auto'
            return ('encoder', OrdinalEncoder(categories=cats))
        else:
            raise ValueError(f"Không hỗ trợ loại encoder: {encoder_type}")

class ImputerFactory:
    """Factory class để tạo các imputer khác nhau"""
    
    @staticmethod
    def run(imputer_config: dict) -> tuple:
        strategy = imputer_config.get('strategy', 'mean')
        if strategy == 'constant':
            fill_value = imputer_config.get('fill_value', None)
            return ('imputer', SimpleImputer(strategy=strategy, fill_value=fill_value))
        else:
            return ('imputer', SimpleImputer(strategy=strategy))
        
class TextVectorizerFactory:
    """Factory class để tạo các text vectorizer khác nhau"""
    
    @staticmethod
    def run(vectorizer_dict: dict) -> tuple:
        vectorizer_type = vectorizer_dict.get('type', None)
        max_features = vectorizer_dict.get('max_features', None)
        if vectorizer_type == 'tfidf':
            return ('text_vectorizer', TfidfVectorizer(max_features=max_features))
        else:
            raise ValueError(f"Không hỗ trợ loại vectorizer: {vectorizer_type}")
        
class CutoffTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, cutoff_dict: dict):
        self.lower = cutoff_dict.get('lower', None)
        self.upper = cutoff_dict.get('upper', None)
        self.right = cutoff_dict.get('right', True)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        if self.right:
            return X.clip(self.lower,    self.upper, axis=1)
        else:
            return X.clip(self.lower, self.upper, axis=1, inclusive='left')
