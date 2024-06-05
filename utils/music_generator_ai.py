from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI

from utils.parsers_ai import MusicLyrics, music_lyrics_parser
from utils.prompt_ai import get_lyrics_generator_prompt

def generate_music_lyrics(elements, style, num_verses, taille,orientation,mode="auto"):
    prompt = get_lyrics_generator_prompt(mode)
    llm = ChatOpenAI(temperature=0.05, model_name="gpt-4o",)
    chain = prompt | llm | music_lyrics_parser

    res = chain.invoke({
        "elements": elements,
        "style": style,
        "num_verses": num_verses,
        "taille": taille,
        "orientation":orientation
    })

    return res