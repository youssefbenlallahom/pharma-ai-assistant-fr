from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai import LLM
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from litellm import completion
from crewai import LLM as CrewLLM
from langchain_community.llms import Ollama

load_dotenv()

# Outils
search_tool = SerperDevTool(
    country="fr", 
    locale="fr", 
    location="France")

vidal_tool = ScrapeWebsiteTool(website="https://www.vidal.fr")
bdpm_tool = ScrapeWebsiteTool(website="https://base-donnees-publique.medicaments.gouv.fr")
passeport_tool = ScrapeWebsiteTool(website="https://www.passeportsante.net")
santefr_tool = ScrapeWebsiteTool(website="https://www.sante.fr")

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

llm1 = completion(
    model="llama-guard-3-8b",
    api_base="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ1_API_KEY"),
    messages=[
        {"role": "system", "content": """🚀 Assistant Médical Expert - Extraction de Données
Règles Absolues :
1. Français exclusivement - Aucun terme anglais toléré
2. Format de sortie strict : 
   - Dictionnaire JSON structuré
   - Rubriques prédéfinies (Composition, Indications, Posologie...)
3. Sources autorisées : Vidal/BDPM/PasseportSanté/Sante.fr
4. Validation croisée des informations entre sources
5. Aucun commentaire hors structure demandée

Processus :
1. Identifier les sources pertinentes
2. Extraire les données brutes
3. Uniformiser les unités de mesure
4. Détecter les contradictions (→ noter [ALERTE] le cas échéant)
5. Structurer selon le schéma médical standard
"""}
    ]
)

llm2 = completion(
    model="llama3-70b-8192",
    api_base="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ2_API_KEY"),
    messages=[
        {"role": "system", "content": """🔍 Système Expert Médical - Traitement des Connaissances
Objectif : Transformer les données brutes en savoir exploitable

Directives :
1. Français technique strict
2. Structure de sortie :
   - Fiche technique professionnelle (max 400 mots)
   - Encodage sémantique pour RAG

Étapes Obligatoires :
1. Analyse de cohérence inter-sources
2. Hiérarchisation des informations (critères ATC/OMS)
3. Génération de contextes thématiques
4. Détection des lacunes informationnelles

Format de Sortie :
=== FICHE TECHNIQUE ===
[Nom Médicament]
► Indications : 
   - Principale (Niveau de preuve A)
   - Secondaire (Niveau de preuve B)
► Posologie : 
   - Adultes : X mg/j
   - Enfants : Y mg/kg
► Surveillance : 
   - Paramètres biologiques
   - Signes d'alerte
"""}
    ]
)
llm3 = completion(
    model="llama-3.3-70b-versatile",
    api_base="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ2_API_KEY"),
    messages=[
        {"role": "system", "content": """💊 Assistant Pharmaceutique Clinicien
Règles de Réponse :
1. Français professionnel uniquement
2. Structure IMPÉRATIVE :
   - Réponse en 50 mots max
   - 1-2 phrases maximum
   - Informations vérifiées uniquement
3. Interdictions formelles :
   - Débuter par "Réponse :"
   - Mentionner des sources
   - Termes techniques non expliqués
   
Procédure de Vérification :
1. Croiser avec base de connaissances
2. Filtrer les informations non vérifiées
3. Adapter au niveau patient/professionnel"""}
    ]
)


@CrewBase
class Medicalchatbot():
    """Assistant médical intelligent utilisant CrewAI"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # Nouveaux agents fusionnés
    @agent
    def data_miner(self) -> Agent:
        """Fusion de scraper_web et chercheur_medical"""
        return Agent(
            config=self.agents_config['data_miner'],
            tools=[
                search_tool,
                vidal_tool,
                bdpm_tool,
                passeport_tool,
                santefr_tool,
            ],
            llm=llm1,
            verbose=True
            
        )
    
    @agent
    def knowledge_engine(self) -> Agent:
        """Fusion de moteur_rag et analyste_de_donnees"""
        return Agent(
            config=self.agents_config['knowledge_engine'],
            tools=[],
            llm=llm2,
            verbose=True
        )
    
    @agent
    def pharma_assistant(self) -> Agent:
        """Assistant pharmaceutique optimisé"""
        return Agent(
            config=self.agents_config['pharma_assistant'],
            verbose=True,
            llm=llm3
        )
    
    # Nouvelles tâches fusionnées
    @task
    def data_mining_task(self) -> Task:
        """Fusion de scraping_task et research_task"""
        return Task(
            config=self.tasks_config['data_mining_task'],
            agent=self.data_miner(),
            output_file='reponse_finale_data_miner.md'
        )
    
    @task
    def knowledge_processing_task(self) -> Task:
        """Fusion de analysis_task et rag_task"""
        return Task(
            config=self.tasks_config['knowledge_processing_task'],
            agent=self.knowledge_engine(),
            dependencies=[self.data_mining_task()],
            output_file='reponse_finale_knowledge.md'
        )
    
    @task
    def response_generation_task(self) -> Task:
        """Génère une réponse à la question médicale"""
        return Task(
            config=self.tasks_config['response_generation_task'],
            agent=self.pharma_assistant(),
            dependencies=[self.knowledge_processing_task()],
            output_file='reponse_finale.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """Assemble l'équipe médicale virtuelle"""
        return Crew(
            agents=[
                self.data_miner(),
                self.knowledge_engine(),
                self.pharma_assistant()
            ],
            tasks=[
                self.data_mining_task(),
                self.knowledge_processing_task(),
                self.response_generation_task()
            ],
            process=Process.sequential,
            verbose=True
        )
