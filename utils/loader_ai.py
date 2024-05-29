from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredPowerPointLoader

from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma,FAISS


def load_document(file_path):
    """
    Charge un document texte ou PDF et l'indexe dans une base de données vectorielle.

    Args:
    file_path (str): Chemin vers le fichier à charger (TXT ou PDF).
    """
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    elif file_path.endswith('.docx'):
        loader=Docx2txtLoader(file_path)
    elif file_path.endswith('.pptx'):
        loader=UnstructuredPowerPointLoader(".pptx")
    else:
        raise ValueError("Format de fichier non supporté. Utilisez un fichier PDF ou TXT ou DOCX ou PPTX.")

    documents = loader.load()
    return documents




def load_document_and_save_on_vectorbd(file_path, embedding_model,chunk_size=800,chunk_overlap=100,mode="faiss"):
    """
    Charge un document texte, PDF, DOCX ou PPTX et l'indexe dans une base de données vectorielle.

    Args:
    file_path (str): Chemin vers le fichier à charger.
    embedding_model (OpenAIEmbeddings): Le modèle d'embedding.

    Returns:
    (FAISS, list): La base de données vectorielle et les documents chargés.
    """

    documents = load_document(file_path)
    #print(documents)  # On a une liste de documents représentant chacune des pages via l'objet Document
    #Splitter
    text_splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator='\n')
    docs = text_splitter.split_documents(documents=documents)
    if mode=="faiss":
        vectorsstore = FAISS.from_documents(docs, embedding_model)
    else:
        vectorsstore=Chroma.from_documents(docs, embedding_model)
    return (vectorsstore, docs )

