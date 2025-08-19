import json
from contextlib import asynccontextmanager

import asyncpg
from loguru import logger


@asynccontextmanager
async def DatabaseAsyncContextManager(db_pool: asyncpg.pool.Pool) -> asyncpg.Connection:
    # Perform setup that would go in __aenter__

    logger.debug("Acquiring a connection from the db_pool")
    async with db_pool.acquire() as connection:
        async with connection.transaction():
            logger.debug("Acquired a connection from the db_pool")
            # Set the type codec to use float instead of Decimal for numeric types
            await connection.set_type_codec(
                "numeric",
                encoder=str,
                decoder=float,
                schema="pg_catalog",
                format="text",
            )
            # Set the type codes to use instead of string for json types
            await connection.set_type_codec(
                "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
            )

            yield connection  # obj should be the object that will be bound in the as clause

    # Perform teardown that would go in __aexit__
