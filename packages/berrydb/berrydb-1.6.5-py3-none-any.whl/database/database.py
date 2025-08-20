import json
import logging
import os
import tempfile
import urllib.request
from urllib.parse import urlparse, unquote

import requests

import constants.constants as bdb_constants
from berrydb.berrydb_settings import Settings
from constants.constants import (ALZHEIMER_SE_TYPE,
                                 AUDIO_TRANSCRIPTION_SE_TYPE, FASHION_SE_TYPE,
                                 IMAGE_CAPTIONING_SE_TYPE,
                                 IMAGE_CLASSIFICATION_SE_TYPE, LOGGING_LEVEL,
                                 MEDICAL_NER_SE_TYPE, NER_SE_TYPE,
                                 PNEUMONIA_SE_TYPE, SEMANTICS_ANNOTATE_URL,
                                 SEMANTICS_PREDICT_URL,
                                 TEXT_CLASSIFICATION_SE_TYPE,
                                 TEXT_SUMMARIZATION_SE_TYPE,
                                 bulk_upsert_documents_url, caption_url,
                                 chat_with_database_url, debug_mode,
                                 document_by_id_url, documents_url,
                                 embed_database_url, extract_pdf_url, fts_url,
                                 label_summary_url, populate_upload_template_url, query_url,
                                 transcription_url, transcription_yt_url)
from utils.utils import Utils
from berrydb.IngestType import IngestType
from berrydb.IngestFileType import IngestFileType
from model_garden.model_provider import ModelProvider
from model_garden.model import BerryDBModel

logging.basicConfig(level=LOGGING_LEVEL,
                    format="%(asctime)s - %(levelname)s - %(message)s")


logger = logging.getLogger(__name__)


class Database:
    __api_key: str
    __bucket_name: str
    __database_name: str
    __org_name: str
    __settings: Settings

    def __init__(self, api_key: str, bucket_name: str, org_name: str, database_name: str):
        if api_key is None:
            Utils.print_error_and_exit("API Key cannot be None")
        if bucket_name is None:
            Utils.print_error_and_exit("Bucket name cannot be None")
        if org_name is None:
            Utils.print_error_and_exit("Organization name cannot be None")
        self.__api_key = api_key
        self.__bucket_name = bucket_name
        self.__database_name = database_name
        self.__org_name = org_name
        self.__settings = Settings.Builder().build()
        self.__settings_name = None

    def settings(self, settings: Settings | str) -> Settings:
        """
        .. note::
            Refer to the :ref:`Settings <settings>` documentation to learn how to create and save settings.
        .. #end

        **Example:**
        ```python
        # import Settings
        from berrydb import Settings

        settings = database.settings("settings-name")
        settings = database.settings(settings)
        ```
        ---
        """
        if settings is None:
            Utils.print_error_and_exit("Settings cannot be None")
        elif isinstance(settings, str):
            self.__settings_name = settings
            settings_obj = Settings.get(self.__api_key, settings)
            self.__settings = settings_obj
        elif isinstance(settings, Settings):
            self.__settings = settings
            self.__settings_name = None
        else:
            Utils.print_error_and_exit(
                "settings must be an instance of class Settings. import using 'from berrydb.settings import Settings'")
        return self.__settings

    def api_key(self):
        return self.__api_key

    def bucket_name(self):
        return self.__bucket_name

    def org_name(self):
        """To get the name of the organization of the connected database

        Args:
                No Arguments

        Returns:
                str: Get the organization ID of the connected database
        """
        return self.__org_name

    def database_name(self):
        """
        The `database_name` method retrieves the name of the currently connected database. This name is essential for identifying and working with the specific database in your system, especially when managing multiple databases.

        **Parameters**:
        - `None`: This method does not require any parameters to be passed.

        **Returns**:
        - `str`: A string representing the name of the connected database.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Retrieve the name of the connected database
        db_name = database.database_name()

        # Print the database name
        print(f"Connected to database: {db_name}")
        ```
        ---
        """
        return self.__database_name

    def get_all_documents(self, document_ids=None):
        """
        The `get_all_documents` method retrieves all documents in the currently connected database. This functionality allows users to access the entire dataset, which is useful for reviewing, processing, or analyzing the data in bulk.

        **Parameters**:
        - `None`: A list containing all documents from the connected database. Each document is typically represented as a dictionary, with key-value pairs corresponding to the document's fields and their respective values. If no documents are found, an empty list will be returned.

        **Returns**:
        - `List[Dict]`: A list of documents from the connected database.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)
        documents = database.get_all_documents()

        # Check if any documents were returned and print them
        if documents:
            print("Documents retrieved from the database:")
            for doc in documents:
                print(doc['BerryDb'])
        ```
        ---
        """

        url = bdb_constants.BASE_URL + documents_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseName": self.__database_name,
        }
        if document_ids is not None:
            if isinstance(document_ids, str):
                params['id'] = document_ids
            if isinstance(document_ids, list):
                params['id'] = ",".join(document_ids)

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            if debug_mode:
                print("documents result ", response.json())
            return json.loads(response.text)
        except Exception as e:
            print("Failed to fetch document: {}".format(str(e)))
            return []

    def get_all_documents_with_col_filter(self, col_filter=["*"]):
        """
        The `get_all_documents_with_col_filter` method retrieves documents from the currently connected database while applying a filter to specify which columns should be included in the returned documents. This method is useful for narrowing down the data returned, allowing you to focus on specific fields of interest.

        **Parameters**:
        - **col_filter** (`list`, optional): A list of column names to filter the documents. If no specific columns are provided, the method defaults to ["*"], which retrieves all columns for each document. You can specify column names as strings (e.g., ["name", "age"]) to limit the returned fields.

        **Returns**:
        - `List[Dict]`:  list of documents from the connected database, with each document being represented as a dictionary. The returned documents will only include the columns specified in the col_filter. If no documents match the criteria or if the database is empty, an empty list will be returned.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)
        column_filter = ["name", "age"]  # Specify columns to retrieve
        filtered_documents = database.get_all_documents_with_col_filter(column_filter)
        ```

        ---
        """

        url = bdb_constants.BASE_URL + documents_url

        url += "?apiKey=" + self.__api_key
        url += "&bucket=" + self.__bucket_name
        url += "&databaseName=" + str(self.__database_name)
        url += "&columns=" + (",".join(col_filter))

        if debug_mode:
            print("url:", url)
        try:
            response = requests.get(url)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            if debug_mode:
                print("documents result ", response.json())
            # return response.json()
            return json.loads(response.text)
        except Exception as e:
            print("Failed to fetch document: {}".format(str(e)))
            return []

    def get_document_by_object_id(
        self,
        document_id,
        key_name=None,
        key_value=None,
    ):
        """
        The `get_document_by_object_id` method retrieves documents from the connected database using a specified object/document ID. This method can also apply additional filtering based on an optional key-value pair, allowing for more precise data retrieval. It is useful for locating specific documents or for filtering results based on certain criteria.

        **Parameters**:
        - **document_id** (`str`): The unique key or ID of the document you wish to retrieve. This identifier should correspond to an existing document in the connected database.
        - **key_name** (`str`, optional): The name of an optional key to filter the documents further. If provided, the method will return documents that match both the `document_id` and the specified key.
        - **key_value** (`str`, optional): The value associated with the `key_name` that you want to filter by. This value should match the corresponding field in the document. If not specified, only the `document_id` will be used for retrieval.


        **Returns**:
        - `List[Dict]`: A list of documents that match the provided document_id or the additional filters. If no documents are found, an empty list will be returned.

        **Example**
        ```python
        document_id = "DOCUMENT_ID"
        key_name = "status"
        key_value = "active"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Retrieve documents based on the document ID and optional filters
        matching_documents = database.get_document_by_object_id(document_id, key_name, key_value)

        if matching_documents:
            print("Documents retrieved:")
            for doc in matching_documents:
                # Do operations here
                print(doc)
        ```
        ---
        """

        from urllib.parse import quote
        url = bdb_constants.BASE_URL + \
            document_by_id_url.format(quote(document_id))
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseName": self.__database_name,
        }

        if document_id is not None:
            params["docId"] = document_id
        if key_name is not None:
            params["keyName"] = key_name
        if key_value is not None:
            params["keyValue"] = key_value

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.text, response.status_code)
            jsonRes = response.json()
            if debug_mode:
                print("docById result ", jsonRes)
            return jsonRes
        except Exception as e:
            print("Failed to fetch document by id {} : {}".format(
                document_id, str(e)))
            return ""

    def query(self, query: str):
        """
        The `query` method allows users to execute SQL-like queries on the currently connected database. This method provides powerful capabilities for retrieving specific documents based on various conditions, making it essential for data retrieval and analysis.

        **Parameters**:
        - **query** (`str`): An SQL-like query string that defines the criteria for retrieving documents from the database. The query can include various clauses such as SELECT, WHERE, ORDER BY, and other SQL commands supported by the database.

        **Returns**:
        - `List[Dict]`: A list of documents that match the criteria specified in the query. Each document is represented as a dictionary, containing key-value pairs corresponding to the document's fields. If no documents match the query, an empty list will be returned.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)
        database_id = database.databaseId()
        query_string = f'SELECT * FROM `BerryDB` WHERE databaseId = "{database_id}" age > 30 ORDER BY name'

        # Run the query on the database
        results = database.query(query_string)

        if results:
            print("Documents retrieved from the database:")
            for doc in results:
                # Do operations here
                print(doc)
        ```
        ---
        """

        url = bdb_constants.BASE_URL + query_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseName": self.__database_name,
        }
        payload = {"query": query}

        if debug_mode:
            print("url:", url)
            print("params:", params)
            print("payload:", payload)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(
                url, json=payload, headers=headers, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            if debug_mode:
                print("query result ", response.json())
            return json.loads(response.text)
        except Exception as e:
            print("Failed to query : {}".format(str(e)))
            return ""

    def __upsert(self, documents) -> str:
        url = bdb_constants.BASE_URL + bulk_upsert_documents_url
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseName": self.__database_name,
        }

        payload = json.dumps(documents)
        if debug_mode:
            print("url:", url)
            print("payload:", payload)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(
                url, data=payload, headers=headers, params=params)
            if response.status_code != 200:
                try:
                    resp_content = response.json()
                except ValueError:
                    resp_content = response.text
                Utils.handleApiCallFailure(resp_content, response.status_code)
            if debug_mode:
                print("upsert result ", response)
            return response.text
        except Exception as e:
            print("Failed to upsert document: {}".format(str(e)))
            return ""

    def upsert(self, documents) -> str:
        """
        The upsert method allows users to add new documents to the connected database or update existing documents if they already exist. This functionality is useful for maintaining up-to-date records without the need to manually check for existing documents.

        .. note::
            To update a document in the database, the document must contain a key called `id` that matches the ID of the document being edited. Additionally, the document must belong to the currently connected database, which should be part of the organization. If the key `id` is not present, a random string will be assigned as its identifier and a new document/record is created in the connected database. It is recommended that the "id" key not be included in the documents when creating new entries in the connected database. Allow BerryDB to handle ID creation to prevent clashes and avoid overwriting or inadvertently updating existing documents.
        .. #end

        **Parameters**:
        - **documents** (`List[Dict]`): A list of document objects to add or update. Each document should have a key `"id"`; if not, a random string will be assigned.

        .. note::
            It is recommended that the "id" key not be included in the documents when creating new entries in the connected database. Allow BerryDB to handle ID creation to prevent clashes and avoid overwriting or inadvertently updating existing documents.
        .. #end

        **Returns**:
        - `str`: A message indicating the outcome of the operation. This message will specify whether the operation was successful or if there was a failure, providing context for any issues encountered.

        **Example**
        ```python
        documents_to_upsert = [
            {"id": "doc_1", "name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}  # This document will be assigned a random ID
        ]

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Add or update the documents in the database
        result = database.upsert(documents_to_upsert)

        print(result)
        ```
        ---
        """
        try:
            if type(documents) != list:
                documents = [documents]
            return self.__upsert(documents)
        except Exception as e:
            print("Failed to upsert documents: {}".format(str(e)))
            return ""

    def delete_document(self, document_id):
        """
        The `deleteDocument` method allows users to permanently remove a document from the connected database using its unique identifier. This action is irreversible, so caution should be exercised when deleting documents to avoid unintentional data loss.

        **Parameters**:
        - **document_id** (`str`): The unique identifier of the document to be deleted. This ID must correspond to an existing document within the connected database.

        **Returns**:
        - `str`: A message indicating the outcome of the deletion operation. The message will confirm whether the document was successfully deleted or provide details in case of a failure.

        **Example**
        ```python
        document_id = "DOCUMENT_ID"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Delete the specified document
        result = database.deleteDocument(document_id)

        print(result)
        ```
        ---
        """

        from urllib.parse import quote
        url = bdb_constants.BASE_URL + \
            document_by_id_url.format(quote(document_id))
        params = {
            "apiKey": self.__api_key,
            "bucket": self.__bucket_name,
            "databaseName": self.__database_name,
        }

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.delete(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            jsonRes = response.text
            if debug_mode:
                print("Delete document result ", jsonRes)
            return jsonRes
        except Exception as e:
            print("Failed to delete document by id {}, reason : {}".format(
                document_id, str(e)))
            return ""

    # def transcribe(self, video_url: str):
    #     url = bdb_constants.ML_BACKEND_BASE_URL + transcription_url

    #     body = {
    #         "url": video_url,
    #     }

    #     payload = json.dumps(body)
    #     if debug_mode:
    #         print("url:", url)
    #         print("payload:", payload)
    #     headers = Utils.get_headers(self.__api_key)

    #     try:
    #         response = requests.post(url, headers=headers, data=payload)
    #         if response.status_code != 200:
    #             Utils.handleApiCallFailure(response.json(), response.status_code)
    #         res = response.text
    #         if debug_mode:
    #             print("Transcription result: ", res)
    #         return res
    #     except Exception as e:
    #         print(f"Failed to get transcription for the url {video_url}, reason : {str(e)}")
    #         return ""

    def transcribe_yt(self, video_url: str):

        url = bdb_constants.ML_BACKEND_BASE_URL + transcription_yt_url

        body = {
            "url": video_url,
        }

        payload = json.dumps(body)
        if debug_mode:
            print("url:", url)
            print("payload:", payload)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            res = response.text
            if debug_mode:
                print("Youtube transcription result: ", res)
            return res
        except Exception as e:
            print(
                f"Failed to get transcription for the youtube url {video_url}, reason : {str(e)}")
            return ""

    def caption(self, image_url: str):
        url = bdb_constants.ML_BACKEND_BASE_URL + caption_url

        body = {
            "url": image_url,
        }

        payload = json.dumps(body)
        if debug_mode:
            print("url:", url)
            print("payload:", payload)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            res = response.text
            if debug_mode:
                print("Caption result: ", res)
            return res
        except Exception as e:
            print(
                f"Failed to get caption for the url {image_url}, reason : {str(e)}")
            return ""

    def enable_fts(self, fields=None, override=False):
        """Creates a new full-text search (FTS) index on the database.

        Args:
                fields (list): List of fields (JSON paths) to build the index on. If empty, the index fields set on the schema is considered
                override (bool): If True, replaces any existing index

        Returns:
                FTS: An instance of FTS object
        """
        from fts.fts import FTS

        url = bdb_constants.BASE_URL + fts_url

        params = {
            "databaseName": self.__database_name,
            "apiKey": self.__api_key,
        }

        body = {
            "fields": fields,
            "override": override,
        }
        payload = json.dumps(body)

        if debug_mode:
            print("url:", url)
            print("params:", params)
            print("payload:", payload)

        try:
            response = requests.post(url, params=params, data=payload, headers={
                                     'Content-Type': 'application/json'})

            if response.status_code != 201:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)

            res = response.json()
            if debug_mode:
                print("FTS result: ", res)

            return FTS(self.__api_key, self.__database_name, res['indexedFields'])
        except Exception as e:
            errMsg = "Failed to enable FTS"
            print(f"{errMsg}, reason : {str(e)}")
            return

    def embed(
        self,
        embedding_api_key: str,
    ):
        """
        The `embed` method allows users to generate embeddings for the documents in the database using a specified embedding function, often powered by an OpenAI language model. This is useful for tasks such as similarity search, clustering, or any application that requires semantic understanding of the data.

        **Parameters**:
        - **open_ai_api_key** (`str`): The API key used to authenticate requests to the OpenAI API. This key must be valid and associated with your OpenAI account.

        **Returns**:
        - `str`: A message indicating the success or failure of the embedding operation. This message will provide context for any errors encountered during the process.

        **Example**
        ```python
        open_ai_api_key = "YOUR_OPENAI_API_KEY"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Embed the documents in the database
        result = database.embed(
            open_ai_api_key=open_ai_api_key
        )

        print(result)
        ```
        ---
        """

        url = bdb_constants.BERRY_GPT_BASE_URL + embed_database_url

        body = {
            "database": self.__database_name,
            "apiKey": self.__api_key,
            "orgName": self.__org_name,
            "llmApiKey": embedding_api_key,
            "settingsName": self.__settings_name,
            "embeddingApiKey": embedding_api_key,
        }
        if self.__settings_name is None:
            body["settings"] = self.__settings.__dict__

        if debug_mode:
            print("url:", url)
            print("body:", body)
        payload = json.dumps(body)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            res = response.json()
            if debug_mode:
                print("Embed result: ", res)
            return res
        except Exception as e:
            errMsg = "Failed to embed the database. Please try again later."
            print(f"{errMsg}, reason : {str(e)}")
            raise e

    def chat(
        self,
        llm_api_key: str,
        question: str,
        embedding_model_api_key: str | None = None,
    ):
        """
        The `chat` method is designed to query a database using a language model (LLM). This method takes a user-defined question and returns an answer generated by the LLM, allowing for interaction with the database in a conversational manner.

        **Parameters**:
        - **llm_api_key** (`str`): The API key used to authenticate requests to the LLM provider.
        - **question** (`str`): The query or question that you want to ask regarding the database. This can be a natural language question or a specific request for information.
        - **embedding_model_api_key** (`str`, optional): The API key/token of your embedding model (Only used if the embedding and chat providers do not match)

        **Returns**:
        - `str`: The generated answer to the query or an error message if the operation fails.

        **Example**
        ```python
        llm_api_key = "OPENAI_API_KEY"
        question = "What are the benefits of using machine learning?"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Get answers from the database using the OpenAI API
        response = database.chat(
            llm_api_key=llm_api_key,
            question=question
        )

        print(f"Response: {response}")
        ```
        ---
        """

        url = bdb_constants.BERRY_GPT_BASE_URL + chat_with_database_url

        body = {
            key: value
            for key, value in {
                "question": question,
                "apiKey": self.__api_key,
                "database": self.__database_name,
                "orgName": self.__org_name,
                "llmApiKey": llm_api_key,
                "embeddingApiKey": embedding_model_api_key,
                "settingsName": self.__settings_name,
            }.items()
            if value is not None
        }
        if self.__settings_name is None:
            body["settings"] = self.__settings.__dict__

        if debug_mode:
            print("url:", url)
            print("body:", body)
        payload = json.dumps(body)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            res = response.json()
            if debug_mode:
                print("Database chat result: ", res)
            return res['answer']
        except Exception as e:
            errMsg = "Failed to chat with the database. Please try again later."
            print(f"{errMsg}, reason : {str(e)}")
            raise e

    def chat_for_eval(
        self,
        llm_api_key: str,
        question: str,
        embedding_model_api_key: str | None = None,
    ) -> dict:
        """
        The `chat_for_eval` method is designed to query a database using a language model (LLM) and also trace the LLM responses for . This method takes a user-defined question and returns an answer generated by the LLM, allowing for interaction with the database in a conversational manner.

        **Parameters**:
        - **llm_api_key** (`str`): The API key used to authenticate requests to the LLM provider.
        - **question** (`str`): The query or question that you want to ask regarding the database. This can be a natural language question or a specific request for information.
        - **embedding_model_api_key** (`str`, optional): The API key/token of your embedding model (Only used if the embedding and chat providers do not match)

        **Returns**:
        - `dict`: A dictionary containing the generated answer along with the documents used as context for the response, or an error message if the operation fails.

        **Example**
        ```python
        llm_api_key = "OPENAI_API_KEY"
        question = "What are the benefits of using machine learning?"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Get answers from the database using the LLM API
        response = database.chat_for_eval(
            llm_api_key=llm_api_key,
            question=question,
        )

        print(f"Response: {response['answer']}")
        ```
        ---
        """

        url = bdb_constants.BERRY_GPT_BASE_URL + chat_with_database_url

        body = {
            key: value
            for key, value in {
                "question": question,
                "database": self.__database_name,
                "orgName": self.__org_name,
                "apiKey": self.__api_key,
                "llmApiKey": llm_api_key,
                "embeddingApiKey": embedding_model_api_key,
                "settingsName": self.__settings_name,
            }.items()
            if value is not None
        }
        if self.__settings_name is None:
            body["settings"] = self.__settings.__dict__

        if debug_mode:
            print("url:", url)
            print("body:", body)
        payload = json.dumps(body)
        headers = Utils.get_headers(self.__api_key)

        try:
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)
            res = response.json()
            if debug_mode:
                print("Database chat result: ", res)
            return res
        except Exception as e:
            errMsg = "Failed to chat with the database. Please try again later."
            print(f"{errMsg}, reason : {str(e)}")
            raise e

    def similarity_search(self, llm_api_key: str, query: str):
        """
        Performs a search of the database and returns a list of documents based on the query and the configured settings

        **Parameters**:
        - **llm_api_key** (`str`): The API key used to authenticate requests to the LLM provider.
        - **query** (`str`): The query or question that you want to ask regarding the database. This can be a natural language question or a specific request for information.

        **Returns**:
        - `dict`: A list of documents.

        **Example**
        ```python
        llm_api_key = "OPENAI_API_KEY"
        query = "What are the benefits of using machine learning?"

        # 'database' as an instance of the connected database (See connect/create_database methods)
        # Get a list of matching documents for the database
        response = database.similarity_search(
            llm_api_key=llm_api_key,
            query=query,
        )
        results = response['results']
        print("vectorDocuments", res['vector'])
        print("ftsDocuments", res['fts'])
        print("keywordSearchDocuments", res['keyword_search'])
        ```

        .. seealso::
            Refer to the :ref:`Settings <settings>` documentation to learn how to create and save settings.
        """
        url = bdb_constants.BERRY_GPT_BASE_URL + bdb_constants.similarity_search_url
        body = {
            "question": query,
            "database": self.__database_name,
            "orgName": self.__org_name,
            "apiKey": self.__api_key,
            "llmApiKey": llm_api_key,
            "embeddingApiKey": llm_api_key,
            "settingsName": self.__settings_name,
        }
        if self.__settings_name is None:
            body["settings"] = self.__settings.__dict__

        if debug_mode:
            print("url:", url)
            print("body:", body)
        payload = json.dumps(body)
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            Utils.handleApiCallFailure(response.json(), response.status_code)
        return response.json()

    def ingest_pdf(self, file_list, extract_json_path=None):
        """
        The `ingest_pdf` method processes a list of PDF files, extracting their content and adding the documents into the connected database. The extracted data can optionally be saved to a specified JSON path depending on your need and schema design.

        **Parameters**:
        - **file_list** (`list[File]`): A list of PDF files to be processed. Each file in the list should be a valid PDF object that can be ingested and parsed
        - **extract_json_path** (`str`, optional): The JSON path where the extracted data should be added in the JSON document. If not provided, the extracted data will be stored under the 'content' field by default

        **Returns**:
        - `List[Dict]`: Returns a list of extracted documents, with each document represented as a dictionary containing the extracted content.

        **Example**
        ```python
        file_list = ["file1.pdf", "file2.pdf"]  # List of PDF files to ingest
        extract_json_path = "content"  # Optional path to save extracted data (Default: "content")
        # If for example the extract_json_path = "content", the extracted text is in the key "content.text"
        # "content" key will be of type 'dict'

        # 'database' as an instance of the connected database (See connect/create_database methods)
        extracted_documents = database.ingest_pdf(
            file_list=file_list,
            extract_json_path=extract_json_path
        )

        # Print the documents
        for doc in extracted_documents:
            print(doc)
        ```
        ---
        """
        try:
            if type(file_list) is str:
                file_list = [file_list]
            if not file_list or not len(file_list):
                raise ValueError("At least one file must be provided")
            if len(file_list) > 5:
                raise ValueError("Exceeded maximum allowed files (5)")

            for file in file_list:
                if not file.endswith(".pdf"):
                    raise ValueError("All files must be of type PDF")

            extract_json_path = extract_json_path or "content"

            Utils.validate_json_path(extract_json_path)

            files = []
            for file_path in file_list:
                files.append(("files", open(file_path, "rb")))

            url = bdb_constants.BERRY_GPT_BASE_URL + extract_pdf_url

            params = {
                "databaseName": self.__database_name,
                "apiKey": self.__api_key,
                "extractJsonPath": extract_json_path,
            }

            if debug_mode:
                print("url:", url)
                print("params:", params)

            response = requests.post(url, files=files, params=params)

            if response.status_code == 200:
                print("Success")
                response_json = response.json()
                if response_json["success"]:
                    return response_json["message"]
            else:
                print(
                    f"Failed with ingest PDFs, status code: {response.status_code}")
        except Exception as e:
            print(f"Failed with ingest PDFs, reason: {e}")
            if debug_mode:
                raise e

    def add_annotations(self, document_id: str, annotations: list[dict], task: str, annotated_field: str) -> str | None:
        """
        Adds/updates a list of annotations in a specific document in the database.

        This method allows you to associate structured annotation data with an existing
        document identified by its `document_id`. The annotations are provided as a
        list of dictionaries, where each dictionary represents a single annotation.

        Parameters:
        - **annotations** (`list[dict]`): A non-empty list of dictionaries, where each
          dictionary represents an annotation to be added/updated in the document. The structure
          of these dictionaries should conform to your annotation schema.
        - **document_id** (`str`): The unique identifier of the document to which the
          annotations will be added. This cannot be None or an empty string.

        Returns:
        - `str`: A success message from the API if the annotations are added successfully.
        - `None`: If the operation fails due to validation errors, API issues, or network problems.

        Raises:
        - `ValueError`: If `annotations` is not a non-empty list or `document_id` is invalid.
        """
        if not isinstance(annotations, list) or not annotations:
            raise ValueError(
                "annotations must be a non-empty list of dictionaries.")
        if not document_id or not isinstance(document_id, str):
            raise ValueError(
                "document_id cannot be None or empty and must be a string.")

        url = bdb_constants.BASE_URL + \
            bdb_constants.upsert_annotations_url.format(document_id)
        params = {
            "apiKey": self.__api_key,
            "databaseName": self.__database_name,
        }

        payload = {"annotations": annotations,
                   "task": task, "annotatedField": annotated_field}
        payload = json.dumps(payload)
        headers = Utils.get_headers(self.__api_key)

        if debug_mode:
            print(f"url: {url}")
            print(f"params: {params}")
            print(f"payload: {payload}")

        try:
            response = requests.post(
                url, data=payload, headers=headers, params=params)
            response_json = response.json()
            if response.status_code != 200:
                Utils.handleApiCallFailure(response_json, response.status_code)

            if debug_mode:
                print(f"add_annotations result: {response_json}")

            if "message" in response_json:
                print(f"{response_json['message']}")
                return response_json["message"]
            else:
                print("Successfully added annotations.")
                return json.dumps(response_json)
        except Exception as e:
            logger.error(
                f"Failed to add annotations for document ID '{document_id}', reason: {str(e)}")
            return None

    # Sematic Extraction methods
    def ner(self, json_path, document_ids=[], annotate=False):
        """
        The `ner` (Named Entity Recognition) method processes the text in JSON path and extracts semantic data from specified documents. This method can also optionally annotate the extracted semantic data back into the documents. The return value varies based on annotate flag. Please refer to the example for a clearer understanding.

        **Parameters**:
        - **json_path** (`str`): The JSON path to the key containing the text for which Named Entity Recognition (NER) should be performed
        -  **document_ids** (`list`, optional): A list of document IDs representing the specific documents you want to extract semantic data from. If annotate is False and no document IDs are provided, a validation error will be raised
        -   **annotate** (`str`, optional): A flag indicating whether to add the extracted semantic data back into the original documents as annotations. Defaults to False. If True, the method will return a hash representing the annotated document; otherwise, it returns the predictions for the specified document IDs

        **Returns**:
        - If `annotate` is `True`:
        - A hash to track the status of the job.
        - If `annotate` is `False`:
        -  A dictionary with keys corresponding to the individual document IDs specified in 'document_ids,' and the predictions as their values.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)

        # Scenario 1: annotate = True
        # If the 'document_ids' parameter is not specified, Named Entity Recognition (NER) will be performed on all documents in the database. If specific document IDs are provided, NER will only be applied to those documents. The predictions will then be added to the individual items within the specified documents. This process is executed asynchronously, so it may take some time for the predictions to appear in the documents. The returned hash can be used to track the status of the job however, this feature is not yet functional and will be implemented in the near future.
        document_ids = ["doc-1", "doc-2"] # (Optional)
        hash = database.ner(
                json_path=json_path,
                document_ids=document_ids,
                annotate=True
            )

        # Scenario 2: annotate = False
        # A list of document IDs in the 'document_ids' parameter is required. If 'annotate' is set to False, the predictions are returned as a dict, with the keys corresponding to the individual document IDs specified in 'document_ids.' These predictions are not automatically added to the documents in the database, instead they should be added into the respective documents using the upsert or query APIs (an example using query is provided below).
        document_ids = ["doc-3", "doc-4"]
        predictions = database.ner(
                json_path=json_path,
                document_ids=document_ids,
                annotate=False
            )

        def upsert_annotation_to_document(database_id, document_id, annotation):
        query = f'UPDATE `BerryDb` SET annotations = CASE WHEN ARRAY_LENGTH(annotations) > 0 THEN ARRAY_APPEND(annotations, {annotation}) ELSE [{annotation}] END WHERE databaseId = "{database_id}" AND id = "{document_id}"'
        print("Adding annotation to document with ID: ", document_id)
        database.query(query)

        for doc_id in predictions:
        upsert_annotation_to_document(database.databaseId(), doc_id, predictions[doc_id])
        ```
        ---
        """
        extraction_type = NER_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def medical_ner(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = MEDICAL_NER_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def text_summarization(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = TEXT_SUMMARIZATION_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def image_classification(self, json_path, labels, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): Labels for the classification of text
                arg3 (str): document IDs of the documents you want to extract the data of (optional)
                arg4 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = IMAGE_CLASSIFICATION_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, labels, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def image_captioning(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = IMAGE_CAPTIONING_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def pneumonia_detection(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = PNEUMONIA_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def alzheimer_detection(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = ALZHEIMER_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def fashion(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = FASHION_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def audio_transcription(self, json_path, document_ids=[], annotate=False):
        """Function summary

        Args:
                arg1 (str): JSON path to the object you want to extract semantic for
                arg2 (str): document IDs of the documents you want to extract the data of (optional)
                arg3 (str): Add sematic data to the document (optional)

        Returns:
                list | str: sematic data | hash
        """
        extraction_type = AUDIO_TRANSCRIPTION_SE_TYPE
        try:
            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, None, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def text_classification(self, json_path, labels, document_ids=[], annotate=False):
        """
        The `text_classification` method processes the text in JSON path and extracts semantic data from specified documents. This method can also optionally annotate the extracted semantic data back into the documents. The return value varies based on annotate flag. Please refer to the example for a clearer understanding.

        **Parameters**:
        - **json_path** (`str`): The JSON path to the key containing the text for which classification should be performed
        - **labels** (`list[str]`): A list of strings representing the categories or classes for text classification, with a maximum of 10 labels allowed
        - **document_ids** (`list`, optional): A list of document IDs representing the specific documents you want to extract semantic data from. If annotate is False and no document IDs are provided, a validation error will be raised
        - **annotate** (`str`, optional): A flag indicating whether to add the extracted semantic data back into the original documents as annotations. Defaults to False. If True, the method will return a hash representing the annotated document; otherwise, it returns the predictions for the specified document IDs

        **Returns**:
        - If `annotate` is `True`:
        - A hash to track the status of the job.
        - If `annotate` is `False`:
        -  A dictionary with keys corresponding to the individual document IDs specified in 'document_ids,' and the predictions as their values.

        **Example**
        ```python
        # 'database' as an instance of the connected database (See connect/create_database methods)

        # Scenario 1: annotate = True
        # If the 'document_ids' parameter is not specified, Text Classification will be performed on all documents in the database. If specific document IDs are provided, Text Classification will only be applied to those documents. The predictions will then be added to the individual items within the specified documents. This process is executed asynchronously, so it may take some time for the predictions to appear in the documents. The returned hash can be used to track the status of the job however, this feature is not yet functional and will be implemented in the near future.
        document_ids = ["doc-1", "doc-2"] # (Optional)
        hash = database.text_classification(
                json_path=json_path,
                labels=['POSITIVE', 'NEGATIVE', 'NEUTRAL']
                document_ids=document_ids,
                annotate=True
            )

        # Scenario 2: annotate = False
        # A list of document IDs in the 'document_ids' parameter is required. If 'annotate' is set to False, the predictions are returned as a dict, with the keys corresponding to the individual document IDs specified in 'document_ids.' These predictions are not automatically added to the documents in the database, instead they should be added into the respective documents using the upsert or query APIs (an example using query is provided below).
        document_ids = ["doc-3", "doc-4"]
        predictions = database.text_classification(
                json_path=json_path,
                labels=['POSITIVE', 'NEGATIVE', 'NEUTRAL']
                document_ids=document_ids,
                annotate=False
            )

        def upsert_annotation_to_document(database_id, document_id, annotation):
        query = f'UPDATE `BerryDb` SET annotations = CASE WHEN ARRAY_LENGTH(annotations) > 0 THEN ARRAY_APPEND(annotations, {annotation}) ELSE [{annotation}] END WHERE databaseId = "{database_id}" AND id = "{document_id}"'
        print("Adding annotation to document with ID: ", document_id)
        database.query(query)

        for doc_id in predictions:
        upsert_annotation_to_document(database.databaseId(), doc_id, predictions[doc_id])
        ```
        ---
        """
        extraction_type = TEXT_CLASSIFICATION_SE_TYPE
        if not (labels and len(labels)):
            raise ValueError(
                f"Labels are required for {extraction_type} to classify the text.")
        try:

            return self.__semantic_extraction_base(extraction_type, json_path, document_ids, labels, annotate)

        except Exception as e:
            logger.exception("Failed to extract semantics for {}, reason: {}".format(
                extraction_type, str(e)))
            raise e

    def __semantic_extraction_base(self, extraction_type, json_path, document_ids=None, labels=None, annotate=False):

        if not json_path:
            raise ValueError("JSON path is required")
        if not annotate and not (document_ids and len(document_ids)):
            raise ValueError(
                "Document IDs are required if you are not annotating the document")

        url = bdb_constants.BASE_URL + SEMANTICS_PREDICT_URL
        if annotate:
            url = bdb_constants.BASE_URL + SEMANTICS_ANNOTATE_URL

        params = {
            "apiKey": self.__api_key,
        }

        body = {
            "databaseName": self.__database_name,
            "documentIds": document_ids,
            "extract": extraction_type,
            "jsonPath": json_path,
        }

        if labels and len(labels):
            body["labels"] = labels

        payload = json.dumps(body)
        headers = Utils.get_headers(self.__api_key)

        logger.debug(f"url:{url}")
        logger.debug(f"params: {repr(params)}")
        logger.debug(f"payload: {payload}")
        logger.debug(f"headers: {repr(headers)}")

        if not annotate:
            print("Retrieving predictions for documents with IDs ", document_ids)
        from requests import Response
        response: Response = requests.post(
            url, params=params, data=payload, headers=headers)

        if response.status_code == 200:
            if not annotate:
                print("Predictions retrieved Successfully!")
            return response.json()

        if not annotate:
            print("Failed to retrieve predictions!")
        Utils.handleApiCallFailure(response.json(), response.status_code)

    def label_summary(self):
        url = bdb_constants.ML_BACKEND_BASE_URL + label_summary_url
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "databaseName": self.database_name(),
            "apiKey": self.api_key()
        }

        try:
            print("Starting to summarize labels for database: ",
                  self.database_name())
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)

            print("Response:", response.json())
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error while summarizing database: {e}")
            return None

    def transcribe(self, json_path: str, document_ids: list[str] = None):
        """
        Transcribes audio for documents using the configured BerryDB model.

        This method fetches documents (all or by IDs), reads an audio URL from the
        provided JSON path, and invokes the BerryDB audio transcription model. The
        resulting transcription is added as an annotation to each processed document.

        **Parameters**:
        - json_path (`str`): JSON path pointing to the field that contains the audio URL
          in each document. Must not be empty.
        - document_ids (`list[str]` | None): Optional list of document IDs to limit
          processing. If not provided, all documents in the database are processed.

        **Returns**:
        - `None`: Annotations are written back to the database; no value is returned.

        **Example**:
        ```python
        # Transcribe audio for all documents using the field 'media.audioUrl'
        database.transcribe(json_path="media.audioUrl")

        # Transcribe audio for specific documents only
        database.transcribe(json_path="media.audioUrl", document_ids=["doc-1", "doc-2"])
        ```
        ---
        """
        if json_path is None or len(json_path) == 0:
            raise ValueError("JSON path is required")

        from model_garden.model_repo import ModelRepo
        model_repo = ModelRepo(self.__api_key)

        if not document_ids:
            documents = self.get_all_documents()
        else:
            documents = self.get_all_documents(document_ids=document_ids)

        model = model_repo.get_by_name(
            'audio-transcription', ModelProvider.BERRYDB_MODEL)

        for doc in documents:
            audio_url = Utils.get_value_from_json_path(doc, json_path)
            if audio_url is None:
                print(
                    f"Skipping document with id {doc['id']} because json_path {json_path} not found")
                continue
            prediction = model.predict({"audioUrl": audio_url})
            self.add_annotations(
                doc['id'], [prediction], 'speech transcription', json_path)

    def analyze_sentiment(self, json_path: str, document_ids: list[str] = None):
        """
        Performs audio sentiment analysis using the configured BerryDB model.

        This method fetches documents (all or by IDs), reads an audio URL from the
        provided JSON path, runs the sentiment analysis model, and writes the
        prediction back as an annotation on each processed document.

        **Parameters**:
        - json_path (`str`): JSON path pointing to the field that contains the audio URL
          in each document. Must not be empty.
        - document_ids (`list[str]` | None): Optional list of document IDs to limit
          processing. If not provided, all documents in the database are processed.

        **Returns**:
        - `None`: Annotations are written back to the database; no value is returned.

        **Example**:
        ```python
        # Analyze sentiment for all documents using the field 'media.audioUrl'
        database.analyze_sentiment(json_path="media.audioUrl")

        # Analyze sentiment for specific documents only
        database.analyze_sentiment(json_path="media.audioUrl", document_ids=["doc-3", "doc-4"])
        ```
        ---
        """
        if json_path is None or len(json_path) == 0:
            raise ValueError("JSON path is required")

        from model_garden.model_repo import ModelRepo, ModelProvider
        model_repo = ModelRepo(self.__api_key)

        if not document_ids:
            documents = self.get_all_documents()
        else:
            documents = self.get_all_documents(document_ids=document_ids)

        model = model_repo.get_by_name(
            'audio-sentiment-analysis', ModelProvider.BERRYDB_MODEL)

        for doc in documents:
            audio_url = Utils.get_value_from_json_path(doc, json_path)
            if audio_url is None:
                print(
                    f"Skipping document with id {doc['id']} because json_path {json_path} not found")
                continue
            prediction = model.predict({"audioUrl": audio_url})
            self.add_annotations(
                doc['id'], [prediction], 'text classification', json_path)

    def ingest(self, ingest_type: IngestType, ingest_file_type: IngestFileType, artifacts: list[str]):
        """
        Ingests content into the database from URLs or local files.

        **What it does**:
        - When given URLs, it accepts HTML pages, PDF files, or Excel (XLSX) sheets.
        - When given files, it accepts PDF or Excel (XLSX) files from your local disk.
        - Adds the ingested records into the currently connected database.

        **Parameters**:
        - **ingest_type** (`IngestType`): Where your inputs come from. Use `IngestType.URL` for URLs
          or `IngestType.FILE` for local files.
        - **ingest_file_type** (`IngestFileType`): The type of content: `PDF`, `XLSX`, or `HTML`.
          Note: `HTML` is only valid with `IngestType.URL`.
        - **artifacts** (`list[str]`): URLs (for URL ingest) or absolute file paths (for file ingest).

        **Returns**:
        - `str`: A success message indicating the request was accepted. For URL inputs,
          processing may continue in the background.

        **Raises**:
        - **ValueError**: If the combination of ingest type/file type is invalid or artifacts is empty.
        - **Exception**: If the request fails.

        **Examples**:
        ```python
        # Ingest a webpage by URL
        database.ingest(IngestType.URL, IngestFileType.HTML, ["https://berrydb.io"])

        # Ingest a local PDF
        database.ingest(IngestType.FILE, IngestFileType.PDF, ["/absolute/path/to/file.pdf"])

        # Ingest an Excel sheet by URL
        database.ingest(IngestType.URL, IngestFileType.XLSX, ["https://example.com/data.xlsx"])
        ```

        .. seealso::
            For details on the enums used, see:
            - :ref:`IngestType <ingesttype>`
            - :ref:`IngestFileType <ingestfiletype>`
        .. #end

        ---
        """
        # Validate input combinations
        if ingest_type == IngestType.URL:
            if ingest_file_type not in [IngestFileType.PDF, IngestFileType.XLSX, IngestFileType.HTML]:
                raise ValueError(
                    "URL ingest only supports PDF, XLSX, and HTML file types")
        elif ingest_type == IngestType.FILE:
            if ingest_file_type not in [IngestFileType.PDF, IngestFileType.XLSX]:
                raise ValueError(
                    "File ingest only supports PDF and XLSX file types")
        else:
            raise ValueError(
                "Invalid ingest_type. Must be IngestType.URL or IngestType.FILE")

        if not artifacts:
            raise ValueError("Artifacts list cannot be empty")

        url = bdb_constants.BASE_URL + populate_upload_template_url
        params = {"apiKey": self.__api_key}

        # Prepare form data & files
        form_data = {}
        files = None

        if ingest_type == IngestType.URL:
            if ingest_file_type == IngestFileType.HTML:
                # HTML URLs -> send URLs directly
                form_data = {
                    "databaseName": self.__database_name,
                    "userEmail": "",
                    "uploadType": "URLs",
                    "urls": artifacts
                }
            else:
                # PDF or XLSX from URL -> download files first
                temp_files = []
                try:
                    for artifact_url in artifacts:
                        # Derive a stable filename from the URL if possible
                        parsed = urlparse(artifact_url)
                        candidate_name = os.path.basename(parsed.path)
                        candidate_name = unquote(
                            candidate_name) if candidate_name else None
                        suffix = f".{ingest_file_type.value.lower()}"
                        if not candidate_name or not candidate_name.lower().endswith(suffix):
                            candidate_name = None  # ignore mismatched or missing

                        if candidate_name:
                            temp_dir = tempfile.gettempdir()
                            temp_path = os.path.join(temp_dir, candidate_name)
                            urllib.request.urlretrieve(artifact_url, temp_path)
                            temp_files.append(temp_path)
                        else:
                            # Fallback to a safe temporary name
                            temp_file = tempfile.NamedTemporaryFile(
                                delete=False, suffix=suffix)
                            temp_files.append(temp_file.name)
                            urllib.request.urlretrieve(
                                artifact_url, temp_file.name)
                            temp_file.close()

                    form_data = {
                        "databaseName": self.__database_name,
                        "userEmail": "",
                        "uploadType": "Excel" if ingest_file_type == IngestFileType.XLSX else "PDF"
                    }

                    files = []
                    for temp_file_path in temp_files:
                        with open(temp_file_path, 'rb') as f:
                            files.append(('file', (
                                os.path.basename(temp_file_path),
                                f.read(),
                                'multipart/form-data'
                            )))
                finally:
                    for temp_file_path in temp_files:
                        try:
                            os.unlink(temp_file_path)
                        except OSError:
                            pass
        else:
            # Local file ingest
            form_data = {
                "databaseName": self.__database_name,
                "userEmail": "",
                "uploadType": "Excel" if ingest_file_type == IngestFileType.XLSX else "PDF"
            }

            files = []
            for file_path in artifacts:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")

                with open(file_path, 'rb') as f:
                    files.append(('file', (
                        os.path.basename(file_path),
                        f.read(),
                        'multipart/form-data'
                    )))

        try:
            if files:
                # Send multipart form-data with file
                response = requests.post(
                    url, params=params, data=form_data, files=files)
            else:
                # Send only form-data (HTML URL case)
                response = requests.post(url, params=params, data=form_data)

            if response.status_code != 200:
                Utils.handleApiCallFailure(
                    response.json(), response.status_code)

            # Return human-friendly message instead of raw JSON
            if ingest_type == IngestType.URL:
                if ingest_file_type == IngestFileType.HTML:
                    return "URLs accepted. Web pages are being processed asynchronously. Time may vary based on content length."
                if ingest_file_type == IngestFileType.PDF:
                    return "PDF URLs accepted. Processing is asynchronous and may take longer for larger documents."
                if ingest_file_type == IngestFileType.XLSX:
                    return "Excel URLs accepted. Processing is asynchronous and depends on content length."
            else:
                if ingest_file_type == IngestFileType.PDF:
                    return "PDF files uploaded successfully. Processing will start shortly and may take longer for documents with more pages."
                if ingest_file_type == IngestFileType.XLSX:
                    return "Excel files uploaded successfully. Processing will start shortly."

            return "Ingest request accepted. Files are being processed asynchronously. Time may vary based on content length."

        except Exception as e:
            logger.error(
                f"Failed to ingest {ingest_type.value} {ingest_file_type.value}: {str(e)}")
            raise

    def annotate(self, model_name: str, json_path: str, model_args: dict = None):
        """
        Annotates documents in the database using a specified model.

        This method fetches documents, extracts data from a specified JSON path,
        invokes a model to get predictions, and adds the predictions as annotations
        back to the documents.

        **Parameters**:
        - **model_name** (`str`): The name of the model to use for annotation.
        - **json_path** (`str`): The JSON path to extract data from for prediction.
        - **model_args** (`dict`, optional): Additional arguments to pass to the model (eg: labels, etc).

        **Returns**:
        - `None`: The annotations are written back to the database.

        **Raises**:
        - `ValueError`: If `model_name`, or `json_path` are not provided.
        - `Exception`: If the specified model is not found.
        """
        if not all([model_name, json_path]):
            raise ValueError(
                "model_name, provider_type, and json_path are required.")

        if model_args is not None and not isinstance(model_args, dict):
            raise ValueError("model_args must be None or a dictionary")

        from model_garden.model_repo import ModelRepo
        from model_garden.model import Model
        model_repo = ModelRepo(self.__api_key)

        model: Model = model_repo.get_by_name(model_name)
        if model is None:
            raise Exception(
                f"Model '{model_name}' not found.")

        documents = self.get_all_documents()

        for doc in documents:
            doc_id = doc["_meta"]["objectId"]
            data_to_predict = Utils.get_value_from_json_path(doc, json_path)
            if data_to_predict is None:
                print(
                    f"Skipping document with id {doc_id} because json_path {json_path} not found.")
                continue
            if debug_mode:
                print("data_to_predict: ", data_to_predict)
                print("type model: ", type(model))

            model_input = data_to_predict
            if isinstance(model, BerryDBModel):
                model_input = {"inputs": data_to_predict}
                model_args = (model_args or {})
                model_args["label_studio_transform"] = True
            print(f"Fetching prediction for document with id {doc_id}")
            prediction = model.predict(model_input, model_args=model_args)
            self.add_annotations(
                doc_id, [prediction], model.config.name, json_path)

    def evaluator(self, llm_api_key: str, embedding_api_key: str | None = None, metrics_database_name: str | None = "EvalMetricsDB"):
        """
        The `evaluator` method initializes and returns an instance of `BerryDBRAGEvaluator`, configured to assess various metrics for a specific project in BerryDB. This evaluator can be used to measure and track key performance indicators within the database.

        **Parameters**:
        - **llm_api_key** (`str`): The API key used to authenticate requests to the LLM API. This key must be valid and associated with your account
        - **embedding_api_key** (`str`, optional): This is required only when the chat and embedding models are different. Provide the API key for the embedding model as per settings.
        - **metrics_database_name** (`str`, optional): The name of the database where evaluation metrics will be stored. Defaults to "**EvalMetricsDB**"

        .. note::
            This method requires that the database specified by metrics_database_name (or the default EvalMetricsDB) already exists. The method does not create a new database and will raise an error if the specified database is not found.
        .. #end

        **Returns**:
        - `BerryDBRAGEvaluator`: An instance of the BerryDBRAGEvaluator class, initialized with the specified API keys and project/database names for evaluating and storing metrics.

        **Example**:
        ```python
        # Initialize the evaluator with the required OpenAI API key
        llm_api_key = "LLM_API_KEY"
        embedding_api_key = "EMBEDDING_API_KEY"
        evaluator = database.evaluator(
            llm_api_key=llm_api_key,
            embedding_api_key=embedding_api_key,
            metrics_database_name="MyMetricsDB"
        )
        ```

        .. seealso::
            See :meth:`eval <evaluator.berrydb_rag_evaluator.BerryDBRAGEvaluator.eval>` for instructions on performing additional operations with the evaluator.
        ..  # end
        ---
        """
        from evaluator.berrydb_rag_evaluator import BerryDBRAGEvaluator
        return BerryDBRAGEvaluator(
            api_key=self.__api_key,
            settings_name=self.__settings_name,
            settings=self.__settings,
            llm_api_key=llm_api_key,
            database=self,
            embedding_api_key=embedding_api_key,
            metrics_database_name=metrics_database_name or "EvalMetricsDB",
        )
