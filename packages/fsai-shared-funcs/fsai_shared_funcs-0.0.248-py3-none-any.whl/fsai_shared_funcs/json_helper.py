import json
from contextlib import contextmanager

import jsonlines
from beartype import beartype


@contextmanager
@beartype
def get_json_contents(file_path: str, iterable: bool = True):
    # If the output file path is a jsonl file
    if file_path.endswith(".jsonl"):
        reader_total = open(file_path).read().count("\n")
        with jsonlines.open(file_path) as reader:
            yield reader_total, reader
        reader.close()

    # If the output file path is a json file
    if file_path.endswith(".json"):
        # Open the file
        with open(file_path) as f:
            try:
                reader = json.load(f)
            except json.JSONDecodeError as e:
                # logger.warning(e)

                if iterable == True:
                    reader = []
                else:
                    reader = {}

        # Close the file
        f.close()

        reader_total = len(reader)

        if iterable == True:
            yield reader_total, iter(reader)
        else:
            yield reader_total, reader
