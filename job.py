import os
import shutil
import time
import zipfile
import pandas as pd
import json
from typing import List, Dict
import rarfile

from inference.infer_extraction import inference, inference_by_theme, inference_without_rag
from utils.extraction_ai import extraire_elements_key_from_context
from utils.googdrive.quickstart import upload_file_in_folder_to_gdrive
from utils.music_generator_ai import generate_music_lyrics, download_file_by_url
from utils.parsers_ai import MusicLyrics
from utils.sunowrapper.generate_song import generate_music, fetch_feed
from utils.tools import format_lyrics_single_refrain, format_lyrics

UPLOAD_DIR = "./uploads"
OUTPUT_DIR = "./output"
ZIP_OUTPUT_DIR = "./zip_outputs"


def process_music_from_docs(file_paths: List[str], metadata_path: str) -> Dict:
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"The file {metadata_path} does not exist.")

    if metadata_path.endswith(".xlsx"):
        df = pd.read_excel(metadata_path)
    else:
        df = pd.read_csv(metadata_path)

    outputs = []

    for index, row in df.iterrows():
        doc_id = str(row['id'])
        orientation = row['orientation']
        niv_detail = 7
        style = row['style']
        langue = row['langue']
        niveau = row['niveau']
        matiere = row['matiere']

        file_path = next((path for path in file_paths if os.path.basename(path).startswith(doc_id)), None)
        if not file_path:
            continue

        data = inference(file_path, orientation=orientation, langue=langue, niveau=niveau, matiere=matiere,
                         k=niv_detail)
        os.remove(file_path)
        elements = data['answer']
        data = generate_music_lyrics(elements=elements, style=style, orientation=orientation, langue=langue)

        out = MusicLyrics.parse_obj(data)
        tmp_dict = out.to_dict()
        tmp_dict['url'] = []
        tmp_dict['langue'] = langue
        tmp_dict["music"] = generate_music(format_lyrics(out.lyrics), out.title, out.style)
        time.sleep(300)

        c = 1
        name = ""
        for music_id in tmp_dict["music"]:
            dat = fetch_feed(music_id)[0]

            audio_url = download_file_by_url(dat['audio_url'])
            image_url = download_file_by_url(dat['image_large_url'])

            name = f"{doc_id}_{style}_{langue}_{matiere}_folder"
            dat["url_drive"] = upload_file_in_folder_to_gdrive(audio_url, f"{doc_id}_v{c}.mp3",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            dat["img_drive"] = upload_file_in_folder_to_gdrive(image_url, f"{doc_id}_v{c}.jpeg",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            tmp_dict['url'].append(dat)
            c += 1

        output_path = os.path.join(OUTPUT_DIR, f"{doc_id}_output.json")

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        upload_file_in_folder_to_gdrive(output_path, f"data.json", '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
        outputs.append(tmp_dict)



    return { "data": outputs}


def process_without_music_from_docs(file_paths: List[str], metadata_path: str) -> Dict:
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"The file {metadata_path} does not exist.")

    if metadata_path.endswith(".xlsx"):
        df = pd.read_excel(metadata_path)
    else:
        df = pd.read_csv(metadata_path)

    outputs = []

    for index, row in df.iterrows():
        doc_id = str(row['id'])
        orientation = row['orientation']
        niv_detail = 7
        style = row['style']
        langue = row['langue']
        niveau = row['niveau']
        matiere = row['matiere']

        file_path = next((path for path in file_paths if os.path.basename(path).startswith(doc_id)), None)
        if not file_path:
            continue

        data = inference_without_rag(file_path, orientation=orientation, langue=langue, niveau=niveau, matiere=matiere,
                                     k=niv_detail)
        os.remove(file_path)
        elements = data
        data = generate_music_lyrics(elements=elements, style=style, orientation=orientation, langue=langue)

        out = MusicLyrics.parse_obj(data)
        tmp_dict = out.to_dict()
        tmp_dict['url'] = []
        tmp_dict['langue'] = langue
        tmp_dict["music"] = generate_music(format_lyrics(out.lyrics), out.title, out.style)
        time.sleep(300)

        c = 1
        name = ""
        for music_id in tmp_dict["music"]:
            dat = fetch_feed(music_id)[0]

            audio_url = download_file_by_url(dat['audio_url'])
            image_url = download_file_by_url(dat['image_large_url'])

            name = f"{doc_id}_without_{style}_{langue}_{matiere}_folder"
            dat["url_drive"] = upload_file_in_folder_to_gdrive(audio_url, f"{doc_id}_v{c}.mp3",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            dat["img_drive"] = upload_file_in_folder_to_gdrive(image_url, f"{doc_id}_v{c}.jpeg",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            tmp_dict['url'].append(dat)
            c += 1

        output_path = os.path.join(OUTPUT_DIR, f"{doc_id}_output.json")

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        upload_file_in_folder_to_gdrive(output_path, f"data.json", '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
        outputs.append(tmp_dict)




    return {"data": outputs}


def process_lyrics_from_theme(metadata_path: str) -> Dict:
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"The file {metadata_path} does not exist.")

    if metadata_path.endswith(".xlsx"):
        df = pd.read_excel(metadata_path)
    else:
        raise ValueError("Le fichier doit être au format Excel (.xlsx)")

    outputs = []

    for index, row in df.iterrows():
        theme = row['theme']
        orientation = row['orientation']
        style = row['style']
        langue = row['langue']
        niveau = row['niveau']
        matiere = row['matiere']

        a = inference_by_theme(theme, orientation, niveau=niveau, matiere=matiere, langue=langue)
        tmp = extraire_elements_key_from_context(a, orientation)

        data = generate_music_lyrics(elements=tmp.content, style=style, langue=langue, orientation=orientation)
        out = MusicLyrics.parse_obj(data)
        tmp_dict = out.to_dict()
        tmp_dict['url'] = []
        tmp_dict['langue'] = langue
        tmp_dict["music"] = generate_music(format_lyrics(out.lyrics), out.title, out.style)
        time.sleep(300)

        c = 1
        name = ""
        for music_id in tmp_dict["music"]:
            dat = fetch_feed(music_id)[0]
            audio_url = download_file_by_url(dat['audio_url'])
            image_url = download_file_by_url(dat['image_large_url'])
            name = dat["title"].replace(' ', '').lower()
            name += f"_{style}_{langue}_{matiere}"
            dat["url_drive"] = upload_file_in_folder_to_gdrive(audio_url,
                                                               f"{dat['title'].replace(' ', '').lower()}_v{c}.mp3",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            dat["img_drive"] = upload_file_in_folder_to_gdrive(image_url,
                                                               f"{dat['title'].replace(' ', '').lower()}_v{c}.jpeg",
                                                               '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
            tmp_dict['url'].append(dat)
            c += 1

        output_path = os.path.join(OUTPUT_DIR, f"{theme.replace(' ', '')}_output.json")

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        upload_file_in_folder_to_gdrive(output_path, f"data.json", '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s', name)
        outputs.append(tmp_dict)



    return { "data": outputs}
