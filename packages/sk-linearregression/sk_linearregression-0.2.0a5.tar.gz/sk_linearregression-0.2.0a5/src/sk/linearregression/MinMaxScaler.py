import numpy as np

def MinMaxScaler(X, feature_range=(0, 1)):
    X = np.array(X, dtype=float)
    min, max = feature_range

    X_min = X.min(axis=0)
    X_max = X.max(axis=0)

    denom = np.where(X_max - X_min == 0, 1, X_max - X_min)

    X_scaled = (X - X_min) / denom * (max_range - min_range) + min_range

    return X_scaled