from rara_meta_extractor.tools.utils import load_txt, load_json
from rara_meta_extractor.constants.schemas import TEXT_CLASSIFIER_SCHEMA
from rara_meta_extractor.constants.data_classes import (
    TextBlock, AuthorField, TextPartLabel, TEXT_BLOCKS, META_YEAR_FIELDS
)
import importlib.resources
import os
import logging


LOGGER = logging.getLogger("rara-meta-extractor")

METADATA_TEXT_BLOCKS = [TextBlock.METADATA, TextBlock.TITLE_PAGE]

# File paths
AUTHOR_FIELDS_FILE_PATH =  importlib.resources.files("rara_meta_extractor.data.fields") / "kata_author_fields.txt"
META_FIELDS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.fields") / "kata_meta_fields.txt"

META_EXTRACTOR_INSTRUCTIONS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.instructions") / "meta_extractor_instructions.txt"
TEXT_CLASSIFIER_INSTRUCTIONS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.instructions") / "text_classifier_instructions.txt"

META_SCHEMA_PATH = importlib.resources.files("rara_meta_extractor.data.schemas") / "meta_schema.json"

AUTHOR_ROLES_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.field_translations") / "author_roles.json"

EPUB_AUTHOR_ROLES_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.field_translations") / "relator_to_est.json"
EPUB_META_KEYS_FILE_PATH = importlib.resources.files("rara_meta_extractor.data.fields") / "epub_meta_keys.txt"

AUTHOR_ROLES_DICT = load_json(AUTHOR_ROLES_FILE_PATH)

EPUB_AUTHOR_ROLES_DICT = load_json(EPUB_AUTHOR_ROLES_FILE_PATH)

AUTHOR_FIELDS = load_txt(AUTHOR_FIELDS_FILE_PATH, to_list=True)
META_FIELDS = load_txt(META_FIELDS_FILE_PATH, to_list=True)

EPUB_META_KEYS = load_txt(EPUB_META_KEYS_FILE_PATH, to_list=True)


LLAMA_META_EXTRACTOR_INSTRUCTIONS = load_txt(META_EXTRACTOR_INSTRUCTIONS_FILE_PATH)
LLAMA_TEXT_CLASSIFIER_INSTRUCTIONS = load_txt(TEXT_CLASSIFIER_INSTRUCTIONS_FILE_PATH)

META_SCHEMA = load_json(META_SCHEMA_PATH)


LLAMA_TEXT_CLASSIFIER_URL = "http://dev-elastic1.texta.ee:8080"
LLAMA_META_EXTRACTOR_URL = "http://localhost:8080" #"http://dev-elastic1.texta.ee:8080" #

FIELDS = META_FIELDS + AUTHOR_FIELDS


DEFAULT_INSTRUCTIONS = "This is a conversation between User and Llama - a metadata extrator with skills of professional cataloguer. Please extract the following fields: {0}"

KATA_INSTRUCTIONS = (
    f"This is a conversation between User and Llama - a metadata extrator with skills of professional cataloguer. " +
    f"Your only assignment is to extract relevant metadata and OUTPUT IT AS JSON DICT. " +
    f"THIS IS VERY IMPORTANT! Output it as JSON DICT or DIE. Fields you are trying to extract are the following: {FIELDS}\n"
)

META_EXTRACTOR_CONFIG = {
    "llama_host_url": LLAMA_META_EXTRACTOR_URL,
    "instructions": KATA_INSTRUCTIONS,
    "fields": [],
    "json_schema": {},
    "temperature": 0.1,
    "n_predict": 500
}

TEXT_CLASSIFIER_CONFIG = {
    "llama_host_url": LLAMA_TEXT_CLASSIFIER_URL,
    "instructions": LLAMA_TEXT_CLASSIFIER_INSTRUCTIONS,
    "fields": TEXT_CLASSIFIER_SCHEMA,
    "json_schema": {},
    "temperature": 0.0,
    "n_predict": 500
}

# For filtering false-positive authors extracted from EPUBs.
# Dont' allow names that contain
# more words than EPUB_AUTHOR_MAX_N_WORDS or
# more characters  than EPUB_AUTHOR_MAX_LENGTH
EPUB_AUTHOR_MAX_N_WORDS = 7
EPUB_AUTHOR_MAX_LENGTH = 50


# For filtering chapter names - the assumption is that
# if some required ratio (TABLE_OF_CONTENTS_MIN_UPPERCASE_RATIO)
# of chapters only contains uppercase characters and the average length
# of those chapter names is at least TABLE_OF_CONTENTS_MIN_UPPERCASE_AVG_LENGTH
# (to exclude names in only roman numerals etc), then chapter names in other casings
# are false positives
TABLE_OF_CONTENTS_MIN_UPPERCASE_RATIO = 0.3
TABLE_OF_CONTENTS_MIN_UPPERCASE_AVG_LENGTH = 10
