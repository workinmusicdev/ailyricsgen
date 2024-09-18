from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

def upload_file_to_gdrive(file_path, file_name, parent_directory_id):
    # Authenticate using the service account credentials
    gauth = GoogleAuth()
    p = Path.cwd() / "utils" / "googdrive" / "certificates.json"
    
    # Print the absolute path of the credentials file for debugging
    print(f"Using credentials file at: {p.absolute()}")
    
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        p.absolute(),
        scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.appdata', 'https://www.googleapis.com/auth/drive.metadata.readonly']
    )

    drive = GoogleDrive(gauth)

    # Upload the file to the specified folder
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

# Test the upload function
if __name__ == "__main__":
    # Define the file to upload and the target folder ID
    file_path = "test.txt"  # Local file to upload
    file_name = "Uploaded_Test_File.txt"  # Name of the file in Google Drive
    parent_directory_id = "1tIK3iYywsTc_gDLs0DP8kOe7OjYwLhMT"  # Replace with your folder ID

    # Call the function and print the public link
    public_url = upload_file_to_gdrive(file_path, file_name, parent_directory_id)
    print(f"Public URL of uploaded file: {public_url}")
