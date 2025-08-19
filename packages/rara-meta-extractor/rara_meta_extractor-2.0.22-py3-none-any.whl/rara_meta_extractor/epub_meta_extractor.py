from typing import Dict, Any, List, Tuple
from pprint import pprint
import regex as re
import json
import typing
from copy import deepcopy
from rara_meta_extractor.config import (
    EPUB_AUTHOR_ROLES_DICT, EPUB_META_KEYS, LOGGER, EPUB_AUTHOR_MAX_LENGTH, EPUB_AUTHOR_MAX_N_WORDS
)
from rara_meta_extractor.constants.data_classes import MetaField
from rara_meta_extractor.tools.meta_formatter import Author, Title, Meta

class EPUBMetaExtractor:
    def __init__(self):
        self.relator_to_est: dict = EPUB_AUTHOR_ROLES_DICT
        self.meta_keys: List[str] = EPUB_META_KEYS
        self.metadata_set = {
            meta_key: {}
            for meta_key in self.meta_keys
        }
        self.find_script = re.compile(r"<[^>]*>")
        self.cover_name = re.compile(r"[^.]*.(xht|ht|x)ml")
        self.isbn_description = re.compile(
            r"ISBN ^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$"
        )

    def _remove_empty(self, data_list: list) -> List[Any]:
        filtered = [item for item in data_list if item]
        return filtered

    def _get_values(self, data_list: list) -> List[Any]:
        values = [
            elem.get("value", elem)
            for elem in data_list
        ]
        return values

    def _replace_key(self, url_key: str) -> str:
        if "}" in url_key:
            new_key = url_key.split("}")[-1]
            return new_key
        else:
            return url_key

    def _iterate_until_find_data_dict(self, structure: dict) -> dict:
        structure_data = {}
        for structure_item in structure:
            if isinstance(structure_item, str):
                structure_data["value"] = structure_item
            else:
                for tuple_item in structure_item:
                    if isinstance(tuple_item, str):
                        structure_data["value"] = tuple_item
                    elif isinstance(tuple_item, dict):
                        if len(tuple_item) > 0:
                            [
                                structure_data.update(
                                    {self._replace_key(key): value}
                                )
                                for key, value in tuple_item.items()
                            ]
        return structure_data

    def _iterate_until_find_data_list(self,
            structure: List[Any]
    ) -> List[dict]:
        structure_data = []
        for structure_item in structure:
            if None not in structure_item:
                temp_data = {}
                if isinstance(structure_item, str):
                    if structure_item is not None:
                        temp_data["value"] = structure_item
                else:
                    for tuple_item in structure_item:
                        if isinstance(tuple_item, str):
                            temp_data["value"] = tuple_item
                        elif isinstance(tuple_item, dict):
                            if len(tuple_item) > 0:
                                [
                                    temp_data.update(
                                        {self._replace_key(key): value}
                                    )
                                    for key, value in tuple_item.items()
                                ]
                structure_data.append(temp_data)
        return structure_data

    def _iterate_until_find_data(self, structure: List[Any] | dict ) -> list:
        # Seeing if multiple values inside the structure
        if len(structure) == 1:
            structure_data = self._iterate_until_find_data_dict(structure)
            return [structure_data]
        else:
            structured_data_list = []
            temp_dict = self._iterate_until_find_data_list(structure)
            structured_data_list.extend(temp_dict)
            return structured_data_list


    def _parse_authors(self,
            authors: List[dict], is_primary: bool,
            unk_key: str = "unknown", simple: bool = False
    ) -> List[dict]:
        parsed_authors = []
        for author in authors:
            original_role = author.get("role", "")
            role = self.relator_to_est.get(original_role, unk_key)
            name = author.get("value", author)

            author_structure = Author(
                name=name,
                is_primary=is_primary,
                role=role,
                map_role=False
            ).to_dict(simple=simple)

            if role == unk_key:
                LOGGER.debug(f"Could not detect role for author: {author}.")

            if Author.is_false_positive(
                author_name=author_structure.get("name"),
                max_n_words=EPUB_AUTHOR_MAX_N_WORDS,
                max_length=EPUB_AUTHOR_MAX_LENGTH
            ):
                LOGGER.info(
                    f"Assuming that author '{author_structure}' is a " \
                    f"false positive based on the name's length " \
                    f"and number of words. Not adding it to the results."
                )
                continue
            parsed_authors.append(author_structure)
        return parsed_authors

    def _authors_correct_structure(self,
            parsed_metadata: dict, unk_key: str = "unknown", simple: bool = False
    ) -> List[dict]:
        authors = []

        creators = parsed_metadata.get("creator", [])
        contributors = parsed_metadata.get("contributor", [])

        if not creators:
            creators = []
        if not contributors:
            contributors = []

        creators = self._remove_empty(creators)
        contributors = self._remove_empty(contributors)

        parsed_creators = self._parse_authors(
            authors=creators, is_primary=True, simple=simple
        )
        parsed_contributors = self._parse_authors(
            authors=contributors, is_primary=False, simple=simple
        )

        authors = parsed_creators + parsed_contributors
        return authors

    def _get_publication_time(self, dates: List[dict]) -> List[str] | str:
        publication_time = [
            date.get("value")
            for date in dates
        ]
        if len(publication_time) == 1:
            publication_time = publication_time[0]
        return publication_time

    def _process_date(self, parsed_metadata: dict) -> dict:
        relevant_dates = ["creation", "publication"]
        date_info = {}
        dates = parsed_metadata.get("date", [])
        if len(dates) == 1:
            publication_time = self._get_publication_time(
                dates=dates
            )

        else:
            events = [
                date for date in dates
                if "event" in date
            ]
            if events:
                publication_creation = [
                    date for date in events
                    if date.get("event", "") in relevant_dates
                ]
                if publication_creation:
                    publication_time = self._get_publication_time(
                        dates=publication_creation
                    )

                else:
                    publication_time = self._get_publication_time(
                        dates=events
                    )
            else:
                publication_time = self._get_publication_time(
                    dates=dates
                )

        date_info["publication_date"]  = publication_time # TODO!
        return date_info

    def _identify_date(self,
            parsed_metadata: dict, unk_key: str = "unknown"
    ) -> dict:
        date_info = {"publication_date": unk_key}

        dates = parsed_metadata.get("date", [])
        timestamps = parsed_metadata.get("timestamp", [])

        if dates:
            parsed_date = self._process_date(parsed_metadata)
            date_info.update(parsed_date)
            publication_time = date_info.get("publication_date")

            if "0101-01-01" in publication_time and timestamps:
                timestamp = timestamps[0].get("content", "")
                if timestamp and timestamp != "0101-01-01T00:00:00+00:00":
                    date_info["publication_date"] = timestamp

        elif timestamps:
            timestamp = timestamps[0].get("content", "")
            if timestamp and timestamp != "0101-01-01T00:00:00+00:00":
                date_info["publication_date"] = timestamp # TODO!!!!
        return date_info

    def get_series_data(self, parsed_metadata: dict) -> dict:
        series_info = {}
        series = parsed_metadata.get("series", [])
        if series:
            # TODO!!!!
            series_info["added_series_volume"] = str(int(float(
                parsed_metadata["series_index"][0]["content"]
            )))
            series_info["added_series_title"] = series[0]["content"]
        return series

    def _correct_structure_other_metadata(self,
            parsed_metadata: dict, other_meta: dict
    ) -> dict:
        other_vals = {}
        if parsed_metadata["identifier"] != {}:
            for identifier in parsed_metadata["identifier"]:
                if "value" in identifier:
                    if "id" in identifier:
                        if identifier["id"] in ["ISBN", "isbn-id"]:
                            other_vals["isbn"] = [identifier["value"]]

                        if identifier["id"] == "ISSN":
                            other_vals["issn"] = [identifier["value"]]

                        if identifier["id"].lower() in ["bookid", "book-id", "uuid_id"]:
                            if "ID" not in other_vals:
                                other_vals["ID"] = [identifier["value"]]
                            else:
                                other_vals["ID"] = other_vals["ID"].append(
                                    identifier["value"]
                                )
                    elif "scheme" in identifier:
                        if identifier["scheme"] == "ISBN":
                            other_vals["isbn"] = [identifier["value"]]

                        if identifier["scheme"] == "ISSN":
                            other_vals["issn"] = [identifier["value"]]

                        if identifier["scheme"].lower() in ["bookid", "uuid", "uid"]:
                            if "ID" not in other_vals:
                                other_vals["ID"] = [identifier["value"]]
                            else:
                                other_vals["ID"] = other_vals["ID"].append(
                                    identifier["value"]
                                )
        if parsed_metadata["source"] != {}:
            for source in parsed_metadata["source"]:
                if "id" in source:
                    if source["id"] == "src-id":
                        if "ID" not in other_vals:
                            other_vals["ID"] = [source["value"]]
                        else:
                            other_vals["ID"] = other_vals["ID"].append(
                                source["value"]
                            )
        series = self.get_series_data(parsed_metadata)
        if series != {}:
            other_vals["series"] = series

        if parsed_metadata["publisher"] != {}:
            other_vals["publisher"] = [
                item["value"] if "value" in item else item
                for item in parsed_metadata["publisher"]
            ]
        if parsed_metadata["format"] != {}:
            other_vals["task_task"] = {
                "file_type": parsed_metadata["format"][0]["value"]
            }
        if len(parsed_metadata["subject"]) > 0:
            if len(parsed_metadata["subject"][0]) > 0:
                other_vals["uncontrolled_index_termin"] = [
                    item["value"]
                    for item in parsed_metadata["subject"]
                ]
        if len(parsed_metadata["type"]) > 0:
            if len(parsed_metadata["type"][0]) > 0:
                other_vals["uncontrolled_index_termin"] = [
                    item["value"]
                    for item in parsed_metadata["type"]
                ]
        if len(parsed_metadata["rights"]) > 0:
            other_vals["copyright_year"] = [
                item["value"]
                if "value" in parsed_metadata["rights"] else item
                for item in parsed_metadata["rights"]
            ]
        if other_meta != {}:
            [
                other_vals[key].append(val)
                for key, val in other_meta.items()
                if key in other_vals and val not in other_vals[key]
            ]
        return other_vals

    def _clean_script_description(self, description: str) -> str:
        if self.find_script.search(description):
            subbed_description = self.find_script.sub("", description)
            return subbed_description
        else:
            return description

    def _parse_isbn_description(self, description: str) -> str | None:
        if self.isbn_description.match(description):
            return None
        else:
            return description

    def _clean_descriptions(self, included_text: str|list, correct_structure: dict) -> dict:
        if isinstance(included_text, list):
            descriptions = []
            for description in included_text:
                if description != {}:
                    description = description.strip()
                    if len(description) > 3:
                        # Description contains
                        if "<" in description:
                            descriptions.append(
                                self._clean_script_description(description)
                            )
                        # Description refers to cover file
                        elif self.cover_name.match(description):
                            pass
                        elif description.startswith("ISBN"):
                            if "ISBN" not in correct_structure:
                                isbn = self._parse_isbn_description(description)
                                if isbn:
                                    correct_structure["ISBN"] = description.split()[-1]
                                else:
                                    descriptions.append(description)
                        else:
                            descriptions.append(description)
            if descriptions != []:
                correct_structure[MetaField.INCLUDED_TEXT] = {
                    "text_value": descriptions
                }

        elif isinstance(included_text, str):
            description = included_text.strip()
            if len(description) > 3:
                # Description likely contains script
                if "<" in description:
                    correct_structure[MetaField.INCLUDED_TEXT] = {
                        "text_value": self._clean_script_description(description)
                    }
                # Description refers to cover file
                elif self.cover_name.match(description):
                    pass
                elif description.startswith("ISBN"):
                    if "ISBN" not in correct_structure:
                        isbn = self._parse_isbn_description(description)
                        if isbn:
                            correct_structure["ISBN"] = description.split()[-1]
                        else:
                            correct_structure[MetaField.INCLUDED_TEXT] = {
                                "text_value": description
                            }
                else:
                    correct_structure[MetaField.INCLUDED_TEXT] = {
                        "text_value": description
                    }
        return correct_structure

    def postfilter_authors(self, authors: list) -> Tuple[Dict, list]:
        other_meta = {}
        new_authors = []
        for author in authors:
            if author["role"] in ["väljaandja", "tootja", "levitaja"]:
                if author["role"] == "väljaandja":
                    other_meta[MetaField.MANUFACTURER] = author["name"]
                elif author["role"] == "tootja":
                    other_meta[Metafield.PUBLISHER] = author["name"]
                elif author["role"] == "levitaja":
                    other_meta[MetaField.DISTRIBUTER_NAME] = author["name"]
            else:
                new_authors.append(author)
        return new_authors, other_meta

    def get_included_text(self, parsed_metadata: dict)-> list | str:
        descriptions_info = []

        descriptions = parsed_metadata.get("description", [])
        coverages = parsed_metadata.get("coverage", [])

        parsed_descriptions = self._get_values(descriptions)
        parsed_coverages = self._get_values(coverages)

        descriptions_info = parsed_descriptions + parsed_coverages
        if len(descriptions_info) == 1:
            included_texts = descriptions_info[0]
        else:
            included_texts = descriptions_info
        return included_texts

    def get_titles(self, parsed_metadata: dict) -> dict:
        task_title = {}
        titles = [
            item.get("value", item)
            for item in parsed_metadata.get("title", [])
        ]
        title_sort = parsed_metadata.get("title_sort", [])
        if len(title_sort) > 0:
            for title in title_sort:
                value = title.get("content")
                if value not in titles:
                    titles.append(value)
        task_title["title"] = titles # TODO: move key somewhere else?
        return task_title


    def correct_structure(self, parsed_metadata: dict, simple: bool = False) -> dict:
        # Language should be coming from digitizer,
        # ignore ebook language for now
        correct_structure = {
            "task_title": self.get_titles(parsed_metadata)
        }
        authors, other_meta = self.postfilter_authors(
            authors=self._authors_correct_structure(parsed_metadata, simple=simple)
        )
        correct_structure.update(
            {"task_author": authors}
        )
        correct_structure.update(
            self._correct_structure_other_metadata(
                parsed_metadata=parsed_metadata,
                other_meta=other_meta
            )
        )
        correct_structure.update(
            self._identify_date(parsed_metadata)
        )
        included_text = self.get_included_text(parsed_metadata)
        if included_text != [] and included_text != {}:
            correct_structure = self._clean_descriptions(
                included_text=included_text,
                correct_structure=correct_structure
            )
        return correct_structure

    def parse_ebook_metadata(self, metadata: dict) -> dict:
        metadata_set = deepcopy(self.metadata_set)
        for metadata_item in metadata_set:
            for value in metadata:
                if metadata_item in value:
                    metadata_set[metadata_item] = self._iterate_until_find_data(
                        structure=value[metadata_item]
                    )
        return metadata_set

    def _reformat(self, item_correct_structure: dict, simple: bool = False, language: str = "") -> dict:
        # Hotfix
        key_map = {
            "task_author": MetaField.AUTHORS,
            "task_title": MetaField.TITLES
        }
        new_structure = {}
        for key, value in list(item_correct_structure.items()):
            key = key_map.get(key, key)
            if key == MetaField.TITLES:
                value = Title(titles=value.get("title", []), lang=language).to_dicts(simple=simple)
            new_structure[key] = value
        new_structure = Meta.update_field_types(new_structure)
        return new_structure


    def extract_meta(self, epub_metadata: dict, simple: bool = False, language: str = "") -> dict:
        # is the type correct????
        metadata_from_digitizer = list(epub_metadata.values())
        item_parsed = self.parse_ebook_metadata(metadata_from_digitizer)
        item_correct_structure = self.correct_structure(item_parsed, simple=simple)
        # hotfix:
        fields_to_ignore = ["ID", "copyright_year"]#, MetaField.INCLUDED_TEXT]
        for field in fields_to_ignore:
            item_correct_structure.pop(field, "")
        item_correct_structure = self._reformat(item_correct_structure, simple=simple, language=language)

        return item_correct_structure
