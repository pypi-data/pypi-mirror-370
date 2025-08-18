import os
import logging
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime
import boto3
from ..storage_handler import DatasetStorageHandler
from ..models.metadata import DatasetMetadata
from ..handlers.utils import summarize_dataset
from ..handlers.conditions import DatasetConditionChecker

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self, *, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        logger.info(f"S3Handler initialized for endpoint '{endpoint_url}' and bucket '{bucket_name}'.")

    def download_file(self, remote_path: str, local_path: Path, s3_client) -> None:
        if not s3_client:
            raise HTTPException(status_code=503, detail="S3 service is not available.")
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                s3_client.head_object(Bucket=self.bucket_name, Key=remote_path)  
            except s3_client.exceptions.NoSuchKey:
                raise ValueError(f"The file or folder '{remote_path}' does not exist in the S3 bucket '{self.bucket_name}'.")
            
            s3_client.download_file(self.bucket_name, remote_path, str(local_path))
            logger.info(f"S3 Download: '{remote_path}' -> '{local_path}' (bucket='{self.bucket_name}')")
        except Exception as e:
            logger.error(f"S3 download failed for '{remote_path}' in bucket '{self.bucket_name}': {e}")
            raise HTTPException(status_code=500, detail=f"S3 download error: {e}")

    def process_s3_dataset(self, s3_file_path: str, dataset_name: str, user_name: str, private: bool, dataset_tag: str) -> dict:
        """
        Download an S3 dataset, persist it to S3-mounted temp directory, and return metadata.
        """
        try:
            mount_dataset_name = dataset_name or Path(s3_file_path).stem
            storage_handler = DatasetStorageHandler(mount_dataset_name)

            DatasetConditionChecker().check_s3_size(
                access_key=self.access_key,
                secret_key=self.secret_key,
                endpoint_url=self.endpoint_url,
                bucket_name=self.bucket_name,
                s3_path=s3_file_path
            )
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                endpoint_url=self.endpoint_url
            )

            temp_dir = storage_handler.temp_dir
            logger.info(f"Using S3-mounted temp directory: {temp_dir}")

            local_file = temp_dir / Path(s3_file_path).name
            self.download_file(s3_file_path, local_file, s3_client)

            dataset_id = storage_handler.generate_dataset_id()
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                dataset_name=dataset_name or local_file.stem,
                dataset_config=None,
                last_commit=None,
                last_modified=None,
                user_name=user_name,
                private=private,
                source="s3",
                created_at=datetime.now().isoformat(),
                file_path="",
                summary=summarize_dataset(local_file),
                dataset_tag=dataset_tag
            )

            stored_path = storage_handler.store_dataset(local_file, metadata)

            return {
                "status": "success",
                "message": "Dataset from S3 stored successfully.",
                "dataset_id": dataset_id,
                "stored_path": stored_path
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing S3 dataset: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal error processing S3 dataset: {e}")
        finally:
            storage_handler.unmount()