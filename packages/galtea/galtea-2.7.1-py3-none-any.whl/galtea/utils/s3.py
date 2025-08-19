import os

import requests


def upload_file_to_s3(file_path: str, presigned_url: str) -> bool:
    # Extract the file name from the presigned URL
    with open(file_path, "rb") as file_data:
        file_content = file_data.read()

        headers = {"Content-Type": "application/octet-stream"}
        response = requests.put(presigned_url, data=file_content, headers=headers)

        response.raise_for_status()

        return response.status_code == 200 or response.status_code == 204


def download_file_from_s3(presigned_url: str, file_name: str, destination_path: str) -> bool:
    try:
        # Create output directory if it doesn't exist
        os.makedirs(destination_path, exist_ok=True)

        # Get the filename from the URI
        filename = os.path.basename(file_name)
        file_path = os.path.join(destination_path, filename)

        # Send a GET request to the pre-signed URL
        response = requests.get(presigned_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Write the content to the file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"File downloaded successfully to: {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
    except OSError as e:
        print(f"Error creating directory or writing file: {e}")

    return file_path
