import streamlit as st
import requests

API_URL = "http://localhost:8000/predict"

# Page config
st.set_page_config(page_title="Insurance Predictor", layout="centered")

st.title("💡 Insurance Premium Predictor")
st.markdown("Fill the details and get instant prediction")

# ---------------- INPUT SECTION ----------------
with st.form("prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Age", 1, 119, 30)
        weight = st.number_input("Weight (kg)", 1.0, 200.0, 65.0)
        income_lpa = st.number_input("Income (LPA)", 0.1, 100.0, 10.0)

    with col2:
        height = st.number_input("Height (m)", 0.5, 2.5, 1.7)
        smoker = st.selectbox("Smoker", [True, False])
        occupation = st.selectbox(
            "Occupation",
            ['retired', 'freelancer', 'student', 'government_job',
             'business_owner', 'unemployed', 'private_job']
        )

    city = st.text_input("City", "Mumbai")

    submit = st.form_submit_button("🔍 Predict")

# ---------------- RESULT SECTION ----------------
if submit:
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        with st.spinner("Analyzing..."):
            response = requests.post(API_URL, json=input_data)

        if response.status_code == 200:
            result = response.json()

            # Adjust this based on your API response
            prediction = result.get("response", result)

            category = prediction.get("Predicted Category", "Unknown")
            confidence = prediction.get("confidence", 0)

            # 🎯 SUCCESS CARD
            st.markdown("### 🎯 Prediction Result")

            if category.lower() == "low":
                st.success(f"🟢 Category: {category}")
            elif category.lower() == "medium":
                st.warning(f"🟡 Category: {category}")
            else:
                st.error(f"🔴 Category: {category}")

            # 📊 Metrics
            col1, col2 = st.columns(2)
            col1.metric("Confidence", f"{confidence:.2%}")
            col2.metric("Risk Level", category)

            # 📈 Probabilities (optional)
            if "class_probabilities" in prediction:
                st.markdown("### 📊 Class Probabilities")
                st.bar_chart(prediction["class_probabilities"])

            # 🔍 Raw response (collapsible)
            with st.expander("🔎 View Raw API Response"):
                st.json(result)

        else:
            st.error(f"❌ API Failed (Status {response.status_code})")
            st.text(response.text)

    except requests.exceptions.ConnectionError:
        st.error("🚫 Cannot connect to FastAPI server (Is uvicorn running?)")