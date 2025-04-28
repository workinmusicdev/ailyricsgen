from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials

from datetime import date
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

def upload_file_to_s3(file_path, s3_file_name, folder):  #, bucket_name, s3_file_name):

    """
    Uploads a file to the specified S3 bucket in the 'generated_musics' folder.

    :param file_path: Path to the file to upload
    :param bucket_name: Name of the S3 bucket
    :param s3_file_name: Desired name of the file in the S3 bucket (with folder path)
    :return: The S3 URL of the uploaded file if successful, None otherwise
    """

    # Initialize the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION'),
    )

    try:
        # Upload the file with folder path (e.g., generated_musics/uploaded_test_file.txt)
        bucket_name = "wim-music-upload"
        s3_file_name = f"POP CLASSIQUE_V4/MODULE 10 _ Kit de survie express/{folder}/{s3_file_name}"
        s3.upload_file(file_path, bucket_name, s3_file_name)
        print(f"File '{file_path}' uploaded to '{bucket_name}' as '{s3_file_name}'")

        # Create a public URL for the file
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_file_name}"
        return s3_url
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None


# Test the upload function
# if __name__ == "__main__":
#     file_path = "test.txt"  # Local file path
#     bucket_name = "wim-music-upload"  # Replace with your S3 bucket name
#     s3_file_name = "generated_musics/uploaded_test_file.txt"  # Desired name in S3, inside the 'generated_musics' folder

#     # Call the function and print the public URL
#     s3_url = upload_file_to_s3(file_path, bucket_name, s3_file_name)
#     if s3_url:
#         print(f"Public URL: {s3_url}")




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

def check_file_exists(drive, file_name, folder_id):
    # Function to check if a file with the same name exists in the folder
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    for file in file_list:
        if file['title'] == file_name:
            return True
    return False

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

    # Check if the file already exists in the folder
    if check_file_exists(drive, file_name, folder_id):
        print("\n--------- File already exists in Google Drive ----------")
        return None

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


