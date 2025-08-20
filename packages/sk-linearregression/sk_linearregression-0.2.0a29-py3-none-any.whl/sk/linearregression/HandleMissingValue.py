import pandas as pd
import numpy as np

def HandleMissingValue(X):
    X = X.copy()
    
    # Fill missing numeric values with median
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        X[col] = X[col].fillna(X[col].median())
    
    # Fill missing categorical values with mode
    categorical_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
    for col in categorical_cols:
        X[col] = X[col].fillna(X[col].mode()[0])
    
    # Convert all categorical columns to dummy variables
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
    
    # Ensure all columns are float
    X_encoded = X_encoded.astype(float)
    
    return X_encoded
