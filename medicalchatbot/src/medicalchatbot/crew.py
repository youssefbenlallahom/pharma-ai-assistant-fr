from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool ,SeleniumScrapingTool
from crewai import LLM
from dotenv import load_dotenv
import os
from langchain_groq import ChatGroq
from litellm import completion
from crewai import LLM as CrewLLM
from langchain_community.llms import Ollama
from crewai_tools import SeleniumScrapingTool
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv()

# Outils
search_tool = SerperDevTool(
    country="fr", 
    locale="fr", 
    location="France")

vidal_tool = ScrapeWebsiteTool(website_url="https://www.vidal.fr")
bdpm_tool = ScrapeWebsiteTool(website_url="https://base-donnees-publique.medicaments.gouv.fr")
passeport_tool = ScrapeWebsiteTool(website_url="https://www.passeportsante.net")
santefr_tool = ScrapeWebsiteTool(website_url="https://www.sante.fr")


class MedicamentScrapingTool(SeleniumScrapingTool):
    def __init__(self, website_url=""):
        super().__init__(website_url=website_url)
    
    def scrape_with_more_button(self, url=None):
        """Méthode personnalisée pour scraper avec clic sur 'voir plus'"""
        if url:
            self.website_url = url
            
        # Utiliser le driver Selenium pour naviguer
        content = self.scrape()
        
        # Tentative de clic sur 'voir plus'
        try:
            # Liste des sélecteurs possibles pour 'voir plus'
            selectors = [
                "//button[contains(text(), 'Voir plus de détails')]",
                "//a[contains(text(), 'Voir plus de détails')]",
                "//span[contains(text(), 'voir plus')]",
                "//div[contains(@class, 'readmore')]",
                "//button[contains(@class, 'showmore')]",
                ".toggledetailmed", 
                ".btnplus",
                "a[data-txt='Voir moins de détails']",
                ".readmore-button",
                "a:contains('Voir plus')",
                "button:contains('Voir plus de détails')"
            ]
            
            driver = self._get_driver()
            
            for selector in selectors:
                try:
                    more_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    more_button.click()
                    time.sleep(2)  # Attendre le chargement du contenu
                    break  # Sortir de la boucle si un bouton a été cliqué
                except:
                    continue
                    
            # Récupérer le contenu après avoir cliqué
            return driver.page_source
        except:
            # En cas d'échec, retourner le contenu initial
            return content
        
med_custom_scraper = MedicamentScrapingTool()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

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
3. Sources autorisées : Vidal/BDPM/PasseportSanté/Sante.fr/med.tn
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
    api_key=os.getenv("GROQ3_API_KEY"),
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
                med_custom_scraper  
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
