from string import punctuation

# -------------------------------------------- #
# Paterns used by Text Part Classifier
# -------------------------------------------- #

# Table of contents title variants
TABLE_OF_CONTENTS_PATTERNS = [
    r"Sisukord",
    r"Contents",
    r"Table of Contents"
]

# Abstract title variants
ABSTRACT_PATTERNS = [
    r"Abstract",
    r"Annotatsioon"
]
# Conclusion title variants
CONCLUSION_PATTERNS = [
    r"Kokkuvõte(?!:)",
    r"Kokkuvõte ja järeldused",
    r"Kokkuvõte ja soovitused",
    r"Kokkuvõte ja ettepanekud",
    r"Summary",
    r"Summary in Estonian",
    r"Conclusions?",
    r"Lühitutvustus(?!:)",
    r"Lühikokkuvõte(?!:)",
    r"Lühike kokkuvõte(?!:)",
    r"Kokkuvõte auditeerimise tulemustest",
    r"Discussion and conclusions?",
    r"Final Comments and Conclusions?",
    r"Discussion and Conclusion",
    r"The main conclusions of the work are the following",
    r"In Conclusion"
]

ORDINAL_PATTERNS = [
    "first", "second", "third", "fourth", "fifth",
    "esimene", "teine", "kolmas", "neljas", "viies",
    "chapter", "peatükk", "peatüki", "rühmatööst"
]

# -------------------------------------------- #
# SKIP patterns
# -------------------------------------------- #

SKIP_WORDS = ["the", "an", "a", "der", "das"]
SKIP_CHARS = punctuation
