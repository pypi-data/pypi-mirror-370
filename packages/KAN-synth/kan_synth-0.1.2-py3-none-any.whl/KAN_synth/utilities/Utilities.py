"""
Utilities.py

Utilities for Evaluating Synthetic Tabular Data Quality and Model Transferability.

This module provides a set of utility functions for quantitatively evaluating synthetic tabular datasets.
It includes tools for statistical comparison with real data, assessing machine learning model transferability,
and visualizing performance metrics for both regression and classification tasks.

Main functionalities:
    - `overall_similarity`: Computes a composite similarity score between real and synthetic datasets 
      using statistical moments (mean, median, variance, etc.) and distributional metrics (KS-test, Wasserstein distance).
    - `evaluate_all_models`: Evaluates regression performance by training models on synthetic data 
      and testing on real data, using repeated holdout for statistical robustness.
    - `evaluate_all_models_classification`: Analogous evaluation procedure for classification tasks, 
      supporting categorical preprocessing and weighted scoring metrics (Accuracy, Precision, Recall, F1).
    - `visualize_reg_score`: Visual comparison of regression metrics between real and synthetic generators, 
      with normalized scoring and ranking.
    - `visualize_class_score`: Similar visualization for classification metrics and overall fidelity of each generator.

Note:
    - These functions assume input data as Pandas DataFrames and models as scikit-learn compatible estimators.
    - Designed to support benchmarking pipelines for synthetic data generation projects.

Dependencies:
    - pandas, numpy, matplotlib, scipy, scikit-learn
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp, wasserstein_distance
from sklearn.base import clone
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler

# Import comparisons functions
def overall_similarity(real_df, synthetic_df, 
                       weight_mean=0.3, weight_median=0.2, weight_mode=0.1, weight_sd=0.1, weight_var=0.1,
                       weight_ks=0.2, weight_wasserstein=0.1):
    """
    Computes an overall similarity score between real and synthetic datasets based
    on normalized differences in mean, median (if numerical) and mode (if categorical) across columns.

    Parameters:
    - real_df (pd.DataFrame): Real dataset
    - synthetic_df (pd.DataFrame): Synthetic dataset
    - weight_mean (float, optional): Weight for mean difference. Defaults to 0.3.
    - weight_median (float, optional): Weight for median difference. Defaults to 0.3.
    - weight_mode (float, optional): Weight for mode difference. Defaults to 0.2.
    - weight_sd (float, optional): Weight for standard deviation difference. Defaults to 0.1
    - weight_var (float, optional): Weight for variance difference. Defaults to 0.1

    Returns:
    Returns a score between 0 and 100, where 100 indicates perfect similarity.
    """

    # Drop datetime columns
    real_df = real_df.select_dtypes(exclude=["datetime64"])
    synthetic_df = synthetic_df.select_dtypes(exclude=["datetime64"])

    scores = []
    common_cols = set(real_df.columns).intersection(set(synthetic_df.columns))

    for col in common_cols:
        # Check if numerical
        if pd.api.types.is_numeric_dtype(real_df[col]):
            # Classic statistics
            real_mean, syn_mean = real_df[col].mean(), synthetic_df[col].mean() 
            real_median, syn_median = real_df[col].median(), synthetic_df[col].median()
            real_sd, syn_sd = real_df[col].std(), synthetic_df[col].std()
            real_var, syn_var = real_df[col].var(), synthetic_df[col].var()
            
            # Avoid division by zero
            norm_mean = min(1, abs(real_mean - syn_mean) / (abs(real_mean) + 1e-6))
            norm_median = min(1, abs(real_median - syn_median) / (abs(real_median) + 1e-6))
            norm_sd = min(1, abs(real_sd - syn_sd) / (abs(real_sd) + 1e-6))
            norm_var = min(1, abs(real_var - syn_var) / (abs(real_var) + 1e-6))
      
            # Kolomogorov-Smirnov Test (Checks if distributions are similar)
            ks_stat, _ = ks_2samp(real_df[col].dropna(), synthetic_df[col].dropna())
        
            # Wasserstein Distance (Lower means closer distributions)
            wasserstein_dist = wasserstein_distance(real_df[col].dropna(), synthetic_df[col])
            norm_wasserstein = 1 / (1 + wasserstein_dist) # now between 0 and 1

            col_score = 1 - (weight_mean * norm_mean + 
                             weight_median * norm_median + 
                             weight_sd * norm_sd + 
                             weight_var * norm_var +
                             weight_ks * ks_stat + 
                             weight_wasserstein * (1 - norm_wasserstein))
        
        else:
            real_mode = real_df[col].mode()
            syn_mode = synthetic_df[col].mode()
            if not real_mode.empty and not syn_mode.empty:
                mode_score = 1.0 if real_mode.iloc[0] == syn_mode.iloc[0] else 0.0
            else:
                mode_score = 0.0
            col_score = mode_score* weight_mode
        
        scores.append(col_score)
    
    overall_score = np.mean(scores) * 100
    return round(overall_score, 2)

# Machine Learning efficacy comparison
def evaluate_all_models(X_real, y_real, synthetic_datasets, models, test_size=0.2, random_state=1618, repeats=10):
    """
    Evaluate all models on all synthetic datasets using repeated holdout for robust results.

    Parameters:
    - X_real (pd.DataFrame): Features from the real dataset
    - y_real (pd.Series): Target variable from the real dataset
    - synthetic_datasets (dict): Dictionary of synthetic datasets
    - models (dict): Dictionary of models to evaluate
    - test_size (float, optional): Proportion of data to use for testing. Defaults to 0.2.
    - random_state (int, optional): Seed for random number generation. Defaults to 1618
    - repeats (int, optional): Number of random splits of the data for statistical significant results. Defaults to 1

    Returns:
    - real_metrics_df (pd.DataFrame): Evaluation metrics for each model on real data
    - overall_syn_metrics_df (pd.DataFrame): Average Evaluation metrics
    - detailed_syn_metrics (dict): Nested dictionary of metrics for each synthetic data generator 
    """

    # Scale the data
    scaler = StandardScaler()
    X_real_scaled = scaler.fit_transform(X_real)

    # Dictionaries to hold repeated metrics
    real_metrics_accum = {model_name: [] for model_name in models}
    detailed_syn_metrics_accum = {method: {model_name: [] for model_name in models} for method in synthetic_datasets}

    # Repeated holdouts
    for i in range(repeats):
        current_seed = random_state + i # change random state everytime to evaluate different part of the dataframe

        # Split real data
        X_train_real, X_test_real, y_train_real, y_test_real = train_test_split(
            X_real_scaled, y_real, test_size=test_size, random_state=current_seed
        )

        # Evaluate all models on real data
        for model_name, model in models.items():
            model_clone = clone(model)
            model_clone.fit(X_train_real, y_train_real)
            y_pred_real = model_clone.predict(X_test_real)

            real_metrics_accum[model_name].append({
                "MAE": mean_absolute_error(y_test_real, y_pred_real),
                "MSE": mean_squared_error(y_test_real, y_pred_real),
                "R2": r2_score(y_test_real, y_pred_real)
            })
        
        # Evaluate synthetic data 
        for method, (X_syn, y_syn) in synthetic_datasets.items():
            X_syn_scaled = scaler.transform(X_syn)

            # Split the syn data (To ensure same proportions)
            X_train_syn, _ , y_train_syn, _ = train_test_split(
                X_syn_scaled, y_syn, test_size=test_size, random_state=current_seed
            )

            for model_name, model in models.items():
                model_clone = clone(model)
                model_clone.fit(X_train_syn, y_train_syn)
                y_pred_syn = model_clone.predict(X_test_real) # Test on REAL data
                
                # Test everything on REAL data
                detailed_syn_metrics_accum[method][model_name].append({
                    "MAE": mean_absolute_error(y_test_real, y_pred_syn),
                    "MSE": mean_squared_error(y_test_real, y_pred_syn),
                    "R2": r2_score(y_test_real, y_pred_syn)
                })
    
    # Avarege all the results
    real_metrics = {
        model_name: {
            metric: np.mean([res[metric] for res in results])
            for metric in ["MAE", "MSE", "R2"]
        }
        for model_name, results in real_metrics_accum.items()
    }

    real_metrics_df = pd.DataFrame(real_metrics).T

    # Same for synthetic data
    detailed_syn_metrics = {
        method: {
            model_name: {
                metric: np.mean([res[metric] for res in results])
                for metric in ["MAE", "MSE", "R2"]
            }
            for model_name, results in model_dict.items()
        }
        for method, model_dict in detailed_syn_metrics_accum.items()
    }

    # Compute overall avareges for synthetic data
    overall_syn_metrics = {
        method: {
            "MAE_avg": np.mean([metrics["MAE"] for metrics in model_dict.values()]),
            "MSE_avg": np.mean([metrics["MSE"] for metrics in model_dict.values()]),
            "R2_avg": np.mean([metrics["R2"] for metrics in model_dict.values()]),
        }
        for method, model_dict in detailed_syn_metrics.items()
    }

    overall_syn_metrics_df = pd.DataFrame(overall_syn_metrics).T # Transpose to have metrics as columns

    return real_metrics_df, overall_syn_metrics_df, detailed_syn_metrics

def evaluate_all_models_classification(X_real, y_real, synthetic_datasets, models, test_size=0.2, random_state=1618, repeats=10):
    """
    Evaluate all models on all synthetic datasets using repeated holdout for robust results (Classification tasks only).

    Parameters:
    - X_real (pd.DataFrame): Features from the real dataset
    - y_real (pd.Series): Target variable from the real dataset
    - synthetic_datasets (dict): Dictionary of synthetic datasets
    - models (dict): Dictionary of models to evaluate
    - test_size (float, optional): Proportion of data to use for testing. Defaults to 0.2.
    - random_state (int, optional): Seed for random number generation. Defaults to 1618
    - repeats (int, optional): Number of random splits of the data for statistical significant results. Defaults to 1

    Returns:
    - real_metrics_df (pd.DataFrame): Evaluation metrics for each model on real data
    - overall_syn_metrics_df (pd.DataFrame): Average Evaluation metrics.
    """
     
    # Scale the features (only numeric columns)
    scaler = StandardScaler()
    numeric_cols = X_real.select_dtypes(include=["number"]).columns
    X_real[numeric_cols] = scaler.fit_transform(X_real[numeric_cols])

    non_numeric = X_real.select_dtypes(exclude=["number"]).columns.tolist()
    ohe = OneHotEncoder(sparse=False, handle_unknown="ignore")
    cat = ohe.fit_transform(X_real[non_numeric])
    cat_df = pd.DataFrame(cat, columns=ohe.get_feature_names_out(non_numeric), index=X_real.index)

    X_real = pd.concat([X_real[numeric_cols], cat_df], axis=1)
    
    # Metrics and dict to accumulate results
    metrics_names = ["Accuracy", "Precision", "Recall", "F1"]
    real_accum = {m:[] for m in metrics_names}
    syn_accum = {
         method:{m:[] for m in metrics_names}
         for method in synthetic_datasets
    }

    # Repeated holdouts
    for i in range(repeats):
        seed = random_state + i
        X_train_real, X_test_real, y_train_real, y_test_real = train_test_split(
             X_real, y_real, test_size=test_size, random_state=seed
        )

        # Evaluate on real
        for name, model in models.items():
            m = clone(model)
            m.fit(X_train_real, y_train_real)
            y_pred = m.predict(X_test_real)
             
            real_accum["Accuracy"].append(accuracy_score(y_test_real, y_pred))
            real_accum["Precision"].append(precision_score(y_test_real, y_pred, average="weighted"))
            real_accum["Recall"].append(recall_score(y_test_real, y_pred, average="weighted"))
            real_accum["F1"].append(f1_score(y_test_real, y_pred, average="weighted"))

        # Evaluate each synthetic data df
        for method, (X_syn, y_syn) in synthetic_datasets.items():
            numeric_cols_s = X_syn.select_dtypes(include=["number"]).columns
            X_syn[numeric_cols_s] = scaler.fit_transform(X_syn[numeric_cols_s])
            non_numeric = X_syn.select_dtypes(exclude=["number"]).columns.tolist()
            ohe_s = OneHotEncoder(sparse=False, handle_unknown="ignore")
            cat_s = ohe.fit_transform(X_syn[non_numeric])
            cat_df_s = pd.DataFrame(cat_s, columns=ohe_s.get_feature_names_out(non_numeric), index=X_real.index)

            X_syn = pd.concat([X_syn[numeric_cols], cat_df_s], axis=1)
            Xs_train, _, ys_train, _ = train_test_split(
                X_syn, y_syn, test_size=test_size, random_state=seed
            )

            for name, model in models.items():
                m = clone(model)
                m.fit(Xs_train, ys_train)
                y_pred = m.predict(X_test_real) # Test on REAL

                syn_accum[method]["Accuracy"].append(accuracy_score(y_test_real, y_pred))
                syn_accum[method]["Precision"].append(precision_score(y_test_real, y_pred, average="weighted"))
                syn_accum[method]['Recall'].append(recall_score(y_test_real, y_pred, average='weighted'))
                syn_accum[method]['F1'].append(f1_score(y_test_real, y_pred, average='weighted')) 
    
    # Aggregate into DataFrames
    real_metrics = {
         m: np.mean(scores) for m, scores in real_accum.items()
    }
    real_metrics_df = pd.DataFrame([real_metrics])

    overall_syn = {}
    for method, metrics in syn_accum.items():
        overall_syn[method] = {m: np.mean(scores) for m, scores in metrics.items()}
    overall_syn_metrics_df = pd.DataFrame.from_dict(overall_syn, orient="index")

    return real_metrics_df, overall_syn_metrics_df

def visualize_reg_score(real_metrics_df, overall_syn_metrics_df, model_names):
    """
    Visualize regression performance of synthetic data generators using MAE and RMSE as reference.

    This function compares regression metrics between real and synthetic datasets, computes 
    delta values for MAE and RMSE, transforms them into normalized scores, and produces an 
    overall performance score for each model. Results are visualized in a bar chart.

    Parameters:
    - real_metrics_df (pd.DataFrame): Regression metrics from the real dataset (containing "MAE", "MSE" columns).
    - overall_syn_metrics_df (pd.DataFrame): Regression metrics averaged over synthetic datasets (must include "MAE_avg", "MSE_avg").
    - model_names (list of str): List of model names to assign as index for plotting.

    Returns:
    - None: Displays a bar plot with the overall score for each synthetic data generator.
    """

    # Create diff metrics to store the differences in performance from the original data
    # Compute the differences
    diff_metrics = overall_syn_metrics_df.copy()

    # Calculate RMSE 
    overall_syn_metrics_df["RMSE_avg"] = np.sqrt(overall_syn_metrics_df["MSE_avg"])
    real_rmse = np.sqrt(real_metrics_df.mean()["MSE"])

    # Compute the difference is RMSE
    diff_metrics["Delta_RMSE"] = abs(real_rmse - overall_syn_metrics_df["RMSE_avg"])

    # Absolute difference
    for metric in ["MAE"]:
        diff_metrics[f"Delta_{metric}"] = abs(real_metrics_df.mean()[metric] - overall_syn_metrics_df[f"{metric}_avg"])

    # Normalize the scores
    real_mae = real_metrics_df.mean()["MAE"]

    diff_metrics["MAE_Score"] = 1 - (diff_metrics["Delta_MAE"] / real_mae)
    diff_metrics["RMSE_Score"] = 1 - (diff_metrics["Delta_RMSE"] / real_rmse)

    diff_metrics.index = model_names

    print(diff_metrics)

    # Creating a overall score (since now MAE_Score, RMSE_Score and R2_Score are in the same range (-inf, 1])
    diff_metrics["Overall_Score"] = (diff_metrics[["MAE_Score", "RMSE_Score"]].mean(axis=1)) 
    diff_metrics = diff_metrics.sort_values(by="Overall_Score", ascending=False)
    print(diff_metrics[["MAE_Score", "RMSE_Score"]])
    print(diff_metrics["Overall_Score"])

    # Visualize the rank
    fig, ax = plt.subplots(1,1,figsize=(12,6))
    bars = ax.bar(diff_metrics.index, diff_metrics["Overall_Score"], color="green", edgecolor="black")

    for bar in bars:
        height = bar.get_height()
        if height >= 0:
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    height + 0.02,
                    f"{height:.2f}",
                    ha="center", va="bottom",
                    fontsize=10, fontweight="bold")
        else:
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    height - 0.02,
                    f"{height:.2f}",
                    ha="center", va="top",
                    fontsize=10, fontweight="bold")

    ax.set_title("Overall Performance of Synthetic Data Generators")
    ax.set_ylabel("Overall Score (Better if closer to 1)")
    ax.set_xlabel("Synthetic Data Generator")
    ax.set_xticklabels(diff_metrics.index, rotation=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

def visualize_class_score(real_metrics_df_class, overall_syn_metrics_df_class, model_names):
    """
    Visualize classification performance of synthetic data generators using Accuracy, Precision, Recall, and F1.

    This function compares classification metrics between real and synthetic datasets, computes 
    delta values, derives normalized per-metric scores, and calculates an overall score 
    reflecting similarity to real-data performance. Outputs are visualized in a bar chart.

    Parameters:
    - real_metrics_df_class (pd.DataFrame): Classification metrics from the real dataset (single-row DataFrame).
    - overall_syn_metrics_df_class (pd.DataFrame): Average classification metrics over synthetic datasets.
    - model_names (list of str): List of model names to use as index for visualization.

    Returns:
    - None: Displays a bar plot with the overall classification score for each synthetic model.
    """

    # Create diff metrics to store the differences in performance from the original data
    # Compute the differences
    diff = overall_syn_metrics_df_class.copy()
    for metric in diff.columns:
        diff[f"Delta_{metric}"] = abs(real_metrics_df_class.at[0, metric] - diff[metric])

    # Compute per-metric score = 1 - (delta/real)
    for metric in diff.columns:
        if metric.startswith("Delta_"):
            base = real_metrics_df_class.at[0, metric.replace("Delta_", "")]
            diff[f"{metric.replace('Delta_', '')} Score"] = 1 - (diff[metric] / base)

    # Overall score
    score_cols = [c for c in diff.columns if c.endswith("Score")]
    diff["Overall_Score"] = diff[score_cols].mean(axis=1)
    print(diff["Overall_Score"])

    diff.index = model_names

    # Visualize the rank
    fig, ax = plt.subplots(1,1,figsize=(12,6))
    bars = ax.bar(diff.index, diff["Overall_Score"], color="green", edgecolor="black")

    for bar in bars:
        height = bar.get_height()
        if height >= 0:
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    height + 0.02,
                    f"{height:.2f}",
                    ha="center", va="bottom",
                    fontsize=10, fontweight="bold")
        else:
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    height - 0.02,
                    f"{height:.2f}",
                    ha="center", va="top",
                    fontsize=10, fontweight="bold")

    ax.set_title("Overall Performance of Synthetic Data Generators")
    ax.set_ylabel("Overall Score (Better if closer to 1)")
    ax.set_xlabel("Synthetic Data Generator")
    ax.set_xticklabels(diff.index, rotation=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()


