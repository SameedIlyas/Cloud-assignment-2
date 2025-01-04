import os
from huggingface_hub import snapshot_download
from google.cloud import storage
import torch
import shutil
from pathlib import Path

def download_and_upload_model(
    model_id="OFA-Sys/small-stable-diffusion-v0",
    bucket_name="cloud-assignment-staz",
    local_model_path="./model_cache",
    gcs_model_path="models/stable-diffusion-small"
):
    """
    Downloads a model from Hugging Face and uploads it to Google Cloud Storage.
    
    Args:
        model_id (str): Hugging Face model ID
        bucket_name (str): Google Cloud Storage bucket name
        local_model_path (str): Local path to store the model temporarily
        gcs_model_path (str): Path within the GCS bucket to store the model
    """
    print(f"Downloading model {model_id}...")
    
    # Download model from Hugging Face
    local_dir = snapshot_download(
        repo_id=model_id,
        cache_dir=local_model_path,
        local_dir=local_model_path,
        local_dir_use_symlinks=False
    )
    
    print("Model downloaded successfully!")
    
    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    def upload_folder_to_gcs(local_path, gcs_base_path):
        local_path = Path(local_path)
        for item in local_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(local_path)
                gcs_path = f"{gcs_base_path}/{relative_path}"
                blob = bucket.blob(gcs_path)
                blob.upload_from_filename(str(item))
                print(f"Uploaded {item} to gs://{bucket_name}/{gcs_path}")
    
    print(f"Uploading model to GCS bucket {bucket_name}...")
    upload_folder_to_gcs(local_model_path, gcs_model_path)
    
    # Clean up local files
    print("Cleaning up local files...")
    shutil.rmtree(local_model_path)
    
    print("Model transfer completed successfully!")
    print(f"Model is now available at: gs://{bucket_name}/{gcs_model_path}")

# Example usage
if __name__ == "__main__":
    # Make sure you're authenticated with Google Cloud
    # This should be automatic in Vertex AI Workbench
    
    download_and_upload_model(
        model_id="OFA-Sys/small-stable-diffusion-v0",
        bucket_name="cloud-assignment-staz",  # Replace with your bucket name
        local_model_path="./model_cache",
        gcs_model_path="models/stable-diffusion-small"
    )