from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os
from config import Config
from database import db_manager
from ml_model import DiseasePredictor

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database connection
@app.before_first_request
def initialize_database():
    """Initialize database connection and create tables"""
    try:
        if db_manager.connect():
            db_manager.create_tables()
            print("Database initialized successfully")
        else:
            print("Failed to connect to database")
    except Exception as e:
        print(f"Database initialization error: {e}")

# Initialize ML model
ml_model = DiseasePredictor()

# Symptom database
symptom_database = {
    'fever': 'Fever',
    'cough': 'Cough', 
    'runny_nose': 'Runny Nose',
    'vomiting': 'Vomiting',
    'rash': 'Rash',
    'headache': 'Headache',
    'sore_throat': 'Sore Throat',
    'nausea': 'Nausea',
    'fatigue': 'Fatigue',
    'loss_of_appetite': 'Loss of Appetite',
    'body_ache': 'Body Ache',
    'diarrhea': 'Diarrhea',
    'dizziness': 'Dizziness',
    'chest_pain': 'Chest Pain',
    'shortness_of_breath': 'Shortness of Breath'
}

@app.route('/')
def index():
    """Main page"""
    try:
        # Get students from database
        students = db_manager.get_all_students()
        return render_template('index.html', 
                             symptom_database=symptom_database,
                             students=students)
    except Exception as e:
        print(f"Error loading index page: {e}")
        return render_template('index.html', 
                             symptom_database=symptom_database,
                             students=[])

@app.route('/add_student', methods=['POST'])
def add_student():
    """Add new student health record to database"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        admission_date = data.get('admission_date', '')
        symptoms = data.get('symptoms', [])
        
        # Validation
        if not name or not phone or not admission_date:
            return jsonify({'success': False, 'error': 'All fields are required'})
        
        if not symptoms:
            return jsonify({'success': False, 'error': 'At least one symptom is required'})
        
        # Predict disease using ML
        disease, confidence = ml_model.predict_disease(symptoms)
        
        # Determine status
        status = 'Good' if disease == 'Unknown' else 'Requires Attention'
        
        # Create student record
        student_record = {
            'name': name,
            'phone': phone,
            'admission_date': admission_date,
            'symptoms': symptoms,
            'disease': disease,
            'confidence': float(confidence),
            'status': status
        }
        
        # Insert into database
        student_id = db_manager.insert_student(student_record)
        
        if student_id:
            # Add ID and timestamp to the record
            student_record['id'] = student_id
            student_record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({
                'success': True,
                'student': student_record,
                'message': 'Student health record added successfully to database'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to save to database'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_students')
def get_students():
    """Get all student records from database"""
    try:
        students = db_manager.get_all_students()
        return jsonify({'students': students})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """Delete a student record from database"""
    try:
        success = db_manager.delete_student(student_id)
        if success:
            return jsonify({'success': True, 'message': 'Student record deleted from database'})
        else:
            return jsonify({'success': False, 'error': 'Student record not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/predict_disease', methods=['POST'])
def predict_disease():
    """Predict disease for given symptoms"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        disease, confidence = ml_model.predict_disease(symptoms)
        
        return jsonify({
            'success': True,
            'prediction': {'disease': disease, 'confidence': confidence}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_data')
def export_data():
    """Export all data from database to JSON"""
    try:
        students = db_manager.get_all_students()
        training_data = db_manager.get_training_data()
        
        export_data = {
            'students': students,
            'training_data': training_data,
            'export_date': datetime.now().isoformat()
        }
        
        with open('exported_data.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return jsonify({
            'success': True, 
            'message': f'Data exported to exported_data.json ({len(students)} students, {len(training_data)} training examples)'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/train_model', methods=['POST'])
def train_model():
    """Train the ML model with user-provided training data"""
    try:
        data = request.get_json()
        training_data = data.get('training_data', [])
        
        if not training_data:
            return jsonify({'success': False, 'error': 'No training data provided'})
        
        # Store training data in database
        for example in training_data:
            symptoms = example['symptoms']
            disease = example['disease']
            db_manager.insert_training_data(symptoms, disease)
        
        # Retrain the model with new data
        success = ml_model.train_model()
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Model trained successfully with {len(training_data)} examples from database',
                'training_examples': len(training_data)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to train model'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_training_data')
def get_training_data():
    """Get all training data from database"""
    try:
        training_data = db_manager.get_training_data()
        return jsonify({'success': True, 'training_data': training_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_training_data', methods=['POST'])
def clear_training_data():
    """Clear all training data from database"""
    try:
        success = db_manager.clear_training_data()
        if success:
            # Retrain model with default data
            ml_model.train_model()
            return jsonify({'success': True, 'message': 'Training data cleared and model reset to default'})
        else:
            return jsonify({'success': False, 'error': 'Failed to clear training data'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint with database status"""
    try:
        db_stats = db_manager.get_database_stats()
        model_info = ml_model.get_model_info()
        
        return jsonify({
            'status': 'healthy',
            'database_connected': db_manager.connection and db_manager.connection.is_connected(),
            'database_stats': db_stats,
            'model_info': model_info,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/database_status')
def database_status():
    """Get detailed database status"""
    try:
        db_stats = db_manager.get_database_stats()
        return jsonify({
            'success': True,
            'database_stats': db_stats,
            'connection_status': 'connected' if db_manager.connection and db_manager.connection.is_connected() else 'disconnected'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Cleanup on shutdown
@app.teardown_appcontext
def close_db_connection(error):
    """Close database connection when app context ends"""
    db_manager.disconnect()

if __name__ == '__main__':
    print("Starting Student Health Monitoring System with MySQL...")
    print("Note: ML model will be trained with data from MySQL database")
    print("Access the web interface at: http://localhost:5000")
    
    # Initialize database connection
    if db_manager.connect():
        db_manager.create_tables()
        print("Database initialized successfully")
        
        # Train model with database data
        ml_model.train_model()
    else:
        print("Warning: Failed to connect to database. Some features may not work.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
