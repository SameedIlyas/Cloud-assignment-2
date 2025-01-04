import os
from google.cloud import storage
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from diffusers import StableDiffusionPipeline, EulerDiscreteScheduler
import torch
from PIL import Image
import io
import time
from typing import Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GCS client
storage_client = storage.Client()

# Download model files from GCS and set up the local model directory
def download_model_from_gcs(bucket_name: str, model_path: str, local_dir: str):
    """Download all files from a GCS bucket model path to a local directory."""
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=model_path)
    
    for blob in blobs:
        local_file_path = os.path.join(local_dir, os.path.relpath(blob.name, model_path))
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        blob.download_to_filename(local_file_path)

# Define model location and local paths
bucket_name = "cloud-assignment-staz"
model_path = "models/stable-diffusion-small"  # e.g., "models/stable-diffusion-2"
local_model_dir = "./stable-diffusion-model"
images_path = "generated_images"

# Download model from GCS
download_model_from_gcs(bucket_name, model_path, local_model_dir)

# Initialize the model
scheduler = EulerDiscreteScheduler.from_pretrained(local_model_dir, subfolder="scheduler")
pipe = StableDiffusionPipeline.from_pretrained(
    local_model_dir,
    scheduler=scheduler,
    torch_dtype=torch.float32  # Use float32 for CPU
)
pipe = pipe.to("cpu")  # Ensure the pipeline uses the CPU

class PromptRequest(BaseModel):
    prompt: str

def save_image_to_gcs(image: Image.Image, bucket_name: str, image_path: str) -> str:
    """Save PIL Image to Google Cloud Storage and return public URL."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(image_path)
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Upload to GCS
    blob.upload_from_string(
        img_byte_arr,
        content_type='image/png'
    )

    return f"https://storage.googleapis.com/{bucket_name}/{image_path}"

@app.post("/generate-image")
async def generate_image(request: PromptRequest):
    try:
        # Generate image from prompt with limited inference steps
        image = pipe(
            request.prompt, 
            num_inference_steps=10
        ).images[0]
        
        # Create image filename from prompt
        timestamp = int(time.time())
        filename = f"{request.prompt.replace(' ', '_')}_{timestamp}.png"
        image_path = f"{images_path}/{filename}"
        
        # Save image to GCS and get URL
        image_url = save_image_to_gcs(
            image,
            bucket_name,
            image_path
        )
        
        return {
            "status": "success",
            "image_url": image_url,
            "prompt": request.prompt
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating image: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
