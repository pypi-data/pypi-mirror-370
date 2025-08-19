from pathlib import Path
import json


def read_dict_file(path_to_file: Path) -> dict:
    with open(path_to_file, encoding='UTF-8') as _fh:
        return json.load(_fh)

def pjson(content: dict) -> str:
    """Pretty JSON, to make it easy to read data."""
    return json.dumps(content, indent=4)