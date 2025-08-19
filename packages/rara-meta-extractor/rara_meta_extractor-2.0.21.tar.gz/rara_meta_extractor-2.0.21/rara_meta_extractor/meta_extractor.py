import regex as re
from typing import List, Dict
from collections import defaultdict
from copy import deepcopy
from rara_meta_extractor.config import (
    META_EXTRACTOR_CONFIG, TEXT_CLASSIFIER_CONFIG, METADATA_TEXT_BLOCKS, LOGGER,
    AUTHOR_FIELDS, META_FIELDS, TextBlock
)
from rara_meta_extractor.constants.data_classes import (
    ExtractorType, MetaField, TextBlock, AuthorField, TextPartLabel, HostEntryField,
    IssueType, DEFAULT_ISSUE_TYPE, SeriesField, EPUB_FIELDS_TO_PREFER
)
from rara_meta_extractor.regex_extractors import ISBNRegexExtractor
from rara_meta_extractor.tools.meta_formatter import Meta, TextPart, TableOfContents
from rara_meta_extractor.tools.utils import detect_language
from rara_meta_extractor.llm_agents import TextClassifierAgent, MetaExtractorAgent
from rara_meta_extractor.epub_meta_extractor import EPUBMetaExtractor
from rara_meta_extractor.mets_alto_meta_extractor import MetsAltoMetaExtractor
from rara_meta_extractor.text_part_classifiers.regex_text_part_classifier import RegexTextPartClassifier
from rara_meta_extractor.text_part_classifiers.epub_text_part_classifier import EPUBTextPartClassifier
from rara_meta_extractor.text_part_classifiers.mets_alto_text_part_classifier import MetsAltoTextPartClassifier

#import logging
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)


class MetaExtractor:
    def __init__(self,
        meta_extractor_config: dict = META_EXTRACTOR_CONFIG,
        text_classifier_config: dict = TEXT_CLASSIFIER_CONFIG
    ):
        self.meta_extractor_config = meta_extractor_config
        self.text_classifier_config = text_classifier_config

        self.meta_agent = MetaExtractorAgent(self.meta_extractor_config)
        self.text_classifier_agent = TextClassifierAgent(self.text_classifier_config)

        self.text_part_classifier = RegexTextPartClassifier()
        self.epub_text_part_classifier = EPUBTextPartClassifier()
        self.mets_alto_text_part_classifier = MetsAltoTextPartClassifier()

        self.epub_meta_extractor = EPUBMetaExtractor()
        self.mets_alto_meta_extractor = MetsAltoMetaExtractor()

        self.isbn_regex_extractor = ISBNRegexExtractor()



    def classify_text(self, text: str, default: str = TextBlock.METADATA) -> str:
        """ Classifies text into one of the text blocks defined in TextBlock.

        Parameters
        -----------
        text: str
            Text to classify
        default: str
            Default value to return in case of an exception.

        Returns
        -----------
        str:
            Text class.
        """
        try:
            text_type_dict = self.text_classifier_agent.extract(text=text)
            LOGGER.debug(f"Llama text classifier output: {text_type_dict}")
            text_class = text_type_dict.get("text_type")[0]
        except Exception as e:
            LOGGER.exception(
                f"Detecting text type for text '{text[:50]}' failed with error: {e}. "
                f"Defaulting to '{default}'"
            )
            text_class = default
        return text_class


    def _construct_llama_input(self, texts: List[str], use_llm: bool = False,
            max_length_per_text: int = 1500, n_first_pages: int = 5,
            n_last_pages: int = 0, n_strict_include: int = 3
    ) -> List[str]:
        """ Construct input for Llama.

        Parameters
        -----------
        texts: List[str]
            Raw texts
        use_llm: bool
            If enabled, LLM is used for each n_first_page and n_last_page text
            to detect, if they contain metadata or not. Only texts containing
            metadata will be passed to Llama for metadata extraction.
        max_length_per_text: int
            Used only if `use_llm=False` and is not applied to `n_strict_include`
            first texts. For other texts, this param will be used to decide, if
            the text will be added to Llama input or not (texts longer than the
            threshold set with this param will be ignored).
        n_first_pages: int
            How many first pages to consider as potential inputs?
        n_last_pages: int
            How many last pages to consider as potential inputs?
        n_strict_include: int
            How many first pages to always include?

        Returns
        -----------
        List[str]:
            List of verified texts
        """
        LOGGER.debug("Constructing Llama input!")
        n_pages  = len(texts)

        # If number of pages is smaller than number of
        # first and last pages combined, modify the
        # number of last pages in order to avoid
        # duplicates in final Llama input
        if n_pages < n_first_pages + n_last_pages:
            n_last_pages = max(n_pages - n_first_pages, 0)

        first_pages = texts[:n_first_pages]
        last_pages = texts[-n_last_pages:] if n_last_pages > 0 else []
        if n_strict_include > n_first_pages:
            n_strict_include = n_first_pages
        texts_to_analyze = first_pages + last_pages

        if use_llm:
            verified_texts = []
            for text in texts_to_analyze:
                text_type = self.classify_text(text)
                if text_type in METADATA_TEXT_BLOCKS:
                    verified_texts.append(text)
            if not verified_texts:
                LOGGER.error(
                    f"No verified metadata text block found from texts {texts} with LLM!"
                )
        else:
            verified_texts = texts_to_analyze[:n_strict_include]

            for text in texts_to_analyze[n_strict_include:]:
                if (len(text) < max_length_per_text and not
                    re.search("sisukord|table of contents", text, re.IGNORECASE)
                ):
                    verified_texts.append(text)
        return verified_texts

    def _get_text_parts(self, texts: List[dict]) -> List[dict]:
        """ Wrapper function for detecting text partsself.

        Parameters
        -----------
        texts: List[dict]
            Raw texts.

        Returns
        -----------
        List[dict]:
            List of dicts where each dict contains
            one text part label, corresponding text block and
            language of the text block. NB! multiple texts might be concatted
            into one, if conclusion spans over multiple pages etc.

        """
        text_parts = []
        _text_parts = defaultdict(lambda: defaultdict(list))

        for i, text in enumerate(texts):
            LOGGER.debug(f"Classifying text number {i+1}...")
            raw_text = text.get("text", "")
            lang = text.get("language", "")
            label = self.text_part_classifier.get_label(raw_text)
            if label != TextPartLabel.OTHER:
                _text_parts[label]["texts"].append(raw_text)
                _text_parts[label]["langs"].append(lang)

        for label, values in _text_parts.items():
            texts = values.get("texts")
            langs = values.get("langs")
            lang_counts = defaultdict(int)
            for lang in langs:
                lang_counts[lang]+=1
            most_frequent_lang = sorted(
                list(lang_counts.items()),
                key=lambda x: x[1],
                reverse=True
            )[0][0]
            text_part = "\n".join(texts)
            if not most_frequent_lang:
                most_frequent_lang = detect_language(text_part)
            new_text_part = TextPart(
                text_type=label,
                text_value=text_part,
                language=most_frequent_lang
            ).to_dict()

            text_parts.append(new_text_part)
        return text_parts

    def _get_host_entry(self, meta: dict) -> dict:
        LOGGER.debug(f"Constructing host_entry.")
        # Meta field has a lot of fields with whitespaces, we need
        # them with underscore : S
        pub_date_field = "_".join(MetaField.PUBLICATION_DATE.split())
        issue_type = meta.get(MetaField.ISSUE_TYPE, "")
        publication_date = meta.get(pub_date_field, "")
        host_entry = {
            HostEntryField.PUBLICATION_DATE: publication_date,
            HostEntryField.NAME: "",
            HostEntryField.PART_NUMBER: ""
        }
        if issue_type in [IssueType.JOURNAL, IssueType.PERIODICAL, IssueType.NEWSPAPER]:
            titles = meta.get("titles", [])
            if titles:
                series_name = titles[0]["title"]
                part_number = titles[0]["part_number"]
                host_entry[HostEntryField.NAME] = series_name
                host_entry[HostEntryField.PART_NUMBER] = part_number
        if not host_entry.get(HostEntryField.NAME, ""):
            series_name = meta.get(MetaField.SERIES_NAME, "")
            if series_name:
                host_entry[HostEntryField.NAME] = series_name
        if not host_entry.get(HostEntryField.PART_NUMBER, ""):
            series_volume = meta.get(MetaField.SERIES_VOLUME, "")
            if series_volume:
                host_entry[HostEntryField.PART_NUMBER] = series_volume
        # if only publication date is filled, remove it from the host entry
        if not host_entry.get(HostEntryField.NAME, None) and not host_entry.get(HostEntryField.PART_NUMBER, None):
            host_entry[HostEntryField.PUBLICATION_DATE] = ""
        
        return host_entry


    def _get_series_info(self, meta: dict) ->  dict:
        LOGGER.debug(f"Constructing series info.")
        series_info = {
            SeriesField.ISSN: meta.get(MetaField.SERIES_ISSN, ""),
            SeriesField.STATEMENT: meta.get(MetaField.SERIES_NAME, ""),
            SeriesField.VOLUME: meta.get(MetaField.SERIES_VOLUME, "")
        }
        return series_info

    def extract_from_digitizer_output(self, digitizer_output: dict, **kwargs) -> dict:
        """ Extracts metadata from Digitizer output.
        """
        LOGGER.info("Extracting metadata from Digitizer output.")

        texts = digitizer_output.get("texts", [])
        doc_meta = digitizer_output.get("doc_meta", {})

        mets_alto_metadata = doc_meta.get("mets_alto_metadata", [])
        epub_metadata = doc_meta.get("epub_metadata", {})
        languages = doc_meta.get("languages", [])
        language = ""
        if languages:
            language = languages[0].get("language", "")


        result = self.extract(
            texts=texts,
            epub_metadata=epub_metadata,
            mets_alto_metadata=mets_alto_metadata,
            language=language,
            **kwargs
        )
        return result

    def extract_simple(self, text: str, lang: str,
            simple: bool = True, **kwargs
    ) -> dict:
        """ For simple usage. Passes plaintext to Llama extractor.
        """
        texts = [{"text": text, "lang": lang}]
        result = self.extract(texts=texts, simple=simple, **kwargs)
        return result

    def extract(self,
            texts: List[dict],
            epub_metadata: dict = {},
            mets_alto_metadata: List[str] = [],
            verify_texts_with_llm: bool = False,
            n_trials: int = 1,
            merge_texts: bool = True,
            min_ratio: float = 0.8,
            add_missing_keys: bool = False,
            detect_text_parts: bool = True,
            max_length_per_text: int = 1500,
            n_first_pages: int = 5,
            n_last_pages: int = 0,
            n_strict_include: int = 3,
            simple: bool = False,
            llama_api_timeout: int = 90,
            language: str = ""
    ) -> dict:
        """ Extracts relevant metadata from a batch of texts

        Parameters
        -----------
        texts: List[dict]
            List of texts from where to extract meta information. For EPUB and METS/ALTO,
            expects content of `texts` from digitizer output. Otherwise, must minimally
            contain keys `text` and `lang`.
        epub_metadata: dict
            Expects the content of `doc_meta.epub_metadata` from digitizer output.
        mets_alto_meta: List[str]
            Expects the content of `doc_meta.mets_alto_metadata` from digitizer output.
        verify_texts_with_llm: bool
            If enabled, each text is passed to text classifier agent first
            and only texts classified as metadata blocks are passed to
            meta extractor(s).
        n_trials: int
            Indicates how many trials to run for predicting metadata with LlamaExtractor
            for the same text. NB! Setting it higher than 1 has purpose only if temperature
            > 0.
        merge_texts: bool
            If enabled, texts are merged into a single text block before passing
            it to LlamaExtractor. Otherwise texts are passed one by one to LlamaExtractor
            and results are merged afterwards.
        min_ratio: float
            Relevant only if n_trials > 1. Indicates the ratio of times a meta value
            has to be predicted during trials. E.g. if min_ratio = 0.7 and a value is predicted
            2 out of 3 trials, it will not be returned as 2/3 = 0.66 < 0.7.
        add_missing_keys: bool
            If enabled, all possible meta keys are added to the output, even if
            the content has not been extracted.
        detect_text_parts: bool
            If enabled, runs text part detection for detecting conclusions, abstracts etc.
        max_length_per_text: int
            If verify_texts_with_llm is set to False, this param is used for dummy metadata detection -
            if a text is longer than the threshold set with this param, it will not be included
            into Llama input.
        n_first_pages: int
            How many first pages to consider for possible Llama input? NB! Not all of them are
            actually added to the input as the pages are passed through prefiltering.
        n_last_pages: int
            How many last pages to consider for possible Llama input? NB! Not all of them are
            actually added to the input as the pages are passed through prefiltering.
        n_strict_include: int
            Number of pages (out of n_first_pages + n_list_pages set) to pass to Llama
            without additional prefiltering.
        simple: bool
            If enabled, the outputs of titles and authors are simplified (some fields
            necessary mostly for constructing final MARC files are removed).
        llama_api_timeout: int
            Llama API query timeout in seconds.

        """
        meta_batches = []
        verified_texts = []
        text_parts = []
        meta = {}
        epub_meta = {}
        raw_meta = {}

        # TODO: param for applying LLM if mets-alto / epub meta is present?
        # or make it dynamic based on what fields are detected?
        success = None
        if epub_metadata:
            extractor_type = [ExtractorType.EPUB]
            LOGGER.info(f"Using {extractor_type} for metadata extraction.")
            meta: dict = self.epub_meta_extractor.extract_meta(
                epub_metadata=epub_metadata, simple=simple, language=language
            )
            LOGGER.debug(f"Meta detected with {extractor_type}: {meta}")
            # Add some condition for switching to Llama extractor?
            success = False


        elif mets_alto_metadata:
            extractor_type = [ExtractorType.METS_ALTO]
            LOGGER.info(f"Using {extractor_type} for metadata extraction.")
            meta: dict = self.mets_alto_meta_extractor.extract_meta(
                mets_alto_metadata=mets_alto_metadata,
                digitized_texts=texts,
                simple=simple
            )
            success = True

        if not success:
            if success == None:
                extractor_type = [ExtractorType.LLAMA]
            else:
                epub_meta = deepcopy(meta)
                extractor_type = [ExtractorType.EPUB, ExtractorType.LLAMA]
            LOGGER.info(f"Using {extractor_type} for metadata extraction.")
            raw_texts = [
                doc.get("text") for doc in texts
                if doc.get("text").strip()
            ]

            verified_texts = self._construct_llama_input(
                texts=raw_texts,
                use_llm=verify_texts_with_llm,
                max_length_per_text=max_length_per_text,
                n_first_pages=n_first_pages,
                n_last_pages=n_last_pages,
                n_strict_include=n_strict_include
            )

            if merge_texts:
                text_str = "\n\n".join(verified_texts)
                if text_str:
                    verified_texts = [text_str]
                else:
                    verified_texts = []

                LOGGER.debug(f"Constructed Llama input of size {len(text_str)} characters.")

            for text in verified_texts:
                for trial_nr in range(n_trials):
                    try:
                        LOGGER.debug(
                            f"Trial nr {trial_nr}. Extracting information with Llama agent " \
                            f"from text '{text[:20]}...'."
                        )
                        meta_batch = self.meta_agent.extract(text=text, timeout=llama_api_timeout)
                        LOGGER.debug(f"Raw LLM output: {meta_batch}")
                        meta_batches.append(meta_batch)
                    except Exception as e:
                        LOGGER.exception(
                            f"Extracting meta information from text: {text[:50]} " \
                            f"failed with error: {e}."
                    )
        # Detect and add text parts
        if detect_text_parts:

            if ExtractorType.EPUB in extractor_type:
                LOGGER.info(f"Detecting text parts with EPUB text part classifier.")
                text_parts = self.epub_text_part_classifier.get_parts_of_text(
                    digitized_texts=texts,
                    epub_meta=meta
                )
                meta[MetaField.TEXT_PARTS] = text_parts

            elif ExtractorType.METS_ALTO in extractor_type:
                LOGGER.info(f"Detecting text parts with METS/ALTO text part classifier.")
                text_parts = self.mets_alto_text_part_classifier.get_parts_of_text(
                    digitized_texts=texts,
                    mets_alto_meta=raw_meta
                )
                meta[MetaField.TEXT_PARTS] = text_parts
            else:
                LOGGER.info(f"Detecting text parts with Regex text part classifier.")
                text_parts = self._get_text_parts(texts)


        if ExtractorType.LLAMA in extractor_type:
            meta = Meta(
                meta_batches=meta_batches,
                text_parts=text_parts,
                min_ratio=min_ratio,
                add_missing_keys=add_missing_keys,
                simple=simple,
                language=language
            ).to_dict()

        # Included texts are expected parts of meta extractor output in
        # text part classifiers, but once text parts are detected (or ignored),
        # they no longer serve purpose in the output
        meta.pop(MetaField.INCLUDED_TEXT, {})

        # Add chapter list, if table of contents is found
        meta[MetaField.TABLE_OF_CONTENTS] = TableOfContents(extracted_meta=meta).table_of_contents

        # Filter out table of contents in text parts
        filtered_text_parts = []
        for text_part in text_parts:
            if text_part["text_type"] == TextPartLabel.TABLE_OF_CONTENTS:
                continue
            else:
                filtered_text_parts.append(text_part)

        if ExtractorType.EPUB in extractor_type:
        # If both Llama and Epub extractors are used,
        # overwrite some LLama fields with the values
        # detected with epub extractor
            for field in EPUB_FIELDS_TO_PREFER:
                LOGGER.debug(
                    f"Overwriting Llama-Extractor values with values detected by EPUB-Extractor (field='{field}')"
                )
                value = epub_meta.get(field, None)
                LOGGER.debug(f"Llama-Extractor value: {meta.get(field, '')}")
                LOGGER.debug(f"EPUB-Extractor value: {value}. NB! If this value == None, the old value is kept!")
                if value:
                   meta[field] = value

        meta[MetaField.TEXT_PARTS] = filtered_text_parts
        meta[MetaField.HOST_ENTRY] = self._get_host_entry(meta)

        series_info = self._get_series_info(meta)

        series_fields = [MetaField.SERIES_ISSN, MetaField.SERIES_NAME, MetaField.SERIES_VOLUME]
        meta[MetaField.SERIES] = series_info
        for field in series_fields:
            meta.pop(field, "")

        if MetaField.ISSUE_TYPE not in meta:
            meta[MetaField.ISSUE_TYPE] = DEFAULT_ISSUE_TYPE

        # Try extracting ISBN with Regex, if not found with other extractors
        if meta[MetaField.ISSUE_TYPE] == IssueType.BOOK and (MetaField.ISBN not in meta or not meta[MetaField.ISBN]):
            if not verified_texts:
                verified_texts = [text.get("text") for text in texts[:n_first_pages]]

            text = "\n".join(verified_texts)
            isbn = self.isbn_regex_extractor.extract(text)
            meta[MetaField.ISBN] = isbn



        result = {
            "meta": meta,
            "extractor": extractor_type
        }
        return result
