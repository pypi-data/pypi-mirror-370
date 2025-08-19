from rara_meta_extractor.epub_meta_extractor import EPUBMetaExtractor
from rara_meta_extractor.text_part_classifiers.epub_text_part_classifier import EPUBTextPartClassifier
from rara_meta_extractor.tools.utils import jl_generator
from typing import List
from pprint import pprint
import pytest
import os

def load_testset(file_path: str) -> List[dict]:
    testset = []
    for doc in jl_generator(file_path):
        doc_id = doc.get("ester_id")
        data = doc.get("digi_output")
        epub_meta = data.get("doc_meta").get("epub_metadata")
        digitized_texts = data.get("texts")
        testset.append(
            {
                "epub_metadata": epub_meta,
                "digitized_texts": digitized_texts
            }
        )
    return testset

def get_classifier_input(file_path: str) -> List[dict]:
    testset = load_testset(file_path)
    extractor = EPUBMetaExtractor()

    classifier_input = []
    for doc_batch in testset:
        epub_meta = doc_batch.get("epub_metadata")
        digitized_texts = doc_batch.get("digitized_texts")
        meta = extractor.extract_meta(epub_metadata=epub_meta)
        pprint(meta)

        classifier_input.append(
            {
                "digitized_texts": digitized_texts,
                "epub_meta": meta
            }
        )
    return classifier_input

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(ROOT_DIR, "tests", "test_data", "epub_meta", "digitized_epubs.jl")

CLASSIFIER_TESTSET = get_classifier_input(TEST_FILE)
EPUB_CLASSIFIER = EPUBTextPartClassifier()

#@pytest.mark.skip(reason="EPUB text part classifier currently broken due do changes in EPUB extractor output.")
def test_epub_text_part_classifier():
    # TODO: inspect why @ inices
    no_text_part_indices = {0, 2, 4, 5, 6}
    for i, doc_batch in enumerate(CLASSIFIER_TESTSET):
        epub_text_parts = EPUB_CLASSIFIER.get_parts_of_text(**doc_batch)
        if i not in no_text_part_indices:
            assert epub_text_parts
