import pandas as pd
import random

def generate_data(rows=1000):
    """Creates a more realistic, patterned dataset for training."""
    data = []
    
    # --- NEW: Expanded list of symptoms ---
    all_symptoms = [
        'symptom_diarrhea', 'symptom_vomiting', 'symptom_fever', 
        'symptom_headache', 'symptom_fatigue', 'symptom_nausea', 
        'symptom_abdominal_cramps'
    ]
    
    for i in range(rows):
        village = f"V00{random.randint(1, 5)}"
        age_group = random.choice(['19-40', '41-60', '60+', 'Jun-18', '0-5'])
        
        # Randomly select a number of symptoms to be present
        num_symptoms = random.randint(0, len(all_symptoms))
        symptoms_present = random.sample(all_symptoms, num_symptoms)
        
        # Create a dictionary for all symptom columns, initialized to 0
        symptoms = {col: 0 for col in all_symptoms}
        for sym in symptoms_present:
            symptoms[sym] = 1
            
        # --- NEW: More complex rule for outbreaks ---
        # Base the outbreak chance on the number and type of symptoms
        score = 0
        if symptoms['symptom_diarrhea'] == 1: score += 3
        if symptoms['symptom_vomiting'] == 1: score += 3
        if symptoms['symptom_fever'] == 1: score += 2
        if symptoms['symptom_nausea'] == 1: score += 1
        if symptoms['symptom_abdominal_cramps'] == 1: score += 1
        
        # Higher score = higher chance of outbreak
        outbreak_chance = score / 15  # Max possible score is 10, making it more sensitive
        confirmed_outbreak = 1 if random.random() < outbreak_chance else 0
        
        row = {
            'village_id': village,
            'age_group': age_group,
            **symptoms,
            'confirmed_outbreak': confirmed_outbreak
        }
        data.append(row)
        
    df = pd.DataFrame(data)
    
    # Ensure a consistent column order
    final_cols = ['village_id', 'age_group'] + all_symptoms + ['confirmed_outbreak']
    df = df[final_cols]
    
    df.to_csv('dataset.csv', index=False)
    print(f"New realistic 'dataset.csv' created successfully with {rows} rows.")

if __name__ == '__main__':
    generate_data()