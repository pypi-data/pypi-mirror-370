from typing import List

from bs4 import BeautifulSoup, Tag

# TODO: rename EPUB_AUTHOR_ROLES_DICT
from rara_meta_extractor.config import (
    EPUB_AUTHOR_ROLES_DICT
)
from rara_meta_extractor.constants.data_classes import (
    MetaField, AuthorField, TitleTypeSimple, TitleType, ISSUE_STYLE_MAP
)
from rara_meta_extractor.tools.meta_formatter import Author, Title, Meta


class MetsAltoMetaExtractor:
    def __init__(self):
        self.relator_to_est: dict = EPUB_AUTHOR_ROLES_DICT

        # Needed subitems from METS ALTO meta fields
        # (don't want separate metadata for pictures, chapters/articles)
        self.relevant_subitems = ["PRINT", "ELEC", "ISSUE"]

    def _get_role_equivalent(self, role_candidate: str) -> str:
        """ Find MARC relator roles equivalents, used only for parsing
        authors/contributors from sections_meta fields.
        If role is not in dictionary, then role is unknown
        """
        role = self.relator_to_est.get(role_candidate, AuthorField.UNKNOWN)
        return role

    def _parse_section_meta(
            self,
            sec_meta: Tag | str,
            seq_nr: str,
            article_id: str,
            simple: bool = False
    ) -> dict:
        """
        Parse section meta.

        Parameters
        ----------
        article_id : str Reference uuid to match a periodical with database records.
        """
        section_parsed = {"sequence_number": seq_nr, "article_id": article_id}

        if isinstance(sec_meta, str):
            sec_meta = BeautifulSoup(sec_meta, "lxml-xml")

        if sec_meta.title:
            title = [tag.string for tag in sec_meta.find_all("title")]
            section_parsed["title"] = title

        if sec_meta.titleInfo:
            if not isinstance(sec_meta.titleInfo, str):
                if "xml:lang" in sec_meta.titleInfo.attrs.keys():
                    title_language = sec_meta.titleInfo["xml:lang"]
                    section_parsed["title_language"] = title_language

        titles = section_parsed.pop("title", [])
        title_lang = section_parsed.pop("title_language", "")
        title_type = TitleType.METS_TITLE if not simple else TitleTypeSimple.METS_TITLE

        new_titles = Title(titles=titles, lang=title_lang, title_type=title_type).to_dicts(
            simple=simple
        )
        section_parsed[MetaField.TITLES] = new_titles
        kw = [tag for tag in sec_meta.find_all("subject")]

        if kw != []:
            keywords = [
                {
                    "original_keyword_value": k.topic.string
                }
                for k in kw
            ]
            section_parsed["other_keywords"] = keywords

        names = [tag for tag in sec_meta.find_all("name")]

        if names:
            authors = []
            for name in names:
                author_type = name.get("type", "")
                author_name = " ".join(
                    [
                        namePart.string
                        for namePart in name.find_all("namePart")
                    ]
                )
                author_role = self._get_role_equivalent(
                    role_candidate=name.roleTerm.string
                )
                new_author = Author(
                    name=author_name,
                    role=author_role,
                    is_primary=True,
                    author_type=author_type,
                    map_role=False
                ).to_dict(simple=simple)
                authors.append(new_author)

            # We don't know if author is primary or not, so this is
            # currently left out of the authors list,
            # however we can get the author type
            section_parsed[MetaField.AUTHORS] = authors

        if sec_meta.languageTerm:
            language_term = sec_meta.languageTerm.string
            section_parsed["language"] = language_term
        return section_parsed

    def _run_sections_parsing(self, digitized_texts: List[dict], simple: bool = False) -> List[dict]:
        """ Optional, useful for getting tables of
        content/parts of text.
        """
        sections_meta = []

        section_meta = [
            {
                "sequence_number": section["sequence_nr"],
                "section_meta": section["section_meta"],
                "article_id": section.get("article_id", ""),
            }
            for section in digitized_texts
            if section.get("section_meta", None)
        ]
        if section_meta != [{}]:
            for sec_meta in section_meta:
                section_meta_p = self._parse_section_meta(
                    sec_meta=sec_meta.get("section_meta"),
                    seq_nr=sec_meta.get("sequence_number"),
                    article_id=sec_meta.get("article_id", ""),
                    simple=simple
                )
                sections_meta.append(section_meta_p)
        return sections_meta

    def _check_if_in_dict(self, target_dict: dict, add_key: str, val: str) -> dict:
        """ Checking if value, key already present in target dictionary.
        Adding key to dictionary, if not present, appending value
        to dictionary key if not present etc.
        """
        if add_key in target_dict:
            if val not in target_dict[add_key]:
                target_dict[add_key].append(val)
        else:
            target_dict[add_key] = [val]
        return target_dict

    def _parse_issn(self, issn: str) -> str:
        parts = issn.split("-")
        parsed_issn = "".join(parts)
        return [parsed_issn]

    def extract_meta(
            self,
            mets_alto_metadata: List[str], digitized_texts: List[dict], simple: bool = False
    ) -> dict:

        mini_parsed_xml = {
            MetaField.TITLES: {},
            "task_task": {}
        }

        for subitem in mets_alto_metadata:

            si_soup = BeautifulSoup(subitem, "lxml-xml")
            relevant_subitems = [
                n_subitem
                for n_subitem in self.relevant_subitems
                if n_subitem in si_soup.dmdSec["ID"]
            ]

            if relevant_subitems:
                if si_soup.title != None:
                    title = si_soup.title.string
                    if title:
                        mini_parsed_xml[MetaField.TITLES] = self._check_if_in_dict(
                            target_dict=mini_parsed_xml[MetaField.TITLES],
                            add_key="title",
                            val=title
                        )

                if si_soup.partNumber:
                    part_nr = si_soup.partNumber.string
                    mini_parsed_xml[MetaField.TITLES]["part_number"] = part_nr

                if si_soup.dateIssued:
                    dateissued = si_soup.dateIssued.string
                    dateissued = str(dateissued)
                    mini_parsed_xml = self._check_if_in_dict(
                        target_dict=mini_parsed_xml,
                        add_key="publication_date",
                        val=dateissued
                    )

                if si_soup.copyrightDate:
                    datecpr = si_soup.copyrightDate.string
                    mini_parsed_xml["copyright_year"] = datecpr

                if si_soup.identifier:
                    identifier = [
                        {
                            "id": idf.string,
                            "type": idf["type"]
                        }
                        if "type" in idf.attrs.keys()
                        else {"id": idf.string, "type": "unknown"}
                        for idf in si_soup.find_all("identifier")
                    ]
                    other_ids = []
                    for id_ex in identifier:
                        if id_ex["type"] == "CatalogueIdentifier":
                            mini_parsed_xml["ester_ID"] = id_ex["id"]
                        elif id_ex["type"] == "issn":
                            mini_parsed_xml["issn"] = self._parse_issn(id_ex["id"])
                        elif id_ex["type"] == "local":
                            mini_parsed_xml["task_task"]["article_date"] = id_ex["id"]
                        else:
                            other_ids.append(id_ex["id"])

                    if other_ids != []:
                        mini_parsed_xml["ID"] = other_ids

                if si_soup.typeOfResource:
                    resource_type = si_soup.typeOfResource.string
                    if "content_type" not in mini_parsed_xml:
                        mini_parsed_xml["content_type"] = resource_type

                if si_soup.titleInfo:
                    if not isinstance(si_soup.titleInfo, str):
                        if "xml:lang" in si_soup.titleInfo.attrs.keys():
                            title_language = si_soup.titleInfo["xml:lang"]
                            if "title_language" not in mini_parsed_xml[MetaField.TITLES]:
                                mini_parsed_xml[MetaField.TITLES]["title_language"] = title_language

                if si_soup.genre:
                    genre = [
                        genre.string
                        for genre in si_soup.find_all("genre")
                        if genre.string != "\n"
                    ]
                    if genre:
                        for g in genre:
                            mini_parsed_xml["task_task"] = self._check_if_in_dict(
                                target_dict=mini_parsed_xml["task_task"],
                                add_key="style",
                                val=g
                            )
        sections_meta_parsed = self._run_sections_parsing(digitized_texts, simple=simple)
        mini_parsed_xml.update(
            {
                "sections": sections_meta_parsed
            }
        )

        titles = mini_parsed_xml.pop(MetaField.TITLES, {})
        new_titles = Title(
            titles=titles.get("title", []),
            lang=titles.get("title_language", ""),
            part_number=titles.get("part_number", "")
        ).to_dicts(simple=simple)
        mini_parsed_xml[MetaField.TITLES] = new_titles
        task_task = mini_parsed_xml.pop("task_task")
        raw_issue_types = task_task.get("style", [])
        if raw_issue_types:
            issue_type = ISSUE_STYLE_MAP.get(raw_issue_types[0], "")
        mini_parsed_xml[MetaField.ISSUE_TYPE] = issue_type
        mini_parsed_xml = Meta.update_field_types(
            meta_dict=mini_parsed_xml,
            custom_keys_to_ignore=["sections"]
        )

        return mini_parsed_xml
