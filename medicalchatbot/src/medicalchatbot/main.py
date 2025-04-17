#!/usr/bin/env python3
import sys
import warnings
from datetime import datetime
from medicalchatbot.crew import Medicalchatbot
from dotenv import load_dotenv
load_dotenv()
import os

# Ignorer les avertissements de syntaxe potentiellement inutiles
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    try:
        topic = input("Entrez votre question médicale : ")
        
        inputs = {
            'topic': topic,
            'current_year': str(datetime.now().year)
        }

        # Lancer l'exécution
        result = Medicalchatbot().crew().kickoff(inputs=inputs)
        print(f"\nRÉPONSE : {result}\n")
        
    except Exception as e:
        print(f"[ERREUR] Échec de l'exécution : {e}")

def train():
    """
    Entraîne l'assistant pharmaceutique pour un nombre d'itérations spécifié et enregistre la sortie dans un fichier.
    Utilisation : python main.py train <n_iterations> <filename>
    """
    if len(sys.argv) < 4:
        print("Usage : python main.py train <n_iterations> <filename>")
        return

    try:
        n_iterations = int(sys.argv[2])
        filename = sys.argv[3]
        # Demander une question au lieu de la statique
        topic = input("Entrez la question pour l'entraînement : ")
        
        inputs = {
            "topic": topic  # Question saisie par l'utilisateur
        }
        Medicalchatbot().crew().train(n_iterations=n_iterations, filename=filename, inputs=inputs)
    except Exception as e:
        print(f"[ERREUR] Échec de l'entraînement de l'assistant : {e}")

def replay():
    """
    Rejoue l'exécution de l'assistant à partir d'une tâche spécifique.
    Utilisation : python main.py replay <task_id>
    """
    if len(sys.argv) < 3:
        print("Usage : python main.py replay <task_id>")
        return

    try:
        task_id = sys.argv[2]
        Medicalchatbot().crew().replay(task_id=task_id)
    except Exception as e:
        print(f"[ERREUR] Échec de la lecture de l'exécution de l'assistant : {e}")

def test():
    """
    Teste l'exécution de l'assistant et renvoie les résultats.
    Utilisation : python main.py test <n_iterations> <openai_model_name>
    """
    if len(sys.argv) < 4:
        print("Usage : python main.py test <n_iterations> <openai_model_name>")
        return

    try:
        n_iterations = int(sys.argv[2])
        model_name = sys.argv[3]
        # Demander une question pour les tests
        topic = input("Entrez la question pour le test : ")
        
        inputs = {
            "topic": topic,  # Question saisie par l'utilisateur
            "current_year": str(datetime.now().year)
        }
        Medicalchatbot().crew().test(n_iterations=n_iterations, openai_model_name=model_name, inputs=inputs)
    except Exception as e:
        print(f"[ERREUR] Échec du test de l'assistant : {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python main.py [run|train|test|replay] <args...>")
    else:
        command = sys.argv[1].lower()
        if command == "run":
            run()
        elif command == "train":
            train()
        elif command == "replay":
            replay()
        elif command == "test":
            test()
        else:
            print(f"[ERREUR] Commande inconnue '{command}'. Utilisez 'run', 'train', 'test' ou 'replay'.")
