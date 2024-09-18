import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

def upload_file_to_s3(file_path, bucket_name, s3_file_name):
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
if __name__ == "__main__":
    file_path = "test.txt"  # Local file path
    bucket_name = "wim-music-upload"  # Replace with your S3 bucket name
    s3_file_name = "generated_musics/uploaded_test_file.txt"  # Desired name in S3, inside the 'generated_musics' folder

    # Call the function and print the public URL
    s3_url = upload_file_to_s3(file_path, bucket_name, s3_file_name)
    if s3_url:
        print(f"Public URL: {s3_url}")

