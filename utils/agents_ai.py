from dotenv import load_dotenv
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor, create_react_agent, create_openai_functions_agent
from langchain.chains.llm_math.base import LLMMathChain

from langchain_community.utilities import WikipediaAPIWrapper, GooglePlacesAPIWrapper, SerpAPIWrapper

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
        Tool(name="Search", func=search.run,
             description="Effectue des recherches sur des informations générales, des thèmes en général et concepts éducatifs"),
        Tool(name="Calculator", func=llm_math_chain.run,
             description="Propose des outils de calcul mathématique."),
        Tool(name="Wikipedia", func=wikipedia.run,
             description="Offre un accès  à des connaissances , encyclopédie , idéal pour approfondir la connaissance et des notions sur des sujets."),
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

