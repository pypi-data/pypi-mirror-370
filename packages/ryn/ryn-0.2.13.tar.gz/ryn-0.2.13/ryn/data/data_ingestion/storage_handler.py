import os
import shutil
import uuid
import json
from pathlib import Path
from fastapi import HTTPException
import logging
from .models.metadata import DatasetMetadata
from .lakefs.lakefs_handler import lakefs_handler
import subprocess
from clearml import Dataset as ClearMLDataset

logger = logging.getLogger(__name__)
PVC_BASE_DIR = Path(__file__).resolve().parent.parent / "PV_Datasets"
METADATA_DIR = PVC_BASE_DIR / "metadata"
TEMP_DIR = PVC_BASE_DIR 
ACCESS_KEY = "AKIAJDZZU24FDN57HUAQ"
SECRET_KEY = "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"

class DatasetStorageHandler:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.mount_point = Path(f"/mnt/s3/{dataset_name}")
        self.base_dir = self.mount_point / "main"
        self.metadata_dir = self.base_dir / "metadata"
        self.temp_dir = self.base_dir / "temp"
        lakefs_clt = lakefs_handler(dataset_name, ACCESS_KEY, SECRET_KEY)
        lakefs_clt.mount_repo(str(self.mount_point))
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def unmount(self):
        try:
            subprocess.run(["fusermount", "-u", str(self.mount_point)], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to unmount {self.mount_point}: {e}")
    
    def generate_dataset_id(self) -> str:
        return str(uuid.uuid4())
    
    def store_dataset(self, source_path: Path, metadata: DatasetMetadata) -> str:
        dataset_dir = self.base_dir / metadata.dataset_name
        print(source_path)
        try:
            dataset_dir.mkdir(exist_ok=True)
            if source_path.is_dir():
                stored_path = dataset_dir / "data"
                if stored_path.exists():
                    shutil.rmtree(stored_path)
                shutil.move(str(source_path), str(stored_path))
            elif source_path.is_file():
                stored_path = dataset_dir / source_path.name
                shutil.move(str(source_path), str(stored_path))
            else:
                raise FileNotFoundError(f"Source path {source_path} does not exist or is not a file/directory.")

            metadata.file_path = str(stored_path)
            self.save_metadata(metadata)
            logger.info(f"Dataset {metadata.dataset_id} stored at {stored_path}")
            
            clearml_path = f"s3://{self.dataset_name}/main"
            self.register_with_clearml(metadata, clearml_path)
            return str(stored_path)
        except (IOError, OSError, FileNotFoundError) as e:
            logger.error(f"Failed to store dataset {metadata.dataset_id}: {e}")
            if dataset_dir.exists():
                shutil.rmtree(dataset_dir)
            raise HTTPException(status_code=500, detail=f"Error storing dataset file: {e}")
    
    def save_metadata(self, metadata: DatasetMetadata):
        metadata_file = self.metadata_dir / f"{metadata.dataset_id}.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(metadata.dict(), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save metadata for {metadata.dataset_id}: {e}")
            raise HTTPException(status_code=500, detail="Error saving dataset metadata.")

    def load_metadata(self, dataset_id: str) -> DatasetMetadata:
        metadata_file = self.metadata_dir / f"{dataset_id}.json"
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            return DatasetMetadata(**data)
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Metadata not found for this dataset.")
        except Exception as e:
            logger.error(f"Failed to load metadata for {dataset_id}: {e}")
            raise HTTPException(status_code=500, detail="Error reading dataset metadata.")
        
    def register_with_clearml(self, metadata: DatasetMetadata, stored_path: str):
        try:
            dataset = ClearMLDataset.create(
                dataset_name=metadata.dataset_name,
                dataset_project="importing",
                description=f"Dataset ID: {metadata.dataset_id}\nStored path: {stored_path}"
            )
            dataset.add_external_files(
                source_url=stored_path,
                dataset_path=metadata.dataset_name
            )
            dataset.upload()
            dataset.finalize()
            logger.info(f"Dataset {metadata.dataset_name} registered with ClearML.")
        except Exception as e:
            logger.error(f"Failed to register dataset with ClearML: {e}")