from dataclasses import dataclass

@dataclass(frozen=True)
class TextBlock:
    REGULAR: str = "regular text block"
    METADATA: str = "metadata text block"
    TITLE_PAGE: str = "title page"
    ABSTRACT: str = "abstract text block"
    SUMMARY: str = "summary text block"


@dataclass(frozen=True)
class IssueType:
    NEWSPAPER: str = "Ajaleht"
    JOURNAL: str = "Ajakiri"
    PERIODICAL: str = "Jätkväljaanne"
    BOOK: str = "Raamat"

@dataclass(frozen=True)
class ExtractorType:
    LLAMA: str = "Llama-Extractor"
    EPUB: str = "EPUB-Extractor"
    METS_ALTO: str = "METS/ALTO-Extractor"

@dataclass(frozen=True)
class TextPartLabel:
    TABLE_OF_CONTENTS: str = "Sisukord"
    ABSTRACT: str = "Abstrakt"
    CONCLUSION: str = "Kokkuvõte"
    OTHER: str = "Muu"

@dataclass(frozen=True)
class AuthorField:
    AUTHOR: str = "author"
    UNKNOWN: str = "Teadmata"

@dataclass(frozen=True)
class AuthorType:
    PER: str = "PER"
    ORG: str = "ORG"
    UNK: str = ""


@dataclass(frozen=True)
class TitleType:
    AUTHOR_WITHOUT_TITLE: str = "pealkirjata autor"
    NORMALIZED_TITLE: str = "normitud eelispealkiri"
    TITLE: str = "väljaandes esitatud kujul põhipealkiri"
    PARALLEL_TITLE: str = "rööppealkiri"
    ADDITIONAL_TITLE: str = "alampealkiri"
    METS_TITLE: str = "väljaandes esitatud kujul põhipealkiri"

@dataclass(frozen=True)
class TitleTypeSimple:
    TITLE: str = "main_title"
    ADDITIONAL_TITLE: str = "subtitle"
    METS_TITLE: str = "article_or_chapter_title"
    PARALLEL_TITLE: str = "parallel_title"


@dataclass(frozen=True)
class AuthorNameOrder:
    FIRST_NAME_FIRST: int = 0
    LAST_NAME_FIRST: int = 1
    FAMILY_NAME_FIRST: int = 3

@dataclass(frozen=True)
class DataRestrictions:
    ISBN_MIN_LENGTH: int = 10
    ISBN_MAX_LENGTH: int = 13
    ISSN_LENGTH: int = 8
    YEAR_LENGTH: int = 4

@dataclass(frozen=True)
class MetaYearField:
    DISTRIBUTION_DATE: str = "distribution date"
    PUBLICATION_DATE: str = "publication date"
    MANUFACTURE_DATE: str = "manufacture date"

@dataclass(frozen=True)
class SeriesField:
    ISSN: str = "issn"
    STATEMENT: str = "name"
    VOLUME: str = "volume"

@dataclass(frozen=True)
class MetaField:
    TITLES: str = "titles"
    TITLE: str = "title"
    SUBTITLE: str = "title remainder"
    TITLE_PART_NR: str = "title part nr"
    TITLE_PART_NAME: str = "title part name"
    TITLE_VARFORM: str = "title varform"
    ISBN: str = "isbn"
    ISSN: str = "issn"
    EDITION_INFO: str = "edition info/number"
    DISTRIBUTION_PLACE: str = "distribution_place"
    DISTRIBUTER_NAME: str = "distributer name"
    DISTRIBUTION_DATE: str = "distribution date"
    MANUFACTURE_DATE: str = "manufacture date"
    MANUFACTURER: str = "manufacturer"
    MANUFACTURE_PLACE: str = "manufacture place"
    PUBLICATION_DATE: str = "publication_date"
    PUBLISHER: str = "publisher"
    PUBLICATION_PLACE: str = "publication place"
    #SUMMARY_LANG: str = "summary or abstract language"
    #TOC_LANG: str = "table of contents language"
    #ORIGINAL_LANG: str = "language original"
    COUNTRY_FROM_008: str = "country from 008"
    TEXT_TYPE: str = "text_type"
    AUTHORS: str = "authors"
    TEXT_PARTS: str = "text_parts"
    ISSUE_TYPE: str = "issue_type"
    UDK: str = "udk"
    UDC: str = "udc"
    UNK: str = "unknown"
    INCLUDED_TEXT: str = "description"
    TABLE_OF_CONTENTS: str = "table_of_contents"
    SECTIONS: str = "sections"
    HOST_ENTRY: str = "host_entry"
    SERIES_ISSN: str = "series_issn"
    SERIES_NAME: str = "series_statement"
    SERIES_VOLUME: str = "series_volume"
    SERIES: str = "series"


@dataclass(frozen=True)
class HostEntryField:
    NAME: str = "name"
    PUBLICATION_DATE: str = "publication_date"
    PART_NUMBER: str = "part_number"

TITLE_TYPES_MAP = {
    TitleType.AUTHOR_WITHOUT_TITLE: 130,
    TitleType.NORMALIZED_TITLE: 240,
    TitleType.TITLE: 245,
    TitleType.PARALLEL_TITLE: 246,
    TitleType.ADDITIONAL_TITLE: 245,
    TitleType.METS_TITLE: 245
}


ISSUE_STYLE_MAP = {
    "newspaper": IssueType.NEWSPAPER,
    "ajalehed": IssueType.NEWSPAPER,
    "journal": IssueType.JOURNAL,
    "ajakirjad": IssueType.JOURNAL,
    "periodical": IssueType.PERIODICAL,
    "jätkväljanded": IssueType.PERIODICAL,
    "books": IssueType.BOOK,
    "raamatud": IssueType.BOOK
}
AUTHOR_TYPES_MAP = {"personal": AuthorType.PER}

DEFAULT_ISSUE_TYPE = IssueType.BOOK

TEXT_BLOCKS = [v for v in vars(TextBlock()).values()]
META_YEAR_FIELDS = [v for v in vars(MetaYearField()).values()]

META_FIELDS_WITH_MULTIPLE_VALUES = [MetaField.ISBN, MetaField.ISSN, MetaField.UDK, MetaField.UDC]

TITLE_KEYS = [
    MetaField.TITLE, MetaField.SUBTITLE, MetaField.TITLE_PART_NR,
    MetaField.TITLE_PART_NAME, MetaField.TITLE_VARFORM
]
META_KEYS_TO_IGNORE = TITLE_KEYS


EPUB_FIELDS_TO_PREFER = [MetaField.ISBN, MetaField.PUBLICATION_DATE]
