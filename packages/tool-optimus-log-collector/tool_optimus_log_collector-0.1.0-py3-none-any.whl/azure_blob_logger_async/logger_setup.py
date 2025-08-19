# logger_setup.py
import logging
import asyncio
from azure.identity.aio import ManagedIdentityCredential
from azure_blob_logger_async.async_blob_log_handler import AsyncAzureBlobLogHandler, log_worker

log_queue = asyncio.Queue()
logger = logging.getLogger("AzureBlobLogger")
logger.setLevel(logging.INFO)

# Reusable function
async def start_blob_logger(
    client_id: str,
    blob_account_url: str,
    blob_container_name: str,
    log_level=logging.INFO
):
    try:
        credential = ManagedIdentityCredential(client_id=client_id)
        handler = AsyncAzureBlobLogHandler(blob_account_url, blob_container_name, log_queue, credential)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        logger.setLevel(log_level)
        logger.addHandler(handler)

        # Start worker
        asyncio.create_task(log_worker(log_queue, blob_account_url, blob_container_name, credential))
        print("[AzureBlobLogger] Logger initialized and worker started.")
    except Exception as e:
        print(f"[AzureBlobLogger] Logger setup failed: {e}")
