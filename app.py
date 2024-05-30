from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import shutil
import os

from inference.infer_extraction import inference, inference_by_theme
from utils.extraction_ai import extraire_elements_key_from_context
from utils.music_generator_ai import generate_music_lyrics
from utils.parsers_ai import MusicLyrics

load_dotenv()
app = FastAPI()

UPLOAD_DIR = "uploads"

# Créer le répertoire de téléchargement s'il n'existe pas
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract_elements_key_from_docs/",tags=['extraction'])
async def extract_elements_key_from_docs(
        file: UploadFile = File(..., description="Le document à traiter (Word, PDF, PowerPoint)"),
        orientation: str = Form(..., description="L'orientation du contexte à extraire du document"),
        min_char: int = Form(1000, description="Le nombre minimum de caractères pour le contexte extrait"),
        max_char: int = Form(1500, description="Le nombre maximum de caractères pour le contexte extrait"),
        niv_detail: int = Form(5, description="Le niveau de détail pour l'extraction (4 à 10)")
):
    # Sauvegarder le fichier de manière permanente
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(f"File saved at: {file_path}")

    # Appeler la fonction d'inférence avec le chemin du fichier
    data = inference(
        file_path,
        orientation=orientation,
        min_nombre_caracteres=min_char,
        max_nombre_caracteres=max_char,
        mode="chroma",
        k=niv_detail,
    )

    # Supprimer le fichier après traitement
    os.remove(file_path)
    print(f"File deleted: {file_path}")

    # Extraire les éléments de réponse
    elements = data['answer']

    return {"context": elements}


@app.post("/extract_elements_key_from_theme/",tags=['extraction'])
async def extract_elements_key_from_theme(
        theme: str = Form(..., description="Le thème pour générer les paroles"),
        orientation: str = Form("Comprendre l'intelligence artificielle et des exemples d'application",
                                description="L'orientation des paroles générées"),

        taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères")
):
    # Appeler la fonction d'inférence avec le thème et l'orientation
    a = inference_by_theme(theme, orientation)
    tmp=extraire_elements_key_from_context(a, orientation, taille)

    return {"context": tmp.content}

@app.post("/generate_lyrics_from_elements_keys/",tags=['module'])
async def generate_lyrics_from_elements_key(
    elements: str = Form(..., description="Les éléments clés pour générer les paroles"),
    style: str = Form(..., description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
    num_verses: int = Form(3, description="Le nombre de couplets à générer"),
    taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères"),
    orientation: str = Form(..., description="L'orientation des paroles générées"),
):
    data = generate_music_lyrics(
        elements=elements,
        style=style,
        num_verses=num_verses,
        taille=taille,
        orientation=orientation,
    )
    return MusicLyrics.parse_obj(data)




@app.post("/generate_lyrics_docs/",tags=['complete'])
async def generate_lyrics_from_docs(
        file: UploadFile = File(..., description="Le document à traiter (Word, PDF, PowerPoint)"),
        orientation: str = Form(..., description="L'orientation du contexte à extraire du document"),
        min_char: int = Form(1000, description="Le nombre minimum de caractères pour le contexte extrait"),
        max_char: int = Form(1500, description="Le nombre maximum de caractères pour le contexte extrait"),
        niv_detail: int = Form(5, description="Le niveau de détail pour l'extraction (4 à 10)"),
    style: str = Form(..., description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
    num_verses: int = Form(3, description="Le nombre de couplets à générer"),
    taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères"),

):
    # Sauvegarder le fichier de manière permanente
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(f"File saved at: {file_path}")

    # Appeler la fonction d'inférence avec le chemin du fichier
    data = inference(
        file_path,
        orientation=orientation,
        min_nombre_caracteres=min_char,
        max_nombre_caracteres=max_char,
        mode="chroma",
        k=niv_detail,
    )

    # Supprimer le fichier après traitement
    os.remove(file_path)
    print(f"File deleted: {file_path}")

    # Extraire les éléments de réponse
    elements = data['answer']
    data = generate_music_lyrics(
        elements=elements,
        style=style,
        num_verses=num_verses,
        taille=taille,
        orientation=orientation,
    )

    return MusicLyrics.parse_obj(data)


@app.post("/generate_lyrics_theme/",tags=["complete"])
async def generate_lyrics_from_theme(
        theme: str = Form(..., description="Le thème pour générer les paroles"),
        orientation: str = Form("Comprendre l'intelligence artificielle et des exemples d'application",
                                description="L'orientation des paroles générées"),
        style: str = Form("Rap", description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
        num_verses: int = Form(3, description="Le nombre de couplets à générer"),
        taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères")
):
    # Appeler la fonction d'inférence avec le thème et l'orientation
    a = inference_by_theme(theme, orientation)
    tmp=extraire_elements_key_from_context(a, orientation, taille)


    # Générer les paroles de musique
    data = generate_music_lyrics(
        elements=tmp.content,
        style=style,
        num_verses=num_verses,
        taille=taille,
        orientation=orientation,
    )


    return MusicLyrics.parse_obj(data)

# Lancer l'application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
