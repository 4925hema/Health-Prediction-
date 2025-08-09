// Global variables
let symptomArray = [];
let studentId = 1;
let trainingData = [];

// ML Model - Simple Naive Bayes-like approach for disease prediction
class DiseasePredictor {
    constructor() {
        this.diseaseSymptoms = {
            'Common Cold': {
                symptoms: ['runny_nose', 'cough', 'sore_throat', 'fatigue'],
                weight: 0.8
            },
            'Flu': {
                symptoms: ['fever', 'cough', 'body_ache', 'fatigue', 'headache'],
                weight: 0.9
            },
            'Stomach Flu': {
                symptoms: ['nausea', 'vomiting', 'diarrhea', 'fever', 'loss_of_appetite'],
                weight: 0.85
            },
            'Migraine': {
                symptoms: ['headache', 'nausea', 'dizziness'],
                weight: 0.75
            },
            'Tonsillitis': {
                symptoms: ['sore_throat', 'fever', 'headache', 'loss_of_appetite'],
                weight: 0.8
            },
            'Chickenpox': {
                symptoms: ['rash', 'fever', 'fatigue', 'loss_of_appetite'],
                weight: 0.9
            },
            'Pneumonia': {
                symptoms: ['cough', 'fever', 'shortness_of_breath', 'chest_pain', 'fatigue'],
                weight: 0.95
            },
            'Allergic Reaction': {
                symptoms: ['rash', 'runny_nose', 'shortness_of_breath'],
                weight: 0.7
            }
        };
    }

    predictDisease(symptoms) {
        if (symptoms.length === 0) {
            return { disease: 'Healthy', confidence: 1.0 };
        }

        let bestMatch = { disease: 'Unknown', confidence: 0.0 };
        
        for (const [disease, data] of Object.entries(this.diseaseSymptoms)) {
            const matchingSymptoms = symptoms.filter(symptom => 
                data.symptoms.includes(symptom)
            ).length;
            
            if (matchingSymptoms > 0) {
                const confidence = (matchingSymptoms / data.symptoms.length) * data.weight;
                if (confidence > bestMatch.confidence) {
                    bestMatch = { disease, confidence: Math.min(confidence, 1.0) };
                }
            }
        }

        // If no good match found, try partial matches
        if (bestMatch.confidence < 0.3) {
            for (const [disease, data] of Object.entries(this.diseaseSymptoms)) {
                const partialMatches = symptoms.filter(symptom => 
                    data.symptoms.some(ds => ds.includes(symptom) || symptom.includes(ds))
                ).length;
                
                if (partialMatches > 0) {
                    const confidence = (partialMatches / Math.max(symptoms.length, data.symptoms.length)) * data.weight * 0.7;
                    if (confidence > bestMatch.confidence) {
                        bestMatch = { disease, confidence: Math.min(confidence, 1.0) };
                    }
                }
            }
        }

        return bestMatch;
    }

    // Train the model with new data
    trainModel(newData) {
        trainingData.push(newData);
        // In a real ML system, this would update the model weights
        console.log('Training data updated:', trainingData.length, 'records');
    }
}

// Initialize the ML model
const diseasePredictor = new DiseasePredictor();

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('admissionDate').value = today;

    // Add symptom button
    document.getElementById('addSymptoms').addEventListener('click', addSymptom);
    
    // Form submission
    document.getElementById('healthForm').addEventListener('submit', handleFormSubmit);
    
    // Remove symptom when clicked
    document.getElementById('symptomList').addEventListener('click', removeSymptom);
});

function addSymptom() {
    const symptomSelect = document.getElementById('symptomSelect');
    const selectedSymptom = symptomSelect.value;
    
    if (selectedSymptom && !symptomArray.includes(selectedSymptom)) {
        symptomArray.push(selectedSymptom);
        updateSymptomList();
        symptomSelect.value = '';
    }
}

function removeSymptom(e) {
    if (e.target.classList.contains('symptom-tag')) {
        const symptom = e.target.textContent;
        symptomArray = symptomArray.filter(s => s !== symptom);
        updateSymptomList();
    }
}

function updateSymptomList() {
    const listDiv = document.getElementById('symptomList');
    if (symptomArray.length === 0) {
        listDiv.innerHTML = '<p class="no-symptoms">No symptoms added yet</p>';
    } else {
        listDiv.innerHTML = symptomArray.map(s => 
            `<span class="symptom-tag" title="Click to remove">${s.replace(/_/g, ' ')}</span>`
        ).join('');
    }
}

function handleFormSubmit(e) {
    e.preventDefault();

    const name = document.getElementById('name').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const admissionDate = document.getElementById('admissionDate').value;
    
    if (!name || !phone || !admissionDate) {
        alert('Please fill in all required fields');
        return;
    }

    if (symptomArray.length === 0) {
        alert('Please add at least one symptom');
        return;
    }

    // Predict disease using ML
    const prediction = diseasePredictor.predictDisease(symptomArray);
    const status = prediction.disease === 'Healthy' ? 'Good' : 'Requires Attention';
    const timestamp = new Date().toLocaleString();

    // Add to table
    addToTable(name, phone, admissionDate, symptomArray, prediction, status, timestamp);

    // Train the model with this data
    diseasePredictor.trainModel({
        symptoms: symptomArray,
        disease: prediction.disease,
        confidence: prediction.confidence
    });

    // Reset form
    resetForm();
}

function addToTable(name, phone, admissionDate, symptoms, prediction, status, timestamp) {
    const table = document.getElementById('healthTable').querySelector('tbody');
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td>${studentId++}</td>
        <td>${name}</td>
        <td>${phone}</td>
        <td>${formatDate(admissionDate)}</td>
        <td>${symptoms.map(s => s.replace(/_/g, ' ')).join(', ')}</td>
        <td>${prediction.disease}</td>
        <td>${(prediction.confidence * 100).toFixed(1)}%</td>
        <td class="status-${status.toLowerCase().replace(' ', '-')}">${status}</td>
        <td>${timestamp}</td>
    `;
    
    table.appendChild(row);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function resetForm() {
    symptomArray = [];
    updateSymptomList();
    document.getElementById('healthForm').reset();
    document.getElementById('admissionDate').value = new Date().toISOString().split('T')[0];
}

// Initialize symptom list
updateSymptomList();
