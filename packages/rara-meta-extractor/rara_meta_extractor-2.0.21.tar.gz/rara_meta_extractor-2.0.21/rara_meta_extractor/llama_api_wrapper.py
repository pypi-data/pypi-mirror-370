import json
from typing import List, Any

import requests

from rara_meta_extractor.config import LOGGER


class LlamaAPIConnector:
    # TODO: parameetrid kontrollida -https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md
    def __init__(
            self,
            host_url: str,  # e.g. "http://localhost:8080"
            stream: bool = False,
            n_predict: int = 400,
            temperature: float = 0.7,
            stop: List[str] = ["</s>", "Llama:", "User:"],
            repeat_last_n: int = 256,
            repeat_penalty: float = 1.18,
            penalize_nl: bool = False,
            top_k: int = 40,
            top_p: float = 0.95,
            min_p: float = 0.05,
            tfs_z: int = 1,
            typical_p: int = 1,
            presence_penalty: float = 0,  # ?
            frequency_penalty: float = 0,  # ?
            mirostat: float = 0,  # ?
            mirostat_tau: int = 5,
            mirostat_eta: float = 0.1,
            n_probs: float = 0,  # ?
            min_keep: float = 0,  # ?
            cache_prompt: bool = False,
            api_key: str = ""
            ):
        self.host_url = host_url
        self.stream = stream
        self.n_predict = n_predict
        self.temperature = temperature
        self.stop = stop
        self.repeat_last_n = repeat_last_n
        self.repeat_penalty = repeat_penalty
        self.penalize_nl = penalize_nl
        self.top_k = top_k
        self.top_p = top_p
        self.min_p = min_p
        self.tfs_z = tfs_z
        self.typical_p = typical_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.mirostat = mirostat
        self.mirostat_tau = mirostat_tau
        self.mirostat_eta = mirostat_eta
        self.n_probs = n_probs
        self.min_keep = min_keep
        self.cache_prompt = cache_prompt
        self.api_key = api_key

    @property
    def query_params(self) -> dict:
        """Convert the instance's attributes to a dictionary.
        """
        params = self.__dict__.copy()
        params.pop("host_url")
        return params

    def query(
            self, instructions: str, context: str, json_schema: dict = {},
            output_full_response: bool = False, default_response: Any = {},
            timeout: int = 90
            ) -> Any:
        """ Query information from a Llama model via an API call.

        Parameters
        -----------
        instructions: str
            Instructions for the model (system prompt).
        context: str
            User query (text).
        json_schema: dict
            Specifies output format / fieldsself.
        output_full_response: bool
            If enabled, the whole API response is added to the output;
            otherwise only "content" (the "answer").
        default_response: Any
            Default output in case Llama generates an invalid JSON string
            which cannot be loaded.

        Returns
        -----------
        Any:
            The answer to user's query (can be any type, especially when
            using a fine-tuned model or specific JSON schema) or the
            whole API response (dict).
        """
        prompt = f"{instructions}\n\nUser: {context}\nLlama:"
        payload = self.query_params
        payload["prompt"] = prompt
        if json_schema:
            payload["json_schema"] = json_schema

        url = f"{self.host_url}/completion"

        response = requests.post(url, json=payload, timeout=timeout)
        extracted_data = {}
        if response.status_code == 200:
            json_response = response.json()
            try:
                content = json_response.pop("content")
                content_json = json.loads(content)
            except Exception as e:
                LOGGER.debug(f"Loading JSON from response failed with error: {e}. Response.text: '{response.text}'")
                content_json = default_response
            if output_full_response:
                json_response["content"] = content_json
                output = json_response
            else:
                output = content_json
        else:
            LOGGER.error(f"Status: {response.status_code}")
            LOGGER.error(response.text)
        return output
