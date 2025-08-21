import json
from typing import Tuple

import requests

import constants.constants as bdb_constants
from annotation_project.annotation_project import AnnotationProject
from constants.constants import (DEFAULT_BUCKET, create_database_url,
                                 create_label_studio_project_url,
                                 create_schema_url, debug_mode,
                                 delete_database_url, evaluate_endpoints,
                                 get_database_id_url,
                                 get_database_list_by_api_key_url,
                                 get_schema_id_url, validate_api_key_url)
from model_garden.model_config import _clear_model_categories_cache
from model_garden.model_repo import ModelRepo
from utils.berrydb_init_exception import BerryDBInitializationException
from utils.utils import Utils


class BerryDB:

    @staticmethod
    def __validate_initialization():
        """
        Validates that `init` has been called. If not, prints a guide and exits.
        """
        if bdb_constants.BASE_URL is None:
            print(
                """
                # BerryDB SDK Initialization Guide
                Before using any features of the SDK, you **must** initialize it by setting the base URL for BerryDB using the `init` method.
                This is a required step to configure the SDK to communicate with your BerryDB instance.

                Example:
                    BerryDB.init("https://my-berrydb-instance.com")
                    **or**
                    BerryDB.init("101.102.103.104")

                You can use the BerryDB SDK methods, after initializing.

                """)
            raise BerryDBInitializationException()

    @staticmethod
    def init(host:str) -> None:
        """
            Initializes the SDK with the given host, which can be an IPv4 address or a domain name,
            optionally including a port. If no scheme (http/https) is provided, "https://" is prefixed by default.

            Parameters:
            - **host** *(str)*: The host address of your BerryDB instance. Examples: "https://my-berrydb.com", "my-berrydb:8080", "192.168.1.1", "192.168.1.1:8080"

            Returns:
            - None

            Raises:
            - ValueError: If the host is invalid or uses an unsupported scheme.

            Example:
            ```python
            # import BerryDB
            from berrydb import BerryDB

            BerryDB.init("app.berrydb.io")
            ```
            ---
        """
        import ipaddress
        import re
        from urllib.parse import urlparse

        host = host.strip()

        def is_valid_ip(ip: str) -> bool:
            try:
                ipaddress.ip_address(ip)
                return True
            except ValueError:
                return False

        domain_regex = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"

        parsed = urlparse(host)

        if not parsed.scheme:
            host_candidate = host
            if host.count(':') == 1:
                host_part, port_str = host.rsplit(":", 1)
                try:
                    port = int(port_str)
                    if not (1 <= port <= 65535):
                        raise ValueError
                    host_candidate = host_part
                except ValueError:
                    raise ValueError(f"Invalid port in host: {host}")

            if not (is_valid_ip(host_candidate) or re.match(domain_regex, host_candidate)):
                raise ValueError(f"Invalid host: {host}")

            host = f"https://{host}"
        elif parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Unsupported scheme: {parsed.scheme}")

        host = host.rstrip("/")

        evaluate_endpoints(host)
        _clear_model_categories_cache()

    @classmethod
    def connect(
        cls,
        api_key:str,
        database_name:str,
        bucket_name:str = DEFAULT_BUCKET,
    ):
        """
        This method establishes a connection to the specified database. The connection uses the provided **api_key** for authentication and allows you to interact with the database referenced by **database_name**.

        .. tip::
            You can find your BerryDB **api_key** `here <https://app.berrydb.io/settings>`_.
        .. #end

        An organization is defined by the domain in the email-id used when creating your BerryDB account. For example, if the account is registered with the email address ``john@tatooine.com``, the corresponding organization will be ``tatooine.com``.

        Once the connection is established, you will receive a database connection object. This object can be used to perform further operations, such as querying, inserting/updating data within the connected database.

        **Parameters:**
        - **api_key** *(str)*: API Key for authentication.
        - **database_name** *(str)*: Name of the database to connect.

        .. note::
            ``database_name`` cannot contain ``-`` (hyphens) and can only contain the following characters: ``A-Z``, ``a-z``, ``0-9``, ``#``, ``_``, and must start with a letter. It should be between 1 and 128 characters long.
        .. #end

        **Returns:**
        - **Database**: An instance of the database.
        - **None**: If the database does not exist in the organization.

        **Example:**
        ```python
        from berrydb import BerryDB

        berrydb_api_key = "BERRYDB_API_KEY"
        database_name = "myNewDatabase"
        database = BerryDB.connect(berrydb_api_key, database_name)
        ```
        ---
        """

        from database.database import Database
        BerryDB.__validate_initialization()

        bucket_name = cls.__validate_bucket_name(bucket_name)

        if debug_mode:
            print("api_key: ", api_key)
            print("database_name: ", database_name)
            print("bucket_name: ", bucket_name)
            print("\n\n")

        try:
            org_name: str = cls.__validate_api_key(api_key, database_name)
        except Exception as e:
            raise e

        if org_name is None:
            raise ValueError(f"Error: Either your API key is invalid or you are not authorized to access the database {database_name}")

        return Database(api_key, bucket_name, org_name, database_name)

    @classmethod
    def databases(cls, api_key:str):
        """
        The databases method retrieves a list of all databases accessible to the organization associated with the provided API key. Each database is represented as a dictionary containing relevant metadata about that database, such as its name, ID, creation date, and other associated properties.

        This method is essential for listing the databases available in your organization, making it easier to interact with them for further operations like querying, updating, or deleting records.

        Parameters:

        - **api_key** (*str*): API Key for authentication.

        Returns:

        - `List[Dict]`: A list where each entry is a dictionary representing a database.

        Example:
        ```python
        # import BerryDB
        from berrydb import BerryDB

        berrydb_api_key = "BERRYDB_API_KEY"
        db_list = BerryDB.databases(berrydb_api_key)
        print("List of Databases in the organization: ", db_list)
        ```
        ---
        """
        BerryDB.__validate_initialization()
        url = bdb_constants.BASE_URL + get_database_list_by_api_key_url
        params = {"apiKey": api_key}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            jsonResponse = response.json()
            if debug_mode:
                print("databases result ", jsonResponse)
            if (
                "database" in jsonResponse
                and "responseList" in jsonResponse["database"]
            ):
                databaseNames = {}
                # print("\nDatabases:")
                for db in jsonResponse["database"]["responseList"]:
                    name = db["name"] if "name" in db else ""
                    schemaName = db["schemaName"] if "schemaName" in db else ""
                    description = db["description"] if "description" in db else ""
                    dbId = db["id"] if "id" in db else ""
                    schemaId = db["schemaId"] if "schemaId" in db else ""
                    isContentType = db["contentType"] if "contentType" in db else ""
                    databaseNames[name] = {
                        "id": dbId,
                        "schemaId": schemaId,
                        "schemaName": schemaName,
                        "description": description,
                        "isContentType": isContentType,
                    }
                    # print(name + " : " + str(databaseNames[name]))
                # print("\n")
                return databaseNames
            return {}
        except Exception as e:
            print("Failed to fetch databases: {}".format(str(e)))
            return {}

    @classmethod
    def create_schema(cls, api_key:str, schema_name:str, schema_desc:str, schema_details:dict):
        """
        The `create_schema` method is used to define and create a new schema for a database. This schema provides a structured way to store data, including specifying data types, filterable fields, indexable fields, and other metadata. Schemas are shared resources accessible to all members of the organization. Create the right schema required for your use case. BerryDB supports schema evolution. You can always add new fields and change your schema without impacting your app. (Support for editing schemas within the SDK is planned for future releases. Currently, you can edit schemas using the Web App.)

        Parameters:

        - **api_key** (`str`): The API Key used for authentication. This key must belong to the user creating the schema.
        - **schema_name** (`str`): The name of the schema being created. It should be a unique within the organization.
        - **schema_desc** (`str`): A brief description of the schema, which explains its purpose.
        - **schema_details** (`Dict`): A dictionary that defines the structure of the schema. This includes fields, data types, indexing, filtering, and more. The schema consists of:
            - **schemaName** (`str`): The name of the schema.
            - **userId** (`str`): The ID of the user creating the schema.
            - **userEmail** (`str`): The email of the user.
            - **rawSchema** (`Dict[str, any]`): A dictionary that outlines the fields and data structure for the schema. This includes nested objects and arrays.
            - **schemaDataTypes** (`Dict[str, str]`): A dictionary that specifies the data types for each field in the schema, including nested fields within objects and arrays.
            - **filterFields** (`List[str]`): An optional list of fields that can be used to filter data within the schema.
            - **indexFields** (`List[str]`): A list of fields that will be indexed to improve query performance.
            - **displayTextField** (`str`): The field that represents the main display text for each record. (`Optional`)
            - **displayImageField** (`str`): The field that represents the display image for each record. (`Optional`)

        .. note::
            `schema_name` cannot contain `-`(Hyphens) and can only contain the following characters: `A-Z` `a-z` `0-9` `#` `_`, and must start with a letter, [`A-Z` `a-z`]. The length of the schema name should be between `1` and `128`.
            `schema_desc` length should be between `1` and `256`.
        .. #end

        Returns:

        - **str**: A success message if the schema is created successfully.
        - **None**: If there is an error during schema creation, an error message will be printed, and `None` will be returned.

        **Example**:
        ```python
        # import BerryDB
        from berrydb import BerryDB

        berrydb_api_key =  "BERRYDB_API_KEY"
        email_id = "EMAIL_ID"
        db_name = "StudentData"
        schema_name = "MyNewSchema"
        schema = {
            "schemaName": schema_name,
            "rawSchema": {
                "profilePic": "",
                "name": "",
                "age": 0,
                "isAlumni": False
                "addresses": [
                    {
                        "line1": "",
                        "line2": "",
                        "area": "",
                        "country": "",
                        "zipcode": ""
                    }
                ]
            },
            "schemaDataTypes": {
                "profilePic": "string",
                "name": "string",
                "age": "number",
                "isAlumni": "boolean",
                "addresses": "array",
                "addresses[0]": "object",
                "addresses[0].line1": "string",
                "addresses[0].line2": "string",
                "addresses[0].area": "string",
                "addresses[0].country": "string",
                "addresses[0].zipcode": "string"
            },
            "filterFields": [
                "addresses[0].country",
                "isAlumni"
            ],
            "indexFields": [
                "name",
                "addresses[0].area"
            ],
            "displayTextField": "name"
            "displayImageField": "profilePic"
        }

        print(BerryDB.create_schema(api_key=berrydb_api_key, schema_name=schema_name, schema_desc="This is a schema to store users and their addresses", schema_details=schema))
        ```
        ---
        """
        BerryDB.__validate_initialization()
        if debug_mode:
            print("schema_details: ", schema_details)

        url = bdb_constants.BASE_URL + create_schema_url
        params = {"apiKey": api_key}

        payload = json.dumps(
            {
                "name": schema_name,
                "description": schema_desc,
                "details": schema_details,
            }
        )
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
        }

        if debug_mode:
            print("url:", url)
            print("payload:", payload)
            # print("headers:", headers)

        try:
            response = requests.post(url, params=params, data=payload, headers=headers)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Schema creation result ", response.json())
            json_res = json.loads(response.text)
            if json_res["responseList"][0]["schemaId"]:
                print(
                    json_res["message"]
                    if json_res["message"]
                    else "Schema created successfully"
                )
                res = json_res["responseList"][0]
                res["schema_name"] = schema_name
                return res
            else:
                Utils.handleApiCallFailure(
                    "Schema creation failed, please try again later.",
                    response.status_code,
                )
        except Exception as e:
            print("Failed to create the Schema: {}".format(str(e)))
            return None

    @classmethod
    def create_database(
        cls, api_key:str, database_name:str, schema_name:str, bucket_name:str = DEFAULT_BUCKET
    ):
        """
        The `create_database` method is used to initialize a new database instance within the BerryDB ecosystem confined to the organization the user belongs to. Similar to the `connect <#berrydb.BerryDB.BerryDB.connect>`_ method it returns a database connection object. If a database with the specified name already exists, an informative failure message is printed, and the method returns None, preventing any accidental overwrites.

        .. tip::
            You can find your BerryDB **api_key** `here <https://app.berrydb.io/settings>`_.
        .. #end

        An organization is defined by the domain in the email-id used when creating your BerryDB account. For example, if the account is registered with the email address `john@tatooine.com`, the corresponding organization will be `tatooine.com`.

        Databases are shared resources accessible to all members of the organization.

        Once the connection is established, you will receive a database connection object. This object can be used to perform further operations, such as querying, inserting/updating data within the connected database.

        **Parameters**:
        - **api_key** (`str`): API Key for authentication.
        - **database_name** (`str`): The unique name for the new database. This identifier will be used to reference the database in future operations. Ensure that the name is distinct from existing databases.
        - **schema_name** (`str`): The name of the schema that will be applied to the database. This schema dictates the structure of the data, including the fields and their data types, ensuring data consistency and integrity.

        **Returns**:
        - `Database`: An instance of the newly created database.
        - `None`: If a database with the provided name already exists, a failure message is printed, and `None` is returned.

        **Example**
        ```python
        # import BerryDB
        from berrydb import BerryDB

        # Define your API key and other required parameters
        berrydb_api_key = "BERRYDB_API_KEY"  # Replace with your actual API key
        database_name = "MyNewDatabase"  # Desired name for the new database
        schema_name = "MySchema"  # Name of the schema to apply to the new database

        # Create a new database
        database = BerryDB.create_database(
            api_key=berrydb_api_key,
            database_name=database_name,
            schema_name=schema_name
        )
        ```
        ---
        """
        BerryDB.__validate_initialization()
        schema_id = None
        user_id = None
        try:
            schema_id, user_id = cls.__get_schema_id_by_name(api_key, schema_name)
        except Exception as e:
            pass
        if debug_mode:
            print("schema_id :", schema_id)
            print("user_id: ", user_id)
        if not (schema_id and user_id):
            return

        url = bdb_constants.BASE_URL + create_database_url
        payload = {
            "schemaId": str(schema_id),
            "userId": user_id,
            "databaseName": database_name,
        }
        # headers = Utils.get_headers(api_key, "multipart/form-data")
        params = {"apiKey": api_key}

        if debug_mode:
            print("url:", url)
            print("payload:", payload)
            print("params:", params)
            # print("headers:", headers)

        try:
            from database.database import Database
            session = requests.session()
            response = session.post(url, data=payload, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Database creation result ", response.json())
            json_res = json.loads(response.text)
            if "organizationName" in json_res:
                print(
                    json_res["message"]
                    if json_res["message"]
                    else "Database created successfully"
                )
                return Database(
                    api_key, bucket_name, json_res["organizationName"], database_name
                )
            else:
                Utils.handleApiCallFailure(
                    "Database creation failed, please try again later.",
                    response.status_code,
                )


        except Exception as e:
            raise Exception("Failed to create the database: {}".format(str(e)))


    @classmethod
    def delete_database(cls, api_key, database_name):
        """
        The `delete_database` method is used to permanently remove a specified database from your organization. This **action is irreversible**, so it should be used with caution. Upon successful deletion, a confirmation message will be returned.

        **Parameters**:
        - **api_key** (`str`): API Key for authentication.
        - **database_name** (`str`): The name of the database you wish to delete. Ensure that the provided name matches exactly with the existing database to avoid errors or unintended deletions.

        **Returns**:
        - `str`: A confirmation message indicating that the database has been successfully deleted.
        - `str`: If the deletion fails due to an incorrect database name or if the database does not exist in the , an error message will be returned instead.

        **Example**
        ```python
        # import BerryDB
        from berrydb import BerryDB

        # Define your API key and the database name to delete
        berrydb_api_key = "BERRYDB_API_KEY"  # Replace with your actual API key
        database_name = "MyOldDatabase"  # Name of the database to be deleted

        # Delete the specified database
        result = BerryDB.delete_database(api_key=berrydb_api_key, database_name=database_name)
        print(result)
        ```
        ---
        """
        BerryDB.__validate_initialization()
        # schema_id = None
        # user_id = None
        database = cls.__get_database(api_key, database_name)
        print("database :", database)

        # schema_id = None
        # user_id = None
        # try:
        #     schema_id, user_id = cls.__get_schema_id_by_name(
        #         api_key, database["schemaName"]
        #     )
        # except Exception as e:
        #     pass
        # if debug_mode:
        #     print("schema_id :", schema_id)
        #     print("user_id: ", user_id)
        # if not (schema_id and user_id):
        #     return

        url = bdb_constants.BASE_URL + delete_database_url
        params = {"databaseName": database, "apiKey": api_key}
        headers = {
            "Content-Type": "application/json",
        }

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.delete(url, params=params, headers=headers)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Database deletion result ", response.json())
            json_res = json.loads(response.text)
            return json_res["message"]
        except Exception as e:
            print("Failed to delete the database: {}".format(str(e)))
            return None

    @classmethod
    def create_annotation_project(
        self, berrydb_api_key:str, annotations_api_key:str, project_name:str, project_description:str|None=""
    ):
        """
        The `create_annotation_project` method is used to create a new Annotations project within BerryDB. Annotations projects are designed to organize and manage data annotation tasks for various datasets.
        An annotation project is useful for tasks such as Named Entity Recognition, text or image classification, labeling, image captioning, text summarization, object detection, sentiment analysis, and more. It enables you to efficiently label and organize data. Within BerryDB, you can easily sift through the annotated data using queries, filters, or even leverage LLMs (Large Language Models) for more advanced data exploration.

        .. tip::
            You can find your BerryDB **annotations_api_key** `here <https://app.berrydb.io/settings>`_. This key is separate from the standard BerryDB API key to maintain distinct roles, allowing non-developers to manage and annotate records independently.
        .. #end

        **Parameters**:
        - **berrydb_api_key** (`str`): Your BerryDB API Key.
        - **annotations_api_key** (`str`): Your BerryDB annotations API Key.
        - **project_name** (`str`): The name of the project to be created. This name will be used to identify and manage the project within the BerryDB Annotations system. While there are no restrictions on using the same project name within an organization, it is recommended to use unique names to avoid confusion and ensure better project management.
        - **project_description** (`str`, optional): An optional description for the project. This can be used to provide additional context or information about the project's goals, data, or purpose. If no description is provided, this field defaults to an empty string.

        **Returns**:
        - `str`: A success or failure message indicating the result of the project creation attempt. A success message will confirm the creation of the project, while a failure message will explain the reason for any errors.

        **Example**
        ```python
        # import BerryDB
        from berrydb import BerryDB

        # Define your API key and other required parameters
        berrydb_api_key = "BERRYDB_API_KEY"  # Replace with your actual BerryDB API key
        annotations_api_key = "ANNOTATIONS_API_KEY"  # Replace with your actual annotations API key
        project_name = "ImageClassification"  # Desired name for the new project
        project_description = "A project for classifying images into different categories."  # Optional description

        # Create a new annotations project
        my_annotation_project = BerryDB.create_annotation_project(
            berrydb_api_key=berrydb_api_key,
            annotations_api_key=annotations_api_key,
            project_name=project_name,
            project_description=project_description
        )
        ```
        .. note::
            After creating a project you may perform further actions. Refer to: :meth:`AnnotationProject <annotation_project.annotation_project.AnnotationProject.setup_label_config>`
        .. #end

        ---
        """
        BerryDB.__validate_initialization()

        if not (isinstance(project_name, str) and len(project_name.strip())):
            raise ValueError(f"project_name must be string and cannot be None or empty")

        url = bdb_constants.LABEL_STUDIO_BASE_URL + create_label_studio_project_url
        payload = {"title": project_name, "description": project_description}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {annotations_api_key}",
        }

        if debug_mode:
            print("url:", url)
            print("payload:", payload)

        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            if response.status_code != 201:
                print("Failed to create Project!")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Create LS project result ", response.json())
            project_details = json.loads(response.text)
            print("Project created successfully")
            return AnnotationProject(berrydb_api_key, annotations_api_key, project_details["id"], project_name)
        except Exception as e:
            print(f"Failed to create your project: {str(e)}")
            return None

    @classmethod
    def model_repo(self, berrydb_api_key:str) -> ModelRepo:
        """
        Provides access to the BerryDB Model Repository.

        The Model Repository is the central point for managing models within BerryDB.
        You can use the returned `ModelRepo` instance to save new models,
        request models from integrated providers (like HuggingFace, Vertex AI), and retrieve
        information about existing models.

        Parameters:
        - **berrydb_api_key** (`str`): The API key for authenticating with BerryDB.

        Returns:
        - `ModelRepo`: An instance of the Model Repository, allowing interaction
          with BerryDB's model management features.

        Example:
        ```python
        from berrydb import BerryDB

        # Initialize BerryDB (if not already done)
        # BerryDB.init("your-berrydb-host")

        api_key = "YOUR_BERRYDB_API_KEY"

        # Get the model repository instance
        repo = BerryDB.model_repo(api_key)

        # You can now use the 'repo' object to interact with models, e.g.:
        # hf_model_config = ModelConfig.huggingface_builder()...build(api_key=api_key)
        ```

        .. note::
            `Refer ModelConfig </model_config.html>`_ to learn how to configure models to add them to your model repository.

            `Refer Model </model.html>`_ to learn how to save and retrieve predictions from your model repository.
        .. #end
        """
        BerryDB.__validate_initialization()
        return ModelRepo(berrydb_api_key)

    """ @classmethod
    def __get_project(self, annotations_api_key, project_id):
        try:
            if debug_mode:
                print(annotations_api_key)
                print(project_id)
            ls = Client(url=label_studio_base_url, api_key=annotations_api_key)
            project = ls.get_project(id=project_id)
            if not project:
                print(f"Failed to get project")
            if debug_mode:
                print("Fetched project result: ",  project)
            return project
        except Exception as e:
            print(f"Failed to get project: {str(e)}")
            raise Exception(e)
            return None """

    @classmethod
    def __get_schema_id_by_name(cls, api_key: str, schema_name: str) -> Tuple[int, int]:
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Schema Name

        Returns:
            (int : Schema ID, int : User ID)
        """

        url = bdb_constants.BASE_URL + get_schema_id_url
        params = {"apiKey": api_key, "schemaName": schema_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get schema id by name result ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("schema", None):
                return (
                    json_res["schema"].get("id", None),
                    json_res["schema"].get("userId", None),
                )
        except Exception as e:
            # err_msg = "Either the schema does not exist or does not belong to you."
            print("Failed to fetch your schema: {}".format(str(e)))

    @classmethod
    def __validate_bucket_name(cls, bucket_name: str) -> str:
        """Validate the bucket name, to check if it is supported

        Args:
            bucket_name (str): Bucket name

        Returns:
            str : Bucket name
        """
        if not bucket_name:
            return DEFAULT_BUCKET
        if bucket_name not in bdb_constants.ALLOWED_BUCKET_NAMES:
            print(f"{bdb_constants.TEXT_COLOR_WARNING}Warning: Bucket name that you have provided is not supported, using the default bucket.{bdb_constants.TEXT_COLOR_ENDC}")
            return DEFAULT_BUCKET
        return bucket_name

    @classmethod
    def __validate_api_key(cls, api_key: str, database_name: str):
        """Validate the API key and check if the user is authorized to access the database.

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            str : Organization name
        """

        url = bdb_constants.BASE_URL + validate_api_key_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.post(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Validate API key result: ", response.json())
            json_res = response.json()
            if json_res.get("organizationName", None):
                return json_res["organizationName"]
        except Exception as e:
            raise Exception("Failed to validate your API key: {}".format(str(e)))

    def __get_database_id(self, api_key: str, database_name: str):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            int : Database ID
        """

        url = bdb_constants.BASE_URL + get_database_id_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get database id by name result: ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("database", None):
                return json_res["database"].get("id", None)
        except Exception as e:
            print("Failed to fetch your database: {}".format(str(e)))

    @classmethod
    def __get_database(cls, api_key: str, database_name: str):
        """Function summary

        Args:
            arg1 (str): API Key
            arg2 (str): Database Name

        Returns:
            int : Database ID
        """

        url = bdb_constants.BASE_URL + get_database_id_url
        params = {"apiKey": api_key, "databaseName": database_name}

        if debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if debug_mode:
                print("Get database id by name result: ", response.json())
            json_res = json.loads(response.text)
            if json_res.get("database", None):
                return json_res["database"]
        except Exception as e:
            print("Failed to fetch your database: {}".format(str(e)))


if __name__ == "__main__":
    pass