from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_openai import OpenAI, ChatOpenAI

from utils.prompt_ai import load_extraction_prompt


def extraire_elements_pertinents(orientation, store, embedding_model,min_nombre_caracteres=1000,max_nombre_caracteres=2000, k=5):
    retriever = store.as_retriever(search_kwargs={ "k" : k})
    prompt = load_extraction_prompt()
    llm=ChatOpenAI(model="gpt-4o",temperature=0)

    question_answer_chain=create_stuff_documents_chain(llm, prompt)

    chain = create_retrieval_chain(retriever, question_answer_chain)


    return chain.invoke({"input": orientation,"nombre_caracteres":min_nombre_caracteres,"nombre_caracteres_max":max_nombre_caracteres})


