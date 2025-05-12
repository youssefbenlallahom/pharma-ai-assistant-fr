from flask import Flask, render_template, request, jsonify
from medicalchatbot.crew import Medicalchatbot
import threading
import base64
import cv2
import numpy as np
import easyocr
import tensorflow as tf
import re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import uuid
import os

app = Flask(__name__)
# Configuration pour la compression des réponses
app.config['COMPRESS_ALGORITHM'] = 'gzip'
app.config['COMPRESS_LEVEL'] = 6

# Variables globales pour les modèles et ressources partagées
cnn_model = None
reader = None
crew = None
models_initialized = False
initialization_lock = threading.Lock()
response_cache = {}  # Cache simple pour les réponses
max_workers = 4  # Nombre maximum de workers pour le pool de threads
executor = ThreadPoolExecutor(max_workers=max_workers)

def initialize_crew():
    global crew
    if crew is None:
        crew = Medicalchatbot().crew()
    return crew

def initialize_cnn_model():
    global cnn_model
    if cnn_model is None:
        try:
            # Utiliser un chemin relatif pour le modèle
            model_path = os.path.join(os.path.dirname(__file__), "ocr", "CustomCNN_model.keras")
            if os.path.exists(model_path):
                cnn_model = tf.keras.models.load_model(model_path)
            else:
                print(f"Modèle non trouvé à {model_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du modèle CNN: {str(e)}")
            print("Utilisation du mode de secours")
    return cnn_model

def initialize_ocr():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en', 'fr'], gpu=False)
    return reader

def initialize_models():
    global models_initialized
    
    with initialization_lock:
        if not models_initialized:
            try:
                # Initialisation minimale au démarrage
                initialize_crew()
                models_initialized = True
                print("Initialisation de base terminée avec succès")
                
                # Lancement de l'initialisation des modèles lourds en arrière-plan
                executor.submit(initialize_cnn_model)
                
                # Note: OCR sera initialisé à la demande
            except Exception as e:
                print(f"Erreur lors de l'initialisation: {str(e)}")
                raise

# Créez un thread pour l'initialisation de base
initialization_thread = threading.Thread(target=initialize_models)
initialization_thread.daemon = True
initialization_thread.start()

@app.route('/')
def home():
    return render_template('index.html')

# Fonction de cache pour les questions fréquentes
@lru_cache(maxsize=100)
def get_cached_response(question):
    # Normalisation de la question pour améliorer les chances de hit du cache
    normalized_question = question.lower().strip()
    return response_cache.get(normalized_question)

@app.route('/ask', methods=['POST'])
def ask_question():
    global models_initialized
    
    if not models_initialized:
        return jsonify({
            'error': 'Les modèles sont en cours d\'initialisation. Veuillez réessayer dans quelques instants.',
            'response': 'Désolé, les modèles sont en cours de chargement. Veuillez patienter quelques secondes et réessayer.'
        }), 503
    
    data = request.json
    question = data['question']
    
    # Vérifier si la réponse est en cache
    cached_result = get_cached_response(question)
    if cached_result:
        return jsonify(cached_result)

    try:
        # Utilisation d'une variable en mémoire au lieu d'un fichier
        response_text = None
        
        def run_crew():
            nonlocal response_text
            crew = initialize_crew()
            result = crew.kickoff(inputs={
                'question': question,
                'topic': question
            })
            
            # Debug et extraction améliorée
            print(f"Type of result: {type(result)}")
            
            try:
                # Dans les versions récentes de CrewAI, la sortie est souvent dans les artifacts
                if hasattr(result, "artifacts") and hasattr(result.artifacts, "values"):
                    # Récupérer la valeur du dernier artifact (généralement la réponse finale)
                    artifacts_values = list(result.artifacts.values())
                    if artifacts_values:
                        response_text = artifacts_values[-1]  # Prendre le dernier
                    else:
                        response_text = str(result)
                # Autres tentatives si la méthode ci-dessus échoue
                elif hasattr(result, "content"):
                    response_text = result.content
                elif hasattr(result, "raw_output"):
                    response_text = result.raw_output
                elif hasattr(result, "output"):
                    response_text = result.output
                else:
                    # Lecture directe du fichier généré comme fallback
                    try:
                        with open("reponse_finale.md", "r", encoding="utf-8") as f:
                            response_text = f.read()
                    except:
                        response_text = str(result)
            except Exception as e:
                print(f"Erreur lors de l'extraction de la réponse: {str(e)}")
                response_text = f"Une erreur est survenue: {str(e)}"

        # Soumission de la tâche au pool de threads au lieu de créer un nouveau thread
        future = executor.submit(run_crew)
        future.result()  # Attendre le résultat

        if response_text:
            result = {
                'response': response_text,
                'sources': [
                    "Vidal",
                    "BDPM",
                    "PasseportSanté"
                ]
            }
            
            # Mettre en cache la réponse pour les futures requêtes
            normalized_question = question.lower().strip()
            response_cache[normalized_question] = result
            
            return jsonify(result)
        else:
            return jsonify({
                'error': 'La génération de réponse a échoué',
                'response': 'Désolé, une erreur est survenue lors du traitement.'
            }), 500
    except Exception as e:
        print(f"Erreur dans ask_question: {str(e)}")
        return jsonify({
            'error': f'Erreur inattendue: {str(e)}',
            'response': 'Désolé, une erreur inattendue est survenue lors du traitement.'
        }), 500


@app.route('/analyze-medication', methods=['POST'])
def analyze_medication():
    global models_initialized
    
    if not models_initialized:
        return jsonify({
            'success': False, 
            'error': 'Les modèles sont en cours d\'initialisation. Veuillez réessayer dans quelques instants.'
        }), 503
    
    image_data = request.json.get('image', '')
    
    if not image_data:
        return jsonify({'success': False, 'error': 'Aucune image fournie'})
    
    try:
        # Initialiser OCR à la demande
        initialize_ocr()
        
        # Convertir l'image base64 en format OpenCV
        encoded_data = image_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Simplification du prétraitement de l'image selon le modèle Streamlit
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Utiliser EasyOCR pour détecter le texte
        results = reader.readtext(gray)
        
        predictions = []
        
        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            
            # Calcul simple de la zone de texte pour la confiance
            width = bottom_right[0] - top_left[0]
            height = bottom_right[1] - top_left[1]
            area = width * height
            
            # Approche simplifiée pour la confiance selon le modèle Streamlit
            confidence = min(0.5 + area / 10000, 0.99)
            
            predictions.append({
                "word": text,
                "bbox": (top_left, bottom_right),
                "confidence": confidence,
                "area": area
            })
        
        if predictions:
            # Trier par taille de zone (la plus grande en premier)
            predictions.sort(key=lambda x: x['area'], reverse=True)
            
            # Le texte avec la plus grande zone est le nom du médicament
            med_name = predictions[0]['word']
            
            # Tout le reste va dans la description
            other_texts = [p['word'] for p in predictions[1:]]
            med_desc = " ".join(other_texts) if other_texts else ""
            
            return jsonify({
                'success': True,
                'medication_name': med_name,
                'description': med_desc,
                'confidence': float(predictions[0]['confidence'])
            })
        else:
            return jsonify({'success': False, 'error': 'Aucun texte détecté sur l\'image. Veuillez réessayer avec une image plus claire.'})
    
    except Exception as e:
        print(f"Erreur dans analyze_medication: {str(e)}")
        return jsonify({'success': False, 'error': f'Une erreur est survenue: {str(e)}'})
    
@app.route('/status', methods=['GET'])
def check_status():
    return jsonify({
        'models_initialized': models_initialized,
        'ocr_initialized': reader is not None,
        'cnn_initialized': cnn_model is not None,
        'crew_initialized': crew is not None,
        'initialization_thread_alive': initialization_thread.is_alive(),
        'cache_size': len(response_cache)
    })

# Ajout d'une route pour vider le cache si nécessaire
@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    response_cache.clear()
    get_cached_response.cache_clear()
    return jsonify({'success': True, 'message': 'Cache vidé avec succès'})

# Add this route to serve the camera modal template
@app.route('/camera-modal')
def camera_modal():
    return render_template('camera.html')

# Add a special route for handling the submit action when no send button exists
@app.route('/submit-question', methods=['POST'])
def submit_question():
    """Endpoint pour traiter les questions soumises via Enter depuis le formulaire"""
    data = request.json
    if 'question' not in data:
        return jsonify({'error': 'Aucune question fournie'}), 400
    
    # Rediriger vers la fonction ask_question existante
    return ask_question()

if __name__ == '__main__':
    # En production, remplacez cette ligne par l'utilisation d'un serveur WSGI
    # comme Gunicorn
    app.run(debug=False, threaded=True)