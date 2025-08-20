def TrainTestSplit(X, Y, test_size=0.2):
    split_idx = int(len(X) * (1 - test_size))  # train size
    X_train = X[:split_idx]
    X_test = X[split_idx:]
    Y_train = Y[:split_idx]
    Y_test = Y[split_idx:]
    return X_train, X_test, Y_train, Y_test
