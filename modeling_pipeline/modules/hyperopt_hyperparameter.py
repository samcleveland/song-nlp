

import numpy as np
from hyperopt import hp
from hyperopt.pyll.base import scope

def create_hyperopt_feature_space(feature_list: list) -> dict:
    feature_space = {}
    for col in feature_list:
        feature_space[col] = hp.choice(col, [0, 1])
        
    return feature_space

def create_hyperopt_hyperparameters_space(model_type:str = 'xgb_regressor') -> dict:
    
    hyperparameter_space = {
        'colsample_bytree':         hp.uniform('colsample_bytree', 0.5, 1),
        'early_stopping_rounds':    hp.uniform('early_stopping_rounds', 5, 15),
        'enable_categorical':       True,
        'eta':                      hp.quniform('eta', 0.025, 0.5, 0.025),
        'gamma':                    hp.uniform('gamma', 0, 9),
        'max_delta_step':           hp.uniform('max_delta_step', 1, 10),
        'min_child_weight':         scope.int(hp.quniform('min_child_weight', 0, 10, 1)),
        'max_depth':                scope.int(hp.quniform('max_depth', 3, 15, 1)),
        'n_estimators':             scope.int(hp.quniform('n_estimators', 100, 1500, 100)),
        'n_jobs':                   -1,
        'random_state':             60601,
        'reg_alpha':                scope.int(hp.quniform('reg_alpha', 0, 100, 5)),
        'reg_lambda':               hp.uniform('reg_lambda', 0, 1)
        }
    
    if model_type == 'xgb_regressor':
        hyperparameter_space['objective'] = 'reg:squarederror'
        hyperparameter_space['eval_metric'] = 'rmse'
        
    return hyperparameter_space