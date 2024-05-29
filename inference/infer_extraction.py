from langchain.agents import AgentExecutor

from utils.agents_ai import setup_agent
from utils.embeddings_ai import load_embedding_openai
from utils.extraction_ai import extraire_elements_pertinents
from utils.loader_ai import load_document_and_save_on_vectorbd


def inference(file_path,orientation,min_nombre_caracteres=1000,max_nombre_caracteres=2000,mode="chroma",k=5):
    embedding=load_embedding_openai()
    tmp_store, docs=load_document_and_save_on_vectorbd(file_path,embedding,)
    print(len(docs))

    output=extraire_elements_pertinents(orientation,tmp_store,embedding,min_nombre_caracteres=min_nombre_caracteres,max_nombre_caracteres=max_nombre_caracteres,k=k)


    return output


def inference_by_theme(theme,orientation):
    # Load environment variables if needed


    # Setup the agent using the defined utility function
    agent_executor: AgentExecutor = setup_agent()
    question=f"J'aimerais en apprendre sur {theme} en te basant {orientation}"
    response = agent_executor.invoke({"input":question})

    print(response)