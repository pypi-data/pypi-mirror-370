import requests
from typing import Optional, Dict, Any
from .Base import BaseAPI


class OutputModule(BaseAPI):
    """
    Output Module API endpoints for Collibra DGC.
    """
    def __init__(self, connector):
        super().__init__(connector)
        self.__base_api = connector.api + "/outputModule"

    def export_json(
        self,
        body: str,
        validation_enabled: bool = False
    ) -> Dict[Any, Any]:
        """
        Exports results in JSON format, returns the results immediately.

        Performs an Output Module query and exports the returns results immediately in JSON format.

        Please note that the ViewConfig/TableViewConfig's syntax validation is not executed by default.
        DGC admin console settings may impact the execution of the query (especially in terms of timeout
        and a limit on the number of results).

        Args:
            view_config (str): The JSON/YAML representation of ViewConfig/TableViewConfig
                             that describes the query to be performed.
            validation_enabled (bool): Determines if the ViewConfig's syntax should be validated
                                     (True) or not (False). Default value is False for backward
                                     compatibility reasons but it is strongly advised to always
                                     enable this validation.

        Returns:
            Dict[Any, Any]: The exported results in JSON format.

        Raises:
            requests.exceptions.RequestException: If the API request fails.
        """
        endpoint = f"{self.__base_api}/export/json"

        headers = {
            'Content-Type': 'application/json'
        }

        return self._post(url=endpoint, data=body, headers=headers).json()
