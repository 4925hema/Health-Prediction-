#!/usr/bin/env python3
"""
Test script for the ML Disease Prediction Model
This script demonstrates how the model works without running the web application
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

# Disease definitions with symptoms
disease_symptoms = {
    'Common Cold': ['runny_nose', 'cough', 'sore_throat', 'fatigue'],
    'Flu': ['fever', 'cough', 'body_ache', 'fatigue', 'headache'],
    'Stomach Flu': ['nausea', 'vomiting', 'diarrhea', 'fever', 'loss_of_appetite'],
    'Migraine': ['headache', 'nausea', 'dizziness'],
    'Tonsillitis': ['sore_throat', 'fever', 'headache', 'loss_of_appetite'],
    'Chickenpox': ['rash', 'fever', 'fatigue', 'loss_of_appetite'],
    'Pneumonia': ['cough', 'fever', 'shortness_of_breath', 'chest_pain', 'fatigue'],
    'Allergic Reaction': ['rash', 'runny_nose', 'shortness_of_breath']
}

# Training data for ML model
training_data = [
    (['fever', 'cough', 'body_ache'], 'Flu'),
    (['runny_nose', 'cough', 'sore_throat'], 'Common Cold'),
    (['nausea', 'vomiting', 'diarrhea'], 'Stomach Flu'),
    (['headache', 'nausea', 'dizziness'], 'Migraine'),
    (['sore_throat', 'fever', 'headache'], 'Tonsillitis'),
    (['rash', 'fever', 'fatigue'], 'Chickenpox'),
    (['cough', 'fever', 'shortness_of_breath'], 'Pneumonia'),
    (['rash', 'runny_nose', 'shortness_of_breath'], 'Allergic Reaction'),
    # Add more training examples
    (['fever', 'cough', 'fatigue'], 'Flu'),
    (['runny_nose', 'sore_throat'], 'Common Cold'),
    (['nausea', 'vomiting'], 'Stomach Flu'),
    (['headache', 'dizziness'], 'Migraine'),
    (['fever', 'rash'], 'Chickenpox'),
    (['cough', 'chest_pain'], 'Pneumonia'),
    (['rash', 'runny_nose'], 'Allergic Reaction'),
    # Additional variations
    (['fever', 'cough', 'headache'], 'Flu'),
    (['cough', 'sore_throat'], 'Common Cold'),
    (['diarrhea', 'fever'], 'Stomach Flu'),
    (['headache', 'nausea'], 'Migraine'),
    (['fever', 'fatigue'], 'Flu'),
    (['runny_nose', 'cough'], 'Common Cold')
]

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.diseases = list(disease_symptoms.keys())
        self.train_model()
    
    def prepare_training_data(self):
        """Convert training data to text format for TF-IDF"""
        X = []
        y = []
        
        for symptoms, disease in training_data:
            # Convert symptoms list to text
            symptom_text = ' '.join(symptoms)
            X.append(symptom_text)
            y.append(disease)
        
        return X, y
    
    def train_model(self):
        """Train the ML model using TF-IDF and Naive Bayes"""
        X, y = self.prepare_training_data()
        
        # Create pipeline with TF-IDF vectorizer and Naive Bayes classifier
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english')),
            ('clf', MultinomialNB())
        ])
        
        # Train the model
        self.model.fit(X, y)
        print("✅ ML Model trained successfully!")
        print(f"📊 Training examples: {len(training_data)}")
        print(f"🏥 Supported diseases: {len(disease_symptoms)}")
    
    def predict_disease(self, symptoms):
        """Predict disease based on symptoms"""
        if not symptoms:
            return {'disease': 'Healthy', 'confidence': 1.0}
        
        # Convert symptoms to text
        symptom_text = ' '.join(symptoms)
        
        try:
            # Get prediction probabilities
            proba = self.model.predict_proba([symptom_text])[0]
            predicted_class = self.model.predict([symptom_text])[0]
            
            # Get confidence (highest probability)
            confidence = np.max(proba)
            
            # If confidence is too low, use rule-based approach
            if confidence < 0.3:
                return self.rule_based_prediction(symptoms)
            
            return {
                'disease': predicted_class,
                'confidence': float(confidence)
            }
            
        except Exception as e:
            print(f"⚠️ ML prediction error: {e}")
            return self.rule_based_prediction(symptoms)
    
    def rule_based_prediction(self, symptoms):
        """Fallback rule-based prediction"""
        best_match = {'disease': 'Unknown', 'confidence': 0.0}
        
        for disease, disease_symptom_list in disease_symptoms.items():
            matching_symptoms = len(set(symptoms) & set(disease_symptom_list))
            
            if matching_symptoms > 0:
                confidence = matching_symptoms / len(disease_symptom_list)
                if confidence > best_match['confidence']:
                    best_match = {'disease': disease, 'confidence': confidence}
        
        return best_match
    
    def save_model(self, filename='disease_model.pkl'):
        """Save the trained model"""
        with open(filename, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"💾 Model saved to {filename}")
    
    def load_model(self, filename='disease_model.pkl'):
        """Load a saved model"""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.model = pickle.load(f)
            print(f"📥 Model loaded from {filename}")
            return True
        return False

def test_predictions():
    """Test the model with various symptom combinations"""
    print("\n" + "="*60)
    print("🧪 TESTING DISEASE PREDICTIONS")
    print("="*60)
    
    # Initialize predictor
    predictor = DiseasePredictor()
    
    # Test cases
    test_cases = [
        ['fever', 'cough', 'body_ache'],
        ['runny_nose', 'cough', 'sore_throat'],
        ['nausea', 'vomiting', 'diarrhea'],
        ['headache', 'nausea', 'dizziness'],
        ['rash', 'fever', 'fatigue'],
        ['cough', 'fever', 'shortness_of_breath'],
        ['fever', 'cough'],  # Partial symptoms
        ['headache'],  # Single symptom
        ['unknown_symptom'],  # Unknown symptom
        []  # No symptoms
    ]
    
    for i, symptoms in enumerate(test_cases, 1):
        prediction = predictor.predict_disease(symptoms)
        
        print(f"\n🔍 Test Case {i}:")
        print(f"   Symptoms: {symptoms if symptoms else 'None'}")
        print(f"   Prediction: {prediction['disease']}")
        print(f"   Confidence: {prediction['confidence']:.2%}")
        
        # Show matching symptoms for known diseases
        if prediction['disease'] != 'Unknown' and prediction['disease'] != 'Healthy':
            disease_symptom_list = disease_symptoms.get(prediction['disease'], [])
            matching = set(symptoms) & set(disease_symptom_list)
            print(f"   Matching symptoms: {list(matching)}")
    
    # Save the model
    predictor.save_model()
    
    print("\n" + "="*60)
    print("✅ Testing completed successfully!")
    print("="*60)

def show_model_info():
    """Display information about the model and training data"""
    print("\n📋 MODEL INFORMATION")
    print("-" * 40)
    
    print(f"🏥 Supported Diseases ({len(disease_symptoms)}):")
    for disease, symptoms in disease_symptoms.items():
        print(f"   • {disease}: {', '.join(symptoms)}")
    
    print(f"\n📚 Training Examples ({len(training_data)}):")
    for symptoms, disease in training_data[:5]:  # Show first 5
        print(f"   • {disease}: {', '.join(symptoms)}")
    if len(training_data) > 5:
        print(f"   ... and {len(training_data) - 5} more examples")

if __name__ == "__main__":
    print("🏥 STUDENT HEALTH MONITORING SYSTEM")
    print("🤖 ML Disease Prediction Model Test")
    print("=" * 60)
    
    # Show model information
    show_model_info()
    
    # Test predictions
    test_predictions()
    
    print("\n🚀 Ready to run the web application!")
    print("   Run: python app.py")
    print("   Then visit: http://localhost:5000")
