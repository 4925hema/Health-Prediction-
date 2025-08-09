from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
import json
from database import db_manager

class DiseasePredictor:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.diseases = []
        self.disease_symptoms = {
            'Common Cold': ['runny_nose', 'cough', 'sore_throat', 'fatigue'],
            'Flu': ['fever', 'cough', 'body_ache', 'fatigue', 'headache'],
            'Stomach Flu': ['nausea', 'vomiting', 'diarrhea', 'fever', 'loss_of_appetite'],
            'Migraine': ['headache', 'nausea', 'dizziness'],
            'Tonsillitis': ['sore_throat', 'fever', 'headache', 'loss_of_appetite'],
            'Chickenpox': ['rash', 'fever', 'fatigue', 'loss_of_appetite'],
            'Pneumonia': ['cough', 'fever', 'shortness_of_breath', 'chest_pain', 'fatigue'],
            'Allergic Reaction': ['rash', 'runny_nose', 'shortness_of_breath']
        }
    
    def load_training_data_from_db(self):
        """Load training data from database"""
        try:
            training_data = db_manager.get_training_data()
            if training_data:
                return training_data
            else:
                # Fallback to default training data if database is empty
                return self._get_default_training_data()
        except Exception as e:
            print(f"Error loading training data from database: {e}")
            return self._get_default_training_data()
    
    def _get_default_training_data(self):
        """Get default training data when database is empty"""
        return [
            {'symptoms': ['fever', 'cough', 'body_ache'], 'disease': 'Flu'},
            {'symptoms': ['runny_nose', 'cough', 'sore_throat'], 'disease': 'Common Cold'},
            {'symptoms': ['nausea', 'vomiting', 'diarrhea'], 'disease': 'Stomach Flu'},
            {'symptoms': ['headache', 'nausea', 'dizziness'], 'disease': 'Migraine'},
            {'symptoms': ['sore_throat', 'fever', 'headache'], 'disease': 'Tonsillitis'},
            {'symptoms': ['rash', 'fever', 'fatigue'], 'disease': 'Chickenpox'},
            {'symptoms': ['cough', 'fever', 'shortness_of_breath'], 'disease': 'Pneumonia'},
            {'symptoms': ['rash', 'runny_nose', 'shortness_of_breath'], 'disease': 'Allergic Reaction'}
        ]
    
    def prepare_training_data(self, training_data):
        """Convert training data to text format for TF-IDF"""
        X = []
        y = []
        
        for item in training_data:
            symptoms = item['symptoms']
            disease = item['disease']
            
            # Convert symptoms list to text
            symptom_text = ' '.join(symptoms)
            X.append(symptom_text)
            y.append(disease)
        
        return X, y
    
    def train_model(self, custom_training_data=None):
        """Train the ML model using TF-IDF and Naive Bayes"""
        try:
            # Use custom training data if provided, otherwise load from database
            if custom_training_data:
                training_data = custom_training_data
            else:
                training_data = self.load_training_data_from_db()
            
            if not training_data:
                print("No training data available")
                return False
            
            X, y = self.prepare_training_data(training_data)
            
            # Update diseases list
            self.diseases = list(set(y))
            
            # Create pipeline with TF-IDF vectorizer and Naive Bayes classifier
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(lowercase=True, stop_words='english')),
                ('clf', MultinomialNB())
            ])
            
            # Train the model
            self.model.fit(X, y)
            print(f"ML Model trained successfully with {len(training_data)} examples!")
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def predict_disease(self, symptoms):
        """Predict disease based on symptoms"""
        if not symptoms:
            return "Unknown", 0.0
        
        # Convert symptoms list to text for TF-IDF
        symptoms_text = ' '.join(symptoms)
        
        try:
            # Try ML prediction first
            if self.model is not None:
                prediction = self.model.predict([symptoms_text])[0]
                confidence = self.model.predict_proba([symptoms_text]).max()
                return prediction, confidence
        except Exception as e:
            print(f"ML prediction failed: {e}")
        
        # Fallback to rule-based prediction
        return self._rule_based_prediction(symptoms)
    
    def _rule_based_prediction(self, symptoms):
        """Rule-based disease prediction as fallback"""
        best_match = None
        best_score = 0
        
        for disease, disease_symptoms in self.disease_symptoms.items():
            # Calculate similarity score
            common_symptoms = set(symptoms) & set(disease_symptoms)
            if common_symptoms:
                score = len(common_symptoms) / len(disease_symptoms)
                if score > best_score:
                    best_score = score
                    best_match = disease
        
        if best_match and best_score > 0.3:
            return best_match, best_score
        else:
            return "Unknown", 0.0
    
    def save_model(self, filename='disease_model.pkl'):
        """Save the trained model"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"Model saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, filename='disease_model.pkl'):
        """Load a saved model"""
        try:
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"Model loaded from {filename}")
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_model_info(self):
        """Get information about the current model"""
        return {
            'model_loaded': self.model is not None,
            'diseases_count': len(self.diseases),
            'diseases': self.diseases,
            'training_data_source': 'database' if self.model else 'none'
        }
