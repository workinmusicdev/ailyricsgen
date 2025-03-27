from langchain.agents import AgentExecutor
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import CharacterTextSplitter

from utils.agents_ai import request_openai, setup_agent
from utils.embeddings_ai import load_embedding_openai
from utils.extraction_ai import extraire_elements_pertinents
from utils.loader_ai import load_document_and_save_on_vectorbd


def inference(file_path,orientation,min_nombre_caracteres=1500,max_nombre_caracteres=200,k=5,matiere="",niveau="",langue=""):
    embedding=load_embedding_openai()
    tmp_store, docs=load_document_and_save_on_vectorbd(file_path,embedding,)
    print(len(docs))
    if niveau!="":
        orientation+=f".Pour un niveau {niveau}"
    orientation+=f" en {langue}"

    output=extraire_elements_pertinents(orientation,tmp_store,embedding,min_nombre_caracteres=min_nombre_caracteres,max_nombre_caracteres=max_nombre_caracteres,k=k,matiere=matiere)


    return output


def load_document(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")

    documents = loader.load()
    return documents



def inference_without_rag(file_path, orientation="", min_nombre_caracteres=1500, max_nombre_caracteres=200, k=5,
                          matiere="", niveau="", langue=""):
    documents = load_document(file_path)
    text=[i.page_content for i in documents]
    return "\n\n".join(text)


def inference_by_theme(theme,orientation,niveau="",langue="français",matiere="Français"):
    # Load environment variables if needed


    # Setup the agent using the defined utility function
    agent_executor: AgentExecutor = setup_agent()
    # Charger l'orientation
    if niveau!="":
        orientation+=f".Pour un niveau {niveau}"
    orientation+=f" dans le domaine {matiere}"
    orientation+=f" en {langue}"
    #Optimiser
    question=f"J'aimerais en apprendre sur {theme} en te basant {orientation}"
    # response = agent_executor.invoke({"input":question})

    # print("response")
    # print(response)
    # print("response")

    response2 = request_openai(prompt=question, model="gpt-4o", temperature=0.0)
    print("response2")
    print(response2)
    print("response2")

    # Add the retrieved data to the output
    return response2