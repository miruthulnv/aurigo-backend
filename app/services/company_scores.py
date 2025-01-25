from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from flask import Blueprint
company_scores_bp = Blueprint('company_scores', __name__)

MODEL_FILE_PATH = "random_forest_model.pkl"

@company_scores_bp.route('/api/model-evaluation', methods=['GET'])
def evaluate_model():
    file_path = "../tender_with_ratings.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return jsonify({"error": "File not found. Check the file path."}), 400

    features = [
        "Experience (years)", "Bid Cost ($)", "Estimated Duration (days)",
        "Reputation Score", "Location Advantage", "Cost Deviation (%)",
        "Deadline Deviation (%)"
    ]
    target = "Numeric Rating"

    df = df.dropna(subset=features + [target])

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save trained model
    with open(MODEL_FILE_PATH, "wb") as model_file:
        pickle.dump(model, model_file)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return jsonify({
        "mean_absolute_error": mae,
        "mean_squared_error": mse,
        "r2_score": r2
    })

@company_scores_bp.route('/api/company-ratings', methods=['POST','GET'])
def calculate_ratings():
    file_path = "app/tender_with_ratings.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        return jsonify({"error": "File not found. Check the file path."}), 400

    features = [
        "Experience (years)", "Bid Cost ($)", "Estimated Duration (days)",
        "Reputation Score", "Location Advantage", "Cost Deviation (%)",
        "Deadline Deviation (%)"
    ]
    target = "Numeric Rating"
    df = df.dropna(subset=features + [target])
    X = df[features]
    y = df[target]

    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the Random Forest Regressor model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Load the already trained model if exists
    # try:
    #     with open(MODEL_FILE_PATH, "rb") as model_file:
    #         model = pickle.load(model_file)
    # except FileNotFoundError:
    #     return jsonify({"error": "Model not found. Train the model first."}), 500

    df["Predicted Rating"] = model.predict(X)
    sorted_companies = (
        df.groupby("Company ID")["Predicted Rating"]
        .mean()
        .reset_index()
        .sort_values(by="Predicted Rating", ascending=False)
    )

    result = sorted_companies.to_dict(orient="records")
    return jsonify({"ranked_companies": result})

if __name__ == '__main__':
    app.run(debug=True)
