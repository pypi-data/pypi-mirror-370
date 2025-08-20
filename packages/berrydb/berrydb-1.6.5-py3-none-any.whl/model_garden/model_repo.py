import logging
from pathlib import Path
from typing import Iterable, List, Optional

import requests

from constants import constants as bdb_constants
from model_garden.model import Model, BerryDBModel,HuggingFaceModel, VertexAIModel, CustomModel, ModelConfig
from model_garden.model_provider import ModelProvider
from utils.utils import Utils

logging.basicConfig(level=bdb_constants.LOGGING_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

class ModelRepo:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def vertexai_models_for_request(self) -> List[Model]:
        """Fetches a list of models the user can request from the Vertex AI API."""

        """ if self.provider != ModelProvider.VERTEX_AI_MODEL:
            raise NotImplementedError(f"list_models_ready_for_request_url not supported for provider {self.provider}") """

        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.list_models_ready_for_request_url
        params = { "apiKey": self.api_key }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        data = response.json()
        # for item in data:
        #     print("Model Name: ", item.get('name', ""), ", Description: ", item.get('description', ""))
        return data

    def __build_model_config(self, data:dict):
        config:ModelConfig|None = None
        if data["type"] == "custom":
            builder = ModelConfig.custom_builder()\
                ._id(data.get('id'))\
                .name(data.get('name'))\
                .description(data.get('description'))\
                ._predict_url(data.get('url'))\
                ._project_url(data.get('projectUrl'))\
                .self_hosted(data.get('selfHosted'))\
                .hosted_url(data.get('hostedUrl'))\
                .framework(data.get('framework'))\
                .upload_file_url(data.get('url'))\
                .framework_version(data.get('frameworkVersion'))\
                .hardware_accelerator((data.get('accelerator', '') or "").lower() == "gpu")\
                .category(data.get('category'))\
                .subcategory(data.get('subcategory'))
            config = builder.build(api_key=self.api_key)
        elif data["type"] == "huggingface":
            builder = ModelConfig.huggingface_builder()\
                .category(data.get('category'))\
                .subcategory(data.get('subcategory'))\
                ._id(data.get('id'))\
                .name(data.get('name'))\
                .description(data.get('description'))\
                ._predict_url(data.get('url'))\
                ._project_url(data.get('projectUrl'))\
                .hf_model_name(data.get('hfModelName'))\
                ._hf_type(data.get('hfType'))\
                ._hf_status(data.get('hfStatus'))
            config = builder.build(api_key=self.api_key)
        elif data["type"] == "vertexai":
            builder = ModelConfig.vertexai_builder()\
                ._id(data.get('id'))\
                .name(data.get('name'))\
                ._predict_url(data.get('url'))\
                ._project_url(data.get('projectUrl'))\
                .request_model(data.get('requestModel'))\
                .notes(data.get('notes'))
            # VertexAI models currently don't have category/subcategory in this SDK's config
            config = builder.build(api_key=self.api_key)
        elif data["type"] == "berrydb":
            builder = ModelConfig.berrydb_builder()\
                ._id(data.get('id'))\
                .name(data.get('name'))\
                .description(data.get('description'))\
                ._predict_url(data.get('url'))\
                ._project_url(data.get('projectUrl'))
            # BerryDB internal models currently don't have category/subcategory in this SDK's config
            config = builder.build(api_key=self.api_key)
        return config


    def get(
        self,
        provider: ModelProvider,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
    ) -> List[Model]:
        """
        Fetches a list of models from the model repository based on the provider and optional category/subcategory filters.

        Parameters:
        - **provider** (`ModelProvider`): The provider of the model(s) to fetch (e.g., `ModelProvider.HUGGING_FACE_MODEL`, `ModelProvider.VERTEX_AI_MODEL`). This parameter is required.
        - **category** (`str`, optional): The category to filter models by. Defaults to `None`.
        - **subcategory** (`str`, optional): The subcategory to filter models by. If provided, `category` must also be provided. Defaults to `None`.

        Returns:
        - `List[Model]`: A list of `Model` instances matching the criteria.
           Returns an empty list if no models are found.

        Raises:
        - `ValueError`: If the `provider` is `None` or invalid.
        - `ValueError`: If `subcategory` is provided without `category`.

        Example:
        ```python
        from berrydb import BerryDB, ModelProvider

        # Initialize BerryDB (if not already done)
        # BerryDB.init("your-berrydb-host")

        berrydb_api_key = "BERRYDB_API_KEY"

        # Get the model repository
        repo = BerryDB.model_repo(berrydb_api_key)

        # Example 1: Get all Custom models
        try:
            custom_models_list = repo.get(provider=ModelProvider.CUSTOM_MODEL)
            if custom_models_list:
                print(f"Fetched {len(custom_models_list)} Custom models:")
                for model_item in custom_models_list:
                    print(f"- {model_item.config.name}")
            else:
                print("No Custom models found.")
        except Exception as e:
            print(f"Error fetching Custom models: {e}")

        # Example 2: Get Hugging Face models in 'Text Generation' category
        try:
            text_gen_models = repo.get(
                provider=ModelProvider.HUGGING_FACE_MODEL,
                category="Text Generation" # Make sure this category exists
            )
            if text_gen_models:
                print(f"Found {len(text_gen_models)} Text Generation models.")
            else:
                print("No Text Generation models found for Hugging Face.")
        except Exception as e:
            print(f"Error fetching Text Generation models: {e}")

        # Example 3: Get Custom models in 'Computer Vision' category and 'Image Classification' subcategory
        try:
            image_classification_models = repo.get(
                provider=ModelProvider.CUSTOM_MODEL,
                category="Computer Vision", # Make sure this category exists
                subcategory="Image Classification" # Make sure this subcategory exists for the category
            )
            if image_classification_models:
                print(f"Found {len(image_classification_models)} Image Classification models.")
            else:
                print("No Image Classification models found for Custom provider with specified category/subcategory.")
        except Exception as e:
            print(f"Error fetching Image Classification models: {e}")
        ```

        .. seealso::
            - :ref:`ModelProvider <modelprovider>`
        .. #end
        """
        if not provider or not isinstance(provider, ModelProvider):
            raise ValueError("Valid provider is required and must be an instance of ModelProvider.")
        if category is not None and not isinstance(category, str):
            raise ValueError("Category must be a non-empty string or None.")
        if subcategory is not None and not isinstance(subcategory, str):
            raise ValueError("Subcategory must be a non-empty string or None.")
        if subcategory and not category:
            raise ValueError("Category must be provided if subcategory is specified.")

        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.get_models_url
        params = {"apiKey": self.api_key, "type": provider.value}
        if category:
            params["category"] = category
        if subcategory: # This implies category is also present due to the check above
            params["subcategory"] = subcategory

        if bdb_constants.debug_mode:
            logger.debug(f"Requesting models from URL: {url} with params: {params}")

        response = requests.get(url, params=params)
        if bdb_constants.debug_mode:
            logger.debug(f"Response status: {response.status_code}, Response text: {response.text}")

        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        data = response.json()
        model_list = []

        if isinstance(data, list):
            for m_data in data:
                try:
                    config = self.__build_model_config(m_data)
                    if config:
                        model_list.append(self.__create_model_by_provider(config))
                except Exception as e:
                    logger.error(f"Failed to build model config or create model for data: {m_data}. Error: {e}")
                    logger.error(f"Skipping model...")
                    continue
        elif isinstance(data, dict) and data:
            try:
                config = self.__build_model_config(data)
                if config:
                    model_list.append(self.__create_model_by_provider(config))
            except Exception as e:
                logger.error(f"Failed to build model config or create model for single data object: {data}. Error: {e}")
        elif not data:
            logger.info(f"No models found for provider '{provider.value}' with specified filters.")


        return model_list

    def get_by_name(self, model_name: str, provider: ModelProvider|None = None) -> Optional[Model]:
        """
        Fetches a specific model by its name and provider.

        Parameters:
        - **model_name** (`str`): The name of the specific model to fetch.
        - **provider** (`ModelProvider`, optional): The provider of the model to fetch.

        Returns:
        - `Model` | `None`: An instance of the Model class if found, otherwise `None`.

        Raises:
        - `ValueError`: If `provider` is not of type `ModelProvider` or `model_name` is `None` or invalid.
        - An exception (via `Utils.handleApiCallFailure`) if another API error occurs (e.g. server error).

        Example:
        ```python
        from berrydb import BerryDB, ModelProvider

        # Initialize BerryDB (if not already done)
        # BerryDB.init("your-berrydb-host")

        berrydb_api_key = "BERRYDB_API_KEY"
        repo = BerryDB.model_repo(berrydb_api_key)

        try:
            # Example 1: Get a specific Hugging Face model
            hf_model = repo.get_by_name(
                model_name="my-sentiment-analyzer"
                provider=ModelProvider.HUGGING_FACE_MODEL,
            )
            if hf_model:
                print(f"Fetched Hugging Face model: {hf_model.config.name}")
            else:
                print("Hugging Face model 'my-sentiment-analyzer' not found.")

            # Example 2: Get a specific Vertex AI model
            vertex_model = repo.get_by_name(
                model_name="gemini-pro" # Ensure this model exists
                provider=ModelProvider.VERTEX_AI_MODEL,
            )
            if vertex_model:
                print(f"Fetched Vertex AI model: {vertex_model.config.name}")
            else:
                print("Vertex AI model 'gemini-pro' not found.")

        except Exception as e: # Catch other potential API errors
            print(f"An error occurred: {e}")
        ```

        .. seealso::
            - :ref:`ModelProvider <modelprovider>`
        .. #end
        """
        # The provider must be either None or of type ModelProvider
        if provider is not None and not isinstance(provider, ModelProvider):
            raise ValueError("Valid provider is required and must be an instance of ModelProvider or None.")
        if not model_name or not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("Valid model_name is required and must be a non-empty string.")

        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.get_models_url
        params = {"apiKey": self.api_key, "name": model_name.strip()}
        if provider:
            params["type"] = provider.value

        if bdb_constants.debug_mode:
            logger.debug(f"Requesting model by name from URL: {url} with params: {params}")

        response = requests.get(url, params=params)
        if bdb_constants.debug_mode:
            logger.debug(f"Response status: {response.status_code}, Response text: {response.text}")

        if response.status_code == 404:
            logger.info(f"Model '{model_name}' not found for provider '{provider.value}'. API returned 404.")
            return None
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        model_data_list = response.json()

        if isinstance(model_data_list, list):
            if not model_data_list:
                logger.info(f"Model '{model_name}' not found for provider '{provider.value}'. API returned with empty list.")
                return None
            model_data_item = model_data_list[0]
        elif isinstance(model_data_list, dict) and model_data_list:
             model_data_item = model_data_list
        else:
            logger.error(f"Unexpected API response format for get_by_name. Data: {model_data_list}")
            return None


        try:
            config = self.__build_model_config(model_data_item)
            return self.__create_model_by_provider(config) if config else None
        except Exception as e:
            logger.error(f"Failed to build model config or create model for data: {model_data_item}. Error: {e}")
            return None

    def save(self, model_config: ModelConfig) -> Model:
        """
        Saves a new model to BerryDB.

        This method takes a `ModelConfig` object and registers the new model
        with BerryDB. You may save models of type `HuggingFace Model` and `Custom Model`.

        For `Custom Models` that are not self-hosted, either the path to the model file has `upload_file_path` has to be provided
        or a downloadable URL containing the model `upload_file_url` has to be provided.

        .. note::
            If your model has a specific folder and file structure, please zip the folder accordingly and use it to add the model.
        .. #end

        Parameters:
        - **model_config** (`ModelConfig`): An instance of `ModelConfig` containing all
          the necessary details for the model to be saved. This object should be
          created using one of the specific builders like `ModelConfig.huggingface_builder()`
          or `ModelConfig.custom_builder()`.

        Returns:
        - `Model`: An instance of `Model` class representing the successfully saved model.
          This object can be used for further operations.

        Raises:
        - `ValueError`: If `model_config` is `None`, not an instance of `ModelConfig`,
          or if essential provider-specific fields are missing (e.g., `hf_model_name`
          for Hugging Face models, or `hosted_url` for self-hosted custom models,
          or file paths/URLs for non-self-hosted custom models).

        Example:
        ```python
        from berrydb import BerryDB, ModelProvider, ModelConfig

        berrydb_api_key = "BERRYDB_API_KEY"
        repo = BerryDB.model_repo(berrydb_api_key)

        # Example 1: Save a Hugging Face model
        hf_config = (
            ModelConfig.huggingface_builder()
            .name("my-sentiment-classifier")
            .description("A sentiment analysis model from Hugging Face.")
            .hf_model_name("distilbert-base-uncased-finetuned-sst-2-english")
            .build(api_key="BERRYDB_API_KEY")
        )
        saved_hf_model = repo.save(hf_config)

        # Example 2: Save a self-hosted Custom Model
        custom_self_hosted_config = (
            ModelConfig.custom_builder()
            .name("my-custom-ner-api")
            .description("A self-hosted NER model.")
            .self_hosted(True)
            .hosted_url("http://my-ner-service.example.com/predict")
            .build(api_key="BERRYDB_API_KEY")
        )
        saved_custom_model = repo.save(custom_self_hosted_config)
        ```
        """
        if not (model_config and isinstance(model_config, ModelConfig)):
            raise ValueError("model_config is required and must be of type ModelConfig")

        if model_config.provider == ModelProvider.BERRYDB_MODEL:
            raise NotImplementedError(f"save not allowed for model provider {str(model_config.provider.value)}")

        if model_config.provider == ModelProvider.VERTEX_AI_MODEL:
            raise NotImplementedError(f"save not supported for model provider {str(model_config.provider.value)}, use the request method instead.")

        if not (model_config.provider == ModelProvider.HUGGING_FACE_MODEL or model_config.provider == ModelProvider.CUSTOM_MODEL):
            raise NotImplementedError(f"save not supported for model provider {str(model_config.provider.value)}")

        payload = {}

        if model_config.provider == ModelProvider.HUGGING_FACE_MODEL:
            if not model_config.hf_model_name:
                raise ValueError("hf_model_name is required for Hugging Face models")
            payload = {
                "name": model_config.name,
                "hfModelName": model_config.hf_model_name,
                "description": model_config.description,
                "category": model_config.category,
                "subcategory": model_config.subcategory,
            }

        else:
            if model_config.self_hosted:
                payload = {
                    "hostedUrl": model_config.hosted_url,
                    "selfHosted": True,
                    "category": model_config.category,
                    "subcategory": model_config.subcategory,
                }
            else:
                payload = {
                    "name": model_config.name,
                    "description": model_config.description,
                    "framework": model_config.framework,
                    "modelFrameworkVersion": model_config.framework_version,
                    "accelerator": "gpu" if model_config.hardware_accelerator else "cpu",
                    "selfHosted": False,
                    "category": model_config.category,
                    "subcategory": model_config.subcategory,
                }

            if model_config.upload_file_path is not None and len(model_config.upload_file_path):
                gcs_uri = self.__upload_files(model_name=model_config.name, paths=model_config.upload_file_path)
                payload["url"] = gcs_uri
            if model_config.upload_file_url:
                payload["url"] = model_config.upload_file_url

        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.add_model_url.format(model_config.provider.value)
        params = {"apiKey": self.api_key}
        if bdb_constants.debug_mode:
            print("url:", url)
            print("payload:", payload)
            print("params:", params)
        response = requests.post(url, json=payload, params=params)
        if bdb_constants.debug_mode:
            print("response.status_code:", response.status_code)
            print("response.text:", response.text)

        if not (response.status_code == 200 or response.status_code == 201):
            Utils.handleApiCallFailure(response.json(), response.status_code)

        json_response = response.json()
        if 'id' in json_response:
            model_config._id = json_response['id']
        if 'hfType' in json_response:
            model_config._hf_type = json_response['hfType']
        if 'hfStatus' in json_response:
            model_config._hf_status = json_response['hfStatus']

        print(f"Model {model_config.name} successfully saved.")
        return self.__create_model_by_provider(model_config)

    def __create_model_by_provider(self, config: ModelConfig):
        if config.provider == ModelProvider.HUGGING_FACE_MODEL:
            return HuggingFaceModel(self.api_key, config)
        elif config.provider == ModelProvider.VERTEX_AI_MODEL:
            return VertexAIModel(self.api_key, config)
        elif config.provider == ModelProvider.CUSTOM_MODEL:
            return CustomModel(self.api_key, config)
        elif config.provider == ModelProvider.BERRYDB_MODEL:
            return BerryDBModel(self.api_key, config)
        else:
            raise ValueError(f"Unsupported model provider: {config.provider.value}")

    def __multipart(self, model_name: str, paths: Iterable[str | Path]) -> List[tuple]:
        parts: List[tuple] = [("modelName", (None, model_name))]
        for fp in paths:
            p = Path(fp)
            parts.append(("files", (p.name, p.read_bytes())))
        return parts

    def __upload_files(self, *, model_name: str, paths: Iterable[str | Path]) -> str:
        files = self.__multipart(model_name, paths)
        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.upload_model_url
        params = {"apiKey": self.api_key}
        if bdb_constants.debug_mode:
            print("url:", url)
            print("files:", files)
            print("params:", params)
        response = requests.post(url, files=files, params=params)
        if bdb_constants.debug_mode:
            print("data.text:", response.text)
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)
        response = response.json()
        if "gcsUri" not in response:
            raise ValueError("Unable to upload model files, please check the file path and try again.")
        return response["gcsUri"]

    def request(self, model_config: ModelConfig) -> Model:
        """
        Requests a model deployment from the specified provider.

        This method initiates a request to deploy a model. Currently, it only supports Vertex AI models.

        Parameters:
        - **model_config** (`ModelConfig`): An instance of `ModelConfig` representing the model to be requested.
          It should be created using the `ModelConfig.vertexai_builder()` for Vertex AI models. The config must contain a `request_model` attribute.

        Returns:
        - `Model`: An instance of the `Model` class representing the requested model.
          This object can be used for further operations.

        Raises:
        - `ValueError`: If `model_config` is `None` or not an instance of `ModelConfig`.
        - `NotImplementedError`: If the method is called for a provider other than Vertex AI.

        Example:
        ```python
        from berrydb import BerryDB, ModelProvider, ModelConfig

        # Initialize BerryDB (if not already done)
        # BerryDB.init("your-berrydb-host")

        berrydb_api_key = "BERRYDB_API_KEY"
        repo = BerryDB.model_repo(berrydb_api_key)

        # Create a Vertex AI model config
        vertex_config = (
            ModelConfig.vertexai_builder()
            .name("gemini-pro")
            .request_model("gemini-pro")
            .notes("Requesting a Gemini Pro model.")
            .build(api_key="BERRYDB_API_KEY")
        )

        # Request the Vertex AI model
        requested_model = repo.request(vertex_config)
        ```
        """
        if not (model_config and isinstance(model_config, ModelConfig)):
            raise ValueError("model is required and must be of type Model")

        if model_config.provider != ModelProvider.VERTEX_AI_MODEL:
            raise NotImplementedError(f"request not supported for provider {str(model_config.provider.value)}, use save instead")

        url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.model_request_url
        params = {"apiKey": self.api_key}
        payload = {"name": model_config.name, "requestModel": model_config.request_model, "notes": model_config.notes}
        response = requests.post(url, json=payload, params=params)

        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        print("Model requested successfully!")