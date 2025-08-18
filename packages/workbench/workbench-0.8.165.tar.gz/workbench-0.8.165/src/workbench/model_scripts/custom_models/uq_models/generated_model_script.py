# Model: NGBoost Regressor with Distribution output
from ngboost import NGBRegressor
from xgboost import XGBRegressor  # Base Estimator
from sklearn.model_selection import train_test_split
import numpy as np

# Model Performance Scores
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    root_mean_squared_error
)

from io import StringIO
import json
import argparse
import joblib
import os
import pandas as pd

# Local Imports
from proximity import Proximity



# Template Placeholders
TEMPLATE_PARAMS = {
    "id_column": "id",
    "features": ['molwt', 'mollogp', 'molmr', 'heavyatomcount', 'numhacceptors', 'numhdonors', 'numheteroatoms', 'numrotatablebonds', 'numvalenceelectrons', 'numaromaticrings', 'numsaturatedrings', 'numaliphaticrings', 'ringcount', 'tpsa', 'labuteasa', 'balabanj', 'bertzct'],
    "target": "solubility",
    "train_all_data": True,
    "track_columns": ['solubility']
}


# Function to check if dataframe is empty
def check_dataframe(df: pd.DataFrame, df_name: str) -> None:
    """
    Check if the provided dataframe is empty and raise an exception if it is.

    Args:
        df (pd.DataFrame): DataFrame to check
        df_name (str): Name of the DataFrame
    """
    if df.empty:
        msg = f"*** The training data {df_name} has 0 rows! ***STOPPING***"
        print(msg)
        raise ValueError(msg)


def match_features_case_insensitive(df: pd.DataFrame, model_features: list) -> pd.DataFrame:
    """
    Matches and renames DataFrame columns to match model feature names (case-insensitive).
    Prioritizes exact matches, then case-insensitive matches.

    Raises ValueError if any model features cannot be matched.
    """
    df_columns_lower = {col.lower(): col for col in df.columns}
    rename_dict = {}
    missing = []
    for feature in model_features:
        if feature in df.columns:
            continue  # Exact match
        elif feature.lower() in df_columns_lower:
            rename_dict[df_columns_lower[feature.lower()]] = feature
        else:
            missing.append(feature)

    if missing:
        raise ValueError(f"Features not found: {missing}")

    # Rename the DataFrame columns to match the model features
    return df.rename(columns=rename_dict)


def distance_weighted_calibrated_intervals(
        df_pred: pd.DataFrame,
        prox_df: pd.DataFrame,
        calibration_strength: float = 0.7,
        distance_decay: float = 3.0,
) -> pd.DataFrame:
    """
    Calibrate intervals using distance-weighted neighbor quantiles.
    Uses all 10 neighbors with distance-based weighting.
    """
    id_column = TEMPLATE_PARAMS["id_column"]
    target_column = TEMPLATE_PARAMS["target"]

    # Distance-weighted neighbor statistics
    def weighted_quantile(values, weights, q):
        """Calculate weighted quantile"""
        if len(values) == 0:
            return np.nan
        sorted_indices = np.argsort(values)
        sorted_values = values[sorted_indices]
        sorted_weights = weights[sorted_indices]
        cumsum = np.cumsum(sorted_weights)
        cutoff = q * cumsum[-1]
        return np.interp(cutoff, cumsum, sorted_values)

    # Calculate distance weights (closer neighbors get more weight)
    prox_df = prox_df.copy()
    prox_df['weight'] = 1 / (1 + prox_df['distance'] ** distance_decay)

    # Get weighted quantiles and statistics for each ID
    neighbor_stats = []
    for id_val, group in prox_df.groupby(id_column):
        values = group[target_column].values
        weights = group['weight'].values

        # Normalize weights
        weights = weights / weights.sum()

        stats = {
            id_column: id_val,
            'local_q025': weighted_quantile(values, weights, 0.025),
            'local_q25': weighted_quantile(values, weights, 0.25),
            'local_q75': weighted_quantile(values, weights, 0.75),
            'local_q975': weighted_quantile(values, weights, 0.975),
            'local_median': weighted_quantile(values, weights, 0.5),
            'local_std': np.sqrt(np.average((values - np.average(values, weights=weights)) ** 2, weights=weights)),
            'avg_distance': group['distance'].mean(),
            'min_distance': group['distance'].min(),
            'max_distance': group['distance'].max(),
        }
        neighbor_stats.append(stats)

    neighbor_df = pd.DataFrame(neighbor_stats)
    out = df_pred.merge(neighbor_df, on=id_column, how='left')

    # Model disagreement score (normalized by prediction std)
    model_disagreement = (out["prediction"] - out["prediction_uq"]).abs()
    disagreement_score = (model_disagreement / out["prediction_std"]).clip(0, 2)

    # Local confidence based on:
    # 1. How close the neighbors are (closer = more confident)
    # 2. How much local variance there is (less variance = more confident)
    max_reasonable_distance = out['max_distance'].quantile(0.8)  # 80th percentile as reference
    distance_confidence = (1 - (out['avg_distance'] / max_reasonable_distance)).clip(0.1, 1.0)

    variance_confidence = (out["prediction_std"] / out["local_std"]).clip(0.5, 2.0)
    local_confidence = distance_confidence * variance_confidence.clip(0.5, 1.5)

    # Calibration weight: higher when models disagree and we have good local data
    calibration_weight = (
            calibration_strength *
            local_confidence *  # Weight by local data quality
            disagreement_score.clip(0.3, 1.0)  # More calibration when models disagree
    )

    # Consensus prediction (slight preference for NGBoost since it provides intervals)
    consensus_pred = 0.65 * out["prediction_uq"] + 0.35 * out["prediction"]

    # Re-center local intervals around consensus prediction
    local_center_offset = consensus_pred - out["local_median"]

    # Apply calibration to each quantile
    quantile_pairs = [
        ("q_025", "local_q025"),
        ("q_25", "local_q25"),
        ("q_75", "local_q75"),
        ("q_975", "local_q975")
    ]

    for model_q, local_q in quantile_pairs:
        # Adjust local quantiles to be centered around consensus
        adjusted_local_q = out[local_q] + local_center_offset

        # Blend model and local intervals
        out[model_q] = (
                (1 - calibration_weight) * out[model_q] +
                calibration_weight * adjusted_local_q
        )

    # Ensure proper interval ordering and bounds using pandas
    out["q_025"] = pd.concat([out["q_025"], consensus_pred], axis=1).min(axis=1)
    out["q_975"] = pd.concat([out["q_975"], consensus_pred], axis=1).max(axis=1)
    out["q_25"] = pd.concat([out["q_25"], out["q_75"]], axis=1).min(axis=1)

    # Optional: Add some interval expansion when neighbors are very far
    # (indicates we're in a sparse region of feature space)
    sparse_region_mask = out['min_distance'] > out['min_distance'].quantile(0.9)
    expansion_factor = 1 + 0.2 * sparse_region_mask  # 20% expansion in sparse regions

    for q in ["q_025", "q_25", "q_75", "q_975"]:
        interval_width = out[q] - consensus_pred
        out[q] = consensus_pred + interval_width * expansion_factor

    # Clean up temporary columns
    cleanup_cols = [col for col in out.columns if col.startswith("local_")] + \
                   ['avg_distance', 'min_distance', 'max_distance']

    return out.drop(columns=cleanup_cols)


# TRAINING SECTION
#
# This section (__main__) is where SageMaker will execute the training job
# and save the model artifacts to the model directory.
#
if __name__ == "__main__":
    # Template Parameters
    id_column = TEMPLATE_PARAMS["id_column"]
    features = TEMPLATE_PARAMS["features"]
    target = TEMPLATE_PARAMS["target"]
    train_all_data = TEMPLATE_PARAMS["train_all_data"]
    track_columns = TEMPLATE_PARAMS["track_columns"]  # Can be None
    validation_split = 0.2

    # Script arguments for input/output directories
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    parser.add_argument("--train", type=str, default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")
    )
    args = parser.parse_args()

    # Load training data from the specified directory
    training_files = [
        os.path.join(args.train, file)
        for file in os.listdir(args.train) if file.endswith(".csv")
    ]
    print(f"Training Files: {training_files}")

    # Combine files and read them all into a single pandas dataframe
    df = pd.concat([pd.read_csv(file, engine="python") for file in training_files])

    # Check if the DataFrame is empty
    check_dataframe(df, "training_df")

    # Training data split logic
    if train_all_data:
        # Use all data for both training and validation
        print("Training on all data...")
        df_train = df.copy()
        df_val = df.copy()
    elif "training" in df.columns:
        # Split data based on a 'training' column if it exists
        print("Splitting data based on 'training' column...")
        df_train = df[df["training"]].copy()
        df_val = df[~df["training"]].copy()
    else:
        # Perform a random split if no 'training' column is found
        print("Splitting data randomly...")
        df_train, df_val = train_test_split(df, test_size=validation_split, random_state=42)

    # We're using XGBoost for point predictions and NGBoost for uncertainty quantification
    xgb_model = XGBRegressor()
    ngb_model = NGBRegressor()

    # Prepare features and targets for training
    X_train = df_train[features]
    X_val = df_val[features]
    y_train = df_train[target]
    y_val = df_val[target]

    # Train both models using the training data
    xgb_model.fit(X_train, y_train)
    ngb_model.fit(X_train, y_train, X_val=X_val, Y_val=y_val)

    # Make Predictions on the Validation Set
    print(f"Making Predictions on Validation Set...")
    y_validate = df_val[target]
    X_validate = df_val[features]
    preds = xgb_model.predict(X_validate)

    # Calculate various model performance metrics (regression)
    rmse = root_mean_squared_error(y_validate, preds)
    mae = mean_absolute_error(y_validate, preds)
    r2 = r2_score(y_validate, preds)
    print(f"RMSE: {rmse:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"R2: {r2:.3f}")
    print(f"NumRows: {len(df_val)}")

    # Save the trained XGBoost model
    xgb_model.save_model(os.path.join(args.model_dir, "xgb_model.json"))

    # Save the trained NGBoost model
    joblib.dump(ngb_model, os.path.join(args.model_dir, "ngb_model.joblib"))

    # Save the feature list to validate input during predictions
    with open(os.path.join(args.model_dir, "feature_columns.json"), "w") as fp:
        json.dump(features, fp)

    # Now the Proximity model
    model = Proximity(df_train, id_column, features, target, track_columns=track_columns)

    # Now serialize the model
    model.serialize(args.model_dir)


#
# Inference Section
#
def model_fn(model_dir) -> dict:
    """Load and return XGBoost and NGBoost regressors from model directory."""

    # Load XGBoost regressor
    xgb_path = os.path.join(model_dir, "xgb_model.json")
    xgb_model = XGBRegressor(enable_categorical=True)
    xgb_model.load_model(xgb_path)

    # Load NGBoost regressor
    ngb_model = joblib.load(os.path.join(model_dir, "ngb_model.joblib"))

    # Deserialize the proximity model
    prox_model = Proximity.deserialize(model_dir)

    return {
        "xgboost": xgb_model,
        "ngboost": ngb_model,
        "proximity": prox_model
    }


def input_fn(input_data, content_type):
    """Parse input data and return a DataFrame."""
    if not input_data:
        raise ValueError("Empty input data is not supported!")

    # Decode bytes to string if necessary
    if isinstance(input_data, bytes):
        input_data = input_data.decode("utf-8")

    if "text/csv" in content_type:
        return pd.read_csv(StringIO(input_data))
    elif "application/json" in content_type:
        return pd.DataFrame(json.loads(input_data))  # Assumes JSON array of records
    else:
        raise ValueError(f"{content_type} not supported!")


def output_fn(output_df, accept_type):
    """Supports both CSV and JSON output formats."""
    if "text/csv" in accept_type:
        csv_output = output_df.fillna("N/A").to_csv(index=False)  # CSV with N/A for missing values
        return csv_output, "text/csv"
    elif "application/json" in accept_type:
        return output_df.to_json(orient="records"), "application/json"  # JSON array of records (NaNs -> null)
    else:
        raise RuntimeError(f"{accept_type} accept type is not supported by this script.")


def predict_fn(df, models) -> pd.DataFrame:
    """Make Predictions with our XGB Quantile Regression Model

    Args:
        df (pd.DataFrame): The input DataFrame
        models (dict): The dictionary of models to use for predictions

    Returns:
        pd.DataFrame: The DataFrame with the predictions added
    """

    # Grab our feature columns (from training)
    model_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
    with open(os.path.join(model_dir, "feature_columns.json")) as fp:
        model_features = json.load(fp)

    # Match features in a case-insensitive manner
    matched_df = match_features_case_insensitive(df, model_features)

    # Use XGBoost for point predictions
    df["prediction"] = models["xgboost"].predict(matched_df[model_features])

    # NGBoost predict returns distribution objects
    y_dists = models["ngboost"].pred_dist(matched_df[model_features])

    # Extract parameters from distribution
    dist_params = y_dists.params

    # Extract mean and std from distribution parameters
    df["prediction_uq"] = dist_params['loc']  # mean
    df["prediction_std"] = dist_params['scale']  # standard deviation

    # Add 95% prediction intervals using ppf (percent point function)
    df["q_025"] = y_dists.ppf(0.025)  # 2.5th percentile
    df["q_975"] = y_dists.ppf(0.975)  # 97.5th percentile

    # Add 50% prediction intervals
    df["q_25"] = y_dists.ppf(0.25)   # 25th percentile
    df["q_75"] = y_dists.ppf(0.75)   # 75th percentile

    # Compute Nearest neighbors with Proximity model
    prox_df = models["proximity"].neighbors(df)

    # Shrink prediction intervals based on KNN variance
    df = distance_weighted_calibrated_intervals(df, prox_df)

    # Return the modified DataFrame
    return df
