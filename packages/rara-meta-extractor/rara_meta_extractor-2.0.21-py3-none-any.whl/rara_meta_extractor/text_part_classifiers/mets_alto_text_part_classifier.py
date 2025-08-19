import json
from typing import List, Tuple
from pprint import pprint
from rara_meta_extractor.constants.data_classes import TextPartLabel, MetaField
from rara_meta_extractor.text_part_classifiers.base_text_part_classifier import BaseTextPartClassifier
from rara_meta_extractor.config import LOGGER

class MetsAltoTextPartClassifier(BaseTextPartClassifier):
    def __init__(self):
        super().__init__()
        self.section_types: dict = {
            TextPartLabel.TABLE_OF_CONTENTS: "TABLE_OF_CONTENTS",
            TextPartLabel.CONCLUSION: "CONCLUSION",
            TextPartLabel.ABSTRACT: "ABSTRACT"
        }
        self.used_sections: list = []
        self.conclusion_upper_keywords: list = []

    def _metsalto_parsed_sections_to_toc(self,
            metsalto_parsed_texts: list
    ) -> Tuple[list, list]:
        """ Putting together table of contents using metsalto
        section titles and authors from section meta.
        """
        toc = []

        if metsalto_parsed_texts:
            for item in metsalto_parsed_texts:
                sec_data = {}
                if MetaField.TITLES in item:
                    sec_data["title"] = item[MetaField.TITLES]
                if MetaField.AUTHORS in item:
                    sec_data["names"] = [
                        name["name"]
                        for name in item[MetaField.AUTHORS]
                    ]
                toc.append(sec_data)
        return toc

    def _get_section_types(self,
            digitized_texts: List[dict], search_type: str
    ) -> List[dict]:
        """ Getting text by using section types.
        """
        found_items = []
        for section in digitized_texts:
            if "section_type" in section:
                if section["section_type"] == self.section_types[search_type]:
                    if search_type == TextPartLabel.TABLE_OF_CONTENTS:
                        found_items.append(self._remove_double_toc(section["text"]))
                        self.used_sections.append(section["sequence_nr"])
                    elif search_type == TextPartLabel.CONCLUSION:
                        found_items.append(
                            {
                                "sequence_nr": section["sequence_nr"],
                                "text_value": section["text"],
                                "task_language": section["language"]
                            }
                        )
                        self.used_sections.append(section["sequence_nr"])
                    else:
                        found_items.append(
                            {
                                "text_value":section["text"],
                                "task_language":section["language"]
                            }
                        )
                        self.used_sections.append(section["sequence_nr"])
        if search_type == TextPartLabel.CONCLUSION:
            found_items = self._postprocess_concl(found_items)
        return found_items

    def get_conclusions(self, digitized_texts: List[dict]) -> List[dict]:
        """ Using different methods to find conclusions.
        """
        LOGGER.debug(f"Searching for conclusions.")
        concl = self._get_section_types(
            digitized_texts=digitized_texts,
            search_type=TextPartLabel.CONCLUSION
        )
        if not concl:
            concl = self._look_through_section_titles(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.CONCLUSION
            )
        if not concl:
            concl = self._look_through_texts(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.CONCLUSION
            )
        return concl

    def get_tables_of_content(self,
            metsalto_sections, digitized_texts: List[dict]
    ) -> List[dict]:
        """ Using diferents methods to find tables of content.
        """
        LOGGER.debug(f"Searching for tables of content.")
        # Using different methods to find tables of content for mets-alto files
        # since mets_alto usually has authors names associated with chapters,
        # we first try to fetch section titles and author names by themselves
        toc = self._metsalto_parsed_sections_to_toc(metsalto_sections)
        if not toc:
            # then we try to extract the text through section types
            toc = self._get_section_types(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.TABLE_OF_CONTENTS
            )
        if not toc:
            # after this we look at where the toc should be according
            # to section titles and extract the text
            toc = self._look_through_section_titles(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.TABLE_OF_CONTENTS
            )
        if not toc:
            # after this we look at the text itself using keywords
            toc = self._look_through_texts(
                digitized_texts=digitized_texts,
                search_type=TextPartLabel.TABLE_OF_CONTENTS
            )
        return toc

    def get_abstracts(self, digitized_texts: List[dict]) -> List[dict]:
        """ Using different methods to find abstracts.
        """
        LOGGER.debug(f"Searching for abstracts.")
        abstracts = self._get_section_types(
            digitized_texts=digitized_texts,
            search_type=TextPartLabel.ABSTRACT
        )
        if not abstracts:
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

    def get_parts_of_text(self, digitized_texts: List[dict], mets_alto_meta: dict) -> dict:
        """ Getting results for mets-alto files

        Parameters
        -----------
        digitized_texts: List[dict]
            `texts` from Digitizer output.
        epub_meta: dict
            Output of `MetsAltoMetaExtractor.extract_meta()`.

        Returns
        -----------
        dict
            TODO
        """
        LOGGER.info(f"Classifying METS/ALTO text sections.")
        # TODO: move "sections" key into constants! but same
        # with this key in mets alto meta extractor!
        metsalto_sections = mets_alto_meta.get(MetaField.SECTIONS, [])

        tables_of_content = self.get_tables_of_content(
            metsalto_sections=metsalto_sections,
            digitized_texts=digitized_texts
        )
        conclusions = self.get_conclusions(
            digitized_texts=digitized_texts
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
