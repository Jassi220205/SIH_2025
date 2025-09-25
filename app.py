import os
from flask import Flask, render_template, request
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import joblib
import pandas as pd

# --- 1. APP & DATABASE SETUP ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the trained AI model
try:
    model = joblib.load('outbreak_model.pkl')
    model_columns = list(model.feature_names_in_)
    print("Model loaded successfully.")
except FileNotFoundError:
    model = None
    model_columns = []
    print("Model file not found. Predictions will be disabled.")

# Assign coordinates to villages
VILLAGE_COORDINATES = {
    "V001": [18.0792, 82.6841], "V002": [17.652, 82.411],
    "V003": [18.230, 82.872], "V004": [17.891, 82.522],
    "V005": [17.485, 82.021]
}

# --- 2. DATABASE MODEL ---
class PatientReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    suspected_disease = db.Column(db.String(100))
    symptoms = db.Column(db.String(300))
    notes = db.Column(db.Text)
    filename = db.Column(db.String(200))


# --- 3. ROUTES ---
@app.route('/')
def index():
    """Renders the main form page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Processes the symptom form, saves data, makes a prediction, and shows the result."""
    patient_name = request.form.get('patient')
    village = request.form.get('village')
    age = request.form.get('age')
    gender = request.form.get('gender')
    disease = request.form.get('disease')
    symptoms = request.form.getlist('symptoms')
    notes = request.form.get('notes')

    prediction_result = "Not available"
    if model:
        input_data = {col: [0] for col in model_columns}
        for symptom in symptoms:
            symptom_key = f"symptom_{symptom.replace(' ', '_').lower()}"
            if symptom_key in input_data:
                input_data[symptom_key] = [1]
        
        input_df = pd.DataFrame(input_data)
        prediction = model.predict(input_df)[0]
        prediction_proba = model.predict_proba(input_df)[0][1]

        if prediction == 1:
            prediction_result = f"High Risk ({prediction_proba*100:.0f}%)"
            try:
                msg = Message(
                    subject=f"High Risk Alert: Potential Outbreak in {village}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=['health_official@example.com'] # CHANGE RECIPIENT
                )
                msg.body = f"A high-risk patient report submitted for {village}..."
                mail.send(msg)
                print("High-risk alert email sent successfully.")
            except Exception as e:
                print(f"Error sending email: {e}")
        else:
            prediction_result = f"Low Risk ({prediction_proba*100:.0f}%)"

    filename = "No file uploaded."
    if 'attachment' in request.files and request.files['attachment'].filename != '':
        file = request.files['attachment']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    symptoms_str = ", ".join(symptoms)
    new_report = PatientReport(
        patient_name=patient_name, village=village, age=age, gender=gender,
        suspected_disease=disease, symptoms=symptoms_str, notes=notes,
        filename=filename
    )
    db.session.add(new_report)
    db.session.commit()

    return render_template(
        'result.html',
        patient=patient_name, village=village, age=age, gender=gender,
        disease=disease, symptoms=symptoms, notes=notes, filename=filename,
        prediction=prediction_result
    )

@app.route('/dashboard')
def dashboard():
    """Renders the dashboard page with analytics and filtering."""
    selected_village = request.args.get('village')
    
    unique_villages_query = db.session.query(PatientReport.village).distinct().all()
    villages = sorted([v[0] for v in unique_villages_query if v[0]])

    query = PatientReport.query
    if selected_village and selected_village != 'all':
        query = query.filter_by(village=selected_village)

    filtered_reports = query.all()
    
    total_reports = len(filtered_reports)
    disease_counts = {}
    village_cases = {}

    for report in filtered_reports:
        disease = report.suspected_disease
        if disease:
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        village = report.village
        if village in VILLAGE_COORDINATES:
            village_cases[village] = village_cases.get(village, 0) + 1
    
    hotspot_data = []
    for village, case_count in village_cases.items():
        hotspot_data.append({
            "village_name": village,
            "coords": VILLAGE_COORDINATES.get(village, [0, 0]),
            "cases": case_count
        })

    return render_template(
        'dashboard.html', 
        reports=filtered_reports,
        total_reports=total_reports, 
        disease_counts=disease_counts,
        hotspot_data=hotspot_data,
        villages=villages,
        selected_village=selected_village
    )

# --- 4. RUN THE APP ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

