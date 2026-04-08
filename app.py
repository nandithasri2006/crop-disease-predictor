from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)

# Load trained model and encoders
model = joblib.load('xgb_disease_model.pkl')
scaler = joblib.load('scaler.pkl')
crop_mapping = joblib.load('crop_mapping.pkl')       # e.g., {'apple':0, 'banana':1, ...}
disease_mapping = joblib.load('disease_mapping.pkl') # e.g., {0:'No Disease',1:'Fungal',...}

# Optional: colors for each disease
disease_colors = {
    'No Disease': '#2ecc71',
    'Fungal': '#e67e22',
    'Bacterial': '#e74c3c',
    'Viral': '#9b59b6'
}

def main_predict(crop_name, N, P, K, temperature, humidity, ph, rainfall):
    label = crop_mapping.get(crop_name.lower())
    if label is None:
        return "Unknown Crop"
    
    df_input = pd.DataFrame([{
        'label': label,
        'N': N,
        'P': P,
        'K': K,
        'temperature': temperature,
        'humidity': humidity,
        'ph': ph,
        'rainfall': rainfall
    }])

    numeric_cols = ['N','P','K','temperature','humidity','ph','rainfall']
    df_input[numeric_cols] = scaler.transform(df_input[numeric_cols])

    pred_numeric = model.predict(df_input)[0]
    disease_name = disease_mapping.get(pred_numeric, "Unknown")

    return disease_name

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    color = '#fff'

    if request.method == 'POST':
        crop_name = request.form['crop']
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        prediction = main_predict(crop_name, N, P, K, temperature, humidity, ph, rainfall)
        color = disease_colors.get(prediction, '#3498db')

    crops = list(crop_mapping.keys())
    return render_template('index.html',
                           prediction=prediction,
                           color=color,
                           crops=crops)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)