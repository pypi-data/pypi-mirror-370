from dotenv import load_dotenv

from aipmodel.model_registry import MLOpsManager

load_dotenv()

# STEP 1: Initialize with your ClearML credentials | if you are not in Cluster, fill out variables
manager = MLOpsManager(
    # clearml_api_server_url="your-endpoint_url",
    # clearml_username="your-clearml_username",
    # clearml_access_key="your-clearml-access-key",
    # clearml_secret_key="your-clearml-secret-key"
)

# STEP 2: Upload local model
local_model_id = manager.add_model(
    source_type="local",
    model_name="your_local_model",
    source_path="path/to/your/local/model/folder",
    code_path="path/to/your/local/model/model.py",  # Optional
)

# STEP 3: Upload HuggingFace model
hf_model_id = manager.add_model(
    source_type="hf",
    model_name="your_hf_model",
    hf_source="facebook/wav2vec2-base-960h"
)

# STEP 4: Upload model from your own S3 (e.g., AWS S3, MinIO, or Ceph)
s3_model_id = manager.add_model(
    source_type="s3",
    model_name="your_s3_model",
    endpoint_url="http://your-s3-endpoint.com",
    bucket_name="your-s3-bucket",
    access_key="your-s3-access-key",
    secret_key="your-s3-secret-key",
    source_path="path/in/your/bucket/",
    code_path="path/to/your/local/model/model.py",  # Optional
)

# STEP 5: Download a model locally
manager.get_model(
    model_name="your_hf_model",  # or any valid model name
    local_dest="./downloaded_model/",
)

# STEP 6: List all models in your AIP project
manager.list_models()

# STEP 7: Get model information
manager.get_model_info("your_hf_model")

# STEP 8: Delete a model
manager.delete_model(model_id=local_model_id)