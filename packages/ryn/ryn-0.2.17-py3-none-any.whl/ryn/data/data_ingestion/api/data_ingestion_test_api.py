import asyncio
from fastapi import FastAPI, HTTPException
from ..models.requests import (
    HuggingFaceDownloadRequest,
    KaggleDownloadRequest,
    OpenMLDownloadRequest,
    S3DownloadRequest,
    ListDatasetsRequest,
    DownloadDatasetRequest,
)
from ..storage_handler import DatasetStorageHandler
from ..handlers.huggingface_handler import process_huggingface_dataset
from ..handlers.kaggle_handler import process_kaggle_dataset
from ..handlers.openml_handler import process_openml_dataset
from ..handlers.s3_handler import S3Handler
from fastapi import Request  # This might be missing or incorrectly written as 'from Request'
from concurrent.futures import ProcessPoolExecutor

app = FastAPI(
    title="Dataset Ingestion API",
    description="API to download datasets from various sources like HuggingFace, Kaggle, S3, and OpenML.",
    version="1.0.0",
)


# Create a queue to handle the requests
request_queue = asyncio.Queue()

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_queue():
    while True:
        request, handler = await request_queue.get()
        try:
            if request is not None:
                if asyncio.iscoroutinefunction(handler):
                    await handler(request)
                else:
                    handler(request)
            else:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
        except Exception as e:
            logger.error(f"Error processing request: {e}")
        finally:
            request_queue.task_done()

# Start the queue worker in the background
@app.on_event("startup")
async def startup():
    num_workers = 5
    for _ in range(num_workers):
        asyncio.create_task(process_queue())
        
@app.get("/health")
def health_check():
    return {"status": "ok"}

executor = ProcessPoolExecutor(max_workers=4)

@app.post("/huggingface")
async def ingest_huggingface(request: Request, huggingface_request: HuggingFaceDownloadRequest):
    async def handle_huggingface_request():
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            process_huggingface_dataset,
            huggingface_request.dataset_name,
            huggingface_request.dataset_config,
            huggingface_request.user_name,
            huggingface_request.private,
            huggingface_request.dataset_tag,
            
        )
        logger.info(f"Result from process_huggingface_dataset: {result}")
    await request_queue.put((None, handle_huggingface_request))
    return {"message": "Request added to queue"}

@app.on_event("shutdown")
async def shutdown():
    executor.shutdown()

@app.post("/kaggle")
async def ingest_kaggle(request: KaggleDownloadRequest):
    async def handle_kaggle_request():
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            process_kaggle_dataset,
            request.dataset_id,
            request.user_name,
            request.kaggle_username,
            request.kaggle_key,
            request.private
        )
        logger.info(f"Result from process_kaggle_dataset: {result}")
    await request_queue.put((None, handle_kaggle_request))
    return {"message": "Request added to queue"}

@app.post("/openml")
async def ingest_openml(request: OpenMLDownloadRequest):
    async def handle_openml_request():
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            process_openml_dataset,
            request.dataset_id,
            request.dataset_name,
            request.user_name,
            request.private
        )
        logger.info(f"Result from process_openml_dataset: {result}")
    await request_queue.put((None, handle_openml_request))
    return {"message": "Request added to queue"}

@app.post("/s3")
async def ingest_s3(request: Request, s3_request: S3DownloadRequest):
    raw_body = await request.body()
    logger.info(f"Raw request body: {raw_body}")
    s3_handler = S3Handler(
        access_key=s3_request.access_key,
        secret_key=s3_request.secret_key,
        endpoint_url=s3_request.endpoint_url,
        bucket_name=s3_request.bucket_name,
    )
    async def handle_s3_request():
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor,
            s3_handler.process_s3_dataset,
            s3_request.s3_file_path,
            s3_request.dataset_name,
            s3_request.user_name,
            s3_request.private
        )
        logger.info(f"Result from process_s3_dataset: {result}")
    await request_queue.put((None, handle_s3_request))
    return {"message": "Request added to queue"}



@app.post("/list-datasets")
async def list_datasets(request: ListDatasetsRequest):
    try:
        storage_handler = DatasetStorageHandler("temp_mount")
        datasets = []
        for metadata_file in storage_handler.metadata_dir.glob("*.json"):
            metadata = storage_handler.load_metadata(metadata_file.stem)
            if request.user_name and metadata.user_name != request.user_name:
                continue
            if request.private_only and not metadata.private:
                continue
            datasets.append(metadata)
        return datasets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {e}")
    finally:
        storage_handler.unmount()

@app.post("/download-dataset")
async def download_dataset(request: DownloadDatasetRequest):
    try:
        storage_handler = DatasetStorageHandler("temp_mount")  # Temporary mount for download
        metadata = storage_handler.load_metadata(request.dataset_id)
        if metadata.private and metadata.user_name != request.user_name:
            raise HTTPException(status_code=403, detail="Access denied.")
        return {
            "dataset_id": metadata.dataset_id,
            "dataset_name": metadata.dataset_name,
            "file_path": metadata.file_path,
            "summary": metadata.summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")
    finally:
        storage_handler.unmount()
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7070)