import os
import shutil
import time

import pandas as pd
import json
from typing import List, Dict

from inference.infer_extraction import inference, inference_by_theme, inference_without_rag
from utils.extraction_ai import extraire_elements_key_from_context
from utils.googdrive.quickstart import upload_file_in_folder_to_gdrive, upload_file_to_s3
from utils.music_generator_ai import generate_music_lyrics, download_file_by_url
from utils.parsers_ai import MusicLyrics
from utils.sunowrapper.generate_song import generate_music, fetch_feed
from utils.tools import  format_lyrics

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

        #
        print("doc_id, orientation, style, langue, niveau, matiere")
        print(doc_id, orientation, style, langue, niveau, matiere)
        print("doc_id, orientation, style, langue, niveau, matiere")

        file_path = next((path for path in file_paths if os.path.basename(path).startswith(doc_id)), None)
        print(file_path)
        if not file_path:
            print("No file found !")
            continue

        data = inference(file_path, orientation=orientation, langue=langue, niveau=niveau, matiere=matiere,
                         k=niv_detail)
        
        print('data')
        print(data)
        print('data')

        os.remove(file_path)
        elements = data['answer']
        data = generate_music_lyrics(elements=elements, style=style, orientation=orientation, langue=langue)

        print("data")
        print(data)

        out = MusicLyrics.parse_obj(data)
        print(out)

        tmp_dict = out.to_dict()
        print("tmp_dict")
        print(tmp_dict)
        print("tmp_dict")


        tmp_dict['url'] = []
        tmp_dict['langue'] = langue
        tmp_dict["music"] = generate_music(format_lyrics(out.lyrics), out.title, out.style)

        print("tmp_dict")
        print(tmp_dict)
        print("tmp_dict")
        print("BEFORE THE SLEEPING  <-------------> STEP 1 achieved")
        time.sleep(500)

        c = 1
        name = ""

        for music_id in tmp_dict["music"]:
            print(music_id)
            print('fetching feed')
            dat = fetch_feed(music_id)[0]

            audio_url = download_file_by_url(dat['audio_url'])
            image_url = download_file_by_url(dat['image_large_url'])

            name = f"{doc_id}_{style}_{langue}_{matiere}_folder"
            print(name)
            dat["url_drive"] = upload_file_to_s3(audio_url, f"{doc_id}_v{c}.mp3", name)
            dat["img_drive"] = upload_file_to_s3(image_url, f"{doc_id}_v{c}.jpeg", name)
            tmp_dict['url'].append(dat)
            c += 1

        output_path = os.path.join(OUTPUT_DIR, f"{doc_id}_output.json")

        with open(output_path, "w", encoding="utf-8") as json_file: # 1tIK3iYywsTc_gDLs0DP8kOe7OjYwLhMT
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        upload_file_to_s3(output_path, f"data.json",  name)
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
        time.sleep(500)

        c = 1
        name = ""
        for music_id in tmp_dict["music"]:
            dat = fetch_feed(music_id)[0]

            audio_url = download_file_by_url(dat['audio_url'])
            image_url = download_file_by_url(dat['image_large_url'])

            name = f"{doc_id}_without_{style}_{langue}_{matiere}_folder"
            dat["url_drive"] = upload_file_to_s3(audio_url, f"{doc_id}_v{c}.mp3", name)
            dat["img_drive"] = upload_file_to_s3(image_url, f"{doc_id}_v{c}.jpeg", name)
            tmp_dict['url'].append(dat)
            c += 1

        output_path = os.path.join(OUTPUT_DIR, f"{doc_id}_output.json")

        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        upload_file_to_s3(output_path, f"data.json", name)
        outputs.append(tmp_dict)


    return {"data": outputs}



import os
import pandas as pd
from typing import Dict

def process_lyrics_from_theme(metadata_path: str) -> None:
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"The file {metadata_path} does not exist.")

    if not metadata_path.endswith(".xlsx"):
        raise ValueError("Le fichier doit être au format Excel (.xlsx)")
    
    output_path = "output.xlsx"
    # Vérifier et forcer l'extension .xlsx pour output_path
    # if not output_path.endswith(".xlsx"):
    #     output_path += ".xlsx"

    df = pd.read_excel(metadata_path)
    df.insert(0, "id", range(1,len(df)+1))  # Ajout de la colonne id
    df["lyrics"] = ""  # Initialisation de la colonne lyrics

    save_interval = 10  # Sauvegarde toutes les 10 entrées
    
    for index, row in df.iterrows():
        try:
            # id_row = str(row["id"])  # La colonne id existe maintenant
            theme = row["theme"]
            orientation = row["orientation"]
            style = row["style"]
            langue = row["langue"]
            niveau = row["niveau"]
            matiere = row["matiere"]

            a = inference_by_theme(theme, orientation, niveau=niveau, matiere=matiere, langue=langue)
            tmp = extraire_elements_key_from_context(a, orientation)
            data = generate_music_lyrics(elements=tmp.content, style=style, langue=langue, orientation=orientation, theme=theme, niveau=niveau)
            out = MusicLyrics.parse_obj(data)
            
            df.at[index, "lyrics"] = out.lyrics  # Ajout des lyrics dans la colonne
            
            print(f"Résultat généré pour {index} - Lyrics ajoutés")
    
        except Exception as e:
            print(e)
            print(f"Erreur lors du traitement de l'entrée {index}: {e}")
        
        if (index + 1) % save_interval == 0:
            df.to_excel(output_path, index=False)  # Sauvegarde périodique
            print(f"Progression sauvegardée à {output_path}")
    
    df.to_excel(output_path, index=False)  # Enregistrement final
    print(f"Fichier final sauvegardé : {output_path}")




# The one which generate songs from themes
# def process_lyrics_from_theme(metadata_path: str) -> Dict:
#     if not os.path.exists(metadata_path):
#         raise FileNotFoundError(f"The file {metadata_path} does not exist.")

#     if metadata_path.endswith(".xlsx"):
#         df = pd.read_excel(metadata_path)
#     else:
#         raise ValueError("Le fichier doit être au format Excel (.xlsx)")

#     outputs = []

#     for index, row in df.iterrows():
        
#         id_row = str(row.get('id', ''))
#         theme = id_row +'_'+ row['theme']
#         orientation = row['orientation']
#         style = row['style']
#         langue = row['langue']
#         niveau = row['niveau']
#         matiere = row['matiere']

#         a = inference_by_theme(theme, orientation, niveau=niveau, matiere=matiere, langue=langue)

#         print("------------------------------ A")
#         print(a)
#         print('------------------------------ A')
#         tmp = extraire_elements_key_from_context(a, orientation)

#         data = generate_music_lyrics(elements=tmp.content, style=style, langue=langue, orientation=orientation, theme=theme, niveau=niveau)
#         print("------------------------------")
#         print(data)
#         print('------------------------------')

#         out = MusicLyrics.parse_obj(data)
#         tmp_dict = out.to_dict()
#         tmp_dict['url'] = []
#         tmp_dict['langue'] = langue


#         # resultat = generate_music(format_lyrics(out.lyrics), out.title, out.style)

#         print(f"resultat Gen {id_row} ------------------ Done :")
#         # print(resultat)
#         print(f"resultat Gen {id_row} ------------------ Done :")

#         time.sleep(5)

        # c = 1
        # name = ""
        # for music_id in tmp_dict["music"]:
        #     dat = fetch_feed(music_id)[0]
        #     audio_url = download_file_by_url(dat['audio_url'])
        #     image_url = download_file_by_url(dat['image_large_url'])
        #     name = id_row + '_' + dat["title"].replace(' ', '').lower()
        #     name += f"_{style}_{langue}_{matiere}"
        #     dat["url_drive"] = upload_file_to_s3(audio_url,f"{dat['title'].replace(' ', '').lower()}_v{c}.mp3", name)
        #     dat["img_drive"] = upload_file_to_s3(image_url,f"{dat['title'].replace(' ', '').lower()}_v{c}.jpeg",name)
        #     tmp_dict['url'].append(dat)
        #     c += 1

        # output_path = os.path.join(OUTPUT_DIR, f"{theme.replace(' ', '')}_output.json")

        # with open(output_path, "w", encoding="utf-8") as json_file:
        #     json.dump(tmp_dict, json_file, ensure_ascii=False, indent=4)
        # upload_file_to_s3(output_path, f"data.json", name)
        # outputs.append(tmp_dict)



    # return { "data": outputs}
