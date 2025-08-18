import numpy as np
import logging
logging.basicConfig(level=logging.INFO)

class EqualiserError(Exception):
    pass

class MultiLinearRegression:
    def __init__(self,epoch=1000,lr=0.001):
        self.lr = lr
        self.epoch = epoch
        self.m = None
        self.b = 0

    def fit(self,x,y):

        x = np.array(x)  # shape: (n_samples, n_features)
        y = np.array(y)

        if(len(x) != len(y)):
            raise EqualiserError("x and y are not equal")
        
        n_samples, n_features = x.shape
        self.m = np.zeros(n_features)
        
        logging.info("Training Started...")
        prev_loss = float('inf')
        for i in range(self.epoch):
            y_pred = np.dot(x, self.m) + self.b
            error = y - y_pred

            loss = np.mean(error ** 2)
            logging.info(f"epoch {i+1}, loss: {loss:.4f}")

            prev_loss = loss


            m_grad = -2* np.dot(x.T , error) / n_samples
            b_grad = -2* np.mean(error)

            self.m = self.m - (self.lr * m_grad)
            self.b = self.b - (self.lr * b_grad)

        logging.info(f"Training finished.\n m = {self.m}, b = {self.b:.4f}")
        return self
    
    def predict(self,x):
        logging.info("Predicting...")
        y_pred = np.dot(x, self.m) + self.b
        y_pred = np.array(y_pred)
        logging.info(y_pred)
        return y_pred
    