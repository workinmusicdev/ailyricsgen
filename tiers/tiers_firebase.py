import os

import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import firestore
from firebase import firebase

from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate('./ServiceAccountWim.json')
default_app = firebase_admin.initialize_app(cred,{
    'storageBucket': os.environ.get('STORAGE_BUCKET')  # Assurez-vous que STORAGE_BUCKET est défini dans votre fichier .env
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


def get_list_collection(collection_ref):
    """
    Charge tous les documents dans une collection et les retourne sous forme de liste.

    :param collection_ref: Référence de la collection
    :return: Liste des documents dans la collection
    """
    docs = collection_ref.get()
    return [doc.to_dict() for doc in docs]


def filter_collection(collection_ref, field, operation, value):
    """
    Filtre une collection selon un champ, une opération et une valeur spécifique.

    :param collection_ref: Référence de la collection
    :param field: Champ à filtrer
    :param operation: Opération de filtre (par ex. "==", ">", "<=", etc.)
    :param value: Valeur pour le filtre
    :return: Liste des documents filtrés
    """
    query = collection_ref.where(field, operation, value).get()
    return [doc.to_dict() for doc in query]


def upload_file(local_file_path, storage_file_path):
    """
    Télécharge un fichier local vers Firebase Storage.

    :param local_file_path: Chemin du fichier local
    :param storage_file_path: Chemin du fichier dans Firebase Storage
    :return: URL de téléchargement du fichier stocké
    """
    blob = bucket.blob(storage_file_path)
    blob.upload_from_filename(local_file_path)
    blob.make_public()
    return blob.public_url


def download_file(storage_file_path, local_file_path):
    """
    Télécharge un fichier de Firebase Storage vers le système local.

    :param storage_file_path: Chemin du fichier dans Firebase Storage
    :param local_file_path: Chemin du fichier local
    """
    blob = bucket.blob(storage_file_path)
    blob.download_to_filename(local_file_path)


def list_files(prefix=None):
    """
    Liste tous les fichiers dans Firebase Storage avec un préfixe donné.

    :param prefix: Préfixe pour filtrer les fichiers
    :return: Liste des chemins des fichiers
    """
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs]

## Teste
if __name__=="__main__":
    # Tester les fonctions
    #print(list_files())
    #print(upload_file("t.mp3","tenor.mp3"))
    matiere = "Economie"
    style = "POP"
    pop_economie=get_collection(matiere,style)
    print(get_list_collection(pop_economie))

