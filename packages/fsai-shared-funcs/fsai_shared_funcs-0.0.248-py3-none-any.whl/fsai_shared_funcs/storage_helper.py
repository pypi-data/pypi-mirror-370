from typing import Generator

from beartype import beartype
from loguru import logger


class DiskStorageAdapter:
    def __init__(self, base_path="/mnt/data/", chunk_size=1024):
        self.base_path = base_path
        self.chunk_size = chunk_size

    @beartype
    def get_bytes(self, file_key: str) -> bytes:
        # Get the bytes generator
        bytes_generator = self.get_bytes_generator(file_key)

        # Join the bytes
        bytes = b"".join(bytes_generator)

        # Return the bytes
        return bytes

    def get_bytes_generator(self, file_key: str) -> Generator[bytes, None, None]:
        full_key = "{}{}".format(self.base_path, file_key)

        logger.debug("Opening File: {}".format(full_key))

        try:
            with open(full_key, "rb") as f:
                while True:
                    bytes = f.read(self.chunk_size)

                    if not bytes:
                        break

                    yield bytes
        except Exception as e:
            logger.error("Error opening the file: {}".format(full_key))
            logger.error(e)
            raise e


# import os
# from beartype import beartype

# class S3StorageAdapter:
#     def __init__(self, s3_client, s3_bucket_name, chunk_size=1024):
#         self.s3_client = s3_client
#         self.s3_bucket_name = s3_bucket_name
#         self.chunk_size = chunk_size

#     def get_image_bytes(self, image_key):
#         # Access the image from storage via image key
#         obj = self.s3_client.get_object(
#             Bucket=self.s3_bucket_name,
#             Key=image_key,
#         )

#         # Access the file via chunked iterator
#         iterator = obj["Body"].iter_chunks(chunk_size=self.chunk_size)

#         while True:
#             try:
#                 bytes = next(iterator)

#                 if not bytes:
#                     break

#                 yield bytes

#             except Exception as e:
#                 break


# @beartype
# def get_storage_configuration() -> dict:
#     config_mapping = {
#         "S3_ACCESS_KEY": "",
#         "S3_SECRET_KEY": "",
#         "S3_BUCKET_NAME": "",
#     }

#     config = {}

#     for key, default in config_mapping.items():
#         config[key] = os.getenv(key, default)

#         if len(str(config[key])) == 0:
#             raise Exception("The environment variable {} is empty.".format(key))

#     return config
