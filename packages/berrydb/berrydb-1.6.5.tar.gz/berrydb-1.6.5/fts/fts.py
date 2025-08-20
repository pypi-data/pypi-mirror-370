import requests

from constants import constants as bdb_constants
from utils.utils import Utils


class FTS:
    __api_key: str
    __database_name: str
    __indexed_fields: list

    def __init__(self, api_key, database_name, indexed_fields):
        self.__api_key = api_key
        self.__database_name = database_name
        self.__indexed_fields = indexed_fields

    def status(self):
        """Returns the status of FTS index.

        Returns:
                "building" | "online"
        """
        url = bdb_constants.BASE_URL + bdb_constants.fts_status_url

        params = {
            "databaseName": self.__database_name,
            "apiKey": self.__api_key,
        }

        if bdb_constants.debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)

            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)

            res = response.json()
            if bdb_constants.debug_mode:
                print("FTS result: ", res)

            return res["status"]
        except Exception as e:
            errMsg = "Failed to check status for FTS"
            print(f"{errMsg}, reason : {str(e)}")
            return

    def query(self, q):
        """Performs a full-text search (FTS) across indexed fields and returns matching results.

        Args:
                q (str): The search query

        Returns:
                A list matching items
        """
        url = bdb_constants.BASE_URL + bdb_constants.fts_url

        params = {
            "query": q,
            "databaseName": self.__database_name,
            "apiKey": self.__api_key,
        }

        if bdb_constants.debug_mode:
            print("url:", url)
            print("params:", params)

        try:
            response = requests.get(url, params=params)

            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)

            res = response.json()
            if bdb_constants.debug_mode:
                print("FTS result: ", res)

            return res
        except Exception as e:
            errMsg = "Failed to perform FTS"
            print(f"{errMsg}, reason : {str(e)}")
            return