import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from sklearn.linear_model import LogisticRegression
import json

# Initialize session state
if "symptom_log" not in st.session_state:
    st.session_state.symptom_log = []

# Use Google Sheets API with Streamlit Secrets
def append_to_google_sheet(data_row):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
    client = gspread.authorize(creds)

    # Debug: List accessible sheets
    sheet_titles = [sheet.title for sheet in client.openall()]
    st.write("Accessible sheets:", sheet_titles)

    sheet = client.open("IBS Tracker Data").sheet1
    sheet.append_row(data_row)

# Sample ML model (mock training data)
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

# Mapping for severity levels
def map_level(level):
    return {
        "None": 0,
        "Mild": 2,
        "Moderate": 5,
        "High": 7,
        "Severe/Extreme": 10
    }[level]

severity_description = {
    "None": "No noticeable symptoms or triggers.",
    "Mild": "Slight discomfort, manageable without intervention.",
    "Moderate": "More persistent discomfort, may affect daily activities.",
    "High": "Significant symptoms affecting quality of life.",
    "Severe/Extreme": "Severe symptoms requiring strong management or medical advice."
}

# Streamlit UI
st.title("IBS Flare-Up Predictor & Tracker")

# Symptom inputs
food_trigger_level = st.radio("How spicy was your food today?", list(severity_description.keys()))
st.caption(severity_description[food_trigger_level])
stress_level = st.radio("Your stress level today?", list(severity_description.keys()))
st.caption(severity_description[stress_level])
previous_symptom_level = st.radio("IBS symptoms yesterday?", list(severity_description.keys()))
st.caption(severity_description[previous_symptom_level])

abdominal_pain = st.slider("Abdominal Pain (0–10)", 0, 10, 4)
bloating = st.slider("Bloating (0–10)", 0, 10, 4)
sleep = st.slider("Sleep Hours", 3, 10, 6)
water = st.slider("Water Intake (L)", 0.5, 5.0, 2.5, 0.1)
exercise = st.selectbox("Did you exercise today?", ["No", "Yes"])

# Common triggers
spices = st.multiselect("Any of these consumed today?", [
    "Red chili powder", "Green chili", "Garam masala", "Pickles", "Fried snacks", "Caffeinated drinks"
])

# Food trigger detection
user_foods = st.text_area("Foods you consumed today (comma-separated)")
common_triggers = ["pickle", "coffee", "fry", "masala", "sauce", "noodles", "ghee", "spice", "curd"]
if user_foods:
    detected = [f.strip() for f in user_foods.lower().split(",") if any(t in f for t in common_triggers)]
    for trigger in detected:
        if trigger not in spices:
            spices.append(trigger)
    if detected:
        st.warning("Triggers detected: " + ", ".join(detected))

# Prepare input
data = np.array([[
    map_level(food_trigger_level),
    map_level(stress_level),
    sleep,
    water,
    1 if exercise == "Yes" else 0,
    map_level(previous_symptom_level),
    len(spices)
]])

# Predict
if st.button("Predict Flare-Up"):
    prediction = model.predict(data)[0]
    flare_status = "Yes" if prediction else "No"

    today = datetime.now().strftime("%Y-%m-%d")
    data_row = [today, flare_status, abdominal_pain, bloating, "-"]
    append_to_google_sheet(data_row)

    st.session_state.symptom_log.append({
        "flare_up": flare_status,
        "abdominal_pain": abdominal_pain,
        "bloating": bloating
    })

    if prediction:
        st.error("High chance of flare-up. Try a bland diet, hydrate, reduce stress.")
    else:
        st.success("Low chance of flare-up. Keep up the good routine!")

# Show symptom trend chart
if st.session_state.symptom_log:
    st.markdown("### Symptom Trends")
    log = st.session_state.symptom_log[-30:]
    days = list(range(1, len(log) + 1))
    pain = [entry["abdominal_pain"] for entry in log]
    bloat = [entry["bloating"] for entry in log]
    flares = [1 if entry["flare_up"] == "Yes" else 0 for entry in log]

    fig, ax = plt.subplots()
    ax.plot(days, pain, label="Abdominal Pain", color="red")
    ax.plot(days, bloat, label="Bloating", color="blue")
    ax.plot(days, flares, label="Flare-Ups", color="green", linestyle="--")
    ax.set_xlabel("Days")
    ax.set_ylabel("Severity")
    ax.set_title("IBS Symptom Trends")
    ax.legend()
    st.pyplot(fig)
