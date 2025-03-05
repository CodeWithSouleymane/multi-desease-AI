import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def generate_sample_data(disease_name, n_samples=1000):
    """
    Generate sample data for training disease prediction models
    """
    np.random.seed(42)  # For reproducibility
    
    if disease_name.lower() == 'covid-19':
        # Features: population_density, vaccination_rate, avg_age, mobility_index, hospital_beds, testing_rate
        X = pd.DataFrame({
            'population_density': np.random.gamma(5, 2, n_samples),  # people per sq km
            'vaccination_rate': np.random.beta(5, 2, n_samples) * 100,  # percentage
            'avg_age': np.random.normal(40, 10, n_samples),  # years
            'mobility_index': np.random.beta(2, 2, n_samples) * 100,  # 0-100 scale
            'hospital_beds': np.random.gamma(3, 1, n_samples),  # per 1000 people
            'testing_rate': np.random.gamma(10, 3, n_samples)  # per 1000 people
        })
        
        # Generate target based on a simple rule
        # Higher risk with: high population density, low vaccination, high mobility, low hospital beds
        risk_score = (
            X['population_density'] / 50 +
            (100 - X['vaccination_rate']) / 20 +
            X['mobility_index'] / 25 -
            X['hospital_beds'] * 5
        ) / 20
        
    elif disease_name.lower() == 'influenza':
        # Features: temperature, humidity, flu_vaccination, school_density, prev_season_cases, public_transport_usage
        X = pd.DataFrame({
            'temperature': np.random.normal(15, 10, n_samples),  # Celsius
            'humidity': np.random.beta(5, 2, n_samples) * 100,  # percentage
            'flu_vaccination': np.random.beta(2, 3, n_samples) * 100,  # percentage
            'school_density': np.random.gamma(2, 1, n_samples),  # schools per sq km
            'prev_season_cases': np.random.gamma(500, 200, n_samples),  # number of cases
            'public_transport_usage': np.random.beta(3, 2, n_samples) * 100  # percentage
        })
        
        # Generate target based on a simple rule
        # Higher risk with: low temperature, low humidity, low vaccination, high school density, high transport usage
        risk_score = (
            (20 - X['temperature']) / 10 +
            (60 - X['humidity']) / 20 +
            (100 - X['flu_vaccination']) / 25 +
            X['school_density'] * 5 +
            X['public_transport_usage'] / 20
        ) / 20
        
    elif disease_name.lower() == 'dengue':
        # Features: rainfall, temperature_dengue, humidity_dengue, vegetation_index, standing_water, population_density_dengue
        X = pd.DataFrame({
            'rainfall': np.random.gamma(10, 5, n_samples),  # mm
            'temperature_dengue': np.random.normal(28, 5, n_samples),  # Celsius
            'humidity_dengue': np.random.beta(5, 2, n_samples) * 100,  # percentage
            'vegetation_index': np.random.beta(5, 2, n_samples),  # 0-1 scale
            'standing_water': np.random.beta(2, 5, n_samples),  # 0-1 scale
            'population_density_dengue': np.random.gamma(5, 2, n_samples)  # people per sq km
        })
        
        # Generate target based on a simple rule
        # Higher risk with: high rainfall, high temperature, high humidity, high standing water
        risk_score = (
            X['rainfall'] / 50 +
            (X['temperature_dengue'] - 20) / 5 +
            (X['humidity_dengue'] - 50) / 10 +
            X['standing_water'] * 5 +
            X['population_density_dengue'] / 50
        ) / 10
        
    elif disease_name.lower() == 'malaria':
        # Features: rainfall_malaria, temperature_malaria, humidity_malaria, mosquito_density, bednet_usage, antimalarial_access
        X = pd.DataFrame({
            'rainfall_malaria': np.random.gamma(10, 5, n_samples),  # mm
            'temperature_malaria': np.random.normal(28, 5, n_samples),  # Celsius
            'humidity_malaria': np.random.beta(5, 2, n_samples) * 100,  # percentage
            'mosquito_density': np.random.gamma(50, 20, n_samples),  # mosquitoes per sq km
            'bednet_usage': np.random.beta(2, 3, n_samples) * 100,  # percentage
            'antimalarial_access': np.random.beta(2, 3, n_samples) * 100  # percentage
        })
        
        # Generate target based on a simple rule
        # Higher risk with: high rainfall, high temperature, high humidity, high mosquito density, low bednet usage
        risk_score = (
            X['rainfall_malaria'] / 50 +
            (X['temperature_malaria'] - 20) / 5 +
            (X['humidity_malaria'] - 50) / 10 +
            X['mosquito_density'] / 100 -
            X['bednet_usage'] / 20 -
            X['antimalarial_access'] / 20
        ) / 10
    
    else:
        raise ValueError(f"Disease '{disease_name}' not supported")
    
    # Convert risk score to binary outcome with some randomness
    y = (risk_score + np.random.normal(0, 0.1, n_samples) > 0.5).astype(int)
    
    return X, y

def train_disease_model(disease_name, save_path=None):
    """
    Train a machine learning model for disease prediction
    """
    X, y = generate_sample_data(disease_name)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    if disease_name.lower() in ['covid-19', 'influenza']:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    print(f"Model for {disease_name}:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Save model and scaler
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({'model': model, 'scaler': scaler, 'features': X.columns.tolist()}, save_path)
        print(f"Model saved to {save_path}")
    
    return model, scaler, X.columns.tolist()

def predict_risk(model_path, input_data):
    """
    Make predictions using a trained model
    """
    # Load model, scaler, and feature list
    model_data = joblib.load(model_path)
    model = model_data['model']
    scaler = model_data['scaler']
    features = model_data['features']
    
    # Ensure input data has the correct features
    input_df = pd.DataFrame([input_data])
    for feature in features:
        if feature not in input_df.columns:
            input_df[feature] = 0  # Default value if feature is missing
    
    # Keep only the features used by the model
    input_df = input_df[features]
    
    # Scale the input data
    input_scaled = scaler.transform(input_df)
    
    # Make prediction
    risk_proba = model.predict_proba(input_scaled)[0][1]
    
    return risk_proba

def initialize_models(models_dir):
    """
    Initialize and save models for all supported diseases
    """
    os.makedirs(models_dir, exist_ok=True)
    
    diseases = ['COVID-19', 'Influenza', 'Dengue', 'Malaria']
    
    for disease in diseases:
        model_path = os.path.join(models_dir, f"{disease.lower().replace(' ', '_')}_model.pkl")
        if not os.path.exists(model_path):
            print(f"Training model for {disease}...")
            train_disease_model(disease, model_path)
        else:
            print(f"Model for {disease} already exists.")
    
    print("All models initialized successfully.")
