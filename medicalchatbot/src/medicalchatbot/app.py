# app.py
from flask import Flask, render_template, request, jsonify
from medicalchatbot.crew import Medicalchatbot
import threading

app = Flask(__name__)
crew = Medicalchatbot().crew()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json['question']
    
    def run_crew():
        # Ajoutez à la fois 'question' et 'topic' dans les inputs
        crew.kickoff(inputs={
            'question': question,
            'topic': question  # Utilisez la question comme topic
        })
    
    thread = threading.Thread(target=run_crew)
    thread.start()
    thread.join()
    
    try:
        with open('reponse_finale.md', 'r') as f:
            response = f.read()
        
        return jsonify({
            'response': response,
            'sources': [
                "Vidal",
                "BDPM",
                "PasseportSanté"
            ]
        })
    except FileNotFoundError:
        return jsonify({
            'error': 'La génération de réponse a échoué',
            'response': 'Désolé, une erreur est survenue lors du traitement.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)