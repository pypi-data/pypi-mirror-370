from rara_meta_extractor.llama_extractor import LlamaExtractor
from rara_meta_extractor.config import (
    META_EXTRACTOR_CONFIG, TEXT_CLASSIFIER_CONFIG, METADATA_TEXT_BLOCKS
)
from rara_meta_extractor.constants.data_classes import MetaField

class TextClassifierAgent(LlamaExtractor):
    """ Llama agent for classifying texts.
    """
    def __init__(self, config: dict = TEXT_CLASSIFIER_CONFIG):
        default_config: dict = TEXT_CLASSIFIER_CONFIG
        default_config.update(config)
        super().__init__(**default_config)

    def has_meta(self, text: str, timeout: int = 90) -> bool:
        """ Outputs a boolean value indicating, if the
        given text contains metadata or not.
        """
        text_info = self.extract(text, timeout=timeout)
        try:
            text_classes = text_info.get(MetaField.TEXT_TYPE, "")
            if text_classes[0] in METADATA_TEXT_BLOCKS:
                meta = True
            else:
                meta = False
        except:
            meta = False
        return meta


class MetaExtractorAgent(LlamaExtractor):
    """ Llama agent for extracting metadata.
    """
    def __init__(self, config: dict = META_EXTRACTOR_CONFIG):
        default_config: dict = META_EXTRACTOR_CONFIG
        default_config.update(config)
        super().__init__(**default_config)
