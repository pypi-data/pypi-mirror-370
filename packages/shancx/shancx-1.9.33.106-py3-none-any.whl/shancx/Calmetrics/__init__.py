#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
def start():
    print("import successful")
# constants
__author__ = 'shancx'
 
__author_email__ = 'shancx@126.com'

# @Time : 2025/08/19 下午11:31
# @Author : shanchangxi
# @File : Calmetrics.py
 
 
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
    