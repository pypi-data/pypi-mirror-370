import pandas as pd

def HandleMissingValue(df, y_column_name, drop_tabel_names=None):
    if drop_tabel_names is None:
        drop_tabel_names = []

    # Drop explicitly specified columns (except target)
    drop_columns = [col for col in drop_tabel_names if col != y_column_name]
    if drop_columns:
        df.drop(columns=drop_columns, inplace=True)

    # Calculate missing percentage per column
    null_percentage = df.isnull().sum() / len(df) * 100

    # Identify columns to drop or fill (never drop target)
    null_percentage_most = [col for col in null_percentage[null_percentage > 40].index
                            if col != y_column_name]
    null_percentage_less = [col for col in null_percentage[null_percentage <= 40].index
                            if col != y_column_name]

    # Drop high-missing columns (excluding target)
    if null_percentage_most:
        df.drop(columns=null_percentage_most, inplace=True)

    # Fill low-missing categorical/numeric columns
    for col in null_percentage_less:
        if df[col].dtype == "object" or df[col].dtype.name == "category":
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            df[col] = df[col].fillna(df[col].median())

    # One-hot encode categorical columns
    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    df_encoded = pd.get_dummies(df, columns=categorical_columns)

    return df_encoded
