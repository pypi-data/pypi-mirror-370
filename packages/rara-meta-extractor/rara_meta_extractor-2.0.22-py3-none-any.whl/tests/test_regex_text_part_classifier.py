from rara_meta_extractor.text_part_classifiers.regex_text_part_classifier import RegexTextPartClassifier
from rara_meta_extractor.config import TextPartLabel

import pytest
import os

def load_text(file_path: str) -> str:
    with open(file_path, "r") as f:
        text = f.read()
    return text

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(ROOT_DIR, "tests", "test_data", "text_part", "regex")

TEST_TEXTS = {
    TextPartLabel.CONCLUSION: load_text(os.path.join(TEST_DATA_DIR, "conclusion.txt")),
    TextPartLabel.ABSTRACT: load_text(os.path.join(TEST_DATA_DIR, "abstract.txt")),
    TextPartLabel.TABLE_OF_CONTENTS: load_text(os.path.join(TEST_DATA_DIR, "table_of_contents.txt")),
    TextPartLabel.OTHER: load_text(os.path.join(TEST_DATA_DIR, "other.txt"))
}

def test_text_part_classifier():
    tpc = RegexTextPartClassifier()
    for true_label, test_text in TEST_TEXTS.items():
        predicted_label = tpc.get_label(test_text)
        assert true_label == predicted_label
