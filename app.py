import json
import subprocess
import sys
import time
import zipfile
from pyunpack import Archive
import aiofiles
import boto3
from botocore.exceptions import NoCredentialsError
from utils.email_notifier import send_mail
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import shutil
import os
from redis import Redis
from rq import Queue
from starlette.responses import FileResponse, JSONResponse
from inference.infer_extraction import inference, inference_by_theme
from job import process_music_from_docs, process_lyrics_from_theme, process_without_music_from_docs
from models.data_input import GenerateMusicRequest
from utils.extraction_ai import extraire_elements_key_from_context, format_to_human
from utils.googdrive.quickstart import upload_file_to_gdrive, upload_file_in_folder_to_gdrive, upload_file_to_s3
from utils.music_generator_ai import generate_music_lyrics, download_file_by_url
from utils.parsers_ai import MusicLyrics
from utils.sunowrapper.generate_song import fetch_feed, generate_music
from utils.tools import format_lyrics_single_refrain, format_lyrics_single_refrain
from rq.job import Job, Retry
from rq.registry import StartedJobRegistry, FinishedJobRegistry
import logging

load_dotenv()
app = FastAPI()

# Lire les variables d'environnement pour la configuration de Redis
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

redis_conn = Redis(host=redis_host, port=redis_port)
task_queue = Queue("task_queue", connection=redis_conn, default_timeout=172800)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./output"
ZIP_OUTPUT_DIR = "zip_outputs/"
TEMP_DIR = "/media"

# Configure AWS S3
S3_BUCKET = "wimbucketstorage"
s3_client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(ZIP_OUTPUT_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    logging.info(f"Saving file '{upload_file.filename}' to {destination}")
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logging.info(f"File '{upload_file.filename}' successfully saved to {destination}")
    except Exception as e:
        logging.error(f"Error saving file '{upload_file.filename}': {e}")
    finally:
        upload_file.file.close()
    return destination


def extract_files(archive_path: str, extract_to: str, filename: str) -> List[str]:
    logging.info(f"Extracting archive '{archive_path}' to {extract_to}")
    try:
        Archive(archive_path).extractall(extract_to)
        logging.info(f"Archive '{archive_path}' successfully extracted to {extract_to}")
    except Exception as e:
        logging.error(f"Error extracting archive '{archive_path}': {e}")
        raise e  # Raise the exception to ensure the error is propagated
    
    extract_to = os.path.join(extract_to, filename)
    return [os.path.join(extract_to, file) for file in os.listdir(extract_to)]


@app.post("/job/generate_music_from_docs/", tags=['text to music (multiple)'])
async def job_generate_music_from_docs(
        document_archive: UploadFile = File(..., description="Le fichier ZIP ou RAR contenant les documents à traiter"),
        metadata_file: UploadFile = File(..., description="Fichier Excel ou CSV avec les paramètres d'orientation, taille, style, etc."),
        email_notification: Optional[str] = Form("workinmusic.app@gmail.com")
):
    logging.info("Job 'generate_music_from_docs' started")
    
    # Save the uploaded archive file
    archive_path = os.path.join(UPLOAD_DIR, document_archive.filename)
    logging.info(f"Saving uploaded archive to '{archive_path}'")
    save_upload_file(document_archive, archive_path)

    # Extract the archive file
    extract_to = os.path.join(UPLOAD_DIR, os.path.splitext(document_archive.filename)[0])
    os.makedirs(extract_to, exist_ok=True)
    logging.info(f"Extracting archive to '{extract_to}'")
    document_paths = extract_files(archive_path, extract_to,os.path.splitext(document_archive.filename)[0])

    # Check if the files exist and log the result
    for path in document_paths:
        if not os.path.exists(path):
            logging.warning(f"File not found: {path}")
        else:
            logging.info(f"File exists: {path}")

    # Save the metadata file
    metadata_path = os.path.join(UPLOAD_DIR, metadata_file.filename)
    logging.info(f"Saving metadata file to '{metadata_path}'")
    save_upload_file(metadata_file, metadata_path)

    # Send email notification
    logging.info(f"Sending start job notification to '{email_notification}'")
    send_mail(
        subject="WIM Gen : Job start",
        message=f"Your job has started with {len(document_paths)} files.",
        recipient_email=email_notification
    )

    # Enqueue the job
    logging.info(f"Enqueuing job for processing")
    job_instance = task_queue.enqueue(
        process_music_from_docs, document_paths, metadata_path,
        job_timeout=172800, retry=Retry(max=3)
    )

    logging.info(f"Job successfully enqueued with ID '{job_instance.id}'")

    return {
        "success": True,
        "job_id": job_instance.id
    }



@app.post("/job/generate_music_without_docs/", tags=['text to music (multiple)'])
async def job_generate_music_without_docs(
        document_archive: UploadFile = File(..., description="Le fichier ZIP ou RAR contenant les documents à traiter"),
        metadata_file: UploadFile = File(...,
                                         description="Fichier Excel ou CSV avec les paramètres d'orientation, taille, style, etc."),
        email_notification: Optional[str] = Form("workinmusic.app@gmail.com")
):
    # Save the uploaded archive file
    archive_path = os.path.join(UPLOAD_DIR, document_archive.filename)
    save_upload_file(document_archive, archive_path)

    # Extract the archive file
    extract_to = os.path.join(UPLOAD_DIR, os.path.splitext(document_archive.filename)[0])
    os.makedirs(extract_to, exist_ok=True)
    document_paths = extract_files(archive_path, extract_to, os.path.splitext(document_archive.filename)[0])

    # Check if the files exist and print a message if they don't
    for path in document_paths:
        if not os.path.exists(path):
            print(f"File not found: {path}")
        else:
            print(f"File exists: {path}")

    # Save the metadata file
    metadata_path = os.path.join(UPLOAD_DIR, metadata_file.filename)
    save_upload_file(metadata_file, metadata_path)

    send_mail(
        subject="WIM Gen : Job start",
        message=f"Your job has started with {len(document_paths)} files.",
        recipient_email=email_notification
    )

    job_instance = task_queue.enqueue(
        process_without_music_from_docs, document_paths, metadata_path,
        job_timeout=172800, retry=Retry(max=3)
    )

    return {
        "success": True,
        "job_id": job_instance.id
    }


# Here first 
@app.post("/job/generate_music_from_theme/", tags=['text to music (multiple)'])
async def job_generate_music_from_theme(
        metadata_file: UploadFile = File(...,
                                         description="Fichier Excel avec les paramètres (thème, orientation, taille, etc.)"),
        email_notification: Optional[str] = Form("workinmusic.app@gmail.com")
):
    metadata_path = os.path.join(UPLOAD_DIR, metadata_file.filename)
    save_upload_file(metadata_file, metadata_path)
    # os.makedirs("generated_step1.xlsx", exist_ok=True)

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


@app.get("/job/status/{job_id}", tags=["job"])
async def get_job_status(job_id: str):
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


@app.get("/download/{file_name}", tags=['ressource'])
async def download_file(file_name: str):
    file_path = os.path.join(ZIP_OUTPUT_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    return JSONResponse(content={"message": "File not found"}, status_code=404)


@app.post("/generation/callback", tags=["debug"])
async def handle_generation_callback(body: dict):
    # Affiche le contenu du body dans la console
    print(body)

    data = body.get('data', {}).get('data', [])

    c = 1

    for music in data:

        tmp_dict = {}
        tmp_dict['url'] = []
        tmp_dict['langue'] = music.get('langue', "")
        tmp_dict['title'] = music.get('title', "")
        tmp_dict['tags'] = music.get('tags', "")
        tmp_dict['prompt'] = music.get('prompt', "")
        tmp_dict['source_audio_url'] = music.get('source_audio_url', "")
        tmp_dict['source_image_url'] = music.get('source_image_url', "")
        tmp_dict['stream_audio_url'] = music.get('stream_audio_url', "")
        tmp_dict['source_stream_audio_url'] = music.get('source_stream_audio_url', "")
        tmp_dict['duration'] = music.get('duration', "")
        tmp_dict['model_name'] = music.get('model_name', "")

        # Si audio_url est manquant, utiliser stream_audio_url
        audio_url_original = music.get('audio_url') or music.get('stream_audio_url')
        audio_url = download_file_by_url(audio_url_original)

        image_url_original = music.get('image_url') or music.get('source_image_url')
        image_url = download_file_by_url(image_url_original)

        name = music.get('title', f"music_{c}")
        safe_name = name.replace(' ', '').lower()

        url_drive = upload_file_to_s3(audio_url, f"{safe_name}_{c}.mp3", name)
        img_drive = upload_file_to_s3(image_url, f"{safe_name}_{c}.jpeg", name)

        tmp_dict['url'].append({
            "url_drive": url_drive,
            "img_drive": img_drive,
            "audio_url": audio_url_original,
            "image_url": image_url_original,
            "title": music.get('title', ""),
            "duration": music.get('duration', ""),
        })

        output_path = os.path.join(OUTPUT_DIR, f"{safe_name}_output.json")

        c += 1

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)

        upload_file_to_s3(output_path, f"data.json", name)



if __name__ == "__main__":
    import uvicorn
    import subprocess

    from redis import Redis
    from rq import Queue

    redis_conn = Redis(host="localhost", port=6379)
    task_queue = Queue("task_queue", connection=redis_conn)

    # Vider la file d'attente
    task_queue.empty()
    print("File d'attente vidée avec succès")

    # Start the worker in a separate process
    worker_process = subprocess.Popen(["rq", "worker", "task_queue"])
    # worker_process = subprocess.Popen([sys.executable, "-m", "rq", "worker", "task_queue"])

    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)

    # Ensure the worker process is terminated when the main process exits
    worker_process.wait()
