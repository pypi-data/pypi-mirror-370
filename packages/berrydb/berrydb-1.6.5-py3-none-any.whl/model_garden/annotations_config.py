import requests
from typing import List, Dict, Optional

from utils.utils import Utils
import requests
from constants import constants as bdb_constants

class AnnotationsConfig:

    def __init__(
        self,
        name: str = None,
        input_transform_expression: str = None,
        output_transform_expression: str = None,
        additional_transform_expressions: Optional[List[Dict[str, str]]] = None,
        llm_provider: Optional[str] = bdb_constants.DEFAULT_PROVIDER,
        llm_model: Optional[str] = None,
        prompt: Optional[str] = None,
        id: Optional[str] = None
    ):
        # Validate mandatory fields
        if not (isinstance(name, str) and len(name.strip())):
            raise ValueError("name is required")
        if not input_transform_expression:
            raise ValueError("input_transform_expression is required")
        if not output_transform_expression:
            raise ValueError("output_transform_expression is required")

        # Validate additional_transform_expressions
        if additional_transform_expressions is not None and len(additional_transform_expressions) > 0:
            for idx, expr in enumerate(additional_transform_expressions):
                if not isinstance(expr, dict):
                    raise ValueError(f"additional_transform_expressions[{idx}] must be a dict")
                required_keys = {'expression', 'jsonPath'}
                if set(expr.keys()) != required_keys:
                    raise ValueError(
                        f"additional_transform_expressions[{idx}] must contain only 'expression' and 'jsonPath' keys"
                    )

        # Validate provider/model from metadata
        response = requests.get(bdb_constants.BERRY_GPT_BASE_URL + bdb_constants.chat_settings_metadata_url)
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        metadata = response.json()
        valid_providers = {p['value'] for p in metadata.get("chat_settings", {}).get("provider", [])}
        if llm_provider and llm_provider not in valid_providers:
            raise ValueError(f"Invalid llm_provider '{llm_provider}'. Choose from: {valid_providers}")

        valid_models = {m['value'] for m in metadata.get("chat_settings", {}).get("model", {}).get(llm_provider, [])}
        if llm_model and llm_model not in valid_models:
            raise ValueError(f"Invalid llm_model '{llm_model}' for provider '{llm_provider}'. Choose from: {valid_models}")

        self.input_transform_expression = input_transform_expression
        self.output_transform_expression = output_transform_expression
        self.additional_transform_expressions = additional_transform_expressions or []
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.prompt = prompt
        self.name = name
        self.id = id

    def save(self, berrydb_api_key: str):
        """
        Saves or updates the annotations configuration in BerryDB.

        Parameters:
        - **berrydb_api_key** (`str`): The API key for authenticating with BerryDB.

        Returns:
        - `AnnotationsConfig`: The `AnnotationsConfig` instance.

        Example:
        ```python
        from berrydb.model_garden.annotations_config import AnnotationsConfig

        # API key for BerryDB
        my_api_key = "YOUR_BERRYDB_API_KEY"

        # Example 1: Create and save a new annotations configuration
        new_config_builder = AnnotationsConfig.builder()
        new_config = (
            new_config_builder
            .name("my-ner-config")
            .input_transform_expression("data.text")
            .output_transform_expression("annotations.ner")
            .llm_provider("openai")
            .llm_model("gpt-4o-mini")
            .prompt("Extract named entities from the following text: {{input}}")
            .build()
        )
        # Save the new configuration to BerryDB
        saved_new_config = new_config.save(my_api_key)
        print(f"Saved new config with ID: {saved_new_config.id}")

        # Example 2: Get an existing configuration, modify, and save (update)
        existing_config_builder = AnnotationsConfig.get_config_as_builder(
            api_key=my_api_key,
            config_name="my-ner-config" # Assuming this config exists
        )
        existing_config = existing_config_builder.prompt(
            "Identify and label all persons, organizations, and locations in this text: {{input}}"
        ).build()

        # Update the configuration in BerryDB
        updated_config = existing_config.save(my_api_key)
        ```
        """
        data = {
            "inputTransformExpression": self.input_transform_expression,
            "outputTransformExpression": self.output_transform_expression,
            "additionalExpressions": self.additional_transform_expressions,
            "llmProvider": self.llm_provider,
            "llmModel": self.llm_model,
            "prompt": self.prompt,
            "name": self.name
        }
        headers = {"Content-Type": "application/json"}
        if self.id:
            url = f"{bdb_constants.BASE_URL + bdb_constants.annotation_configs}/{self.id}"
            params = {"apiKey": berrydb_api_key}
            if bdb_constants.debug_mode:
                print("url: ", url)
                print("params: ", params)
                print("data: ", data)
            response = requests.put(url, json=data, headers=headers, params=params)
        else:
            url = f"{bdb_constants.BASE_URL + bdb_constants.annotation_configs}"
            params = {"apiKey": berrydb_api_key}
            if bdb_constants.debug_mode:
                print("url: ", url)
                print("params: ", params)
                print("data: ", data)
            response = requests.post(url, json=data, headers=headers, params=params)
        if bdb_constants.debug_mode:
            print("response.status_code: ", response.status_code)
            print("response.text: ", response.text)

        if not (response.status_code == 200 or response.status_code == 201):
            Utils.handleApiCallFailure(response.json(), response.status_code)

        return self

    @staticmethod
    def get_config_as_builder(api_key: str, config_name: str) -> "AnnotationsConfig.Builder":
        """
        Retrieves an existing annotations configuration from BerryDB as a builder instance.

        This allows for easy modification of a previously saved configuration.

        Parameters:
        - **api_key** (`str`): The API key for authenticating with BerryDB.
        - **config_name** (`str`): The name of the annotations configuration to retrieve.

        Returns:
        - `AnnotationsConfig.Builder`: A builder instance pre-populated with the
          settings of the fetched configuration.

        Example:
        ```python
        from berrydb import AnnotationsConfig

        my_api_key = "YOUR_BERRYDB_API_KEY"
        existing_config_name = "my-ner-config" # Name of a config already in BerryDB

        # Get the existing config as a builder
        builder = AnnotationsConfig.get_config_as_builder(
            api_key=my_api_key,
            config_name=existing_config_name
        )

        # Now you can modify it, e.g., change the prompt
        modified_config = (
            builder
            .prompt("A new prompt for entity extraction: {{input}}")
            .build()
        )
        # modified_config.save(my_api_key) # And save the changes
        ```
        """
        url = f"{bdb_constants.BASE_URL + bdb_constants.annotation_configs}"
        params = {"apiKey": api_key, "name": config_name}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)

        data = response.json()
        if not (data and "annotationConfig" in data):
            raise Exception("Failed to fetch your annotations config, please try again later.")

        data = data["annotationConfig"]
        return AnnotationsConfig.builder()\
            .input_transform_expression(data.get("inputTransformExpression"))\
            .output_transform_expression(data.get("outputTransformExpression"))\
            .additional_transform_expressions(data.get("additionalTransformExpressions", []))\
            .llm_provider(data.get("llmProvider"))\
            .llm_model(data.get("llmModel"))\
            .prompt(data.get("prompt"))\
            .name(data.get("name"))\
            ._id(data.get("id"))

    @classmethod
    def builder(cls):
        """
        Returns a builder for creating `AnnotationsConfig` instances.

        This method provides a convenient way to construct an
        `AnnotationsConfig` object by incrementally setting its attributes.

        Returns:
        - `AnnotationsConfig.Builder`: An instance of the builder that can be
          used to set the attributes of an `AnnotationsConfig`.

        Example:
        ```python
        from berrydb.model_garden.annotations_config import AnnotationsConfig

        # Get a builder instance
        config_builder = AnnotationsConfig.builder()

        # Configure the annotations settings
        my_config = (
            config_builder
            .name("my-custom-annotation-config")
            .input_transform_expression("document.full_text")
            .output_transform_expression("annotations.entities")
            .llm_provider("openai")
            .llm_model("gpt-4o-mini")
            .prompt("Extract all named entities from the text: {{input}}")
            .additional_transform_expressions([
                {"jsonPath": "annotations.sentiment", "expression": "document.sentiment_score"}
            ])
            .build()
        )

        # The my_config object is now an instance of AnnotationsConfig
        # and can be used, for example, with its save() method.
        ```
        """
        return AnnotationsConfig.Builder()

    class Builder:
        def __init__(self):
            self.__input_transform_expression: Optional[str] = None
            self.__output_transform_expression: Optional[str] = None
            self.__additional_transform_expressions: Optional[List[Dict[str, str]]] = None
            self.__llm_provider: Optional[str] = bdb_constants.DEFAULT_PROVIDER
            self.__llm_model: Optional[str] = None
            self.__prompt: Optional[str] = None
            self.__name: Optional[str] = None
            self.__id: Optional[str] = None

        def input_transform_expression(self, jsonata_expr: str):
            """
            Sets the input transformation expression for the annotations configuration.

            This expression, written in JSONata, defines how to extract the input data
            (e.g., text to be annotated) from a source document or data structure.
            JSONata provides a powerful way to query and transform JSON-like data.

            Parameters:
            - **jsonata_expr** (`str`): The JSONata expression string.
              For example, `source_data.article_body` to extract the value of
              `article_body` from a `source_data` object, or more complex
              JSONata expressions for intricate transformations.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb.model_garden.annotations_config import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-config")
                .input_transform_expression("payload.document.text_content") # JSONata expression
                # ... other configurations ...
                .build()
            )
            ```
            """
            self.__input_transform_expression = jsonata_expr
            return self

        def output_transform_expression(self, jsonata_expr: str):
            """
            Sets the output transformation expression for the annotations configuration.

            This expression, written in JSONata, defines how to process and structure
            the output received from the model or LLM or other annotation source before it is
            stored. It maps the raw output into the desired annotation format.

            Parameters:
            - **jsonata_expr** (`str`): The JSONata expression string.
              For example, `llm_output.entities` to extract an 'entities' field
              from the LLM's output, or a more complex expression to reshape the data.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-annotation-processor")
                .output_transform_expression("llm_response.parsed_output.labels") # JSONata expression
                .input_transform_expression("document.text")
                # ... other configurations ...
                .build()
            )
            ```
            """
            self.__output_transform_expression = jsonata_expr
            return self

        def additional_transform_expressions(self, jsonata_expressions: List[Dict[str, str]]):
            """
            Sets a list of additional transformation expressions for the annotations configuration.

            These expressions, written in JSONata, allow you to apply further transformations
            to the data. This is applied when the annotation is being submitted to BerryDB.
            Each expression in the list should specify a `jsonPath` where the result of the
            `expression` should be placed in the final output structure.

            Parameters:
            - **jsonata_expressions** (`List[Dict[str, str]]`): A list of dictionaries. Each dictionary
              must contain two keys:
                - **'jsonPath'** (`str`): The JSONPath where the result of the expression should be placed.
                - **'expression'** (`str`): The JSONata expression to evaluate.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-complex-annotation-config")
                .input_transform_expression("document.text")
                .output_transform_expression("llm_response.main_result")
                .additional_transform_expressions([
                    {"jsonPath": "metadata.sentiment_score", "expression": "document.sentiment"},
                    {"jsonPath": "summary.length", "expression": "llm_response.summary ~> $length()"}
                ])
                .build()
            )
            ```
            """
            self.__additional_transform_expressions = jsonata_expressions
            return self

        def llm_provider(self, provider:str = bdb_constants.DEFAULT_PROVIDER):
            """
            Sets the Large Language Model (LLM) provider for the annotations configuration.

            This specifies which LLM provider (e.g., "openai", "anthropic") will be
            used if this configuration is leveraged.

            Parameters:
            - **provider** (`str`, optional): The name of the LLM provider.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config_with_openai = (
                builder
                .name("openai-config")
                .llm_provider("openai") # Explicitly set to OpenAI
                .llm_model("gpt-4o-mini") # A model from OpenAI
                .prompt("Extract entities: {{input}}")
                .input_transform_expression("data.text")
                .output_transform_expression("annotations.ner")
                .build()
            )

            builder_default_provider = AnnotationsConfig.builder()
            config_with_default = (
                builder_default_provider
                .name("default-provider-config")
                # .llm_provider() is not called, so it uses the default
                # .llm_model("some-default-model") # Uses default LLM model
                .prompt("Summarize: {{input}}")
                .input_transform_expression("data.text")
                .output_transform_expression("annotations.summary")
                .build()
            )
            ```
            """
            self.__llm_provider = provider
            return self

        def llm_model(self, model: str):
            """
            Sets the specific Large Language Model (LLM) to be used for the annotations configuration.

            This specifies the particular model (e.g., "gpt-4o-mini", "claude-3-opus-20240229")
            from the selected `llm_provider` that will be used if this configuration
            is leveraged for automated annotation generation.

            Ensure the chosen model is compatible with and available from the
            previously set `llm_provider`.

            Parameters:
            - **model** (`str`): The name or identifier of the LLM model.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-ner-config-with-specific-model")
                .llm_provider("openai")  # First, set the provider
                .llm_model("gpt-4o-mini") # Then, set the specific model from that provider
                .prompt("Extract all named entities from the following text: {{input}}")
                .input_transform_expression("data.text_content")
                .output_transform_expression("annotations.entities")
                .build()
            )
            ```
            """
            self.__llm_model = model
            return self

        def prompt(self, prompt: str):
            """
            Sets the prompt template for the LLM in the annotations configuration.

            This template defines the instructions and context provided to the
            Large Language Model (LLM).

            Parameters:
            - **prompt** (`str`): The prompt template string.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-entity-extraction-config")
                .prompt("Extract all person names and locations from the following text: {{input}}")
                .llm_provider("openai")
                .llm_model("gpt-4o-mini")
                .input_transform_expression("document.text_content")
                .output_transform_expression("annotations.extracted_entities")
                .build()
            )
            ```
            """
            self.__prompt = prompt
            return self

        def name(self, name: str):
            """
            Sets the name for the annotations configuration.

            Parameters:
            - **name** (`str`): The name of the configuration.

            Returns:
            - `AnnotationsConfig.Builder`: The builder instance, allowing for method chaining.

            Example:
            ```python
            from berrydb import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-new-config")
                # ... other configurations ...
                .build()
            )
            ```
            """
            self.__name = name
            return self

        def _id(self, id: str):
            self.__id = id
            return self

        def build(self, config_name:str|None = None):
            """
            Constructs an `AnnotationsConfig` instance using the configured settings.

            Parameters:
            - **config_name** (`str`, optional): An optional name for the configuration.
              If not provided, the name set using the `name()` builder method will be used.

            Returns:
            - `AnnotationsConfig`: A new `AnnotationsConfig` instance.

            Example:
            ```python
            from berrydb.model_garden.annotations_config import AnnotationsConfig

            builder = AnnotationsConfig.builder()
            config = (
                builder
                .name("my-final-config")
                # ... other configurations ...
                .build()
            )
            ```
            """
            return AnnotationsConfig(
                input_transform_expression=self.__input_transform_expression,
                output_transform_expression=self.__output_transform_expression,
                name=config_name or self.__name,
                additional_transform_expressions=self.__additional_transform_expressions,
                llm_provider=self.__llm_provider,
                llm_model=self.__llm_model,
                prompt=self.__prompt,
                id=self.__id
            )
