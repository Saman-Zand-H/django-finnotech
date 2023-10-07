import socket
import unittest

from nanohttp import quickstart

from pyfinnotech import FinnotechApiClient
from pyfinnotech.const import (
    ALL_SCOPE_CLIENT_CREDENTIALS,
    ALL_SCOPE_AUTHORIZATION_TOKEN,
)
from pyfinnotech.tests.mock_api_server import (
    FinnotechRootMockController,
    valid_mock_client_id,
    valid_mock_client_secret,
)


class ApiClientTestCase(unittest.TestCase):
    _server_shutdown = None
    api_client = None

    @classmethod
    def find_free_port(cls):
        s = socket.socket()
        s.bind(("", 0))  # Bind to a free port provided by the host.
        port = s.getsockname()[1]  # Return the port number assigned.
        s.close()
        return port

    @classmethod
    def setUpClass(cls):
        server_port = cls.find_free_port()
        cls._server_shutdown = quickstart(
            controller=FinnotechRootMockController(), port=server_port, block=False
        )
        cls.api_client = FinnotechApiClient(
            client_id=valid_mock_client_id,
            client_secret=valid_mock_client_secret,
            base_url=f"http://localhost:{server_port}",
            scopes=ALL_SCOPE_CLIENT_CREDENTIALS + ALL_SCOPE_AUTHORIZATION_TOKEN,
        )
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls._server_shutdown()
        super().tearDownClass()
