from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date


def upload_file_to_gdrive(file_path, file_name, parent_directory_id):
    # Authenticate using the service account credentials
    gauth = GoogleAuth()
    p=Path.cwd()/"utils"/"googdrive"/"certificates.json"
    print(p.absolute())
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        p.absolute(),
        scopes=['https://www.googleapis.com/auth/drive']
    )

    drive = GoogleDrive(gauth)

    # Upload the file directly to the specified folder
    file_to_upload = drive.CreateFile({'parents': [{"id": parent_directory_id}], 'title': file_name})
    file_to_upload.SetContentFile(file_path)
    file_to_upload.Upload()
    print("\n--------- File is Uploaded ----------")

    # Make the file public and get the shareable link
    file_to_upload.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    # Return the public URL
    public_url = file_to_upload['alternateLink']
    return public_url


def get_folder_id(drive, folder_name, parent_directory_id=None):
    query = f"title = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    if parent_directory_id:
        query += f" and '{parent_directory_id}' in parents"

    file_list = drive.ListFile({'q': query}).GetList()
    if file_list:
        return file_list[0]['id']
    return None


def create_folder_in_gdrive(drive, folder_name, parent_directory_id=None):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_directory_id:
        folder_metadata['parents'] = [{'id': parent_directory_id}]

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    print(f"\n--------- Folder '{folder_name}' Created ----------")

    return folder['id']


def upload_file_in_folder_to_gdrive(file_path, file_name, parent_directory_id, folder_name):
    # Authenticate using the service account credentials
    gauth = GoogleAuth()
    p = Path.cwd() / "utils" / "googdrive" / "certificates.json"
    print(p.absolute())
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        p.absolute(),
        scopes=['https://www.googleapis.com/auth/drive']
    )

    drive = GoogleDrive(gauth)

    # Check if the folder already exists
    folder_id = get_folder_id(drive, folder_name, parent_directory_id)

    # If the folder does not exist, create it
    if not folder_id:
        folder_id = create_folder_in_gdrive(drive, folder_name, parent_directory_id)

    # Upload the file to the folder
    file_to_upload = drive.CreateFile({'parents': [{"id": folder_id}], 'title': file_name})
    file_to_upload.SetContentFile(file_path)
    file_to_upload.Upload()
    print("\n--------- File is Uploaded ----------")

    # Make the file public and get the shareable link
    file_to_upload.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    # Return the public URL
    public_url = file_to_upload['alternateLink']
    return public_url

# Example usage
#f=upload_file_to_gdrive('./Rapport_7_Juin_2024.pdf', 'rapport.pdf', '1GKdhuP-dnsHQgmhgKoYAVDlscWbLZ-2s')

#print(f)


