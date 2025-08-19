from rara_meta_extractor.epub_meta_extractor import EPUBMetaExtractor
from rara_meta_extractor.tools.utils import jl_generator
from typing import List

import pytest
import os


def load_testset(file_path: str) -> List[dict]:
    testset = []
    for doc in jl_generator(file_path):
        doc_id = doc.get("ester_id")
        data = doc.get("digi_output")
        epub_meta = data.get("doc_meta").get("epub_metadata")
        testset.append(
            {
                "epub_metadata": epub_meta
            }
        )
    return testset

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(ROOT_DIR, "tests", "test_data", "epub_meta", "digitized_epubs.jl")
TESTSET = load_testset(TEST_FILE)

EPUB_EXTRACTOR = EPUBMetaExtractor()

def test_epub_extractor():
    for doc_batch in TESTSET:
        meta = EPUB_EXTRACTOR.extract_meta(**doc_batch)
        assert meta
