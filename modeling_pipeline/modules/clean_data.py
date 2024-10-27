import numpy as np
import pandas as pd

def remove_feature(model_features: pd.DataFrame, col) -> pd.DataFrame:
    model_features.loc[model_features['feature'] == col, 'in_model'] = 0
    return model_features

def print_removed_features(columns:list, change:str) -> None:
    print(f'The features {change}:\n')
    print(*sorted(columns), sep = '\n')
    print('\n')

def remove_id_columns_from_feature_set(model_features: pd.DataFrame, verbose:bool = True) -> pd.DataFrame:
    model_features_update = model_features.copy()
    
    columns = model_features[model_features['stat_data_type'] == 'id']['feature'].tolist()
    
    for col in columns:
        model_features_updated = remove_feature(model_features_update, col)
        
    if verbose:
        print_removed_features(columns, 'removed from feature set')
        
    return model_features_updated
    
def clean_continuous_numeric_columns(df:pd.DataFrame, model_features:pd.DataFrame, verbose:bool = True) -> pd.DataFrame:
    df_clean = df.copy()
    
    columns = model_features[model_features['stat_data_type'] == 'continuous - numeric']['feature'].tolist()
    
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors = 'coerce')
        df_clean[col] = df_clean[col].astype(float)
        
    if verbose:
        print_removed_features(columns, 'converted to float64')
        
    return df_clean
        
def clean_ordinal_categorical_columns(df:pd.DataFrame, model_features:pd.DataFrame, verbose:bool = True) -> pd.DataFrame:
    df_clean = df.copy()
    
    columns = model_features[model_features['stat_data_type'] == 'ordinal - categorical']['feature'].tolist()
    
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors = 'coerce')
        df_clean[col] = df_clean[col].astype('category')
        
    if verbose:
        print_removed_features(columns, 'converted to category')
        
    return df_clean
        

def clean_binary_categorical_columns(df:pd.DataFrame, model_features:pd.DataFrame, verbose:bool = True) -> pd.DataFrame:
    df_clean = df.copy()
    
    columns = model_features[model_features['stat_data_type'] == 'binary - categorical']['feature'].tolist()
    
    for col in columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors = 'coerce')
        df_clean[col] = df_clean[col].astype(int)
        
    if verbose:
        print_removed_features(columns, 'converted to 0/1 integer')
        
    return df_clean