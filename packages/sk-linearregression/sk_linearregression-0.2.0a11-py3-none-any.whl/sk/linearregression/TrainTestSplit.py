def TrainTestSplit(df, y_column_name, test_size=0.2):
    Y = df[y_conlumn_name]
    X = df.drop(columns=[y_column_name])
    X_test = X[:int(len(X) * test_size)]
    X_train = X[int(len(X) * test_size):]
    Y_test = Y[:int(len(Y) * test_size)]
    Y_train = Y[int(len(Y) * test_size):]
    return X_train, X_test, Y_train, Y_test