import numpy as np

def MinMaxScaler(X, feature_range=(0, 1)):
    """
    Scale all numeric columns to the given feature range.
    """
    X = X.copy()
    min_range, max_range = feature_range

    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X_numeric = X[numeric_cols]

    X_min = X_numeric.min()
    X_max = X_numeric.max()
    denom = X_max - X_min
    denom[denom == 0] = 1  # prevent division by zero

    X_scaled = (X_numeric - X_min) / denom * (max_range - min_range) + min_range

    # Replace numeric columns in X with scaled values
    X[numeric_cols] = X_scaled

    return X