from flask import Flask, render_template, request
import joblib
import numpy as np
# test comment
app = Flask(__name__)
# I have added a comment line above
# Load trained model
model = joblib.load('random_forest_model.pkl')

# List of all 22 features
features = [
    'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)',
    'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP',
    'MDVP:PPQ', 'Jitter:DDP', 'MDVP:Shimmer', 'MDVP:Shimmer(dB)',
    'Shimmer:APQ3', 'Shimmer:APQ5', 'MDVP:APQ', 'Shimmer:DDA',
    'NHR', 'HNR', 'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get user input as float
    input_data = [float(request.form[feat]) for feat in features]
    input_data = np.array(input_data).reshape(1, -1)

    # Predict
    prediction = model.predict(input_data)[0]
    result = 'Parkinson Positive' if prediction == 1 else 'Healthy'

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
