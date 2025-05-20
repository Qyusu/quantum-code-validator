import json
import os
import pathlib
from pathlib import Path
from typing import Optional

from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account

from src.constants import REF_DOCS_DIR


def get_credentials() -> service_account.Credentials:
    """
    Retrieve Google Cloud credentials.

    Returns:
        service_account.Credentials: Credentials object

    Raises:
        KeyError: If GOOGLE_CREDENTIALS_JSON environment variable is not set
        json.JSONDecodeError: If the credentials JSON is malformed
    """
    try:
        sa_info = json.loads(os.environ["GOOGLE_CREDENTIALS_JSON"])
        return service_account.Credentials.from_service_account_info(sa_info)
    except KeyError:
        raise KeyError("GOOGLE_CREDENTIALS_JSON environment variable is not set")
    except json.JSONDecodeError:
        raise ValueError("Invalid credentials JSON format")


def initialize_storage_client(
    credentials: service_account.Credentials, bucket_name: str, prefix: Optional[str] = None
) -> tuple[storage.Client, storage.Bucket, str]:
    """
    Initialize the storage client.

    Args:
        credentials: Authentication credentials
        bucket_name: Name of the GCS bucket
        prefix: Object prefix (optional)

    Returns:
        tuple[storage.Client, storage.Bucket, str]: Tuple of client, bucket, and prefix

    Raises:
        GoogleCloudError: If client initialization fails
    """
    try:
        client = storage.Client(credentials=credentials)
        bucket = client.bucket(bucket_name)
        prefix = prefix or ""
        return client, bucket, prefix
    except GoogleCloudError as e:
        raise GoogleCloudError(f"Failed to initialize storage client: {str(e)}")


def download_blob(blob: storage.Blob, prefix: str, download_dir: Path = REF_DOCS_DIR) -> None:
    """
    Download the specified blob to local storage.

    Args:
        blob: Blob to download
        prefix: Object prefix
        download_dir: Local download directory

    Raises:
        GoogleCloudError: If download fails
    """
    try:
        blob_name = str(blob.name)  # Explicitly convert to string
        relative_path = blob_name[len(prefix) :] if prefix else blob_name
        local_path = download_dir / relative_path

        # Create directory if it doesn't exist
        pathlib.Path(local_path).parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        blob.download_to_filename(local_path)
        print(f"✅ Downloaded: {blob_name} → {local_path}")
    except GoogleCloudError as e:
        raise GoogleCloudError(f"Failed to download file {blob.name}: {str(e)}")


def main() -> None:
    """
    Main execution function.
    """
    try:
        # Get credentials
        credentials = get_credentials()

        # Get configuration from environment variables
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("GCS_BUCKET_NAME environment variable is not set")

        prefix = os.getenv("GCS_PREFIX", "")

        # Initialize storage client
        _, bucket, prefix = initialize_storage_client(credentials=credentials, bucket_name=bucket_name, prefix=prefix)

        # Download files
        blobs = bucket.list_blobs(prefix=prefix)
        for blob in blobs:
            download_blob(blob, prefix)

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
