import logging
from typing import List, Optional, Dict, Tuple

import requests

from constants import constants as bdb_constants
from model_garden.model_provider import ModelProvider
from utils.utils import Utils

# Module-level cache for model categories
_cached_categories_data: Optional[List[Dict]] = None
_cached_categories_key: Optional[Tuple[str, str]] = None # (ml_backend_url, api_key)

def _clear_model_categories_cache():
    """Clears the model categories cache. Called when SDK host might change."""
    global _cached_categories_data, _cached_categories_key
    logger.debug("Clearing model categories cache.")
    _cached_categories_data = None
    _cached_categories_key = None

logger = logging.getLogger("ModelConfig")


class ModelConfig:

    def __init__(self, *args, **kwargs):
        self.provider:ModelProvider
        # common
        self._api_key:str
        self._id:str
        self.name:str
        self.description:str|None
        self.category:str|None
        self.subcategory:str|None
        # huggingface
        self.hf_model_name:str|None
        self._hf_type:str|None
        self._hf_status:str|None
        # vertex ai
        self.request_model:str|None
        self.notes:str|None
        # custom
        self.self_hosted:bool|None
        self._predict_url:str|None
        self._project_url:str|None
        self.hosted_url:str|None
        self.upload_file_path:List[str]|None
        self.upload_file_url:str|None
        self.framework:str|None
        self.framework_version:str|None
        self.hardware_accelerator:bool|None
        raise RuntimeError("Use a specific builder, e.g. ModelConfig.huggingface_builder(), to create instances.")

    @classmethod
    def _create(
        cls,
        _api_key: str,
        provider: ModelProvider,
        name: str,
        _id:str = None,
        description: str|None = None,
        hf_model_name: Optional[str] = None,
        _hf_type: Optional[str] = None,
        _hf_status: Optional[str] = None,
        notes: Optional[str] = None,
        self_hosted: Optional[bool] = False,
        _predict_url: Optional[str] = None,
        _project_url: Optional[str] = None,
        upload_file_path: Optional[List[str]] = None,
        upload_file_url: Optional[str] = None,
        hosted_url: Optional[str] = None,
        framework: Optional[str] = None,
        framework_version: Optional[str] = None,
        hardware_accelerator: Optional[bool] = False,
        request_model: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
    ) -> "ModelConfig":
        self = object.__new__(cls)
        self.provider = provider
        self._id = _id
        self._api_key = _api_key
        self.name = name
        self.description = description
        self.self_hosted = self_hosted
        self._predict_url = _predict_url
        self._project_url = _project_url
        self.hosted_url = hosted_url
        self.upload_file_path = upload_file_path
        self.upload_file_url = upload_file_url
        self.framework = framework
        self.framework_version = framework_version
        self.hardware_accelerator = hardware_accelerator
        self.request_model = request_model
        self.hf_model_name = hf_model_name
        self._hf_type = _hf_type
        self._hf_status = _hf_status
        self.notes = notes
        self.category = category
        self.subcategory = subcategory
        self.__validate()
        return self

    def __validate(self):
        # Common mandatory
        if not (self.provider and isinstance(self.provider, ModelProvider)):
            raise ValueError("provider is mandatory and should be of type ModelProvider")
        if not self.name:
            raise ValueError("name is mandatory")
        if not (isinstance(self.name, str) and len(self.name.strip()) > 0):
            raise ValueError("name must be a non-empty string")
        if self.description and not isinstance(self.description, str):
            raise ValueError("description must be a string or None")

        # Category and Subcategory validation for HuggingFace and Custom models
        if self.provider in [ModelProvider.HUGGING_FACE_MODEL, ModelProvider.CUSTOM_MODEL]:
            if self.category is None or not (isinstance(self.category, str) and len(self.category.strip()) > 0):
                raise ValueError("Category is mandatory for Hugging Face and Custom models")
            if self.subcategory is None or not (isinstance(self.subcategory, str) and len(self.subcategory.strip()) > 0):
                raise ValueError("Subcategory is mandatory for Hugging Face and Custom models")
            if not (isinstance(self.category, str) and len(self.category.strip()) > 0):
                raise ValueError("category must be a non-empty string if provided")
            if not (self.subcategory and isinstance(self.subcategory, str) and len(self.subcategory.strip()) > 0):
                raise ValueError("subcategory is mandatory and must be a non-empty string if category is provided")

            if not bdb_constants.BASE_URL:
                raise RuntimeError(
                    "BerryDB SDK not initialized. Call BerryDB.init(host) before validating model categories."
                )
            try:
                available_categories_data = ModelConfig.__get_or_fetch_categories_data(self._api_key)
            except ValueError as e:
                # _get_or_fetch_categories_data raises ValueError on failure with a descriptive message.
                # Re-raise it to indicate validation failure.
                raise e

            found_category_data = next((cat_data for cat_data in available_categories_data if cat_data.get("name") == self.category), None)

            if not found_category_data:
                valid_category_names = [c.get("name") for c in available_categories_data if c.get("name")]
                logger.warning(f"Invalid category '{self.category}' provided. Available: {', '.join(sorted(valid_category_names))}")
                raise ValueError(
                    f"Invalid category '{self.category}'. "
                    f"Available categories are: {', '.join(sorted(valid_category_names))}."
                )
            valid_subcategories_for_category = [sc.get("name") for sc in found_category_data.get("subcategories", []) if sc.get("name")]
            if self.subcategory not in valid_subcategories_for_category:
                raise ValueError(
                    f"Invalid subcategory '{self.subcategory}' for category '{self.category}'. "
                    f"Available subcategories for '{self.category}' are: {', '.join(sorted(valid_subcategories_for_category))}."
                )

        # Provider-specific
        if self.provider == ModelProvider.HUGGING_FACE_MODEL:
            if not self.hf_model_name:
                raise ValueError("hf_model_name is mandatory for Hugging Face models")

        if self.provider == ModelProvider.VERTEX_AI_MODEL:
            if not self.request_model:
                raise ValueError("request_model is mandatory for Vertex AI models")

        if self.provider == ModelProvider.CUSTOM_MODEL:
            if self.self_hosted is None or not isinstance(self.self_hosted, bool):
                self.self_hosted = False
            if self.self_hosted and not (self.hosted_url and isinstance(self.hosted_url, str)):
                    raise ValueError("hosted_url is mandatory for self-hosted custom models")
            if not self.self_hosted:
                if not ((isinstance(self.upload_file_path, list) and len(self.upload_file_path))\
                    or (self.upload_file_url and isinstance(self.upload_file_url, str))):
                        raise ValueError("Either upload_file_path or upload_file_url is mandatory if not self-hosted")
                if not (self.framework and isinstance(self.framework, str)):
                    raise ValueError("framework is mandatory for custom models and must be a string")
                if not (self.framework_version and isinstance(self.framework_version, str)):
                    raise ValueError("framework_version is mandatory for custom models and must be a string")
                """ frameworks_api_url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.model_frameworks_url
                try:
                    response = requests.get(frameworks_api_url)
                    if response.status_code != 200:
                        Utils.handleApiCallFailure(response.json(), response.status_code)
                    available_frameworks_meta = response.json()
                except requests.exceptions.RequestException as e:
                    raise ValueError(
                        f"Could not fetch model framework data from BerryDB: {e}. "
                        "Please ensure BerryDB is accessible and correctly initialized."
                    )
                except ValueError as e: # JSONDecodeError inherits from ValueError
                    raise ValueError(
                        f"Could not parse model framework metadata from BerryDB. Invalid JSON received: {e}"
                    )

                framework_options = {
                    k: v for k, v in available_frameworks_meta.items()
                }

                if self.framework not in framework_options:
                    raise ValueError(
                        f"Invalid framework '{self.framework}'. "
                        f"Available frameworks are: {', '.join(sorted(framework_options.keys()))}."
                    )

                available_versions = framework_options[self.framework]
                if self.framework_version not in available_versions:
                    raise ValueError(
                        f"Invalid framework_version '{self.framework_version}' for framework '{self.framework}'. "
                        f"Available versions for '{self.framework}' are: {', '.join(sorted(available_versions))}."
                    ) """

    @staticmethod
    def __get_or_fetch_categories_data(api_key: str) -> List[Dict]:
        """
        Fetches model categories from API or returns from cache.
        Updates cache on successful fetch, clears cache on failure.
        """
        global _cached_categories_data, _cached_categories_key

        if not bdb_constants.ML_BACKEND_BASE_URL:
            # This check is also in __validate and get_available_model_categories,
            # but good to have here as this is the direct API interaction point.
            raise RuntimeError(
                "BerryDB SDK not initialized. Call BerryDB.init(host) before fetching model categories."
            )

        current_key = (bdb_constants.ML_BACKEND_BASE_URL, api_key)

        if _cached_categories_key == current_key and _cached_categories_data is not None:
            logger.debug("Returning model categories from cache.")
            return _cached_categories_data

        # Key mismatch or no cache, fetch new data
        categories_url = bdb_constants.ML_BACKEND_BASE_URL + bdb_constants.get_model_categories_url
        params = {"apiKey": api_key}

        logger.info(f"Fetching model categories from {categories_url}...")

        try:
            response = requests.get(categories_url, params=params)
            response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)
            data = response.json()

            _cached_categories_data = data
            _cached_categories_key = current_key
            logger.info("Successfully fetched and cached model categories.")
            return data
        except (requests.exceptions.RequestException, ValueError) as e: # Catches network errors, HTTP errors, JSON decode errors
            _clear_model_categories_cache() # Clear cache on any fetch error
            logger.error(f"Failed to fetch or parse model categories: {e}")
            raise ValueError(f"Could not fetch or parse model category data from BerryDB: {e}") from e

    @staticmethod
    def get_available_model_categories(api_key:str) -> Dict[str, List[str]]:
        """
        Fetches the available model categories and their subcategories from BerryDB.

        This can be used to understand the valid options for the `category`
        and `subcategory` parameters when configuring Hugging Face or Custom models.
        The category and subcategory help in organizing and discovering models within BerryDB.
        The SDK must be initialized using `BerryDB.init(host)` before calling this method.

        Returns:
        - `Dict[str, List[str]]`: A dictionary where keys are category names (str)
          and values are lists of subcategory names (List[str]) for that category.

        Parameters:
        - **api_key** (`str`): The API key for authenticating with BerryDB.

        Example:
        ```python
         from berrydb import ModelConfig, BerryDB

        # Ensure BerryDB SDK is initialized
        # BerryDB.init("YOUR_BERRYDB_HOST")
        berrydb_api_key = "BERRYDB_API_KEY" # Replace with your actual API key

        try:
            categories_data = ModelConfig.get_available_model_categories(api_key=berrydb_api_key)
            # categories_data will look like:
            # {
            #     "Generative AI": [
            #         "Supervised Language Model Fine-tuning",
            #         "Human Preference collection for RLHF",
            #         # ... other subcategories ...
            #     ],
            #     "Others": ["Others"]
            # }
            for category_name, subcategories_list in categories_data.items():
                print(f"Category: {category_name}")
                for subcategory_name in subcategories_list:
                    print(f"  Subcategory: {subcategory_name}")
        except Exception as e:
            print(f"Error fetching categories: {e}")
        ```
        """
        if not bdb_constants.ML_BACKEND_BASE_URL:
            raise RuntimeError(
                "BerryDB SDK not initialized. Call BerryDB.init(host) before fetching model categories."
            )
        try:
            # Use the caching helper
            raw_categories_data = ModelConfig.__get_or_fetch_categories_data(api_key)

            processed_categories: Dict[str, List[str]] = {}
            for category_item in raw_categories_data:
                category_name = category_item.get("name")
                if category_name:
                    subcategories = [
                        subcat.get("name")
                        for subcat in category_item.get("subcategories", [])
                        if subcat.get("name")
                    ]
                    processed_categories[category_name] = subcategories
            return processed_categories
        except ValueError as e: # _get_or_fetch_categories_data raises ValueError
            # Wrap in RuntimeError as per original method's behavior for API call failures
            raise RuntimeError(f"Failed to get available model categories: {e}") from e

    # Provider-specific builder entry points
    @classmethod
    def huggingface_builder(cls) -> "HuggingFaceModelConfigBuilder":
        """
        Returns a builder for creating Hugging Face model configurations.

        This class method provides a convenient way to construct a `ModelConfig`
        specifically tailored for Hugging Face models.

        Returns:
        - `ModelConfig.HuggingFaceModelConfigBuilder`: An instance of the builder
        that can be used to set Hugging Face specific model attributes.

        Example:
        ```python
        from berrydb import ModelConfig

        # Configure the Hugging Face model
        hf_config = (
            ModelConfig.huggingface_builder()
            .name("my-sentiment-analyzer")
            .description("A sentiment analysis model from Hugging Face.")
            .hf_model_name("distilbert-base-uncased-finetuned-sst-2-english")
            .build(api_key="BERRYDB_API_KEY")
        )

        # The hf_config object is now ready to be used, for example, with repo.save()
        ```
        """
        return ModelConfig.HuggingFaceModelConfigBuilder()

    @classmethod
    def custom_builder(cls) -> "CustomModelConfigBuilder":
        """
        Returns a builder for creating Custom model configurations.

        This class method provides a convenient way to construct a `ModelConfig`
        specifically tailored for Custom models, which can be either self-hosted
        or hosted by BerryDB.

        Returns:
        - `ModelConfig.CustomModelConfigBuilder`: An instance of the builder
        that can be used to set Custom model specific attributes.

        Example:
        ```python
        from berrydb import ModelConfig

        # Example 1: Configure a self-hosted Custom Model
        custom_self_hosted_builder = ModelConfig.custom_builder()
        custom_self_hosted_config = (
            custom_self_hosted_builder
            .name("my-custom-ner-api")
            .description("A self-hosted NER model.")
            .self_hosted()
            .hosted_url("http://my-ner-service.example.com/predict")
            .build(api_key="BERRYDB_API_KEY")
        )
        # The custom_self_hosted_config object is now ready to be used.

        # Example 2: Configure a BerryDB-hosted Custom Model (uploading a file)
        custom_berrydb_hosted_config = (
            ModelConfig.custom_builder()
            .name("my-image-classifier")
            .description("An image classification model hosted on BerryDB.")
            .self_hosted(False)  # Explicitly or by default
            .upload_file_path(["/path/to/your/model.zip"]) # Path to your model artifact(s)
            .framework("tensorflow")
            .framework_version("2.5")
            .hardware_accelerator(True) # Optional: request GPU
            .build(api_key="BERRYDB_API_KEY")
        )
        # The custom_berrydb_hosted_config object is now ready to be used.

        # Example 3: Configure a BerryDB-hosted Custom Model (using a downloadable URL)
        custom_url_hosted_config = (
            ModelConfig.custom_builder()
            .name("my-text-generator")
            .description("A text generation model from a URL, hosted on BerryDB.")
            .upload_file_url("http://example.com/models/my_text_model.zip")
            .framework("pytorch")
            .framework_version("1.9")
            .build(api_key="BERRYDB_API_KEY")
        )
        # The custom_url_hosted_config object is now ready to be used.
        ```
        """
        return ModelConfig.CustomModelConfigBuilder()

    @classmethod
    def vertexai_builder(cls) -> "VertexAIModelConfigBuilder":
        """
        Returns a builder for creating Vertex AI model configurations.

        This class method provides a convenient way to construct a `ModelConfig`
        specifically tailored for requesting models from Vertex AI.

        Returns:
        - `ModelConfig.VertexAIModelConfigBuilder`: An instance of the builder
        that can be used to set Vertex AI specific model attributes for a request.

        Example:
        ```python
        from berrydb import ModelConfig

        # Configure the Vertex AI model request
        vertex_config = (
            ModelConfig.vertexai_builder()
            .name("gemini-pro-request")  # Name for your reference in BerryDB
            .request_model("gemini-pro")  # The actual Vertex AI model name to request
            .notes("Requesting a Gemini Pro model for text generation.")
            .build(api_key="BERRYDB_API_KEY")
        )

        # The vertex_config object is now ready to be used, for example, with repo.request()
        ```
        """
        return ModelConfig.VertexAIModelConfigBuilder()

    @classmethod
    def berrydb_builder(cls) -> "BerryDBModelConfigBuilder":
        """
        Returns a builder for creating BerryDB model configurations.

        This class method provides a convenient way to construct a `ModelConfig`
        specifically tailored for models managed by BerryDB.

        Returns:
        - `ModelConfig.BerryDBModelConfigBuilder`: An instance of the builder
        that can be used to set BerryDB specific model attributes.

        Example:
        ```python
        from berrydb import ModelConfig

        # Configure the BerryDB model
        berrydb_config = (
            ModelConfig.berrydb_builder()
            .name("my-internal-model")
            .description("An internal model managed by BerryDB.")
            .build(api_key="BERRYDB_API_KEY")
        )

        # The berrydb_config object is now ready to be used.
        ```
        """
        return ModelConfig.BerryDBModelConfigBuilder()


    class HuggingFaceModelConfigBuilder:
        def __init__(self):
            self.__id = None
            self.__name = None
            self.__description = None
            self.__predict_url = None
            self.__project_url = None
            self.__hf_model_name = None
            self.__hf_type = None
            self.__hf_status = None
            self.__category = None
            self.__subcategory = None

        def _id(self, id:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__id = id
            return self

        def name(self, name:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            """
            Sets the name for the Hugging Face model configuration.

            This name is used to identify the model configuration within BerryDB.

            Parameters:
            - **name** (`str`): The desired name for the model configuration.

            Returns:
            - `ModelConfig.HuggingFaceModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            hf_builder = ModelConfig.huggingface_builder()
            hf_config = (
                hf_builder
                .name("my-awesome-hf-model")
                .hf_model_name("bert-base-uncased")
                # ... other configurations ...
                .build(api_key="BERRYDB_API_KEY")
            )
            # hf_config.name will be "my-awesome-hf-model"
            ```
            """
            self.__name = name
            return self

        def description(self, desc:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            """
            Sets the description for the Hugging Face model configuration.

            This provides additional context or details about the model.

            Parameters:
            - **desc** (`str`): The description string for the model configuration.

            Returns:
            - `ModelConfig.HuggingFaceModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            hf_builder = ModelConfig.huggingface_builder()
            hf_config = (
                hf_builder
                .description("A T5 model fine-tuned for English to French translation.")
                .name("my-hf-translator")
                .hf_model_name("t5-small")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__description = desc
            return self

        def hf_model_name(self, hf_model_name:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            """
            Sets the Hugging Face model ID for the configuration.

            This is the identifier of the model on the Hugging Face Hub
            (e.g., "bert-base-uncased", "t5-small").

            Parameters:
            - **hf_model_name** (`str`): The Hugging Face model ID.

            Returns:
            - `ModelConfig.HuggingFaceModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            hf_builder = ModelConfig.huggingface_builder()
            hf_config = (
                hf_builder
                .hf_model_name("distilbert-base-uncased-finetuned-sst-2-english")
                .name("my-hf-sentiment-model")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__hf_model_name = hf_model_name
            return self

        def _hf_type(self, hf_type:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__hf_type = hf_type
            return self

        def _hf_status(self, hf_status:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__hf_status = hf_status
            return self

        def _predict_url(self, url:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__predict_url = url
            return self

        def _project_url(self, url:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__project_url = url
            return self

        def category(self, category:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__category = category
            return self

        def subcategory(self, subcategory:str) -> "ModelConfig.HuggingFaceModelConfigBuilder":
            self.__subcategory = subcategory
            return self

        def build(self, api_key:str) -> "ModelConfig":
            """
            Constructs a `ModelConfig` instance for a Hugging Face model.

            This method uses all the settings previously configured on the builder
            to create a new `ModelConfig` object.

            Returns:
            - `ModelConfig`: A new `ModelConfig` instance configured for a Hugging Face model.

            Example:
            ```python
            from berrydb import ModelConfig

            hf_builder = ModelConfig.huggingface_builder()
            hf_config = (
                hf_builder
                .name("my-hf-model")
                .hf_model_name("bert-base-uncased")
                .description("A standard BERT model.")
                .build(api_key="BERRYDB_API_KEY") # This call creates the ModelConfig instance
            )
            # hf_config is now an instance of ModelConfig
            ```
            """
            return ModelConfig._create(
                provider=ModelProvider.HUGGING_FACE_MODEL,
                _api_key=api_key,
                _id=self.__id,
                name=self.__name,
                _predict_url=self.__predict_url,
                _project_url=self.__project_url,
                description=self.__description,
                hf_model_name=self.__hf_model_name,
                _hf_type=self.__hf_type,
                _hf_status=self.__hf_status,
                category=self.__category,
                subcategory=self.__subcategory,
            )


    class CustomModelConfigBuilder:
        def __init__(self):
            self.__id:str|None = None
            self.__name:str|None = None
            self.__description:str|None = None
            self.__self_hosted:bool|None = False
            self.__predict_url:str|None = None
            self.__project_url:str|None = None
            # Optional fields
            self.__upload_file_path:List[str]|None = None
            self.__upload_file_url:str|None = None
            self.__hosted_url:str|None = None
            self.__framework:str|None = None
            self.__framework_version:str|None = None
            self.__hardware_accelerator:bool = False
            self.__category:str = None
            self.__subcategory:str = None

        def _id(self, id:str) -> "ModelConfig.CustomModelConfigBuilder":
            self.__id = id
            return self

        def name(self, name:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the name for the Custom model configuration.

            This name is used to identify the model configuration within BerryDB.

            Parameters:
            - **name** (`str`): The desired name for the model configuration.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-custom-image-classifier")
                # ... other configurations for the custom model ...
                .build(api_key="BERRYDB_API_KEY")
            )
            # custom_config.name will be "my-custom-image-classifier"
            ```
            """
            self.__name = name
            return self

        def description(self, desc:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the description for the Custom model configuration.

            This provides additional context or details about the model.

            Parameters:
            - **desc** (`str`): The description string for the model configuration.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-object-detector")
                .description("A custom model trained to detect various objects in images.")
                # ... other configurations for the custom model ...
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__description = desc
            return self

        def self_hosted(self, hosted:bool = True) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Specifies if the Custom model is self-hosted.

            If `True`, BerryDB expects the model to be accessible via a URL
            provided by `hosted_url()`. If `False` (or not set, as `False` is
            the default if this method isn't called after `upload_file_path` or
            `upload_file_url` is used), BerryDB will host the model, and you
            must provide model artifacts via `upload_file_path()` or `upload_file_url()`.

            Parameters:
            - **hosted** (`bool`, optional): `True` if the model is self-hosted,
              `False` otherwise. Defaults to `True` if called without arguments.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            # Configure a self-hosted model
            self_hosted_builder = ModelConfig.custom_builder()
            self_hosted_config = (
                self_hosted_builder
                .name("my-external-api-model")
                .self_hosted(True) # or simply .self_hosted()
                .hosted_url("http://my.service.com/predict")
                .build(api_key="BERRYDB_API_KEY")
            )

            ```
            .. note::
                self_hosted is implicitly False
            ..
            """
            self.__self_hosted = hosted
            return self

        def upload_file_path(self, path:List[str]) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the local file path(s) for the Custom model artifacts.

            Use this method when BerryDB is hosting the model (`self_hosted` is `False`)
            and you are providing the model files from your local filesystem.
            The provided path(s) will be uploaded to BerryDB.

            Parameters:
            - **path** (`List[str]`): A list of strings, where each string is a path to a model file to
            be uploaded. If the model requires a directory structure, it should be zipped before upload.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-local-pytorch-model")
                .description("A PyTorch model uploaded from local files.")
                .upload_file_path(["/path/to/my_model.pt", "/path/to/config.json"]) # or ["/path/to/model_directory.zip"]
                .framework("pytorch")
                .framework_version("1.9")
                # .self_hosted(False) # Implicitly False when upload_file_path is used
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            if not (isinstance(path, list) and len(path) > 0):
                raise ValueError("upload_file_path must be a non-empty list")
            self.__upload_file_path = path
            return self

        def upload_file_url(self, url:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the URL from which Custom model artifacts can be downloaded.

            Use this method when BerryDB is hosting the model (`self_hosted` is `False`)
            and your model files are accessible via a public URL. BerryDB will
            download the artifacts from this URL.

            Parameters:
            - **url** (`str`): The direct downloadable URL to the model artifact(s)
              (e.g., a URL to a .zip file).

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-remote-sklearn-model")
                .description("An sklearn model downloaded from a URL.")
                .upload_file_url("http://example.com/models/my_sklearn_model.zip")
                .framework("scikit-learn")
                .framework_version("1.0")
                # .self_hosted(False) # Implicitly False when upload_file_url is used
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            if not (isinstance(url, str)):
                raise ValueError("upload_file_url must be a non-empty list")
            self.__upload_file_url = url
            return self

        def hosted_url(self, url:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the prediction endpoint URL for a self-hosted Custom model.

            Use this method when `self_hosted` is `True`. BerryDB will use this URL
            to send prediction requests to your model.

            Parameters:
            - **url** (`str`): The complete URL of your model's prediction endpoint.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-external-sentiment-analyzer")
                .self_hosted(True) # Indicate it's self-hosted
                .hosted_url("https://my.custom.model.api/predict") # Provide the endpoint
                .description("A sentiment analysis model hosted on my own server.")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__hosted_url = url
            return self

        def framework(self, framework:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the framework for the Custom model.

            This specifies the machine learning framework used by your model
            (e.g., "keras", "pytorch", "scikit-learn"). This information is
            needed by BerryDB when hosting the model.

            Parameters:
            - **framework** (`str`): The name of the machine learning framework.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-tf-model")
                .framework("keras")
                # ... other configurations for a tensorflow model ...
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__framework = framework
            return self

        def framework_version(self, version:str) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Sets the framework version for the Custom model.

            This specifies the version of the machine learning framework
            (e.g., "2.14" for TensorFlow/Keras, "1.9" for PyTorch). This information is
            needed by BerryDB when hosting the model.

            Parameters:
            - **version** (`str`): The version string of the machine learning framework.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-tf-model-specific-version")
                .framework("keras")
                .framework_version("2.14")
                # ... other configurations ...
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__framework_version = version
            return self

        def hardware_accelerator(self, accel:bool = True) -> "ModelConfig.CustomModelConfigBuilder":
            """
            Specifies if a hardware accelerator (GPU) should be used for the Custom model.

            This is applicable when BerryDB is hosting the model (`self_hosted` is `False`).
            Setting this to `True` requests a GPU for the model deployment.

            Parameters:
            - **accel** (`bool`, optional): `True` to request a hardware accelerator (GPU),
              `False` otherwise. Defaults to `True`.

            Returns:
            - `ModelConfig.CustomModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config_gpu = (
                custom_builder
                .name("my-gpu-intensive-model")
                .upload_file_path(["/path/to/model_files.zip"])
                .framework("pytorch")
                .framework_version("1.10")
                .hardware_accelerator(True) # Request GPU
                .build(api_key="BERRYDB_API_KEY")
            )

            custom_builder_cpu = ModelConfig.custom_builder()
            custom_config_cpu = (
                custom_builder_cpu
                .name("my-cpu-model")
                .upload_file_path(["/path/to/other_model.zip"])
                .framework("sklearn")
                .framework_version("1.0")
                .hardware_accelerator(False) # Explicitly request CPU
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__hardware_accelerator = accel
            return self

        def _predict_url(self, url:str) -> "ModelConfig.CustomModelConfigBuilder":
            self.__predict_url = url
            return self

        def _project_url(self, url:str) -> "ModelConfig.CustomModelConfigBuilder":
            self.__project_url = url
            return self

        def category(self, category:str) -> "ModelConfig.CustomModelConfigBuilder":
            self.__category = category
            return self

        def subcategory(self, subcategory:str) -> "ModelConfig.CustomModelConfigBuilder":
            self.__subcategory = subcategory
            return self

        def build(self, api_key:str) -> "ModelConfig":
            """
            Constructs a `ModelConfig` instance for a Custom model.

            This method uses all the settings previously configured on the builder
            to create a new `ModelConfig` object.

            Returns:
            - `ModelConfig`: A new `ModelConfig` instance configured for a Custom model.

            Example:
            ```python
            from berrydb import ModelConfig

            custom_builder = ModelConfig.custom_builder()
            custom_config = (
                custom_builder
                .name("my-custom-model")
                .description("A custom model for a specific task.")
                .self_hosted(False)
                .upload_file_path(["/path/to/model.zip"])
                .framework("tensorflow")
                .framework_version("2.7")
                .build(api_key="BERRYDB_API_KEY") # This call creates the ModelConfig instance
            )
            # custom_config is now an instance of ModelConfig
            ```
            """
            return ModelConfig._create(
                provider=ModelProvider.CUSTOM_MODEL,
                name=self.__name,
                _id=self.__id,
                _api_key=api_key,
                description=self.__description,
                self_hosted=self.__self_hosted,
                _project_url=self.__predict_url,
                _predict_url=self.__project_url,
                upload_file_path=self.__upload_file_path,
                upload_file_url=self.__upload_file_url,
                hosted_url=self.__hosted_url,
                framework=self.__framework,
                framework_version=self.__framework_version,
                hardware_accelerator=self.__hardware_accelerator,
                category=self.__category,
                subcategory=self.__subcategory,
            )


    class VertexAIModelConfigBuilder:
        def __init__(self):
            self.__id = None
            self.__name = None
            self.__notes = None
            self.__request_model = None
            self.__predict_url = None
            self.__project_url = None

        def _id(self, id:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            self.__id = id
            return self

        def name(self, name:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            """
            Sets the reference name for the Vertex AI model configuration.

            This name is used to identify this specific model request/configuration
            within BerryDB.

            Parameters:
            - **name** (`str`): The desired name for the Vertex AI model configuration.

            Returns:
            - `ModelConfig.VertexAIModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            vertex_builder = ModelConfig.vertexai_builder()
            vertex_config = (
                vertex_builder
                .name("my-gemini-pro-request") # Name for BerryDB reference
                .request_model("gemini-pro")    # Actual Vertex AI model
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__name = name
            return self

        def request_model(self, request_model:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            """
            Sets the Vertex AI model to be requested.

            This specifies the identifier of the model from Google Vertex AI
            that BerryDB should attempt to make available (e.g., "gemini-pro",
            "text-bison@001").

            Parameters:
            - **request_model** (`str`): The Vertex AI model identifier.

            Returns:
            - `ModelConfig.VertexAIModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            vertex_builder = ModelConfig.vertexai_builder()
            vertex_config = (
                vertex_builder
                .name("my-vertex-text-model") # Name for BerryDB reference
                .request_model("text-bison@001") # The Vertex AI model to request
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """

            self.__request_model = request_model
            return self

        def notes(self, notes:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            """
            Sets optional notes for the Vertex AI model request.

            These notes can be used to add any relevant comments or metadata
            associated with the model request.

            Parameters:
            - **notes** (`str`): A string containing notes for the model request.

            Returns:
            - `ModelConfig.VertexAIModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            vertex_builder = ModelConfig.vertexai_builder()
            vertex_config = (
                vertex_builder
                .name("my-vertex-image-model")
                .request_model("imagegeneration@005")
                .notes("Requesting for internal testing of image generation capabilities.")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__notes = notes
            return self

        def _predict_url(self, url:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            self.__predict_url = url
            return self

        def _project_url(self, url:str) -> "ModelConfig.VertexAIModelConfigBuilder":
            self.__project_url = url
            return self

        def build(self, api_key:str) -> "ModelConfig":
            """
            Constructs a `ModelConfig` instance for a Vertex AI model request.

            This method uses all the settings previously configured on the builder
            to create a new `ModelConfig` object. The API key is required for
            potential validation steps during model configuration creation.

            Parameters:
            - **api_key** (`str`): The API key for BerryDB.

            Returns:
            - `ModelConfig`: A new `ModelConfig` instance configured for a Vertex AI model request.

            Example:
            ```python
            from berrydb import ModelConfig

            vertex_builder = ModelConfig.vertexai_builder()
            vertex_config = (
                vertex_builder
                .name("my-vertex-model-request")
                .request_model("gemini-pro")
                .notes("Requesting for text generation.")
                .build(api_key="BERRYDB_API_KEY") # Pass API key here
            )
            # vertex_config is now an instance of ModelConfig
            ```
            """
            return ModelConfig._create(
                provider=ModelProvider.VERTEX_AI_MODEL,
                _id=self.__id,
                _api_key=api_key,
                name=self.__name,
                request_model=self.__request_model,
                notes=self.__notes,
                _project_url=self.__project_url,
                _predict_url=self.__predict_url,
            )

    class BerryDBModelConfigBuilder:
        def __init__(self):
            self.__id = None
            self.__name = None
            self.__description = None
            self.__predict_url = None
            self.__project_url = None

        def _id(self, id:str) -> "ModelConfig.BerryDBModelConfigBuilder":
            self.__id = id
            return self

        def name(self, name:str) -> "ModelConfig.BerryDBModelConfigBuilder":
            """
            Sets the name for the BerryDB model configuration.

            This name is used to identify the model configuration within BerryDB.

            Parameters:
            - **name** (`str`): The desired name for the model configuration.

            Returns:
            - `ModelConfig.BerryDBModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            berrydb_builder = ModelConfig.berrydb_builder()
            berrydb_config = (
                berrydb_builder
                .name("my-internal-berrydb-model")
                .description("An internal model used for specific BerryDB tasks.")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__name = name
            return self

        def description(self, description:str) -> "ModelConfig.BerryDBModelConfigBuilder":
            """
            Sets the description for the BerryDB model configuration.

            This provides additional context or details about the internal model.

            Parameters:
            - **description** (`str`): The description string for the model configuration.

            Returns:
            - `ModelConfig.BerryDBModelConfigBuilder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import ModelConfig

            berrydb_builder = ModelConfig.berrydb_builder()
            berrydb_config = (
                berrydb_builder
                .name("my-internal-data-processor")
                .description("An internal model used for preprocessing specific datasets.")
                .build(api_key="BERRYDB_API_KEY")
            )
            ```
            """
            self.__description = description
            return self

        def _predict_url(self, url:str) -> "ModelConfig.BerryDBModelConfigBuilder":
            self.__predict_url = url
            return self

        def _project_url(self, url:str) -> "ModelConfig.BerryDBModelConfigBuilder":
            self.__project_url = url
            return self

        def build(self, api_key:str) -> "ModelConfig":
            """
            Constructs a `ModelConfig` instance for an internal BerryDB model.

            This method uses all the settings previously configured on the builder
            to create a new `ModelConfig` object. The API key is required for
            potential validation steps during model configuration creation.

            Parameters:
            - **api_key** (`str`): The API key for BerryDB.

            Returns:
            - `ModelConfig`: A new `ModelConfig` instance configured for an internal BerryDB model.

            Example:
            ```python
            from berrydb import ModelConfig

            berrydb_builder = ModelConfig.berrydb_builder()
            berrydb_config = (
                berrydb_builder
                .name("my-internal-model")
                .description("An internal model for BerryDB operations.")
                .build(api_key="BERRYDB_API_KEY") # This call creates the ModelConfig instance
            )
            # berrydb_config is now an instance of ModelConfig
            ```
            """
            return ModelConfig._create(
                provider=ModelProvider.BERRYDB_MODEL,
                _id=self.__id,
                _api_key=api_key,
                name=self.__name,
                description=self.__description,
                _predict_url=self.__predict_url,
                _project_url=self.__project_url,
            )
