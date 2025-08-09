#!/usr/bin/env python3
"""
Demo Data Generator for Student Health Monitoring System
This script creates sample student health records for demonstration purposes
"""

import json
from datetime import datetime, timedelta
import random

# Sample student names
student_names = [
    "Aarav Patel", "Zara Khan", "Arjun Singh", "Aisha Rahman",
    "Vihaan Sharma", "Maya Gupta", "Reyansh Verma", "Anaya Joshi",
    "Advait Kumar", "Kiara Malhotra", "Dhruv Reddy", "Pari Nair",
    "Ishaan Iyer", "Avni Kapoor", "Krish Mehta", "Riya Saxena"
]

# Sample symptoms for different diseases
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

def generate_phone():
    """Generate a random 10-digit phone number"""
    return f"9{random.randint(100000000, 999999999)}"

def generate_admission_date():
    """Generate a random admission date within the last 2 years"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years ago
    random_days = random.randint(0, (end_date - start_date).days)
    return (start_date + timedelta(days=random_days)).strftime('%Y-%m-%d')

def generate_symptoms(disease):
    """Generate symptoms for a given disease with some variation"""
    base_symptoms = disease_symptoms[disease]
    # Randomly select 70-100% of symptoms
    num_symptoms = random.randint(int(len(base_symptoms) * 0.7), len(base_symptoms))
    selected_symptoms = random.sample(base_symptoms, num_symptoms)
    
    # Sometimes add a random symptom (realistic scenario)
    if random.random() < 0.3:
        all_symptoms = list(disease_symptoms.keys())
        random_disease = random.choice(all_symptoms)
        random_symptom = random.choice(disease_symptoms[random_disease])
        if random_symptom not in selected_symptoms:
            selected_symptoms.append(random_symptom)
    
    return selected_symptoms

def generate_confidence(disease, symptoms):
    """Generate realistic confidence scores"""
    base_symptoms = disease_symptoms[disease]
    matching_symptoms = len(set(symptoms) & set(base_symptoms))
    total_symptoms = len(base_symptoms)
    
    # Base confidence based on symptom match
    base_confidence = matching_symptoms / total_symptoms
    
    # Add some randomness for realism
    variation = random.uniform(-0.1, 0.1)
    confidence = max(0.1, min(0.95, base_confidence + variation))
    
    return round(confidence, 3)

def generate_demo_records(num_records=20):
    """Generate demo student health records"""
    records = []
    
    for i in range(num_records):
        # Randomly select a disease
        disease = random.choice(list(disease_symptoms.keys()))
        
        # Generate symptoms for this disease
        symptoms = generate_symptoms(disease)
        
        # Generate confidence
        confidence = generate_confidence(disease, symptoms)
        
        # Determine status
        status = 'Good' if disease == 'Common Cold' and confidence < 0.5 else 'Requires Attention'
        
        # Create record
        record = {
            'id': i + 1,
            'name': random.choice(student_names),
            'phone': generate_phone(),
            'admission_date': generate_admission_date(),
            'symptoms': symptoms,
            'disease': disease,
            'confidence': confidence,
            'status': status,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        records.append(record)
    
    return records

def save_demo_data(records, filename='demo_students.json'):
    """Save demo data to JSON file"""
    demo_data = {
        'generated_at': datetime.now().isoformat(),
        'total_records': len(records),
        'students': records
    }
    
    with open(filename, 'w') as f:
        json.dump(demo_data, f, indent=2)
    
    print(f"✅ Demo data saved to {filename}")
    print(f"📊 Generated {len(records)} student health records")

def display_sample_records(records, num_samples=5):
    """Display sample records for verification"""
    print(f"\n📋 Sample Records (showing {min(num_samples, len(records))}):")
    print("-" * 80)
    
    for i, record in enumerate(records[:num_samples]):
        print(f"Record {i+1}:")
        print(f"  Name: {record['name']}")
        print(f"  Disease: {record['disease']}")
        print(f"  Symptoms: {', '.join(record['symptoms'])}")
        print(f"  Confidence: {record['confidence']:.1%}")
        print(f"  Status: {record['status']}")
        print()

def main():
    """Main function to generate and save demo data"""
    print("🏥 STUDENT HEALTH MONITORING SYSTEM")
    print("🎭 Demo Data Generator")
    print("=" * 50)
    
    # Generate demo records
    print("Generating demo student health records...")
    records = generate_demo_records(20)
    
    # Display sample records
    display_sample_records(records)
    
    # Save to file
    save_demo_data(records)
    
    print("\n🚀 Demo data generation completed!")
    print("You can now:")
    print("1. Run the web application: python app.py")
    print("2. Import demo data manually or use the generated JSON file")
    print("3. Test the ML model with realistic data")

if __name__ == "__main__":
    main()
