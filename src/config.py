import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Securely get API key and model name
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest") # Default model

# Model Configurations
POSE_MODEL = "yolov8n-pose.pt"
TRACKING_MODEL = "facebook/detr-resnet-50"

# Configuration for Ray (for parallel processing)
RAY_CONFIG = {
    "num_cpus": os.cpu_count(),
    "num_gpus": 0,
    "ignore_reinit_error": True,
}

# Dask Configuration
DASK_N_WORKERS = 4
DASK_THREADS_PER_WORKER = 2
