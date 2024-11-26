import pandas as pd
import numpy as np
from ctgan import CTGAN

# Step 1: Create a sample dataset to train the model
np.random.seed(42)

# Generate random transaction data
train_data = pd.DataFrame({
    'transaction_id': np.arange(1000),
    'amount': np.random.lognormal(mean=3, sigma=1, size=1000),
    'transaction_time': np.random.randint(0, 24*60*60, size=1000),  # Seconds in a day
    'location_id': np.random.randint(1, 1000, size=1000),
    'merchant_id': np.random.randint(1, 500, size=1000),
    'device_id': np.random.randint(1, 10000, size=1000),
    'customer_age': np.random.randint(18, 90, size=1000),
    'customer_gender': np.random.choice(['M', 'F'], size=1000),
    'transaction_category': np.random.choice(
        ['Grocery', 'Electronics', 'Clothing', 'Restaurant', 'Fuel'],
        size=1000
    ),
    'num_prev_transactions': np.random.randint(0, 1000, size=1000),
    'credit_score': np.random.randint(300, 850, size=1000),
    'fraud': np.random.choice([0, 1], size=1000, p=[0.95, 0.05])  # 5% fraud rate
})

# Step 2: Define discrete columns for the CTGAN model
# (CTGAN in the latest versions uses this approach)
discrete_columns = [
    'location_id',
    'merchant_id',
    'device_id',
    'customer_gender',
    'transaction_category',
    'fraud'
]

# Step 3: Initialize and train the CTGAN model
model = CTGAN(epochs=100)
model.fit(train_data, discrete_columns=discrete_columns)

# Step 4: Generate synthetic transaction data
synthetic_data = model.sample(10000)

# Step 5: Save the synthetic data to a CSV file
synthetic_data.to_csv('synthetic_transactions.csv', index=False)

# Optional: Display a message when done
print("Synthetic dataset generated and saved to 'synthetic_transactions.csv'.")
