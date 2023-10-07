from pyfinnotech.tests.helper import ApiClientTestCase

client_invalid_mock_cards = [
    "000000000000000",
    "A000000000000000",
]


class ClientCredentialTestCase(ApiClientTestCase):
    def test_fetch_client_credential(self):
        client_credential = self.api_client.client_credential
        self.assertIsNotNone(client_credential.token)
        self.assertIsNotNone(client_credential.refresh_token)
        self.assertIsNotNone(client_credential.creation_date)
        self.assertIsNotNone(client_credential.life_time)
        self.assertIsNotNone(client_credential.scopes)
        self.assertIsNotNone(client_credential.scopes)

    def test_refresh_client_credential(self):
        client_credential = self.api_client.client_credential
        client_credential.refresh(self.api_client)
        self.assertIsNotNone(client_credential.token)
        self.assertIsNotNone(client_credential.refresh_token)
        self.assertIsNotNone(client_credential.creation_date)
        self.assertIsNotNone(client_credential.life_time)
        self.assertIsNotNone(client_credential.scopes)
        self.assertIsNotNone(client_credential.scopes)

    def test_revoke_client_credential(self):
        # TODO:
        pass
