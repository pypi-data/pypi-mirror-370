# stock_predictor.py
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

class StockPredictor:
    def __init__(self, ticker="^NSEI", start="2020-01-01", end="2024-01-01"):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.data = None
        self.model = None

    def load_data(self):
        """Download index data from Yahoo Finance"""
        self.data = yf.download(self.ticker, start=self.start, end=self.end)
        self.data.dropna(inplace=True)
        print(f"Data loaded: {self.data.shape[0]} rows")
        return self.data

    def prepare_features(self):
        """Create features & target for prediction"""
        self.data["MA5"] = self.data["Close"].rolling(window=5).mean()
        self.data["MA20"] = self.data["Close"].rolling(window=20).mean()
        self.data.dropna(inplace=True)

        # Features
        self.X = self.data[["Open", "High", "Low", "Close", "Volume", "MA5", "MA20"]]
        # Target: 1 if price goes up tomorrow, else 0
        self.data["Target"] = (self.data["Close"].shift(-1) > self.data["Close"]).astype(int)
        self.y = self.data["Target"]

    def train_linear(self):
        reg = LinearRegression()
        reg.fit(self.X, self.y)
        self.model = reg
        print("Linear regression trained")
        return reg.coef_, reg.intercept_

    def train_logistic(self):
        log_reg = LogisticRegression()
        log_reg.fit(self.X, self.y)
        self.model = log_reg
        print("Logistic regression trained")
        return log_reg.score(self.X, self.y)

    def predict(self):
        if self.model is None:
            raise ValueError("Model not trained")
        preds = self.model.predict(self.X)
        return preds

    def evaluate(self):
        preds = self.predict()
        acc = accuracy_score(self.y, preds)
        print(f"Accuracy: {acc:.2%}")
        print(confusion_matrix(self.y, preds))
        print(classification_report(self.y, preds))

    def plot(self):
        plt.figure(figsize=(12,6))
        plt.plot(self.data["Close"], label="Close Price")
        plt.plot(self.data["MA5"], label="MA5")
        plt.plot(self.data["MA20"], label="MA20")
        plt.legend()
        plt.title(f"{self.ticker} Price & Moving Averages")
        plt.show()
