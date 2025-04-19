import streamlit as st
import numpy as np
from sklearn.linear_model import LogisticRegression

# Sample training (mock model)
model = LogisticRegression()
X_sample = np.array([
    [5, 7, 5, 2.0, 1, 6],
    [2, 3, 8, 3.0, 0, 2],
    [8, 8, 4, 1.5, 0, 7],
    [1, 1, 7, 2.5, 1, 1],
    [9, 9, 3, 1.0, 0, 8]
])
y_sample = [1, 0, 1, 0, 1]
model.fit(X_sample, y_sample)

# Streamlit UI
st.title("IBS Flare-Up Predictor")
st.write("Enter your daily details to predict the chance of an IBS flare-up.")

food_trigger = st.slider("Food Trigger Score (0-10)", 0, 10, 5)
stress = st.slider("Stress Level (0-10)", 0, 10, 5)
sleep = st.slider("Sleep Quality (Hours)", 3, 10, 6)
water = st.slider("Water Intake (Liters)", 0.5, 5.0, 2.5, 0.1)
exercise = st.selectbox("Did you exercise today?", ["No", "Yes"])
previous_symptoms = st.slider("Previous Day's Symptom Score (0-10)", 0, 10, 5)

# Convert inputs
data = np.array([[food_trigger, stress, sleep, water, 1 if exercise == "Yes" else 0, previous_symptoms]])

# Predict
if st.button("Predict Flare-Up"):
    prediction = model.predict(data)[0]
    if prediction:
        st.error("High chance of flare-up today. Take preventive steps.")
    else:
        st.success("Low chance of flare-up today. Keep maintaining your routine!")