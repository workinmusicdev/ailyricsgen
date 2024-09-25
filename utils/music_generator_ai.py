from pathlib import Path

import requests
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI

from utils.parsers_ai import MusicLyrics, music_lyrics_parser
from utils.prompt_ai import get_lyrics_generator_prompt

def generate_music_lyrics(elements, style, orientation,num_verses=3, taille=1500,mode="auto",langue="français"):

    print("##################")
    print(langue)
    print("##################")
    prompt = get_lyrics_generator_prompt(mode, langue)
    print("##################")
    print(prompt)
    print("##################")
    llm = ChatOpenAI(temperature=0.05, model_name="gpt-4o",)
    chain = prompt | llm | music_lyrics_parser

    res = chain.invoke({
        "elements": elements,
        "style": style,
        "num_verses": num_verses,
        "taille": taille,
        "orientation":orientation,
        "langue":langue,
    })

    return res


def download_file_by_url(url, path=Path.cwd()/"temp"):
    try:
        p=Path.cwd()/"temp"
        # Envoyer une requête GET pour télécharger le fichier
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Vérifie si la requête a réussi

        # Extraire le nom du fichier de l'URL
        file_name = url.split("/")[-1]
        file_path = f"{p.absolute()}/{file_name}"

        # Ouvrir un fichier en mode binaire pour l'écriture
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filtrer les chunks vides
                    file.write(chunk)

        print(f"Le fichier a été téléchargé avec succès et enregistré à {file_path}")
        return file_path
    except requests.exceptions.RequestException as e:
        print(f"Une erreur s'est produite lors du téléchargement du fichier: {e}")

#download_file_by_url("https://cdn1.suno.ai/f629e036-f649-4ae6-8567-dc58a6d15ad0.mp3","./tmp")
