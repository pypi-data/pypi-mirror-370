import enum
import ntpath
import os
from pathlib import Path

import boto3
from beartype import beartype
from beartype.typing import Union
from loguru import logger
from smart_open import open


# Enum for size units
class SIZE_UNIT(enum.Enum):
    BYTES = 1
    KB = 2
    MB = 3
    GB = 4


@beartype
def get_directory_name(file_path: str) -> str:
    return os.path.dirname(file_path)


@beartype
def convert_unit(
    size_in_bytes: Union[float, int], unit: SIZE_UNIT
) -> Union[float, int]:
    """Convert the size from bytes to other units like KB, MB or GB"""
    if unit == SIZE_UNIT.KB:
        return size_in_bytes / 1024
    elif unit == SIZE_UNIT.MB:
        return size_in_bytes / (1024 * 1024)
    elif unit == SIZE_UNIT.GB:
        return size_in_bytes / (1024 * 1024 * 1024)
    else:
        return size_in_bytes


@beartype
def delete_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except Exception as e:
        logger.debug(e)


@beartype
def file_exists(file_path: str) -> bool:
    if os.path.exists(file_path):
        return True

    return False


@beartype
def get_file_name_from_path(file_path: str) -> str:
    head, tail = ntpath.split(file_path)
    return tail or ntpath.basename(head)


@beartype
def combine_path_and_filename(file_path: str, file_name: str):
    return os.path.join(
        file_path,
        file_name.lstrip(
            os.path.sep
        ),  # remove leading forward slash which causes join to think path is relative
    )


@beartype
def remove_file_extention(file_path: str):
    path = Path(file_path).with_suffix("")
    return str(path)


@beartype
def create_directory(file_path: str):
    try:
        os.makedirs(file_path, exist_ok=True)
    except:  # noqa: E722
        pass


@beartype
def get_file_size(file_path: str, unit: SIZE_UNIT):
    file_size_b = os.stat(file_path).st_size
    file_size_in_units = convert_unit(file_size_b, unit)
    return file_size_in_units


@beartype
def touch_file(file_path: str, mode=0o777, _create_directory=True):
    # Create the directory path
    if _create_directory is True:
        dir_name = get_directory_name(file_path)

        create_directory(dir_name)

    try:
        path = Path(file_path)
        path.touch(mode=mode, exist_ok=True)
    except Exception as e:
        logger.debug(e)


class GvoFileManager:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
        self.profiles = {}

    def add_s3_profile(self, profile_name, bucket_name, aws_session=None):
        self.profiles[profile_name] = {
            "type": "s3",
            "bucket_name": bucket_name,
            "session": aws_session or boto3.Session(),
        }

    def add_local_profile(self, profile_name, base_path):
        self.profiles[profile_name] = {
            "type": "local",
            "base_path": base_path,
        }

    def read_file(self, profile_name, object_name):
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ValueError(f"Profile {profile_name} not found")

        if profile["type"] == "s3":
            bucket_name = profile["bucket_name"]
            session = profile["session"]
            s3_client = session.client("s3")

            try:
                # Try reading from S3
                obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
                iterator = obj["Body"].iter_chunks(chunk_size=self.chunk_size)
                logger.debug("File read from S3")
                return iterator
            except Exception as e:
                raise FileNotFoundError(f"Could not read from S3: {e}")

        elif profile["type"] == "local":
            base_path = profile["base_path"]
            local_path = os.path.join(base_path, object_name)

            if os.path.exists(local_path):
                logger.debug("File read from local")

                def local_file_iterator(path, chunk_size):
                    with open(path, "rb") as f:
                        while True:
                            chunk = f.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk

                return local_file_iterator(local_path, self.chunk_size)
            else:
                raise FileNotFoundError(f"File not found on local disk: {local_path}")

    def delete_file(self, profile_name, object_name) -> bool:
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ValueError(f"Profile {profile_name} not found")

        if profile["type"] == "s3":
            bucket_name = profile["bucket_name"]
            session = profile["session"]
            s3_client = session.client("s3")

            try:
                # Attempt to delete the object from S3
                s3_client.delete_object(Bucket=bucket_name, Key=object_name)
                logger.debug(
                    f"File {object_name} successfully deleted from S3 bucket {bucket_name}"
                )
                return True
            except s3_client.exceptions.NoSuchKey:
                # Raise specific exception if file doesn't exist in S3
                raise FileNotFoundError(
                    f"File {object_name} not found in S3 bucket {bucket_name}"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to delete {object_name} from S3: {e}")

        elif profile["type"] == "local":
            base_path = profile["base_path"]
            local_path = os.path.join(base_path, object_name)

            if os.path.exists(local_path):
                os.remove(local_path)
                logger.debug(f"File {local_path} successfully deleted from local disk")
                return True
            else:
                # Raise FileNotFoundError if local file does not exist
                raise FileNotFoundError(f"File {local_path} not found on local disk")
        else:
            # Raise an error if profile type is not supported
            raise ValueError(f"Unsupported profile type: {profile['type']}")

    def upload_file(
        self, profile_name, local_path, object_name, storage_class="GLACIER_IR"
    ):
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ValueError(f"Profile {profile_name} not found")

        if profile["type"] == "s3":
            bucket_name = profile["bucket_name"]
            # session = profile["session"]
            s3_uri = f"s3://{bucket_name}/{object_name}"

            kwargs = {
                "StorageClass": storage_class,
            }

            with open(
                s3_uri,
                "wb",
                transport_params={
                    "client_kwargs": {"S3.Client.create_multipart_upload": kwargs}
                },
            ) as fout:
                with open(local_path, "rb") as fin:
                    fout.write(fin.read())

            logger.debug(
                f"File {local_path} uploaded to bucket {bucket_name} as {object_name} with {storage_class} storage class."
            )
        else:
            raise ValueError("Upload only supported for S3 profiles")

    def file_exists(self, profile_name, object_name):
        profile = self.profiles.get(profile_name)
        if not profile:
            raise ValueError(f"Profile {profile_name} not found")

        if profile["type"] == "s3":
            bucket_name = profile["bucket_name"]
            session = profile["session"]
            s3_client = session.client("s3")

            try:
                # Check if the object exists in S3
                s3_client.head_object(Bucket=bucket_name, Key=object_name)
                return True
            except s3_client.exceptions.NoSuchKey:
                return False
            except s3_client.exceptions.ClientError as e:
                # if e.response["Error"]["Code"] == "404":
                #     logger.debug(
                #         f"File {object_name} not found in S3 bucket {bucket_name}"
                #     )

                # elif e.response["Error"]["Code"] == "403":
                #     logger.debug(
                #         f"Access denied to file {object_name} in S3 bucket {bucket_name}"
                #     )

                return False
            except Exception as e:
                raise RuntimeError(
                    f"Failed to check if {object_name} exists in S3: {e}"
                )

        elif profile["type"] == "local":
            base_path = profile["base_path"]
            local_path = os.path.join(base_path, object_name)

            return os.path.exists(local_path)
        else:
            raise ValueError(f"Unsupported profile type: {profile['type']}")
