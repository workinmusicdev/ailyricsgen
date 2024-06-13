import json
import time
import zipfile

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import tempfile
import shutil
import os
from redis import Redis
from rq import Queue
from starlette.responses import FileResponse, JSONResponse
from inference.infer_extraction import inference, inference_by_theme
from job import  process_music_from_docs, process_lyrics_from_theme
from models.data_input import GenerateMusicRequest
from utils.extraction_ai import extraire_elements_key_from_context, format_to_human
from utils.googdrive.quickstart import upload_file_to_gdrive, upload_file_in_folder_to_gdrive
from utils.lrcgenerator.genlrc import load_whisper_model
from utils.music_generator_ai import generate_music_lyrics, download_file_by_url
from utils.parsers_ai import MusicLyrics, Lyrics
from utils.sunowrapper.generate_song import fetch_feed, generate_music
from utils.tools import format_lyrics_single_refrain, format_lyrics_single_refrain
from rq.job import Job
from rq.registry import StartedJobRegistry, FinishedJobRegistry


load_dotenv()
app = FastAPI()
redis_conn=Redis(host="146.59.196.155",port=6379)
task_queue=Queue("task_queue",connection=redis_conn)

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./output"
ZIP_OUTPUT_DIR = "zip_outputs/"
# Créer le répertoire de téléchargement s'il n'existe pas
os.makedirs(ZIP_OUTPUT_DIR, exist_ok=True)
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle Whisper au démarrage de l'application

@app.get("/job/status/{job_id}", tags=["job"])
async def get_job_status(job_id: str):
    """
    Endpoint to get the status and result of a job.
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if job.is_finished:
        return {"status": job.get_status(), "result": job.result}
    elif job.is_queued:
        return {"status": job.get_status(), "result": None}
    elif job.is_started:
        return {"status": job.get_status(), "result": None}
    else:
        return {"status": job.get_status(), "result": None}


@app.get("/queue/status", tags=["job"])
async def get_queue_status():
    """
    Endpoint to get the status of the queue.
    """
    job_ids = task_queue.job_ids
    started_registry = StartedJobRegistry(queue=task_queue)
    finished_registry = FinishedJobRegistry(queue=task_queue)

    return {
        "total_jobs": len(job_ids),
        "finished_jobs": len(finished_registry.get_job_ids()),
        "started_jobs": len(started_registry.get_job_ids()),
        "queued_jobs": len(job_ids) - len(finished_registry.get_job_ids()) - len(started_registry.get_job_ids()),
        "started_job_ids": started_registry.get_job_ids(),
        "queued_job_ids": task_queue.job_ids,
    }


@app.post("/extract_elements_key_from_docs/",tags=['module'])
async def extract_elements_key_from_docs(
        file: UploadFile = File(..., description="Le document à traiter (Word, PDF, PowerPoint)"),
        orientation: str = Form(..., description="L'orientation du contexte à extraire du document"),
        min_char: int = Form(1000, description="Le nombre minimum de caractères pour le contexte extrait"),
        max_char: int = Form(1500, description="Le nombre maximum de caractères pour le contexte extrait"),
        niv_detail: int = Form(5, description="Le niveau de détail pour l'extraction (4 à 10)"),
        matiere:str= Form("",description="Nom de la matière concerné pour avoir une génération personnalisé"),
        niveau:str=Form("Terminale",description="Niveau de la classe"),
        langue:str=Form("Français",description="Langue de la génération")

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
        matiere=matiere,
        niveau=niveau,
        langue=langue,
        k=niv_detail,

    )

    # Supprimer le fichier après traitement
    os.remove(file_path)
    print(f"File deleted: {file_path}")

    # Extraire les éléments de réponse
    elements = data['answer']

    return {"context": elements}


@app.post("/extract_elements_key_from_theme/",tags=['module'])
async def extract_elements_key_from_theme(
        theme: str = Form(..., description="Le thème pour générer les paroles"),
        orientation: str = Form("Comprendre l'intelligence artificielle et des exemples d'application",
                                description="L'orientation des paroles générées"),

        taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères"),
    matiere: str = Form("", description="Nom de la matière concerné pour avoir une génération personnalisé"),
    niveau:str = Form("Terminale", description="Niveau de la classe"),
langue:str = Form("Français", description="Langue de la génération")
):
    # Appeler la fonction d'inférence avec le thème et l'orientation
    a = inference_by_theme(theme, orientation,niveau=niveau,langue=langue,matiere=matiere)
    tmp=extraire_elements_key_from_context(a, orientation, taille)

    return {"context": tmp.content}

@app.post("/generate_lyrics_from_elements_keys/",tags=['module'])
async def generate_lyrics_from_elements_key(
    elements: str = Form(..., description="Les éléments clés pour générer les paroles"),
    style: str = Form(..., description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
    num_verses: int = Form(3, description="Le nombre de couplets à générer"),
    taille: int = Form(1300, description="La taille totale des paroles générées en nombre de caractères"),
    orientation: str = Form(..., description="L'orientation des paroles générées"),
        mode: str = Form("auto", description="Selectioon du choix du nombre couplets, auto / manuel"),

        langue: str = Form("Français", description="Langue de la génération")

):
    data = generate_music_lyrics(
        elements=elements,
        style=style,
        num_verses=num_verses,
        taille=taille,
        orientation=orientation,
        langue=langue,
        mode=mode
    )

    out = MusicLyrics.parse_obj(data).to_dict()
    tmp = format_to_human(out['lyrics'])
    print(tmp)

    out.update(Lyrics.parse_obj(tmp).to_dict())
    return out


@app.post("/generate_lyrics_docs/",tags=['text to lyrics'])
async def generate_lyrics_from_docs(
        file: UploadFile = File(..., description="Le document à traiter (Word, PDF, PowerPoint)"),
        orientation: str = Form(..., description="L'orientation du contexte à extraire du document"),
        min_char: int = Form(1000, description="Le nombre minimum de caractères pour le contexte extrait"),
        max_char: int = Form(1500, description="Le nombre maximum de caractères pour le contexte extrait"),
        niv_detail: int = Form(5, description="Le niveau de détail pour l'extraction (4 à 10)"),
    style: str = Form(..., description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
    num_verses: int = Form(3, description="Le nombre de couplets à générer"),
    taille: int = Form(1500, description="La taille totale des paroles générées en nombre de caractères"),
        mode: str=Form("auto",description="Selectioon du choix du nombre couplets, auto / manuel"),
        matiere: str = Form("", description="Nom de la matière concerné pour avoir une génération personnalisé"),
        niveau: str = Form("Terminale", description="Niveau de la classe"),
        langue: str = Form("Français", description="Langue de la génération")

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
        matiere=matiere,
        langue=langue,
        niveau=niveau,
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
        mode=mode,
        langue=langue

    )

    out = MusicLyrics.parse_obj(data).to_dict()
    tmp = format_to_human(out['lyrics'])
    print(tmp)

    out.update(Lyrics.parse_obj(tmp).to_dict())
    return out



@app.post("/generate_lyrics_theme/",tags=["text to lyrics"])
async def generate_lyrics_from_theme(
        theme: str = Form(..., description="Le thème pour générer les paroles"),
        orientation: str = Form("Comprendre l'intelligence artificielle et des exemples d'application",
                                description="L'orientation des paroles générées"),
        style: str = Form("Rap", description="Le style des paroles (par exemple, Rap, Pop, etc.)"),
        num_verses: int = Form(3, description="Le nombre de couplets à générer"),
        taille: int = Form(1400, description="La taille totale des paroles générées en nombre de caractères"),
        mode: str = Form("auto", description="Selectioon du choix du nombre couplets, auto / manuel"),
        matiere: str = Form("", description="Nom de la matière concerné pour avoir une génération personnalisé"),
        niveau: str = Form("Terminale", description="Niveau de la classe"),
        langue: str = Form("Français", description="Langue de la génération")

):
    # Appeler la fonction d'inférence avec le thème et l'orientation
    a = inference_by_theme(theme, orientation,matiere=matiere,langue=langue,niveau=niveau)
    tmp=extraire_elements_key_from_context(a, orientation, taille)


    # Générer les paroles de musique
    data = generate_music_lyrics(
        elements=tmp.content,
        style=style,
        num_verses=num_verses,
        taille=taille,
        orientation=orientation,
        mode=mode,
        langue=langue
    )


    return MusicLyrics.parse_obj(data)


@app.get("/get_music_ressource/{music_id}",tags=["ressource"])
def fetch_feed_endpoint(music_id: str):
    try:
        return fetch_feed(music_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-music", response_model=list,tags=['module'])
def generate_music_endpoint(request: GenerateMusicRequest):
    """
    Generate music based on provided lyrics, title, and style.

    Args:
    - request (GenerateMusicRequest): The request body containing lyrics, title, and style.

    Returns:
    - list: A list of clip IDs generated by the music generation API.

    Raises:
    - HTTPException: If the music generation API fails.
    """
    try:
        return generate_music(request.lyrics, request.title, request.style)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_music_from_multiple_docs/", tags=['old'])
async def generate_music_from_multi_docs(
        files: List[UploadFile] = File(..., description="Les documents à traiter (Word, PDF, PowerPoint)"),
        metadata_file: UploadFile = File(...,
                                         description="Fichier Excel ou CSV avec les paramètres d'orientation, taille, style, etc.")
):
    # Sauvegarder les fichiers de manière permanente
    file_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(file_path)

    metadata_path = os.path.join(UPLOAD_DIR, metadata_file.filename)
    with open(metadata_path, "wb") as f:
        shutil.copyfileobj(metadata_file.file, f)

    # Lire les métadonnées du fichier Excel ou CSV
    if metadata_path.endswith(".xlsx"):
        df = pd.read_excel(metadata_path)
    else:
        df = pd.read_csv(metadata_path)

    outputs = []

    for index, row in df.iterrows():
        doc_id = str(row['id'])
        orientation = row['orientation']

        niv_detail = row['niv_detail']
        style = row['style']
        langue=row['langue']
        niveau=row['niveau']
        matiere=row['matiere']


        print(row)
        # Trouver le fichier correspondant à l'id
        file_path = next((path for path in file_paths if os.path.basename(path).startswith(doc_id)), None)
        print(row['id'],file_path)
        if not file_path:
            continue

        # Appeler la fonction d'inférence avec le chemin du fichier
        data = inference(
            file_path,
            orientation=orientation,

            langue=langue,
            niveau=niveau,
            matiere=matiere,
            k=niv_detail,
        )

        # Supprimer le fichier après traitement
        os.remove(file_path)

        # Extraire les éléments de réponse
        elements = data['answer']
        data = generate_music_lyrics(
            elements=elements,
            style=style,

            orientation=orientation,
            langue=langue
        )

        out = MusicLyrics.parse_obj(data)
        tmp_dict = out.to_dict()
        tmp_dict['url'] = []
        tmp_dict["music"] = generate_music(format_lyrics_single_refrain(out.lyrics), out.title, out.style)
        time.sleep(500)
        print(tmp_dict)
        c = 1
        name = ""
        for id in tmp_dict["music"]:
            print(id)
            dat = fetch_feed(id)[0]
            print(dat)
            n = download_file_by_url(dat['audio_url'], )
            n2 = download_file_by_url(dat['image_large_url'], )
            name = dat["title"].replace(' ', '').lower()
            dat["url_drive"] = upload_file_in_folder_to_gdrive(n, f"{dat['title'].replace(' ', '').lower()}_v{c}.mp3",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s',
                                                               dat["title"].replace(' ', '').lower())
            dat["img_drive"] = upload_file_in_folder_to_gdrive(n2, f"{dat['title'].replace(' ', '').lower()}_v{c}.jpeg",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s',
                                                               dat["title"].replace(' ', '').lower())
            tmp_dict['url'].append(dat)
            c += 1

        # Sauvegarder le résultat sous forme de JSON avec encodage UTF-8
        output_path = os.path.join(OUTPUT_DIR, f"{file_path.split('.')[0].replace(' ', '')}_output.json")
        f = upload_file_in_folder_to_gdrive(output_path, f"data.json",
                                            '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s',
                                            name)
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)

        outputs.append(tmp_dict)
    # Créer un fichier ZIP contenant tous les fichiers JSON générés
    zip_path = os.path.join(ZIP_OUTPUT_DIR, "outputs.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)
    # Supprimer tous les fichiers JSON dans OUTPUT_DIR
    for file in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    # Retourner l'URL pour télécharger le fichier ZIP
    zip_url = f"/download/{os.path.basename(zip_path)}"

    return {
        "download":zip_url,
        "data":outputs
    }

@app.post("/generate_lyrics_multiple_theme/", tags=["old"])
async def generate_lyrics_multi_from_theme(
        metadata_file: UploadFile = File(..., description="Fichier Excel avec les paramètres (thème, orientation, taille, etc.)")
):
    # Sauvegarder le fichier de métadonnées de manière permanente
    metadata_path = os.path.join(UPLOAD_DIR, metadata_file.filename)
    with open(metadata_path, "wb") as f:
        shutil.copyfileobj(metadata_file.file, f)

    # Lire les métadonnées du fichier Excel
    if metadata_path.endswith(".xlsx"):
        df = pd.read_excel(metadata_path)
    else:
        return JSONResponse(content={"message": "Le fichier doit être au format Excel (.xlsx)"}, status_code=400)

    outputs = []

    for index, row in df.iterrows():
        theme = row['theme']
        orientation = row['orientation']
        style = row['style']
        langue = row['langue']
        niveau = row['niveau']
        matiere = row['matiere']


        # Appeler la fonction d'inférence avec le thème et l'orientation
        a = inference_by_theme(theme, orientation,niveau=niveau,matiere=matiere,langue=langue)
        tmp = extraire_elements_key_from_context(a, orientation, )

        # Générer les paroles de musique
        data = generate_music_lyrics(
            elements=tmp.content,
            style=style,
            langue=langue,



            orientation=orientation,

        )

        out = MusicLyrics.parse_obj(data)
        tmp_dict = out.to_dict()
        tmp_dict['url']=[]
        tmp_dict["music"] = generate_music(format_lyrics_single_refrain(out.lyrics), out.title, out.style)
        time.sleep(500)
        print(tmp_dict)
        c=1
        name=""
        for id in tmp_dict["music"]:
            print(id)
            dat=fetch_feed(id)[0]
            print(dat)
            n=download_file_by_url(dat['audio_url'],)
            n2=download_file_by_url(dat['image_large_url'], )
            name=dat["title"].replace(' ', '').lower()
            dat["url_drive"]= upload_file_in_folder_to_gdrive(n, f"{dat['title'].replace(' ','').lower()}_v{c}.mp3", '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', dat["title"].replace(' ','').lower())
            dat["img_drive"] = upload_file_in_folder_to_gdrive(n2, f"{dat['title'].replace(' ', '').lower()}_v{c}.jpeg",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s',
                                                               dat["title"].replace(' ', '').lower())
            tmp_dict['url'].append(dat)
            c+=1

        # Sauvegarder le résultat sous forme de JSON avec encodage UTF-8
        output_path = os.path.join(OUTPUT_DIR, f"{theme.replace(' ','')}_output.json")
        f=upload_file_in_folder_to_gdrive(output_path, f"data.json",
                                        '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s',
                                        name)
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)

        outputs.append(tmp_dict)


    # Créer un fichier ZIP contenant tous les fichiers JSON générés
    zip_path = os.path.join(ZIP_OUTPUT_DIR, "outputs.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(OUTPUT_DIR):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=file)

    # Supprimer tous les fichiers JSON dans OUTPUT_DIR
    for file in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    # Retourner l'URL pour télécharger le fichier ZIP
    zip_url = f"/download/{os.path.basename(zip_path)}"
    return {"zip_url": zip_url,
            "data":outputs}

@app.get("/download/{file_name}",tags=['ressource'])
async def download_file(file_name: str):
    file_path = os.path.join(ZIP_OUTPUT_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    return JSONResponse(content={"message": "File not found"}, status_code=404)




@app.post("/job/generate_music_from_multiple_docs/", tags=['text to music (multiple)'])
async def job_generate_music_from_multi_docs(
        files: List[UploadFile] = File(..., description="Les documents à traiter (Word, PDF, PowerPoint)"),
        metadata_file: UploadFile = File(..., description="Fichier Excel ou CSV avec les paramètres d'orientation, taille, style, etc.")
):
    job_instance = task_queue.enqueue(process_music_from_docs, files, metadata_file,job_timeout=18000)
    return {
        "success": True,
        "job_id": job_instance.id
    }

@app.post("/job/generate_lyrics_multiple_theme/", tags=['text to music (multiple)'])
async def job_generate_lyrics_multi_from_theme(
        metadata_file: UploadFile = File(..., description="Fichier Excel avec les paramètres (thème, orientation, taille, etc.)")
):
    job_instance = task_queue.enqueue(process_lyrics_from_theme, metadata_file,job_timeout=18000)
    return {
        "success": True,
        "job_id": job_instance.id
    }


# Lancer l'application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
#rq worker task_queue