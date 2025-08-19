import os
import json
import jsonlines
import langdetect
from typing import List, Optional

def load_txt(file_path: str, to_list: Optional[bool] = False) -> List[str] | str:
    """ Loads text from a given file_path.

    Parameters
    -----------
    file_path: str
        Path to file containing the text.
    to_list: Optional[bool]
        If enabled, each row is treated as a list element
        and a list of strings is returned.

    Returns
    -----------
    out: List[str] | str

    """
    with open(file_path, "r") as f:
        out = f.read().strip()
        if to_list:
            out = [
                row.strip()
                for row in out.split("\n")
                if row.strip()
            ]
    return out

def load_json(file_path: str) -> list | dict:
    """ Loads a JSON file.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

def dump_json(data, file_path: str):
    """ Dump data into a JSON file.
    """
    with open(file_path, "w") as f:
        json.dump(data, f)

def jl_generator(file_path: str):
    """ Iterates over a JSON-Lines file and
    yields rows.
    """
    with jsonlines.open(file_path, "r") as f:
        for row in f:
            yield row

def write_line(doc: dict, jl_file_path: str):
    """ Appends documents into a JSON-Lines file.
    """
    with jsonlines.open(jl_file_path, "a") as f:
        f.write(doc)

def detect_language(text: str) -> str:
    """ Detects language of the text.
    """
    try:
        lang = langdetect.detect(text)
    except:
        lang = ""
    return lang
