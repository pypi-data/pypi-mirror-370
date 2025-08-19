import asyncio
from azure_blob_logger_async import logger, start_blob_logger, log_queue


async def main():
    await start_blob_logger(
        client_id="CLIENT_ID",
        blob_account_url="BLOB_STORAGE_ACCOUNT",
        blob_container_name="BLOB_CONTAINER"
    )

    logger.info("This is a test log.")
    logger.error("This is a test error.")

    await log_queue.join()



