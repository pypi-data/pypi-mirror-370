import json
import logging
from typing import List

import requests

from constants import constants as bdb_constants
from model_garden.annotations_config import AnnotationsConfig
from model_garden.model import Model
from utils.utils import Utils
from database.database import Database

logger = logging.getLogger(__name__)

class AnnotationProject:
    __berrydb_api_key: str
    __annotations_api_key: str
    __project_id: int
    __project_name: str

    def __init__(self, berrydb_api_key:str, annotations_api_key: str, project_id: int, project_name: str):
        if berrydb_api_key is None:
            Utils.print_error_and_exit("BerryDB API key cannot be None")
        if annotations_api_key is None:
            Utils.print_error_and_exit("Annotations API key cannot be None")
        if project_id is None:
            Utils.print_error_and_exit("Project not found")
        if project_name is None:
            Utils.print_error_and_exit("Project name cannot be None")

        self.__berrydb_api_key = berrydb_api_key
        self.__annotations_api_key = annotations_api_key
        self.__project_id = project_id
        self.__project_name = project_name

    def berrydb_api_key(self):
        """
        Retrieves the BerryDB API key associated with this annotation project.

        This API key is used for authenticating operations related to BerryDB
        services, such as populating the project with data from a BerryDB database.

        Returns:
        - `str`: The BerryDB API key for the project.

        Example:
        ```python
        # Assuming 'my_annotation_project' is an instance of AnnotationProject
        # project_api_key = my_annotation_project.berrydb_api_key()
        # print(f"The BerryDB API key for this project is: {project_api_key}")

        # This key might be used internally or for other SDK operations
        # that require authentication with the main BerryDB services.
        ```
        ---
        """
        return self.__berrydb_api_key

    def annotations_api_key(self):
        return self.__annotations_api_key

    def project_name(self):
        return self.__project_name

    def project_id(self):
        return self.__project_id

    def setup_label_config(self, label_config):
        """
        The `setup_label_config` method configures the label settings for the specified annotation project. This configuration defines the labeling structure and rules to ensure consistent and organized annotation of data within the project. It is essential for tasks such as Named Entity Recognition (NER), image or text classification, and other annotation-based workflows where specific labels are applied to different data points. Without this setup, annotations and predictions added to the project will not be visible in the UI, making it a critical step for visualizing and managing the labeled data.

        **Parameters**:
        - **label_config** (`str`): A string representing the label configuration. This configuration defines the labels that will be used within the project and their respective properties. The format typically follows a predefined structure that outlines label categories, attributes, and potentially hierarchical relationships between labels.

        **Returns**:
        - `Dict`: A dict with a message indicating whether the label configuration was successfully applied to the project. In case of an error (e.g., invalid project ID or configuration format), the returned message will provide details about the failure.

        **Example**
        ```python
        # Define your API key and other required parameters
        project_id = 12345  # ID of the project you want to configure

        # Label config for Topic Modeling
        project_config = '''
        <View>
        <Text name="text" value="$content.text"/>
        <View style="box-shadow: 2px 2px 5px #999; padding: 20px; margin-top: 2em; border-radius: 5px;">
            <Header value="Choose text sentiment"/>
            <Choices name="sentiment" toName="text" choice="single" showInLine="true">
            <Choice value="Introduction"/>
            <Choice value="Plan Information"/>
            <Choice value="Eligibility"/>
            <Choice value="Benefits"/>
            <Choice value="Financial Information"/>
            <Choice value="Provider Information"/>
            <Choice value="Claims and Reimbursements"/>
            <Choice value="Administrative Information"/>
            <Choice value="Legal and Regulatory Information"/>
            <Choice value="Dates and Deadlines"/>
            </Choices>
        </View>
        </View>
        '''

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # Setup label for Topic Modeling
        label_config = my_annotation_project.setup_label_config(project_config)
        if label_config:
            print("Label config setup succesful!")
        ```
        ---
        """

        url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.setup_label_config_url.format(self.__project_id)
        payload = json.dumps({"label_config": label_config})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.__annotations_api_key}",
        }

        if bdb_constants.debug_mode:
            print("url:", url)
            print("payload:", payload)

        try:
            response = requests.patch(url, data=payload, headers=headers)
            if response.status_code != 200:
                print("Project label config setup Failed!")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if bdb_constants.debug_mode:
                print("Setup config result ", response.json())
            print("Project label config setup successful!")
            return response.json()
        except Exception as e:
            print(f"Failed to setup config: {str(e)}")
            return None

    def populate(self, database:Database|str):
        """
        The `populate` method is designed to fill a specific annotation project with data retrieved from a designated database. This process allows users to efficiently import existing data for annotation tasks, enabling faster project setup and reducing the need for manual data entry.

        **Parameters**:
         - **database** (`Database | str`): The BerryDB database from which data will be sourced. This can be an instance of the `Database` class or a string representing the name of the database. If a string is provided, the SDK will attempt to connect to this database using the `berrydb_api_key` associated with this `AnnotationProject`.

        **Returns**:
        - `Dict | None`: A dictionary containing the API response upon successful population, or `None` if an error occurs during the process. The dictionary typically includes details about the import task.

        **Example**
        ```python
        # Define your required parameters
        database_name = "PatientDB"  # Name of the database from which to populate data

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # Option 1: Using database name (string)
        result_from_name = my_annotation_project.populate(database_name)
        if result_from_name:
            print(f"Successfully populated project using database name: {database_name}")

        # Option 2: Using a Database object (When you either create or connect to a database)
        from berrydb import BerryDB
        my_database_object = BerryDB.connect(api_key="your_api_key", database_name=database_name)
        result_from_object = my_annotation_project.populate(my_database_object)
        ```
        ---
        """
        if database is None or not (isinstance(database, Database) or isinstance(database, str)):
            raise ValueError("Error: database is required, it should either be a string or an instance of Database")

        if isinstance(database, Database):
            database_name = database.database_name()
        else:
            database_name = database
            from berrydb import BerryDB
            BerryDB.connect(self.berrydb_api_key(), database_name)

        if database_name is None or not isinstance(database_name, str) or database_name.strip() == "":
            raise ValueError("Error: database_name is required and must be of type str")

        try:
            reimport_url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.reimport_label_studio_project_url.format(self.__project_id)
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Token {}".format(self.__annotations_api_key),
            }
            reimport_data = {
                "file_upload_ids": [],
                "files_as_tasks_list": False,
                "database_name": database_name,
                "bdb_api_key": self.__berrydb_api_key,
            }

            if bdb_constants.debug_mode:
                print("url:", reimport_url)
                print("payload:", reimport_data)

            reimport_response = requests.post(
                reimport_url, data=json.dumps(reimport_data), headers=headers
            )
            if reimport_response.status_code != 201:
                print("Project populated Failed!")
                Utils.handleApiCallFailure(
                    reimport_response.json(), reimport_response.status_code
                )
            if bdb_constants.debug_mode:
                print("Populate project result: ", reimport_response.json())
            print("Project populated successfully!")
            return reimport_response.json()
        except Exception as e:
            print(f"Failed to populate your project: {str(e)}")
            if bdb_constants.debug_mode:
                raise e
            return None

    def connect_to_ml(self, model:Model|None = None, model_url:str|None = None, model_title:str = "ML Model"):
        """
        The `connect_to_ml` method establishes a connection between a specified annotation project and a Machine Learning (ML) model backend. This integration enables the project to leverage the capabilities of the ML model for tasks such as predictions, automated annotations, or data analysis, thereby enhancing the annotation workflow.

        .. tip::
            You can find your BerryDB ML Model URLs for **ml_url** `here <https://app.berrydb.io/ml-models>`_.
        .. #end

        **Parameters**:
        - **ml_url** (`str`): The URL of the ML backend to which the project will be connected. This URL should point to a deployed ML model or service that is accessible from the BerryDB environment.
        - **ml_title** (`str`, optional): A title for the connection, which provides context for the integration. By default, this is set to "ML Model", but you can customize it to better describe the specific ML model being used.


        **Returns**:
        - `None`: This method does not return a value. Instead, it establishes the connection and prints a success or failure message indicating the result of the operation.

        **Example**
        ```python
        ml_url = "http://app.berrydb.io/berrydb/model/model-id"
        ml_title = "Text Classification Model"

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # Connect the annotation project to the specified ML model
        my_annotation_project.connect_to_ml(ml_url, ml_title)
        ```
        ---
        """

        if model is None and model_url is None:
            raise ValueError("Either `model` or `model_url` must be provided.")

        if model is not None and not (isinstance(model, Model) and model.config._project_url and isinstance(model.config._project_url, str)):
            raise TypeError("`model` must be an instance of Model.")

        if model_url is not None and not isinstance(model_url, str):
            raise TypeError("`model_url` must be a string.")

        # TODO: Check for existing connected ML models and use the PATCH method to update the existing ML model connection
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Token {}".format(self.__annotations_api_key),
            }
            ml_payload = {
                "project": self.__project_id,
                "title": model_title or "ML Model",
                "url": model_url or model.config._project_url,
                "is_interactive": False,
            }
            ml_connect_response = requests.post(
                bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.connect_project_to_ml_url, data=json.dumps(ml_payload), headers=headers
            )
            if ml_connect_response.status_code != 201:
                print("Project Failed to connect to ML Model")
                Utils.handleApiCallFailure(
                    ml_connect_response.json(), ml_connect_response.status_code
                )
            if bdb_constants.debug_mode:
                    print("Connect project to ML result: ", ml_connect_response.json())
            print("Project connected to ML Model successfully!")
        except Exception as e:
            print(f"Failed to Connect project to BerryDB ML backend: {str(e)}")
            return None

    def retrieve_prediction(self, task_ids: List[int]):
        """
        The `retrieve_prediction` method is used to add a custom prediction to a specific task/record within an annotation project. This allows users to associate automated insights or model outputs with individual task, facilitating the annotation process and improving overall data management.

        **Parameters**:
        - **task_ids** (`List[int]`): The identifier of the tasks for which the prediction will be retrieved. This IDs should correspond to a valid tasks within the specified project.

        **Returns**:
        - `None`: This method does not return a value. Instead, it retrieves predictions to the specified tasks asynchronously.

        **Example**
        ```python
        task_ids = [12340, 12341, 12342]

        # Retrieve predictions for the specified tasks
        ner_proj.retrieve_prediction(task_id)
        ```
        ---
        """

        try:
            if not self.__annotations_api_key:
                raise ValueError("Error: annotations_api_key is required and must be of type str")
            if not self.__project_id:
                raise ValueError("Error: project_id is required and must be of type int")
            if not (task_ids and isinstance(task_ids, list) and len(task_ids)):
                raise ValueError("Error: task_id is required and must be of type int")

            url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.retrieve_predictions_url

            payload = {
                "selectedItems": {
                    "all": False,
                    "included": task_ids
                },
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {self.__annotations_api_key}",
            }
            params = {
                "id": "retrieve_tasks_predictions",
                "project": self.__project_id,
            }

            if bdb_constants.debug_mode:
                print("url:", url)
                print("payload:", payload)
                print("params:", params)

            print(f'Retrieving predictions for tasks with IDs: {",".join(task_ids)} in project with ID: {self.__project_id}')
            response = requests.post(url, json=payload, headers=headers, verify=False, params=params)
            if not (response.status_code == 200 or response.status_code == 201):
                print(f'Failed to retrieve predictions for tasks with IDs: {",".join(task_ids)}')
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if bdb_constants.debug_mode:
                print("Setup config result ", response.json())
            print(f'Attempting to retrieve predictions for tasks with IDs: {",".join(task_ids)}')
            return response.json()
        except Exception as e:
            print(f"Failed to retrieve predictions: {str(e)}")
            return None

    def create_prediction(self, task_id, prediction):
        """
        The `create_prediction` method is used to add a custom prediction to a specific task/record within an annotation project. This allows users to associate automated insights or model outputs with individual task, facilitating the annotation process and improving overall data management.

        **Parameters**:
        - **task_id** (`int`): The unique identifier of the task to which the prediction will be added. This ID should correspond to a valid task within the specified project.
        - **prediction** (`dict`): A dictionary containing the prediction data to be associated with the task/record. The structure of this dictionary should align with the expected format for predictions in your project based on the setup configuration, and it may include fields such as labels, polygon_labels, confidence scores, etc., and additional metadata.

        **Returns**:
        - `None`: This method does not return a value. Instead, it adds the prediction to the specified task and prints a success or failure message to indicate the result of the

        **Example**
        ```python
        task_id = 67890
        prediction = {
            "label": "Positive",
            "confidence": 0.95,
            "additional_info": "Predicted based on sentiment analysis model."
        }

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # Create a prediction for the specified task
        my_annotation_project.create_prediction(task_id, prediction)
        ```
        ---
        """

        try:
            import warnings

            from urllib3.exceptions import InsecureRequestWarning

            # Suppress only the InsecureRequestWarning from urllib3
            warnings.simplefilter('ignore', InsecureRequestWarning)
            if not self.__annotations_api_key:
                print("Error: annotations_api_key is required and must be of type str")
                return
            if not self.__project_id:
                print("Error: project_id is required and must be of type int")
                return
            if not task_id:
                print("Error: task_id is required and must be of type int")
                return

            url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.create_predictions_url.format(task_id)

            if type(prediction) != dict:
                print("Error: prediction has to be dict type")
                return
            prediction["project"] = self.__project_id
            prediction["task"] = task_id

            payload = json.dumps(prediction)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {self.__annotations_api_key}",
            }

            if bdb_constants.debug_mode:
                print("url:", url)
                print("payload:", payload)

            print(f"Adding prediction to task with ID: {task_id} in project with ID: {self.__project_id}")
            response = requests.post(url, data=payload, headers=headers, verify=False)
            if response.status_code != 201:
                print(f"Failed to add prediction to task with ID: {task_id}")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if bdb_constants.debug_mode:
                print("Setup config result ", response.json())
            print(f"Successfully added prediction to task with ID: {task_id}")
            return response.json()
        except Exception as e:
            print(f"Failed to create prediction: {str(e)}")
            return None

    def create_annotation(self, task_id, annotation):
        """
        Create an annotation for a task in the annotation project.

        **Parameters**:
        - **task_id** (`int`): The unique identifier of the task that the annotation will be associated with. This ID must match an existing task within the specified project.
        - **annotation** (`Dict`): A dictionary containing the details of the annotation to be added to the task. The structure of this dictionary should reflect the required fields and values for your annotation, such as labels, coordinates for bounding boxes, or any relevant metadata.

        **Returns**:
        - `None`: This method does not return a value. Instead, it adds the annotation to the specified task and prints a success or failure message indicating the result of the operation.

        **Example**
        ```python
        task_id = 67890
        annotation = {
            "label": "Cat",
            "bounding_box": {
                "x": 50,
                "y": 30,
                "width": 100,
                "height": 80
            },
            "confidence": 0.97
        }

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # Create an annotation for the specified task
        my_annotation_project.create_annotation(task_id, annotation)
        ```
        ---
        """

        try:
            import warnings

            from urllib3.exceptions import InsecureRequestWarning

            # Suppress only the InsecureRequestWarning from urllib3
            warnings.simplefilter('ignore', InsecureRequestWarning)
            if not self.__annotations_api_key:
                raise ValueError("Error: annotations_api_key is required and must be of type str")
            if self.__project_id is None:
                raise ValueError("Error: project_id is required and must be of type int")
            if not self.__berrydb_api_key:
                raise ValueError("Error: berrydb_api_key is required")
            if task_id is None:
                raise ValueError("Error: task_id is required and must be of type int")
            if not annotation:
                raise ValueError("Error: annotation is required")

            url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.create_annotations_url.format(task_id, self.__project_id, self.__berrydb_api_key)

            if type(annotation) != dict:
                raise ValueError("Error: annotations has to be dict type")
            annotation["project"] = self.__project_id

            payload = json.dumps(annotation)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Token {self.__annotations_api_key}",
            }

            if bdb_constants.debug_mode:
                print("url:", url)
                print("payload:", payload)

            print(f"Adding annotation to task with ID: {task_id} in project with ID: {self.__project_id}")
            response = requests.post(url, data=payload, headers=headers, verify=False)
            if response.status_code != 201:
                print(f"Failed to add annotation to task with ID: {task_id}")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if bdb_constants.debug_mode:
                print("Setup config result ", response.json())
            print(f"Successfully added annotation to task with ID: {task_id}")
            return response.json()
        except Exception as e:
            print(f"Failed to create annotations: {str(e)}")
            return None

    def attach_annotations_config(self, annotations_config: AnnotationsConfig):
        """
        Attaches a predefined annotations configuration to the annotation project.

        This method links an `AnnotationsConfig` instance to the current project.
        The `AnnotationsConfig` defines how annotations should be generated,
        potentially using LLMs, specific prompts, and data transformations.
        Attaching it to a project enables automated annotation workflows based
        on that configuration.

        .. note::
           The `annotations_config` parameter must be an instance of
           :class:`~berrydb.model_garden.annotations_config.AnnotationsConfig`.
           Please refer to the :doc:`annotation_config` page for details on how to
           create and save an ``AnnotationsConfig`` object using its builder.

        Parameters:
        - **annotations_config** (`AnnotationsConfig`): An instance of `AnnotationsConfig`
          that has been previously created and saved. The `name` attribute of this
          config is used to identify it in BerryDB.

        Returns:
        - `dict`: A dictionary containing the response from BerryDB, typically
          confirming that the configuration has been successfully attached.

        Raises:
        - `ValueError`: If the `annotations_config` does not have a `name`.

        Example:
        ```python
        from berrydb import AnnotationsConfig

        # Assume 'my_annotation_project' is an instance of AnnotationProject
        # and 'berrydb_api_key' is your BerryDB API key.

        # First, create and save an AnnotationsConfig
        ner_config = (
            AnnotationsConfig.builder()
            .name("my-project-ner-config")
            .input_transform_expression("data.text_content")
            .output_transform_expression("annotations.ner_tags")
            .llm_provider("openai")
            .llm_model("gpt-4o-mini")
            .prompt("Extract named entities: {{input}}")
            .build()
        )
        ner_config.save(berrydb_api_key) # Save it to BerryDB

        # Now, attach this saved config to your annotation project
        try:
            my_annotation_project.attach_annotations_config(ner_config)
            print(f"Successfully attached '{ner_config.name}' to project '{my_annotation_project.project_name()}'.")
        except Exception as e:
            print(f"Error attaching annotations config: {e}")
        ```
        ---
        """
        if not annotations_config.name:
            raise ValueError("Error: annotations_config name is required and must be of type string")

        url = bdb_constants.LABEL_STUDIO_BASE_URL + bdb_constants.attach_annotations_config_to_project_url.format(self.__project_id)
        payload = json.dumps({"annotation_config_name": annotations_config.name})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.__annotations_api_key}",
        }

        if bdb_constants.debug_mode:
            print("url:", url)
            print("payload:", payload)

        try:
            response = requests.patch(url, data=payload, headers=headers)
            if response.status_code != 200:
                print("Project label config setup Failed!")
                Utils.handleApiCallFailure(response.json(), response.status_code)
            if bdb_constants.debug_mode:
                print("Setup config result ", response.json())
            print("Project label config setup successful!")
            return response.json()
        except Exception as e:
            print(f"Failed to setup config: {str(e)}")
            return None

    def get_task_data(self):
        """
        Retrieves a list of all tasks within the annotation project, along with
        their corresponding BerryDB document IDs and database names.

        This method fetches information for every task in the project. Each task
        typically represents a single data item
        that has been imported into the annotation project. The `task_id` returned
        for each task can then be used with other methods like
        :meth:`retrieve_prediction <annotation_project.annotation_project.AnnotationProject.retrieve_prediction>`,
        :meth:`create_annotation <annotation_project.annotation_project.AnnotationProject.create_annotation>`, or
        :meth:`create_prediction <annotation_project.annotation_project.AnnotationProject.create_prediction>`
        to interact with individual tasks.

        Returns:
        - `List[Dict[str, any]]`: A list of dictionaries, where each dictionary
          represents a task and contains the following keys:
            - **'task_id'** (`int`): The unique identifier of the task within the
              annotation project.
            - **'document_id'** (`str`): The original identifier of the document
              in BerryDB from which this task was created.
            - **'database_name'** (`str`): The name of the BerryDB database from
              which the original document was sourced.

        Raises:
        - `Exception`: If there's an issue fetching the tasks from BerryDB,
          for example, due to network issues or if the project is not found.

        Example:
        ```python
        # Assuming 'my_annotation_project' is an instance of AnnotationProject

        try:
            all_tasks_info = my_annotation_project.get_task_data()
            if all_tasks_info:
                print(f"Found {len(all_tasks_info)} tasks in project '{my_annotation_project.project_name()}':")
                for task_info in all_tasks_info:
                    task_id = task_info['task_id']

                    Example: Retrieve prediction for this task
                    try:
                        prediction = my_annotation_project.retrieve_prediction(task_ids=[task_id])
                        if prediction:
                            print(f"    Prediction for task {task_id}: {prediction}")
                    except Exception as pred_e:
                        print(f"    Could not retrieve prediction for task {task_id}: {pred_e}")

                    # Example: Create an example annotation for this task
                    ex_annotation_data = {
                        "result": [
                            {
                                "from_name": "label", # Matches your label config
                                "to_name": "text",   # Matches your label config
                                "type": "choices",   # Matches your label config
                                "value": {"choices": ["SomeLabel"]}
                            }
                        ]
                    }
                    try:
                       my_annotation_project.create_annotation(task_id, ex_annotation_data)
                       print(f"    Successfully created annotation for task {task_id}")
                    except Exception as ann_e:
                       print(f"    Could not create annotation for task {task_id}: {ann_e}")

            else:
                print(f"No tasks found in project '{my_annotation_project.project_name()}'.")
        except Exception as e:
            print(f"Error retrieving task data: {e}")
        ```
        """
        url = f"{bdb_constants.LABEL_STUDIO_BASE_URL}/api/projects/{self.__project_id}/tasks"
        headers = {"Authorization": f"Token {self.__annotations_api_key}"}
        params = {"page": 1, "page_size": -1}

        task_ids = []

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch tasks for project with name: {self.__project_name}")

            data = response.json()
            tasks = data or []

            task_ids.extend([{"task_id": task["id"], "document_id": task.get("data", {}).get("_meta", {}).get("objectId", {}),\
                            "database_name": task.get("data", {}).get("_meta", {}).get("databaseName", {})} for task in tasks])
            return task_ids
        except:
            raise Exception(f"Failed to fetch tasks for project with name: {self.__project_name}")
