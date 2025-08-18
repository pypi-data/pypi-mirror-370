from stockpredictor.stock_predictor import stockpredictor

# Create object for NIFTY 50
sp = stockpredictor(ticker="^NSEI", start="2023-01-01", end="2024-01-01")

# 1. Load data
sp.load_data()

# 2. Prepare features
sp.prepare_features()

# 3. Train model
# You can choose linear or logistic regression
sp.train_logistic()   # Logistic regression
# OR
# sp.train_linear()

# 4. Make predictions
predictions = sp.predict()
print(predictions[:10])  # show first 10 predictions

# 5. Evaluate performance
sp.evaluate()

# 6. Plot stock prices with moving averages
sp.plot()
