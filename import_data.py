import pandas as pd
from app import app, db, PatientReport
import random # <-- IMPORTED RANDOM

def parse_age(age_group):
    """A helper function to get a representative age from an age group string."""
    if isinstance(age_group, str):
        if '60+' in age_group:
            return 65
        if 'Jun-18' in age_group:
            return 12
        if '-' in age_group:
            return int(age_group.split('-')[0]) + 5
    return 30

def import_excel_data():
    df = pd.read_csv('dataset.csv')
    
    print(f"Found {len(df)} rows in the CSV file. Starting import...")
    
    # --- NEW: List of possible diseases ---
    DISEASE_LIST = ['Typhoid', 'Hepatitis A', 'Giardiasis', 'E. coli Infection']

    for index, row in df.iterrows():
        symptoms = []
        if row.get('symptom_fever') == 1: symptoms.append('Fever')
        if row.get('symptom_vomiting') == 1: symptoms.append('Vomiting')
        if row.get('symptom_diarrhea') == 1: symptoms.append('Diarrhea')
        symptoms_str = ", ".join(symptoms) if symptoms else 'None'
        
        new_report = PatientReport(
            patient_name=f"Patient_{row['village_id']}_{index}",
            gender=random.choice(['Male', 'Female']),
            village=row['village_id'],
            age=parse_age(row['age_group']),
            symptoms=symptoms_str,
            # --- CHANGED: Use random.choice for more variety ---
            suspected_disease='Cholera' if row['confirmed_outbreak'] == 1 else random.choice(DISEASE_LIST)
        )
        db.session.add(new_report)

    db.session.commit()
    print("Data import completed successfully!")

if __name__ == '__main__':
    with app.app_context():
        import_excel_data()