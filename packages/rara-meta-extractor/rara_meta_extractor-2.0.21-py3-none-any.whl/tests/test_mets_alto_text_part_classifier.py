from rara_meta_extractor.mets_alto_meta_extractor import MetsAltoMetaExtractor
from rara_meta_extractor.text_part_classifiers.mets_alto_text_part_classifier import MetsAltoTextPartClassifier
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


def get_classifier_input(file_path: str) -> List[dict]:
    testset = load_testset(file_path)
    extractor = MetsAltoMetaExtractor()

    classifier_input = []
    for doc_batch in testset:
        meta = extractor.extract_meta(**doc_batch)
        digitized_texts = doc_batch.get("digitized_texts")
        classifier_input.append(
            {
                "digitized_texts": digitized_texts,
                "mets_alto_meta": meta
            }
        )
    return classifier_input

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_FILE = os.path.join(ROOT_DIR, "tests", "test_data", "mets_alto_meta", "digitized_mets_alto.jl")

CLASSIFIER_TESTSET = get_classifier_input(TEST_FILE)
METS_ALTO_CLASSIFIER = MetsAltoTextPartClassifier()

#@pytest.mark.skip(reason="Mets/Alto text part classifier currently broken due do changes in Mets/Alto extractor output.")
def test_mets_alto_text_part_classifier():
    for doc_batch in CLASSIFIER_TESTSET:
        mets_alto_text_parts = METS_ALTO_CLASSIFIER.get_parts_of_text(**doc_batch)
        assert mets_alto_text_parts
