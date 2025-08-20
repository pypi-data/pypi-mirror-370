import pandas as pd
import numpy as np

def HandleMissingValue(X):
    # Calculate missing percentage per column
    null_percentage = X.isnull().sum() / len(X) * 100

    # Split columns by missing percentage
    null_percentage_most = null_percentage[null_percentage > 40].index.tolist()
    null_percentage_less = null_percentage[null_percentage <= 40].index.tolist()

    # Drop high-missing columns
    X = X.drop(columns=null_percentage_most)

    # Fill low-missing columns
    for col in null_percentage_less:
        if X[col].dtype == "object" or X[col].dtype.name == "category":
            X[col] = X[col].fillna(X[col].mode()[0])
        else:
            X[col] = X[col].fillna(X[col].median())

    # Convert categorical columns to numeric using one-hot encoding
    categorical_columns = X.select_dtypes(include=["object", "category"]).columns.tolist()
    X_encoded = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

    # Ensure all columns are numeric (float)
    X_encoded = X_encoded.astype(float)

    return X_encoded
