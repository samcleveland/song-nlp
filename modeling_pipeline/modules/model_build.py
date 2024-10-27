import numpy as np
import pandas as pd

import xgboost as xgb
from xgboost import DMatrix

import matplotlib.pyplot as plt



def stratify_folds(df:pd.DataFrame, stratify_by:list, groups:list = None, nfolds:int = 5, seed:int = 60601) -> list[tuple]:
    
    stratcol = list(groups + stratify_by)
    n, g = len(stratify_by), len(groups)
    np.random.seed(seed=seed)
    
    if groups is None:
        group_df = df
    else:
        group_df = df[stratcol].groupby(groups, as_index=False).mean()
        
    l = len(group_df)
    
    rand = np.random.normal(loc=0, scale=1, size=l)
    
    stratscore = np.zeros(l)
    
    for i in range(n):
        col = group_df[stratcol[g+i]].to_numpy()
        perc = np.percentile(col, np.arange(1, 99.001, step=1))
        digi = np.digitize(col, perc)
        stratlist = np.argsort(stratscore)
        
    stratassign = np.zeros(l).astype(int)
    
    for ifold in range(nfolds):
        stratassign[stratlist[ifold::nfolds]] = ifold
        group_df['fold_assignment'] = pd.DataFrame(stratassign)
        
    append = list(groups + ['fold_assignment'])
        
    df1 = df.merge(group_df[append], how='left', left_on=groups, right_on=groups)[['fold_assignment']]
    
    folds = []
    
    for i in range(nfolds):
        outfold = df1[df1['fold_assignment'] == i].index.tolist()
        infold = df1[df1['fold_assignment'] != i].index.tolist()
        folds += [(infold, outfold)]
        
    return folds

def create_testing_dataframes(df:pd.DataFrame, 
                              ids:list, 
                              stratify_by:list, 
                              dv:list, 
                              nfolds:int = 5, 
                              seed:int = 60601):
    
    fold_strategy = stratify_folds(df, stratify_by, groups=ids, nfolds=nfolds, seed=seed)
    
    # set training and validation dataframes
    training = df.iloc[fold_strategy[0][0]]
    validation = df.iloc[fold_strategy[0][1]]
    
    # Create train and validation df
    X_train = training[[x for x in df.columns if x not in dv + ids]]
    y_train = training[dv]
    
    X_val = validation[[x for x in df.columns if x not in dv + ids]]
    y_val = validation[dv]
    
    dtrain = DMatrix(data=X_train, label=y_train, enable_categorical=True)
    dval = DMatrix(data=X_val, label=y_val, enable_categorical=True)
    
    return (training, validation, X_train, y_train, X_val, y_val, dtrain, dval)


def lift_chart(predicted:list, actual:list, bins = 10) -> None:
    # generate deciles for scored songs
    results_df = pd.DataFrame([predicted, actual], index=['predicted','actual']).T
    results_df['decile'] = pd.qcut(results_df['predicted'].rank(method='first'), bins, labels=np.array(range(bins)))

    # Aggregate data for lift charts
    results_df = results_df.groupby('decile', observed=False).mean()

    # Plot
    x = np.array(results_df.index)  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(layout='constrained')

    ind = np.arange(len(results_df.index))

    ax.bar(ind, results_df['predicted'], width, label='Predicted')
    ax.bar(ind+width, results_df['actual'], width, label='Actual')

    ax.set_ylabel('Tempo')
    ax.set_title('Tempo by Prediction Decile')
    ax.set_xticks(x, x)
    ax.legend(loc='upper left', ncols=3)
    
    plt.show()

    
    return results_df
    
    
    
    
    
    
    
    