import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
from sklearn.base import BaseEstimator


class EqualiserError(Exception):
    pass


class LinearRegression(BaseEstimator):
    def __init__(self,epoch=1000,lr=0.001):
        self.lr = lr
        self.epoch = epoch
        self.m = 0
        self.b = 0

    def fit(self,x,y):
        if (len(x) != len(y)):
            raise EqualiserError("x and y are not equal")
        
        logging.info("Training Started...")
        prev_loss = float('inf')
        for i in range(self.epoch):
            y_pred = self.m * x + self.b
            error = y - y_pred

            loss = np.mean(error**2)
            logging.info(f"epoch{i+1}, loss: {loss:.4f}")

            if loss > prev_loss:
                logging.warning(f"Stopping Early as loss started incresing at {i+1} epoch")
                break
            prev_loss = loss

            m_grad = -2* np.mean(x *error)
            b_grad = -2* np.mean(error)

            self.m = self.m - (self.lr * m_grad)
            self.b = self.b - (self.lr * b_grad)

        logging.info(f"Training finished.\n m = {self.m:.4f}, b = {self.b:.4f}")
        return self


    def predict(self,x):
        logging.info("Predicting")
        y_pred = self.m * x + self.b
        np.array(y_pred)
        logging.info(y_pred)
        return y_pred
    
    @staticmethod
    def mse_score(y_true , y_pred):
        n = len(y_true)
        return (np.sum((y_true - y_pred)**2)/n)
    
    @staticmethod
    def r2_score(y_true , y_pred):
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)
        
    