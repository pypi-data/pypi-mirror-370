import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
from sklearn.base import BaseEstimator

class EqualiserError(Exception):
    pass

class DecisionTreeRegressor(BaseEstimator):
    def __init__(self, max_depth=3, min_samples_split=2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None

    class Node:
        def __init__(self, feature_index=None, threshold=None, left=None, right=None, value=None):
            self.feature_index = feature_index
            self.threshold = threshold
            self.left = left
            self.right = right
            self.value = value

    def fit(self, X, y):
        if len(X) != len(y):
            raise EqualiserError("X and y are not equal")
        
        logging.info("Training Started...")
        self.tree = self._build_tree(X, y)
        logging.info("Training finished.")
        return self

    def _build_tree(self, X, y, depth=0):
        n_samples, n_features = X.shape
        if n_samples < self.min_samples_split or depth >= self.max_depth:
            leaf_value = np.mean(y)
            return self.Node(value=leaf_value)

        best_feature, best_threshold = self._best_split(X, y)
        if best_feature is None:
            leaf_value = np.mean(y)
            return self.Node(value=leaf_value)

        left_idx = X[:, best_feature] <= best_threshold
        right_idx = X[:, best_feature] > best_threshold

        left = self._build_tree(X[left_idx], y[left_idx], depth+1)
        right = self._build_tree(X[right_idx], y[right_idx], depth+1)
        return self.Node(feature_index=best_feature, threshold=best_threshold, left=left, right=right)

    def _best_split(self, X, y):
        n_samples, n_features = X.shape
        if n_samples <= 1:
            return None, None

        best_mse = float('inf')
        split_idx, split_thresh = None, None

        for feature_index in range(n_features):
            thresholds = np.unique(X[:, feature_index])
            for t in thresholds:
                left_mask = X[:, feature_index] <= t
                right_mask = X[:, feature_index] > t
                if sum(left_mask) == 0 or sum(right_mask) == 0:
                    continue

                y_left, y_right = y[left_mask], y[right_mask]
                mse = (len(y_left) * np.var(y_left) + len(y_right) * np.var(y_right)) / n_samples

                if mse < best_mse:
                    best_mse = mse
                    split_idx = feature_index
                    split_thresh = t

        return split_idx, split_thresh

    def predict(self, X):
        logging.info("Predicting")
        return np.array([self._predict_sample(x, self.tree) for x in X])

    def _predict_sample(self, x, node):
        if node.value is not None:
            return node.value
        if x[node.feature_index] <= node.threshold:
            return self._predict_sample(x, node.left)
        else:
            return self._predict_sample(x, node.right)

    @staticmethod
    def mse_score(y_true , y_pred):
        n = len(y_true)
        return np.sum((y_true - y_pred)**2)/n

    @staticmethod
    def r2_score(y_true , y_pred):
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot)
