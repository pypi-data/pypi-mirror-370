import pandas as pd
import numpy as np

def MinMaxScaler(X, feature_range=(0, 1)):
    X = X.copy()  # avoid modifying original
    min_range, max_range = feature_range

    # Select only numeric columns
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

    X_numeric = X[numeric_cols].values.astype(float)

    X_min = X_numeric.min(axis=0)
    X_max = X_numeric.max(axis=0)
    denom = np.where(X_max - X_min == 0, 1, X_max - X_min)

    X_scaled = (X_numeric - X_min) / denom * (max_range - min_range) + min_range

    # Convert back to DataFrame to keep column names
    X_scaled_df = pd.DataFrame(X_scaled, columns=numeric_cols, index=X.index)

    # Add back non-numeric columns unchanged
    non_numeric_cols = X.drop(columns=numeric_cols)
    X_scaled_df = pd.concat([X_scaled_df, non_numeric_cols], axis=1)

    return X_scaled_df
