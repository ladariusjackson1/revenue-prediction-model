import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

print("🚀 Data engineering pipeline initialized successfully!")

# 1. Simulating our raw financial dataset for Double Eagle Financial LLC
raw_data = {
    'advertising_spend': [1200, 1500, np.nan, 2100, 1800, 2500, 1500, 2900],
    'active_customers': [45, 50, 48, 65, np.nan, 80, 50, 95],
    'region': ['North', 'South', 'North', 'West', 'South', 'West', 'North', 'South'],
    'quarterly_revenue': [15000, 18500, 16000, 24000, 21000, 29000, 18500, 34000]
}

df = pd.DataFrame(raw_data)
print("\n--- Raw Ingested Data Matrix ---")
print(df)

# 2. Imputing Missing Values (Filling NaN gaps with the column average)
df['advertising_spend'] = df['advertising_spend'].fillna(df['advertising_spend'].mean())
df['active_customers'] = df['active_customers'].fillna(df['active_customers'].mean())

# 3. Categorical One-Hot Encoding (Converting text regions to numbers)
df = pd.get_dummies(df, columns=['region'], drop_first=True)

# 4. Splitting Independent Features (X) from the Target Output (y)
X = df.drop(columns=['quarterly_revenue'])
y = df['quarterly_revenue']

# 5. Standardizing and Scaling Matrix Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 6. Building the 80/20 Train-Test Split Vault
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

print("\n--- Data Preprocessing Pipeline Metrics ---")
print(f"Total training input rows (X_train shape): {X_train.shape}")
print(f"Total testing evaluation rows (X_test shape): {X_test.shape}")
print("🏁 Pipeline complete. Data vaults are locked and ready for modeling!")