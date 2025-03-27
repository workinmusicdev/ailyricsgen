from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent, create_openai_functions_agent
from langchain.chains.llm_math.base import LLMMathChain
import requests
from langchain_community.utilities import WikipediaAPIWrapper, GooglePlacesAPIWrapper, SerpAPIWrapper
import os
import json
from langchain_core.tools import Tool

from langchain_openai import ChatOpenAI

load_dotenv()
def setup_agent():
    llm = ChatOpenAI(temperature=0.1, model_name="gpt-4")  # Utiliser GPT-4

    # Initialisation des API Wrappers
    wikipedia = WikipediaAPIWrapper()
    search = SerpAPIWrapper()

    # Initialisation de la chaîne LLMMath
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)

    # Initialisation de la chaîne RAG (Retrieval-Augmented Generation)
   # rag_chain = RAGChain.from_llm(llm=llm, retriever=search, verbose=False)

    # Définition des outils
    tools = [
        # Tool(name="Search", func=search.run,
        #      description="Effectue des recherches sur des informations générales, des thèmes en général et concepts éducatifs"),
        Tool(name="Calculator", func=llm_math_chain.run,
             description="Propose des outils de calcul mathématique."),
        #Tool(name="Wikipedia", func=wikipedia.run,
         #    description="Fais des recherches sur des informations encyclopédie"),
       # Tool(name="DocumentRetrieval", func=rag_chain.run,
        #     description="Récupère et génère des documents en utilisant une base de connaissances augmentée par la récupération.")
    ]

    # Récupération du prompt
    prompt = hub.pull("hwchase17/openai-functions-agent")

    # Création de l'agent
    agent = create_openai_functions_agent(llm, tools, prompt)

    # Création de l'exécuteur d'agent
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor

# Méthode pour faire une requête directe vers l'API OpenAI avec requests
def request_openai(prompt: str, model: str = "gpt-4", temperature: float = 0.1) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("response.text")
    print(response.text)
    print("response.text")

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}