import time

from elasticsearch import helpers
from loguru import logger


def bulk_index(es, batch: list):
    logger.info("Trying to index batch to ElasticSearch...")
    start = time.time()
    helpers.bulk(es, batch)
    end = time.time()
    logger.debug("Time taken to index: {}".format(end - start))
    logger.success("Batch successfully indexed to ElasticSearch")
