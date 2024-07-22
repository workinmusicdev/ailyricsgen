import json
import subprocess
import time
import zipfile

import aiofiles
import boto3
from botocore.exceptions import NoCredentialsError


from utils.email_notifier import send_mail
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import tempfile
import rarfile
import shutil
import os
from redis import Redis
from rq import Queue
from starlette.responses import FileResponse, JSONResponse
from inference.infer_extraction import inference, inference_by_theme
from job import  process_music_from_docs, process_lyrics_from_theme,process_without_music_from_docs
from models.data_input import GenerateMusicRequest
from utils.extraction_ai import extraire_elements_key_from_context, format_to_human
from utils.googdrive.quickstart import upload_file_to_gdrive, upload_file_in_folder_to_gdrive

from utils.music_generator_ai import generate_music_lyrics, download_file_by_url
from utils.parsers_ai import MusicLyrics, Lyrics
from utils.sunowrapper.generate_song import fetch_feed, generate_music
from utils.tools import format_lyrics_single_refrain, format_lyrics_single_refrain
from rq.job import Job, Retry
from rq.registry import StartedJobRegistry, FinishedJobRegistry


load_dotenv()
app = FastAPI()
# Lire les variables d'environnement pour la configuration de Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_conn = Redis(host=redis_host, port=redis_port)
task_queue=Queue("task_queue",connection=redis_conn,default_timeout=172800)

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./output"
ZIP_OUTPUT_DIR = "zip_outputs/"
TEMP_DIR = "/media"

# Configure AWS S3
S3_BUCKET = "wimbucketstorage"
s3_client = boto3.client('s3', aws_access_key_id='AKIAZQ3DOIWH4GXKQBUP', aws_secret_access_key='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')

def upload_to_s3(file_obj, bucket_name, object_name=None):
    try:
        if object_name is None:
            object_name = file_obj.filename
        s3_client.upload_fileobj(file_obj.file, bucket_name, object_name)
        return f"s3://{bucket_name}/{object_name}"
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Credentials not available")


os.makedirs(TEMP_DIR, exist_ok=True)
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


@app.get("/download/{file_name}",tags=['ressource'])
async def download_file(file_name: str):
    file_path = os.path.join(ZIP_OUTPUT_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    return JSONResponse(content={"message": "File not found"}, status_code=404)

# Fonction pour extraire les fichiers d'un ZIP
def extract_files_from_zip(zip_path: str, extract_to: str) -> List[str]:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return [os.path.join(extract_to, file) for file in os.listdir(extract_to)]


# Fonction pour extraire les fichiers d'un ZIP
def extract_files_from_zip(zip_path: str, extract_to: str) -> List[str]:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    return [os.path.join(extract_to, file) for file in os.listdir(extract_to)]


# Fonction pour sauvegarder un fichier uploadé localement
def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination




def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    return destination

@app.post("/job/generate_music_from_docs/", tags=['text to music (multiple)'])
async def job_generate_music_without_docs_from_docs(
        documents: List[UploadFile] = File(..., description="Les fichiers à traiter"),
        metadata_file: UploadFile = File(..., description="Fichier Excel ou CSV avec les paramètres d'orientation, taille, style, etc."),
        email_notification: Optional[str] = Form("workinmusic.app@gmail.com")
):
    document_paths = []

    for document in documents:
        document_path = f"uploads/{document.filename}"
        os.makedirs(os.path.dirname(document_path), exist_ok=True)
        save_upload_file(document, document_path)
        document_paths.append(document_path)

    metadata_path = f"uploads/{metadata_file.filename}"
    save_upload_file(metadata_file, metadata_path)

    send_mail(
        subject="WIM Gen : Job start",
        message=f"Your job has started with {len(document_paths)} files.",
        recipient_email=email_notification
    )

    job_instance = task_queue.enqueue(
        process_without_music_from_docs(), document_paths, metadata_path,
        job_timeout=172800, retry=Retry(max=3)
    )

    return {
        "success": True,
        "job_id": job_instance.id
    }




# Exemple d'utilisation de la route
@app.post("/job/generate_music_from_theme/", tags=['text to music (multiple)'])
async def job_generate_music_from_theme(
        metadata_file: UploadFile = File(...,
                                         description="Fichier Excel avec les paramètres (thème, orientation, taille, etc.)"),
        email_notification: Optional[str] = Form("workinmusic.app@gmail.com")
):
    metadata_path = f"uploads/{metadata_file.filename}"
    save_upload_file(metadata_file, metadata_path)
    os.makedirs("uploads/extracted/", exist_ok=True)
    # Envoyer un email
    send_mail(
        subject="WIM Gen : Job start",
        message=f"Your job has started.",
        recipient_email=email_notification
    )

    job_instance = task_queue.enqueue(
        process_lyrics_from_theme, metadata_path,
        job_timeout=172800, retry=Retry(max=3)
    )

    return {
        "success": True,
        "job_id": job_instance.id
    }
