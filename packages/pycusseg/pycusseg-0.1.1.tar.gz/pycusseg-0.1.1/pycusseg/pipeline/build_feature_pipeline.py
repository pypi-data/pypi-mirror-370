from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer
from sklearn.base import BaseEstimator
import pandas as pd
import yaml
from functools import reduce
from .factory import (
    ImputerFactory,
    TransformerFactory,
    ScalerFactory,
    EncoderFactory,
    ExtractDatePartsTransformer,
    TextVectorizerFactory,
    CutoffTransformer
)


class FeaturePipelineBuilder:
    """Class để xây dựng feature pipeline"""
    
    def __init__(self, config_path: str = "feature.yml"):
        self.config_path = config_path
        self.transformers = []
        self.used_columns = set()
        
    def _load_config(self):
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)
    
    def _build_steps(self, feature: dict) -> list:
        steps = feature.get('steps', [])
        if not steps:
            return [('identity', FunctionTransformer(lambda x: x))]
            
        # Kiểm tra nếu có drop=True thì trả về transformer để drop cột
       
            
        step_list = []
        for step in steps:
            if 'drop' in step:
                if step['drop'] == True:
                    return 'drop'
            if 'cutoff' in step:
                step_list.append(CutoffTransformer(step['cutoff']))
            if 'imputer' in step:
                step_list.append(ImputerFactory.run(step['imputer']))
            if 'transformer' in step:
                step_list.append(TransformerFactory.run(step['transformer']))
            if 'scaler' in step:
                step_list.append(ScalerFactory.run(step['scaler']))
            if 'encoder' in step:
                categories = step.get('categories', 'auto')
                step_list.append(EncoderFactory.run(step['encoder'], categories))
            if 'text_vectorizer' in step:
                step_list.append(TextVectorizerFactory.run(step['text_vectorizer'], step.get('max_features', None)))
        return step_list if step_list else [('identity', FunctionTransformer(lambda x: x))]
    

    def build(self) -> ColumnTransformer:
        config = self._load_config()
        
        for feature in config['features']:
            name = feature['name']
            if name in self.used_columns:
                continue
            self.used_columns.add(name)
            step_list = self._build_steps(feature)
            if step_list == 'drop':
                self.transformers.append((f"{name}", 'drop', [name]))
            else:
                pipeline = Pipeline(step_list)
                pipeline.set_output(transform='pandas')
                self.transformers.append((f"{name}", pipeline, [name]))
            
        column_transformer = ColumnTransformer(self.transformers, remainder='passthrough', verbose_feature_names_out=False)
        column_transformer.set_output(transform='pandas')
        return column_transformer

# class AggregateFeatureBuilder:
#     """Class để xây dựng các feature tổng hợp"""
    
#     def __init__(self, config_path: str, raw_df: pd.DataFrame):
#         self.config_path = config_path
#         self.raw_df = raw_df
#         self.transformers = []
#         self.transformed_dfs = []
        
#     def _load_config(self):
#         with open(self.config_path) as f:
#             return yaml.safe_load(f)
            
#     def build(self) -> tuple[list[BaseEstimator], pd.DataFrame]:
#         config = self._load_config()
        
#         for block in config['aggregations']:
#             groupby_key = block['groupby']
#             aggs = block['aggregations']

#             transformer = GroupbyAggregator(groupby_key, aggs)
#             transformer.fit(self.raw_df)

#             transformed_df = transformer.transform(self.raw_df)
#             self.transformers.append(transformer)
#             self.transformed_dfs.append(transformed_df)

#         df_merged = reduce(lambda left, right: pd.merge(left, right, how='left'), self.transformed_dfs)
#         return self.transformers, df_merged
