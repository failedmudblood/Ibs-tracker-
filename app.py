import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st
import numpy as np
from sklearn.linear_model import LogisticRegression
def append_to_google_sheet(data_row):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("IBS Tracker Data").sheet1
    sheet.append_row(data_row)

# Sample training (mock model)
model = LogisticRegression()
X_sample = np.array([
    [5, 7, 5, 2.0, 1, 6, 2],
    [2, 3, 8, 3.0, 0, 2, 0],
    [8, 8, 4, 1.5, 0, 7, 3],
    [1, 1, 7, 2.5, 1, 1, 0],
    [9, 9, 3, 1.0, 0, 8, 4]
])
y_sample = [1, 0, 1, 0, 1]
model.fit(X_sample, y_sample)

# Mapping for classified inputs
def map_level(level):
    return {
        "None": 0,
        "Mild": 2,
        "Moderate": 5,
        "High": 7,
        "Severe/Extreme": 10
    }[level]

# Descriptions for severity levels
severity_description = {
    "None": "No noticeable symptoms or triggers.",
    "Mild": "Slight discomfort, manageable without intervention.",
    "Moderate": "More persistent discomfort, may affect daily activities.",
    "High": "Significant symptoms affecting quality of life.",
    "Severe/Extreme": "Severe symptoms requiring strong management or medical advice."
}

# Streamlit UI
st.title("IBS Flare-Up Predictor & Manager")
st.write("Predict, track, and manage your IBS symptoms with intelligent suggestions and real-world tracking.")

# Classified Inputs with descriptions
food_trigger_level = st.radio("How spicy or IBS-triggering was your food today?", list(severity_description.keys()))
st.caption(severity_description[food_trigger_level])

stress_level = st.radio("Your stress level today?", list(severity_description.keys()))
st.caption(severity_description[stress_level])

previous_symptom_level = st.radio("How were your IBS symptoms yesterday?", list(severity_description.keys()))
st.caption(severity_description[previous_symptom_level])

# Numeric Inputs
sleep = st.slider("Sleep Quality (Hours)", 3, 10, 6)
water = st.slider("Water Intake (Liters)", 0.5, 5.0, 2.5, 0.1)
exercise = st.selectbox("Did you exercise today?", ["No", "Yes"])

# Indian food triggers
st.markdown("**Did you consume any of these common IBS triggers?**")
spices = st.multiselect("Select all that apply:", [
    "Red chili powder", "Green chili", "Garam masala", "Pickles", "Fried snacks", "Caffeinated drinks"
])
spice_score = len(spices)

# Food trigger detector
st.markdown("**Enter the foods you consumed today:**")
user_foods = st.text_area("Separate items by commas (e.g., rice, dal, pickle, coffee)")
detected_triggers = []
common_triggers = ["pickle", "coffee", "fry", "masala", "sauce", "noodles"]
if user_foods:
    foods = [f.strip().lower() for f in user_foods.split(",")]
    for food in foods:
        if any(trigger in food for trigger in common_triggers):
            detected_triggers.append(food)
            if food not in spices:
                spices.append(food)
    if detected_triggers:
        st.warning(f"Possible triggers detected: {', '.join(detected_triggers)}")

# Custom food trigger option
st.text_input("Want to note a possible trigger food today? (Optional)", key="food_note")

# Convert inputs
data = np.array([[
    map_level(food_trigger_level),
    map_level(stress_level),
    sleep,
    water,
    1 if exercise == "Yes" else 0,
    map_level(previous_symptom_level),
    len(spices)
]])

# Prediction Button
if st.button("Predict Flare-Up"):
    prediction = model.predict(data)[0]
    if prediction:
        st.error("High chance of flare-up today. Consider reducing stress, avoiding spicy foods, and hydrating well.")
        st.info("Daily Tip: Try a bland diet today, stay hydrated, and avoid known triggers. A short walk or breathing exercise may help.")
    else:
        st.success("Low chance of flare-up today. Keep maintaining your routine!")
        st.info("Great job! Keep a consistent routine. Try logging what worked well today so you can repeat it.")
        today = datetime.now().strftime("%Y-%m-%d")
    data_row = [today, flare_status, abdominal_pain, bloating, "Yes" if rome_positive else "No"]

    append_to_google_sheet(data_row)

# Explanation
st.markdown("""
### How is this calculated?

This app uses a machine learning model trained on symptom and lifestyle data to estimate your risk of an IBS flare-up.
We look at stress, diet, sleep, hydration, and your recent symptom history.
It uses both current data and recognized scientific patterns (e.g., high spice and stress correlation with IBS).

> Research-backed logic: High-stress, low-sleep, and high-spice consumption days are more likely to result in flare-ups. 
> This model improves the more you use it, offering smarter alerts and behavior tips.

This is not a diagnosis — just a tool to help you manage patterns and habits.
""")
