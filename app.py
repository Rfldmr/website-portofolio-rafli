from flask import Flask, render_template, json, request, redirect, send_from_directory, jsonify, session
import os

import nltk
# NLTK downloads (cukup dijalankan sekali saat pertama kali)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from tensorflow import keras
import random

app = Flask(__name__)
app.config.from_object('config.Config')

# Load data functions

def load_experience():
    with open('data/experience.json', 'r') as f:
        return json.load(f)['experience']

def load_education():
    with open('data/education.json', 'r') as f:
        return json.load(f)['education']

def load_certifications():
    with open('data/certifications.json', 'r') as f:
        return json.load(f)['certifications']

def load_projects():
    with open('data/projects.json', 'r') as f:
        return json.load(f)['projects']
    
def load_education():
    with open('data/education.json', 'r') as f:
        return json.load(f)['education']

def load_certifications():
    with open('data/certifications.json', 'r') as f:
        return json.load(f)['certifications']

def get_project(project_id):
    projects = load_projects()
    for project in projects:
        if project['id'] == project_id:
            return project
    return None

lemmatizer = WordNetLemmatizer()
model = keras.models.load_model('model/chatbot_brmp_model.h5')
intents = json.loads(open('intents.json', encoding='utf-8').read())
words = pickle.load(open('model/words.pkl','rb'))
classes = pickle.load(open('model/classes.pkl','rb'))

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    for sw in sentence_words:
        for i, word in enumerate(words):
            if word == sw:
                bag[i] = 1
    return bag

def predict_class(sentence):
    p = bag_of_words(sentence, words)
    res = model.predict(np.expand_dims(p, axis=0))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return results

def getResponse(ints, intents_json):
    if not ints:
        return "Maaf, aku belum dilatih untuk menjawab itu. Coba tanyakan hal lain tentang profil atau proyek Rafli."
    tag = classes[ints[0][0]]
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            return result
    return "Maaf, aku tidak menemukan jawaban untuk itu."

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

# --- ROUTES API CHATBOT (BARU) ---
@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    prompt = data.get('message', '')
    
    ints = predict_class(prompt)
    response = getResponse(ints, intents)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)