"""
TVAE_Data_Generation_test.py

Generate synthetic tabular datasets using TVAE and KAN-based TVAE variants.

This script loads a selected dataset (from the UCI, Kaggle, or SDGym collections), performs basic preprocessing 
(e.g., removing irrelevant columns, handling datetime, encoding categories), and generates synthetic data using 
the following models:

    - TVAE (standard)
    - KAN-TVAE (all layers replaced)
    - Hybrid-KAN-TVAE (only first layer replaced)  
  
Each model is trained for 100 epochs and the synthetic outputs are saved to CSV for downstream benchmarking 
(e.g., Machine Learning Utility evaluation).

Output paths are hardcoded per dataset and saved in the corresponding `TestDatasets/<DatasetName>Synthetic/` folder.
"""

import numpy as np
import pandas as pd
import torch
from ctgan import TVAE
from KAN_synth.models.KAN_TVAE_code import KAN_TVAE
from KAN_synth.models.Hybrid_TVAE_code import HYBRID_KAN_TVAE

print(torch.cuda.is_available(), torch.version.cuda)

# Set device for CUDA or CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 

# Load the needed dataset
#df = pd.read_csv("TestDatasets/adult.csv")
#df = pd.read_csv("TestDatasets/energydata_complete.csv")
#df = pd.read_csv("TestDatasets/covtype.csv", nrows=100000)
#df = pd.read_csv("TestDatasets/credit.csv")
df = pd.read_csv("TestDatasets/alarm.csv")
#df = pd.read_csv("TestDatasets/news.csv")
#df = pd.read_csv("TestDatasets/benjing.csv")
#df = pd.read_csv("TestDatasets/bike.csv")

# Remove missing values
df = df.dropna()

# Only for news dataset
#df = df.drop(["url"], axis=1)

# SPECIFIC PREPROCESSING
# Only for bike dataset
#df = df.drop(["instant", "dteday"], axis=1)

# Only for Benjing dataset
#df = df.drop(["No"], axis=1)

# Only for energy dataset
#df = df.drop(["date"], axis=1)

# Only for alarm dataset
df = df.drop(["DateTime", "ProcessID", "AssetID"], axis=1)
valid_classes = ["1 - High", "2 - Medium", "3 - Low"]
df = df[df["AlarmSeverityName"].isin(valid_classes)]

# Number of rows in the dataframe
nrows = len(df)

# Strip any trailing spaces from column names
df.columns = df.columns.str.strip()

# Detect and convert datetime columns to Unix timestamps
datetime_columns = []
for col in df.columns:
    if df[col].dtype == object:
        converted = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        if converted.notna().mean() > 0.8:
            converted = converted.fillna(method="ffill")
            # Convert to Unix timestamp (seconds)
            df[col] = converted.astype(np.int64) // 10**9
            datetime_columns.append(col)
            print(f"Column '{col}' was parsed as datetime -> converted to Unix timestamp.")

# Convert all numeric columns to numeric dtype explicitly
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Identify discrete (categorical) columns
discrete_columns = list(df.select_dtypes(include=["object", "category", "bool"]).columns)
discrete_columns = list(set(discrete_columns) - set(datetime_columns))

# Check and drop any columns with mixed types
for col in df.columns:
    sample_types = set(df[col].dropna().map(type))
    if len(sample_types) > 1:
        print(f"Warning: Column '{col}' has mixed types {sample_types}. Removing it.")
        df.drop(columns=[col], inplace=True)

# Final cleanup of discrete columns
discrete_columns = [c for c in discrete_columns if c in df.columns]

print("Start modeling")

# HYBRID_KAN_TVAE
model = HYBRID_KAN_TVAE(epochs=100, 
                  verbose=True, 
                  grid_size_enc=5, 
                  spline_order_enc=3,
                  grid_size_dec=5,
                  spline_order_dec=3)
model.fit(df, discrete_columns=discrete_columns)
print("Hybrid Model trained successfully")

# Sample
synthetic_df_Hybrid_KAN_TVAE = model.sample(nrows)
synthetic_df_Hybrid_KAN_TVAE.to_csv("TestDatasets/AlarmSynthetic/synthetic_df_Hybrid_KAN_TVAE.csv", index=False)

# KAN_TVAE
model = KAN_TVAE(epochs=100, 
                  verbose=True, 
                  grid_size_enc=5, 
                  spline_order_enc=3,
                  grid_size_dec=5, 
                  spline_order_dec=3)
model.fit(df, discrete_columns=discrete_columns)
print("Model trained successfully")

# Sample 
synthetic_df_KAN_TVAE = model.sample(nrows)
synthetic_df_KAN_TVAE.to_csv("TestDatasets/AlarmSynthetic/synthetic_df_KAN_TVAE.csv", index=False)

# Standard CTGAN
model = TVAE(epochs=100, verbose=True)
model.fit(df, discrete_columns=discrete_columns)
print("Model trained successfully")

# Sample
synthetic_df_STANDARD_TVAE = model.sample(nrows)
synthetic_df_STANDARD_TVAE.to_csv("TestDatasets/AlarmSynthetic/synthetic_df_STANDARD_TVAE.csv", index=False)
