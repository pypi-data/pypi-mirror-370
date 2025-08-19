import requests
import json
from typing import List, Union

#https://github.com/ggml-org/llama.cpp/tree/master/grammars
class JSONSchemaGenerator:
    def __init__(self):
        self.keywords_key = "keywords"

    def generate_keyword_schema(
        self, keywords: List[str] = [],
        min_keywords: int | None = None,
        max_keywords: int | None = None
    ) -> dict:
        """ Generates JSON schema for keyword extraction.
        """
        json_schema = {
          "type": "object",
          "properties": {
            "topics": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          },
          "required": [self.keywords_key]
        }
        if min_keywords:
            json_schema["properties"]["topics"]["minItems"] = min_keywords
        if max_keywords:
            json_schema["properties"]["topics"]["maxItems"] = max_keywords
        if keywords:
            json_schema["properties"][self.keywords_key]["items"]["enum"] = keywords
        return json_schema

    def generate_json_schema(self, **kwargs) -> dict:
        """Generates JSON schema for the given fields.
        """
        if isinstance(kwargs.get("fields")[0], str):
            json_schema = self._generate_json_schema_simple(**kwargs)
        else:
            json_schema = self._generate_json_schema_restricted(**kwargs)
        return json_schema

    def _generate_json_schema_simple(self,
            fields: List[str],
            default_type: str = "string",
            max_length: int = 100,
            min_length: int = 2,
            min_items: int = 0,
            max_items: int = 100,
            required_fields: List[str] = [],
            require_all: bool = False
        ) -> dict:
        """Generates JSON schema for the given fields.
        NB! Currently assumes that the output corresponding to
        each field is a list of `default_type` (string).
        """
        json_schema = {
            "type": "object",
            "properties": {
            field: {
                "type": "array",
                "items": {
                    "type": default_type,
                    "maxLength": max_length,
                    "minLength": min_length
                },
                "minItems": min_items,
                "maxItems": max_items
            }
            for field in fields
          },
        }
        if required_fields:
            json_schema["required"] = required_fields
        elif require_all:
            json_schema["required"] = fields
        return json_schema

    def _generate_json_schema_restricted(self,
            fields: List[dict],
            default_type: str = "string",
            max_length: int = 100,
            min_items: int = 0,
            max_items: int = 10,
            required_fields: List[str] = [],
            require_all: bool = False
        ) -> dict:
        """Generates JSON schema for the given fields according to restrictions
        passed with key `restrictions`.
        `fields` has to be formatted as follows:
        [{"name": <str:field_name>, "restrictions": <dict: restrictions for field>}, ...]
        """

        json_schema = {
          "type": "object",
          "properties": {
            field.get("name"): {
              "type": "array",
              "items": {
                  **{
                    "type": default_type,
                    "maxLength": max_length
                  },
                  **field.get("item_restrictions", {})
              },
              **field.get("list_restrictions", {})
            }
            for field in fields
          }
        }
        if required_fields:
            json_schema["required"] = required_fields
        elif require_all:
            json_schema["required"] = [field.get("name") for field in fields]
        return json_schema
