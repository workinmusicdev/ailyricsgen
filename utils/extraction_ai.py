from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAI, ChatOpenAI

from utils.parsers_ai import Lyrics, lyrics_parser
from utils.prompt_ai import load_extraction_prompt, load_extraction_prompt_from_context, prompt_format_to_human_lyrics


def extraire_elements_pertinents(orientation, store, embedding_model,min_nombre_caracteres=1000,max_nombre_caracteres=2000, k=5,matiere="math"):
    retriever = store.as_retriever(search_kwargs={ "k" : k})
    prompt = load_extraction_prompt()
    orientation=f" {orientation}"
    llm=ChatOpenAI(model="gpt-4o",temperature=0)

    question_answer_chain=create_stuff_documents_chain(llm, prompt)

    chain = create_retrieval_chain(retriever, question_answer_chain)


    return chain.invoke({"input": orientation,"nombre_caracteres":min_nombre_caracteres,"nombre_caracteres_max":max_nombre_caracteres})

def extraire_elements_key_from_context(context,orientation,nbr_caratères=1400,):
    prompt = load_extraction_prompt_from_context()
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", )
    chain = prompt | llm

    res = chain.invoke({
        "elements": context,
        "taille": nbr_caratères,
        "orientation": orientation
    })

    return res

def format_to_human(lyrics):
    prompt = prompt_format_to_human_lyrics()
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o", )
    chain = prompt | llm | lyrics_parser

    res = chain.invoke({
        "elements": lyrics,
    })

    return res


