import pandas as pd
import numpy as np

def highly_correlated_features(df: pd.DataFrame, 
                               model_features: pd.DataFrame, 
                               corr_method:str = 'pearson', 
                               corr_threshold:float = 0.99,
                               verbose:bool = True) -> pd.DataFrame:
    
    model_features_updated = model_features.copy()
    
    # list of numeric features still in the model
    relevant_features = model_features_updated[(model_features_updated['in_model'] == 1) &
                                               ((model_features_updated['stat_data_type'] == 'discrete - numeric') |
                                               (model_features_updated['stat_data_type'] == 'continuous - numeric'))]['feature'].tolist()
    
    df_corr = df[relevant_features]
    
    # Correlation Matrix
    corr_matrix = df_corr.corr(method = corr_method).abs()
    
    # Get upper triangle portion of corr matrix
    upper = corr_matrix.where (np.triu(np.ones(corr_matrix.shape), k = 1).astype(bool))
    
    # Correlated features
    dropped_features = [col for col in upper.columns if any(upper[col] >= corr_threshold)]
    
    for col in dropped_features:
        if model_features_updated[model_features_updated['feature'] == col]['in_model'].item() == 1:
            model_features_updated.loc[model_features_updated['feature'] == col, 'in_model'] = 0
            
    if verbose:
        print(f'The featurees dropped for correlation >= {corr_threshold}:\n')
        print(*sorted(set(dropped_features)), sep = '\n')
        print('\n')
    
    return model_features_updated

def set_dependent_variable(df: pd.DataFrame, 
                           model_features: pd.DataFrame,
                           dv:list) -> pd.DataFrame:
    
    model_features_updated = model_features.copy()
    
    for col in dv:
        model_features_updated.loc[model_features_updated['feature'] == col, 'in_model'] = 0
        
    return model_features_updated

def remove_columns_from_feature_set(df: pd.DataFrame, model_features:pd.DataFrame, columns:list, verbose:bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_clean = df.copy()
    model_features_updated = model_features.copy()
    
    df_clean = df_clean.drop(columns, axis=1)
    
    for col in columns:
        model_features_updated.loc[model_features_updated['feature'] == col,'in_model'] = 0
        
    if verbose:
        print('Columns removed from the model: \n')
        print(*sorted(columns), sep='\n')
        print('\n')
        
    return df_clean, model_features_updated