"""Manage API calls and IO procedures."""
# flake8: noqa: E402

import logging

logger = logging.getLogger(__name__)

import os
import tempfile
from pathlib import Path

from google.cloud import bigquery, storage


def get_bq_client(params):
    """Get Google BigQuery client."""
    bq_client = bigquery.Client(project=params["g_ai_project_name"])
    job_config = bigquery.QueryJobConfig(
        allow_large_results=True,
        # flatten_results=True,
        labels={"project-name": params["project_name"]},
    )
    return bq_client, job_config


def upload_pdf_to_bucket(params, content, file_name):
    """Upload bytes content to GCS bucket.

    Args:
        params (dict): Parameters dictionary containing project ID and bucket name.
        content (bytes): Content of the file to be uploaded.
        file_name (str): Name of the file to be uploaded.
    """
    try:
        # Create a temporary file to store the content
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)

        # Write the content to the temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        # Upload the temporary file to the bucket
        client = storage.Client(project=params["doc_ai_bucket_project_name"])
        bucket = client.bucket(params["doc_ai_bucket_batch_input"])

        blob = bucket.blob(file_name)
        blob.upload_from_filename(temp_file_path)

        # Delete the temporary file
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        return f"gs://{params['doc_ai_bucket_batch_input']}/{file_name}", client  # noqa

    except Exception as e:
        print(
            f"Error uploading {file_name} to bucket {params['doc_ai_bucket_batch_input']}: {e}"
        )
        return None, None


def delete_folder_from_bucket(params, bucket_name, folder_name):
    """Delete a folder (prefix) and its contents from a GCS bucket.

    Args:
        bucket_name (str): Name of the GCS bucket.
        folder_name (str): Name of the folder (prefix) to delete.
    """
    try:
        client = storage.Client(project=params["doc_ai_bucket_project_name"])
        bucket = client.get_bucket(bucket_name)

        # List all objects with the given prefix (folder name)
        blobs = bucket.list_blobs(prefix=folder_name)

        # Delete each object
        for blob in blobs:
            blob.delete()

    except Exception as e:
        logger.error(
            f"Error deleting folder {folder_name} from bucket {bucket_name}: {e}"
        )


def get_storage_client(params) -> storage.Client:
    """Get Google Storage client."""
    return storage.Client(project=params["doc_ai_bucket_project_name"])


def download_dir_from_bucket(bucket, directory_cloud, directory_local) -> bool:
    """Download file from Google blob storage.

    Args:
        bucket: Google Storage bucket object
        directory_cloud: directory to download
        directory_local: directory where to download

    Returns:
        bool: True if folder is not exists and not empty
    """
    result = False
    blobs = bucket.list_blobs(prefix=directory_cloud)  # Get list of files
    for blob in blobs:
        result = True
        if blob.name.endswith("/"):
            continue
        file_split = blob.name.split("/")
        directory = "/".join(file_split[0:-1])
        directory = directory_local / Path(directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(directory_local / Path(blob.name))
    return result
