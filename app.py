import streamlit as st
import numpy as np
from sklearn.linear_model import LogisticRegression

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

# Streamlit UI
st.title("IBS Flare-Up Predictor")
st.write("Enter your daily details to predict the chance of an IBS flare-up.")

# Classified Inputs
food_trigger_level = st.radio("How spicy or IBS-triggering was your food today?",
                              ["None", "Mild", "Moderate", "High", "Severe/Extreme"])
stress_level = st.radio("Your stress level today?",
                        ["None", "Mild", "Moderate", "High", "Severe/Extreme"])
previous_symptom_level = st.radio("How were your IBS symptoms yesterday?",
                                  ["None", "Mild", "Moderate", "High", "Severe/Extreme"])

# Numeric Inputs
sleep = st.slider("Sleep Quality (Hours)", 3, 10, 6)
water = st.slider("Water Intake (Liters)", 0.5, 5.0, 2.5, 0.1)
exercise = st.selectbox("Did you exercise today?", ["No", "Yes"])

# Indian food triggers
st.markdown("**Did you consume any of these common IBS triggers?**")
spices = st.multiselect("Select all that apply:", [
    "Red chili powder", "Green chili", "Garam masala",
    "Pickles", "Fried snacks", "Caffeinated drinks"
])
spice_score = len(spices)

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
    spice_score
]])

# Prediction Button
if st.button("Predict Flare-Up"):
    prediction = model.predict(data)[0]
    if prediction:
        st.error("High chance of flare-up today. Consider reducing stress, avoiding spicy foods, and hydrating well.")
    else:
        st.success("Low chance of flare-up today. Keep maintaining your routine!")

# Explanation
st.markdown("""
### How is this calculated?

This app uses a machine learning model trained on symptom and lifestyle data to estimate your risk of an IBS flare-up.
We look at stress, diet, sleep, hydration, and your recent symptom history.
This is not a diagnosis — just a tool to help you manage patterns and habits.
""")
