from rara_meta_extractor.mets_alto_meta_extractor import MetsAltoMetaExtractor
from rara_meta_extractor.tools.utils import jl_generator
from typing import List
from pprint import pprint

import pytest
import os


def load_testset(file_path: str) -> List[dict]:
    testset = []
    for doc in jl_generator(file_path):
        doc_id = doc.get("dir_name")
        data = doc.get("digitized_data")
        mets_alto_meta = data.get("doc_meta").get("mets_alto_metadata")
        digitized_texts = data.get("texts")
        testset.append(
            {
                "mets_alto_metadata": mets_alto_meta,
                "digitized_texts": digitized_texts
            }
        )
    return testset

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(ROOT_DIR, "tests", "test_data", "mets_alto_meta", "digitized_mets_alto.jl")
TESTSET = load_testset(TEST_FILE)

METS_ALTO_EXTRACTOR = MetsAltoMetaExtractor()

def test_mets_alto_extractor():
    for doc_batch in TESTSET:
        meta = METS_ALTO_EXTRACTOR.extract_meta(**doc_batch)
        assert meta

test_mets_alto_extractor()
