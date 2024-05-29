#Import Dependencies

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# to create a new file named vectorstore in your current directory.
def load_knowledgeBase():
        embeddings=OpenAIEmbeddings(api_key="Enter your API key")
        DB_FAISS_PATH = 'vectorstore/db_faiss'
        db = FAISS.load_local(DB_FAISS_PATH, embeddings)
        return db