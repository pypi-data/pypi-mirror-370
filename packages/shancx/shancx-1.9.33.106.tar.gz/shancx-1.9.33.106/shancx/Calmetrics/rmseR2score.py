 
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import pearsonr
import numpy as np
def calculate_metrics(y_true, y_pred):
    # Calculate metrics
    correlation, _ = pearsonr(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mask = y_true != 0
    y_true = y_true[mask]
    y_pred = y_pred[mask]
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)    
    
"""
dt_res[f'{flag}'] = dt_res[f'{flag}'].astype(float)
dt_res[f'{flag}_p'] = dt_res[f'{flag}_p'].astype(float)
dt_ = dt_res[(dt_res[f'{flag}'] != 0) & (dt_res[f'{flag}_p'] != 0)]
dt_ = dt_res[(dt_res[f'{flag}'] < 900000.0) & (dt_res[f'{flag}_p'] < 900000.0)]      
dt_.replace([np.inf, -np.inf], np.nan, inplace=True)
dt_.dropna(inplace=True)
correlation, rmse, mape, r2 = calculate_metrics(dt_[f"{flag}"], dt_[f"{flag}_p"])
"""
    