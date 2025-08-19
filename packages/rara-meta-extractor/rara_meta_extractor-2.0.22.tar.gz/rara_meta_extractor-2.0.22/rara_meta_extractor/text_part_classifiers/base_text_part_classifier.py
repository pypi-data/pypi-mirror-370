import json
from typing import List, Tuple
from pprint import pprint
from rara_meta_extractor.constants.data_classes import TextPartLabel
from rara_meta_extractor.config import LOGGER
from rara_meta_extractor.tools.meta_formatter import TextPart

class BaseTextPartClassifier:
    def __init__(self):
        self.search_types_keywords: dict = {
            TextPartLabel.TABLE_OF_CONTENTS: [
                "sisukord", "table of contents", "contents"
            ],
            TextPartLabel.CONCLUSION: [
                "kokkuvõte", "sisukokkuvõte", "conclusion"
            ],
            TextPartLabel.ABSTRACT: [
                "abstract", "abstracts", "annotatsioon"
            ]
        }

    def _make_concl_upper_keywords(self):
        """ Generating conclusion keywords with upper/title-case values
        for determining conclusions from inside section text.
        """
        upper_kw = [
            kw.upper()
            for kw in self._search_types_keywords[TextPartLabel.CONCLUSION]
        ]
        upper_kw.extend(
            [
                kw.title()
                for kw in self._search_types_keywords[TextPartLabel.CONCLUSION]
            ]
        )
        self.conclusion_upper_keywords = upper_kw


    def _remove_double_toc(self, toc_text: str) -> str:
        """ Helper functions to get rid of double tables of
        content/postprocess conclusions
        """
        ttl = toc_text.lower()
        for kw in self.search_types_keywords[TextPartLabel.TABLE_OF_CONTENTS]:
            if kw in ttl:
                if ttl.count(kw)>1:
                    double_kw = "\n"+kw
                    toc_text = toc_text[0:len(ttl.split(double_kw)[0])]
                    return toc_text
        return toc_text

    def _is_consecutive(self, list_of_ints: List[int]) -> bool:
        """ Check if conclusions are consecutive for joining.
        """
        sorted_list = sorted(list_of_ints)
        for i in range(1, len(sorted_list)):
            if sorted_list[i] != sorted_list[i-1] + 1:
                return False
        return True

    def _join_conclusions(self, consecutive_conclusions: List[dict]) -> List[dict]:
        """ Join consecutive conclusions.
        """
        language = consecutive_conclusions[0]["task_language"]
        consecutive_conclusions.sort(key=lambda d: d["sequence_nr"])
        concl_text = " \n".join(
            [
                item["text_value"]
                for item in consecutive_conclusions
            ]
        )
        concl = [
            {
                "text_value": concl_text,
                "task_language": language
            }
        ]
        return concl

    def _postprocess_concl(self, concl: list) -> List[dict]:
        """ Postprocess conclusions: join any consecutive conclusions,
        otherwise remove unnecessary info.
        """
        if len(concl) > 0:
            if len(concl) > 1:
                if len(set([item["task_language"] for item in concl]))==1:
                    concl_nums = [int(item["sequence_nr"]) for item in concl]
                    if self._is_consecutive(concl_nums):
                        concl = self._join_conclusions(concl)
            else:
                concl = [
                    {
                        "text_value": item["text_value"],
                        "task_language": item["task_language"]
                    }
                    for item in concl
                ]
        return concl


    def _look_through_section_titles(self,
            digitized_texts: List[dict], search_type: str
    ) -> List[dict]:
        """ Looking through section titles to get the included text.
        """
        LOGGER.debug(f"Going through section titles with search_type='{search_type}'.")
        found_items = []

        has_title = [
            txt for txt in digitized_texts
            if "section_title" in txt
        ]

        has_title_not_none = [
            txt for txt in has_title
            if txt["section_title"] != None
        ]

        for section in has_title_not_none:
            if section["sequence_nr"] not in self.used_sections:
                if len(section["text"])>20:
                    section_title = section["section_title"].lower().strip().strip(".,")
                    if section_title in self.search_types_keywords[search_type]:
                        if search_type == TextPartLabel.TABLE_OF_CONTENTS:
                            found_items.append(
                                self._remove_double_toc(section["text"])
                            )
                            self.used_sections.append(section["sequence_nr"])
                        elif search_type == TextPartLabel.CONCLUSION:
                            found_items.append(
                                {
                                    "sequence_nr": section["sequence_nr"],
                                    "text_value":section["text"],
                                    "task_language":section["language"]
                                }
                            )
                            self.used_sections.append(section["sequence_nr"])
                        else:
                            found_items.append(
                                {
                                    "text_value": section["text"],
                                    "task_language":section["language"]
                                }
                            )
                            self.used_sections.append(section["sequence_nr"])
        if search_type == TextPartLabel.CONCLUSION:
            found_items = self._postprocess_concl(found_items)
        return found_items

    def _look_through_texts(self,
            digitized_texts: List[dict], search_type: str
    ) -> List[dict]:
        """ Additionally looking through the start of texts
        (might have false positives).
        """
        LOGGER.debug(f"Going through digitized_texts with search_type='{search_type}'.")
        found_items = []
        for section in digitized_texts:
            # We don't look though found sections again
            if section["sequence_nr"] not in self.used_sections:
                if len(section["text"])>20:
                    # We check to see if keywords are in the first
                    # 20 characters of the text
                    text_start = section["text"][0:20]
                    if search_type == TextPartLabel.CONCLUSION:
                        st_matches = [
                            kw for kw in self.conclusion_upper_keywords
                            if kw in text_start
                        ]
                        if st_matches != []:
                            found_items.append(
                                {
                                    "sequence_nr": section["sequence_nr"],
                                    "text_value": section["text"],
                                    "task_language": section["language"]
                                }
                            )
                            self.used_sections.append(section["sequence_nr"])
                    else:
                        st_matches = [
                            kw for kw in self.search_types_keywords[search_type]
                            if kw in text_start
                        ]
                        if st_matches:
                            if search_type == TextPartLabel.TABLE_OF_CONTENTS:
                                found_items.append(
                                    self._remove_double_toc(section["text"])
                                )
                                self.used_sections.append(section["sequence_nr"])
                            else:
                                found_items.append(
                                    {
                                        "text_value": section["text"],
                                        "task_language":section["language"]
                                    }
                                )
                                self.used_sections.append(section["sequence_nr"])
        if search_type == TextPartLabel.CONCLUSION:
            found_items = self._postprocess_concl(found_items)
        return found_items

    def _results_correct_fields(self, results: dict) -> dict:
        LOGGER.debug(f"Updating field names and format.")
        #final_results = {}
        text_parts = []


        try:
            _text_parts = {
                TextPartLabel.TABLE_OF_CONTENTS: ["\n".join(results["table_of_contents"])],
                TextPartLabel.CONCLUSION: results["conclusions"],
                TextPartLabel.ABSTRACT: results["abstracts"]
            }
        except:
            _text_parts = {
                TextPartLabel.TABLE_OF_CONTENTS: [
                    "\n".join([
                        v.get("title", [])[0].get("title")
                        for v in results["table_of_contents"]
                        if v.get("title", [])
                    ])
                ],
                TextPartLabel.CONCLUSION: results["conclusions"],
                TextPartLabel.ABSTRACT: results["abstracts"]
            }
        #print(_text_parts)
        for label, values in _text_parts.items():

            for value in values:
                if isinstance(value, dict):
                    value =  value.get("text_value", value)
                if value:
                    new_text_part = TextPart(
                        text_type=label,
                        text_value=value
                    ).to_dict()
                    text_parts.append(new_text_part)

        return text_parts
