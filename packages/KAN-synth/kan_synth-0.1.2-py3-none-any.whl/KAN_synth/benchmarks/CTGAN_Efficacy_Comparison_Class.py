"""
CTGAN_Efficacy_Comparison_Class.py

Evaluate the Machine Learning Utility of CTGAN-based models on synthetic data for classification tasks.

This script loads real and synthetic datasets, computes similarity scores using statistical measures,
and evaluates predictive performance using a suite of regression models. It supports the analysis
of standard CTGAN, KAN-enhanced CTGANs, and hybrid variants on datasets.

Key Steps:
- Load and preprocess real and synthetic datasets
- Compute similarity scores between real and synthetic data
- Train regression models on synthetic data and test on real data
- Save evaluation metrics to CSV
- Visualize model-wise performance based on classification metrics

Requires:
- Synthetic datasets already generated and saved to disk (CTGAN_Data_Generation_test.py)
- Utility functions from `Utilities.py`
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import LinearSVC
from KAN_synth.utilities import overall_similarity, evaluate_all_models_classification, visualize_class_score

# Load and preprocess real dataset
#real_df = pd.read_csv("TestDatasets/adult.csv")
#real_df = pd.read_csv("TestDatasets/covtype.csv", nrows=100000) # NOT DONE YET
#real_df = pd.read_csv("TestDatasets/credit.csv")
real_df = pd.read_csv("TestDatasets/alarm.csv")

# Drop missing values 
real_df = real_df.dropna()

# Only for alarm dataset
real_df = real_df.drop(["DateTime", "ProcessID", "AssetID"], axis=1)
valid_classes = ["1 - High", "2 - Medium", "3 - Low"]
real_df = real_df[real_df["AlarmSeverityName"].isin(valid_classes)]

# Load synthetic datasets
synthetic_df_STANDARD_CTGAN = pd.read_csv("TestDatasets/AlarmSynthetic/synthetic_df_STANDARD_CTGAN.csv")
synthetic_df_KAN_CTGAN = pd.read_csv("TestDatasets/AlarmSynthetic/synthetic_df_KAN_CTGAN.csv")
synthetc_df_HYBRID_CTGAN = pd.read_csv("TestDatasets/AlarmSynthetic/synthetic_df_Hybrid_CTGAN.csv")
synthetic_df_Disc_KAN_CTGAN = pd.read_csv("TestDatasets/AlarmSynthetic/synthetic_df_Disc_KAN_CTGAN.csv")
synthetic_df_Gen_KAN_CTGAN = pd.read_csv("TestDatasets/AlarmSynthetic/synthetic_df_Gen_KAN_CTGAN.csv")

# ---- (Optional) Evaluate similarity between real and synthetic datasets with custom function ----
# Not used in the Thesis

# Split the real dataset in two random subsets (TO TEST THE FUNCTION)
real_data_part_1, real_data_part_2 = train_test_split(real_df, test_size=0.5, random_state=1618)

# NOT USED IN THE THESIS AS A BENCHMARK
sim_score_test = overall_similarity(real_data_part_1, real_data_part_2)
print(f"Similarity score: {sim_score_test}")

sim_score_STANDARD_CTGAN = overall_similarity(real_df, synthetic_df_STANDARD_CTGAN)
print("Similarity between real data and synthetic data with Standard CTGAN: ", sim_score_STANDARD_CTGAN)

sim_score_KAN_CTGAN = overall_similarity(real_df, synthetic_df_KAN_CTGAN)
print("Similarity between real data and synthetic data with KAN CTGAN: ", sim_score_KAN_CTGAN)

sim_score_HYBRID_CTGAN = overall_similarity(real_df, synthetc_df_HYBRID_CTGAN)
print("Similarity between real data and synthetic data with HYBRID KAN CTGAN: ", sim_score_HYBRID_CTGAN)

sim_score_Disc_KAN_CTGAN = overall_similarity(real_df, synthetic_df_Disc_KAN_CTGAN)
print("Similarity between real data and synthetic data with DISC KAN CTGAN: ", sim_score_Disc_KAN_CTGAN)

sim_score_Gen_KAN_CTGAN = overall_similarity(real_df, synthetic_df_Gen_KAN_CTGAN)
print("Similarity between real data and synthetic data with Gen KAN CTGAN: ", sim_score_Gen_KAN_CTGAN)

# Machine Learning Utility Evaluation (Classification)

# Define target column
target_column = "AlarmSeverityName"

# Prepare real dataset
X_real = real_df.drop([target_column], axis=1)
y_real = real_df[target_column]

# Prepare syntethic datsets
X_STANDARD_CTGAN = synthetic_df_STANDARD_CTGAN.drop([target_column], axis=1)
y_STANDARD_CTGAN = synthetic_df_STANDARD_CTGAN[target_column]

X_KAN_CTGAN = synthetic_df_KAN_CTGAN.drop([target_column], axis=1)
y_KAN_CTGAN = synthetic_df_KAN_CTGAN[target_column]

X_HYBRID_KAN_CTGAN = synthetc_df_HYBRID_CTGAN.drop([target_column], axis=1)
y_HYBRID_KAN_CTGAN = synthetc_df_HYBRID_CTGAN[target_column]

X_DISC_KAN_CTGAN = synthetic_df_Disc_KAN_CTGAN.drop([target_column], axis=1)
y_DISC_KAN_CTGAN = synthetic_df_Disc_KAN_CTGAN[target_column]

X_GEN_KAN_CTGAN = synthetic_df_Gen_KAN_CTGAN.drop([target_column], axis=1)
y_GEN_KAN_CTGAN = synthetic_df_Gen_KAN_CTGAN[target_column]

# Dictionary of synthetic datasets
synthetic_datasets = {
    "STANDARD CTGAN": (X_STANDARD_CTGAN, y_STANDARD_CTGAN),
    "KAN CTGAN": (X_KAN_CTGAN, y_KAN_CTGAN),
    "HYBRID KAN CTGAN": (X_HYBRID_KAN_CTGAN, y_HYBRID_KAN_CTGAN),
    "DISC KAN CTGAN": (X_DISC_KAN_CTGAN, y_DISC_KAN_CTGAN),
    "GEN KAN CTGAN": (X_GEN_KAN_CTGAN, y_GEN_KAN_CTGAN)
}

# Classification models
models = {
    "Logistic":    LogisticRegression(max_iter=1000, random_state=1618),
    "RF":          RandomForestClassifier(n_estimators=240, max_depth=40, max_features="sqrt", random_state=1618),
    "XGB":         XGBClassifier(colsample_bytree=0.8, learning_rate=0.1, max_depth=5, n_estimators=100, subsample=1.0, random_state=1618, use_label_encoder=False, eval_metric="logloss"),
    "LinearSVC":   LinearSVC(max_iter=10000, dual=False, random_state=1618),
}

# Create fake dictionary
real_data_dict = {
    "Real_Data": (X_real, y_real)
}

# Run evaluation
print("Start Evaluation", flush=True)
real_metrics_df, overall_syn_metrics_df = evaluate_all_models_classification(X_real, y_real, synthetic_datasets, models, test_size=0.2, random_state=1618, repeats=10)

real_metrics_df.to_csv("TestDatasets/AlarmSynthetic/SyntheticPerformance/real_metrics.csv", index=False)
overall_syn_metrics_df.to_csv("TestDatasets/AlarmSynthetic/SyntheticPerformance/overall_syn_metrics.csv", index=False)
print("Done")

# Visualize Classification Scores
real_metrics_df_class = pd.read_csv("TestDatasets/AlarmSynthetic/SyntheticPerformanceFromCluster/real_metrics.csv")
overall_syn_metrics_df_class = pd.read_csv("TestDatasets/AlarmSynthetic/SyntheticPerformanceFromCluster/overall_syn_metrics.csv")
 
model_names = ["Standard CTGAN", "KAN CTGAN", "Hybrid KAN CTGAN", "DISC KAN CTGAN", "GEN KAN CTGAN"]
visualize_class_score(real_metrics_df_class, overall_syn_metrics_df_class, model_names)




