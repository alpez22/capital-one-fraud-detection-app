import pandas as pd
import numpy as np
from sdv.tabular import CTGAN

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

# Step 2: Define the data types for the CTGAN model
field_types = {
    'transaction_id': 'id',
    'amount': 'float',
    'transaction_time': 'integer',
    'location_id': 'categorical',
    'merchant_id': 'categorical',
    'device_id': 'categorical',
    'customer_age': 'integer',
    'customer_gender': 'categorical',
    'transaction_category': 'categorical',
    'num_prev_transactions': 'integer',
    'credit_score': 'integer',
    'fraud': 'categorical'
}

# Step 3: Initialize and train the CTGAN model
model = CTGAN(field_types=field_types, epochs=100)
model.fit(train_data)

# Step 4: Generate synthetic transaction data
synthetic_data = model.sample(10000)

# Step 5: Save the synthetic data to a CSV file
synthetic_data.to_csv('synthetic_transactions.csv', index=False)

# Optional: Display a message when done
print("Synthetic dataset generated and saved to 'synthetic_transactions.csv'.")
