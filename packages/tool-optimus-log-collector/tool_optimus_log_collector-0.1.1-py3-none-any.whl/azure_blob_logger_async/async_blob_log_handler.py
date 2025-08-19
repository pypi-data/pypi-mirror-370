import logging
import asyncio
from datetime import datetime
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
import sys

# --- Azure SDK Debug Logging ---
logging.getLogger("azure.storage.blob").setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logging.getLogger("azure.storage.blob").addHandler(handler)
# --------------------------------
MAX_LOG_SIZE = 500 * 1024  # 500 KB

class AsyncAzureBlobLogHandler(logging.Handler):
    def __init__(self, account_url, container_name, queue, credential):
        super().__init__()
        self.account_url = account_url
        self.container_name = container_name
        self.queue = queue
        self.credential = credential

    def emit(self, record):
        log_entry = self.format(record)
        self.queue.put_nowait(log_entry)

async def log_worker(queue, account_url, container_name, credential):
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential,
        logging_enable=True  # Enables HTTP-level debugging
    )
    container_client = blob_service_client.get_container_client(container_name)
    try:
        await container_client.create_container()
        print("Container created or existed.")
    except ResourceExistsError:
        print("Container already exists.")

    while True:
        log_entry = await queue.get()
        print(f"Dequeued log: {log_entry[:100]}...")

        date_folder = datetime.utcnow().strftime('%Y-%m-%d')
        base_blob_name = f"logs/{date_folder}/log.log"
        blob_client = container_client.get_blob_client(base_blob_name)
        print(f"Will write to blob: {base_blob_name}")

        try:
            props = await blob_client.get_blob_properties()
            size = props.size
            print(f"Current blob size (bytes): {size}")
        except ResourceNotFoundError:
            size = 0
            print("Blob does not exist yet; will create new.")

        if size >= MAX_LOG_SIZE:
            timestamp = datetime.utcnow().strftime('%H%M%S')
            rotated_blob_name = f"logs/{date_folder}/log_{timestamp}.log"
            blob_client = container_client.get_blob_client(rotated_blob_name)
            print(f"Rotated to new blob: {rotated_blob_name}")

        # Only create if not exists to avoid overwrite
        try:
            await blob_client.create_append_blob()
            print(f"Append blob created: {blob_client.blob_name}")
        except ResourceExistsError:
            print("Append blob already exists; appending to it.")

        try:
            await blob_client.append_block(log_entry.encode('utf-8'))
            print(f"Appended log to blob: {blob_client.blob_name}")
        except Exception as e:
            print(f"Error appending log: {e}")

        queue.task_done()
