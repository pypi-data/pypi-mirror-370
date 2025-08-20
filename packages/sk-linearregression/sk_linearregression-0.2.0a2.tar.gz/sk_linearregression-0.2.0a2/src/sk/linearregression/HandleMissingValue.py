import pandas as pd
def HandleMissingValue(df, drop_tabel_names=[]):

    df.drop(columns=drop_tabel_names, inplace=True)
    # Calculate missing percentage per column
    null_percentage = df.isnull().sum() / len(df) * 100

    # Split columns by missing percentage
    null_percentage_most = null_percentage[null_percentage > 40].index.tolist()
    null_percentage_less = null_percentage[null_percentage < 40].index.tolist()

    # Drop high-missing columns
    df.drop(columns=null_percentage_most, inplace=True)

    # Fill low-missing categorical columns with mode
    for col in null_percentage_less:
        if df[col].dtype == "object" or df[col].dtype.name == "category":
            df[col] = df[col].fillna(df[col].mode()[0])
        else:
            df[col] = df[col].fillna(df[col].median())  # better for numeric


    categorical_columns = df.select_dtypes(include=["object", "category"]).columns.tolist()
    df_encoded = pd.get_dummies(df, columns=categorical_columns)
    return df_encoded