from typing import List, Literal
import requests
import constants.constants as bdb_constants
from utils.utils import Utils

class ChatSettings():
    def __init__(self):
        self.provider: str = bdb_constants.DEFAULT_PROVIDER
        self.model: str = bdb_constants.DEFAULT_OPEN_AI_MODEL
        self.temperature: float = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
        self.system_prompt: str = ""

    def to_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "system_prompt": self.system_prompt
        }

class RetrievalSettings():
    def __init__(self):
        self.k: int = 3
        self.fts: bool = False
        self.number_of_search_docs: int = 0
        self.langchain_api_key: str | None = None
        self.langchain_project_name: str = "BerryDB"
        self.similarity_search_type: str = "dot"

    def to_dict(self):
        return {
            "k": self.k,
            "fts": self.fts,
            "number_of_search_docs": self.number_of_search_docs,
            "langchain_api_key": self.langchain_api_key,
            "langchain_project_name": self.langchain_project_name,
            "similarity_search_type": self.similarity_search_type
        }

class TransformSettings():
    def __init__(self):
        self.filter_expr: List[str] | None = None
        self.filter_action: str = "include"
        self.jsonata_expr: str | None = None

    def to_dict(self):
        return {
            "filter_expr": self.filter_expr,
            "filter_action": self.filter_action,
            "jsonata_expr": self.jsonata_expr
        }

class EmbedSettings():
    def __init__(self):
        self.provider: str = "openai"
        self.model: str = bdb_constants.DEFAULT_OPEN_AI_EMBEDDING_MODEL

    def to_dict(self):
        return {
            "provider": self.provider,
            "model": self.model,
        }

class Settings:
    def __init__(self):
        self.chat_settings: dict = {}
        self.retrieval_settings: dict = {}
        self.transform_settings: dict = {}
        self.embed_settings: dict = {}

        raise RuntimeError("Use Settings.Builder() to create an instance.")

    @classmethod
    def _create(cls, chat_settings: ChatSettings, retrieval_settings: RetrievalSettings,
                transform_settings: TransformSettings, embed_settings: EmbedSettings):
        instance = cls.__new__(cls)
        instance.chat_settings = chat_settings.to_dict()
        instance.retrieval_settings = retrieval_settings.to_dict()
        instance.transform_settings = transform_settings.to_dict()
        instance.embed_settings = embed_settings.to_dict()
        return instance

    def to_builder(self):
        builder = Settings.Builder()

        # Populate chat_settings
        builder.chat_settings(
            provider=self.chat_settings.get("provider"),
            model=self.chat_settings.get("model"),
            temperature=self.chat_settings.get("temperature"),
            system_prompt=self.chat_settings.get("system_prompt")
        )

        # Populate retrieval_settings
        builder.retrieval_settings(
            k=self.retrieval_settings.get("k"),
            fts=self.retrieval_settings.get("fts"),
            number_of_search_docs=self.retrieval_settings.get("number_of_search_docs"),
            tracing_api_key=self.retrieval_settings.get("langchain_api_key"),
            tracing_project_name=self.retrieval_settings.get("langchain_project_name"),
            similarity_search_type=self.retrieval_settings.get("similarity_search_type")
        )

        # Populate transform_settings
        builder.transform_settings(
            filter_expr=self.transform_settings.get("filter_expr"),
            filter_action=self.transform_settings.get("filter_action"),
            jsonata_expr=self.transform_settings.get("jsonata_expr")
        )

        # Populate embed_settings
        builder.embed_settings(
            provider=self.embed_settings.get("provider"),
            model=self.embed_settings.get("model"),
        )

        return builder

    def save(self, berrydb_api_key: str, settings_name: str):
        api_url = bdb_constants.BERRY_GPT_BASE_URL + bdb_constants.save_chat_settings_url
        params = {"apiKey": berrydb_api_key, "name": settings_name}

        data = self.__dict__.copy()  # API accepts snake_case, so no transformation needed

        response = requests.post(api_url, params=params, json=data)
        if response.status_code != 201:
            Utils.handleApiCallFailure(response.json(), response.status_code)
        if bdb_constants.debug_mode:
            print("api_url: ", api_url)
            print("params: ", params)
            print("response: ", response.json())
        return response.json()

    @staticmethod
    def get(berrydb_api_key: str, settings_name: str):
        api_url:str = bdb_constants.BERRY_GPT_BASE_URL + bdb_constants.save_chat_settings_url
        params = {"apiKey": berrydb_api_key, "name": settings_name}

        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            error = {'error': 'Unable to fetch your settings, either it does not exist or you do not have access to it.'}
            Utils.handleApiCallFailure(error, response.status_code)
        json_response = response.json()['settings']

        if bdb_constants.debug_mode:
            print("api_url: ", api_url)
            print("params: ", params)
            print("response: ", json_response)

        def get_config_for_setting(setting_name:str, key:str):
            return json_response.get(setting_name, {}).get(key)

        settings_builder = Settings.Builder()

        if "chat_settings" in json_response:  # Updated to snake_case
            settings_builder.chat_settings(
                provider=get_config_for_setting("chat_settings", "provider"),
                model=get_config_for_setting("chat_settings", "model"),
                temperature=get_config_for_setting("chat_settings", "temperature"),
                system_prompt=get_config_for_setting("chat_settings", "system_prompt"),
            )

        if "retrieval_settings" in json_response:  # Updated to snake_case
            settings_builder.retrieval_settings(
                k=get_config_for_setting("retrieval_settings", "k"),
                fts=get_config_for_setting("retrieval_settings", "fts"),
                number_of_search_docs=get_config_for_setting("retrieval_settings", "number_of_search_docs"),
                tracing_api_key=get_config_for_setting("retrieval_settings", "langchain_api_key"),
                tracing_project_name=get_config_for_setting("retrieval_settings", "langchain_project_name"),
                similarity_search_type=get_config_for_setting("retrieval_settings", "similarity_search_type"),
            )

        if "transform_settings" in json_response:  # Updated to snake_case
            settings_builder.transform_settings(
                filter_expr=get_config_for_setting("transform_settings", "filter_expr"),
                filter_action=get_config_for_setting("transform_settings", "filter_action"),
                jsonata_expr=get_config_for_setting("transform_settings", "jsonata_expr"),
            )

        if "embed_settings" in json_response:  # Updated to snake_case
            settings_builder.embed_settings(
                provider=get_config_for_setting("embed_settings", "provider"),
                model=get_config_for_setting("embed_settings", "model"),
            )

        return settings_builder.build()

    class Builder:
        def __init__(self):
            self._chat_settings = ChatSettings()
            self._retrieval_settings = RetrievalSettings()
            self._transform_settings = TransformSettings()
            self._embed_settings = EmbedSettings()

        def chat_settings(self, provider:Literal['openai'] = "openai", model: str = "gpt-4o-mini", temperature: float = 0.5, system_prompt: str = ""):
            """
            **Parameters:**
            - **provider** (`str`, optional): The chat LLM model provider. Defaults to `'OpenAI'`
            - **model** (`str`, optional): The specific model to use based on the **provider**
            - **temperature** (`float`, optional): Controls the randomness of responses. Between 0 to 2
                -  Lower values (0.0 - 0.3) make responses more deterministic.
                -  Higher values (0.7 - 1.0) increase variability.
            - **system_prompt** (`str`, optional): A custom prompt used to guide the model's behavior and responses
            """
            if provider is None:
                provider = "openai"
            elif not isinstance(provider, str):
                raise ValueError("provider should be a string")
            elif provider not in {"openai", "huggingface"}:
                raise ValueError('Invalid provider, provider should be either "openai" or "huggingface"')

            if model is None:
                model = "gpt-4o-mini"
            elif not isinstance(model, str):
                raise ValueError("model should be a string")
            if temperature is None:
                temperature = 0.5
            elif not isinstance(temperature, (float, int)):
                raise ValueError("temperature should be a float")
            elif not 0.0 <= temperature <= 1.0:
                raise ValueError("temperature should be between 0.0 and 1.0")
            if system_prompt is None:
                system_prompt = ""
            elif not isinstance(system_prompt, str):
                raise ValueError("system_prompt should be a string")

            self._chat_settings.provider = provider
            self._chat_settings.model = model
            self._chat_settings.temperature = temperature
            self._chat_settings.system_prompt = system_prompt
            return self

        def retrieval_settings(self, k: int = 3, number_of_search_docs: int = 0, fts:bool = False, similarity_search_type: Literal['cosine', 'dot', 'l2'] = "dot", tracing_api_key: str | None = None,
                            tracing_project_name: str = "berrydb"):
            """
            **Parameters:**
            - **k** (`int`, optional): Total number of documents to be retrieved. Defaults to `3`.
            - **fts** (`bool`, optional): If you want to use FTS instead of keyword search. Defaults to `False`. To use FTS you need to enable FTS on your BerryDB database, see how to enable `here </database.html#database.Database.enable_fts>`_
            - **number_of_search_docs** (`int`, optional): Number of results to be fetched from FTS or Keyword search in **k** documents
            - **tracing_api_key** (`str`, optional): langsmith API key to trace and evaluate a model with parameters
            - **tracing_project_name** (`str`, optional): A name for for tracing
            - **similarity_search_type** (`str`, optional): The type of vector search you want to perform `'Cosine'`, `'Dot'` or `'L2'`. Defaults to `Cosine`.
            """
            if k is None:
                k = 3
            elif not isinstance(k, int):
                raise ValueError("k should be an integer")
            elif k < 1:
                raise ValueError("k should be a positive integer")

            if number_of_search_docs is None:
                number_of_search_docs = 0
            elif not isinstance(number_of_search_docs, int):
                raise ValueError("number_of_search_docs should be an integer")
            elif number_of_search_docs < 0:
                raise ValueError("number_of_search_docs should be a non-negative integer")

            if number_of_search_docs > k:
                raise ValueError("number_of_search_docs should be less than k")

            if fts is None:
                fts = False
            if not isinstance(fts, bool):
                raise ValueError("fts should be a boolean")

            if tracing_api_key is not None and not isinstance(tracing_api_key, str):
                raise ValueError("langchain_api_key should be a string")

            if tracing_project_name is None:
                tracing_project_name = "berrydb"
            elif not isinstance(tracing_project_name, str):
                raise ValueError("langchain_project_name should be a string")

            if similarity_search_type is None:
                similarity_search_type = "dot"
            elif not isinstance(similarity_search_type, str):
                raise ValueError("similarity_search_type should be a string")
            similarity_search_type = similarity_search_type.lower()
            if similarity_search_type not in ['cosine', 'dot', 'l2']:
                raise ValueError("similarity_search_type should be cosine, dot or l2")


            self._retrieval_settings.k = k
            self._retrieval_settings.fts = fts
            self._retrieval_settings.number_of_search_docs = number_of_search_docs
            self._retrieval_settings.langchain_api_key = tracing_api_key
            self._retrieval_settings.langchain_project_name = tracing_project_name
            self._retrieval_settings.similarity_search_type = similarity_search_type
            return self

        def transform_settings(self, filter_expr: List[str] | None = None, filter_action:Literal['include', 'exclude'] = "include", jsonata_expr: str | None = None):
            """
            **Parameters:**
            - **filter_action** (`str`, optional): Determines how the filter expression is applied.
            Options: `'include'` (keep matching data) or `'exclude'` (remove matching data). Defaults to `'include'`.
            - **filter_expr** (`List[str]`, optional): A list of string that you want to filter from each document in your database based on **filter_action**
            - **jsonata_expr** (`str`, optional): A JSONata expression used for advanced transformations of document fields.

            .. note::
                JSONata expression is applied on the documents after the **filter_expr** has been applied (If provided)
            ..  # end
            """
            if filter_expr is not None and (not isinstance(filter_expr, list) or not all(isinstance(item, str) for item in filter_expr)):
                raise ValueError("filter_expr should be a string")
            if filter_action is not None and not isinstance(filter_action, str):
                raise ValueError("filter_action should be a string")
            if filter_action not in ['include', 'exclude']:
                raise ValueError("filter_action should be either include or exclude")
            if jsonata_expr is not None and not isinstance(jsonata_expr, str):
                raise ValueError("jsonata_expr should be a string")

            self._transform_settings.filter_expr = filter_expr
            self._transform_settings.filter_action = filter_action
            self._transform_settings.jsonata_expr = jsonata_expr
            return self

        def embed_settings(self, provider:Literal['openai', 'huggingface'] = "openai", model: str = None):
            """
            **Parameters:**
            - **provider** (`str`, optional): The embedding provider `'OpenAI'`, `'HuggingFace'`. Defaults to `'OpenAI'`
            - **model** (`str`, optional): The specific embedding model to use

            .. note::
                *Supported Models:*
                    - **OpenAI**: `text-embedding-3-small` **(default)**, `text-embedding-3-large`, `text-embedding-ada-002`
                    - **HuggingFace**: `sentence-transformers/all-mpnet-base-v2` **(default)**, `sentence-transformers/all-MiniLM-L6-v2`, `sentence-transformers/all-MiniLM-L12-v2`, `sentence-transformers/multi-qa-distilbert-dot-v1`, `sentence-transformers/multi-qa-mpnet-base-dot-v1`, `sentence-transformers/msmarco-distilbert-base-tas-b`

            ..  # end
            """
            if provider is None:
                provider = "openai"
            elif not isinstance(provider, str):
                raise ValueError("provider should be a string")
            elif provider not in {"openai", "huggingface"}:
                raise ValueError('Invalid provider, provider should be either "openai" or "huggingface"')

            if model is None:
                model = bdb_constants.DEFAULT_OPEN_AI_EMBEDDING_MODEL
            elif not isinstance(model, str):
                raise ValueError("model should be a string")


            self._embed_settings.provider = provider
            self._embed_settings.model = model
            return self

        def build(self):
            return Settings._create(self._chat_settings, self._retrieval_settings,
                                self._transform_settings, self._embed_settings)