import numpy as np
import pandas as pd

def MinMaxScaler(X, feature_range=(0, 1), min_vals=None, max_vals=None):
    # Convert to numeric array
    X = pd.DataFrame(X).select_dtypes(include=[np.number]).to_numpy(dtype=float)
    min_range, max_range = feature_range

    # Use provided min/max (for test set) or compute from data
    X_min = X.min(axis=0) if min_vals is None else min_vals
    X_max = X.max(axis=0) if max_vals is None else max_vals

    denom = np.where(X_max - X_min == 0, 1, X_max - X_min)

    X_scaled = (X - X_min) / denom * (max_range - min_range) + min_range
    return X_scaled
