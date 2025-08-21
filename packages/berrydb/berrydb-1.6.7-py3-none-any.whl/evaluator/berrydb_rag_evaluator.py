from typing import Any, Dict, List, Optional, Union

import requests

from berrydb.berrydb_settings import Settings
from berrydb.eval_metrics import EvalMetrics
from constants import constants as bdb_constants
from database.database import Database
from utils.utils import Utils


class BerryDBRAGEvaluator:

    def __init__(self, api_key:str, database:Database, llm_api_key:str, settings: Settings|None = None, settings_name: str|None = None, embedding_api_key:Optional[str] = None,
            metrics_database_name:Optional[str]="EvalMetricsDB"):
        from berrydb.BerryDB import BerryDB
        self.__api_key = api_key
        self.__open_ai_api_key = llm_api_key
        self.__embedding_api_key = embedding_api_key
        self.__db = database
        self.__metrics_database_name = metrics_database_name or "EvalMetricsDB"
        self.__settings = settings
        self.__settings_name = settings_name
        try:
            self.__metrics_db = BerryDB.connect(self.__api_key, self.__metrics_database_name)
        except Exception as e:
            raise Exception(f"Could not connect to database with name '{self.__metrics_database_name}' make sure you have the database"
                            + " in your organization else use a different database name using the metrics_database_name attribute")


    def eval(self, test_params: Dict[str, Any], metrics_names: Union[EvalMetrics, List[EvalMetrics]], metrics_args:Optional[Dict[str, Any]] = None , metrics_processor=None):
        """
            This method evaluates the given test cases using the specified metrics.

            **Parameters:**
            - **test_params** (Dict[str, Any]): A dictionary containing the test parameters. This can include
                                                1. The dataset used for testing, under the key "test_data".
                                                2. The name of the test suite, under the key "test_suite_name". (Optional)
                                                3. In case you have multiple runs against the same test suite, you can use the run_name to differentiate. The name of the run should be under the key "run_name". (Optional)

            - **metrics_names** (Union[str, List[str]]): The names of the metrics to be used for evaluation. Redundant metrics are flatten in the code. Metrics can be passed in any of  the following ways:
                                                        1. A single metric name as a string.
                                                            OR
                                                        2. Multiple metrics as a list of individual metric names.
                                                            OR
                                                        3. A single metrics collection name.
                                                            OR
                                                        4. Multiple metrics collections as a list of individual metric names.
                                                            OR
                                                        5. Combination of metrics and metrics collection name/s as a list


            - **metrics_args** Optional[Dict[str, Any]] = None: Metric parameters like the threshold, the model to use for the evaluation, whether to include a reason or not can be passed as a Dict.

            - **metrics_processor** A custom metrics processor function. If not provided, the default metrics processor will be used which upserts all the metrics to EvalMetricsDB.


            **Returns:**
            - Dict: Returns the resultant metrics


            .. seealso::
                - :ref:`EvalMetrics <evalmetrics>`
            .. #end
        """
        # metrics_names, metrics_args = self.__process_input(metrics_names, metrics_args)
        # all_metrics = self.__all_metrics(metrics_names, metrics_args)
        # self.__trigger_time = int(datetime.now().timestamp() * 1000)
        if isinstance(metrics_names, list):
            metrics_names = [v.value for v in metrics_names]
        else:
            metrics_names = metrics_names.value
        if test_params is None or not isinstance(test_params, dict):
            raise ValueError("test_params is required and should be a dictionary")

        if "test_data" not in test_params:
            raise ValueError("test_data is required in test_params.")
        if not isinstance(test_params["test_data"], list):
            raise ValueError("test_data should be a list.")
        for t in test_params["test_data"]:
            if not isinstance(t, dict):
                raise ValueError("Each item in test_data should be a dictionary.")
            if set(t.keys()) != {"input", "expected_output"}:
                raise ValueError("Each dictionary in test_data must contain exactly 'input' and 'expected_output' keys.")
            if not all(isinstance(t[key], str) for key in ["input", "expected_output"]):
                raise ValueError("'input' and 'expected_output' must be strings.")

        payload = {
            "apiKey": self.__api_key,
            "orgName": self.__db.org_name(),
            "databaseName": self.__db.database_name(),
            "metricsDatabaseName": self.__metrics_database_name,
            "llmApiKey": self.__open_ai_api_key,
            "settingsName": self.__settings_name,
            "settings": self.__settings.__dict__,
            "embeddingApiKey": self.__embedding_api_key,
            "testParams": test_params,
            "metricsNames": metrics_names,
            "metricsArgs": metrics_args,
            "upsertMetrics": metrics_processor is None
        }

        url = bdb_constants.BERRY_GPT_BASE_URL + bdb_constants.evaluate_chat_url

        print("url:", url)
        print("payload:", payload)

        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)

            print("Validate API key result: ", response.json())
            json_res = response.json()
            if metrics_processor and isinstance(metrics_processor, callable) and json_res and isinstance(json_res, list) and len(json_res):
                for res in json_res:
                    metrics_processor(res)
            return json_res
        except Exception as e:
            raise Exception("Failed to evaluate your chat responses: {}".format(str(e)))