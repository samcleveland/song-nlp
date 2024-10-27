import pandas as pd
import numpy as np
import xgboost as xgb
from hyperopt import STATUS_OK, Trials, fmin, tpe, space_eval

class Hyperopt_XGB:
    def __init__(self, 
                 model_type: str, 
                 X_train: pd.DataFrame,
                 y_train: pd.DataFrame,
                 X_test: pd.DataFrame,
                 y_test: pd.DataFrame,
                 feature_space: dict,
                 hyperparameter_space: dict,
                 sample_weight:list = None,
                 sample_weight_eval:list = None,
                 ):
        self.model_type = model_type
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.feature_space = feature_space
        self.hyperparameter_space = hyperparameter_space
        self.sample_weight = sample_weight
        self.sample_weight_eval = sample_weight_eval
        self.space = {**self.feature_space, **self.hyperparameter_space}
        
    def objective(self, params:dict) -> dict:
        
        hyperparameters = {k: params[k] for k in self.hyperparameter_space.keys()}
        
        cols = [i for i, j in params.items() if (i in self.feature_space.keys()) & (j == 1)]
        
        if self.model_type == 'xgb_regressor':
            model = xgb.XGBRegressor(**hyperparameters)
        elif self.model_type == 'binary_classifier':
            model = xgb.XGBClassifier(**hyperparameters)
            
        if self.sample_weight is None:
            model.fit(self.X_train[cols],
                      self.y_train,
                      eval_set = [(self.X_train[cols], self.y_train), (self.X_test[cols], self.y_test)],
                      verbose = False)
        else:
            model.fit(self.X_train[cols],
                      self.y_train,
                      eval_set = [(self.X_train[cols], self.y_train), (self.X_test[cols], self.y_test)],
                      sample_weight = self.sample_weight,
                      verbose = False)
            
        if (hyperparameters['eval_metric'] == 'rmse') | (hyperparameters['eval_metric'] == 'logloss'):
            loss = min(model.evals_result()['validation_1'][hyperparameters['eval_metric']])
            
        elif (hyperparameters['eval_metric'] == 'aucpr') | (hyperparameters['eval_metric'] == 'auc'):
            loss = -1 * max(model.evals_result()['validation_1'][hyperparameters['eval_metric']])
            
        return {'loss': loss, 'status': STATUS_OK, 'trained_model': model}
    
    def get_best_model(self, trials):
        valid_trial_list = [trial for trial in trials if STATUS_OK == trial['result']['status']]
        losses = [float(trial['result']['loss']) for trial in valid_trial_list]
        best_trial_obj = valid_trial_list[np.argmin(losses)]
        
        return best_trial_obj['result']['trained_model']
    
    
    # Need to figure out why space_eval is returning hyperparameters
    def optimize(self, max_evals = 20, seed = 60601):
        
        trials = Trials()
        best = fmin(fn = self.objective,
                    space = self.space,
                    algo = tpe.suggest,
                    max_evals = max_evals,
                    rstate = np.random.default_rng(seed=seed),
                    trials = trials)
        
        model = self.get_best_model(trials)
        
        return (space_eval(self.space, best), model)