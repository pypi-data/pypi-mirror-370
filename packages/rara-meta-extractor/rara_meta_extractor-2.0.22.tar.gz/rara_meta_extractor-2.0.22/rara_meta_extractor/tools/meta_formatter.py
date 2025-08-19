import regex as re
import statistics
from copy import deepcopy
from typing import List, Dict, NoReturn, Any, Tuple
from collections import defaultdict
from rara_meta_extractor.tools.utils import detect_language
from rara_meta_extractor.config import (
    LOGGER, META_FIELDS, AUTHOR_FIELDS,
    META_YEAR_FIELDS, AUTHOR_ROLES_DICT,
    TABLE_OF_CONTENTS_MIN_UPPERCASE_RATIO,
    TABLE_OF_CONTENTS_MIN_UPPERCASE_AVG_LENGTH
)
from rara_meta_extractor.constants.data_classes import (
    AuthorField, MetaField, TextBlock, DataRestrictions, MetaField, AuthorType,
    AuthorNameOrder, TitleType, TitleTypeSimple, AUTHOR_TYPES_MAP, TITLE_TYPES_MAP,
    META_FIELDS_WITH_MULTIPLE_VALUES, DEFAULT_ISSUE_TYPE, TextPartLabel,
    META_KEYS_TO_IGNORE, TITLE_KEYS
)
from rara_meta_extractor.constants.patterns import SKIP_CHARS, SKIP_WORDS

difference = lambda x, y: set(x) - set(y)

class MetaValidator:
    def __init__(self, meta_fields: List[str] = META_FIELDS,
            author_fields: List[str] = AUTHOR_FIELDS
    ) -> NoReturn:
        self.meta_fields: List[str] = meta_fields
        self.author_fields: List[str] = author_fields

    def _filter_by_length(self,
        key: str, values: List[Any], length: Tuple[int, int], values_to_str: bool = False
    ) -> List[Any]:
        """ Filters out values not complying to length requirements.
        """
        original_values = deepcopy(values)
        filtered_values = []
        min_length, max_length = length
        for value in values:
            if min_length <= len(str(value)) <= max_length:
                if values_to_str:
                    filtered_values.append(str(value))
                else:
                    filtered_values.append(value)
        diff = difference(original_values, filtered_values)
        if diff:
            LOGGER.debug(
                f"Removed the following values for key '{key}' not complying " \
                f" to length requirement ({length} characters): {list(diff)}"
            )
        return filtered_values

    def _remove_empty(self, key: str, values: List[Any]) -> List[Any]:
        """ Remove empty strings and "None"-s.
        """
        original_values = deepcopy(values)
        values = [
            v for v in values
            if str(v).strip() and str(v).strip() != "None"
        ]
        n_removed = len(original_values) - len(values)
        if n_removed > 0:
            LOGGER.debug(f"Removed {n_removed} empty values for key '{key}'.")
        return values

    def _get_validated_values(self, key: str, values: list,
            check_dates: bool = True
    ) -> List[Any]:
        values = self._remove_empty(key, values)

        if key == MetaField.ISBN:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=[DataRestrictions.ISBN_MIN_LENGTH, DataRestrictions.ISBN_MAX_LENGTH],
                values_to_str=True
            )
        elif key == MetaField.ISSN:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=[DataRestrictions.ISSN_LENGTH, DataRestrictions.ISSN_LENGTH],
                values_to_str=True
            )
        elif check_dates and key.strip() in META_YEAR_FIELDS:
            values = self._filter_by_length(
                key=key,
                values=values,
                length=[DataRestrictions.YEAR_LENGTH, DataRestrictions.YEAR_LENGTH],
                values_to_str=False
            )
        return values

    def _is_valid_key(self, key: str) -> bool:
        """ Checks, if the key is a valid key present in either
        META_FIELDS or AUTHOR_FIELDS list.
        """
        split_key = " ".join(key.split("_"))
        if key in META_FIELDS or split_key in META_FIELDS:
            return True
        if key in AUTHOR_FIELDS or split_key in AUTHOR_FIELDS:
            return True
        return False


class MetaFormatter:
    """ Formats meta
    """
    def __init__(self,
        meta_fields: List[str] = META_FIELDS,
        author_fields: List[str] = AUTHOR_FIELDS
    ) -> NoReturn:
        self.meta_validator = MetaValidator(
            meta_fields=META_FIELDS,
            author_fields=AUTHOR_FIELDS
        )

    def _filter_by_ratio(self, values: List[Tuple[Any, int]],
            n_trials: int, min_ratio: float
    ) -> List[Any]:
        """ Keeps only values that have been predicted
        in `min_ratio` trials.
        """
        filtered_values = [
            v[0] for v in values
            if float(v[1]/n_trials) >= min_ratio
        ]
        return filtered_values

    def _merge_meta(self, meta_batches: List[dict], min_ratio: float = 0.5) -> dict:
        """ Merges meta into a single dict.
        """
        LOGGER.debug("Merging and formatting metadata.")

        formatted_meta = [
            self._format_meta(meta_dict)
            for meta_dict in meta_batches
            if meta_dict
        ]
        meta = {}
        frequencies = defaultdict(lambda: defaultdict(int))
        n_trials = len(formatted_meta)

        for meta_dict in formatted_meta:
            for key, values in meta_dict.items():
                if key == MetaField.TITLES:
                    # "titles" list contains only the main title
                    # for the latest model, so merge them into one
                    values = [" ".join(values)]
                for value in values:
                    if not isinstance(value, str):
                        LOGGER.debug(f"Unhashable value: '{value}'. Skipping.")
                        continue
                    frequencies[key][value]+=1

        for key, value_dict in frequencies.items():
            value_list = sorted(
                list(value_dict.items()),
                key=lambda x: x[1],
                reverse=True
            )
            meta[key] = self._filter_by_ratio(
                values=value_list,
                n_trials=n_trials,
                min_ratio=min_ratio
            )
        return meta

    def _parse_authors(self, authors_list: List[str]) -> List[str]:
        """ Parse weirdly extracted authors like:
        "Reelika RätsepMari-Liis TammikElmar Zimmer"
        """
        LOGGER.debug("Parsing authors.")
        new_authors = []
        for author in authors_list:
            parsed = re.split("(?<=[a-züõöäšž])(?=[A-ZÜÕÖÄŠŽ])", author)
            new_authors.extend(parsed)
        return new_authors

    def _parse_dates(self, values: List[str]) -> List[str]:
        parsed = []
        for value in values:
            match = re.search(r"(?<=\D|^)\d{4}(?=\D|$)", value)
            if match:
                parsed.append(match.group())
        return parsed

    def _add_missing_keys(self, meta: dict,
            keys_to_ignore: List[str] = META_KEYS_TO_IGNORE
        ) -> dict:
        """ Adds missing meta keys.
        """
        meta_copy = deepcopy(meta)
        missing_keys = {}
        for key in META_FIELDS:
            if key not in meta and key not in keys_to_ignore:
                missing_keys[key] = []
        meta_copy.update(missing_keys)
        return meta_copy

    def _remove_empty_fields(self, meta: dict) -> dict:
        """ Removes empty fields.
        """
        new_meta = {}
        for key, values in meta.items():
            if values:
                new_meta[key] = values
        return new_meta

    def _format_meta(self, meta: dict, check_dates: bool = False) -> dict:
        """ Format meta.
        """
        formatted_meta = {}
        for key, values in list(meta.items()):
            key = key.strip()
            if not self.meta_validator._is_valid_key(key):
                LOGGER.error(
                    f"Detected an invalid key '{key}'. " \
                    f"This will NOT be added to the output."
                )
                continue
            values = self.meta_validator._get_validated_values(
                key=key, values=values, check_dates=check_dates
            )
            if values:
                if key in AUTHOR_FIELDS:
                    formatted_meta[key] = self._parse_authors(values)
                elif key in META_YEAR_FIELDS:
                    formatted_meta[key] = self._parse_dates(values)
                else:
                    formatted_meta[key] = values
        return formatted_meta


    def _format_authors(self, meta: dict, simple: bool = False) -> dict:
        """ Convert authors from a flat structure into
        a list of dicts.
        """
        LOGGER.debug("Formatting authors.")
        new_meta = {MetaField.AUTHORS: []}#, "main_author": ""}
        for key, values in list(meta.items()):
            if key in AUTHOR_FIELDS:
                for i, value in enumerate(values):
                    if i == 0 and key == AuthorField.AUTHOR:
                        is_primary = True
                    else:
                        is_primary = False
                    new_author = Author(
                        name=value,
                        role=key,
                        is_primary=is_primary
                    ).to_dict(simple=simple)
                    new_meta["authors"].append(new_author)
            else:
                new_meta[key] = values
        return new_meta


class Author:
    def __init__(self, name: str, role: str, is_primary: bool, author_type: str = AuthorType.UNK,
            unknown_role: str = AuthorField.UNKNOWN, map_role: bool = True,
            author_name_order: int = AuthorNameOrder.FIRST_NAME_FIRST
    ):
        self.name: str = name
        self.is_primary: bool = is_primary
        self.en_role: str = role
        self.et_role: str = AUTHOR_ROLES_DICT.get(self.en_role, unknown_role) if map_role else role
        self.author_type: str = AUTHOR_TYPES_MAP.get(author_type, AuthorType.UNK)
        self.author_name_order: int = author_name_order

    @staticmethod
    def is_false_positive(author_name: str, max_n_words: int = 7,
            max_length: int = 50
    ) -> bool:
        """ Author names detected from EPUBs might sometimes
        contain just a long free form text like:
        'E-raamatu teostus Ants Tuur / www.flagella.ee '
        '- Kvaliteetsed eraamatu lahendused.'
        """
        name_tokens = [
            token.strip()
            for token in author_name.split()
            if token.strip()
        ]
        if len(name_tokens) > max_n_words or len(author_name) > max_length:
            return True
        return False


    def to_dict(self, simple: bool = False) -> dict:
        if simple:
            author_dict = {
                "name": self.name,
                "role": self.et_role
            }
        else:
            author_dict = {
                "is_primary": self.is_primary,
                "name": self.name,
                "role": self.et_role,
                "type": self.author_type,
                "name_order": self.author_name_order
            }
        return author_dict

class Title:
    def __init__(self, titles: List[str] | dict, lang: str = "",
        part_number: str = "", title_type: str = ""
    ):
        self.titles: List[str] | dict = titles
        self.lang: str  = lang
        self.title_type: str = title_type
        self.__part_number: str = part_number

    @property
    def part_number(self) -> str:
        if not self.__part_number:
            if isinstance(self.titles, dict):
                part_numbers = self.titles.get(MetaField.TITLE_PART_NR, [])
                self.__part_number = part_numbers[0] if part_numbers else ""
        return self.__part_number

    @staticmethod
    def find_skip(title: str) -> int:
        """ Number of chars that should not be included into search,
        e.g. Articles like 'the', 'an', various punctuation chars etc.
        """
        skip = 0
        skip_pattern = rf"^(([{SKIP_CHARS}]|({'|'.join(SKIP_WORDS)})\s)\s*)+(?=\S)"
        match = re.search(skip_pattern, title, re.IGNORECASE)
        if match:
            skip = len(match.group())
        return skip

    def _get_title_type(self, i: int | None = None, key: str | None = None,
            simple: bool = False, from_list: bool = True
        ) -> str:
        if self.title_type:
            return self.title_type
        if simple:
            title_type_class = TitleTypeSimple
        else:
            title_type_class = TitleType

        if from_list:
            title_type_map = {
                0: title_type_class.TITLE,
                1: title_type_class.ADDITIONAL_TITLE,
                2: title_type_class.PARALLEL_TITLE
            }
            title_type = title_type_map.get(i, "")
        else:
            title_type_map = {
                MetaField.TITLE: title_type_class.TITLE,
                MetaField.SUBTITLE: title_type_class.ADDITIONAL_TITLE,
                MetaField.TITLE_PART_NAME: title_type_class.PARALLEL_TITLE

            }
            title_type = title_type_map.get(key, "")
        return title_type

    def _clean(self, title: str) -> str:
        title = title.strip("/")
        title = title.strip()
        title = title.strip(":")
        title = title.strip()
        return title


    def to_dicts_from_list(self, simple: bool = False) -> List[dict]:
        formatted = []
        for i, title in enumerate(self.titles):
            if i > 2 and not simple:
                break

            title_type = self._get_title_type(i=i, simple=simple, from_list=True)
            title_type_int = TITLE_TYPES_MAP.get(title_type, None)
            skip = Title.find_skip(title)
            title_language = detect_language(title) if not self.lang else self.lang

            if not simple:
                if title_type == TitleType.ADDITIONAL_TITLE:
                    title_dict = formatted.pop()
                    title_dict["part_title"] = title
                else:
                    title_dict = {
                        "title": self._clean(title),
                        "title_language": title_language,
                        "part_number": self.part_number,
                        "part_title": "",
                        "version": "",
                        "author_from_title": "",
                        "skip": skip,
                        "title_type": title_type,
                        "title_type_int": title_type_int
                    }
            else:
                title_dict = {
                    "title": title,
                    "title_type": title_type
                }
            formatted.append(title_dict)
        return formatted

    def to_dicts_from_dict(self, simple: bool = False) -> List[dict]:
        formatted = []
        keys_to_ignore = [MetaField.TITLE_PART_NR, MetaField.SUBTITLE, MetaField.TITLE_VARFORM]

        for key, titles in self.titles.items():
            if key in keys_to_ignore or not titles:
                continue
            title = " ".join(titles)
            title_type = self._get_title_type(key=key, simple=simple, from_list=False)
            title_type_int = TITLE_TYPES_MAP.get(title_type, None)
            skip = Title.find_skip(title)
            title_language = detect_language(title) if not self.lang else self.lang
            subtitles = self.titles.get(MetaField.SUBTITLE, [])
            subtitle = subtitles[0] if subtitles else ""

            if not simple:
                if key == MetaField.TITLE:
                    title_dict = {
                        "title": self._clean(title),
                        "title_language": title_language,
                        "part_number": self.part_number,
                        "part_title": self._clean(subtitle),
                        "version": "",
                        "author_from_title": "",
                        "skip": skip,
                        "title_type": title_type,
                        "title_type_int": title_type_int
                    }
                else:
                    title_dict = {
                        "title": self._clean(title),
                        "title_language": title_language,
                        "part_number": self.part_number,
                        "part_title": "",
                        "version": "",
                        "author_from_title": "",
                        "skip": skip,
                        "title_type": title_type,
                        "title_type_int": title_type_int
                    }
            else:
                title_dict = {
                    "title": title,
                    "title_type": title_type
                }
            formatted.append(title_dict)
        return formatted

    def to_dicts(self, simple: bool = False) -> List[dict]:
        if isinstance(self.titles, dict):
            formatted = self.to_dicts_from_dict(simple)
        else:
            formatted = self.to_dicts_from_list(simple)
        return formatted

class TextPart:
    def __init__(self, text_type: str, text_value: str, language: str = ""):
        self.text_type = text_type
        self.text_value = text_value
        self.language = language if language else detect_language(text_value)

    def to_dict(self) -> dict:
        text_part_dict = {
            "text_type": self.text_type,
            "text_value": self.text_value,
            "language": self.language
        }
        return text_part_dict

class Meta:
    def __init__(self, meta_batches: List[dict], text_parts: List[dict], min_ratio: float = 0.8,
        add_missing_keys: bool = False, simple: bool = False, language: str = ""
    ) -> NoReturn:
        self.meta_batches: List[dict] = meta_batches
        self.text_parts: List[dict] = text_parts
        self.min_ratio: float = min_ratio
        self.add_missing_keys: bool = add_missing_keys
        self.simple: bool = simple
        self.language: str = language

        self.meta_formatter: MetaFormatter = MetaFormatter(
            meta_fields = META_FIELDS,
            author_fields = AUTHOR_FIELDS
        )

        self.__merged_meta: dict = {}
        self.__meta_with_reformatted_authors: dict = {}
        self.__meta_with_all_keys: dict = {}
        self.__meta_without_empty_fields: dict = {}

    @property
    def merged_meta(self) -> dict:
        if not self.__merged_meta:
            self.__merged_meta = self.meta_formatter._merge_meta(
                meta_batches=self.meta_batches,
                min_ratio=self.min_ratio
            )
        return self.__merged_meta

    @property
    def meta_with_reformatted_authors(self):
        if not self.__meta_with_reformatted_authors:
            self.__meta_with_reformatted_authors = self.meta_formatter._format_authors(
                meta=self.merged_meta, simple=self.simple
            )
        return self.__meta_with_reformatted_authors

    @property
    def meta_with_all_keys(self):
        if not self.__meta_with_all_keys:
            self.__meta_with_all_keys = self.meta_formatter._add_missing_keys(
                meta=self.meta_without_empty_fields
            )
        return self.__meta_with_all_keys

    @property
    def meta_without_empty_fields(self):
        if not self.__meta_without_empty_fields:
            self.__meta_without_empty_fields = self.meta_formatter._remove_empty_fields(
                meta=self.meta_with_reformatted_authors
            )
        return self.__meta_without_empty_fields

    def _concat(self, meta: dict) -> dict:
        concatted = {}
        for key, value in meta.items():
           key_tokens = key.split()
           new_key = "_".join(key_tokens)
           concatted[new_key] = value
        return concatted

    @staticmethod
    def update_field_types(meta_dict: dict, empty_value: Any = "",
            custom_keys_to_ignore: List[str] = []
    ) -> dict:
        keys_to_ignore = [MetaField.TITLES, MetaField.AUTHORS, MetaField.TEXT_PARTS]
        keys_to_ignore.extend(META_FIELDS_WITH_MULTIPLE_VALUES)
        keys_to_ignore.extend(custom_keys_to_ignore)
        for key, values in list(meta_dict.items()):
            if key not in keys_to_ignore:
                if not isinstance(values, list):
                    continue
                if values:
                    meta_dict[key] = values[0]
                else:
                    meta_dict[key] = empty_value
        return meta_dict

    def to_dict(self):
        if self.add_missing_keys:
            meta_dict = self._concat(self.meta_with_all_keys)
        else:
            meta_dict = self._concat(self.meta_without_empty_fields)
        if self.text_parts or self.add_missing_keys:
            meta_dict[MetaField.TEXT_PARTS] = self.text_parts
        if MetaField.TITLES in meta_dict:
            titles = meta_dict.pop(MetaField.TITLES)
            formatted_titles = Title(titles=titles, lang=self.language).to_dicts(simple=self.simple)
            meta_dict[MetaField.TITLES] = formatted_titles
        elif MetaField.TITLE in meta_dict:
            titles = {}
            for key in TITLE_KEYS:
                value = meta_dict.pop(key, "")
                if not value:
                    value = meta_dict.pop("_".join(key.split()), "")
                titles[key] = value
            formatted_titles = Title(titles=titles, lang=self.language).to_dicts(simple=self.simple)
            meta_dict[MetaField.TITLES] = formatted_titles

        meta_dict = Meta.update_field_types(meta_dict)
        # Hotfix
        keys_to_remove = ["country_from_008", "unknown"]
        new_dict = {}
        for key, values in meta_dict.items():
            if key not in keys_to_remove:
                new_dict[key] = values
        meta_dict = new_dict

        # Always add issue type (bib style):
        if MetaField.ISSUE_TYPE not in meta_dict:
            meta_dict[MetaField.ISSUE_TYPE] = DEFAULT_ISSUE_TYPE

        return meta_dict

class TableOfContents:
    def __init__(self, extracted_meta: dict):
        self.__chapters: List[str] = []
        self.__table_of_contents_str: str = ""
        self.__table_of_contents_lang: str = ""
        self._text_parts: List[dict] = extracted_meta.get(MetaField.TEXT_PARTS, [])
        self._authors: List[dict] = extracted_meta.get(MetaField.AUTHORS, [])
        self._sections: List[dict] = extracted_meta.get(MetaField.SECTIONS, [])

    def _clean_chapter(self, chapter: str) -> str:
        LOGGER.debug(f"Chapter title before cleaning: '{chapter}'")
        chapter = re.sub(r"(?<=[^.])\s*([.]\s*)+(\s*\d*|[IVXLCDM]*)*(?=$)", "", chapter)
        LOGGER.debug(f"Chapter title after cleaning: '{chapter}'")
        return chapter

    def _split_chapter(self, cleaned_chapter: str) -> List[str]:
        split_pattern = r"([.]\s*){3,}((\s*\d*|[IVXLCDM]*)\s)*"
        split_match = re.search(split_pattern, cleaned_chapter)
        chapters = [cleaned_chapter]
        if split_match:
            LOGGER.debug(f"Detected a split pattern in chapter '{cleaned_chapter}'. Splitting it into two.")
            splitter = split_match.group()
            chapters = cleaned_chapter.split(splitter, 1)
            chapters = [c.strip() for c in chapters]
        return chapters

    def _filter_by_case(self, chapters: List[str],
            min_ratio: float = TABLE_OF_CONTENTS_MIN_UPPERCASE_RATIO,
            min_avg_length: int = TABLE_OF_CONTENTS_MIN_UPPERCASE_AVG_LENGTH
    ) -> List[str]:
        """ If some titles are in uppercase and others are not,
        assume that the lower-case titles are false positives
        and filter them out.
        """
        chapter_stats = {
            "upper": [],
            "other": [],
            "upper_lens": [],
            "other_lens": []
        }
        out = chapters
        for chapter in chapters:
            if chapter.upper() == chapter:
                chapter_stats["upper"].append(chapter)
                chapter_stats["upper_lens"].append(len(chapter))
            else:
                chapter_stats["other"].append(chapter)
                chapter_stats["other_lens"].append(len(chapter))
        if chapters and len(chapter_stats["upper"])/len(chapters) >= min_ratio:
            if statistics.mean(chapter_stats["upper_lens"]) >= min_avg_length:
                out = chapter_stats["upper"]
        return out

    @property
    def table_of_contents_lang(self) -> str:
        if not self.__table_of_contents_lang:
            for text_part in self._text_parts:
                text_type = text_part.get("text_type", "")
                if text_type == TextPartLabel.TABLE_OF_CONTENTS:
                    self.__table_of_contents_lang = text_part.get("language", "")
        return self.__table_of_contents_lang

    @property
    def table_of_contents_str(self) -> str:
        if not self.__table_of_contents_str:
            for text_part in self._text_parts:
                text_type = text_part.get("text_type", "")
                if text_type == TextPartLabel.TABLE_OF_CONTENTS:
                    self.__table_of_contents_str = text_part.get("text_value", "")
        return self.__table_of_contents_str

    @property
    def table_of_contents(self) -> List[str]:
        """ Extract chapter names from table of contents.
        """
        if not self.__chapters:
            if self._sections:
                chapters = []
                languages = defaultdict(int)
                most_frequent_lang = ""
                for section in self._sections:
                    titles = section.get(MetaField.TITLES, [])
                    _authors = section.get(MetaField.AUTHORS, [])
                    lang = section.get("language", "")

                    languages[lang]+=1
                    chapter = titles[0].get("title") if titles else ""
                    authors = [author.get("name") for author in _authors]
                    if chapter:
                        chapters.append(
                            {"chapter": chapter, "authors": authors}
                        )
                if languages:
                    most_frequent_lang = sorted(
                        list(languages.items()),
                        key = lambda x: x[1],
                        reverse=True
                    )[0][0]
                self.__chapters = {
                    "content": chapters,
                    "language": most_frequent_lang
                }

            else:
                raw_chapters = self.table_of_contents_str.split("\n")
                _chapters = [
                    chapter.strip()
                    for chapter in raw_chapters
                    if chapter.strip()
                ]
                filtered_chapters = self._filter_by_case(_chapters)
                content = []
                for chapter in filtered_chapters:
                    cleaned_chapter = self._clean_chapter(chapter)
                    chapters = self._split_chapter(cleaned_chapter)
                    for chapter in chapters:
                        content.append({"chapter": chapter, "authors": []})
                self.__chapters = {
                    "content": content,
                    "language": self.table_of_contents_lang

                }
        return self.__chapters
