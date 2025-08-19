import json
from typing import List, Tuple, Dict
from rara_meta_extractor.config import LOGGER
from rara_meta_extractor.constants.data_classes import TextPartLabel, MetaField
from rara_meta_extractor.text_part_classifiers.base_text_part_classifier import BaseTextPartClassifier

class EPUBTextPartClassifier(BaseTextPartClassifier):
    def __init__(self):
        super().__init__()
        self.used_sections: list = []
        self.section_title_filter: List[str] = [
            "peatükk", "stseen", "vaatus", "osa", "jagu",
            "üks", "kaks", "kolm", "esimene", "teine", "kolmas"
        ]
        self.section_title_filter_roman: List[str] = [
            "II", "IV", "IX", "ii", "iv",
            "ix", "Ii", "Iv", "Ix", "XII"
        ]
        self.section_title_filter_numbers: List[str] = [
            "1", "2", "3", "4", "5"
        ]
        self.conclusion_upper_keywords: list = []

    def _toc_from_section_titles(self, digitized_texts: List[dict])-> List[dict]:
        """ Trying to put together a table of contents
        for ebooks through section titles.
        """
        # Filter for getting rid of nondescript chapter names
        # we don't want in out table of contents
        toc = []
        has_title = [
            txt for txt in digitized_texts
            if "section_title" in txt
        ]

        title_not_none = [
            txt for txt in has_title
            if txt["section_title"] != None
        ]

        if len(set([section["section_title"] for section in title_not_none])) > 1:
            for section in title_not_none:
                stripped_title = section["section_title"].strip().strip(",.")
                if stripped_title in self.section_title_filter_roman:
                    return toc
                if stripped_title in self.section_title_filter_numbers:
                    return toc
                for filter_item in self.section_title_filter:
                    if filter_item in stripped_title.lower():
                        return toc
            for section in title_not_none:
                if section["section_title"] not in toc:
                    toc.append(section["section_title"])
        return toc

    def _ebooks_get_conclusion_from_meta(self, parsed_meta: dict )-> list:
        """ Using different methods to find conclusions.
        """
        if MetaField.INCLUDED_TEXT in parsed_meta:
            if parsed_meta[MetaField.INCLUDED_TEXT] != None:
                return [parsed_meta[MetaField.INCLUDED_TEXT]]
        return []

    def get_conclusions(self, digitized_texts: List[dict], epub_meta: dict = {}):
        """ Using different methods to find conclusions.
        """
        LOGGER.debug(f"Searching for conclusions.")
        concl = self._look_through_section_titles(
            digitized_texts=digitized_texts,
            search_type=TextPartLabel.CONCLUSION
        )
        if not concl:
            concl = self._look_through_texts(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.CONCLUSION
            )

        # Second option: get conclusion info
        # from parsed_meta (if exists)
        if not concl:
            # ... or whatever key parsed meta is saved as
            if epub_meta:
                # No language data in parsed metadata, so used as second option
                concl = self._ebooks_get_conclusion_from_meta(
                    parsed_meta=epub_meta
                )
        return concl

    def get_tables_of_content(self, digitized_texts: List[dict]):
        """ Using different methods to find tables of content
        for ebook files.
        """
        LOGGER.debug(f"Searching for tables_of_content.")
        # Since ebooks don't have authors names associated with chapters,
        # we first try to fetch section titles by themselves
        toc = self._toc_from_section_titles(digitized_texts=digitized_texts)
        if not toc:
            # After this we look at where the toc should be
            # according to section titles and extract the text
            toc = self._look_through_section_titles(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.TABLE_OF_CONTENTS
            )
        if not toc:
            # After this we look at the text itself using keywords
            toc = self._look_through_texts(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.TABLE_OF_CONTENTS
            )
        return toc

    def get_abstracts(self, digitized_texts: List[dict]):
        """ Using different methods to find abstracts.
        """
        LOGGER.debug(f"Searching for abstracts.")
        abstracts = self._look_through_section_titles(
            digitized_texts=digitized_texts,
            search_type=TextPartLabel.ABSTRACT
        )
        if not abstracts:
            abstracts = self._look_through_texts(
            digitized_texts=digitized_texts,
            search_type=TextPartLabel.ABSTRACT
        )
        return abstracts

    def get_parts_of_text(self, digitized_texts: List[dict], epub_meta: dict) -> dict:
        """ Getting results for ebooks.

        Parameters
        -----------
        digitized_texts: List[dict]
            `texts` from Digitizer output.
        epub_meta: dict
            Output of `EPUBMetaExtractor.extract_meta()`.

        Returns
        -----------
        dict
            TODO
        """
        LOGGER.info(f"Classifying EPUB text sections.")
        tables_of_content = self.get_tables_of_content(
            digitized_texts=digitized_texts
        )
        conclusions = self.get_conclusions(
            digitized_texts=digitized_texts,
            epub_meta=epub_meta
        )
        abstracts = self.get_abstracts(
            digitized_texts=digitized_texts
        )
        results = self._results_correct_fields(
            {
                "table_of_contents": tables_of_content,
                "conclusions": conclusions,
                "abstracts": abstracts
            }
        )
        return results
