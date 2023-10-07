from pyfinnotech.tests.helper import ApiClientTestCase
from pyfinnotech.tests.mock_api_server import valid_mock_ibans

client_invalid_mock_ibans = [
    "IR9108000050001154264320010",
    "TR910800005000115426432001",
]


class IbanValidationTestCase(ApiClientTestCase):
    def test_server_validate_iban(self):
        for c in valid_mock_ibans:
            result = self.api_client.iban_inquiry(c)
            self.assertTrue(result.is_valid)
            self.assertIsNotNone(result.owner_first_name)
            self.assertIsNotNone(result.owner_last_name)

    def test_client_validate_iban(self):
        for c in client_invalid_mock_ibans:
            with self.assertRaises(ValueError):
                self.api_client.iban_inquiry(c)
