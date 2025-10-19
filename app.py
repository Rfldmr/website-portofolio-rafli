from flask import Flask, render_template, json, request, redirect, send_from_directory, jsonify, session
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

import nltk
# Set NLTK data path for hosting
nltk_data_path = os.path.join(os.path.dirname(__file__), 'nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# NLTK downloads with error handling
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', download_dir=nltk_data_path)
    except Exception as e:
        print(f"Failed to download punkt: {e}")

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    try:
        nltk.download('wordnet', download_dir=nltk_data_path)
    except Exception as e:
        print(f"Failed to download wordnet: {e}")

from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import random

# Try to import tensorflow, fallback if not available
try:
    from tensorflow import keras
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("TensorFlow not available, chatbot will be disabled")

app = Flask(__name__)

# Simple config instead of external file
class Config:
    SECRET_KEY = 'your-secret-key-here'
    DEBUG = False

app.config.from_object(Config)

# Load data functions
def load_experience():
    try:
        with open('data/experience.json', 'r') as f:
            return json.load(f)['experience']
    except Exception as e:
        print(f"Error loading experience: {e}")
        return []

def load_education():
    try:
        with open('data/education.json', 'r') as f:
            return json.load(f)['education']
    except Exception as e:
        print(f"Error loading education: {e}")
        return []

def load_certifications():
    try:
        with open('data/certifications.json', 'r') as f:
            return json.load(f)['certifications']
    except Exception as e:
        print(f"Error loading certifications: {e}")
        return []

def load_projects():
    try:
        with open('data/projects.json', 'r') as f:
            return json.load(f)['projects']
    except Exception as e:
        print(f"Error loading projects: {e}")
        return []

def get_project(project_id):
    projects = load_projects()
    for project in projects:
        if project['id'] == project_id:
            return project
    return None

# Initialize chatbot components with error handling
lemmatizer = None
model = None
intents = None
words = []
classes = []

if TF_AVAILABLE:
    try:
        lemmatizer = WordNetLemmatizer()
        
        # Load model with path checking
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'chatbot_brmp_model.h5')
        if os.path.exists(model_path):
            model = keras.models.load_model(model_path)
        else:
            print(f"Model file not found: {model_path}")
        
        # Load intents
        intents_path = os.path.join(os.path.dirname(__file__), 'intents.json')
        if os.path.exists(intents_path):
            with open(intents_path, 'r', encoding='utf-8') as f:
                intents = json.load(f)
        
        # Load pickle files
        words_path = os.path.join(os.path.dirname(__file__), 'model', 'words.pkl')
        classes_path = os.path.join(os.path.dirname(__file__), 'model', 'classes.pkl')
        
        if os.path.exists(words_path):
            words = pickle.load(open(words_path, 'rb'))
        if os.path.exists(classes_path):
            classes = pickle.load(open(classes_path, 'rb'))
            
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        model = None

def clean_up_sentence(sentence):
    if not lemmatizer:
        return sentence.lower().split()
    
    try:
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words
    except Exception as e:
        print(f"Error in clean_up_sentence: {e}")
        return sentence.lower().split()

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    for sw in sentence_words:
        for i, word in enumerate(words):
            if word == sw:
                bag[i] = 1
    return bag

def predict_class(sentence):
    if not model or not words:
        return []
    
    try:
        p = bag_of_words(sentence, words)
        res = model.predict(np.expand_dims(p, axis=0))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return results
    except Exception as e:
        print(f"Error in predict_class: {e}")
        return []

def getResponse(ints, intents_json):
    if not ints or not intents_json or not classes:
        return "Maaf, chatbot sedang dalam maintenance. Silakan hubungi langsung melalui kontak yang tersedia."
    
    try:
        tag = classes[ints[0][0]]
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                return result
        return "Maaf, aku tidak menemukan jawaban untuk itu."
    except Exception as e:
        print(f"Error in getResponse: {e}")
        return "Maaf, terjadi kesalahan sistem."

# Routes
@app.route('/')
def index():
    experience = load_experience()
    education = load_education()
    certifications = load_certifications()
    projects = load_projects()[:3]
    
    return render_template('index.html',
                         experience=experience, 
                         education=education, 
                         certifications=certifications,
                         projects=projects)

@app.route('/projects')
def projects():
    projects = load_projects()
    return render_template('projects.html', projects=projects)

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = get_project(project_id)
    if project:
        return render_template('project-detail.html', project=project)
    return redirect('/projects')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        # Check if chatbot is available
        if not model or not TF_AVAILABLE:
            return jsonify({
                'response': 'Maaf, fitur chatbot sedang dalam maintenance. Silakan hubungi saya melalui email atau LinkedIn yang tersedia di halaman kontak.'
            })
        
        data = request.get_json()
        if not data:
            return jsonify({'response': 'Invalid request format.'}), 400
            
        prompt = data.get('message', '').strip()
        if not prompt:
            return jsonify({'response': 'Pesan tidak boleh kosong.'}), 400
        
        ints = predict_class(prompt)
        response = getResponse(ints, intents)
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        return jsonify({
            'response': 'Maaf, terjadi kesalahan sistem. Silakan coba lagi atau hubungi langsung melalui kontak yang tersedia.'
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
