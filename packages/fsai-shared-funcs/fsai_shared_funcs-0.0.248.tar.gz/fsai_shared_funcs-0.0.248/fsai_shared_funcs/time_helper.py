from datetime import datetime
from random import randint
from time import sleep

from beartype import beartype
from beartype.typing import Callable, Union
from google.protobuf.timestamp_pb2 import Timestamp


def get_datetime_from_pb_ts(timestamp):
    return datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)


@beartype
def get_pb_ts_from_datetime(python_timestamp: datetime) -> Timestamp:
    t = python_timestamp.timestamp()
    return Timestamp(seconds=int(t), nanos=int(t % 1 * 1e9))


@beartype
def random_sleep(
    min_sleep_seconds: int,
    max_sleep_seconds: int,
    pre_callback: Union[Callable, None] = None,
) -> None:
    random_sleep_seconds = randint(min_sleep_seconds, max_sleep_seconds)
    if pre_callback != None:
        pre_callback(random_sleep_seconds)
    sleep(randint(min_sleep_seconds, max_sleep_seconds))
