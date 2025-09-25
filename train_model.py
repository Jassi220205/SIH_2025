import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

def train():
    """Reads the dataset, trains a model on all symptom columns, and saves it."""
    
    try:
        df = pd.read_csv('dataset.csv')
    except FileNotFoundError:
        print("Error: dataset.csv not found.")
        return
    print(f"Dataset loaded with {len(df)} rows.")

    # --- CHANGED: Automatically finds ALL symptom columns ---
    symptom_columns = [col for col in df.columns if 'symptom_' in col]
    print(f"Training model on {len(symptom_columns)} symptoms.")
    # --------------------------------------------------------

    X = df[symptom_columns]
    y = df['confirmed_outbreak']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=1000) # Increased max_iter for more complex data
    model.fit(X_train, y_train)
    print("Model training complete.")

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"New Model Accuracy: {accuracy * 100:.2f}%")

    joblib.dump(model, 'outbreak_model.pkl')
    print("New, more realistic model saved as 'outbreak_model.pkl'")


if __name__ == '__main__':
    train()