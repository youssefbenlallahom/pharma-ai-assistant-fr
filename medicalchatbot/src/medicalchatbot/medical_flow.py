from langflow.interface.custom.custom_component import CustomComponent
from langflow import load_flow_from_json
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from litellm import completion
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration des outils
def setup_tools():
    return {
        "search_tool": SerperDevTool(country="fr", locale="fr", location="France"),
        "vidal_tool": ScrapeWebsiteTool(website="https://www.vidal.fr"),
        "bdpm_tool": ScrapeWebsiteTool(website="https://base-donnees-publique.medicaments.gouv.fr"),
        "doctissimo_tool": ScrapeWebsiteTool(website="https://www.doctissimo.fr"),
        "passeport_tool": ScrapeWebsiteTool(website="https://www.passeportsante.net"),
        "santefr_tool": ScrapeWebsiteTool(website="https://www.sante.fr")
    }

# Configuration des LLMs
def setup_llms():
    return {
        "groq_llm": completion(
            model="llama3-8b-8192",
            api_base="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            messages=[{"role": "system", "content": "Assistant médical expert"}]
        ),
        "ollama_llm": completion(
            model="ollama/mistral",
            api_base="http://localhost:11434",
            messages=[{"role": "system", "content": "Assistant médical expert"}]
        )
    }

class MedicalCrewAIComponent(CustomComponent):
    display_name = "Medical CrewAI"
    description = "Component for medical CrewAI workflow"
    
    def build_config(self):
        return {
            "user_query": {"display_name": "User Query", "info": "The medical question to answer"},
            "verbose": {"display_name": "Verbose", "field_type": "bool", "value": True}
        }
    
    def build(self, user_query: str, verbose: bool = True):
        # Initialisation
        tools = setup_tools()
        llms = setup_llms()
        
        # Création des agents
        data_miner = Agent(
            role="Expert en collecte de données médicales",
            goal="Trouver les informations médicales les plus pertinentes",
            backstory="Spécialiste de la recherche d'informations sur les sources médicales françaises fiables",
            tools=[tools["search_tool"], tools["vidal_tool"], tools["bdpm_tool"]],
            llm=llms["ollama_llm"],
            verbose=verbose
        )
        
        knowledge_engine = Agent(
            role="Expert en analyse médicale",
            goal="Analyser et synthétiser les informations médicales",
            backstory="Data scientist spécialisé dans le traitement des données de santé",
            tools=[tools["doctissimo_tool"], tools["passeport_tool"]],
            llm=llms["ollama_llm"],
            verbose=verbose
        )
        
        pharma_assistant = Agent(
            role="Assistant pharmaceutique",
            goal="Fournir des réponses claires et précises aux patients",
            backstory="Pharmacien expérimenté avec 10 ans d'expérience en officine",
            tools=[tools["santefr_tool"]],
            llm=llms["groq_llm"],
            verbose=verbose
        )
        
        # Création des tâches
        mining_task = Task(
            description=f"Recherche d'informations pour: {user_query}",
            agent=data_miner,
            expected_output="Données brutes pertinentes extraites des sources fiables"
        )
        
        analysis_task = Task(
            description="Analyse et synthèse des données collectées",
            agent=knowledge_engine,
            expected_output="Synthèse structurée des informations médicales",
            context=[mining_task]
        )
        
        response_task = Task(
            description="Génération de la réponse patient",
            agent=pharma_assistant,
            expected_output="Réponse claire et adaptée au grand public",
            context=[analysis_task]
        )
        
        # Configuration de l'équipe
        medical_crew = Crew(
            agents=[data_miner, knowledge_engine, pharma_assistant],
            tasks=[mining_task, analysis_task, response_task],
            process=Process.sequential,
            verbose=verbose
        )
        
        # Exécution
        result = medical_crew.kickoff(inputs={"user_query": user_query})
        
        return {"result": result}