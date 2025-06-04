from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import logging
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.INFO)

# Load trained model
try:
    model = joblib.load("house_price_model_final.pkl")
    logging.info("✅ Model loaded successfully.")
except Exception as e:
    logging.error(f"❌ Error loading model: {e}")
    model = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json() or request.form
        logging.info("Received request: %s", data)

        # Extract and validate data
        location = data.get("location")
        size_sqft = float(data.get("size_sqft", 0))
        bedrooms = int(data.get("bedrooms", 0))
        bathrooms = int(data.get("bathrooms", 0))
        age_of_property = int(data.get("age_of_property", 0))

        # Bin 'age_of_property'
        age_bins = [-1, 5, 10, 20, 50]
        age_labels = [0, 1, 2, 3]
        input_data = pd.DataFrame([[location, size_sqft, bedrooms, bathrooms, age_of_property]],
                                  columns=["location", "size_sqft", "bedrooms", "bathrooms", "age_of_property"])
        input_data["age_of_property_binned"] = pd.cut(input_data["age_of_property"], bins=age_bins, labels=age_labels)

        # Compute price per square foot
        price_per_sqft = round(size_sqft * 0.02, 2)
        input_data["price_per_sqft"] = price_per_sqft

        # Drop 'age_of_property'
        input_data = input_data.drop(columns=["age_of_property"])

        if model:
            predicted_price = round(model.predict(input_data)[0], 2)
            return jsonify({"predicted_price": predicted_price, "price_per_sqft": price_per_sqft})
        else:
            return jsonify({"error": "Model is not loaded."}), 500
    
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 400

# Function to fetch loan offers from the database
def get_loan_offers(income):
    try:
        conn = sqlite3.connect("loans.db")
        cursor = conn.cursor()

        # Fetch loan offers
        cursor.execute("SELECT bank_name, interest_rate, tenure, max_loan_amount FROM loan_offers")
        offers = cursor.fetchall()
        conn.close()

        # Filter loan offers based on income
        loan_offers = []
        for offer in offers:
            bank_name, interest_rate, tenure, max_loan_amount = offer
            loan_amount = min(int(income) * 5, max_loan_amount)  # Loan eligibility: 5x income
            loan_offers.append({
                "bank": bank_name,
                "interest_rate": interest_rate,
                "tenure": tenure,
                "loan_amount": loan_amount
            })

        return loan_offers[:5]  # Return top 5 offers
    except Exception as e:
        logging.error(f"Database error: {e}")
        return []

# Route to fetch loan offers from the predefined database
@app.route("/fetch-loan-offers", methods=["POST"])
def fetch_loan_offers():
    try:
        data = request.get_json()
        logging.info("Received loan request: %s", data)
        income = int(data.get("income", 0))
        
        if income <= 0:
            return jsonify({"error": "Invalid income value"}), 400

        loan_offers = get_loan_offers(income)
        if not loan_offers:
            return jsonify({"error": "No loan offers available."}), 404
        
        logging.info("Sending loan offers: %s", loan_offers)
        return jsonify({"loan_offers": loan_offers})
    
    except Exception as e:
        logging.error(f"Error fetching loan offers: {e}")
        return jsonify({"error": "Failed to fetch loan offers."}), 500

# Route for loan page
@app.route("/loan")
def loan_page():
    return render_template("loan.html")

if __name__ == "__main__":
    app.run(debug=True)
