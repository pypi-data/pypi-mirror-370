import regex as re
from typing import List
from copy import deepcopy
from rara_meta_extractor.config import LOGGER
from rara_meta_extractor.constants.data_classes import TextPartLabel
from rara_meta_extractor.constants.patterns import (
    TABLE_OF_CONTENTS_PATTERNS, ABSTRACT_PATTERNS,
    CONCLUSION_PATTERNS, ORDINAL_PATTERNS
)



class RegexTextPartClassifier:
    def __init__(self):
        # Table of contents item variants
        self.regex_pattern_toc_items1: str = r"\b[\p{Ll}\p{Lu}]+\s+(\. ?){4,}\s+[0-9]+"
        self.regex_pattern_toc_items2: str = r"\b[\p{Ll}\p{Lu}]+\s+[0-9]+"
        self.regex_pattern_toc_items3: str = r"\b[\p{Ll}\p{Lu}0-9]+\n([0-9]+\n){3,}"

        self.ordinal_pattern: str = rf"|".join(ORDINAL_PATTERNS)

        self.__toc_variants: str | re.Pattern = ""
        self.__abstract_variants: str | re.Pattern = ""
        self.__conclusion_variants: str | re.Pattern = ""
        self.counter = 1

    @property
    def toc_variants(self) -> re.Pattern:
        """ Constructs and compiles pattern for
        detecting tables of content.

        Returns
        ---------
        re.Pattern
            Compiled pattern for detecting tables of content.
        """
        if not self.__toc_variants:
            _toc_variants = self._create_variants(
                list_of_items=TABLE_OF_CONTENTS_PATTERNS,
                items_type=TextPartLabel.TABLE_OF_CONTENTS
            )
            #LOGGER.debug(f"Created table of content variants: {_toc_variants}")
            self.__toc_variants = re.compile(_toc_variants)
        return self.__toc_variants

    @property
    def abstract_variants(self) -> re.Pattern:
        """ Constructs and compiles pattern for
        detecting abstracts.

        Returns
        ---------
        re.Pattern
            Compiled pattern for detecting abstracts.
        """
        if not self.__abstract_variants:
            _abstract_variants = self._create_variants(
                list_of_items=ABSTRACT_PATTERNS,
                items_type=TextPartLabel.ABSTRACT
            )
            #LOGGER.debug(f"Created abstract variants: {_abstract_variants}")
            self.__abstract_variants = re.compile(_abstract_variants)
        return self.__abstract_variants

    @property
    def conclusion_variants(self) -> re.Pattern:
        """ Constructs and compiles pattern for
        detecting conclusions.

        Returns
        ---------
        re.Pattern
            Compiled pattern for detecting conclusions.
        """
        if not self.__conclusion_variants:
            _conclusion_variants = self._create_variants(
                list_of_items=CONCLUSION_PATTERNS,
                items_type=TextPartLabel.CONCLUSION
            )
            #LOGGER.debug(f"Created conclusion variants: {_conclusion_variants}")
            self.__conclusion_variants = re.compile(_conclusion_variants)
        return self.__conclusion_variants

    def _make_uppercase_variant(self, item: str) -> str:
        """ Makes uppercase variant of an item.

        Parameters
        -----------
        item: str
            Item to uppercase.

        Returns
        ----------
        str:
            An uppercased item.
        """
        return item.upper()


    def _add_boundaries_front(self, item: str) -> str:
        """ Adds word boundary to the front.

        Parameters
        -----------
        item: str
            Item to add boundary to.

        Returns
        ----------
        str:
            Item with a front boundary.
        """
        return r"\b"+item


    def _add_boundaries_front_newline(self, item: str) -> str:
        """ Adds word boundary to the front with
        newline (in the case of only conclusions).

        Parameters
        -----------
        item: str
            Item to add boundary to.

        Returns
        ----------
        str:
            Item with a front newline boundary.
        """
        new_item = rf"((?<=\n)|(?<=^))(( ?[0-9]+\.? ?)+)?(( ?[VIX]+\.? ?)+)?([\t\r ]+)?{item}"
        return new_item


    def _add_boundaries_back(self, item: str) -> str:
        """ Adds word boundary to the front.

        Parameters
        -----------
        item: str
            Item to add boundary to.

        Returns
        ----------
        str:
            Item with an end boundary.
        """
        return item+r"\b"


    def _attach_variants(self, list_of_items: List[str]) -> str:
        """ Attaches variants for regular expression pattern.

        Parameters
        -----------
        list_of_items: List[str]
            Items to concatinate.

        Returns
        ----------
        str:
            Concatinated items.
        """
        return "|".join(list_of_items)


    def _create_variants(self, list_of_items: List[str], items_type: str) -> str:
        """ Creates different variants depending on the item types.
        Items' type is either conclusion or other.

        Parameters
        -----------
        list_of_items: List[str]
            List of patterns / strings.
        items_type: str
            TextPartLabel class param value.
        """
        LOGGER.debug(f"N-th time calling function _create_variants: {self.counter}")
        LOGGER.debug(f"Generating variations for items with type '{items_type}'.")
        uppercase_variants = [
            self._make_uppercase_variant(item)
            for item in list_of_items
        ]

        list_of_items.extend(uppercase_variants)
        LOGGER.debug(f"Current number of variants to enrich for type '{items_type}': {len(list_of_items)}")

        if items_type != TextPartLabel.CONCLUSION:
            LOGGER.debug(f"Adding boundries front for items with type '{items_type}'.")
            boundaries_front = [
                self._add_boundaries_front(item)
                for item in list_of_items
             ]
            LOGGER.debug(f"Adding boundries back for items with type '{items_type}'.")
            boundaries_back = [
                self._add_boundaries_back(item)
                for item in list_of_items
            ]
            with_boundaries = boundaries_front + boundaries_back
            LOGGER.debug(f"Attaching variants for items with type '{items_type}'.")
            variants =  self._attach_variants(with_boundaries)
        else:
            LOGGER.debug(f"Adding front boundries with newline for items with type '{items_type}'.")
            with_boundaries =  [
                self._add_boundaries_front_newline(item)
                for item in list_of_items
            ]
            LOGGER.debug(f"Attaching variants for items with type '{items_type}'.")
            LOGGER.debug(f"Length of 'with_boundaries': {len(with_boundaries)}; length of 'list_of_items': {len(list_of_items)}")
            variants =  self._attach_variants(with_boundaries)
        self.counter+=1
        return variants


    def is_table_of_contents(self, text: str) -> bool:
        """ Determine, if text contains table of contents.

        Parameters
        -----------
        text: str
            Input text.

        Returns
        -----------
        bool
            Boolean value indicating, if text contains table of contents.
        """
        if re.search(self.regex_pattern_toc_items1, text):
                return True
        else:
            if re.search(self.toc_variants, text):
                if re.search(self.regex_pattern_toc_items2, text):
                    return True
                elif re.search(self.regex_pattern_toc_items3, text):
                    return True
                return True
            elif re.search(self.regex_pattern_toc_items2, text):
                if re.search(self.toc_variants, text.upper()):
                    return True
            elif re.search(self.regex_pattern_toc_items3, text):
                if re.search(self.toc_variants, text.upper()):
                   return True
        return False

    def is_abstract(self, text: str) -> bool:
        """ Determine, if text contains an abstract.

        Parameters
        -----------
        text: str
            Input text.

        Returns
        -----------
        bool
            Boolean value indicating, if text contains an abstarct.
        """
        if re.search(self.abstract_variants, text):
            return True
        return False

    def is_conclusion(self, text: str) -> bool:
        """ Determine, if text contains a conclusion.

        Parameters
        -----------
        text: str
            Input text.

        Returns
        -----------
        bool
            Boolean value indicating, if text contains a conclusion.
        """
        # first we check if any conclusion variants in the text,
        # since the pattern is very long and complex
        simple_pattern = re.compile(self._attach_variants(CONCLUSION_PATTERNS))
        #concl_titles = re.compile(self.conclusin_variants)
        if re.search(simple_pattern, text):
            if re.search(self.conclusion_variants, text):
                get_specific_part = [
                    line
                    for line in text.split("\n")
                    if re.search(self.conclusion_variants, line)
                ]
                for matched_line in get_specific_part:
                    # Trying to avoid chapter conclusions
                    if not re.search(self.ordinal_pattern, matched_line.lower()):
                        # Checking if there's any text after the conclusion title
                        if matched_line != text.split("\n")[-1]:
                            next_line = text.split("\n")[text.split("\n").index(matched_line)+1]
                            if len(next_line.strip())==0:
                                line_after = text.split("\n")[text.split("\n").index(matched_line)+2]
                                if len(line_after) > 35:
                                    return True
                            elif len(next_line) > 35:
                                return True
                        else:
                            return True
        return False

    def get_label(self, text: str) -> str:
        """
        Determines text part in order of exclusion,
        single doc can't have multiple text parts

        Parameters
        -----------
        text: str
            Input text.

        Returns
        -----------
        str:
            Text part label.
        """
        LOGGER.info(f"Detecting text part for text {text[:20]}...")
        if self.is_table_of_contents(text):
            label = TextPartLabel.TABLE_OF_CONTENTS
        elif self.is_abstract(text):
            label = TextPartLabel.ABSTRACT
        elif self.is_conclusion(text):
            label = TextPartLabel.CONCLUSION
        else:
            label = TextPartLabel.OTHER
        self.counter = 1
        return label
