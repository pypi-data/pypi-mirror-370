from typing import List, Any
from pprint import pprint
from rara_meta_extractor.config import LOGGER, DEFAULT_INSTRUCTIONS
from rara_meta_extractor.llama_api_wrapper import LlamaAPIConnector
from rara_meta_extractor.tools.llama_schema_generator import JSONSchemaGenerator



class LlamaExtractor:
    def __init__(
        self,
        llama_host_url: str,
        instructions: str = DEFAULT_INSTRUCTIONS,
        temperature: float = 0.7,
        n_predict: int = 500,
        json_schema: dict = {},
        fields: List[str] | List[dict] = [],
        **kwargs
    ):
        self.llama_host_url: str = llama_host_url
        self.fields_schema: List[str] | List[dict] = fields

        self.llama_connector: LlamaAPIConnector = LlamaAPIConnector(
            host_url=llama_host_url,
            temperature=temperature,
            n_predict=n_predict,
            **kwargs
        )

        self.schema_generator: JSONSchemaGenerator = JSONSchemaGenerator()
        self.__fields: List[str]  = []
        self.__fields_str: str = ""
        self.__instructions: str = instructions.format(self.fields_str)
        self.__json_schema: dict = json_schema


    @property
    def fields(self) -> List[str]:
        if not self.__fields:
            if self.fields_schema and isinstance(self.fields_schema[0], dict):
                self.__fields = [
                    field.get("name")
                    for field in self.fields_schema
                ]
            else:
                self.__fields = self.fields_schema
        return self.__fields

    @property
    def fields_str(self) -> str:
        if not self.__fields_str:
            self.__fields_str = ", ".join(self.fields)
        return self.__fields_str

    @property
    def instructions(self) -> str:
        return self.__instructions

    @property
    def json_schema(self) -> str:
        if not self.__json_schema:
            if self.fields_schema:
                self.__json_schema = self.schema_generator.generate_json_schema(
                    fields=self.fields_schema
                )
        return self.__json_schema

    def extract(self, text: str, instructions: str = "",
            output_full_response: bool = False, default_response: Any = {},
            timeout: int = 90
    ) -> dict:
        """ Extracts information from the input text.

        Parameters
        -----------
        text: str
            Text from where to extract information.
        instructions: str
            Instructions for the LLM.
        output_full_response: bool
            If enabled, the whole API response is added to the output;
            otherwise only "content" (the "answer").
        default_response: Any
            Default output in case Llama generates an invalid JSON string
            which cannot be loaded.

        Returns
        -----------
        Any:
            LLM API resonse (or content). Usually a JSON dict.
        """
        if not instructions:
            instructions = self.instructions

        extracted_data = self.llama_connector.query(
            instructions=instructions,
            context=text,
            json_schema=self.json_schema,
            output_full_response=output_full_response,
            default_response=default_response,
            timeout=timeout
        )
        return extracted_data
