from flask import Flask, request, jsonify,Blueprint
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import MinMaxScaler
from lime import lime_tabular


ranked_bids_bp = Blueprint('ranked_bids_bp', __name__)


# Example SQLAlchemy Tender model
class Tender:
    def __init__(self, id, requirements):
        self.id = id
        self.requirements = requirements


@ranked_bids_bp.route('/api/evaluate-bids', methods=['POST'])
def evaluate_bids():
    # Mock data for tender and bids (replace with actual DB query)
    # tender = Tender(
    #     id="Tender_123",
    #     requirements={
    #         "estimated_cost": 1000000,
    #         "estimated_timeline": 120,
    #         "cost_weight": 0.4,
    #         "timeline_weight": 1.2,
    #         "compliance_weight": 0.1,
    #         "current_factors_weight": 0.6,
    #         "historical_rating_weight": 0.4
    #     }
    # )

    # Example current bids (replace with actual data from DB)
    # current_bids = [
    #     {"bidder_id": "Company_132", "bid_cost": 950000, "proposed_timeline": 100, "compliance": True},
    #     {"bidder_id": "Company_701", "bid_cost": 1000000, "proposed_timeline": 120, "compliance": True},
    #     {"bidder_id": "Company_603", "bid_cost": 980000, "proposed_timeline": 130, "compliance": False}
    # ]

    # Get Tender and current bids from the body
    data = request.get_json()
    # print("Inside evaluate bids")
    print(data)
    if not data:
        return jsonify({"error": "No data provided"}), 400

    tender_data = (data.get('tender'))
    tender = Tender(
        id=tender_data.get('id', 'Unknown'),
        requirements={
            "estimated_cost": tender_data.get('requirements', {}).get('estimated_cost', 0),
            "estimated_timeline": tender_data.get('requirements', {}).get('estimated_timeline', 0),
            "cost_weight": tender_data.get('requirements', {}).get('cost_weight', 0),
            "timeline_weight": tender_data.get('requirements', {}).get('timeline_weight', 0),
            "compliance_weight": tender_data.get('requirements', {}).get('compliance_weight', 0),
            "current_factors_weight": tender_data.get('requirements', {}).get('current_factors_weight', 0),
            "historical_rating_weight": tender_data.get('requirements', {}).get('historical_rating_weight', 0)
        }
    )
    current_bids = (data.get('bids'))
    print(tender)
    print(current_bids)
    if not tender or not current_bids:
        return jsonify({"error": "Missing tender or bids data"}), 400

    # Fetch historical ratings from the `history.py` API
    history_url = "http://127.0.0.1:5000/api/company-ratings"  # Replace with the correct URL
    try:
        response = requests.get(history_url)
        response.raise_for_status()
        historical_ratings = response.json()["ranked_companies"]
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch historical ratings: {str(e)}"}), 500

    # Merge current bids with historical ratings
    bid_df = pd.DataFrame(current_bids)
    history_df = pd.DataFrame(historical_ratings).rename(columns={"Company ID": "bidder_id"})
    merged_df = bid_df.merge(history_df, on="bidder_id", how="left")

    # Handle missing historical ratings
    merged_df["Predicted Rating"].fillna(0, inplace=True)

    # Calculate deviations and normalize values
    scaler = MinMaxScaler()
    requirements = tender.requirements
    merged_df["cost_deviation"] = abs(merged_df["bid_cost"] - requirements["estimated_cost"]) / requirements[
        "estimated_cost"]
    merged_df["timeline_deviation"] = abs(merged_df["proposed_timeline"] - requirements["estimated_timeline"]) / \
                                      requirements["estimated_timeline"]

    # Calculate current score based on weights
    merged_df["current_score"] = (
            (1 - merged_df["cost_deviation"]) * requirements["cost_weight"] +
            (1 - merged_df["timeline_deviation"]) * requirements["timeline_weight"] +
            merged_df["compliance"] * requirements["compliance_weight"]
    )

    # Calculate final score using both historical and current factors
    merged_df["final_score"] = (
            merged_df["current_score"] * requirements["current_factors_weight"] +
            merged_df["Predicted Rating"] * requirements["historical_rating_weight"]
    )

    explainer = lime_tabular.LimeTabularExplainer(
        training_data=merged_df[["bid_cost", "proposed_timeline", "compliance"]].values,
        feature_names=["bid_cost", "proposed_timeline", "compliance"],
        mode="regression"
    )

    insights = []
    for _, row in merged_df.iterrows():
        bid_features = row[["bid_cost", "proposed_timeline", "compliance"]].values
        explanation = explainer.explain_instance(
            data_row=bid_features,
            predict_fn=lambda x: predict_fn(x, requirements)  # Pass the requirements directly
        )
        insights.append({"bidder_id": row["bidder_id"], "lime_explanation": explanation.as_list()})

    ranked_bidders = merged_df.sort_values(by="final_score", ascending=False)[["bidder_id", "final_score"]]
    ranked_bidders["lime_insights"] = [i["lime_explanation"] for i in insights]

    ranked_bidders["readable_insights"] = [
        generate_readable_insights(bid["lime_insights"], bid["bidder_id"])
        for bid in ranked_bidders.to_dict(orient="records")
    ]
    return jsonify({"ranked_bidders": ranked_bidders.to_dict(orient="records")})


def predict_fn(input_data, requirements):
    temp_df = pd.DataFrame(input_data, columns=["bid_cost", "proposed_timeline", "compliance"])
    # Calculate cost and timeline deviations using the requirements passed as an argument
    temp_df["cost_deviation"] = abs(temp_df["bid_cost"] - requirements["estimated_cost"]) / requirements[
        "estimated_cost"]
    temp_df["timeline_deviation"] = abs(temp_df["proposed_timeline"] - requirements["estimated_timeline"]) / \
                                    requirements["estimated_timeline"]
    # Calculate the current score based on weights
    temp_df["current_score"] = (
            (1 - temp_df["cost_deviation"]) * requirements["cost_weight"] +
            (1 - temp_df["timeline_deviation"]) * requirements["timeline_weight"] +
            temp_df["compliance"] * requirements["compliance_weight"]
    )
    return temp_df["current_score"].values


def generate_readable_insights(lime_insights, bidder_id):
    insights = []

    if not lime_insights:
        return f"Bidder {bidder_id}: No LIME insights available."

    for feature, coefficient in lime_insights:
        # Check for correct structure
        if not isinstance(feature, str) or not isinstance(coefficient, (int, float)):
            continue  # Skip invalid entries

        if "proposed_timeline" in feature:
            # Timeline Influence based on coefficient
            if coefficient > 0:
                insights.append(f"Bidder {bidder_id}: Proposed timeline duration was viewed positively.")
            else:
                insights.append(f"Bidder {bidder_id}: Proposed timeline duration negatively impacted the score.")

        elif "compliance" in feature:
            # Compliance Influence based on coefficient
            if coefficient > 0:
                insights.append(f"Bidder {bidder_id}: Compliance level positively affected the score.")
            else:
                insights.append(f"Bidder {bidder_id}: Compliance level negatively impacted the score.")

        elif "bid_cost" in feature:
            # Bid Cost Influence based on coefficient
            if coefficient > 0:
                insights.append(f"Bidder {bidder_id}: Bid cost had a positive impact on the score.")
            else:
                insights.append(f"Bidder {bidder_id}: Bid cost had a negative impact on the score.")

    # Return the combined insights for the bidder
    if not insights:
        return f"Bidder {bidder_id}: No significant impact from the bid parameters."

    return " ".join(insights)


if __name__ == "__main__":
    app.run(debug=True, port=5001)