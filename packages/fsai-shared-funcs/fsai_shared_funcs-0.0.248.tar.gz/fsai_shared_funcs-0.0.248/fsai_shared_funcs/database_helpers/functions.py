import os

import asyncpg
from beartype.typing import Any, Dict, List, Tuple, Union
from loguru import logger


# Serial Dictionary.
class Serial(dict):
    def __getitem__(self, key):
        return f"${list(self.keys()).index(key) + 1}"


# Pyformat to psql format.
def pyformat2psql(query: str, args_dict: Dict[str, Any]) -> Tuple[str, List[Any]]:
    # Remove args not present in query.
    args_list = list(args_dict.keys())
    for value in args_list:
        if f"{{{value}}}" not in query:
            args_dict.pop(value, None)
    # Generate query with serial positions.
    args = Serial(args_dict)
    query_formatted = query.format_map(args)
    args_formatted = list(args.values())
    return query_formatted, args_formatted


def get_database_credentials():
    env_var_mapping = {
        "DATABASE_PASSWORD": "password",
        "DATABASE_USERNAME": "username",
        "DATABASE_HOST": "timescaledb.timescaledb.svc.cluster.local",
        "DATABASE_PORT": 5432,
        "DATABASE_NAME": "",
    }

    credentials = {}

    for key, default in env_var_mapping.items():
        credentials[key] = os.getenv(key, default)

        if len(str(credentials[key])) == 0:
            raise Exception("The environment variable {} is empty.".format(key))

    # Build the database url and append
    credentials["DATABASE_URL"] = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        credentials["DATABASE_USERNAME"],
        credentials["DATABASE_PASSWORD"],
        credentials["DATABASE_HOST"],
        credentials["DATABASE_PORT"],
        credentials["DATABASE_NAME"],
    )

    return credentials


async def get_database_pool() -> Union[asyncpg.pool.Pool, None]:
    # Access the database credentials from environment variables
    credentials = get_database_credentials()

    # Print debug information to the console
    logger.debug("Trying to connect to the database...")
    logger.debug("Host: {}".format(credentials["DATABASE_HOST"]))
    logger.debug("Port: {}".format(credentials["DATABASE_PORT"]))
    logger.debug("Database Name: {}".format(credentials["DATABASE_NAME"]))
    logger.debug("Username: {}".format(credentials["DATABASE_USERNAME"]))

    # Setup the database connection pool
    db_pool = await asyncpg.create_pool(
        user=credentials["DATABASE_USERNAME"],
        password=credentials["DATABASE_PASSWORD"],
        host=credentials["DATABASE_HOST"],
        port=credentials["DATABASE_PORT"],
        database=credentials["DATABASE_NAME"],
        statement_cache_size=0,
    )

    logger.debug("Successfully connected to the database.")

    return db_pool
