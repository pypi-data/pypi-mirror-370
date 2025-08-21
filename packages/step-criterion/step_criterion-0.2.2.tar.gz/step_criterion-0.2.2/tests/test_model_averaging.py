#!/usr/bin/env python3
"""
Quick test script for model averaging functionality
"""

import sys
import os
# Add parent directory to path so we can import step_criterion
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import statsmodels.api as sm
from step_criterion import step_aic, step_bic, step_criterion

# Load test data
longley = sm.datasets.longley.load_pandas().data
longley.rename(columns={'TOTEMP':'y'}, inplace=True)

print("Testing AIC model averaging...")
result_aic = step_aic(longley, initial='y ~ 1', 
                     scope='y ~ GNPDEFL + GNP + UNEMP + ARMED + POP + YEAR', 
                     model_averaging=True, trace=0)

print("AIC Model weights:")
print(result_aic.model_weights)
print(f"Number of AIC models with substantial support (weight > 0.1): {(result_aic.model_weights['Weight'] > 0.1).sum()}")

print("\n" + "="*60 + "\n")

print("Testing BIC model averaging...")
result_bic = step_bic(longley, initial='y ~ 1', 
                     scope='y ~ GNPDEFL + GNP + UNEMP + ARMED + POP + YEAR', 
                     model_averaging=True, trace=0)

print("BIC Model weights:")
print(result_bic.model_weights)
print(f"Number of BIC models with substantial support (weight > 0.1): {(result_bic.model_weights['Weight'] > 0.1).sum()}")

print("\n" + "="*60 + "\n")

print("Testing step_criterion with model averaging...")
result_sc = step_criterion(longley, initial='y ~ 1', 
                          scope='y ~ GNPDEFL + GNP + UNEMP + ARMED + POP + YEAR', 
                          criterion='aic', model_averaging=True, trace=0)

print("step_criterion AIC Model weights:")
print(result_sc.model_weights)

print("\nAll tests completed successfully!")
