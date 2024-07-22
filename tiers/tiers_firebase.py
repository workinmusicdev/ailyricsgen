import os
from decimal import Decimal

import firebase_admin
import pandas as pd
from firebase_admin import credentials, storage
from firebase_admin import firestore
from firebase import firebase
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

buck="gs://workinmusic-30b37.appspot.com"


cred = credentials.Certificate('./ServiceAccountWim.json')
default_app = firebase_admin.initialize_app(cred,{
    'storageBucket': buck # Assurez-vous que STORAGE_BUCKET est défini dans votre fichier .env
})
store = firestore.client()
bucket = storage.bucket()


#project_name=os.environ.get("PROJECT_NAME")
#db_url=f"https://{project_name}.firebaseio.com"
#firebase = firebase.FirebaseApplication(db_url, None)

#doc_ref=store.collection("matieres")
#docs=doc_ref.get()
#for doc in docs:
#    rap_collection = doc_ref.document(doc.id).collection("RAP").get()
#    for rap_doc in rap_collection:
 #       print(f"Rap : {rap_doc.id} {rap_doc.to_dict()}")


def get_collection(doc_id, collection_id):
    """
    Récupère une sous-collection pour un document spécifique.

    :param doc_id: Nom du document (matière)
    :param collection_id: Nom de la sous-collection (style de musique)
    :return: La sous-collection
    """
    return store.collection("matieres").document(doc_id).collection(collection_id)


def get_list_collection(collection_ref, matiere, style):
    """
    Charge tous les documents dans une collection et les retourne sous forme de liste.

    :param collection_ref: Référence de la collection
    :param matiere: Nom de la matière
    :param style: Nom du style de musique
    :return: Liste des documents dans la collection
    """
    docs = collection_ref.get()
    data = []
    for doc in docs:
        item = doc.to_dict()
        item['matiere'] = matiere  # Ajouter la matière
        item['style_enreg'] = style  # Ajouter le style

        data.append(item)
    return data


def clean_data(data):
    """
    Nettoie les données pour s'assurer que les colonnes numériques sont correctement formatées et que les dates sont sans fuseaux horaires.

    :param data: Liste de dictionnaires contenant les données
    :return: Liste de dictionnaires nettoyée
    """
    required_fields = [
        'id', 'beatmaker', 'classe', 'date_created', 'duree_enreg', 'ecoutes',
        'interprete', 'isFree', 'lyrics_enreg', 'style_enreg', 'theme',
        'url_enreg', 'url_img', 'url_mp3', 'matiere'
    ]
    cleaned_data = []
    for item in data:
        cleaned_item = {}
        for field in required_fields:
            if field in item:
                value = item[field]
                if isinstance(value, datetime):
                    cleaned_item[field] = value.replace(tzinfo=None)  # Remove timezone info
                elif isinstance(value, (int, float, Decimal)):
                    cleaned_item[field] = value  # Ensure numeric values are correctly formatted
                elif isinstance(value, str):
                    cleaned_item[field] = value  # Keep as string if not convertible
                else:
                    cleaned_item[field] = value
            else:
                cleaned_item[field] = None  # Set missing fields to None
        # Ajout de la colonne isFree si elle n'existe pas
        if 'isFree' not in cleaned_item:
            cleaned_item['isFree'] = False  # ou toute valeur par défaut appropriée
        cleaned_data.append(cleaned_item)
    return cleaned_data


def save_to_excel(data, output_path):
    """
    Enregistre une liste de dictionnaires dans un fichier Excel.

    :param data: Liste de dictionnaires contenant les données
    :param output_path: Chemin du fichier Excel à créer
    """
    cleaned_data = clean_data(data)
    df = pd.DataFrame(cleaned_data)
    df.to_excel(output_path, index=False)
    print(f'Data saved to {output_path}')


## Teste
if __name__ == "__main__":
    # Liste des matières et des styles
    matieres = [
        "Anglais",
        "Anglais2",
        "Bonus",
        "Economie",
        "Espagnol",
        "Geographie",
        "Histoire",
        "Mathematiques",
        "Philosophie",
        "SVT"
    ]

    styles = [
        "POP",
        "RAP",
        "ZOUK"
    ]

    all_data = []

    for matiere in matieres:
        for style in styles:
            collection = get_collection(matiere, style)
            data = get_list_collection(collection, matiere, style)
            all_data.extend(data)

    # Affichage des données
    print(len(all_data))

    # Sauvegarde des données dans un fichier Excel
    save_to_excel(all_data, 'music_data.xlsx')