"""
TVAE_Efficacy_Comparison_Reg.py

Evaluate the Machine Learning Utility of TVAE-based models on synthetic data for regression tasks.

This script loads real and synthetic datasets, computes similarity scores using statistical measures,
and evaluates predictive performance using a suite of regression models. It supports the analysis
of standard TVAE, KAN-enhanced TVAEs, and hybrid variants on datasets.

Key Steps:
- Load and preprocess real and synthetic datasets
- Compute similarity scores between real and synthetic data
- Train regression models on synthetic data and test on real data
- Save evaluation metrics to CSV
- Visualize model-wise performance based on regression metrics

Requires:
- Synthetic datasets already generated and saved to disk (TVAE_Data_Generation_test.py)
- Utility functions from `Utilities.py`
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from KAN_synth.utilities import overall_similarity, evaluate_all_models, visualize_reg_score

# Load and preprocess real dataset
#real_df = pd.read_csv("TestDatasets/energydata_complete.csv")
#real_df = pd.read_csv("TestDatasets/news.csv", skipinitialspace=True)
#real_df = pd.read_csv("TestDatasets/benjing.csv") # target: pm2.5
real_df = pd.read_csv("TestDatasets/bike.csv") # target: cnt

# Drop missing values 
real_df = real_df.dropna()

# Only for news dataset
#real_df = real_df.drop(["url"], axis=1)

# Only for bike dataset
real_df = real_df.drop(["instant", "dteday"], axis=1)

# Only for Benjing dataset
#real_df = real_df.drop(["No"], axis=1)

# Only for energy
#real_df = real_df.drop(["date"], axis=1)

# Load synthetic datasets
synthetic_df_STANDARD_TVAE = pd.read_csv("TestDatasets/BikeSynthetic/synthetic_df_STANDARD_TVAE.csv")
synthetic_df_KAN_TVAE = pd.read_csv("TestDatasets/BikeSynthetic/synthetic_df_KAN_TVAE.csv")
synthetic_df_hybrid_KAN_TVAE = pd.read_csv("TestDatasets/BikeSynthetic/synthetic_df_Hybrid_KAN_TVAE.csv")

# ---- (Optional) Evaluate similarity between real and synthetic datasets with custom function ----
# Not used in the Thesis

# Split the real dataset in two random subsets (TO TEST THE FUNCTION)
real_data_part_1, real_data_part_2 = train_test_split(real_df, test_size=0.5, random_state=1618)

# Evaluate the two parts on the statistical function (NOT USED AS A BENCHMARK IN THE THESIS)
sim_score_test = overall_similarity(real_data_part_1, real_data_part_2)
print(f"Similarity score: {sim_score_test}")

sim_score_STANDARD_TVAE = overall_similarity(real_df, synthetic_df_STANDARD_TVAE)
print("Similarity between real data and synthetic data with Standard TVAE: ", sim_score_STANDARD_TVAE)

sim_score_KAN_TVAE = overall_similarity(real_df, synthetic_df_KAN_TVAE)
print("Similarity between real data and synthetic data with KAN TVAE: ", sim_score_KAN_TVAE)

sim_score_Hybrid_KAN_TVAE = overall_similarity(real_df, synthetic_df_hybrid_KAN_TVAE)
print("Similarity between real data and synthetic data with Hybrid KAN TVAE: ", sim_score_Hybrid_KAN_TVAE)

# Machine Learning Utility Evaluation (Regression)

# Define target column
target_column = "cnt"

# Prepare real dataset
X_real = real_df.drop([target_column], axis=1)
y_real = real_df[target_column]

# Prepare syntethic datsets
X_STANDARD_TVAE = synthetic_df_STANDARD_TVAE.drop([target_column], axis=1)
y_STANDARD_TVAE = synthetic_df_STANDARD_TVAE[target_column]

X_KAN_TVAE = synthetic_df_KAN_TVAE.drop([target_column], axis=1)
y_KAN_TVAE = synthetic_df_KAN_TVAE[target_column]

X_Hybrid_KAN_TVAE = synthetic_df_hybrid_KAN_TVAE.drop([target_column], axis=1)
y_Hybrid_KAN_TVAE = synthetic_df_hybrid_KAN_TVAE[target_column]

# Dictionary of synthetic datasets
synthetic_datasets = {
    "STANDARD TVAE": (X_STANDARD_TVAE, y_STANDARD_TVAE),
    "KAN TVAE": (X_KAN_TVAE, y_KAN_TVAE),
    "Hybrid KAN TVAE": (X_Hybrid_KAN_TVAE, y_Hybrid_KAN_TVAE)
}

# Regressor models
models = {
    "XGB": XGBRegressor(colsample_bytree = 0.8, 
                     gamma = 0, learning_rate = 0.1, 
                     max_depth = 5, 
                     n_estimators = 100, 
                     subsample = 1.0, 
                     random_state=1618),
    "RF": RandomForestRegressor(max_depth=40, max_features="sqrt", n_estimators=240),
    "SVR": SVR(C=8, gamma=1, kernel="rbf"),
    "Linear": LinearRegression()
}

# Create fake dictionary
real_data_dict = {
    "Real_Data": (X_real, y_real)
}

# Run evaluation
print("Start Evaluaing")
real_metrics_df, overall_syn_metrics_df_TVAE, detailed_syn_metrics_TVAE = evaluate_all_models(X_real, y_real, synthetic_datasets, models, test_size=0.2, random_state=1618, repeats=10)

# Save evaluation outputs
real_metrics_df.to_csv("TestDatasets/BikeSynthetic/SyntheticPerformance/real_metrics_TVAE.csv", index=False)
overall_syn_metrics_df_TVAE.to_csv("TestDatasets/BikeSynthetic/SyntheticPerformance/overall_syn_metrics_TVAE.csv", index=False)
print("Done")

# Visualize Regression Scores
real_metrics_df = pd.read_csv("TestDatasets/BikeSynthetic/SyntheticPerformanceFromCluster/real_metrics_TVAE.csv")
overall_syn_metrics_df_TVAE = pd.read_csv("TestDatasets/BikeSynthetic/SyntheticPerformanceFromCluster/overall_syn_metrics_TVAE.csv")

model_names = ["Standard TVAE", "KAN TVAE", "Hybrid KAN TVAE"]
visualize_reg_score(real_metrics_df, overall_syn_metrics_df_TVAE, model_names)


