import numpy as np
class LinearRegression():
    def __init__(self, x_train, y_train, lr=.03, epochs=500):
        self.w = np.zeros((x_train.shape[1], 1)).astype(float)
        self.b = 0.0
        self.lr = lr
        self.epochs = epochs
        self.x_train = x_train.values.astype(float)
        self.y_train = y_train.values.reshape(-1, 1).astype(float)

    def predict(self, X, w, b):
        X = X.values.astype(float)
        y = X @ w + b
        return y

    def regression(self):
        m = self.x_train.shape[0]
        for i in range(self.epochs):
            y_pred = self.predict(self.x_train, self.w, self.b)

            # loss
            mse = 1 / (2 * m) * ((y_pred - self.y_train).T @ (y_pred - self.y_train))

            print(f"Mean Square Error is: {mse} in epoch: {i}")

            # gradiant
            dw = 1 / m * (self.x_train.T @ (y_pred - self.y_train))
            db = 1 / m * np.sum(y_pred - self.y_train)

            # update weights
            self.w -= self.lr * dw
            self.b -= self.lr * db
        return self.w, self.b
