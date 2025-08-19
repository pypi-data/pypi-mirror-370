from rara_meta_extractor.tools.meta_formatter import Title
from typing import List

import pytest
import os

TEST_SKIP_TITLES = [
    ("Andromeda", 0),
    ("...And Then There Were None", 3),
    ("+ Teised", 2),
    ("Ja nii edasi...", 0),
    ("Miks me elame?", 0),
    ("A Fun Story", 2),
    ("The Great Escape", 4),
    ("... The People", 8)
]

def test_skip_calculation():
    for test_title in TEST_SKIP_TITLES:
        title, expected_skip = test_title
        true_skip = Title.find_skip(title)
        assert expected_skip == true_skip
