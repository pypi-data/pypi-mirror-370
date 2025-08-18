import os
import shutil
import openml
from datasets import get_dataset_infos
from fastapi import HTTPException
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class DatasetConditionChecker:
    def has_enough_space(self, size_bytes: int, buffer_ratio: float = 1.2) -> bool:
        """Check if there's enough available disk space with a buffer."""
        total, used, free = shutil.disk_usage("/")
    
        logger.info(f"Available free disk space: {free} bytes")
        return free >= size_bytes * buffer_ratio , free

    def check_huggingface_size(self, dataset_name: str, dataset_config: str = None):
        """Check if there is enough disk space for the Hugging Face dataset."""
        infos = get_dataset_infos(dataset_name)
        for config, info in infos.items():
            if dataset_config is None or config == dataset_config:
                estimated_size = (
                    getattr(info, "size_in_bytes", 0)
                    or getattr(info, "dataset_size", 0)
                    or getattr(info, "download_size", 0)
                )
                if estimated_size > 0:
                    has_space, free_space = self.has_enough_space(estimated_size)
                    if not has_space:
                        required_size = estimated_size * 1.2  # Apply buffer for logging
                        logger.warning(
                            f"Not enough disk space for dataset '{dataset_name}'. "
                            f"Required: {required_size / (1024 ** 2):.3f} MB, Available: {free_space / (1024 ** 2):.3f} MB"
                        )
                        raise HTTPException(
                            status_code=507,
                            detail=(
                                f"Not enough disk space for Hugging Face dataset '{dataset_name}'. "
                                f"Required: {required_size/ (1024 ** 2):.3f} MB, Available: {free_space/ (1024 ** 2):.3f} MB"
                            )
                        )
                else:
                    logger.warning(f"Could not estimate size for dataset '{dataset_name}'")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Unable to estimate size for dataset '{dataset_name}'"
                    )
        
    def check_openml_size(self, dataset_id: int):
        """Check if there is enough disk space for the OpenML dataset."""
        dataset = openml.datasets.get_dataset(dataset_id, download_data=False, download_qualities=True)
        instances = dataset.qualities.get("NumberOfInstances", 0)
        features = dataset.qualities.get("NumberOfFeatures", 0)

        max_bytes_per_value = 100  # Conservative estimate
        estimated_size = instances * features * max_bytes_per_value

        if estimated_size > 0:
            has_space, free_space = self.has_enough_space(estimated_size)
            if not has_space:
                required_size = estimated_size * 1.1  # Apply buffer for logging
                logger.warning(
                    f"Not enough disk space for OpenML dataset ID '{dataset_id}'. "
                    f"Required: {required_size / (1024 ** 2):.3f} MB, Available: {free_space / (1024 ** 2):.3f} MB"
                )
                raise HTTPException(
                    status_code=507,
                    detail=(
                        f"Not enough disk space for OpenML dataset ID '{dataset_id}'. "
                        f"Required: {required_size / (1024 ** 2):.3f} MB, Available: {free_space / (1024 ** 2)} MB"
                    )
                )
        else:
            logger.warning(f"Could not estimate size for OpenML dataset ID '{dataset_id}'")
            raise HTTPException(
                status_code=400,
                detail=f"Unable to estimate size for OpenML dataset ID '{dataset_id}'"
            )
    def check_s3_size(self, *, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str, s3_path: str) -> None:
        """Check if there is enough disk space for the S3 dataset."""
        # Validate inputs
        logger.debug(f"check_s3_size inputs: access_key={access_key}, secret_key=****, endpoint_url={endpoint_url}, "
                     f"bucket_name={bucket_name}, s3_path={s3_path}, types={[type(x).__name__ for x in [access_key, secret_key, endpoint_url, bucket_name, s3_path]]}")
        
        # Validate inputs
        if not all(isinstance(x, str) for x in [access_key, secret_key, endpoint_url, bucket_name, s3_path]):
            raise HTTPException(
                status_code=400,
               
                detail=f"All S3 parameters must be strings. Received types: "
                       f"access_key={type(access_key).__name__}, secret_key={type(secret_key).__name__}, "
                       f"endpoint_url={type(endpoint_url).__name__}, bucket_name={type(bucket_name).__name__}, "
                       f"s3_path={type(s3_path).__name__}"
            )
        if not bucket_name:
            raise HTTPException(status_code=400, detail="S3 bucket name cannot be empty")
  
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                endpoint_url=endpoint_url,
            )
            
            # try:
            #     s3.head_object(Bucket=bucket_name, Key=s3_path)  
            # except s3.exceptions.NoSuchKey:
            #     raise ValueError(f"The file or folder '{s3_path}' does not exist in the S3 bucket '{self.bucket_name}'.")
        

            total_size = 0
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=s3_path)

            for page in pages:
                contents = page.get('Contents', [])
                for obj in contents:
                    total_size += obj['Size']

            if total_size > 0:
                has_space, free_space = self.has_enough_space(total_size)
                logger.info(f"Estimated S3 size for path '{s3_path}' is {total_size / (1024 ** 2):.2f} MB")
                if not has_space:
                    required_size = total_size * 1.1  # Use 1.1 buffer as in your code
                    logger.warning(
                        f"Not enough disk space for S3 dataset at '{bucket_name}/{s3_path}'. "
                        f"Required: {required_size / (1024 ** 2):.2f} MB, Available: {free_space / (1024 ** 2):.2f} MB"
                    )
                    raise HTTPException(
                        status_code=507,
                        detail=(
                            f"Not enough disk space for S3 dataset at '{bucket_name}/{s3_path}'. "
                            f"Required: {required_size / (1024 ** 2):.2f} MB, Available: {free_space / (1024 ** 2):.2f} MB"
                        )
                    )
            else:
                logger.warning(f"Could not estimate size for S3 dataset at '{bucket_name}/{s3_path}'")
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to estimate size for S3 dataset at '{bucket_name}/{s3_path}'"
                )

        except ClientError as e:
            logger.error(f"Error accessing S3 bucket '{bucket_name}/{s3_path}': {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to access S3 bucket '{bucket_name}/{s3_path}': {str(e)}"
            )
