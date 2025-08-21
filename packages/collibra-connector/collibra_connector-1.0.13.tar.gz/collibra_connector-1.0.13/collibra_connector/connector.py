import logging
import requests
from requests.auth import HTTPBasicAuth

from .api import (
    Asset,
    Community,
    Domain,
    User,
    Responsibility,
    Workflow,
    Metadata,
    Comment,
    Relation,
    OutputModule,
    Utils
)


class CollibraConnector():
    """
    This class is used to connect to the Collibra API.
    It requires the API URL and authentication credentials.
    The authentication is done using HTTP Basic Auth.
    """

    def __init__(self, api: str, username: str, password: str, timeout: int = 30, **kwargs):
        """
        Initializes the CollibraConnector with API URL and authentication credentials.
        :param api: The API URL for Collibra.
        :param username: The username for authentication.
        :param password: The password for authentication.
        """
        self.__auth = HTTPBasicAuth(username, password)
        self.__api = api + "/rest/2.0"
        self.__base_url = api
        self.__timeout = timeout

        # Initialize all API classes
        self.asset = Asset(self)
        self.community = Community(self)
        self.domain = Domain(self)
        self.user = User(self)
        self.responsibility = Responsibility(self)
        self.workflow = Workflow(self)
        self.metadata = Metadata(self)
        self.comment = Comment(self)
        self.relation = Relation(self)
        self.output_module = OutputModule(self)
        self.utils = Utils(self)

        self.uuids = {}
        if kwargs.get('uuids'):
            self.uuids = self.utils.get_uuids()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def __repr__(self):
        return f"CollibraConnector(api={self.__api}, auth={self.__auth})"

    def test_connection(self):
        """Test the connection to Collibra API"""
        try:
            response = requests.get(
                f"{self.__api}/auth/sessions/current",
                auth=self.__auth,
                timeout=self.__timeout
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    @property
    def api(self):
        return self.__api

    @property
    def auth(self):
        return self.__auth

    @property
    def base_url(self):
        return self.__base_url

    @property
    def timeout(self):
        return self.__timeout
